"""Render a reproducible graphics survey; never changes the ROM.

python -X utf8 tools/gfx_survey.py [--out work/qa/graphics] [--raw]

Known pointer tables are bounded by the following code/data, not the first zero slot.
The index lists every source, duplicate, empty slot and decode failure. --raw additionally
renders every ROM bank, including code, so unclassified raw graphics are not silently skipped.
This is evidence for reviewers, not proof that every compression source is known.
"""
import argparse
import hashlib
import sys
from pathlib import Path

from lz import decompress
from skill import SCRIPTS

sys.path.insert(0, str(SCRIPTS))
import tiles  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Ruin Arm (Japan).sfc"


def off(address):
    return ((address & 0x7F0000) >> 1) | (address & 0x7FFF)


def interleave(data):
    """$808F95 / $809097: interleave the two 8-byte planes of each 16-byte group."""
    if len(data) % 16:
        raise ValueError("bitplane conversion needs complete 16-byte groups")
    return bytes(data[base + (i // 2) + (i % 2) * 8]
                 for base in range(0, len(data), 16) for i in range(16))


def sources(rom):
    for address, stride, count in ((0x80B00F, 6, 40), (0x94FF04, 3, 52),
                                   (0x94DC1A, 3, 448), (0x90E383, 3, 6)):
        for i in range(count):
            pos = off(address) + stride * i
            yield f"table_{address:06X}_{i:03X}", int.from_bytes(rom[pos:pos + 3], "little")
    for address in (0x9FEBC0, 0xC08600, 0xC0A926, 0xB8903C, 0xCCA1D5, 0xCC86D6,
                    0xAF851C, 0xAFCBB7, 0xAFC8E5, 0xAFD217, 0xAFCE87, 0xAFB1CD,
                    0xCE8000, 0xB8C0BE, 0xAFA8E2, 0xBF8D00, 0xBF8F81, 0xBF922E, 0xBF8E66):
        yield f"direct_{address:06X}", address


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=ROOT / "work" / "qa" / "graphics")
    ap.add_argument("--raw", action="store_true")
    ap.add_argument("--capture-dir", type=Path, action="append", default=[],
                    help="gfx_capture.lua dumps: add observed sources, seed RAM and verify bytes; repeatable")
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    rom = ROM.read_bytes()
    rows = ["source\taddress\tstatus\tbytes\tevidence"]
    seen, rendered = {}, 0

    def render(name, data, formats):
        nonlocal rendered
        for fmt in formats:
            if len(data) < tiles.SIZE[fmt]:
                rows.append(f"{name}\t-\tskip-{fmt}-too-short\t{len(data)}\t-")
                continue
            # Page large blocks at 512 tiles so reviewers can see the pixels at native size.
            size = 512 * tiles.SIZE[fmt]
            usable = len(data) // tiles.SIZE[fmt] * tiles.SIZE[fmt]
            if usable < len(data):
                rows.append(f"{name}\t{usable:06X}\tskip-{fmt}-trailing-bytes\t{len(data) - usable}\t-")
            for start in range(0, usable, size):
                block = data[start:min(start + size, usable)]
                path = a.out / f"{name}_{fmt}_{start:06X}.png"
                tiles.render(block, fmt, tiles.palette(None, 0, tiles.BPP[fmt]), 32, 2, str(path))
                rendered += 1

    captured = {}
    for directory in a.capture_dir:
        for path in sorted(directory.glob("lz_??????.bin")):
            captured.setdefault(int(path.stem[3:], 16), path)
    candidates = list(sources(rom)) + [("captured_" + f"{addr:06X}", addr) for addr in captured]
    for name, address in candidates:
        if address == 0:
            rows.append(f"{name}\t000000\tempty-slot\t0\t-")
            continue
        if address in seen:
            rows.append(f"{name}\t{address:06X}\tduplicate\t0\t{seen[address]}")
            continue
        seen[address] = name
        if address & 0xFFFF < 0x8000 or off(address) >= len(rom):
            rows.append(f"{name}\t{address:06X}\tskip-not-ROM-pointer\t0\t-")
            continue
        try:
            capture = captured.get(address)
            seed = capture.with_stem(capture.stem + "_before") if capture else None
            data, used = decompress(rom, off(address), initial=seed.read_bytes() if seed and seed.exists() else None)
            if capture and capture.exists() and capture.read_bytes() != data:
                raise ValueError("decoded bytes differ from emulator capture")
        except (IndexError, ValueError) as exc:
            rows.append(f"{name}\t{address:06X}\tdecode-failed\t0\t{exc}")
            continue
        prefix = f"lz_{address:06X}"
        (a.out / f"{prefix}.bin").write_bytes(data)
        proof = f"; matched {capture.as_posix()}" if capture else ""
        rows.append(f"{name}\t{address:06X}\tdecoded\t{len(data)}\t{used} source bytes; {prefix}{proof}")
        render(prefix, data, ("snes2", "snes4", "gba4", "gba8"))
        if data and len(data) % 16 == 0:
            render(prefix + "_planes", interleave(data), ("snes2", "snes4"))
        else:
            rows.append(f"{name}\t{address:06X}\tskip-interleave-size\t{len(data)}\t-")
    if a.raw:
        for start in range(0, len(rom), 0x8000):
            name = f"raw_{start:06X}"
            block = rom[start:start + 0x8000]
            rows.append(f"{name}\t{start:06X}\traw-ROM\t{len(block)}\t-")
            render(name, block, ("snes2", "snes4", "gba4", "gba8"))
    else:
        rows.append(f"raw-ROM\t000000\tnot-requested\t{len(rom)}\tpass --raw")
    (a.out / "index.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    (a.out / "rom.sha1").write_text(hashlib.sha1(rom).hexdigest() + "\n", encoding="ascii")
    failures = sum("\tdecode-failed\t" in row for row in rows)
    print(f"{rendered} sheets; {len(seen)} distinct candidate sources; {failures} decode failures; "
          f"index: {a.out / 'index.tsv'}")
    print("Coverage limit: source tables above only; unenumerated compressed loaders remain open.")


if __name__ == "__main__":
    main()
