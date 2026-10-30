"""font.py: fonts/vwf.txt -> the English glyph codes, their cells and widths (asm/vwf.asm, docs/re/vwf.md).

English text uses codes $0400-$0FFF (not $07FF), drawn from the English font banks (FONT, 4 x 32 KB, each the cell
layout of $9F8000; code c is cell (c - $400) & $3FF of bank FONT + ((c - $400) >> 10)) by the hooks in asm/vwf.asm:
- singles: printable ASCII c -> $0400 + c; other font characters (— ： × …) -> $0401.. in file order.
  Messages use singles only: the dialogue VWF draws each at its advance.
- slices: $0480.. one 16 px cell of a fixed field's text set proportionally (slices()), so a field drawn one code
  per cell reads with no gaps and fits by pixels: 16 px a cell. Assigned per build from the cells the fixed fields
  use (slice_codes()), so the set follows the script.
widths: advance in px per code - $400 (a slice: 16, the last of a run: to the run's end). Codes below $400 (Japanese
cells) are 16 px.

    python -X utf8 tools/font.py     # selftest + summary
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FONT = ROOT / "fonts" / "vwf.txt"
TOP = 2           # file row 0 = cell row 2
SLICE = 0x480     # first slice code
LAST = 0xFFF
BLANK = 0x7FF     # the game's blank code: never a slice
GAP = re.compile(r"( {2,}|\|)")


def parse(path=FONT):
    """{char: (rows, advance)} in file order."""
    out, name, adv, rows = {}, None, None, []

    def done():
        if name is not None:
            assert len(rows) == 12, f"{name}: {len(rows)} rows, need 12"
            w = len(rows[0])
            assert all(len(r) == w for r in rows), f"{name}: ragged rows"
            assert w <= 7, f"{name}: {w} px wide, max 7"
            out[" " if name == "space" else name] = (rows, adv if adv is not None else w + 1)

    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#") and name is None or not line.strip():
            continue
        if line.startswith("== "):
            done()
            parts = line[3:].split(" ")
            name, adv, rows = parts[0], int(parts[1]) if len(parts) > 1 else None, []
        else:
            rows.append(line)
    done()
    return out


GLYPHS = parse()


def singles():
    """{char: code}"""
    out, extra = {}, 0x401
    for c in GLYPHS:
        if 0x20 <= ord(c) < 0x7F:
            out[c] = 0x400 + ord(c)
        else:
            out[c], extra = extra, extra + 1
    assert extra <= 0x420
    return out


SINGLES = singles()


def adv(s):
    return sum(GLYPHS[c][1] for c in s)


def ink(s):
    """px from the run's left edge to its last set column + 1 (adv without the last glyph's trailing gap)."""
    return adv(s[:-1]) + len(GLYPHS[s[-1]][0][0]) if s else 0


def runs(text):
    """[(x, run)] of a field's plain text. A run is cut at 2+ spaces or at "|". 2+ spaces keep the column a 2-letter-
    a-cell layout gave the run (16 px a pair, a lone space before it 4 px), so code that draws a number or cursor at
    a fixed cell still lines up; "|" starts the next 2-cell (32 px) unit (command cells picked by index). Letters
    inside a run are set at their advance."""
    out, i, x = [], 0, 0
    for part in GAP.split(text):
        if part == "|":
            x = -(-x // 32) * 32
        elif GAP.fullmatch(part):
            i += len(part)
            x = 16 * (i // 2) + 4 * (i % 2)
        elif part:
            out.append((x, part))
            x += adv(part)
            i += len(part)
    return out


def slices(text):
    """[cell] for text set by runs(): cell = (12 rows of 16 bits, bit 15 = leftmost px; advance) or None (blank),
    up to the last cell with ink. The last cell's advance runs to the text's end, the others' 16."""
    rows, end = [0] * 12, 0
    for x0, run in runs(text):
        x = x0
        for c in run:
            g, a = GLYPHS[c]
            for r, row in enumerate(g):
                for i, ch in enumerate(row):
                    if ch == "#":
                        rows[r] |= 1 << (x + i)
            x += a
        end = x
    n = max(((r.bit_length() + 15) // 16 for r in rows), default=0)
    out = []
    for k in range(n):
        cell = tuple(int(f"{(r >> 16 * k) & 0xFFFF:016b}"[::-1], 2) for r in rows)
        out.append((cell, 16 if k < n - 1 else min(16, end - 16 * k)) if any(cell) else None)
    return out


def slice_codes(cells):
    """{cell: code} for the sorted cells."""
    codes = [c for c in range(SLICE, LAST + 1) if c != BLANK]
    cells = sorted(set(cells))
    if len(cells) > len(codes):
        raise ValueError(f"{len(cells)} slices, room for {len(codes)}")
    return dict(zip(cells, codes))


def build(codes):
    """(font bytes, 4 banks of $8000; widths bytes $C00) for the singles plus these slice codes ({cell: code})."""
    font, widths = bytearray(0x20000), bytearray(LAST + 1 - 0x400)
    cells = {code: slices(c)[0] for c, code in SINGLES.items() if c != " "}
    cells.update({code: cell for cell, code in codes.items()})
    for c, code in SINGLES.items():
        widths[code - 0x400] = GLYPHS[c][1]
    for code, (rows, a) in cells.items():
        k = code - 0x400
        if code >= SLICE:
            widths[k] = a
        base = (k >> 10) * 0x8000 + (k >> 3 & 0x7F) * 0x100 + (k & 7) * 0x10
        for r, bits in enumerate(rows):
            o = base + (0x80 if r + TOP >= 8 else 0) + (r + TOP & 7)
            font[o], font[o + 8] = bits >> 8, bits & 0xFF
    return bytes(font), bytes(widths)


def selftest():
    assert SINGLES["A"] == 0x441 and SINGLES[" "] == 0x420
    assert runs("Yes   No") == [(0, "Yes"), (48, "No")] and runs("Use  (  )")[1] == (36, "(")
    assert runs("Rght|Left") == [(0, "Rght"), (32, "Left")]
    s = slices("Items")
    assert len(s) == 2 and s[0][1] == 16 and s[1][1] == adv("Items") - 16 and slices("A   B")[1] is None
    assert len(slices("Status")) == 3 and ink("Status") == adv("Status") - 1
    f, w = build(slice_codes(s))
    k = SLICE - 0x400
    assert w[0x41] == adv("A") and sorted(w[k:k + 2]) == sorted(c[1] for c in s)
    assert f[(k >> 3) * 0x100 + (k & 7) * 0x10 + TOP] or f[(k + 1 >> 3) * 0x100 + (k + 1 & 7) * 0x10 + TOP]
    print(f"selftest ok: {len(GLYPHS)} glyphs, widest {max(a for _, a in GLYPHS.values())} px")


if __name__ == "__main__":
    selftest()
