# Compression

## LZSS at `$80900E` (verified)

- Inputs: source `$95-$97` (24-bit), destination `$98-$9A` (usually WRAM `$7E:B800` or `$7F:8000`).
- Block: u16 output size; then a flag byte read **LSB first** before every 8 items. Flag 1 = literal byte. Flag 0 =
  u16 word `w`: copy `(w & $F) + 3` bytes from output position `pos - (w >> 4)` (12-bit distance); positions before the
  output start read as 0 (the routine writes zeros for them).
- `tools/lz.py`: `decompress` + a greedy `compress`; `python tools/lz.py selftest` decompresses the real block
  `$9FEBC0` (138 → 336 bytes, loaded when the first dialogue box opens) and roundtrips it. The packer is not
  byte-identical to the original one; identity builds must copy untouched blocks, never repack them.
- Call sites (`JSL $80900E`): `$80AB40` (table `$80B00F,x`), `$80E828` (`$C08600`), `$80E866` (`$C0A926`), `$81EA7C`
  (`$9FEBC0`, dialogue window), `$81EB93` (table `$94FF04`, 3-byte entries: portraits?), `$87CDFF` (`$B8903C`),
  `$8BE72A` (table near `$90E395`), `$ACB131`/`$ACB192` (table `$94DC1A`, 3-byte entries).
  Tour logs (`tools/lua/lzlog.lua`) also saw `$CCA1D5` and `$CC86D6` (boot/title).

## `$808F01`: same format into `$7F:0000`

Source `$95-$97`, output always `$7F0000`; back references read `$7F` as it stands, so a block may pull in bytes a
previous call left there. Title (f1500-1518): `$AF851C`, `$AFCBB7`, `$AFC8E5`, `$AFD217`, `$AFCE87`, `$AFB1CD` (x2),
each followed by its own upload; `tools/lua/lzlog.lua` logs every call (`lz7f`). The logo (G1) is the `$AFB1CD` run.

## Other loaders (open)

- Every VRAM upload in a boot→title→attract tour came from WRAM (`$7E/$7F`), never straight from ROM
  (`snes_dmalog.lua`, 28k DMAs): all graphics are unpacked or copied into WRAM first. The intro/attract uses a second
  path (VRAM DMA from `$B9:DB35`, data in `$7F`); `$808FA8-$80900D` is another unpacker (`MVN` loop). Find which ROM
  ranges feed them with `tools/lua/readers.lua` before the graphics-text work in phase 5.
