# Graphics-text survey

Japanese drawn as tiles rather than through the font. Rows are added as screens are reached (phase 2 debug tool, phase
5 marker tour); the static sweep is listed at the end.

| # | Screen | Element | Layer | Source (first guess) | State |
|---|---|---|---|---|---|
| G1 | Title | small katakana `ルインアーム` above the English `RUIN ARM` logo | logo tiles at VRAM byte `$A000` (word `$5000`), katakana tiles 24-31 / 40-47 of that run (`tiles.py render --at 0xA000`) | DMA f1527 (`$8086F5`) from `$7F0000`, `$2000` bytes; `$7F` filled by the `$808F01` unpacker (`compression.md`), last call src `$AFB1CD` (file 17B1CD) at f1509/f1518. `$7F0300` at f1526 = the VRAM tile, but `lz.decompress`-style decoding of 17B1CD gives the plane-0 bytes without the interleave: one more step (bitplane expand?) between unpack and DMA is untraced | D10: remove; open (phase 8) |
| G2 | Title | `©PLEX 1995 / ©BANDAI 1995` | - | - | English already |

Not graphics (font-drawn, handled as text): title menu `開始 続き`, name prompt `主人公の名前を自分で付けますか？ 付ける 付けない`,
name confirm `主人公 カーマイン / 妹 ボニー / すべてよろしいですか？ はい いいえ`, dialogue + speaker names, narration
screen, pause-menu tabs `道具 能力 振分 ジョイ 環境`, ending text and staff credits (script block `$02`).

Seen without Japanese: intro/attract demo (fortress, city fire), village map, HUD (portraits, HP bars).

Reached in phase 2 (`tools/debug/warp.py`, shots in `work/qa/warp/`), all look font-drawn (same 16x16 glyphs as the
dialogue; confirm in the phase 5 marker build): name entry grid, name confirm, pause-menu pages (items, status,
`振分` allocation, `ジョイ` + controls list, `環境` options), shop (`買う 売る 道具 修理` tabs, buy list, sell list,
repair), staff roll overlay. The `maps` tour (`work/qa/warp/maps/map_AARR.png`, 187 rooms) is the base for the
place-banner check.

## Still to survey

- Screens the debug tool can't reach yet (`docs/re/debug.md` §Open leads): save/load screen, boss/area banners,
  chapter cards if any, game over, the ending scene.
- Static sweep: every unpacked graphics block. Needs the remaining loaders (`compression.md` §Other loaders) and the
  LZ pointer tables (`$80B00F`, `$94FF04`, `$94DC1A`, `$90E395`) enumerated, then `tiles.py render` sheets read by
  reviewer agents.
