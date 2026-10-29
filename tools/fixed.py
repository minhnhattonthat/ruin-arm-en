"""fixed.py: text in fixed-size fields outside the message blocks, written back in place (docs/re/text.md §Fixed text).

A field is (file offset, length in glyph words). English must fit its field; shorter text is padded with spaces
(glyph 0000), so nothing around a field moves. Sources:
- menu: bank $84 lists drawn by $849B38 (record = pos16, count8, count glyph words; FFFF ends a list), found by a
  structural sweep of MENU. Every list there sits beside a 16-bit pointer table that reaches it.
- TABLES: arrays of equal fields; PTRS: pointer tables to FFFF-terminated strings.

    python -X utf8 tools/fixed.py      # list every table and its field count
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from textdump import Script, off  # noqa: E402

MENU = (0x020A00, 0x026400)
# name: (file offset of field 0, stride in bytes, count, words per field). Blank fields (all spaces) are skipped.
TABLES = {
    "item": (0x05396D, 0x34, 0xDF, 8),         # $8AB96C records + 1 ($84B2A1 reads names of ids < $DF)
    "place": (0x02F9CD, 0x10, 72, 8),          # $85F9CD: map/area names
    "name_hero": (0x02C3DC, 0x10, 16, 8),      # $85C3BC pointer list: default names offered for the hero
    "name_sister": (0x02C4FC, 0x10, 16, 8),    # $85C4DC pointer list: default names for the sister
    "ingot": (0x02E492, 0x10, 16, 8),          # $85E472 pointer list
    "equip": (0x02E7D4, 4, 10, 2),             # $85E7BE pointer list: hand/arrow labels (両手, 木矢..)
    "tactic": (0x0255A5, 6, 5, 3),             # $84D59B pointer list: AI aggressiveness (しない..好戦的)
    "pad": (0x025648, 0x10, 3, 8),             # $84D642 pointer list: controller labels
    "use": (0x02552C, 8, 2, 4),                # $84D528 pointer list: 使う / 使わない
    "act": (0x025540, 8, 2, 4),                # $84D53C pointer list: 行う / 行わない
    "element": (0x00FD33, 10, 4, 5),           # $81FD2B pointer list: alchemy elements
    "heat": (0x00FD5F, 8, 2, 4),               # $81FD5B pointer list: 加熱する / 冷却する
}
PTRS = {"status": (0x02DEE6, 11)}               # $85DEE6: 最強, Mpower.., ailments; the 12th entry is tile data


def glyph_ok(s, w):
    return w < 0x355 and bytes([w & 0xFF, w >> 8]) in s.t.dec


def parse_list(s, o):
    """[(record offset, pos, count)] of a well-formed list at o, else None."""
    recs, p = [], o
    while s.w(p) != 0xFFFF and len(recs) <= 40:
        pos, n = s.w(p), s.d[p + 2]
        ws = [s.w(p + 3 + 2 * k) for k in range(n)]
        if pos >= 0x800 or pos & 1 or not 1 <= n <= 32 or not all(glyph_ok(s, w) for w in ws) or not any(ws):
            return None
        recs.append((p, pos, n))
        p += 3 + 2 * n
    return recs if recs and len(recs) <= 40 else None


def menu_lists(s):
    """[(list offset, [(record offset, pos, count)])] for every well-formed list in MENU.

    A parse can start a few bytes early, on the tail of the data before the list, and still meet the real records
    after its first one (84:D676 vs the real 84:D678: the pad table's last 0000 read as pos). When a later start
    inside the first record reaches the same second record, the later start is the list."""
    out, o = [], MENU[0]
    while o < MENU[1]:
        recs = parse_list(s, o)
        if not recs:
            o += 1
            continue
        end = recs[0][0] + 3 + 2 * recs[0][2]
        for o2 in range(o + 1, end - 3):
            r2 = parse_list(s, o2)
            if r2 and r2[0][0] + 3 + 2 * r2[0][2] == end:
                o, recs = o2, r2
                break
        out.append((o, recs))
        o = recs[-1][0] + 3 + 2 * recs[-1][2] + 2
    return out


def cpu(o):
    return 0x800000 | (o << 1 & 0x7F0000) | 0x8000 | (o & 0x7FFF)


def fields(s):
    """{table: [field dict(id, off, n[, pos])]} in ROM order."""
    t = {"menu": [{"id": f"{cpu(r):06X}", "off": r + 3, "n": n, "pos": pos}
                  for _, recs in menu_lists(s) for r, pos, n in recs]}
    for name, (o, stride, count, n) in TABLES.items():
        t[name] = [{"id": f"{name}_{i:02X}", "off": o + stride * i, "n": n} for i in range(count)
                   if any(s.w(o + stride * i + 2 * k) for k in range(n))]
    for name, (o, count) in PTRS.items():
        bank = cpu(o) & 0xFF0000
        t[name] = []
        for i in range(count):
            a = off(bank | s.w(o + 2 * i))
            n = next(k for k in range(64) if s.w(a + 2 * k) == 0xFFFF)
            t[name].append({"id": f"{name}_{i:02X}", "off": a, "n": n})
    return t


def words(s, f):
    return [s.w(f["off"] + 2 * k) for k in range(f["n"])]


def put(rom, f, ws):
    """Encoded words into field f of rom (bytearray), space-padded. Raises ValueError if they don't fit."""
    if any(w >= 0x8000 for w in ws) or len(ws) > f["n"]:
        raise ValueError(f"{f['id']}: {len(ws)} words (glyphs only), the field holds {f['n']}")
    ws += [0] * (f["n"] - len(ws))
    rom[f["off"]:f["off"] + 2 * f["n"]] = b"".join(w.to_bytes(2, "little") for w in ws)


def main():
    s = Script()
    for name, fs in fields(s).items():
        print(f"{name:12} {len(fs):4} fields  e.g. {s.text(words(s, fs[0])).rstrip()!r}")


if __name__ == "__main__":
    main()
