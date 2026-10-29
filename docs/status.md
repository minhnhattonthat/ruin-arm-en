# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 7 (insert, fit, check): done-when met 2026-10-30 (lint clean incl. control codes, `romdiff.py` with the
  build's write log clean, writes only in allowed places: `tests/test_build.py`; 0 reachable Japanese; smoke ok).
  **Next: the phase-7 engine remainder below (menu widening first), then phase 8 (QA in the emulator).**
- **Done (phase 1-6):** recon, debug warp, identity, extract, VWF engine + marker build + width gate, full English
  script (37 batches, reviewed). See `docs/re/README.md`, `docs/re/vwf.md` and git history.
- **Done (phase 7):**
  - `build.put` logs every write (`build/ruinarm_en.writes.txt`); asar and checksum changes are logged as diffs.
  - Name entry: ABC / abc / Sym alphabet grids (`build.py` GRIDS, D16), verified in emulator (entry, scroll, wrap).
  - Ruin password: `RAIDROID`, case-blind compare hook `$8296F0` (D15), `tools/lua/password.lua` 5/5 cases; hints
    018C/018D/0190 updated.
  - Staff roll strings relocated to `$B1EC00` (bank `$B1` tail), full credit names (D17); lint lets a run reach the
    screen edge and a `{pos}` change column on its row. `credits_0..12` debug scenes.
- **Next (phase 7 remainder, engine):**
  - **Menu widening (D4):** 103 menu fields are 2 cells = 4 letters (Stat, Opts, Pts, Atk, Def, Spd, Hgt, Wgt, Mats,
    Rght, Bd, Si...; full forms in `docs/polish.md` §Fields, `batches.LONG`). Measured: the font is too wide for
    full words in 32 px even proportionally; needs 3-cell slots (command bars have 48 px per command) and/or a narrow
    menu font with packed cells. Details: `docs/re/vwf.md` §Known gaps.
  - Code-built red `個`/`枚` in the shop; title katakana (D10); credits block `$02` (0200-020A) to match the staff
    roll's full names.
- **Phase 8 notes:** credits only show their heading row over the field HUD in the debug view: the ending screen is
  a debug-tool gap (`docs/re/debug.md` §Open leads; also game over, save screen, bosses, story-flag presets).
  Dialogue choices (`{choice}`) not seen in a shot; `{fd:xx}` assumed to end a page. The password entry itself
  (ruin terminal map) was not reached in game: only the compare was run (`password.lua`).
- **Open RE items:** `$849B38` per-caller pointer tables; weapon-type records ~026F80; control words FE/FD/FA/F5/F4/F3;
  event opcode lengths (`$AC8AD6`); which map holds the ruin terminal (object handler `$829600`, table near `$8B84FD`).
- **Translation notes:** 109A/109B signs have glyphs missing in the JP (written "To Rute." / "To .ede.m"): check if
  intentional. 10A9 says Zieg joins on the branch where he stays behind (JP as written). Minor review findings:
  `docs/polish.md`.
- **Inputs:** cold boot: Start at 1500, 2408 title, 2536 title menu, A -> name prompt; mash A -> first control ~f7700.
- **Open bugs:** none.
- **Waiting on the user:** nothing. Not verified: GUI keyboard input in `tools/mesen/Mesen.exe` (needs a person).
  Non-blocking: name spellings picked by agents (D12; alternatives in `glossary.md` Avoid column) and the D15
  password word - say if any should change.
