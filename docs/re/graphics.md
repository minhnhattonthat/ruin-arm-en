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

## Still to survey

- Mid-game screens only the debug tool can reach: pause-menu sub-pages (items, status, `振分` allocation, `ジョイ`
  config, `環境` options, save/load), shops, boss/area banners, chapter cards if any, game over, ending.
- Static sweep: every unpacked graphics block. Needs the remaining loaders (`compression.md` §Other loaders) and the
  LZ pointer tables (`$80B00F`, `$94FF04`, `$94DC1A`, `$90E395`) enumerated, then `tiles.py render` sheets read by
  reviewer agents.
