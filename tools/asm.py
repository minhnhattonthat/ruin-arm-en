"""asm.py: apply asm/vwf.asm to a ROM image with tools/asar/asar.exe (asar 1.91, github.com/RPGHacker/asar).

patch(rom, defs, widths) -> bytes: writes build/vwf/defs.asm (asar defines) and widths.bin, then runs asar on a
temp copy. The release step owns the checksum (--fix-checksum=off)."""
import subprocess
import sys
import tempfile
from pathlib import Path

import worldmap
import unused_tiles

ROOT = Path(__file__).resolve().parents[1]
ASAR = ROOT / "tools" / "asar" / "asar.exe"
ASM = ROOT / "asm" / "vwf.asm"
GEN = ROOT / "build" / "vwf"
# Every org in asm/vwf.asm below the expansion: CPU address -> the original bytes it replaces (checked before
# patching, so another revision or a moved routine fails here, not in game). docs/re/vwf.md lists why each exists.
HOOKS = {0x81E1CC: "aaadb10c", 0x81E227: "68a81869", 0x81E8B7: "ada50c29", 0x81E4B9: "69a100",
         0x81E92E: "8ac9007f", 0x85EC2D: "8ac9007f", 0x8296F0: "a20000bf", 0xAFEF30: "22958f80",
         0x849B63: "2229e981", 0x80C62A: "22018f80", 0x80C8CF: "8600a98000",
         0x8C8300: "a8a9b5"}


def off(a):
    return ((a & 0x7F0000) >> 1) | (a & 0x7FFF)


def patch(rom, defs, widths):
    for a, b in HOOKS.items():
        if rom[off(a):off(a) + len(b) // 2].hex() != b:
            raise SystemExit(f"hook {a:06X}: expected {b}, found {rom[off(a):off(a) + len(b) // 2].hex()}")
    if not ASAR.is_file():
        sys.exit(f"{ASAR} missing: unzip asar191.zip from github.com/RPGHacker/asar/releases (v1.91) there")
    GEN.mkdir(parents=True, exist_ok=True)
    defs = dict(defs, WORLD_FONT_SIZE=worldmap.generate(GEN, rom))
    unused_tiles.generate(GEN, rom)
    (GEN / "defs.asm").write_text("".join(f"!{k} = ${v:06X}\n" for k, v in defs.items()), encoding="utf-8")
    (GEN / "widths.bin").write_bytes(widths)
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "rom.sfc"
        p.write_bytes(rom)
        r = subprocess.run([str(ASAR), "--fix-checksum=off", str(ASM), str(p)], capture_output=True, text=True)
        if r.returncode:
            sys.exit(f"asar failed:\n{r.stdout}{r.stderr}")
        return p.read_bytes()
