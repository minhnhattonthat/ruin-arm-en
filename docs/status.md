# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 7 (insert, fit, check): done-when met 2026-10-30 (lint clean incl. control codes, `romdiff.py` with the
  build's write log clean, writes only in allowed places: `tests/test_build.py`; 0 reachable Japanese; smoke ok).
  Engine remainder done 2026-10-30 except the title katakana (below). **Next: phase 8 (QA in the emulator).**
- **Done (phase 1-6):** recon, debug warp, identity, extract, VWF engine + marker build + width gate, full English
  script (37 batches, reviewed). See `docs/re/README.md`, `docs/re/vwf.md` and git history.
- **Done (phase 7):**
  - `build.put` logs every write (`build/ruinarm_en.writes.txt`); asar and checksum changes are logged as diffs.
  - Name entry: ABC / abc / !?# alphabet grids (`build.py` GRIDS, D16/D18), verified in emulator.
  - Ruin password: `RAIDROID`, case-blind compare hook `$8296F0` (D15), `tools/lua/password.lua` 5/5 cases.
  - Staff roll relocated to `$B1EC00`, full credit names (D17); block `$02` (0200-0209) now matches it (b040).
  - **Menu slices (D18):** fixed fields and the staff roll are set proportionally and cut into 16 px slice codes
    (`font.slices`, `en.Codec`): no digraph gaps, fit by px. English codes `$0400-$0FFF`, font in 4 banks at
    `$FC8000`. Command cells are `|`-joined units. Per-list cell rebalance `fixed.CELLS` (Body, Sister). Full words
    merged (b038/b039): Items, Stats, Allot, Config, Repair, Order, Speed, Height, Weight, Right, Merfolk, element and
    place long forms... Shop's red `個` -> `pc` via `build.PALETTE`. Shots: `work/qa/sheet3.png` (all menus), scene
    `msg_item` (`{item}` insert in dialogue).
- **Phase 8 notes:** credits only show their heading row over the field HUD in the debug view: the ending screen is
  a debug-tool gap (`docs/re/debug.md` §Open leads; also game over, save screen, bosses, story-flag presets).
  Dialogue choices (`{choice}`) not seen in a shot; `{fd:xx}` assumed to end a page. The password entry itself
  (ruin terminal map) was not reached in game: only the compare was run (`password.lua`). Sell/repair/order and
  alchemy screens not re-shot since D18.
- **Open (engine/graphics):** title katakana ルインアーム (D10: remove): source traced to `$808F01` unpack of
  `$AFB1CD` -> `$7F0000` -> VRAM `$5000`, one untraced step between (`docs/re/graphics.md` G1). Hero/sister names
  one letter a cell in menus; shop compare `Use`/`Hold` label half-hidden by the code's icon; short labels left by
  D18 (Atk/Def/Pad/BWH/Tech): a narrow menu font would lift them (`docs/re/vwf.md` §Known gaps).
- **Open RE items:** `$849B38` per-caller pointer tables; weapon-type records ~026F80; control words FE/FD/FA/F5/F4/F3;
  event opcode lengths (`$AC8AD6`); which map holds the ruin terminal (object handler `$829600`, table near `$8B84FD`).
- **Translation notes:** 109A/109B signs have glyphs missing in the JP (written "To Rute." / "To .ede.m"): check if
  intentional. 10A9 says Zieg joins on the branch where he stays behind (JP as written). Minor review findings:
  `docs/polish.md`.
- **Inputs:** cold boot: Start at 1500, 2408 title, 2536 title menu, A -> name prompt; mash A -> first control ~f7700.
- **Open bugs:** none.
- **Waiting on the user:** nothing. Not verified: GUI keyboard input in `tools/mesen/Mesen.exe` (needs a person).
  Non-blocking: name spellings picked by agents (D12; alternatives in `glossary.md` Avoid column), the D15 password
  word, and the D18 labels kept short (Atk/Def/Pad/BWH/Tech) - say if any should change.
