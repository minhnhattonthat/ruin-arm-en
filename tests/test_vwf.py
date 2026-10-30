"""Phase 5: English font, codec and marker build (docs/re/vwf.md)."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Ruin Arm (Japan).sfc"
sys.path.insert(0, str(ROOT / "tools"))
needs_rom = pytest.mark.skipif(not ROM.is_file(), reason="no ROM dump in rom/")


def test_font_and_codec():
    import font
    from en import Codec
    font.selftest()
    c = Codec(["Items"])
    assert c.msg("Hi\n") == [0x448, 0x469, 0xF600]
    assert c.field("Items") == [font.SLICE, font.SLICE + 1] or c.field("Items") == [font.SLICE + 1, font.SLICE]


def test_marker_marks_every_text_string():
    import marker
    from extract import SCRIPT
    for p in SCRIPT.glob("msg*.json"):
        for e in json.loads(p.read_text(encoding="utf-8")):
            text = any(not ch.isascii() for ch in e["jp"])
            if e["id"].startswith("orphan") or not text:
                continue
            en = marker.GATE.get(e["id"]) or marker.message(e["id"], e["jp"])
            assert f"#{e['id']}" in en and not any(not ch.isascii() for ch in en if ch not in "×…—："), e["id"]


@needs_rom
def test_marker_build(tmp_path, monkeypatch):
    """Every marker string encodes and fits (fields, staff in place; messages relocated) and the gate lines are
    exactly marker.LINE px."""
    import build
    import extract
    import marker
    from font import adv
    monkeypatch.setattr(marker, "OUT", tmp_path)
    marker.main()
    monkeypatch.setattr(extract, "SCRIPT", tmp_path)
    rom = build.build(ROM.read_bytes())
    assert len(rom) == build.SIZE
    import jp_reach
    keep = {ln.split()[0] for ln in (ROOT / "script" / "keep_jp.txt").read_text(encoding="utf-8").splitlines() if ln}
    left = [i for i, t in jp_reach.reach(rom) if jp_reach.JP.search(t) and i not in keep]
    assert not left, left[:10]
    lines = marker.GATE["1032"].split("{wait}")[0].split("\n")[1:]
    assert len(lines) == 3 and all(adv(x) == marker.LINE for x in lines)
