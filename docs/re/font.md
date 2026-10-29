# Font

## Dialogue / menu font (verified)

- ROM `$9F8000-$9FFFFF` (file 0F8000-0FFFFF), uncompressed, 1024 cells of **16x16, 1bpp**.
- Cell `c` = four 8x8 1bpp tiles (8 bytes each): TL at `$9F8000 + (c>>3)*$100 + (c&7)*$10`, TR +8, BL +$80, BR +$88
  (the sheet is 8 cells wide, 128 px). Verified by the draw routine `$81E929` reading exactly these bytes for the
  glyphs of a known line (`text.md`).
- Every text system seen so far draws from it: dialogue, narration, credits, title menu `開始 続き`, pause-menu tabs,
  name confirmation. Narrow "two letters per cell" menu labels (`ジョ|イ`, `セー|ブ`, `cm`, `kg`...) are cells
  `$274-$2BD`: pre-drawn half-width katakana pairs, not a second font.
- Glyphs are drawn ~12-14 px wide inside the 16 px cell; the engine advances 16 px per glyph, 14 glyphs per line.
- Render: `python tools/font_sheet.py OUT.png [--first 0x100 --count 0x80 --zoom 3]`.

## Implications for English (phase 5)

- The cell grid is the code space: glyph code = font cell, so English letters can be new cells (`$356-$3FF` are
  free-looking or UI pieces; check before use) or the existing latin `$0AB-$0DE` (full-width 16 px: too wide).
- A VWF in `$81E929`/`$81E195` (shift into the WRAM tile buffer, `$0CB1` = pixel/tile position, `$0CB3` = tilemap
  column) is the expected route; 8x16 or 8x8 glyphs would double the line length.
