"""batches.py: translation batches (docs/translator-brief.md): split the untranslated script, check and merge English.

    python -X utf8 tools/batches.py split            # new work/tl/bNNN.tsv (+ build/terms_bNNN.txt), never overwrites
    python -X utf8 tools/batches.py check b001 ..    # validate work/tl/bNNN.out.tsv; prints OK or one line per error
    python -X utf8 tools/batches.py merge b001 ..    # check, then write the English into script/*.json
    python -X utf8 tools/batches.py fit "text"       # how a message wraps: rows per page with their px
    python -X utf8 tools/batches.py pairs b001 ..    # work/tl/bNNN.pairs.txt for the reviewer (docs/reviewer-brief.md)

Batch TSV: id, speaker, form, limit, jp. jp has dictionary refs written out ({d:XX|word} -> word, D9) and newlines as
the two characters \\n. Output TSV: id, en; \\n in en = a forced line break.
Messages: en is wrapped here (greedy, LINE px per row, ROWS rows per page, pages split at {wait..}/{fe..}); a page
that starts with a speaker ({col:01}Name\\n) keeps that row. Fixed fields: 2 letters per cell (names: 1), staff runs:
2 letters per Japanese glyph. Width numbers: docs/re/vwf.md §Width gate.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import SINGLE_FIELDS  # noqa: E402
from en import pieces  # noqa: E402
from extract import SCRIPT  # noqa: E402
from font import SINGLES, adv  # noqa: E402
from marker import DATA  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TL = ROOT / "work" / "tl"
TERMS = ROOT / "build"
GLOSSARY = ROOT / "glossary.md"
LINE, ROWS = 223, 4
INSERT = {"name": 56, "item": 112, "item_v": 112, "num": 30}   # px reserved for what the game inserts
ORDER = ["msg10", "msg11", "msg12", "msg13", "msg00", "msg01", "msg02", "staff", "name_party", "name_hero",
         "name_sister", "place", "item", "ingot", "equip", "element", "heat", "use", "act", "tactic", "pad", "status",
         "menu"]
MSG_CHARS, MAX_ENTRIES = 3500, 150
CODE = re.compile(r"\{[^{}]*\}")
DREF = re.compile(r"\{d:[0-9A-F]+\|([^{}]*)\}")
PAGE = re.compile(r"(\{(?:wait|fe)(?::[0-9A-F]+)?\})")
JAPANESE = re.compile(r"[぀-ヿ㐀-鿿＀-￯〔〕＊]")
HONORIFIC = re.compile(r"(\{name[^{}]*\}|[ァ-ヴー]+)(さん|くん|君|ちゃん|様|さま|殿)")
HONOR_EN = {"さん": "-san", "くん": "-kun", "君": "-kun", "ちゃん": "-chan", "様": "-sama", "さま": "-sama",
            "殿": "-dono"}
KATA = "ァ-ヴー"


# ---- the script


def load_script():
    """{file stem: entries} for every translatable file (the dictionary stays Japanese, D9)."""
    return {n: json.loads((SCRIPT / f"{n}.json").read_text(encoding="utf-8")) for n in ORDER}


def save(name, entries):
    (SCRIPT / f"{name}.json").write_text(json.dumps(entries, ensure_ascii=False, indent=1) + "\n", encoding="utf-8",
                                         newline="\n")


def kind(name):
    return "msg" if name.startswith("msg") else "staff" if name == "staff" else "name" if name in SINGLE_FIELDS \
        else "field"


def plain_jp(jp):
    return DREF.sub(r"\1", jp)


def translatable(name, e):
    return not e["id"].startswith("orphan") and e["id"] not in DATA and JAPANESE.search(CODE.sub("", e["jp"]))


# ---- message layout


def width(s):
    """px of s: text by font advance, inserts at their reserve, other codes 0."""
    px = 0
    for part in re.split(r"(\{[^{}]*\})", s):
        if CODE.fullmatch(part):
            px += INSERT.get(part[1:-1].split(":")[0], 0)
        else:
            px += adv(part)
    return px


def wrap_line(seg):
    """A forced line -> rows of at most LINE px (greedy on spaces). Fitting lines come back unchanged."""
    if width(seg) <= LINE:
        return [seg]
    rows, cur = [], ""
    for word in seg.split(" "):
        nxt = f"{cur} {word}" if cur else word
        if width(nxt) <= LINE or not cur:
            cur = nxt
        else:
            rows.append(cur)
            cur = word
    return rows + [cur]


def layout(en):
    """[[row, ..] per page] for en (forced breaks = newline)."""
    pages, cur = [], []
    for part in PAGE.split(en):
        if PAGE.fullmatch(part):
            pages.append(cur)
            cur = []
            continue
        for seg in part.split("\n") if part else []:
            cur += wrap_line(seg)
    return [p for p in pages + [cur] if p]


def wrap(en):
    """en with wrap breaks inserted (what merge stores)."""
    out = []
    for part in PAGE.split(en):
        out.append(part if PAGE.fullmatch(part) else "\n".join(r for seg in part.split("\n") for r in wrap_line(seg)))
    return "".join(out)


def headers(text):
    """Pages that open with a speaker row ({col:01}Name then a newline)."""
    n = 0
    for part in PAGE.split(text):
        m = re.match(r"(?:\{(?!col)[^{}]*\})*\{col:01\}([^\n]*)\n", part)
        if m and len(CODE.sub("", m.group(1))) <= 24:
            n += 1
    return n


def codes(text):
    return Counter(c for c in CODE.findall(text) if not c.startswith(("{d:", "{wait}")))


# ---- checks


def char_errors(en):
    bad = sorted({c for c in CODE.sub("", en).replace("\n", "") if c not in SINGLES})
    return [f"characters not in the font: {''.join(bad)!r} (plain ASCII only)"] if bad else []


def msg_errors(jp, en):
    errs = []
    if codes(jp) != codes(en):
        miss, extra = codes(jp) - codes(en), codes(en) - codes(jp)
        errs.append(f"control codes differ: missing {dict(miss)} extra {dict(extra)}")
    last = CODE.findall(jp)[-1:]
    if last and not en.endswith(last[0]):
        errs.append(f"must end with {last[0]}")
    if headers(jp) != headers(en):
        errs.append(f"{headers(jp)} speaker rows in the JP, {headers(en)} in the EN: keep '\\n' right after a speaker")
    for i, page in enumerate(layout(en), 1):
        for r in page:
            if width(r) > LINE:
                errs.append(f"page {i}: a word is wider than a row ({width(r)} px): {r!r}")
        if len(page) > ROWS:
            errs.append(f"page {i}: {len(page)} rows, max {ROWS} (speaker row included): split it with {{wait}}")
    if re.search(r"\{(?:name|item|item_v|num)[^{}]*\}(?:st|nd|rd|th)\b", en):
        errs.append("ordinal suffix glued to a variable: rephrase")
    if re.search(r"\b(?:a|an|A|An) \{(?:name|item)", en):
        errs.append("a/an right before a name/item variable: rephrase")
    return errs


def staff_runs(text):
    return [p for p in re.split(r"\{[^{}]*\}", text)]


def field_errors(name, e, en):
    if kind(name) == "staff":
        jr, er = staff_runs(e["jp"]), staff_runs(en)
        if CODE.findall(e["jp"]) != CODE.findall(en):
            return ["staff: copy every {pos:..}/{end..} code, same order"]
        return [f"run {i}: {er[i]!r} is {len(pieces(er[i]))} cells, the JP run has {len(jr[i])}"
                for i in range(len(jr)) if len(pieces(er[i])) > len(jr[i])]
    if CODE.search(en) or "\n" in en:
        return ["fields take plain text, no codes or breaks"]
    if kind(name) == "name":
        return [f"{len(en)} letters, max {e['max']}"] if len(en) > e["max"] else []
    n = len(pieces(en))
    errs = [f"{n} cells, max {e['max']} (2 letters a cell)"] if n > e["max"] else []
    return errs + [f"pair {p!r} is {adv(p)} px, a cell holds 16: shift a space" for p in pieces(en) if adv(p) > 16]


def glossary():
    """[(jp, [en forms], [avoid])] from the glossary tables (EN alternatives separated by ' / ')."""
    out = []
    for line in GLOSSARY.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")] if line.startswith("|") else []
        if len(cells) < 2 or cells[0] in ("JP", "") or set(cells[0]) <= set("-: "):
            continue
        en = [x.strip() for x in cells[1].split(" / ") if x.strip()]
        avoid = [x.strip() for x in cells[4].split(",") if x.strip()] if len(cells) > 4 else []
        out.append((cells[0], en, avoid))
    return out


def term_in(term, text):
    if re.fullmatch(f"[{KATA}・]+", term):
        return re.search(f"(?<![{KATA}]){re.escape(term)}(?![{KATA}])", text) is not None
    return term in text


def gloss_errors(jp, en, gl):
    errs, text = [], plain_jp(jp)
    for term, forms, avoid in gl:
        if forms and term_in(term, text) and not any(f in en for f in forms):
            errs.append(f"glossary: {term} -> {' / '.join(forms)}")
        errs += [f"glossary: avoid {a!r} ({term})" for a in avoid if re.search(rf"\b{re.escape(a)}\b", en)]
    for jp_h, n in Counter(m.group(2) for m in HONORIFIC.finditer(text)).items():
        if en.count(HONOR_EN[jp_h]) < n:
            errs.append(f"honorific {jp_h} kept as {HONOR_EN[jp_h]} (D1): {n} in the JP, {en.count(HONOR_EN[jp_h])} here")
    return errs


def entry_errors(name, e, en, gl):
    errs = char_errors(en) + (["empty"] if not en.strip() else [])
    if "\\u" in en or "\t" in en:
        errs.append("escape or tab in the text")
    errs += msg_errors(e["jp"], en) if kind(name) == "msg" else field_errors(name, e, en)
    return errs + gloss_errors(e["jp"], en, gl)


# ---- batch files


def index(script):
    return {e["id"]: (name, i) for name, es in script.items() for i, e in enumerate(es)}


def read_tsv(p, cols):
    rows = []
    for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            parts = line.split("\t")
            if len(parts) != cols:
                raise SystemExit(f"{p.name}:{n}: {len(parts)} columns, need {cols}")
            rows.append(parts)
    return rows


def unesc(s):
    return s.replace("\\n", "\n")


def speaker(name, jp):
    if kind(name) != "msg":
        return ""
    m = re.match(r"(?:\{(?!col)[^{}]*\})*\{col:01\}([^\n]*)\n", plain_jp(jp))
    return CODE.sub(lambda c: c.group(0) if c.group(0).startswith("{name") else "", m.group(1)) if m else ""


def form_limit(name, e):
    k = kind(name)
    if k == "msg":
        return ("choice" if "{choice" in e["jp"] else "dlg"), f"{LINE}px x{ROWS}rows"
    if k == "staff":
        return "credit", ",".join(f"{2 * len(r)}ch" for r in staff_runs(e["jp"]) if r)
    if k == "name":
        return "name", f"{e['max']}ch"
    return name, f"{2 * e['max']}ch"


def existing():
    return sorted(TL.glob("b[0-9][0-9][0-9].tsv"))


def split():
    script = load_script()
    done ={r[0] for p in existing() for r in read_tsv(p, 5)}
    num = int(existing()[-1].stem[1:]) + 1 if existing() else 1
    TL.mkdir(parents=True, exist_ok=True)
    TERMS.mkdir(exist_ok=True)
    made = []
    for name in ORDER:
        todo = [e for e in script[name] if not e["en"] and translatable(name, e) and e["id"] not in done]
        cur, chars = [], 0
        for k, e in enumerate(todo + [None]):
            size = len(CODE.sub("", plain_jp(e["jp"]))) if e else 0
            if cur and (e is None or chars + size > MSG_CHARS or len(cur) >= MAX_ENTRIES):
                p = TL / f"b{num:03d}.tsv"
                if p.exists():
                    raise SystemExit(f"{p} exists")
                lines = []
                for x in cur:
                    form, limit = form_limit(name, x)
                    lines.append("\t".join([x["id"], speaker(name, x["jp"]), form, limit,
                                            plain_jp(x["jp"]).replace("\n", "\\n")]))
                p.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
                made.append(f"b{num:03d} {name} {len(cur)} entries {chars} chars")
                num, cur, chars = num + 1, [], 0
            if e:
                cur.append(e)
                chars += size
    print("\n".join(made) or "nothing left to split")
    terms()


def terms():
    """build/terms_bNNN.txt for every batch: the glossary rows whose JP occurs in it (rerun after glossary edits)."""
    gl = glossary()
    TERMS.mkdir(exist_ok=True)
    for p in existing():
        text = "".join(r[4] for r in read_tsv(p, 5))
        rows = [f"{t} -> {' / '.join(f)}" + (f" (avoid: {', '.join(a)})" if a else "") for t, f, a in gl
                if term_in(t, text)]
        (TERMS / f"terms_{p.stem}.txt").write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")


def check(batch, script=None, quiet=False):
    """{id: en} if the batch output is clean, else None (errors printed)."""
    script = script or load_script()
    idx, gl = index(script), glossary()
    inp = read_tsv(TL / f"{batch}.tsv", 5)
    outp = TL / f"{batch}.out.tsv"
    if not outp.exists():
        print(f"{batch}: {outp.name} missing")
        return None
    out = read_tsv(outp, 2)
    errs = []
    ids, got = [r[0] for r in inp], [r[0] for r in out]
    dup = [i for i, c in Counter(got).items() if c > 1]
    errs += [f"{i}: missing" for i in ids if i not in got] + [f"{i}: not in the batch" for i in got if i not in ids]
    errs += [f"{i}: listed twice" for i in dup]
    res = {}
    for i, en in out:
        if i not in idx or i not in ids:
            continue
        name, k = idx[i]
        en = unesc(en)
        errs += [f"{i}: {m}" for m in entry_errors(name, script[name][k], en, gl)]
        res[i] = en
    if errs:
        print(f"{batch}: {len(errs)} errors")
        print("\n".join(errs))
        return None
    if not quiet:
        print(f"{batch}: OK ({len(res)} entries)")
    return res


def merge(batches):
    script = load_script()
    idx = index(script)
    good = {b: check(b, script, quiet=True) for b in batches}
    if any(v is None for v in good.values()):
        raise SystemExit("merge refused: fix the batches above")
    touched = set()
    for b, res in good.items():
        for i, en in res.items():
            name, k = idx[i]
            script[name][k]["en"] = wrap(en) if kind(name) == "msg" else en
            touched.add(name)
        print(f"{b}: merged {len(res)}")
    for name in touched:
        save(name, script[name])


def pairs(batch):
    """work/tl/<batch>.pairs.txt for the reviewer: each entry as '>> id | JP' / EN, with 2 context lines either side."""
    script = load_script()
    idx = index(script)
    out = {r[0]: unesc(r[1]) for r in read_tsv(TL / f"{batch}.out.tsv", 2)}
    lines = []
    for i in [r[0] for r in read_tsv(TL / f"{batch}.tsv", 5)]:
        name, k = idx[i]
        es = script[name]
        for c in range(max(0, k - 2), min(len(es), k + 3)):
            e = es[c]
            jp, en = plain_jp(e["jp"]).replace("\n", " "), (out.get(e["id"]) or e["en"]).replace("\n", " ")
            if e["id"] == i:
                lines += [f">> {i} | {jp}", f"   {en}"]
            elif c in (k - 1, k + 1):
                lines.append(f"   ({e['id']} | {jp} | {en})")
        lines.append("")
    p = TL / f"{batch}.pairs.txt"
    p.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(p.relative_to(ROOT).as_posix())


def fit(text):
    for i, page in enumerate(layout(unesc(text)), 1):
        print(f"page {i}: {len(page)}/{ROWS} rows")
        for r in page:
            print(f"  {width(r):3d}/{LINE} px  {r}")


def selftest():
    assert wrap_line("a b") == ["a b"]
    long = " ".join(["word"] * 20)
    rows = wrap_line(long)
    assert len(rows) > 1 and all(width(r) <= LINE for r in rows) and " ".join(rows) == long
    assert layout("{col:01}{name:01}\nHi.{wait}Two.{end}") == [["{col:01}{name:01}", "Hi."], ["Two.{end}"]]
    assert headers("{fe:10}{col:01}{name:01}{f4}\nHi{fe}{col:01}Bob\nYo") == 2
    assert msg_errors("{col:01}{name:01}\nあ{end}", "{col:01}{name:01}\nOh.{end}") == []
    assert msg_errors("{col:01}{name:01}\nあ{end}", "{col:01}{name:01} Oh.{end}")  # speaker row lost
    assert msg_errors("{d:79|・・・}{end}", "...{end}") == []
    assert term_in("ワース", "ワースの村") and not term_in("ミン", "タイミング")
    assert field_errors("item", {"jp": "薬 草", "max": 8}, "Healing Herb") == []
    assert field_errors("item", {"jp": "x", "max": 2}, "Herbs") != []
    print("selftest ok")


def main():
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
    elif a[0] == "split":
        split()
    elif a[0] == "terms":
        terms()
    elif a[0] == "check":
        sys.exit(0 if all([check(b) is not None for b in a[1:]]) else 1)
    elif a[0] == "merge":
        merge(a[1:])
    elif a[0] == "pairs":
        for b in a[1:]:
            pairs(b)
    elif a[0] == "fit":
        fit(a[1])
    elif a[0] == "selftest":
        selftest()
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
