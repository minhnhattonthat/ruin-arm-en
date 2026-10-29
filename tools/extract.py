"""extract.py: dump every text source to script/<source>.json, and apply their English to a ROM for the build.

    python -X utf8 tools/extract.py        # writes only missing files: never clobbers English

Files (JSON list, one entry per string, ROM order):
- msgXX.json  message block $XX (tools/pack.py): id = message id of the first slot ("1032"), slots = every message id
  that shares the string, jp/en in tools/textdump.py's text format ({end}, {wait}, newline = F600, {d:XX|word}...).
  orphan_<addr> entries are strings no pointer reaches (kept so offsets stay put).
- dict.json   the $838000 dictionary (F8xx words); JP-only compression: English is written out in full (D9).
- staff.json  positioned staff roll; hold = the word after FFFF (frames the page stays up, guess).
- <table>.json  fixed-size fields (tools/fixed.py): max = field length in glyphs, English is space-padded in place.
An empty en keeps the original bytes.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fixed  # noqa: E402
from pack import NEXT, unpack_all  # noqa: E402
from textdump import Script  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "script"


def block_entries(s, b):
    if b.name == "dict":
        return [{"id": f"D{i:02X}", "jp": s.text(ws)} for i, ws in enumerate(b.strings)]
    if b.name == "staff":
        return [{"id": f"S{i:02X}", "jp": s.text(ws[:-1]), "en": "", "hold": ws[-1]} for i, ws in enumerate(b.strings)]
    blk = int(b.name[3:], 16)
    slots = {}
    for k, i in enumerate(b.slots):
        if i != NEXT:
            slots.setdefault(i, []).append(f"{blk << 8 | k:04X}")
    out = []
    at = (b.addr & 0xFFFF) + 2 * len(b.slots)
    for i, ws in enumerate(b.strings):
        e = {"id": slots[i][0] if i in slots else f"orphan_{b.addr & 0xFF0000 | at:06X}"}
        if len(slots.get(i, [])) > 1:
            e["slots"] = slots[i]
        e.update(jp=s.text(ws), en="")
        out.append(e)
        at += 2 * len(ws)
    return out


def field_entries(s, fs):
    out = []
    for f in fs:
        e = {"id": f["id"], "max": f["n"]}
        if "pos" in f:
            e["pos"] = f"{f['pos']:04X}"
        e.update(jp=s.text(fixed.words(s, f)).rstrip(" "), en="")
        out.append(e)
    return out


def sources(s, blocks):
    """{file name: entries freshly decoded from the ROM in s}."""
    out = {b.name: block_entries(s, b) for b in blocks}
    out.update({name: field_entries(s, fs) for name, fs in fixed.fields(s).items()})
    return out


def load(name, fresh):
    """Entries of script/<name>.json, checked against the fresh decode: same ids, same jp (else re-extract)."""
    p = SCRIPT / f"{name}.json"
    if not p.exists():
        return fresh
    got = json.loads(p.read_text(encoding="utf-8"))
    for a, b in zip(got, fresh):
        if a["id"] != b["id"] or a["jp"] != b["jp"]:
            raise ValueError(f"{p.name}: entry {a['id']} does not match the ROM ({b['id']}); re-extract")
    if len(got) != len(fresh):
        raise ValueError(f"{p.name}: {len(got)} entries, the ROM has {len(fresh)}")
    return got


def apply(s, blocks, rom):
    """Put every non-empty en into blocks (strings, packed later by the build) and rom (fixed fields, in place)."""
    for b in blocks:
        for ws_i, e in enumerate(load(b.name, block_entries(s, b))):
            if e.get("en"):
                b.strings[ws_i] = s.encode(e["en"]) + ([e["hold"]] if b.name == "staff" else [])
    for name, fs in fixed.fields(s).items():
        for f, e in zip(fs, load(name, field_entries(s, fs))):
            if e["en"]:
                fixed.put(s, rom, f, e["en"])


def main():
    s = Script()
    SCRIPT.mkdir(exist_ok=True)
    for name, entries in sources(s, unpack_all(s.d)).items():
        p = SCRIPT / f"{name}.json"
        if p.exists():
            print(f"skip  {p.relative_to(ROOT).as_posix()} (exists)")
            continue
        p.write_text(json.dumps(entries, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"wrote {p.relative_to(ROOT).as_posix()}: {len(entries)} entries")


if __name__ == "__main__":
    main()
