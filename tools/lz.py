"""The game's LZSS codec (decompressor at $80900E, docs/re/compression.md).

Block: u16 output size, then groups of one flag byte (read LSB first) + 8 items. Flag 1 = literal byte. Flag 0 = u16
word w: copy (w & 0xF) + 3 bytes from output position pos - (w >> 4). Negative positions use the hardware's
eight-bit zero-fill counter; distance zero requires the prior destination RAM (initial=).

    python tools/lz.py selftest
    python tools/lz.py dump OFFSET OUT.bin      # decompress the block at a file offset
"""
import sys
from pathlib import Path

ROM = Path(__file__).resolve().parent.parent / "rom" / "Ruin Arm (Japan).sfc"


def decompress(data, pos=0, initial=None):
    """-> (bytes, consumed); initial supplies prior destination RAM for distance-zero copies."""
    start = pos
    size = data[pos] | data[pos + 1] << 8
    pos += 2
    out = bytearray()
    flags = bits = 0
    while len(out) < size:
        if not bits:
            flags, bits = data[pos], 8
            pos += 1
        bits -= 1
        lit, flags = flags & 1, flags >> 1
        if lit:
            out.append(data[pos])
            pos += 1
            continue
        w = data[pos] | data[pos + 1] << 8
        pos += 2
        src = ((len(out) - (w >> 4) + 0x8000) & 0xFFFF) - 0x8000
        if src < 0:
            # The 65816 routine keeps the zero-fill counter in eight bits, then
            # tests DEC with BPL. Large negative distances therefore wrap.
            counter = (~src) & 0xFF
            src = -(counter + 1 if counter <= 0x80 else 1)
        for _ in range(min((w & 0xF) + 3, size - len(out))):
            if src >= len(out):
                if initial is None or src >= len(initial):
                    raise ValueError("distance-zero back-reference needs initial destination RAM")
                out.append(initial[src])
            else:
                out.append(out[src] if src >= 0 else 0)
            src += 1
    return bytes(out[:size]) if len(out) > size else bytes(out), pos - start


def compress(data):
    """Greedy LZSS that decompress() reverses exactly (not byte-identical to the original packer)."""
    out = bytearray([len(data) & 0xFF, len(data) >> 8])
    i, n = 0, len(data)
    while i < n:
        flag_at = len(out)
        out.append(0)
        for bit in range(8):
            if i >= n:
                break
            best_len = best_d = 0
            for dist in range(1, min(i, 0xFFF) + 1):
                ln = 0
                while ln < 18 and i + ln < n and data[i + ln - dist] == data[i + ln]:
                    ln += 1
                if ln > best_len:
                    best_len, best_d = ln, dist
                    if ln == 18:
                        break
            if best_len >= 3:
                w = best_d << 4 | (best_len - 3)
                out += bytes([w & 0xFF, w >> 8])
                i += best_len
            else:
                out[flag_at] |= 1 << bit
                out.append(data[i])
                i += 1
    return bytes(out)


def selftest():
    rom = ROM.read_bytes()
    raw, used = decompress(rom, 0x0FEBC0)  # $9FEBC0: loaded when the first dialogue box opens (docs/re/text.md)
    assert len(raw) == 0x150, len(raw)
    assert decompress(compress(raw))[0] == raw
    for sample in (b"", b"a", b"abcabcabcabcabcabc" * 9, bytes(range(256)) * 3):
        assert decompress(compress(sample))[0] == sample
    print(f"lz selftest ok ({used} bytes -> {len(raw)})")


if __name__ == "__main__":
    if sys.argv[1:2] == ["selftest"]:
        selftest()
    elif sys.argv[1:2] == ["dump"]:
        raw, used = decompress(ROM.read_bytes(), int(sys.argv[2], 0))
        Path(sys.argv[3]).write_bytes(raw)
        print(f"{used} bytes -> {len(raw)}")
