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
- Block table `$838642` (file `018642`): 0x14 entries of 24-bit pointers. Blocks `$01` and `$03-$0F` all point at
  `$83867E`, which is a **real block** (found phase 4; phase 1 had it as a dummy): ids `$01xx` and `$03xx-$0Fxx`
  show the same messages. Its slots `$00-$20` share one message, `$E2-$FF` point at block `$11`'s table.
- Each block starts with 16-bit pointers (same bank); count = (first pointer - block start) / 2. Unused slots point at
  the next block's table.

| Block | Table | Msgs | Text (file) | Content |
|---|---|---|---|---|
| `$00` | `$988000` (0C0000) | 256 | 0C0200-0C3CBE | towns/NPCs |
| `$01` (= `$03-$0F`) | `$83867E` (01867E) | 256 (193 unique) | 01887E-01B54A | princess/court, rebels, towns |
| `$13` | `$98BCBE` (0C3CBE) | 256 (110 unique) | 0C3EBE-0C5764 | NPCs, shops (124 slots share the empty message `FFFF` at 0C5762) |
| `$11` | `$83B54A` (01B54A) | 256 | 01B74A-01EEA4 | story |
| `$02` | `$BB8000` (1D8000) | 10 | 1D8020-1D846A | ending + staff credits |
| `$10` | `$BB846A` (1D846A) | 256 | 1D866A-1DBF0A | story |
| `$12` | `$BBBF0A` (1DBF0A) | 256 | 1DC10A-1DFEDC | story |

- Dictionary `$838000` (file 018000-01811F): 144 16-bit pointers (bank `$83`) to `$FFFF`-terminated words,
  018120-018641. Names, places and common endings (`D28 = お父さん`).
- Orphans inside ranges (no pointer): one dead message at 01B834-01B856, one stray `F600` at 1DF416. Keep them in the
  repack so offsets stay identical.
- Free after the script: 01EEA4-020000 (4.4 KB, bank `$83`), 0C5764-0C8000 (10 KB, bank `$98`), see `freespace.md`.
- Unused slots point at the next block's table (`$00` → `$13`'s, `$02` → `$10`'s): no message, keep them pointing
  just past their block.
- **Repack (verified, phase 3):** `tools/pack.py` unpacks dictionary, the seven blocks and the staff roll into word
  lists (shared slots, unused slots and orphans kept) and packs them back; `tools/build.py` wipes each range to `FF`
  and repacks it, and the ROM comes out byte-identical (`tests/test_identity.py`). Exact ranges are pinned in
  `test_blocks_cover_known_ranges`.

## Fixed text (phase 4: `tools/fixed.py`, written back in place, English space-padded to the field)

- **Menu lists** (bank `$84`, file 020A27-026390, 308 records): drawn by `$849B38` (verified: read-hook probe
  `tools/lua/textreads.lua` on every menu/shop/name scene, `work/qa/reads/`). List = records `pos16, count8,
  count x glyph16`, `FFFF` ends it; `pos` = tilemap word offset. Callers pass the list in `[$10]` (JSLs at 020A72,
  021478, 021648, 02199B, 021A37, 021E68), mostly from 16-bit pointer tables sitting beside the lists. Found by a
  structural sweep (`fixed.menu_lists`); the probe's list starts all fall on sweep hits. Includes pause tabs, shop,
  options, status, character profile (race/skill/hobby/likes/dislikes/personality), alchemist (錬金術師) dialogs,
  crafting, name prompts, title `開始 続き`, file menu. Two records look like data (glyph palettes): 84:8A27
  (`〔/〕○×〔01〕..∞`) and 84:967B / 84:96A4 (two-glyph command cells `右装左装..`, `ｾｰﾌﾞﾌﾟﾛﾃｸﾄ..`): each
  2-glyph cell is one command, the code picks cells by index. Check in the phase 5 marker build.
- `$849B38`-format lists with `7Fxx` words (024C1E, digit cells) are tile data, not text (the sweep rejects them).
- **Item names**: `$84B2A1`: id < `$DF` → `$8AB96C + offset[$8AB76E + 2*id]`; record stride `$34`, name = 8 glyph
  words at record + 1 (odd file offset 05396D), `0000`-padded; 110 non-blank. Ids >= `$DF` come from WRAM `$7E5800`
  (crafted items: names typed by the player or taken from `ingot`).
- **Other tables** (`fixed.TABLES`/`PTRS`, each reached by a 16-bit pointer list beside it): places `$85F9CD`
  (72 x 8), default hero/sister names `$85C3DC`/`$85C4FC` (16 x 8 each, read by `$85C616`/`$85C6D9`), ingots
  `$85E492`, equip labels `$85E7D4`, AI tactics `$84D5A5`, pad labels `$84D648`, use/act `$84D52C`/`$84D540`,
  alchemy elements `$81FD33` and heat/cool `$81FD5F`, status words `$85DEFE` (FFFF-terminated, 11).
- Character names (hero `カーマイン`, sister `ボニー`) live in WRAM `$146A` (7 glyphs each).
- **Name entry grids** (modes かな/漢1/漢2, labels `84CCA4..`): row-pointer tables (bank `$84`) `$84E410` (27 rows of
  11 words: 5 + blank + 5; row numbers drawn by code), `$84E698` (39) and `$84EADC` (38) (13 words: reading, blank,
  5 + blank + 5). Row counts are `LDA/CMP/SBC #imm` in both entry routines (`$85B1C8`, copy `$85BDA0`). Phase 7:
  `build.py` GRIDS writes English singles (ABC / abc / Sym, 3-4 rows each) and the counts.
- **Ruin password**: typed in the name entry (object handler `$829600`, state machine `$1814`/`$1284`); `$8296F0`
  compares the 8 words at `$140C` with `$829711` (ライドロイド帝国) and sets `$1816` = `$18` (match) / `$08`. Phase 7:
  `RAIDROID`, compared case-blind (`asm/vwf.asm` `password`; test `tools/lua/password.lua`). Kadam (0147) is only said,
  never typed (no other compare of `$140C`).
- **Staff roll** (found in phase 2, `docs/re/debug.md`; English strings moved to `$B1EC00` by `build.py`, pointers
  in place): `$B1D3E2` (file 18D3E2), 13 pointers (bank `$B1`) to
  strings of glyph words + `$8000|pos` tilemap-position words, `FFFF`-terminated and followed by one more word
  (`$00B4` on every string: frames the page stays up - guess) (18D3FC-18D7D2, verified by the identity repack), drawn by
  `$B1D210` onto BG3. Not part of the six message blocks; includes a special-thanks page not in block `$02`.
  `tests/test_debug.py` decodes page 0.
- **Not extracted yet (leads for phase 5):** weapon-type records near 026F80 (`片手剣(突き)`, `斧`, `弓`; irregular
  stride), debug strings `type000..type6xx` at 027025-027FF0 (7 pointer lists of 32; likely unused), `インゴット`
  names are extracted but may be debug too. Glyph-run scans (both alignments, `>= 4` glyphs, kana-heavy) outside all
  extracted ranges found nothing else that reads as text; enemy names were not found (likely never shown). Text
  built in code (`LDA #glyph / STA` chains) shows up as Japanese that stays in the phase 5 marker build.

## Script files (phase 4)

`tools/extract.py` writes `script/<source>.json` (only missing files). Message format = `Script.text`: glyphs, newline
for `F600`, `{d:XX|word}` dictionary refs, `{end}`/`{wait}`/`{name:04}`/`{goto:00:1103}`..., `{pos:XXXX}` (staff),
`[XXXX]` unknown glyph; `Script.encode` inverts it. `tools/build.py` applies every non-empty `en`
(`extract.apply`): message strings repack in their block (error if a block grows: relocation is phase 5), fixed fields
in place. Tests: `tests/test_extract.py` (roundtrip of every string and field, no overlap, script/ matches the ROM,
en reaches the ROM).

## Tools
- `tools/textdump.py [--expand]`: whole script, one line per message id → `work/re/script_jp.txt`.
- `tools/font_sheet.py`: labelled glyph sheets; `--codes` for a zoomed subset.
- `tools/lua/textreads.lua`: logs each (reading PC, run start) of ROM reads in a CPU range: finds the readers of a
  text table and every string they read (`--var LO=0x848000 --var HI=0x85FFFF`), run beside `scenes.lua` + `warp.lua`.
- `tools/lua/romreads_all.lua`, `readers.lua`, `lzlog.lua`: trace probes used above; `lzcall.lua` (both LZ
  entries with JSL return chain), `wlog.lua` (every byte change in a WRAM range with PC).
