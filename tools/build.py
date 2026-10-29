"""build.py: build build/ruinarm_en.sfc from the dump in rom.sha1.

    python -X utf8 tools/build.py

Every text block (tools/pack.py) is wiped and packed back from its unpacked strings, so each of their bytes comes
from the packer; the en fields of script/*.json replace strings and fixed fields first (tools/extract.py). With every
en empty the output must equal the original: tests/test_identity.py.
"""
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_rom  # noqa: E402
from bps import snes_checksum  # noqa: E402
from extract import apply  # noqa: E402
from pack import off, unpack_all, write  # noqa: E402
from textdump import ROM, Script  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "ruinarm_en.sfc"


def build(orig):
    rom = bytearray(orig)
    blocks = unpack_all(orig)
    sizes = [b.size() for b in blocks]
    apply(Script(orig), blocks, rom)
    for b, n in zip(blocks, sizes):
        if b.size() > n:  # shortcut: no relocation yet; phase 5 moves grown blocks to free space
            raise SystemExit(f"{b.name}: English needs {b.size()} bytes, the block has {n}")
        rom[off(b.addr):off(b.addr) + n] = b"\xff" * n
    for b in blocks:
        write(rom, b)
    return snes_checksum(rom)[0]


def main():
    check_rom.check()
    orig = ROM.read_bytes()
    rom = build(orig)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_bytes(rom)
    print(f"{OUT.relative_to(ROOT)}: sha1 {hashlib.sha1(rom).hexdigest()}, "
          + ("identical to the original" if rom == orig else f"{sum(x != y for x, y in zip(orig, rom))} bytes changed"))


if __name__ == "__main__":
    main()
