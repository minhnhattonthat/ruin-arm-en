"""Phase 4: every extracted string re-encodes to its original words, sources don't overlap, script/ matches the ROM,
and en fields reach the built ROM."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Ruin Arm (Japan).sfc"
sys.path.insert(0, str(ROOT / "tools"))
needs_rom = pytest.mark.skipif(not ROM.is_file(), reason="no ROM dump in rom/")


@pytest.fixture(scope="module")
def s():
    from textdump import Script
    return Script()


@needs_rom
def test_roundtrip_every_string(s):
    import fixed
    from pack import unpack_all
    for b in unpack_all(s.d):
        for ws in b.strings:
            ws = ws[:-1] if b.name == "staff" else ws
            assert s.encode(s.text(ws)) == ws, (b.name, s.text(ws))
    for fs in fixed.fields(s).values():
        for f in fs:
            ws = fixed.words(s, f)
            got = s.encode(s.text(ws).rstrip(" "))
            assert got + [0] * (f["n"] - len(got)) == ws, f["id"]


@needs_rom
def test_sources_dont_overlap(s):
    """Blocks and fixed fields claim disjoint bytes; field counts pinned (a sweep change shows up here)."""
    import fixed
    from pack import off, unpack_all
    spans = [(off(b.addr), off(b.addr) + b.size(), b.name) for b in unpack_all(s.d)]
    t = fixed.fields(s)
    spans += [(f["off"], f["off"] + 2 * f["n"], f["id"]) for fs in t.values() for f in fs]
    spans.sort()
    clash = [(x[2], y[2]) for x, y in zip(spans, spans[1:]) if y[0] < x[1]]
    assert not clash
    assert {k: len(v) for k, v in t.items()} == {
        "menu": 308, "item": 110, "place": 72, "name_hero": 16, "name_sister": 16, "ingot": 16, "equip": 9,
        "tactic": 5, "pad": 3, "use": 2, "act": 2, "element": 4, "heat": 2, "status": 11}


@needs_rom
def test_script_files_match_rom(s):
    from extract import SCRIPT, load, sources
    from pack import unpack_all
    for name, fresh in sources(s, unpack_all(s.d)).items():
        assert (SCRIPT / f"{name}.json").exists(), f"script/{name}.json missing: run tools/extract.py"
        load(name, fresh)


def test_codec_tokens():
    from textdump import Script
    s = Script(rom=b"")
    t = "あ{col:01}{name:04}\n{choice:01:1234:1235:1236}{d:1B|x}{pos:00C4}[0355]{end}"
    ws = s.encode(t)
    assert ws == [0x0001, 0xFC01, 0xF204, 0xF600, 0xF901, 0x1234, 0x1235, 0x1236, 0xF81B, 0x80C4, 0x0355, 0xFF00]
    with pytest.raises(ValueError):
        s.encode("{goto:00}")  # goto needs its target word
    with pytest.raises(ValueError):
        s.encode("{bogus}")


@needs_rom
def test_en_reaches_rom(s, tmp_path, monkeypatch):
    """A message (relocated, MSGTAB points at it, singles) and a fixed field (in place, digraphs) with en set come out
    of the build with those words."""
    import build
    import extract
    import fixed
    from en import Codec
    from pack import off
    ids = {}
    for name in ("msg13", "item"):
        e = json.loads((extract.SCRIPT / f"{name}.json").read_text(encoding="utf-8"))
        e[1]["en"] = "AB{end}" if name == "msg13" else "AB"
        ids[name] = e[1]
        (tmp_path / f"{name}.json").write_text(json.dumps(e, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(extract, "SCRIPT", tmp_path)
    rom = build.build(s.d)
    from textdump import Script
    r = Script(rom)
    for mid in [ids["msg13"]["id"]] + ids["msg13"].get("slots", []):
        o = off(build.MSGTAB) + 3 * int(mid, 16)
        a = int.from_bytes(rom[o:o + 3], "little")
        assert a >= build.TEXT and r.words(off(a))[0] == Codec().msg("AB{end}"), mid
    f = fixed.fields(s)["item"][1]
    assert fixed.words(r, f) == [Codec.pairs_in(["AB"])["AB"]] + [0] * 7
