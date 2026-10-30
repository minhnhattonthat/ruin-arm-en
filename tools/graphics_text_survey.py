"""Render the built bitmap-text assets for independent visual review."""
import argparse
from pathlib import Path

from gfx_survey import interleave, tiles
from lz import decompress
from unused_tiles import POINTER


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rom", type=Path, default=Path("build/ruinarm_en.sfc"))
    ap.add_argument("--out", type=Path, default=Path("work/qa/graphics_fixes/assets"))
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    rom = args.rom.read_bytes()
    address = int.from_bytes(rom[POINTER:POINTER + 3], "little")
    offset = ((address & 0x7F0000) >> 1) | (address & 0x7FFF)
    raw, _ = decompress(rom, offset)
    (args.out / "unused_tiles.bin").write_bytes(raw)
    tiles.render(interleave(raw), "snes4", tiles.palette(None, 0, 4), 16, 4,
                 str(args.out / "sheet_unused_tiles.png"))
    font = Path("build/vwf/worldmap.bin").read_bytes()
    tiles.render(font, "snes2", tiles.palette(None, 0, 2), 16, 4,
                 str(args.out / "sheet_worldmap_font.png"))
    (args.out / "index.txt").write_text(
        f"City tiles: pointer $8C8300 -> ${address:06X}; eleven marker tiles changed.\n"
        "World map: original BG3 glyph range $100-$17A; borders/icons preserved, card captures verify spacing.\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
