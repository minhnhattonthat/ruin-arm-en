# Compression

## LZSS at `$80900E` (verified)

- Inputs: source `$95-$97` (24-bit), destination `$98-$9A` (usually WRAM `$7E:B800` or `$7F:8000`).
- Block: u16 output size; then a flag byte read **LSB first** before every 8 items. Flag 1 = literal byte. Flag 0 =
  u16 word `w`: copy `(w & $F) + 3` bytes from output position `pos - (w >> 4)` (12-bit distance); positions before the
  output start read as 0, subject to the eight-bit counter behavior below.
- `tools/lz.py`: `decompress` + a greedy `compress`; `python tools/lz.py selftest` decompresses the real block
  `$9FEBC0` (138 → 336 bytes, loaded when the first dialogue box opens) and roundtrips it. The packer is not
  byte-identical to the original one; identity builds must copy untouched blocks, never repack them.
- Call sites (`JSL $80900E`): `$80AB40` (table `$80B00F,x`), `$80E828` (`$C08600`), `$80E866` (`$C0A926`), `$81EA7C`
  (`$9FEBC0`, dialogue window), `$81EB93` (table `$94FF04`, 3-byte entries: portraits?), `$87CDFF` (`$B8903C`),
  `$8BE72A` (table near `$90E395`), `$ACB131`/`$ACB192` (table `$94DC1A`, 3-byte entries).
  Tour logs (`tools/lua/lzlog.lua`) also saw `$CCA1D5` and `$CC86D6` (boot/title).

## `$808F01`: same format into `$7F:0000`

Source `$95-$97`, output always `$7F0000`; negative back-reference positions are explicitly zero-filled
(`$808F5B-$808F75`), as in `tools/lz.py`. Title (f1500-1518): `$AF851C`, `$AFCBB7`, `$AFC8E5`, `$AFD217`, `$AFCE87`, `$AFB1CD` (x2),
each followed by its own upload; `tools/lua/lzlog.lua` logs every call (`lz7f`). The logo (G1) is the `$AFB1CD` run.

## Bitplane conversion (verified by disassembly)

- `$808F95-$80900D` is not another unpacker. It interleaves the two eight-byte halves of each 16-byte group:
  output `[input[0], input[8], input[1], input[9], ..., input[7], input[15]]`. It processes `$9B` bytes from
  `$98-$9A`; the title loader calls it immediately after `$808F01`.
- `$809097` performs the same interleave in place, using the stack rather than the direct-page temporary buffer.
  The party sprite loader `$8BE6FB` decompresses through `$80900E` and then calls it.
- That sprite loader's six three-byte source pointers start at `$90E383`, not `$90E395`; the latter starts the
  four-byte animation-record table (`$8BE742`). The sources are `$918384`, `$91BEF2`, `$A99CF2`, `$A88000`,
  `$A78000`, `$A8C29C`.

## Other loaders (open)

- Every VRAM upload in a boot→title→attract tour came from WRAM (`$7E/$7F`), never straight from ROM
  (`snes_dmalog.lua`, 28k DMAs): all graphics are unpacked or copied into WRAM first. The intro/attract uses a second
  path (VRAM DMA from `$B9:DB35`, data in `$7F`). Find which ROM ranges feed them with `tools/lua/readers.lua`.

## Runtime capture and edge cases (2026-10-30)

`tools/lua/gfx_capture.lua` records each distinct source's decoded bytes and prior destination bytes, before
bitplane conversion. Pass one or more `--capture-dir DIR` arguments to `gfx_survey.py` to enumerate these sources,
seed RAM-dependent streams and compare the offline output with the captured output. The index records the proof.

- `$AF851C` really is consumed by the title loader, despite looking like palette data. It outputs 184 bytes.
  Distance-zero back-references read the existing destination RAM; decoding without that RAM is undefined.
- Both unpackers keep the negative-position zero-fill counter in eight bits, then use `DEC` / `BPL`.
  Large negative distances wrap that counter; the source-position subtraction is signed 16-bit. The former
  Python decoder's unbounded zero fill and unsigned positions were not exact.
- `lz.decompress(..., initial=...)` now models both cases. All 15 sources captured through boot/title match
  byte-for-byte, including `$AF851C`; no existing survey PNG changed. Tests cover overlap, negative positions,
  counter wrap and the required initial RAM for distance zero.
- Additional observed sources include `$CE8000`, `$B8C0BE`, `$AFA8E2`, `$BF8D00`, `$BF8F81`, `$BF922E`, `$BF8E66`.
  The raw-banks survey alone cannot identify their decompressed art.
- The complete 640-map original-ROM capture adds 1317 sources beyond the static tables. Packed review sheets and
  exact source offsets come from `tools/gfx_capture_survey.py`; 1313 streams reproduce offline exactly. Four bogus
  streams from unset-story map fixtures (`$00A800`, `$00B800`, `$00D800`, `$00F400`) run their 16-bit source index
  across `$FFFF` into low CPU memory. Their actual captured bytes are included and labelled
  `runtime-source-bank-wrap`, not silently omitted or claimed as verified ROM-only decodes. Non-ROM pointers and
  duplicate/static sources are also explicit index rows. All 555 packed sheets remain independent review inputs.
