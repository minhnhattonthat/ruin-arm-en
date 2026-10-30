# World-map bitmap text

The phase-8 decompressed-graphics survey found Japanese in `$B4862A`. An idle world-map screenshot shows only
Latin place labels; **A opens a Japanese location card and travel confirmation**. This was a real extraction
gap, separate from the ordinary dialogue and menu font. `tools/debug/warp.py world_map_all` now cold-boots all
thirteen cards with both Yes and No selected. It enables the location flags at `$1CB1-$1CB4`; the tour selects
each location through `$7E8000`, opens it with A, selects No with Right, and closes with B. No choice is confirmed.
The log records `$7E800C=0101` for all thirteen No states. The arrow keeps blinking: eight No captures catch its
off interval, while five show the No arrow. This is the original cursor behavior, not a missing-glyph defect.

## Rendering and patch

- `$80C61D` decompresses `$B4862A` through the call at `$80C62A`. Its source includes map graphics, Latin labels,
  Japanese glyphs, window borders, service icons and map data. The Japanese glyphs are loaded into BG3 VRAM
  `$7000` onward (BG3 CHR base `$6000`, tile `$100` onward). Leave the original resource intact for borders/icons.
- `$80C8CF` copies tile lists into the window tilemap. Thirteen location-list pointers are at `$80CAD7`; the
  frame list is `$C902`, the travel prompt `$C96C`, and the blinking Yes/No lists `$C988/$C994`.
- `tools/worldmap.py` generates an 8x16 English alphabet from the project's licensed VWF bitmap font, centering
  narrow letters inside their cells. It reuses the original Japanese glyph slots in tiles `$100-$17A`, excluding
  all border, blank, cursor and service-icon tiles. The `$80C62A` wrapper replaces exactly `$7F2400-$7F2BAF` in
  the decompressed resource; the original DMA path and extent remain unchanged. No new WRAM/VRAM is allocated.
- The `$80C8CF` wrapper redirects only those seventeen list pointers to bank `$D1`; all other lists retain the
  original bank-$80 path. The replacement location frame is 26 tiles wide and all names fit inside it, including
  `Beastfolk Village Rau`. Service icons stay at their original positions. The prompt reads `Travel here?`.
- The background prompt has no selection arrow; the original blinking selector overlays the current Yes/No
  arrow. Putting a default Yes arrow in the background would make it flash while No is selected.
- An earlier attempt uploaded the alphabet to VRAM `$9000`. Although the world map did not use those tiles,
  normal maps cached their background art there: independent city/ending reviews caught garbage across later
  scenes. The final implementation stays within the original font resource. A regression test locks its extent
  to `$7B0` bytes and verifies every preserved border/icon tile against the original.
- Generated assets: `build/vwf/worldmap.asm` and `worldmap.bin`; assembler hooks and source-byte assertions are
  in `asm/vwf.asm` and `tools/asm.py`. The normal 4 MB build includes them; the debug Lua is not in the ROM.

Names follow `glossary.md`, which adopted all thirteen original Latin map labels in phase 9 (D22): ARFF, LONDIUM,
WHAIAL, MARY, RAW, STELM, WARSE, MARTHNAL, RAVENNA, LUTEA, TIFNU, MEDIOM, RAIDROID. `warp.py world_map_labels`
shows them all (every location flag set, no card open); the earlier "RAN" was a misreading of RAW.

## Unused city tiles

The same survey found アキ markers in eleven tiles of `$B5A9A8`, the city tileset. Its pointer is `$8C8300`, in
the `$8C816B` graphics table at index `$1B * 15` (loader `$86BDB6`). The other raw-ROM occurrences of the same
three bytes are consecutive actor-script byte values, not graphics pointers.

`tools/unused_tiles.py` changes only exact marker bitmaps to the two halves of FREE and relocates the compressed
stream through that pointer. All tile indices and every other byte of decompressed art are unchanged. The test
`test_relocated_tiles_preserve_all_non_marker_art` decompresses the actual built pointer and checks that only
tiles 29, 30, 175 and 244-251 differ. All ten maps `$1B00-$1B09` have fresh cold-boot captures.

## Evidence

- Original cards: `work/qa/worldmap_cards/` (all thirteen Japanese cards, VRAM/RAM dumps).
- English cards and Yes/No: `work/qa/graphics_fixes/worldmap/` (26 captures, two sheets).
- City maps: `work/qa/graphics_fixes/city/` (ten city captures plus the starting field, one sheet).
- Built bitmap assets: `python -X utf8 tools/graphics_text_survey.py` renders them under
  `work/qa/graphics_fixes/assets/`, following the relocated city pointer from the built ROM.
- Gate: `work/qa/graphics-fixes-manifest.tsv`, `work/qa/graphics-fixes-verdicts/`.
  The original-source survey retains its Japanese art; its findings are resolved against these English captures.
  Final independent `vram_fixed.tsv` verdicts approve all five sheets and resolve all four source findings;
  `work/qa/ending-verdicts/vram_fixed.tsv` also confirms clean backgrounds throughout the complete ending.
