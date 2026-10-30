# Reverse-engineering notes

One file per subsystem (text engine, pointers, compression, font, graphics). Mark every finding with how far it is
proven, so a later session doesn't build on a guess:

- **verified** - and how: a decoded known string, a corrupt-and-boot test, a breakpoint hit on the drawing path, a
  passing roundtrip test. Name the test or savestate.
- **guess** - and why it seems likely (byte pattern, another game, an earlier patch's notes). Promote it to verified
  before code depends on it.

Addresses are for the dump in `rom.sha1` unless a note says otherwise.

| File | Covers | State |
|---|---|---|
| text.md | encoding (16-bit glyph words, `tbl/jp.tbl`), control words, message/dictionary pointers, text ranges, fixed text (menu lists `$849B38`, items, places, names), script/ format | encoding + pointers + ranges + extraction verified (roundtrip tests); some control-word meanings guessed; weapon types and name grid open |
| font.md | 16x16 1bpp font at `$9F8000`, cell layout, VWF notes | verified |
| compression.md | LZSS `$80900E` (+ `tools/lz.py`), bitplane interleave, call sites | LZ and interleave verified; remaining sources open |
| freespace.md | `$FF` runs, 4 MB expansion | candidates only |
| graphics.md | graphics-text survey, `tools/gfx_survey.py` | expanded maps/ending/save screens reached; static sheets generated but unreviewed |
| vwf.md | English engine: codes, hooks, FONT2, MSGTAB relocation, free WRAM, width gate | verified by the marker build tour + tests |
| debug.md | debug tool: game mode, 640-map exit table, event injection, message ids, flags, save image, staff roll | ending staff roll, game over and save menus reached; full ending/epilogue and story flags open |
