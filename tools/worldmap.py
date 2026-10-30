"""Build the world-map card font and tile lists; names follow glossary.md.

The original cards use Japanese bitmap tiles, not the message font. Reuse only
their original glyph slots, preserving borders/icons and the existing DMA range.
VRAM beyond that range holds cached map art even when the world map does not use it.
"""
from pathlib import Path

from font import GLYPHS
from lz import decompress

NAMES = (
    "Arff", "Kingdom of Rondium", "Wyall", "Maria", "Beastfolk Village Rau",
    "Stelm Duchy", "Worth", "Kingdom of Marsnal", "Ravenna", "Rutea Region",
    "Tifnu Region", "Kingdom of Medeom", "Raidroid Empire",
)
POINTERS = (0xCAF1, 0xCB09, 0xCB39, 0xCB55, 0xCB6D, 0xCB99, 0xCBC1,
            0xCBD9, 0xCC05, 0xCC21, 0xCC4D, 0xCC71, 0xCC9D)
BLANK = 0x3111
SOURCE = 0x1A062A  # $B4862A
RESERVED = {0x100, 0x101, 0x110, 0x111, 0x162, 0x172, 0x174, *range(0x163, 0x170), 0x173}


def generate(folder: Path, original):
    alphabet = sorted(set("".join(NAMES) + "Travel here?YesNo") - {" "})
    available = [tile for tile in range(0x100, 0x17B) if tile not in RESERVED]
    assert len(alphabet) * 2 <= len(available)
    codes = {char: available[2 * i:2 * i + 2] for i, char in enumerate(alphabet)}
    source, _ = decompress(original, SOURCE)
    pixels = bytearray(source[0x2400:0x2BB0])
    for tile in available:
        offset = (tile - 0x100) * 16
        pixels[offset:offset + 16] = b"\xff\x00" * 8
    for char in alphabet:
        rows, _ = GLYPHS[char]
        left = (8 - len(rows[0])) // 2
        masks = [0, 0] + [sum(1 << (7 - left - x) for x, p in enumerate(row) if p == "#") for row in rows] + [0, 0]
        for half, tile in enumerate(codes[char]):
            offset = (tile - 0x100) * 16
            for row, mask in enumerate(masks[half * 8:half * 8 + 8]):
                pixels[offset + row * 2:offset + row * 2 + 2] = bytes((0xFF, mask))
    assert len(pixels) == 0x7B0
    (folder / "worldmap.bin").write_bytes(pixels)
    lines, entries = [], []

    def text(value, bottom=False):
        return [BLANK if c == " " else 0x2000 | codes[c][int(bottom)] for c in value]

    def record(old, name, rows):
        width = len(rows[0][2])
        assert all(len(data) == width for _, _, data in rows)
        entries.append((old, name))
        lines.append(f"{name}:\n\tdw ${width * 2:04X}")
        for i, (row, col, _) in enumerate(rows):
            assert 0 <= col and col + width <= 32
            lines.append(f"\tdw ${(row * 32 + col) * 2:04X}, {name}_{i}")
        lines.append("\tdw 0")
        for i, (_, _, data) in enumerate(rows):
            lines.append(f"{name}_{i}:\n\tdw " + ",".join(f"${w:04X}" for w in data))

    def frame(width, height):
        return [[0x3100] + [0x3101] * (width - 2) + [0x7100]] + [
            [0x3110] + [BLANK] * (width - 2) + [0x7110] for _ in range(height - 2)
        ] + [[0xB100] + [0xB101] * (width - 2) + [0xF100]]

    record(0xC902, "wm_frame", [(9 + i, 3, row) for i, row in enumerate(frame(26, 6))])
    for i, (ptr, name) in enumerate(zip(POINTERS, NAMES)):
        record(ptr, f"wm_card_{i}", [(10, 5, text(name)), (11, 5, text(name, True))])

    def choices(no=False, bottom=False):
        result = text(" Yes   No ", bottom)
        if no is not None:
            result[6 if no else 0] = 0x3572 if bottom else 0x3562
        return result

    prompt = frame(16, 6)
    prompt[1][1:13] = text("Travel here?")
    prompt[2][1:13] = text("Travel here?", True)
    prompt[3][1:11] = choices(None)
    prompt[4][1:11] = choices(None, True)
    record(0xC96C, "wm_travel", [(19 + i, 14, row) for i, row in enumerate(prompt)])
    for old, no in ((0xC988, False), (0xC994, True)):
        record(old, f"wm_choice_{int(no)}", [(22, 15, choices(no)), (23, 15, choices(no, True))])
    lookup = ["worldmap_lists:"] + [f"\tdw ${old:04X}, {name}" for old, name in entries] + ["\tdw 0"]
    (folder / "worldmap.asm").write_text("\n".join(lookup + lines) +
                                       '\nworldmap_font_data:\n\tincbin "worldmap.bin"\n', encoding="utf-8")
    return len(pixels)
