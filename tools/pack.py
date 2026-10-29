"""pack.py: unpack the script's pointer blocks into strings and pack them back (docs/re/text.md).

A block is a table of 16-bit pointers followed, in the same bank, by the strings they point at. unpack() keeps which
slots share a string, slots that point at the next block's table (unused message ids), and words between strings that
no slot reaches (orphans), so pack(unpack(...)) gives the original bytes back: the identity build (phase 3).

    python -X utf8 tools/pack.py      # unpack + pack every block, list them, fail on any byte that differs
"""
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from textdump import DICT, DICT_N, ROM, Script, off  # noqa: E402

STAFF = 0xB1D3E2  # staff roll: strings end FFFF + one more word (how long the page stays up, e.g. $B4 frames)
NEXT = -1         # slot value: points at the next block's table (an unused message id)


@dataclass
class Block:
    name: str
    addr: int       # CPU address of the pointer table; the strings follow it in the same bank
    slots: list     # per slot: index into strings, or NEXT
    strings: list   # word lists in ROM order
    orphans: set    # indices of strings no slot points at; packed in place so every offset stays put

    def size(self):
        return 2 * (len(self.slots) + sum(map(len, self.strings)))


def staff_words(s, o):
    ws = []
    while not ws or ws[-1] != 0xFFFF:
        ws.append(s.w(o + 2 * len(ws)))
    return ws + [s.w(o + 2 * len(ws))], None


def sources(s):
    """(name, table address, slot count or None = from the first pointer, string parser) for every block."""
    yield "dict", DICT, DICT_N, s.words
    for b, p in s.blocks():
        yield f"msg{b:02X}", p, None, s.words
    yield "staff", STAFF, None, lambda o: staff_words(s, o)


def unpack(s, name, addr, n, parse, tables):
    bank, o = addr & 0xFF0000, off(addr)
    n = n or (s.w(o) - (addr & 0xFFFF)) // 2
    ptrs = [s.w(o + 2 * i) for i in range(n)]
    pos, strings, index, orphans = (addr & 0xFFFF) + 2 * n, [], {}, set()
    for t in sorted(set(ptrs)):
        if bank | t in tables and bank | t != addr:
            continue  # unused slot: points at the next block's table
        if t < pos or (t - pos) & 1:
            raise ValueError(f"{name}: string at {bank | t:06X} overlaps or is misaligned (next free {bank | pos:06X})")
        if t > pos:
            orphans.add(len(strings))
            strings.append([s.w(off(bank | a)) for a in range(pos, t, 2)])
        ws, _ = parse(off(bank | t))
        index[t] = len(strings)
        strings.append(ws)
        pos = t + 2 * len(ws)
    return Block(name, addr, [index.get(t, NEXT) for t in ptrs], strings, orphans)


def unpack_all(rom):
    s = Script(rom)
    src = list(sources(s))
    tables = {a for _, a, _, _ in src}
    return [unpack(s, *x, tables) for x in src]


def pack(b):
    """Pointer table + strings, addressed from b.addr. NEXT slots point just past the block."""
    base = b.addr & 0xFFFF
    end = base + b.size()
    if end > 0x10000:
        raise ValueError(f"{b.name}: {b.size()} bytes from {b.addr:06X} cross the bank end")
    at, cur = [], base + 2 * len(b.slots)
    for ws in b.strings:
        at.append(cur)
        cur += 2 * len(ws)
    words = [end if i == NEXT else at[i] for i in b.slots] + [x for ws in b.strings for x in ws]
    return b"".join(x.to_bytes(2, "little") for x in words)


def write(rom, b):
    o = off(b.addr)
    rom[o:o + b.size()] = pack(b)


def main():
    orig = ROM.read_bytes()
    rom = bytearray(orig)
    for b in unpack_all(orig):
        write(rom, b)
        print(f"{b.name:6} {off(b.addr):06X}-{off(b.addr) + b.size():06X} {len(b.slots):3} slots "
              f"{len(b.strings):3} strings {len(b.orphans)} orphans")
    bad = [i for i, (x, y) in enumerate(zip(orig, rom)) if x != y]
    sys.exit(f"{len(bad)} bytes differ, first at {bad[0]:06X}" if bad else print("identical"))


if __name__ == "__main__":
    main()
