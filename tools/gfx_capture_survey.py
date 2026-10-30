"""Pack newly observed graphics sources into review sheets with an exact source-offset index.

python tools/gfx_capture_survey.py work/qa/maps_gfx --out work/qa/graphics_maps
Known static-survey sources are excluded. Each capture is verified against the original ROM decoder;
invalid pointers, mismatches and duplicate captures remain explicit index rows. Original bytes are padded
to 64-byte boundaries so all six tile interpretations preserve source boundaries.
"""
import argparse
from pathlib import Path

from gfx_survey import ROM, interleave, off, sources, tiles
from lz import decompress


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("captures", type=Path, nargs="+")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--exclude-index", type=Path, action="append", default=[],
                    help="exclude verified sources already packed in an earlier immutable survey")
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    rom = ROM.read_bytes()
    known = {address for _, address in sources(rom)}
    for index in a.exclude_index:
        for line in index.read_text(encoding="utf-8").splitlines()[1:]:
            row = line.split("\t")
            if len(row) >= 4 and row[3] in ("verified", "runtime-source-bank-wrap"):
                known.add(int(row[0], 16))
    seen, rows, packed, failures = {}, ["address\tbytes\tstream_offset\tstatus\tcapture"], bytearray(), 0
    for folder in a.captures:
        for path in sorted(folder.glob("lz_??????.bin")):
            address = int(path.stem[3:], 16)
            data = path.read_bytes()
            prefix = f"{address:06X}\t{len(data)}\t"
            if address in known:
                rows.append(prefix + f"-\tstatic-survey\t{path.as_posix()}")
                continue
            if address in seen:
                status = "duplicate" if seen[address] == data else "variant-not-packed"
                failures += status != "duplicate"
                rows.append(prefix + f"-\t{status}\t{path.as_posix()}")
                continue
            if address & 0xFFFF < 0x8000 or off(address) >= len(rom):
                rows.append(prefix + f"-\tnot-ROM-pointer\t{path.as_posix()}")
                continue
            try:
                seed = path.with_stem(path.stem + "_before").read_bytes()
                decoded, used = decompress(rom, off(address), initial=seed)
                status = "verified"
                if decoded != data:
                    if used > 0x10000 - (address & 0xFFFF):
                        # The hardware's 16-bit source index wraps into low CPU
                        # memory; a contiguous ROM decoder cannot reproduce it.
                        # Keep the actual emulator bytes visible to the reviewer.
                        status = "runtime-source-bank-wrap"
                    else:
                        raise ValueError("emulator mismatch")
            except (OSError, ValueError, IndexError) as exc:
                rows.append(prefix + f"-\tdecode-failed:{exc}\t{path.as_posix()}")
                failures += 1
                continue
            seen[address] = data
            rows.append(prefix + f"{len(packed):06X}\t{status}\t{path.as_posix()}")
            packed.extend(data)
            packed.extend(bytes(-len(packed) % 64))
    (a.out / "index.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    (a.out / "packed.bin").write_bytes(packed)
    count = 0
    for label, data, formats in (("raw", packed, ("snes2", "snes4", "gba4", "gba8")),
                                 ("planes", interleave(packed), ("snes2", "snes4"))):
        for fmt in formats:
            page = 512 * tiles.SIZE[fmt]
            for start in range(0, len(data), page):
                target = a.out / f"sheet_{label}_{fmt}_{start:06X}.png"
                tiles.render(data[start:start + page], fmt, tiles.palette(None, 0, tiles.BPP[fmt]),
                             32, 2, str(target))
                count += 1
    runtime = sum("\truntime-source-bank-wrap\t" in row for row in rows)
    print(f"{len(seen)} new sources ({runtime} runtime-only bank wraps), {len(packed)} packed bytes, "
          f"{count} sheets, {failures} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
