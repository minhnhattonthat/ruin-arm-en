import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Ruin Arm (Japan).sfc"
sys.path.insert(0, str(ROOT / "tools"))


@pytest.mark.skipif(not ROM.is_file(), reason="no ROM dump in rom/")
def test_rom_matches_sha1():
    import check_rom
    check_rom.check()  # sys.exit on mismatch fails the test


def test_sha1_listing_filled():
    lines = [l for l in (ROOT / "rom.sha1").read_text(encoding="utf-8").splitlines() if l and not l.startswith("#")]
    assert lines and all(len(l.split(None, 1)[0]) == 40 for l in lines)
