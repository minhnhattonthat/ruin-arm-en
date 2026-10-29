"""en.py: the English codec (codes from tools/font.py). Messages use singles (the dialogue VWF spaces them by width);
fixed fields and the staff roll use digraphs (their drawers give every code a 16 px cell).

    from en import Codec
    c = Codec(pairs)                 # pairs: {two-char string: code}, from Codec.pairs_in(texts)
    c.msg("Hello{end}")  -> words    c.field("Potion") -> words
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from font import SINGLES, pair_codes  # noqa: E402
from tbl import Table  # noqa: E402
from textdump import Script  # noqa: E402

TOKEN = re.compile(r"(\{[^{}]*\}|\[[0-9A-F]{4}\]|\n)")
TABLE = Table([f"{c & 0xFF:02X}{c >> 8:02X}={'\\s' if ch == ' ' else ch}" for ch, c in SINGLES.items()])


def pieces(text):
    """Digraph split: tokens kept whole, each plain run cut into pairs (a run of odd length ends on a single)."""
    out = []
    for part in TOKEN.split(text):
        if TOKEN.fullmatch(part):
            out.append(part)
        else:
            out += [part[i:i + 2] for i in range(0, len(part), 2)]
    return out


class Codec:
    def __init__(self, pairs=None):
        self.pairs = pairs or {}
        self.s = Script(rom=b"", tbl=TABLE)

    @staticmethod
    def pairs_in(texts):
        return pair_codes(p for t in texts for p in pieces(t) if len(p) == 2 and not TOKEN.fullmatch(p))

    def msg(self, text):
        return self.s.encode(text)

    def field(self, text):
        out = []
        for p in pieces(text):
            out += [self.pairs[p]] if len(p) == 2 and p in self.pairs else self.s.encode(p)
        return out


if __name__ == "__main__":
    c = Codec(Codec.pairs_in(["Items", "Use"]))
    assert c.msg("Hi{end}") == [0x448, 0x469, 0xFF00]
    assert c.field("Items") == [c.pairs["It"], c.pairs["em"], 0x473] and c.field("{pos:0012}Us") == [0x8012, c.pairs["Us"]]
    print("selftest ok")
