"""build.py: build build/ruinarm_en.sfc from the dump in rom.sha1.

    python -X utf8 tools/build.py [--script DIR] [--out FILE]     # --script: another script/ (the marker build)

The ROM grows to 4 MB (the header already says 4 MB); asm/vwf.asm (tools/asm.py) adds the dialogue VWF, the
English font bank and a 24-bit pointer per message id (MSGTAB, read by the hook at $81E8B7). en of script/*.json:
- messages: encoded in singles (tools/en.py), written to the expansion (TEXT on), MSGTAB points there; an untranslated
  message keeps pointing at its original bytes, which stay in place.
- fixed fields: in place, digraphs (names: singles), space-padded (tools/fixed.py).
- staff roll: digraphs, repacked in place (tools/pack.py). The dictionary stays Japanese (D9).
The phase-3 identity (unpack + pack = original bytes) is tests/test_identity.py.
"""
import argparse
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import asm  # noqa: E402
import check_rom  # noqa: E402
import extract  # noqa: E402
import fixed  # noqa: E402
import font  # noqa: E402
from bps import snes_checksum  # noqa: E402
from en import Codec  # noqa: E402
from pack import NEXT, off, unpack_all, write  # noqa: E402
from textdump import BLOCKS, ROM, Script  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "ruinarm_en.sfc"
SIZE = 0x400000
FONT2 = 0xD08000            # 32 KB: English cells (tools/font.py), same layout as $9F8000
MSGTAB = 0xD28000           # 0x14 blocks x 256 ids x 3 bytes
TEXT = 0xD2C000             # relocated messages from here to the end of the ROM, never across a bank
SINGLE_FIELDS = {"name_hero", "name_sister", "name_party"}  # names are edited per letter in the name entry: one letter a code
IDS = 0x1400


def words_bytes(ws):
    return b"".join(w.to_bytes(2, "little") for w in ws)


def msg_table(s):
    """Original resolved address of every message id (what $81E8B7 computed), MSGTAB's untranslated value."""
    out = []
    for b in range(IDS >> 8):
        o = off(BLOCKS) + 3 * b
        p = s.d[o] | s.d[o + 1] << 8 | s.d[o + 2] << 16
        out += [p & 0xFF0000 | s.w(off(p) + 2 * i) for i in range(256)]
    return out


def build(orig):
    rom = bytearray(orig.ljust(SIZE, b"\xff"))
    s = Script(orig)
    blocks = unpack_all(orig)
    ents = {b.name: extract.load(b.name, extract.block_entries(s, b)) for b in blocks}
    flds = fixed.fields(s)
    fents = {n: extract.load(n, extract.field_entries(s, fs)) for n, fs in flds.items()}
    codec = Codec(Codec.pairs_in([e["en"] for n, es in fents.items() if n not in SINGLE_FIELDS for e in es]
                                 + [e["en"] for e in ents["staff"]]))
    for n, fs in flds.items():
        for f, e in zip(fs, fents[n]):
            if e["en"]:
                fixed.put(rom, f, (codec.msg if n in SINGLE_FIELDS else codec.field)(e["en"]))
    staff = next(b for b in blocks if b.name == "staff")
    size = staff.size()
    for i, e in enumerate(ents["staff"]):
        if e["en"]:
            staff.strings[i] = codec.field(e["en"]) + [e["hold"]]
    if staff.size() > size:  # shortcut: in place only; relocate the staff strings if English credits outgrow them
        raise SystemExit(f"staff: English needs {staff.size()} bytes, the block has {size}")
    rom[off(staff.addr):off(staff.addr) + size] = b"\xff" * size
    write(rom, staff)

    tab, cur, new = msg_table(s), TEXT, {}
    for b in blocks:
        if not b.name.startswith("msg"):
            continue
        for i, e in enumerate(ents[b.name]):
            if not e["en"]:
                continue
            data = words_bytes(codec.msg(e["en"]))
            if (cur & 0xFFFF) + len(data) > 0x10000:
                cur = (cur & 0xFF0000) + 0x18000
            if cur >= 0x1000000:
                raise SystemExit("relocated messages overflow the 4 MB ROM")
            rom[off(cur):off(cur) + len(data)] = data
            new[b.addr, i] = cur
            cur += len(data)
    for blk in range(IDS >> 8):
        o = off(BLOCKS) + 3 * blk
        p = orig[o] | orig[o + 1] << 8 | orig[o + 2] << 16
        b = next(x for x in blocks if x.addr == p)
        for k, i in enumerate(b.slots):
            if i != NEXT and (p, i) in new:
                tab[blk << 8 | k] = new[p, i]
    rom[off(MSGTAB):off(MSGTAB) + 3 * IDS] = b"".join(a.to_bytes(3, "little") for a in tab)

    cells, widths = font.build(codec.pairs)
    rom[off(FONT2):off(FONT2) + len(cells)] = cells
    rom = asm.patch(bytes(rom), {"FONT2": FONT2, "MSGTAB": MSGTAB}, widths)
    return snes_checksum(bytearray(rom))[0]


def slots(rom):
    """"SLOT TARGET" file offsets of every pointer the game reads text through (jp_left.py --slots): MSGTAB ids
    (unused ids point at the next block's table: left out), staff strings, and each fixed field (its own slot)."""
    s, out = Script(rom), []
    tables = {off(p) for _, p in Script(ROM.read_bytes()).blocks()}
    for i in range(IDS):
        o = off(MSGTAB) + 3 * i
        t = off(int.from_bytes(rom[o:o + 3], "little"))
        if t not in tables:
            out.append(f"{o:06X} {t:06X}")
    staff = next(b for b in unpack_all(rom) if b.name == "staff")
    out += [f"{off(staff.addr) + 2 * k:06X} {off(staff.addr & 0xFF0000 | s.w(off(staff.addr) + 2 * k)):06X}"
            for k in range(len(staff.slots))]
    out += [f"{f['off']:06X} {f['off']:06X}" for fs in fixed.fields(Script(ROM.read_bytes())).values() for f in fs]
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", type=Path, help="script directory (default script/)")
    ap.add_argument("--out", type=Path, default=OUT)
    a = ap.parse_args()
    if a.script:
        extract.SCRIPT = a.script
    check_rom.check()
    orig = ROM.read_bytes()
    rom = build(orig)
    a.out.parent.mkdir(exist_ok=True)
    a.out.write_bytes(rom)
    a.out.with_suffix(".slots.txt").write_text(slots(rom), encoding="utf-8")
    print(f"{a.out.resolve().relative_to(ROOT).as_posix()}: sha1 {hashlib.sha1(rom).hexdigest()}, {len(rom)} bytes")


if __name__ == "__main__":
    main()
