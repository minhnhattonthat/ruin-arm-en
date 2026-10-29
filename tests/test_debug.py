"""Debug-tool facts (docs/re/debug.md): scene list parses, exit table and staff-roll strings where warp.lua expects."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Ruin Arm (Japan).sfc"
sys.path.insert(0, str(ROOT / "tools" / "debug"))
needs_rom = pytest.mark.skipif(not ROM.is_file(), reason="no ROM dump in rom/")


def off(a):
    return ((a & 0x7F0000) >> 1) | (a & 0x7FFF)


def test_scene_names():
    import warp
    names = warp.scene_names()
    assert len(names) == len(set(names))
    assert {"title", "field_start", "menu_items", "credits_0"} <= set(names)


@needs_rom
def test_exit_table():
    d = ROM.read_bytes()
    o = off(0x9AA093)
    ents = [d[o + i * 6:o + i * 6 + 6] for i in range(448)]
    assert ents[7][:2] == b"\x05\x1c", "exit 7 = village -> forest (map $1C05)"
    assert all(e[4] in (0xC0, 0xE0) for e in ents[:447]) and ents[447][4] not in (0xC0, 0xE0)
    maps = {e[0] | e[1] << 8 for e in ents[:447] if e[2] | e[3]}
    assert len(maps) == 187


@needs_rom
def test_staff_roll_strings():
    from tbl import Table
    t = Table.load(ROOT / "tbl" / "jp.tbl")
    d = ROM.read_bytes()
    p = d[off(0xB1D3E2)] | d[off(0xB1D3E2) + 1] << 8
    o, words = off(0xB10000 | p), []
    while (w := d[o] | d[o + 1] << 8) != 0xFFFF:
        if not w & 0x8000:
            words.append(w)
        o += 2
    data = b"".join(w.to_bytes(2, "little") for w in words)
    assert t.decode(data, length=len(data))[0].startswith("プロダクション")
