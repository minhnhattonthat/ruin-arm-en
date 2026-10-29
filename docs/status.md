# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5 (engine spike + marker build) done 2026-10-30. Next: phase 6 (translate). Build = 4 MB ROM with the
  VWF engine; with every `en` empty it differs from the original only in 6 hook sites + checksum (test).
- **Done (phase 1-4):** recon (`docs/re/`), debug warp (`tools/debug/`), identity pack (`tests/test_identity.py`),
  extract (`script/*.json`, 23 files, roundtrip tests). Details in `docs/re/README.md` and git history.
- **Done (phase 5):** engine `asm/vwf.asm` + `tools/asm.py` (asar 1.91 in `tools/asar/`, gitignored), font
  `fonts/vwf.txt` → `tools/font.py`, codec `tools/en.py`, build rewrite (`tools/build.py`): dialogue VWF, English
  font bank FONT2 `$D08000` (singles `$0400+ASCII`, digraphs `$0480+` for fixed fields), every message relocatable
  through MSGTAB `$D28000` (24-bit pointer per id; untranslated ids keep their JP bytes), `{num}` English digits.
  Marker build `tools/marker.py` → `build/ruinarm_marker.sfc`: boots, every reached box shows its id (all 30 scenes
  in `work/qa/marker/`), `tools/jp_reach.py` = 0 reachable Japanese (keep: `848A27` cell palette, data). Width gate
  measured (`docs/re/vwf.md` table): **223 px per dialogue line, 4 rows per page (speaker row counts), fixed fields
  2 letters per cell, names 7 letters, item names 16, staff 2 letters per JP glyph in place**. Torture line (every
  glyph + double spaces) renders. Fixed: a false menu record (`84D676` → real list `84D678`, `fixed.menu_lists`)
  that the marker overwrote and froze the shop's buy screen. D10 (remove title katakana), D11 (VWF dialogue +
  digraph menus) recorded.
- **Next:** phase 6: translator brief limits from the gate table, batch tool (`tools/batches.py`: `work/tl/*.tsv`,
  per-entry limits: messages 223 px/line + 4 rows/page via `font.adv`; fields `2*max` letters, names 7),
  glossary (names: speakers are party-name slots `{name:xx}` filled from WRAM `$146A`, defaults `name_hero`/
  `name_sister`; find where the other NPC names in those slots come from before translating them), then agents.
- **Phase 7 engine items** (`docs/re/vwf.md` §Known gaps): menu VWF (`$849B38` records, `$849B5D` item names) to
  close digraph gaps; names in menus are one letter per cell; code-built red `個` (shop count) and likely `枚`;
  alphabet name-entry grid; title katakana graphics (D10); staff roll relocation if English credits outgrow it;
  lint must hold dialogue lines to 223 px (a longer one loses the crossing glyph and auto-wraps).
- **Debug-tool gaps to close before phase 8** (leads in `docs/re/debug.md` §Open leads): the ending scene (script near
  `$ADF2F4`; the block `$02` messages and the staff roll need its screen setup), game over (damage path `$7EA820,x`
  → `$86EC91`), the save screen (inn script `$ADC2FA`), bosses, story-flag presets (`$7E1C00` bits). Dialogue choices
  (`{choice}`) not seen in a shot yet.
- **Open RE items:** per-caller pointer tables of the `$849B38` lists (to relocate/grow them); weapon-type records
  ~026F80; control words FE/FD/FA/F5/F4/F3; other graphics loaders; event opcode lengths (table `$AC8AD6`).
- **Inputs:** cold boot: Start at 1500 (no skip), 2408 title, 2536 title menu, A → name prompt; mash A → first
  control ~f7700. Pause menu needs ~250 frames after Start. English pages print slower: shop routes wait 300 frames.
- **Tools added:** `tools/lua/wramuse.lua` + `tools/wramfree.py` (free WRAM), `tools/lua/pcsample.lua` (PC every N
  frames: where a hang sits), `tools/lua/regs_at.lua` (registers + `[$10]` at an address).
- **Open bugs:** none.
- **Waiting on the user:** nothing. Not verified: GUI keyboard input in `tools/mesen/Mesen.exe` (needs a person).
