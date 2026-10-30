# English engine: VWF, font bank, message relocation (phase 5)

`asm/vwf.asm` (asar 1.91, `tools/asm.py`), font `fonts/vwf.txt` (`tools/font.py`), codec `tools/en.py`, build
`tools/build.py`. ROM grows to 4 MB (header size byte was already `$0C`). Verified by the marker build tour
(`work/qa/marker/`, scenes below) and `tests/test_identity.py` / `test_vwf.py`.

## Codes

| Codes | What | Drawn by |
|---|---|---|
| `$0000-$03FF` | original Japanese cells (`$9F8000`) | unchanged; the VWF gives them 16 px |
| `$0420-$047E` | singles: printable ASCII c = `$0400 + c`; `$0401-$041F` other font chars (— ： × …) | FONT `$FC8000` |
| `$0480-$0FFF` (not `$07FF`) | slices: one 16 px cell of a fixed field's text set proportionally, assigned per build (`font.slices`, ~1.5k used of 2943) | FONT bank `$FC + (c - $400) >> 10` |
| `$07FF`, `$7Fxx` | game's blank / WRAM glyphs (`$7E5E80`) | unchanged |

Messages are encoded in singles (proportional in the dialogue VWF). Fixed fields (menus, items, places, ...) and the
staff roll are drawn one code per 16 px cell, so the build sets each field's text proportionally and cuts it into
16 px slices, one code each (blank cells: `0000`): no gap between letters, and a field fits by pixels (16 per cell),
not letters. A slice's advance is 16, the last one's runs to the text's end, so an `{item}` insert in dialogue reads
the same. Runs split at 2+ spaces keep the column a 2-letters-a-cell layout gave them (numbers and cursors the code
draws at fixed cells still line up); `|` starts the next 2-cell unit (command cells picked by index, `84967B`,
`8496A4`). Names (`name_hero`/`name_sister`) use singles (the name entry edits them letter by letter): max 7 letters.
The glyph palette record `84:8A27` is patched per cell (`build.PALETTE`: 21-22 `全部` "All", 23 the shop's red `個`
"pc").

## Hooks (original bytes asserted by `tools/asm.py` HOOKS)

| Address | Was | Now |
|---|---|---|
| `$81E1CC` | printer: glyph → `$81E929` into the cell at `$0CB1`, 2x2 tilemap at `$0CB3`, +1 cell, wrap at 14 | `vwf_char`: render the cell into SCRATCH `$7E:9F00` with `$81E929`, OR it into the line at the pen. `$0CB1` = cell base (bits 6+) + pen px in the cell (bits 0-3); every writer of `$0CB1` stores a line base, so px resets with it. A cell is cleared and given its tilemap entries when the pen enters it. Advance: widths table (codes `$0400-$07FF`), else 16. Then the game's own wrap check (`$81E217`) / glyph loop (`$81E21F`) |
| `$81E227` | frame DMA: source = saved `$0CB1`, size = glyphs this frame x `$40` | `vwf_dma`: from the saved cell to the cell holding the pen (min one cell) |
| `$81E8B7` | message id → block table `$838642` → 16-bit pointer | `msg_ptr`: 24-bit pointer per id from MSGTAB `$D28000` (`0x1400` ids x 3). Untranslated ids keep their original address; blocks `$03-$0F` alias `$01` as before |
| `$81E4B9` | `{num}` digit + `$A1` (full-width) | + `$0430` (English digits) |
| `$81E92E`, `$85EC2D` | cell drawer (and its copy for the name entry): `TXA / CMP #$7F00` | `font_a`/`font_b`: codes `$0400-$0FFF` (not `$07FF`) read their FONT bank (DB = bank, Y = cell), others go back to the original path |
| `$8296F0` | ruin password: `$140C` 8 words == `$829711` | `password`: same compare, a-z singles folded to A-Z (`build.py` writes `RAIDROID` at `$829711`) |

Every byte the build changes goes through `build.put` (or, for asar and the checksum, a logged diff) into
`build/ruinarm_en.writes.txt`; `tests/test_build.py` runs `romdiff.py` with it and holds writes inside the original
ROM to fields, staff, grids/password, hook sites and the checksum.

Free WRAM `$7E:9000-$9FFF`: no write in any `tools/lua/wramuse.lua` run (8 scenes + the 187-map tour;
`tools/wramfree.py`). Used: `$9F00-$9F7F` scratch cells, `$9F80-$9F99` VWF vars.

Expansion: `$D18000` code + widths (codes `$0400-$0FFF`), `$D28000` MSGTAB, `$D2C000` relocated messages up to FONT
(one bank never crossed by a message; they end near `$D7`), `$FC8000-$FFFFFF` FONT (4 banks x 1024 cells). `$D08000`
(the old one-bank font) is unused.

Menu records can be redrawn with other cell counts (`fixed.CELLS`, applied by `fixed.relayout`): a record grows by
what the next record of its list gives up, so the list keeps its bytes and VRAM cells (84:D399 `体` "Body",
84:D89E `妹` "Sister"). No pointer in bank `$84` reaches a record after a list's first.

## Width gate (measured in the marker build, `tools/marker.py`)

| Variant | Budget | Evidence |
|---|---|---|
| Dialogue line (portrait or not, narration, shop: one box) | **223 px** of advance (sum of `font.adv`). A pen reaching 224 px runs the game's auto-wrap, and the `\n` after it then leaves a blank line | msg 1032 page 1: three lines of exactly 223 px, last glyph whole, no wrap (`gate` = `msg_bonnie` shot); msg 01B7 at 224 px gave a blank line (first marker run) |
| Rows per page | **4**, the speaker-name row included (`{col:01}{name:xx}...\n` + 3 lines); more scrolls the box | gate page 1 (name + 3), page 2 (4 rows) |
| Past 223 px | the glyph crossing cell 14 is clipped (lost) and the line auto-wraps: lint must hold lines to 223 | gate page 2 line 1 (`0123456` lost the 6) |
| `{name:xx}` insert | name slots: 7 letters (WRAM `$146A`, trailing 0 stripped) = at most 56 px | code `$81E3F2` |
| `{item}` / `{item_v}` insert | item name: 8 slice cells, drawn at slice widths = the name's own px (≤ 112 px reserved) | code `$81E45D`; `msg_item` shot |
| `{num}` | English digits, 6 px each | |
| Fixed fields (menus, items, places, ingots, status...) | **16 px per cell** of the field (`max` in script/*.json, or `fixed.CELLS`), text proportional; the screen may leave less room than the record (status page: label to `:` = 32 px) | menus, status, shop, name confirm shots (`work/qa/sheet3.png`) |
| Names (`name_hero`, `name_sister`) | **7 letters** (one per cell) | status / name confirm shots |
| Staff roll | 16 px per cell from the run's `{pos}` column to tile 31 (strings relocated; a `{pos}` may move column, not row) | `credits_0..12` shots (heading row only: the field HUD hides the rest) |
| Dialogue choices (`{choice}`) | the cursor sits in cell 1 and the selected option's colour starts at cell 3, so each option row is the JP's blank, blank, digit cells (`0000 0000 00A2+n`, written `  1` in the script; `en.py` swaps them in) then text from px 48 | phase 8 `msgs_XX` tour (m_1080_04) |
| Colour (`{col:01}` / `{col}`, `$0CBD` palette bits) | palettes are per 8x8 tile: a colour turned on mid-cell moves the pen to the next tile edge (px 1-8 -> 8, 9-15 -> next cell; `vwf.asm colour`, modelled in `batches.width`); turned off, the rest of that tile keeps the colour. A line break resets the colour (the JP re-opens it each row): `en.carry_col` re-opens a span its next row closes | phase 8 tour |
| `{fd:xx}` / `{fd}` | an inline pause, no line break (the JP writes `{fd:13}\n` where it wants one) | 130B "sky.{fd:13}There's" ran on |
| Ending messages (block `$02`) | not measured: the ending screen setup is a debug-tool gap (`debug.md`) | - |

## Known gaps (phase 7 engine work)

- Hero/sister names (WRAM, singles) show one letter per 16 px cell in menus (`S h i n e`): a runtime VWF for the
  `$7Fxx`/single path in `$849B38` would close it.
- Labels still short because 32 px of screen is all there is (D18): `Atk`/`Def` (status page, shop compare, allot
  page: the `:`/number column sits 32 px after the label), `Pad` (tab), `BWH`, `Tech`, 1-cell ailment icons. A narrow
  menu font (3-4 px lowercase) would fit `Attack`/`Defense`/`Joypad` in 32 px.
- Shop compare `Use  (  )`/`Hold (  )` (84CE36/84CE43): the code draws an icon over cell 1, so only cell 0 (16 px)
  shows the label (`Us`/`Hol` peek out; JP used one kanji).
- Title: the small katakana ルインアーム above the logo (graphics, D10; lead in `graphics.md` G1).
