# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 8 (QA in the emulator), in progress. Phase 7 done-when met 2026-10-30.
- **Done (phase 1-7):** recon, debug warp, identity, extract, VWF engine + marker build + width gate, full English
  script (37 batches, reviewed), insert/fit/check, menu slices (D18), staff roll relocation, name entry, password.
  See `docs/re/README.md`, `docs/re/vwf.md` and git history.
- **Done (phase 8 so far, 2026-10-30):**
  - Title katakana removed (G1, D10): `vwf.asm title_logo` at `$AFEF30` (`docs/re/graphics.md`).
  - Debug tool: `warp.py msgs_XX` tours every message of `script/msgXX.json` from one boot (shot per page,
    `$0CA0` = 3 page wait; sheets of 16 + `sheet.txt` tile names); `world_map` scene (mode `$1B`); other game modes
    mapped in `docs/re/debug.md`.
  - Round 1 visual QA (136 sheets, blocks 00/01/10/13, verdicts in `work/qa/round1/`) found and fixed: colour runs
    starting mid-word (`vwf.asm colour`: tile-edge alignment, modelled in `batches.width`), colour lost after a line
    break (`en.carry_col`), choice cursor over the text (`en.CHOICE`: the JP's 16 px blank/blank/digit cells),
    `{fd..}` mis-modelled as a page end (it is an inline pause; 7 messages re-broken, lint now checks stored rows by
    px), 207 one-word last rows rebalanced (`batches.py balance`, also run by `merge`). Details: `docs/re/vwf.md`.
  - D19: home village Aaf -> Arff (the original's world map is lettered ARFF).
  - Worn signposts 109A/109B kept as worn (the JP shows the dots too), now `"To Rute-"` / `"To -ede-m"`.
- **Next (phase 8):**
  1. Rebuild (109A/109B changed after the round-2 tour started), smoke.
  2. Finish the round-2 tour: `msgs_13`, then `warp.py --all --rom build/ruinarm_en.sfc --out work/qa/tour_en`
     (scenes + maps; scenes sheet is `scenes.png`, maps get `sheet*.png`). Round-2 sheets for blocks 00-12 are in
     `work/qa/tour_en/msgs_*` but predate the 109A/B edit: re-run `msgs_10` or recheck those two by hand.
     The round-2 run was stopped by Claude Code for low system memory: run blocks one or two at a time
     (`--jobs 2`), not six emulators at once.
  3. `qa_gate.py init work/qa/manifest.tsv work/qa/tour_en --glob "*sheet*.png"` (add `scenes.png`), `todo
     --size 30 --out-dir work/qa/chunks`, visual-qa agents (4 at a time) with `docs/visual-qa-brief.md`; JP shots
     for comparison: `work/qa/tour_jp/msgs_XX/` (done).
  4. Fix issues, recheck, `qa_gate.py check` exits 0.
- **Open (debug-tool gaps, phase 8 done-when):** ending scene (script near `$ADF2F4`; block `$02` messages draw only
  there) and game over (no game-over text in the script; jumping to `$86ECAE` does nothing; modes `$0A-$12` fade to
  the title): `docs/re/debug.md` §Open leads. Save screen, bosses, story-flag presets not in the scene list.
- **Open (engine/graphics):** hero/sister names one letter a cell in menus; shop compare `Use`/`Hold` label
  half-hidden by the code's icon; short labels left by D18 (Atk/Def/Pad/BWH/Tech).
- **Open RE items:** `$849B38` per-caller pointer tables; weapon-type records ~026F80; control words FE/FA/F5/F4/F3;
  event opcode lengths (`$AC8AD6`); which map holds the ruin terminal (object handler `$829600`, table near `$8B84FD`).
- **Translation notes:** 10A9 says Zieg joins on the branch where he stays behind (JP as written). Minor review
  findings: `docs/polish.md`.
- **Inputs:** cold boot: Start at 1500, 2408 title, 2536 title menu, A -> name prompt; mash A -> first control ~f7700.
- **Open bugs:** none known beyond the phase-8 queue above.
- **Waiting on the user:** nothing blocking. Not verified: GUI keyboard input in `tools/mesen/Mesen.exe` (needs a
  person). Non-blocking: name spellings picked by agents (D12; alternatives in `glossary.md` Avoid column; D19 took
  the game's own ARFF), the D15 password word, and the D18 labels kept short (Atk/Def/Pad/BWH/Tech).
