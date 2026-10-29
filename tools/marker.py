"""marker.py: the phase-5 marker script: every string's en = its id + filler at full width, controls kept.

    python -X utf8 tools/marker.py                     # -> work/marker/script/*.json
    python -X utf8 tools/build.py --script work/marker/script --out build/ruinarm_marker.sfc

Messages: each line's text runs become one run of filler that fills the line to LINE px (inserted names, items and
numbers counted at NAME/ITEM/NUM px), the message id first. Fixed fields: tag + index, filled to 2 letters a cell
(names: one letter a cell). Staff roll: same per positioned run. DATA ids are glyph palettes, not text: kept.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import SINGLE_FIELDS  # noqa: E402
from extract import SCRIPT  # noqa: E402
from font import adv  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "work" / "marker" / "script"
LINE = 223                    # 14 cells x 16 px; a pen reaching 224 runs the game's auto-wrap (a blank line after)
INSERT = {"name": 56, "item": 112, "item_v": 112, "num": 30}
FILL = "The quick brown fox jumps over the lazy dog. Pack my box with five dozen liquor jugs! "
DATA = {"848A27"}             # digit/symbol cell palette picked by index (docs/re/text.md)
TAG = {"menu": "M", "item": "I", "place": "P", "name_hero": "Hero", "name_sister": "Sis", "name_party": "Pty","ingot": "G",
       "equip": "E", "tactic": "T", "pad": "C", "use": "U", "act": "A", "element": "L", "heat": "H", "status": "S"}
PART = re.compile(r"(\{[^{}]*\}|\n)")
TEXTLIKE = re.compile(r"\{d:[^{}]*\}")


def filler(px, start=""):
    out = start
    for c in FILL * 4:
        if adv(out + c) > px:
            break
        out += c
    return out


def message(mid, jp):
    lines, first, out = re.split(r"(\n|\{wait\})", jp), True, []  # {wait} = new page: a line of its own
    for line in lines:
        if line in ("\n", "{wait}"):
            out.append(line)
            continue
        parts = [p for p in PART.split(line) if p]
        text = [i for i, p in enumerate(parts) if not PART.fullmatch(p) or TEXTLIKE.fullmatch(p)]
        if not text:
            out.append(line)
            continue
        used = sum(INSERT.get(p[1:-1].split(":")[0], 0) for p in parts if PART.fullmatch(p) and not TEXTLIKE.fullmatch(p))
        run = filler(LINE - used, f"#{mid} " if first else "")
        first = False
        parts = [run if i == text[0] else "" if i in text else p for i, p in enumerate(parts)]
        out.append("".join(parts))
    return "".join(out)


def exact(px, start):
    """start + filler whose advance is exactly px (the width-gate line)."""
    base = filler(px - 16, start)
    tails = [a + b + c for a in "MHnoli.' " for b in "MHnoli.' " for c in "MHnoli.'"]
    return base + next(t for t in tails if adv(base + t) == px)


# Width gate + glyph torture (msg 1032 = scenes gate / gate_p2): name line + 3 lines at LINE px exactly, then every
# glyph with double spaces, then 4 text lines to see how many a page shows.
GATE = {"1032": "{col:01}{name:01}{f4}{f4:46}{fa:C1}\n" + "\n".join(exact(LINE, f"#1032 L{i} ") for i in (1, 2, 3))
        + "{wait}ABCDEFGHIJKLMNOPQRSTUVWXYZ  0123456789\nabcdefghijklmnopqrstuvwxyz  .,!?'\"-\n"
        "()/%&+×~=…—：;:[]#*  The End.{wait}Page line 1\nPage line 2\nPage line 3\nPage line 4"
        "{fd}{fe:10}{goto:00:102D}"}


def field(tag, i, cells, single):
    n = cells - 1 if single else 2 * cells
    s = f"{tag}{i:X}"
    return (s + "abcdefghijklmnopqrstuvwxyz")[:n]


def staff(i, jp):
    parts, k = [], 0
    for p in PART.split(jp):
        if not p:
            continue
        if PART.fullmatch(p):
            parts.append(p)
        else:
            parts.append((f"S{i:X}{k}" + "abcdefghijklmnopqrstuvwxyz")[:2 * len(p)])
            k += 1
    return "".join(parts)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    n = 0
    for p in sorted(SCRIPT.glob("*.json")):
        es = json.loads(p.read_text(encoding="utf-8"))
        name = p.stem
        for i, e in enumerate(es):
            if name == "dict" or e["id"].startswith("orphan") or e["id"] in DATA:
                continue
            if name.startswith("msg"):
                en = message(e["id"], e["jp"])
                e["en"] = GATE.get(e["id"]) or (en if en != e["jp"] else "")
            elif name == "staff":
                e["en"] = staff(i, e["jp"])
            else:
                e["en"] = field(TAG[name], i, e["max"], name in SINGLE_FIELDS)
            n += bool(e["en"])
        (OUT / p.name).write_text(json.dumps(es, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"{OUT.as_posix()}: {n} strings marked")


if __name__ == "__main__":
    main()
