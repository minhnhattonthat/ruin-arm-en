"""en.py: the English codec (codes from tools/font.py). Messages use singles (the dialogue VWF spaces them by width);
fixed fields and the staff roll use slices (their drawers give every code a 16 px cell, so each cell holds a 16 px
slice of the text set proportionally).

    from en import Codec
    c = Codec(texts)                 # texts: every fixed-field/staff string of the build (assigns the slice codes)
    c.msg("Hello{end}")  -> words    c.field("Potion") -> words
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from font import SINGLES, slice_codes, slices  # noqa: E402
from tbl import Table  # noqa: E402
from textdump import Script  # noqa: E402

TOKEN = re.compile(r"(\{[^{}]*\}|\[[0-9A-F]{4}\]|\n)")
TABLE = Table([f"{c & 0xFF:02X}{c >> 8:02X}={'\\s' if ch == ' ' else ch}" for ch, c in SINGLES.items()])


BREAK = re.compile(r"(\n|\{wait(?::[0-9A-F]+)?\})")
CHOICE = re.compile(r"(^|\n)  ([1-3])")


def carry_col(text):
    """A line break resets the colour (the JP re-opens {col:01} on each row): re-open it after a break when the
    next row closes the span with {col}, so "{col:01}Stelm\\nDuchy{col}" stays yellow. A speaker row
    ("{col:01}Gilm\\n...") is never closed, so the body stays white."""
    out, on = [], False
    segs = BREAK.split(text)
    for i, s in enumerate(segs):
        if i % 2 == 0:
            close, reopen = s.find("{col}"), s.find("{col:01}")
            if on and close >= 0 and (reopen < 0 or close < reopen):
                s = "{col:01}" + s
            out.append(s)
            last = max(s.rfind("{col:01}"), s.rfind("{col}"))
            on = last >= 0 and s.startswith("{col:01}", last)
        else:
            out.append(s)
    return "".join(out)


def parts(text):
    """Tokens kept whole, plain runs between them."""
    return [p for p in TOKEN.split(text) if p]


class Codec:
    def __init__(self, texts=()):
        self.codes = slice_codes(c for t in texts for p in parts(t) if not TOKEN.fullmatch(p) for c in slices(p) if c)
        self.s = Script(rom=b"", tbl=TABLE)

    def msg(self, text):
        if "{choice" in text:  # options "  1Yes": the JP's 16 px blank, blank, digit cells, so the cursor (cell 1) and
            text = CHOICE.sub(lambda m: f"{m[1]}[0000][0000][{0xA1 + int(m[2]):04X}]", text)  # highlight (cell 3+) fit
        return self.s.encode(carry_col(text))

    def field(self, text):
        """Slice words; a blank cell is 0000 (the game's blank cell)."""
        out = []
        for p in parts(text):
            out += self.s.encode(p) if TOKEN.fullmatch(p) else [self.codes[c] if c else 0 for c in slices(p)]
        return out


if __name__ == "__main__":
    assert carry_col("To {col:01}Stelm\nDuchy{col}.") == "To {col:01}Stelm\n{col:01}Duchy{col}."
    assert carry_col("{col:01}Gilm\nHi {col:01}you{col}.\nNo{col}") == "{col:01}Gilm\nHi {col:01}you{col}.\nNo{col}"
    c = Codec(["Items", "Use", "A   B"])
    assert c.msg("Hi{end}") == [0x448, 0x469, 0xFF00]
    assert c.msg("\n  1Hi\n  2No{choice:00:0001:0002}")[1:4] == [0, 0, 0xA2]
    assert len(c.field("Items")) == 2 and c.field("{pos:0012}Use") == [0x8012] + c.field("Use")
    a, blank, b = c.field("A   B")
    assert blank == 0 and a != b
    print("selftest ok")
