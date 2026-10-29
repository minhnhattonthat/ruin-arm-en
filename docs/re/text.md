# Text engine, encoding, pointers

Addresses: CPU (LoROM, FastROM `$80+` mirror) and file offset. ROM: `rom.sha1`. Mapping LoROM, header `$7FC0`
("SFC RUIN ARM", map `$30` FastROM, type `$02` ROM+RAM+SRAM, size byte `$0C`, SRAM `$03` = 8 KB). No earlier fan
patch found (web search 2026-10-30: only an unlinked forum claim; nothing on romhacking.net to diff against).

## Encoding (verified)

- Every character is one **16-bit little-endian word** = glyph index into the dialogue font (`font.md`).
  Words `$0000-$7FFF` are glyphs, `$8000+` are control words. No Shift-JIS, no 8-bit text anywhere found.
- Table: `tbl/jp.tbl` (key = the two ROM bytes, e.g. `2E00=ん`). Kana/latin `$000-$0DF`, punctuation `$0E0-$0EF`,
  kanji `$0F0-$353` (incl. credit-only name kanji), half-width two-letter menu cells `$274-$2BD`, `$34A-$351`,
  `$354`, written `〔...〕` so the table stays one-to-one. Duplicated glyphs get distinct values (`光₂` `$2C4`,
  `将₂` `$311`, `｡` `$349`, `｢｣` `$33D/$33E`).
- **Verified:** code→glyph by breakpoint on the draw path (dialogue `ボニー / お父さん、` drew glyph cells
  `$9F9210, $9F8C60, $9F9D20, $9F8050...` = codes `$091 $066 $0EA`, `$005 $22E $00B $02E`); table read by eye from
  `tools/font_sheet.py` sheets, then the whole decoded script (`tools/textdump.py --expand`) read by a reviewer
  agent for look-alike swaps: none found. The few odd spots it flagged are the ROM's own bytes (weathered signs
  `「ルテ・へ」` msg `109A/109B` use `・`; `ステルムヘ` uses katakana `ヘ` `$06D`; credit handles `田 鞭々`, `岬 額々`).
- The script uses 662 distinct glyphs; the font has 1024 cells (`$355-$3FF` are window/cursor/menu pieces).

## Text engine (bank $81)

- Printer `$81E195`: reads the next word from the dictionary buffer `$7ED500` if one is active, else from the
  message (`[$0CA7],$0CAD*2`). Glyph → `$81E929` (draws 16x16 1bpp into a WRAM tile buffer), tilemap writes to
  `$7EC844+`. **Fixed 16 px advance; the line wraps itself after 14 glyphs** (`$0CB3 & $3F >= $38`, `$81E212`).
  Box = 3 lines (seen in game). Phase 5 needs a VWF here.
- Control words: high byte = command, low byte = argument; jump table `$81E28B` indexed by `(~hi) & $FF`
  (`$FF`..`$EC`). Argument words that follow in the stream:

| Word | Name in dumps | Extra words | Meaning (verified = seen in game / read in code) |
|---|---|---|---|
| `FFxx` | end | 0 | end of message; low nibble = wait, high nibble = next state (code `$81E2D3`). **Terminator** |
| `FExx` | fe | 0 | like FF but state `$8007`: wait then clear and continue (credits use `FE11` between pages) |
| `FDxx` | fd | 0 | like FF, state `$8001` (close window?) - guess |
| `FCxx` | col | 0 | text palette (`$0CBD`); `FC01` = speaker-name colour, `FC00` back (seen: yellow names) |
| `FBxx` | spd | 0 | print speed `$0CBF` |
| `FAxx` | fa | 0 | sets bits in `$0CC4,x` (portrait/window param) - guess |
| `F9xx` | choice | 2 (xx even) / 3 (xx odd) | choice cursor; the words are the msg ids jumped to per answer. **Terminator** |
| `F8xx` | d | 0 | insert dictionary entry xx (`$838000` table, 144 entries `D00-D8F`) |
| `F7xx` | wait | 0 | wait for key, new page |
| `F6xx` | nl | 0 | new line |
| `F5xx` / `F4xx` | f5 / f4 | 0 | portrait / window parameters (`$0CC4/$0CC5,x`); `F4` calls `$81EB63` (loads portrait) |
| `F3xx` | f3 | 0 | sets low bits of `$0CB7` - guess (box style) |
| `F2xx` | name | 0 | party member xx's name (from WRAM `$146A`, 7 glyphs) |
| `F1xx` | sfx | 0 | sound effect xx (`JSL $80ABA6`) |
| `F0xx` | goto | 1 | continue with message id = next word. **Terminator** |
| `EFxx` | item_v | 0 | item name of the item in `$0CD5` |
| `EExx` | num | 0 | decimal number from `$0CD3` |
| `EDxx` | item | 0 | item name xx (table below) |
| `ECxx` | set | 1 | next word → `$00D2` (event flag/argument) |

## Pointers (verified: every message decodes and the messages tile each text range with no gap)

- Message id = `block << 8 | index` (`$0CA4`/`$0CA5`), events pass it as a word (e.g. event `ADAA11: 32 10` = `$1032`).
- Block table `$838642` (file `018642`): 0x14 entries of 24-bit pointers; unused blocks = `$83867E` (just past it).
- Each block starts with 16-bit pointers (same bank); count = (first pointer - block start) / 2. Unused slots point at
  the next block's table.

| Block | Table | Msgs | Text (file) | Content |
|---|---|---|---|---|
| `$00` | `$988000` (0C0000) | 256 | 0C0200-0C3CBE | towns/NPCs |
| `$13` | `$98BCBE` (0C3CBE) | 256 (110 unique) | 0C3EBE-0C5761 | NPCs, shops |
| `$11` | `$83B54A` (01B54A) | 256 | 01B74A-01EEA4 | story |
| `$02` | `$BB8000` (1D8000) | 10 | 1D8020-1D846A | ending + staff credits |
| `$10` | `$BB846A` (1D846A) | 256 | 1D866A-1DBF0A | story |
| `$12` | `$BBBF0A` (1DBF0A) | 256 | 1DC10A-1DFEDC | story |

- Dictionary `$838000` (file 018000-01811F): 144 16-bit pointers (bank `$83`) to `$FFFF`-terminated words,
  018120-018641. Names, places and common endings (`D28 = お父さん`).
- Orphans inside ranges (no pointer): one dead message at 01B834-01B856, one stray `F600` at 1DF416. Keep them in the
  repack so offsets stay identical.
- Free after the script: 01EEA4-020000 (4.4 KB, bank `$83`), 0C5761-0C8000 (10 KB, bank `$98`), see `freespace.md`.

## Other text (format known, all strings not yet listed)

- **Menu records** (bank `$84`, file ~024D00-026400; guess on the extent, format verified by structure on the
  name-confirm screen `これでよろしいですか？ / はい　いいえ` at 02580C): records `pos16, count8, count x glyph16`,
  list ends `FFFF`. `pos` = tilemap word offset. Pause-menu tabs `道具 能力 振分 ジョイ 環境` and the title menu
  `開始 続き` are font glyphs too. Phase 4: find the readers and their pointer tables instead of the byte scan.
- **Item names**: `$84B2A1`: id < `$DF` → `$8AB96C + offset[$8AB76E + 2*id]`, 8 glyph words, `0000`-padded;
  ids >= `$DF` come from WRAM `$7E5800` (renamable items?).
- Character names (hero `カーマイン`, sister `ボニー`) live in WRAM `$146A` (7 glyphs each); defaults and the name
  entry grid not yet located.
- **Staff roll** (found in phase 2, `docs/re/debug.md`): `$B1D3E2` (file 18D3E2), 11 pointers (bank `$B1`) to
  strings of glyph words + `$8000|pos` tilemap-position words, `FFFF`-terminated (18D3FC-~18D7xx), drawn by
  `$B1D210` onto BG3. Not part of the six message blocks; includes a special-thanks page not in block `$02`.
  `tests/test_debug.py` decodes page 0.
- Still to find in phase 4: enemy names, place names on maps, shop/status labels, save screen, name-entry grid,
  any text built in code (`LDA #glyph / STA` chains). Every screen `tools/debug/warp.py` reaches is a check.

## Tools
- `tools/textdump.py [--expand]`: whole script, one line per message id → `work/re/script_jp.txt`.
- `tools/font_sheet.py`: labelled glyph sheets; `--codes` for a zoomed subset.
- `tools/lua/romreads_all.lua`, `readers.lua`, `lzlog.lua`: trace probes used above; `lzcall.lua` (both LZ
  entries with JSL return chain), `wlog.lua` (every byte change in a WRAM range with PC).
