# Graphics-text survey

Japanese drawn as tiles rather than through the font. Rows are added as screens are reached (phase 2 debug tool, phase
5 marker tour); the static sweep is listed at the end.

| # | Screen | Element | Layer | Source (first guess) | State |
|---|---|---|---|---|---|
| G1 | Title | small katakana `ルインアーム` above the English `RUIN ARM` logo | logo tiles at VRAM byte `$A000` (word `$5000`), katakana tiles 24-31 / 40-47 of that run (`tiles.py render --at 0xA000`) | DMA f1527 (`$8086F5`) from `$7F0000`, `$2000` bytes; `$7F` filled by the `$808F01` unpacker (`compression.md`), last call src `$AFB1CD` (file 17B1CD) at f1509/f1518. `$7F0300` at f1526 = the VRAM tile, but `lz.decompress`-style decoding of 17B1CD gives the plane-0 bytes without the interleave: one more step (bitplane expand?) between unpack and DMA is untraced | Done (phase 8): `asm/vwf.asm` `title_logo` hooks `$AFEF30` (the loader's `JSL $808F95` expand, table `$AFEED4`) and zeroes `$7F0100-$03FF` for entry 4 (`$AFB1CD` -> VRAM `$6000`, the BG chr): tiles 8-31 hold only the katakana (found by zeroing ranges from Lua, `work/qa/z`); entry 0 (-> `$5000`) holds the same art but is not what the screen shows |
| G2 | Title | `©PLEX 1995 / ©BANDAI 1995` | - | - | English already |
| G3 | World map (mode `$1B`, scene `world_map`) | `ARFF` beside the location marker; other places are icons | BG1 (chr byte `$2000`, map `$6800`) | map art | English already (Latin in the original; D19 renamed the village to match) |
| G4 | Ending | `THANKS FOR PLAYING`, `RUIN ARM`, `Fin` | ending graphics | ending event's special screen modes | English/Latin already; reached by the cold-boot `ending_full` route and inspected at zoom in independent visual QA |
| G5 | World-map A-button cards | thirteen location names; travel prompt and Yes/No | BG3 bitmap glyphs | `$B4862A`, tile-list copier `$80C8CF` | Translated with a dedicated English alphabet and wider card frame; `worldmap.md`, `warp.py world_map_all` |
| G6 | City tileset | unused-slot アキ markers | tile bitmap | `$B5A9A8`, pointer `$8C8300` | Eleven exact marker tiles now spell FREE; all other art is byte-identical after decompression; ten city maps recaptured |

Not graphics (font-drawn, handled as text): title menu `開始 続き`, name prompt `主人公の名前を自分で付けますか？ 付ける 付けない`,
name confirm `主人公 カーマイン / 妹 ボニー / すべてよろしいですか？ はい いいえ`, dialogue + speaker names, narration
screen, pause-menu tabs `道具 能力 振分 ジョイ 環境`, ending text and staff credits (script block `$02`).

Seen without Japanese: intro/attract demo (fortress, city fire), village map, HUD (portraits, HP bars).

Reached in phase 2 (`tools/debug/warp.py`, shots in `work/qa/warp/`), all look font-drawn (same 16x16 glyphs as the
dialogue; confirm in the phase 5 marker build): name entry grid, name confirm, pause-menu pages (items, status,
`振分` allocation, `ジョイ` + controls list, `環境` options), shop (`買う 売る 道具 修理` tabs, buy list, sell list,
repair), staff roll overlay. The original `maps` tour covered only 187 rooms: it mistook an empty exit-table slot
for the end. The corrected tour covers 640 mapped rooms (`docs/re/debug.md`); all 40 gameplay sheets were reviewed.

Phase-8 additions (2026-10-30): the ending staff roll is now shown on its actual map `$1D02`, with the HUD hidden
by the ending script (`ending_credits`, `credits_0` through `credits_12`). The second pause-menu row reaches
Auto/People/File, including save/load management. `work/qa/tour_en/menu_file` and `menu_file_load` have matching
original-ROM shots in `tour_jp`; the small tab numbers and empty-file icons are original behavior.

## Coverage

- The full normal ending now runs through the fortress, escape, staff-roll vignettes, forest scene and Fin with
  no skipped script waits (`docs/re/debug.md`). The message tour covers conditional dialogue independently.
  Game over is font-drawn msg `$0187`, then the title menu. All 640 mapped rooms were captured in English and in
  the original; no separate Japanese chapter/area banner was identified in the reviewed screens or static art.
- Static sweep: `python -X utf8 tools/gfx_survey.py --raw` renders all 80 raw ROM banks and known compressed
  sources in planar and linear formats, including the `$808F95` bitplane interleave. It enumerates the menu
  `$80B00F` (40), portrait `$94FF04` (52), object `$94DC1A` (448 including empty slots), and party `$90E383` (6)
  tables, plus direct-call candidates. With `--capture-dir work/qa/gfx_capture`, output is now 2053 PNG sheets;
  every one has a current independent `ok` verdict in `work/qa/graphics-verdicts`. No new Japanese art was found.
  `$AF851C` is now reproduced exactly using its initial WRAM and the hardware counter behavior (`compression.md`).
- `tools/lua/gfx_capture.lua` was also run through all 640 maps of the original ROM, plus the ending lead-in.
  `tools/gfx_capture_survey.py work/qa/maps_gfx work/qa/ending_trace --out work/qa/graphics_maps_a` produces 555
  indexed sheets for 1317 additional sources, in planar, linear and bitplane-interleaved forms. This closes the
  previous tour's compressed-map source gap. `index.tsv` records skips and four runtime-only bank-wrap streams;
  the latter are rendered from emulator bytes, never invented. Review found G5 and G6 above; their English
  replacements are covered separately by `graphics-fixes-manifest.tsv`. All four original-source findings
  have independent fixed verdicts against the English build; both manifests pass with no stale verdicts.
