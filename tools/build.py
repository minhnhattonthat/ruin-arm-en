"""build.py: build build/ruinarm_en.sfc from the dump in rom.sha1.

    python -X utf8 tools/build.py [--script DIR] [--out FILE]     # --script: another script/ (the marker build)

The ROM grows to 4 MB (the header already says 4 MB); asm/vwf.asm (tools/asm.py) adds the dialogue VWF, the
English font bank and a 24-bit pointer per message id (MSGTAB, read by the hook at $81E8B7). en of script/*.json:
- messages: encoded in singles (tools/en.py), written to the expansion (TEXT on), MSGTAB points there; an untranslated
  message keeps pointing at its original bytes, which stay in place.
- fixed fields: in place, digraphs (names: singles), space-padded (tools/fixed.py).
- staff roll: digraphs; pointers in place, strings moved to STAFF_TEXT. The dictionary stays Japanese (D9).
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
from pack import NEXT, off, unpack_all  # noqa: E402
from textdump import BLOCKS, ROM, Script  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "ruinarm_en.sfc"
SIZE = 0x400000
FONT2 = 0xD08000            # 32 KB: English cells (tools/font.py), same layout as $9F8000
MSGTAB = 0xD28000           # 0x14 blocks x 256 ids x 3 bytes
TEXT = 0xD2C000             # relocated messages from here to the end of the ROM, never across a bank
SINGLE_FIELDS = {"name_hero", "name_sister", "name_party"}  # names are edited per letter in the name entry: one letter a code
IDS = 0x1400
STAFF_TEXT = 0xB1EC00       # staff strings: $FF tail of bank $B1 (from $B1:EB54); its pointers are 16-bit, bank $B1
PASSWORD = (0x011711, "RAIDROID")  # $829711: the 8 words the typed ruin password must match (asm/vwf.asm `password`)
# Name-entry grids かな/漢1/漢2 -> ABC/abc/Sym (docs/re/text.md §Name entry): (row pointer table, original row count,
# offsets of that count's immediate in both entry routines $85B1C8/$85BDA0, English rows of 5 + blank + 5 cells).
# A kanji row starts with its reading and a blank (2 words, written blank); a kana row has its number drawn by code.
GRIDS = [
    (0x026410, 0x1B, (0x2B1D5, 0x2B22C, 0x2B231, 0x2B339, 0x2BDAF, 0x2BE07, 0x2BE0C, 0x2BE9B),
     ["ABCDE FGHIJ", "KLMNO PQRST", "UVWXY Z.-'!", "01234 56789"], ""),
    (0x026698, 0x27, (0x2B480, 0x2B4D7, 0x2B4DC, 0x2B5EA, 0x2BF0A, 0x2BF62, 0x2BF67, 0x2BFFC),
     ["abcde fghij", "klmno pqrst", "uvwxy z.-'!", "01234 56789"], "  "),
    (0x026ADC, 0x26, (0x2B63D, 0x2B694, 0x2B699, 0x2B7A7, 0x2C04F, 0x2C0A7, 0x2C0AC, 0x2C141),
     ["01234 56789", ".,!?' -:;/&", "()[]* #+~=%"], "  "),
]


WRITES = []                 # "OFF ORIG NEW BY" lines of the last build() (romdiff.py --writes)


def words_bytes(ws):
    return b"".join(w.to_bytes(2, "little") for w in ws)


def put(rom, o, data, by, orig):
    """The only way build() changes rom: logs the write against the clean original's bytes."""
    WRITES.append(f"{o:X} {orig[o:o + len(data)].ljust(len(data), b'\xff').hex()} {data.hex()} {by}")
    rom[o:o + len(data)] = data


def log_diff(before, after, by, orig):
    """Log each changed span of a step that writes on its own (asar, the checksum)."""
    i, n = 0, len(after)
    while i < n:
        if before[i] == after[i]:
            i += 1
            continue
        j = i
        while j < n and before[j] != after[j]:
            j += 1
        WRITES.append(f"{i:X} {orig[i:j].ljust(j - i, b'\xff').hex()} {after[i:j].hex()} {by}")
        i = j


def msg_table(s):
    """Original resolved address of every message id (what $81E8B7 computed), MSGTAB's untranslated value."""
    out = []
    for b in range(IDS >> 8):
        o = off(BLOCKS) + 3 * b
        p = s.d[o] | s.d[o + 1] << 8 | s.d[o + 2] << 16
        out += [p & 0xFF0000 | s.w(off(p) + 2 * i) for i in range(256)]
    return out


def single(c):
    """Grid/password cell: the English single for c ($0400 + ASCII), blank 0000 for a space."""
    if c != " " and c not in font.SINGLES:
        raise SystemExit(f"{c!r} has no English glyph")
    return 0 if c == " " else 0x400 + ord(c)


def name_entry(rom, orig):
    s = Script(orig)
    for tab, n, at, rows, lead in GRIDS:
        for o in at:
            if orig[o] != n or orig[o - 1] not in (0xA9, 0xC9, 0xE9):
                raise SystemExit(f"grid {tab:06X}: no row count {n:#x} at {o:06X}")
            put(rom, o, bytes([len(rows)]), f"grid_{tab:X}_rows", orig)
        for k, row in enumerate(rows):
            assert len(row) == 11 and row[5] == " ", row
            put(rom, off(0x840000 | s.w(tab + 2 * k)), words_bytes(map(single, lead + row)), f"grid_{tab:X}_{k}", orig)
    o, word = PASSWORD
    put(rom, o, words_bytes(map(single, word)), "password", orig)


def build(orig):
    WRITES.clear()
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
                put(rom, f["off"], fixed.pad(f, (codec.msg if n in SINGLE_FIELDS else codec.field)(e["en"])), f["id"], orig)
    staff = next(b for b in blocks if b.name == "staff")
    for i, e in enumerate(ents["staff"]):
        if e["en"]:
            staff.strings[i] = codec.field(e["en"]) + [e["hold"]]
    at, data = [], b""
    for ws in staff.strings:
        at.append((STAFF_TEXT + len(data)) & 0xFFFF)
        data += words_bytes(ws)
    if (STAFF_TEXT & 0xFFFF) + len(data) > 0x10000:
        raise SystemExit(f"staff: {len(data)} bytes overflow bank $B1 from {STAFF_TEXT:06X}")
    put(rom, off(staff.addr), words_bytes(at[i] for i in staff.slots), "staff_ptrs", orig)
    put(rom, off(STAFF_TEXT), data, "staff", orig)
    name_entry(rom, orig)

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
            put(rom, off(cur), data, f"{b.name}:{i}", orig)
            new[b.addr, i] = cur
            cur += len(data)
    for blk in range(IDS >> 8):
        o = off(BLOCKS) + 3 * blk
        p = orig[o] | orig[o + 1] << 8 | orig[o + 2] << 16
        b = next(x for x in blocks if x.addr == p)
        for k, i in enumerate(b.slots):
            if i != NEXT and (p, i) in new:
                tab[blk << 8 | k] = new[p, i]
    put(rom, off(MSGTAB), b"".join(a.to_bytes(3, "little") for a in tab), "msgtab", orig)

    cells, widths = font.build(codec.pairs)
    put(rom, off(FONT2), cells, "font2", orig)
    patched = asm.patch(bytes(rom), {"FONT2": FONT2, "MSGTAB": MSGTAB}, widths)
    log_diff(rom, patched, "asm", orig)
    done = snes_checksum(bytearray(patched))[0]
    log_diff(patched, done, "checksum", orig)
    return done


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
    a.out.with_suffix(".writes.txt").write_text("\n".join(WRITES) + "\n", encoding="utf-8")
    print(f"{a.out.resolve().relative_to(ROOT).as_posix()}: sha1 {hashlib.sha1(rom).hexdigest()}, {len(rom)} bytes")


if __name__ == "__main__":
    main()
