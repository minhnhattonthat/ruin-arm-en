"""Translate the city tileset's unused-slot markers from アキ to FREE.

Only the eleven exact marker tiles change. All map art and tile numbers stay
unchanged; the rebuilt LZ stream is relocated through its existing pointer.
"""
from lz import compress, decompress

SOURCE = 0x1AA9A8  # $B5A9A8
POINTER = 0x060300  # $8C8300 = map graphics table $8C816B + $1B * 15
MARKERS = {
    bytes.fromhex("007E12121C103000"): bytes.fromhex("00EC8A8ACC8A8A00"),  # ア -> FR
    bytes.fromhex("00107E107E080800"): bytes.fromhex("00EE8888CC88EE00"),  # キ -> EE
}


def translated(original):
    data, _ = decompress(original, SOURCE)
    changed = bytearray(data)
    count = 0
    for offset in range(0, len(data), 32):
        tile = data[offset:offset + 32]
        for before, after in MARKERS.items():
            if tile == bytes(16) + before * 2:
                changed[offset:offset + 32] = bytes(16) + after * 2
                count += 1
    assert count == 11, f"expected eleven unused-slot glyphs, found {count}"
    return bytes(changed)


def generate(folder, original):
    data = translated(original)
    packed = compress(data)
    assert decompress(packed)[0] == data
    (folder / "unused_tiles.lz").write_bytes(packed)
