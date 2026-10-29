"""font.py: fonts/vwf.txt -> the English glyph codes, their cells and widths (asm/vwf.asm, docs/re/font.md §English).

English text uses codes $0400-$07FE, drawn from a second font bank (FONT2, same cell layout as $9F8000) by the hooks
in asm/vwf.asm:
- singles: printable ASCII c -> $0400 + c; other font characters (— ： × …) -> $0401.. in file order.
  Messages use singles only: the dialogue VWF draws each at its advance.
- digraphs: $0480.. two letters in one 16 px cell, for the fixed-width menu fields (16 letters in an 8-cell item name).
  Assigned per build from the pairs the fixed fields use (pairs()), so the set follows the script.
widths: advance in px per code - $400 (digraph = sum of both). Codes below $400 (Japanese cells) are 16 px.

    python -X utf8 tools/font.py     # selftest + summary
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FONT = ROOT / "fonts" / "vwf.txt"
TOP = 2           # file row 0 = cell row 2
DIGRAPH = 0x480   # first digraph code
LAST = 0x7FE      # $07FF is the game's blank code


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


def pair_codes(pairs):
    """{two-char string: code} for the sorted pairs."""
    pairs = sorted(set(pairs))
    if DIGRAPH + len(pairs) > LAST + 1:
        raise ValueError(f"{len(pairs)} digraphs, room for {LAST + 1 - DIGRAPH}")
    return {p: DIGRAPH + i for i, p in enumerate(pairs)}


def adv(s):
    return sum(GLYPHS[c][1] for c in s)


def build(pairs):
    """(font bank bytes $8000, widths bytes $400) for the singles plus these digraph codes ({pair: code})."""
    font, widths = bytearray(0x8000), bytearray(0x400)
    cells = {code: c for c, code in SINGLES.items()}
    cells.update({code: p for p, code in pairs.items()})
    for code, s in cells.items():
        k = code - 0x400
        widths[k] = adv(s)
        if len(s) == 2 and widths[k] > 16:
            raise ValueError(f"digraph {s!r} is {widths[k]} px, a cell holds 16")
        bits = [0] * 16  # 16-bit rows, bit 15 = leftmost pixel
        x = 0
        for c in s:
            rows, a = GLYPHS[c]
            for r, row in enumerate(rows):
                for i, ch in enumerate(row):
                    if ch == "#":
                        bits[TOP + r] |= 0x8000 >> (x + i)
            x += a
        base = (k >> 3) * 0x100 + (k & 7) * 0x10
        for r in range(16):
            o = base + (0x80 if r >= 8 else 0) + (r & 7)
            font[o], font[o + 8] = bits[r] >> 8, bits[r] & 0xFF
    return bytes(font), bytes(widths)


def selftest():
    assert SINGLES["A"] == 0x441 and SINGLES[" "] == 0x420
    f, w = build(pair_codes(["It", "em"]))
    assert w[0x41] == adv("A") and w[DIGRAPH - 0x400] == adv("It")
    k = DIGRAPH - 0x400  # "It" (sorts first): the I's top row is set in the TL tile
    assert f[(k >> 3) * 0x100 + (k & 7) * 0x10 + TOP] != 0
    print(f"selftest ok: {len(GLYPHS)} glyphs, widest {max(a for _, a in GLYPHS.values())} px")


if __name__ == "__main__":
    selftest()
