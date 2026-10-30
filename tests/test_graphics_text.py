from pathlib import Path

import pytest

from lz import decompress
from unused_tiles import POINTER, SOURCE

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Ruin Arm (Japan).sfc"


@pytest.mark.skipif(not ROM.is_file(), reason="no ROM dump")
def test_relocated_tiles_preserve_all_non_marker_art():
    import build
    original = ROM.read_bytes()
    result = build.build(original)
    target = int.from_bytes(result[POINTER:POINTER + 3], "little")
    offset = ((target & 0x7F0000) >> 1) | (target & 0x7FFF)
    before, _ = decompress(original, SOURCE)
    after, _ = decompress(result, offset)
    assert len(after) == len(before) == 8192
    changed = {i // 32 for i in range(8192) if before[i] != after[i]}
    assert changed == {29, 30, 175, 244, 245, 246, 247, 248, 249, 250, 251}


@pytest.mark.skipif(not ROM.is_file(), reason="no ROM dump")
def test_worldmap_font_keeps_native_extent_and_service_icons(tmp_path):
    import worldmap
    original = ROM.read_bytes()
    source, _ = decompress(original, worldmap.SOURCE)
    assert worldmap.generate(tmp_path, original) == 0x7B0
    result = (tmp_path / "worldmap.bin").read_bytes()
    for tile in worldmap.RESERVED:
        offset = (tile - 0x100) * 16
        assert result[offset:offset + 16] == source[0x2400 + offset:0x2410 + offset]
