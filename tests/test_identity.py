"""Phase 3 identity: unpack + pack of every text block gives the original bytes. Phase 5: with every en empty, the
build changes nothing below the expansion but the hook bytes and the header checksum, and MSGTAB holds the
original message pointers."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Ruin Arm (Japan).sfc"
sys.path.insert(0, str(ROOT / "tools"))
needs_rom = pytest.mark.skipif(not ROM.is_file(), reason="no ROM dump in rom/")


@needs_rom
def test_identity_pack():
    from pack import off, unpack_all, write
    orig = ROM.read_bytes()
    rom = bytearray(orig)
    for b in unpack_all(orig):
        rom[off(b.addr):off(b.addr) + b.size()] = b"\xff" * b.size()
        write(rom, b)
    bad = [i for i, (x, y) in enumerate(zip(orig, rom)) if x != y]
    assert not bad, f"{len(bad)} bytes differ, first at {bad[0]:06X}"


@pytest.fixture(scope="module")
def untranslated(tmp_path_factory):
    """The build with every en empty (script/ copied with en cleared)."""
    import json
    import build
    import extract
    d = tmp_path_factory.mktemp("script")
    for p in extract.SCRIPT.glob("*.json"):
        es = json.loads(p.read_text(encoding="utf-8"))
        for e in es:
            if "en" in e:
                e["en"] = ""
        (d / p.name).write_text(json.dumps(es, ensure_ascii=False), encoding="utf-8")
    old, extract.SCRIPT = extract.SCRIPT, d
    try:
        return build.build(ROM.read_bytes())
    finally:
        extract.SCRIPT = old


@needs_rom
def test_untranslated_build_changes_only_hooks(untranslated):
    """Besides the hooks and checksum, only the script-independent engine data (name-entry grids, password)."""
    import build
    from asm import HOOKS, off
    orig = ROM.read_bytes()
    allowed = {o for a, b in HOOKS.items() for o in range(off(a), off(a) + len(b) // 2)} | set(range(0x7FDC, 0x7FE0))
    for o, old, _, by in (w.split(None, 3) for w in build.WRITES):
        if by.startswith(("grid_", "password")):
            allowed.update(range(int(o, 16), int(o, 16) + len(old) // 2))
    bad = [i for i, (x, y) in enumerate(zip(orig, untranslated)) if x != y and i not in allowed]
    assert len(untranslated) == 0x400000 and not bad, f"{len(bad)} bytes differ, first at {bad[0]:06X}" if bad else ""


@needs_rom
def test_msgtab_keeps_original_pointers(untranslated):
    from build import IDS, MSGTAB, msg_table
    from textdump import Script
    from pack import off
    o = off(MSGTAB)
    got = [int.from_bytes(untranslated[o + 3 * i:o + 3 * i + 3], "little") for i in range(IDS)]
    assert got == msg_table(Script(ROM.read_bytes()))


@needs_rom
def test_blocks_cover_known_ranges():
    """The packer covers every text range in docs/re/text.md, so the identity test proves all of them."""
    from pack import off, unpack_all
    spans = {b.name: (off(b.addr), off(b.addr) + b.size()) for b in unpack_all(ROM.read_bytes())}
    assert spans == {"dict": (0x018000, 0x018642), "msg00": (0x0C0000, 0x0C3CBE), "msg13": (0x0C3CBE, 0x0C5764),
                     "msg01": (0x01867E, 0x01B54A),  # 018642-01867E between dict and msg01: the block table
                     "msg11": (0x01B54A, 0x01EEA4), "msg02": (0x1D8000, 0x1D846A), "msg10": (0x1D846A, 0x1DBF0A),
                     "msg12": (0x1DBF0A, 0x1DFEDC), "staff": (0x18D3E2, 0x18D7D2)}


def test_pack_shares_and_next_slots():
    from pack import NEXT, Block, pack
    b = Block("t", 0x838000, [0, 1, 0, NEXT], [[0x0001, 0xFF00], [0xFFFF]], set())
    assert pack(b) == bytes.fromhex("0880 0c80 0880 0e80 0100 00ff ffff".replace(" ", ""))
    with pytest.raises(ValueError):
        pack(Block("t", 0x83FFFE, [0], [[0xFF00]], set()))
