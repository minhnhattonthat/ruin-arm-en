# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 1 (research and recon) done 2026-10-30. Next: phase 2 (debug tool). No build yet.
- **Done (phase 1):** see `docs/re/README.md`.
  - Text: 16-bit glyph words, `tbl/jp.tbl` (0x356 glyphs, one-to-one, kanji read by eye + whole-script reviewer pass),
    20 control words with argument counts, message pointers (block table `$838642`, id = block<<8|index), 144-entry
    dictionary `$838000`, 6 blocks / 1386 lines all decoding and tiling their ranges (`tests/test_recon.py`).
    `tools/textdump.py` → `work/re/script_jp.txt`.
  - Font: 16x16 1bpp at `$9F8000`, fixed 16 px advance, 14 glyphs/line → VWF needed (phase 5).
  - Compression: LZSS `$80900E`, `tools/lz.py` roundtrips a real block.
  - Free space candidates (`docs/re/freespace.md`), 221 KB at `$C1:A000`; header already allows 4 MB.
  - Graphics survey: title katakana `ルインアーム` (OBJ) is the only tile-drawn Japanese on reachable screens.
- **Next:** phase 2: `tools/debug/` warp to any scene from cold boot. Leads: event script interpreter in bank `$AC`
  (reads `$ADAAxx`, message ids as words, e.g. `ADAA11: 32 10` → msg `$1032`); party names WRAM `$146A`; message id
  `$0CA4`. Scene list should cover: pause-menu sub-pages, shops, save screen, each town/dungeon, bosses, ending + credits
  (block `$02`), game over. Then extend `docs/re/graphics.md` with every screen reached.
- **Open RE items (carry into phases 2-5):** menu-record readers/tables (bank `$84`, ~024D00-026400); item/enemy/place
  name tables beyond `$8AB96C`; name-entry grid; meanings of control words FE/FD/FA/F5/F4/F3; other graphics loaders
  (intro path via `$B9DB35`, `$808FA8` MVN unpacker); LZ tables `$80B00F`, `$94DC1A`, `$90E395`; static graphics sweep.
- **Inputs (route notes):** Start at ~1500 skips the intro, title is up ~2100; Start at ~2408 → `開始/続き`, Start →
  name prompt, mash A → first dialogue (~5550) and village gameplay (~14000 from boot). Start in the field opens the
  pause menu; A closes it. Savestates (local, gitignored): `work/states/first_dialogue.mss`, `village_play.mss`.
- **Open bugs:** none.
- **Waiting on the user:** nothing. Not verified: GUI keyboard input in `tools/mesen/Mesen.exe` (needs a person).
