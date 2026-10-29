"""Phase 3 identity build: unpack every text block, wipe it, pack it back: the ROM must come out byte-identical."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Ruin Arm (Japan).sfc"
sys.path.insert(0, str(ROOT / "tools"))
needs_rom = pytest.mark.skipif(not ROM.is_file(), reason="no ROM dump in rom/")


@needs_rom
def test_identity_build():
    from build import build
    orig = ROM.read_bytes()
    rom = build(orig)
    bad = [i for i, (x, y) in enumerate(zip(orig, rom)) if x != y]
    assert len(rom) == len(orig) and not bad, f"{len(bad)} bytes differ, first at {bad[0]:06X}" if bad else "size"


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
