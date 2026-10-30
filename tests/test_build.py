"""Phase 7: the English build. romdiff.py with the build's write log (every changed byte has a write, each write
found the original bytes it expected, none overwrote another), writes in the original 2.5 MB only where a writer is
allowed to go, and no Japanese a pointer still reaches."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Ruin Arm (Japan).sfc"
sys.path.insert(0, str(ROOT / "tools"))
pytestmark = pytest.mark.skipif(not ROM.is_file(), reason="no ROM dump in rom/")


@pytest.fixture(scope="module")
def built():
    import build
    orig = ROM.read_bytes()
    rom = build.build(orig)
    return orig, rom, list(build.WRITES)


def test_romdiff_writes(built, tmp_path):
    import romdiff
    orig, rom, writes = built
    log = tmp_path / "writes.txt"
    log.write_text("\n".join(writes) + "\n", encoding="utf-8")
    errs, _ = romdiff.check(orig, rom, set(), romdiff.load_writes(log))
    assert not errs, "\n".join(errs[:20])


def test_writes_in_allowed_places(built):
    """Inside the original ROM: text fields and the staff block in place, grid/password data, the asm hook sites,
    the header checksum. Everything else goes to the expansion (0x280000+)."""
    import asm
    import build
    import fixed
    from textdump import Script
    orig, rom, writes = built
    fields = {f["id"]: f["off"] - 3 * ("head" in f) for n, fs in fixed.fields(Script(orig)).items()
              for f in (fixed.built(Script(rom), fs) if n == "menu" else fs)}
    hooks = {asm.off(a) for a in asm.HOOKS}
    bad = []
    for w in writes:
        o, old, _, by = w.split(None, 3)
        o, n = int(o, 16), len(old) // 2
        if o >= len(orig):
            continue
        ok = (fields.get(by) == o or by.startswith(("grid_", "password"))
              or by == "staff_ptrs" and o == 0x18D3E2 or by == "staff" and o == asm.off(build.STAFF_TEXT)
              or by == "asm" and any(h <= o < h + 4 and o + n <= h + 4 for h in hooks)
              or by == "checksum" and 0x7FDC <= o and o + n <= 0x7FE0)
        if not ok:
            bad.append(w[:80])
    assert not bad, "\n".join(bad[:20])


def test_no_reachable_japanese(built):
    import jp_reach
    _, rom, _ = built
    keep = {ln.split()[0] for ln in (ROOT / "script" / "keep_jp.txt").read_text(encoding="utf-8").splitlines() if ln}
    left = [i for i, t in jp_reach.reach(rom) if jp_reach.JP.search(t) and i not in keep]
    assert not left, left[:10]
