"""jp_reach.py: Japanese the game can still show from a built ROM: every message MSGTAB reaches, every fixed field,
every staff string, decoded with tbl/jp.tbl (English codes $0400+ decode as [XXXX], so only Japanese glyphs count).

    python -X utf8 tools/jp_reach.py build/ruinarm_marker.sfc [--known script/keep_jp.txt]    # exit 1 if any

The skill's jp_left.py --slots stops at the first 00 byte, which most 16-bit glyph codes here contain, so it can't
walk these strings. Known keeps: one id per line (anything after it is a note).
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fixed  # noqa: E402
from build import IDS, MSGTAB  # noqa: E402
from pack import NEXT, off, unpack_all  # noqa: E402
from textdump import BLOCKS, ROM, Script  # noqa: E402

JP = re.compile(r"[぀-ヿ一-鿿ｦ-ﾟ]")


def reach(rom):
    """[(id, text)] of every reachable string."""
    s, orig = Script(rom), Script(ROM.read_bytes())
    blocks = {b.addr: b for b in unpack_all(orig.d)}
    out, seen = [], set()
    for i in range(IDS):
        o = off(BLOCKS) + 3 * (i >> 8)
        b = blocks[int.from_bytes(orig.d[o:o + 3], "little")]
        if (i & 0xFF) >= len(b.slots) or b.slots[i & 0xFF] == NEXT:
            continue  # not a message: past the block's pointers (block $02 has 10) or an unused slot
        o = off(MSGTAB) + 3 * i
        t = off(int.from_bytes(rom[o:o + 3], "little"))
        if t in seen:
            continue
        seen.add(t)
        out.append((f"{i:04X}", s.text(s.words(t)[0])))
    for b in unpack_all(rom):
        if b.name == "staff":
            out += [(f"S{k:02X}", s.text(b.strings[i][:-1])) for k, i in enumerate(b.slots)]  # relocated: skip orphans
    for fs in fixed.fields(orig).values():
        out += [(f["id"], s.text(fixed.words(s, f))) for f in fs]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rom", type=Path)
    ap.add_argument("--known", type=Path)
    a = ap.parse_args()
    known = set()
    if a.known and a.known.exists():
        known = {ln.split()[0] for ln in a.known.read_text(encoding="utf-8").splitlines() if ln.strip()}
    hits = [(i, t) for i, t in reach(a.rom.read_bytes()) if JP.search(t) and i not in known]
    for i, t in hits[:200]:
        print(f"{i:10} {t[:80]!r}")
    print(f"{len(hits)} reachable strings with Japanese")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
