# English engine: VWF, font bank, message relocation (phase 5)

`asm/vwf.asm` (asar 1.91, `tools/asm.py`), font `fonts/vwf.txt` (`tools/font.py`), codec `tools/en.py`, build
`tools/build.py`. ROM grows to 4 MB (header size byte was already `$0C`). Verified by the marker build tour
(`work/qa/marker/`, scenes below) and `tests/test_identity.py` / `test_vwf.py`.

## Codes

| Codes | What | Drawn by |
|---|---|---|
| `$0000-$03FF` | original Japanese cells (`$9F8000`) | unchanged; the VWF gives them 16 px |
| `$0420-$047E` | singles: printable ASCII c = `$0400 + c`; `$0401-$041F` other font chars (— ： × …) | FONT2 `$D08000` |
| `$0480-$07FE` | digraphs: two letters in one 16 px cell, assigned per build from the fixed fields' pairs | FONT2 |
| `$07FF`, `$7Fxx` | game's blank / WRAM glyphs (`$7E5E80`) | unchanged |

Messages are encoded in singles (proportional in the dialogue VWF). Fixed fields (menus, items, places, ...) and the
staff roll are drawn one code per 16 px cell, so they use digraphs: 2 letters per cell, 16 in an 8-cell item name.
Names (`name_hero`/`name_sister`) use singles (the name entry edits them letter by letter): max 7 letters.

## Hooks (original bytes asserted by `tools/asm.py` HOOKS)

| Address | Was | Now |
|---|---|---|
| `$81E1CC` | printer: glyph → `$81E929` into the cell at `$0CB1`, 2x2 tilemap at `$0CB3`, +1 cell, wrap at 14 | `vwf_char`: render the cell into SCRATCH `$7E:9F00` with `$81E929`, OR it into the line at the pen. `$0CB1` = cell base (bits 6+) + pen px in the cell (bits 0-3); every writer of `$0CB1` stores a line base, so px resets with it. A cell is cleared and given its tilemap entries when the pen enters it. Advance: widths table (codes `$0400-$07FF`), else 16. Then the game's own wrap check (`$81E217`) / glyph loop (`$81E21F`) |
| `$81E227` | frame DMA: source = saved `$0CB1`, size = glyphs this frame x `$40` | `vwf_dma`: from the saved cell to the cell holding the pen (min one cell) |
| `$81E8B7` | message id → block table `$838642` → 16-bit pointer | `msg_ptr`: 24-bit pointer per id from MSGTAB `$D28000` (`0x1400` ids x 3). Untranslated ids keep their original address; blocks `$03-$0F` alias `$01` as before |
| `$81E4B9` | `{num}` digit + `$A1` (full-width) | + `$0430` (English digits) |
| `$81E92E`, `$85EC2D` | cell drawer (and its copy for the name entry): `TXA / CMP #$7F00` | `font_a`/`font_b`: codes `$0400-$07FE` read FONT2 `$D08000`, others go back to the original path |

Free WRAM `$7E:9000-$9FFF`: no write in any `tools/lua/wramuse.lua` run (8 scenes + the 187-map tour;
`tools/wramfree.py`). Used: `$9F00-$9F7F` scratch cells, `$9F80-$9F99` VWF vars.

Expansion: `$D08000` FONT2 (32 KB), `$D18000` code + widths, `$D28000` MSGTAB, `$D2C000-$FFFFFF` relocated messages
(one bank never crossed by a message).

## Width gate (measured in the marker build, `tools/marker.py`)

| Variant | Budget | Evidence |
|---|---|---|
| Dialogue line (portrait or not, narration, shop: one box) | **223 px** of advance (sum of `font.adv`). A pen reaching 224 px runs the game's auto-wrap, and the `\n` after it then leaves a blank line | msg 1032 page 1: three lines of exactly 223 px, last glyph whole, no wrap (`gate` = `msg_bonnie` shot); msg 01B7 at 224 px gave a blank line (first marker run) |
| Rows per page | **4**, the speaker-name row included (`{col:01}{name:xx}...\n` + 3 lines); more scrolls the box | gate page 1 (name + 3), page 2 (4 rows) |
| Past 223 px | the glyph crossing cell 14 is clipped (lost) and the line auto-wraps: lint must hold lines to 223 | gate page 2 line 1 (`0123456` lost the 6) |
| `{name:xx}` insert | name slots: 7 letters (WRAM `$146A`, trailing 0 stripped) = at most 56 px | code `$81E3F2` |
| `{item}` / `{item_v}` insert | item name: 8 digraph cells = 16 letters, drawn at pair widths (≤ 112 px) | code `$81E45D` |
| `{num}` | English digits, 6 px each | |
| Fixed fields (menus, items, places, ingots, status...) | **2 letters per cell** of the field (`max` in script/*.json), a pair ≤ 16 px by construction | menus, status, shop, name confirm shots |
| Names (`name_hero`, `name_sister`) | **7 letters** (one per cell) | status / name confirm shots |
| Staff roll | 2 letters per original glyph per positioned run (repacked in place) | `credits_0/5/10` shots |
| Dialogue choices (`{choice}`) | guess: same 223 px lines; not seen in a shot yet | - |
| Ending messages (block `$02`) | not measured: the ending screen setup is a debug-tool gap (`debug.md`) | - |

## Known gaps (phase 7 engine work)

- Digraph cells leave a gap after each pair (item names read `ab cd ef`): a menu VWF in `$849B38` (records) and
  `$849B5D` (item names) would render each record proportionally across its own cells, storage still 2 letters a
  word. Hero/sister names in menus show one letter per 16 px cell.
- Code-built Japanese: the red `個` after the shop count (and likely `枚`), drawn outside the lists.
- Name entry grid is kana (`026446-0266xx`); needs an alphabet grid of singles.
- Title: the small katakana ルインアーム above the logo (graphics, D10).
- Staff roll is repacked in place: longer English credits need its strings relocated (pointers in bank `$B1`).
