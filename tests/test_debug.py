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
    assert {"title", "first_dialogue", "field_start", "menu_items", "credits_0"} <= set(names)


def test_failed_warp_cannot_reuse_old_evidence(tmp_path, monkeypatch):
    import subprocess
    import warp

    monkeypatch.setattr(warp, "ROOT", tmp_path)
    out = tmp_path / "qa" / "maps"
    out.mkdir(parents=True)
    for name in ("log.txt", "scene.png", "sheet.png", "sheet_2.png", "map_0000.png"):
        (out / name).write_text("READY maps 187", encoding="utf-8")
    monkeypatch.setattr(warp.subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, 1, "", "failed"))
    assert not warp.run("maps", tmp_path / "rom.sfc", out.parent, False)
    assert not list(out.iterdir())
    with pytest.raises(ValueError, match="invalid scene name"):
        warp.run("../maps", tmp_path / "rom.sfc", out.parent, False)


@needs_rom
def test_exit_table():
    d = ROM.read_bytes()
    o = off(0x9AA093)
    ents = [d[o + i * 6:o + i * 6 + 6] for i in range(1873)]
    assert ents[7][:2] == b"\x05\x1c", "exit 7 = village -> forest (map $1C05)"
    assert ents[447] == bytes(6), "the first empty slot is a hole, not the end of the table"
    assert ents[0x5BB][:2] == b"\x02\x1d", "ending staff-roll room"
    assert ents[0x742][:2] == b"\x02\x1e", "ending epilogue room"
    assert all(e[4] in (0, 0xC0, 0xD0, 0xE0) for e in ents[:1872])
    assert ents[1872][4] == 0x73, "the following pointer table starts here"
    maps = {e[0] | e[1] << 8 for e in ents[:1872] if e[2] | e[3]}
    assert len(maps) == 640


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
