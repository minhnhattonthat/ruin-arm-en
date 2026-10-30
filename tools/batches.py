"""batches.py: translation batches (docs/translator-brief.md): split the untranslated script, check and merge English.

    python -X utf8 tools/batches.py split            # new work/tl/bNNN.tsv (+ build/terms_bNNN.txt), never overwrites
    python -X utf8 tools/batches.py check b001 ..    # validate work/tl/bNNN.out.tsv; prints OK or one line per error
    python -X utf8 tools/batches.py merge b001 ..    # check, then write the English into script/*.json
    python -X utf8 tools/batches.py fit "text"       # how a message wraps: rows per page with their px
    python -X utf8 tools/batches.py balance [--write] # one-word last rows take a word from the row above
    python -X utf8 tools/batches.py pairs b001 ..    # work/tl/bNNN.pairs.txt for the reviewer (docs/reviewer-brief.md)
    python -X utf8 tools/batches.py redo p01 1003 .. # re-batch translated ids (+ p01.cur.tsv, current English)
    python -X utf8 tools/batches.py chapters         # work/qa/story/chapters/*.txt for the story pass

Batch TSV: id, speaker, form, limit, jp. jp has dictionary refs written out ({d:XX|word} -> word, D9) and newlines as
the two characters \\n. Output TSV: id, en; \\n in en = a forced line break.
Messages: en is wrapped here (greedy, LINE px per row, ROWS rows per page, pages split at {wait..}/{fe..}); a page
that starts with a speaker ({col:01}Name\\n) keeps that row. Fixed fields: set proportionally, 16 px per cell (names:
1 letter a cell); 2+ spaces keep the next run's 2-letters-a-cell column (font.runs); command cells: "|" between
commands, 32 px each. Staff runs: 16 px per cell from the run's {pos} column to the screen edge. Width numbers:
docs/re/vwf.md §Width gate.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import SINGLE_FIELDS  # noqa: E402
from extract import SCRIPT  # noqa: E402
from fixed import CELLS  # noqa: E402
from font import SINGLES, adv, ink, slices  # noqa: E402
from marker import DATA  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TL = ROOT / "work" / "tl"
TERMS = ROOT / "build"
GLOSSARY = ROOT / "glossary.md"
LINE, ROWS = 223, 4
NAME = 7                    # a party record holds 7 name glyphs ($146A), whatever the default-name table's stride
INSERT = {"name": 56, "item": 112, "item_v": 112, "num": 30}   # px reserved for what the game inserts
ORDER = ["msg10", "msg11", "msg12", "msg13", "msg00", "msg01", "msg02", "staff", "name_party", "name_hero",
         "name_sister", "place", "item", "ingot", "equip", "element", "heat", "use", "act", "tactic", "pad", "status",
         "menu"]
MSG_CHARS, MAX_ENTRIES = 3500, 150
CODE = re.compile(r"\{[^{}]*\}")
DREF = re.compile(r"\{d:[0-9A-F]+\|([^{}]*)\}")
# {fd..} is an inline pause, not a break (phase 8 shots: "sky.{fd:13}There's" ran on and the game cut a word)
PAGE = re.compile(r"(\{(?:wait|fe)(?::[0-9A-F]+)?\})")
JAPANESE = re.compile(r"[぀-ヿ㐀-鿿＀-￯〔〕＊]")
HONORIFIC = re.compile(r"(\{name[^{}]*\}|[ァ-ヴ][ァ-ヴー]*)(さん|くん|君|ちゃん|様|さま|殿)")
HONOR_EN = {"さん": "-san", "くん": "-kun", "君": "-kun", "ちゃん": "-chan", "様": "-sama", "さま": "-sama",
            "殿": "-dono"}
KATA = "ァ-ヴー"
COMMAND_CELLS = {"84967B", "8496A4"}   # two-cell commands picked by index (docs/re/text.md): "A|B|..", 32 px each


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
    return not e["id"].startswith("orphan") and e["id"] not in DATA and JAPANESE.search(CODE.sub("", plain_jp(e["jp"])))


# ---- message layout


def width(s):
    """px of s: text by font advance, inserts at their reserve, other codes 0. Colour on mid-cell moves the pen to
    the next 8 px tile edge (asm/vwf.asm `colour`: palettes are per tile)."""
    px, on = 0, False
    for part in re.split(r"(\{[^{}]*\})", s):
        if part == "{col:01}":
            if not on and px % 16:
                px += 8 - px % 16 if px % 16 <= 8 else 16 - px % 16
            on = True
        elif part == "{col}":
            on = False
        elif CODE.fullmatch(part):
            px += INSERT.get(part[1:-1].split(":")[0], 0)
        else:
            px += sum(adv(c) if c in SINGLES else 16 for c in part)  # Japanese cells are 16 px
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


def balance(en):
    """en with each one-word last row (before {wait}/{fe}/the end) given the last word of the row above, when that
    row keeps 2+ words and the pair fits LINE. Speaker rows have one word, so they never give one."""
    out = []
    for part in PAGE.split(en):
        rows = part.split("\n")
        # a page's speaker row never gives a word ("Wind General Hude" has three)
        if not PAGE.fullmatch(part) and len(rows) > 1 and not (len(rows) == 2 and speaker_rows(part)):
            last, prev = rows[-1], rows[-2].split(" ")
            if CODE.sub("", last).strip() and " " not in last.strip() and len(prev) > 2 \
                    and not last.startswith(" ") and not rows[-2].startswith(" ") \
                    and width(f"{prev[-1]} {last}") <= LINE:
                rows[-2:] = [" ".join(prev[:-1]), f"{prev[-1]} {last}"]
        out.append("\n".join(rows))
    return "".join(out)


def rebalance(write=False):
    """balance() over every message; prints the changed rows, writes script/*.json with write=True."""
    n = 0
    for name, entries in load_script().items():
        if kind(name) != "msg":
            continue
        changed = False
        for e in entries:
            b = balance(e["en"])
            if b != e["en"] and not msg_errors(e["jp"], b, merged=True):
                n += 1
                print(f"{e['id']}: {e['en'][-60:]!r} -> {b[-60:]!r}" if not write else e["id"], end="\n")
                e["en"], changed = b, True
        if write and changed:
            save(name, entries)
    print(f"{n} messages {'rebalanced' if write else 'to rebalance'}")


def speaker_rows(text):
    """Speaker rows ({col:01}Name then a newline) that open a page, without the {col:01}."""
    out = []
    for part in PAGE.split(plain_jp(text)):
        m = re.match(r"(?:\{(?!col)[^{}]*\})*\{col:01\}([^\n]*)\n", part)
        row = CODE.sub("", m.group(1)) if m else ""
        # not a coloured phrase ({col} ends one; a JP row longer than a name; quotes)
        if m and (len(row) <= 10 if JAPANESE.search(row) else width(m.group(1)) <= LINE) and "{col}" not in m.group(1) \
                and not set(row) & set("「、,"):
            out.append(m.group(1))
    return out


def headers(text):
    return len(speaker_rows(text))


def header_codes(text):
    """The codes on each speaker row: the portrait codes after the name stay on that row."""
    return [CODE.findall(r) for r in speaker_rows(text)]


def codes(text):
    return Counter(c for c in CODE.findall(text) if not c.startswith(("{d:", "{wait}")))


# ---- checks


def char_errors(en):
    bad = sorted({c for c in CODE.sub("", en).replace("\n", "") if c not in SINGLES})
    return [f"characters not in the font: {''.join(bad)!r} (plain ASCII only)"] if bad else []


def msg_errors(jp, en, merged=False):
    errs = []
    if codes(jp) != codes(en):
        miss, extra = codes(jp) - codes(en), codes(en) - codes(jp)
        errs.append(f"control codes differ: missing {dict(miss)} extra {dict(extra)}")
    last = CODE.findall(jp)[-1:]
    if last and not en.endswith(last[0]):
        errs.append(f"must end with {last[0]}")
    if not merged and headers(jp) != headers(en):  # merged text has wrap breaks: a coloured first row looks like one
        errs.append(f"{headers(jp)} speaker rows in the JP, {headers(en)} in the EN: keep '\\n' right after a speaker")
    if header_codes(jp) != header_codes(en):
        errs.append(f"speaker-row codes {header_codes(jp)} in the JP, {header_codes(en)} in the EN: keep the row whole")
    rows = max([ROWS] + [len(p) for p in layout(jp)])  # a JP page past 4 rows scrolls the box: as many are fine
    for i, page in enumerate(layout(en), 1):
        for r in page:
            if width(r) > LINE:
                errs.append(f"page {i}: a word is wider than a row ({width(r)} px): {r!r}")
        if len(page) > rows:
            errs.append(f"page {i}: {len(page)} rows, max {rows} (speaker row included): split it with {{wait}}")
    if merged:  # stored text: the game cuts a row past LINE mid-word, so every row must already fit
        errs += [f"row wider than {LINE} px ({width(r)}): {r!r}" for part in PAGE.split(en)
                 for r in part.split("\n") if width(r) > LINE]
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
        def rows(t):
            return re.sub(r"\{pos:([0-9A-F]{4})\}", lambda m: f"{{row {int(m[1], 16) >> 6}}}", "".join(CODE.findall(t)))
        if rows(e["jp"]) != rows(en):
            return ["staff: copy every {pos:..}/{end..} code, same order; a {pos} may change column, not row"]
        # relocated by the build: a run may grow to the screen edge (32 tiles, 1 spare) from its {pos} column
        cols = [int(p, 16) % 0x40 // 2 for p in re.findall(r"\{pos:([0-9A-F]{4})\}", en)]
        return [f"run {i + 1}: {r!r} is {len(slices(r))} cells, column {c} leaves {(31 - c) // 2}"
                for i, (r, c) in enumerate(zip(er[1:], cols)) if c + 2 * len(slices(r)) > 31]
    if CODE.search(en) or "\n" in en:
        return ["fields take plain text, no codes or breaks"]
    if kind(name) == "name":
        return [f"{len(en)} letters, max {NAME}"] if len(en) > NAME else []
    n, cells = len(slices(en)), CELLS.get(e["id"], e["max"])
    errs = [f"{n} cells, max {cells} (16 px a cell)"] if n > cells else []
    if e["id"] in COMMAND_CELLS:
        units = en.split("|")
        if len(units) != e["max"] // 2:
            errs.append(f"command cells: {e['max'] // 2} commands joined by '|', got {len(units)}")
        errs += [f"command {u!r} is {ink(u)} px, max 32" for u in units if ink(u) > 32]
    return errs


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
    errs, text, en = [], plain_jp(jp), en.replace("\n", " ")
    for term, forms, avoid in gl:
        if forms and term_in(term, text) and not any(f.lower() in en.lower() for f in forms):
            errs.append(f"glossary: {term} -> {' / '.join(forms)}")
        errs += [f"glossary: avoid {a!r} ({term})" for a in avoid if re.search(rf"\b{re.escape(a)}\b", en)]
    for jp_h, n in Counter(m.group(2) for m in HONORIFIC.finditer(text)).items():
        if en.count(HONOR_EN[jp_h]) < n:
            errs.append(f"honorific {jp_h} kept as {HONOR_EN[jp_h]} (D1): {n} in the JP, {en.count(HONOR_EN[jp_h])} here")
    return errs


def entry_errors(name, e, en, gl, merged=False):
    errs = char_errors(en.replace("|", "") if e["id"] in COMMAND_CELLS else en) + (["empty"] if not en.strip() else [])
    if "\\u" in en or "\t" in en:
        errs.append("escape or tab in the text")
    errs += msg_errors(e["jp"], en, merged) if kind(name) == "msg" else field_errors(name, e, en)
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
        return "credit", ",".join(f"{(31 - int(p, 16) % 0x40 // 2) // 2 * 16}px"
                                  for p in re.findall(r"\{pos:([0-9A-F]{4})\}", e["jp"]))
    if k == "name":
        return "name", f"{NAME}ch"
    return name, f"{16 * CELLS.get(e['id'], e['max'])}px"


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


def flatten(en):
    """Merged message text -> running text: wrap breaks become spaces; breaks after a speaker row, before an indented or
    '*' row and around blank rows stay."""
    out = []
    for part in PAGE.split(en):
        rows = part.split("\n")
        if PAGE.fullmatch(part) or len(rows) == 1:
            out.append(part)
            continue
        s, hdr = rows[0], bool(speaker_rows(part))
        for i, r in enumerate(rows[1:], 1):
            keep = (i == 1 and hdr) or r.startswith((" ", "*")) or not r or not rows[i - 1]
            s += ("\n" if keep else " ") + r
        out.append(s)
    return "".join(out)


def redo(batch, ids):
    """work/tl/<batch>.tsv for already-translated ids (polish/review fixes) + <batch>.cur.tsv with their current
    English as running text; the translator edits the .cur rows into <batch>.out.tsv."""
    script = load_script()
    idx = index(script)
    p = TL / f"{batch}.tsv"
    if p.exists():
        raise SystemExit(f"{p} exists")
    rows, cur = [], []
    for i in ids:
        name, k = idx[i]
        e = script[name][k]
        form, limit = form_limit(name, e)
        rows.append("\t".join([i, speaker(name, e["jp"]), form, limit, plain_jp(e["jp"]).replace("\n", "\\n")]))
        cur.append(f"{i}\t" + (flatten(e["en"]) if kind(name) == "msg" else e["en"]).replace("\n", "\\n"))
    p.write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
    (TL / f"{batch}.cur.tsv").write_text("\n".join(cur) + "\n", encoding="utf-8", newline="\n")
    print(f"{batch}: {len(ids)} entries")


# story-pass chapters (docs/synopsis.md): id ranges in reading order, story first, then that act's town NPCs
CHAPTERS = {
    "act1": [("1000", "10EC")],
    "act1_towns": [("0000", "00CF"), ("0100", "0120"), ("01A5", "01B1")],
    "act2": [("10ED", "1149"), ("0121", "0138"), ("01C9", "01C9"), ("01E0", "01E0")],
    "act3": [("114A", "11C4"), ("1351", "1383"), ("0139", "0165")],
    "act4": [("11C5", "12B8"), ("0166", "0191")],
    "act5": [("12B9", "12FD")],
    "ending": [("1300", "1350"), ("0200", "0209")],
}


def chapters(folder):
    """One '>> id | speaker | JP' / EN file per chapter for the story reviewer; ids no chapter names go to misc."""
    script = load_script()
    rows = [(name, e) for name in ORDER if kind(name) == "msg" for e in script[name] if e["en"]]
    folder.mkdir(parents=True, exist_ok=True)
    left = {e["id"] for _, e in rows}
    for ch, ranges in [*CHAPTERS.items(), ("misc", [("0000", "FFFF")])]:
        out = []
        for lo, hi in ranges:
            for name, e in rows:
                if lo <= e["id"] <= hi and e["id"] in left:
                    left.discard(e["id"])
                    out.append(f">> {e['id']} | {speaker(name, e['jp'])} | {plain_jp(e['jp'])}\n{e['en']}\n")
        (folder / f"{ch}.txt").write_text("\n".join(out), encoding="utf-8", newline="\n")
        print(f"{ch}: {len(out)} lines")


def terms():
    """build/terms_bNNN.txt for every batch: the glossary rows whose JP occurs in it (rerun after glossary edits)."""
    gl = glossary()
    TERMS.mkdir(exist_ok=True)
    for p in existing() + sorted(TL.glob("p[0-9][0-9].tsv")):
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
            script[name][k]["en"] = balance(wrap(en)) if kind(name) == "msg" else en
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
    assert balance("{col:01}Wind General Hude{f4}\nHa!{end}") == "{col:01}Wind General Hude{f4}\nHa!{end}"
    assert flatten("{col:01}Bob{f4}\nHi there\nfriend.{wait}* Got\nit.\n\n  1Yes") == \
        "{col:01}Bob{f4}\nHi there friend.{wait}* Got it.\n\n  1Yes"
    assert term_in("ワース", "ワースの村") and not term_in("ミン", "タイミング")
    assert field_errors("item", {"id": "item_00", "jp": "薬 草", "max": 8}, "Healing Herb") == []
    assert field_errors("item", {"id": "item_00", "jp": "x", "max": 2}, "Healing Herbs") != []
    assert field_errors("menu", {"id": "8496A4", "jp": "x", "max": 4}, "Save|Load") == []
    assert field_errors("menu", {"id": "8496A4", "jp": "x", "max": 4}, "SaveLoad") != []
    assert field_errors("menu", {"id": "8496A4", "jp": "x", "max": 4}, "Save|Withdraw") != []
    assert field_errors("menu", {"id": "x", "jp": "x", "max": 2}, "Items") == []
    assert field_errors("menu", {"id": "x", "jp": "x", "max": 2}, "Status") != []  # 35 px
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
    elif a[0] == "chapters":
        chapters(ROOT / "work" / "qa" / "story" / "chapters")
    elif a[0] == "redo":
        redo(a[1], a[2:])
    elif a[0] == "pairs":
        for b in a[1:]:
            pairs(b)
    elif a[0] == "fit":
        fit(a[1])
    elif a[0] == "balance":
        rebalance("--write" in a)
    elif a[0] == "selftest":
        selftest()
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
