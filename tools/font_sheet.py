"""Render the 16x16 1bpp dialogue font (docs/re/text.md) as a labelled sheet.

    python tools/font_sheet.py OUT.png [--first 0x000] [--count 0x100] [--zoom 2]
    python tools/font_sheet.py OUT.png --codes 115,117,1A2 --zoom 6

Glyph code c lives at ROM $9F8000 + (c>>3)*0x100 + (c&7)*0x10: four 8x8 1bpp tiles (TL +0, TR +8, BL +0x80, BR +0x88).
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw

ROM = Path(__file__).resolve().parent.parent / "rom" / "Ruin Arm (Japan).sfc"
FONT = 0x0F8000  # file offset of $9F8000 (LoROM)


def glyph(rom, c):
    """16x16 list of 0/1 rows for glyph code c."""
    base = FONT + (c >> 3) * 0x100 + (c & 7) * 0x10
    rows = []
    for half in (0, 0x80):
        for y in range(8):
            left, right = rom[base + half + y], rom[base + half + 8 + y]
            rows.append([(left >> (7 - x)) & 1 for x in range(8)] + [(right >> (7 - x)) & 1 for x in range(8)])
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--first", type=lambda s: int(s, 0), default=0)
    ap.add_argument("--count", type=lambda s: int(s, 0), default=0x100)
    ap.add_argument("--codes", help="comma-separated hex codes instead of a range")
    ap.add_argument("--zoom", type=int, default=2)
    a = ap.parse_args()
    rom = ROM.read_bytes()
    codes = [int(c, 16) for c in a.codes.split(",")] if a.codes else list(range(a.first, a.first + a.count))
    cols, cell = 16 if a.zoom < 4 else 8, 16 * a.zoom + 4
    lab = 12
    img = Image.new("RGB", (cols * cell, ((len(codes) + cols - 1) // cols) * (cell + lab)), "white")
    d = ImageDraw.Draw(img)
    for i, c in enumerate(codes):
        x0, y0 = (i % cols) * cell, (i // cols) * (cell + lab)
        d.text((x0 + 1, y0), f"{c:03X}", fill="red")
        for y, row in enumerate(glyph(rom, c)):
            for x, bit in enumerate(row):
                if bit:
                    d.rectangle([x0 + 2 + x * a.zoom, y0 + lab + y * a.zoom,
                                 x0 + 1 + (x + 1) * a.zoom, y0 + lab - 1 + (y + 1) * a.zoom], fill="black")
    img.save(a.out)
    print(a.out)


if __name__ == "__main__":
    main()
