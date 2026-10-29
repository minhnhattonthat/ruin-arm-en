"""Phase-1 recon facts as tests (docs/re/text.md, compression.md)."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Ruin Arm (Japan).sfc"
sys.path.insert(0, str(ROOT / "tools"))
needs_rom = pytest.mark.skipif(not ROM.is_file(), reason="no ROM dump in rom/")


def test_jp_table_one_to_one():
    from tbl import Table
    t = Table.load(ROOT / "tbl" / "jp.tbl")
    assert len(t.dec) == len(t.enc) == 0x356, "every glyph needs its own value"


def test_lz_codec_samples():
    from lz import compress, decompress
    for sample in (b"", b"x", b"abc" * 50, bytes(range(256)) * 2):
        assert decompress(compress(sample))[0] == sample


@needs_rom
def test_lz_real_block():
    import lz
    lz.selftest()


@needs_rom
def test_script_decodes_and_tiles_ranges():
    """Every message decodes with no unknown glyph, and messages (plus the two known orphans) tile each block."""
    from textdump import Script
    s = Script()
    spans = set()
    for _, mo in s.messages():
        ws, end = s.words(mo)
        assert "[" not in s.text(ws).replace("〔[", ""), hex(mo)  # textdump writes unknown glyphs as [XXXX]
        spans.add((mo, end))
    spans |= {(0x01B834, 0x01B856), (0x1DF416, 0x1DF418)}  # orphan message, stray F600
    for _, p in s.blocks():  # each block's pointer table
        bo = (p & 0x7F0000) >> 1 | p & 0x7FFF
        spans.add((bo, bo + s.w(bo) - (p & 0xFFFF)))
    starts = sorted(spans)
    gaps = [(e, b) for (_, e), (b, _) in zip(starts, starts[1:]) if b > e and e >> 15 == b >> 15]
    assert not gaps, [(hex(e), hex(b)) for e, b in gaps]  # text areas are contiguous within each bank
    overlaps = [(hex(a), hex(b)) for (a, e), (b, _) in zip(starts, starts[1:]) if a < b < e]
    assert not overlaps
