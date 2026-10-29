"""Decode the dialogue script (docs/re/text.md) for reading: one line per message id.

    python -X utf8 tools/textdump.py [--out work/re/script_jp.txt] [--expand]

--expand inlines dictionary words ({d:28|お父さん} -> お父さん). Script.text/encode are the codec of script/*.json.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tbl import Table  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ROM = ROOT / "rom" / "Ruin Arm (Japan).sfc"
BLOCKS = 0x838642   # 24-bit pointer per block, 0x14 blocks; block = msg id >> 8
DICT = 0x838000     # 16-bit pointers (bank $83) to $FFFF-terminated words; F8xx inserts entry xx
DICT_N = 0x90
# control word = cmd<<8 | arg. extra = argument words that follow in the stream.
CTRL = {0xFF: "end", 0xFE: "fe", 0xFD: "fd", 0xFC: "col", 0xFB: "spd", 0xFA: "fa", 0xF9: "choice", 0xF8: "d",
        0xF7: "wait", 0xF6: "nl", 0xF5: "f5", 0xF4: "f4", 0xF3: "f3", 0xF2: "name", 0xF1: "sfx", 0xF0: "goto",
        0xEF: "item_v", 0xEE: "num", 0xED: "item", 0xEC: "set"}
CTRL_ENC = {v: k for k, v in CTRL.items()}
TOKEN = re.compile(r"\{(\w+)(?::([0-9A-F]{2,4}))?((?::[0-9A-F]{4})*)(?:\|[^{}]*)?\}|\[([0-9A-F]{4})\]|\n")


def off(a):
    return ((a & 0x7F0000) >> 1) | (a & 0x7FFF)


class Script:
    def __init__(self, rom=None, tbl=ROOT / "tbl" / "jp.tbl"):
        self.d = rom if rom is not None else ROM.read_bytes()
        self.t = tbl if isinstance(tbl, Table) else Table.load(tbl)

    def w(self, o):
        return self.d[o] | self.d[o + 1] << 8

    def extra(self, x):
        hi = x >> 8
        return 1 if hi in (0xF0, 0xEC) else 2 + (x & 1) if hi == 0xF9 else 0

    def words(self, o):
        """Words of one message from file offset o, through its terminator (end, goto, choice). -> (list, end)"""
        out = []
        while True:
            x = self.w(o)
            o += 2
            out.append(x)
            n = self.extra(x) if x & 0x8000 else 0
            out += [self.w(o + 2 * i) for i in range(n)]
            o += 2 * n
            if x >> 8 in (0xFF, 0xF0, 0xF9):
                return out, o

    def text(self, ws, expand=False):
        """Words -> text. Glyphs via the table ([XXXX] if unknown), F600 = newline, {d:XX|word} = dictionary entry
        (--expand: the word alone), {pos:XXXX} = staff-roll tilemap position ($8000|pos), other control words
        {name} / {name:LO} / {name:LO:ARG..}. encode() inverts it exactly."""
        s, i = [], 0
        while i < len(ws):
            x = ws[i]
            i += 1
            if x < 0x8000:
                s.append(self.t.dec.get(bytes([x & 0xFF, x >> 8]), f"[{x:04X}]"))
                continue
            hi, lo = x >> 8, x & 0xFF
            if x == 0xF600:
                s.append("\n")
            elif hi == 0xF8:
                word = self.text(self.dict_entry(lo))
                s.append(word if expand else f"{{d:{lo:02X}|{word}}}")
            elif hi not in CTRL:
                s.append(f"{{pos:{x & 0x7FFF:04X}}}")
            else:
                n = self.extra(x)
                args = "".join(f":{a:04X}" for a in ws[i:i + n])
                i += n
                s.append(f"{{{CTRL[hi]}{f':{lo:02X}' if lo or args else ''}{args}}}")
        return "".join(s)

    def encode(self, text):
        """Text in text()'s format -> words. Raises ValueError on an unknown character or control."""
        out, i = [], 0
        while i < len(text):
            m = TOKEN.match(text, i)
            if m and m[0] == "\n":
                out.append(0xF600)
            elif m and m[4]:
                out.append(int(m[4], 16))
            elif m:
                name, lo, args = m[1], int(m[2] or "0", 16), [int(a, 16) for a in m[3].split(":")[1:]]
                if name == "pos":
                    out.append(0x8000 | lo)
                    i = m.end()
                    continue
                if name not in CTRL_ENC or lo > 0xFF:
                    raise ValueError(f"unknown control {m[0]} at {i} in {text!r}")
                x = CTRL_ENC[name] << 8 | lo
                if len(args) != self.extra(x):
                    raise ValueError(f"{m[0]} needs {self.extra(x)} argument words at {i} in {text!r}")
                out += [x] + args
            else:
                for k in range(min(self.t.vallen, len(text) - i), 0, -1):
                    key = self.t.enc.get(text[i:i + k])
                    if key:
                        out.append(key[0] | key[1] << 8)
                        i += k
                        break
                else:
                    raise ValueError(f"unencodable {text[i]!r} at {i} in {text!r}")
                continue
            i = m.end()
        return out

    def dict_entry(self, k):
        o, ws = off(0x830000 | self.w(off(DICT) + 2 * k)), []
        while self.w(o) < 0x8000:
            ws.append(self.w(o))
            o += 2
        return ws

    def blocks(self):
        """(block, table address) per distinct table; blocks $03-$0F share block $01's table and are not repeated."""
        o, seen = off(BLOCKS), set()
        for b in range(0x14):
            p = self.d[o + 3 * b] | self.d[o + 3 * b + 1] << 8 | self.d[o + 3 * b + 2] << 16
            if p not in seen:
                seen.add(p)
                yield b, p

    def messages(self):
        """(msg id, file offset) for every pointer slot; pointers into the next table (unused slots) are skipped."""
        tables = {off(p) for _, p in self.blocks()}
        for b, p in self.blocks():
            bo = off(p)
            n = (self.w(bo) - (p & 0xFFFF)) // 2
            for i in range(n):
                mo = off((p & 0xFF0000) | self.w(bo + 2 * i))
                if mo not in tables:
                    yield b << 8 | i, mo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "work" / "re" / "script_jp.txt"))
    ap.add_argument("--expand", action="store_true")
    a = ap.parse_args()
    s = Script()
    lines = [f"D{k:02X}\t{s.text(s.dict_entry(k))}" for k in range(DICT_N)]
    for mid, mo in s.messages():
        ws, _ = s.words(mo)
        lines.append(f"{mid:04X}\t{mo:06X}\t" + s.text(ws, a.expand).replace("\n", "\\n"))
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(a.out, len(lines))


if __name__ == "__main__":
    main()
