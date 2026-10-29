# Graphics-text survey

Japanese drawn as tiles rather than through the font. Rows are added as screens are reached (phase 2 debug tool, phase
5 marker tour); the static sweep is listed at the end.

| # | Screen | Element | Layer | Source (first guess) | State |
|---|---|---|---|---|---|
| G1 | Title | small katakana `ルインアーム` above the English `RUIN ARM` logo | OBJ (logo tiles sit in the OBJ area, VRAM `$C000+`, `work/qa/title/ppu_002300.*`) | WRAM upload, unpacker not yet traced | found; D5: keep or remove, decide in phase 5 |
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
