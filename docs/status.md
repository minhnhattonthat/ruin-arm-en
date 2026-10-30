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
  - Round 2 visual QA (249 sheets, 8 reviewers, verdicts `work/qa/verdicts/`) fixed: speaker headers on one row
    (msg10-12, lint `header_codes`), 1149 page held at the JP's pause, spaces after inline pauses (12D3, 10E7),
    110B, 0190, 01AA, 00CF rows.
  - Game over reached (scene `game_over`: `kill = frames` holds both at HP 0 + dead bit -> msg 0187, then title);
    ending credits block `$02` toured (`msgs_02`, timed pages shot every 40 frames). `docs/re/debug.md`.
  - Emulator power-on RAM zeroed (`tools/emu-config/settings.json`, copy into `tools/mesen/`): the default hero
    name came from random RAM, so every re-tour changed every sheet with a name in it.
  - `tools/release.py` + `docs/release-readme.txt` written (phase 9 ready to run once the gate passes).
  - Current session: build SHA-1 `5331160d42478f6ed0f370d291feb7045983a14a` reproduced; smoke and 28 tests pass;
    `jp_reach.py` reports 0 reachable Japanese strings. No production ROM/text changes this session.
  - Fixed QA-tool gaps: stale screenshots/logs can no longer pass a failed run; `first_dialogue` was accidentally
    omitted by the scene-list parser and is now included. Exit-table holes no longer terminate enumeration:
    1872 slots expose 640 mapped rooms, not 187. Direct script pointers now survive `$AC870C` masking bit 15.
  - Ending credits reached on map `$1D02` with the HUD hidden, cold-boot verified (`work/qa/ending_cold/`);
    `credits_0` through `credits_12` now use that setup. Added `ending_credits`, Auto/People/File/load menu routes.
    File-menu tab numbers and empty-slot graphics were compared against the original and are not patch bugs.
  - `tools/gfx_survey.py --raw`: 2008 unreviewed sheets, all 80 raw ROM banks plus 216 decoded known sources,
    with offsets and every skip/error in `work/qa/graphics/index.tsv`; `$AF851C` candidate decoding remains open.
    `$808F95`/`$809097` bitplane interleave documented in `docs/re/compression.md`.
- **Next (phase 8):**
  1. Fresh zero-RAM captures are complete in `work/qa/tour_en/`: all seven message blocks, all 45 named scenes,
     all 640 map entries. Canonical manifest: `work/qa/manifest.tsv` (319 sheets); `qa_gate.py check` exits 1:
     **319 missing current verdicts, 0 changed since init**. Ready review chunks: `work/qa/chunks/chunk_000.txt`
     through `chunk_010.txt`; use read-only visual-qa roles and write unique `work/qa/verdicts/*.tsv` files.
  2. Earlier per-block review requests named `work/qa/round3/chunksXX` and `work/qa/round3/verdicts/`; none arrived.
     If any arrive later, preserve their file timestamps when copying them to the canonical verdict directory.
     Inspect eight map stalls: exits 481, 509, 612, 618, 622, 643, 654, 981 (map ids in the session report).
  3. Finish the graphics survey and ending/epilogue coverage, fix findings, re-tour changed blocks and get a
     passing `qa_gate.py check`. Phase 9 also needs the story-review/polish gate from the skill before release.
  Session evidence and exact remaining work: `docs/phase8-qa-report.md`. No emulator tours remain running.
- **Open (debug tool):** complete ending/epilogue, bosses, story-flag presets. `$ADF158` enters the fortress ending
  but stalls at `$ADF241` for a missing party member; the staff-roll segment is now reached independently.
- **Open (engine/graphics):** hero/sister names one letter a cell in menus; shop compare `Use`/`Hold` label
  half-hidden by the code's icon; short labels left by D18 (Atk/Def/Pad/BWH/Tech).
- **Open RE items:** `$849B38` per-caller pointer tables; weapon-type records ~026F80; control words FE/FA/F5/F4/F3;
  event opcode lengths (`$AC8AD6`); which map holds the ruin terminal (object handler `$829600`, table near `$8B84FD`).
- **Translation notes:** 10A9 says Zieg joins on the branch where he stays behind (JP as written). Minor review
  findings: `docs/polish.md`.
- **Inputs:** cold boot: Start at 1500, 2408 title, 2536 title menu, A -> name prompt; mash A -> first control ~f7700.
- **Open bugs:** none known beyond the phase-8 queue above.
- **Orchestration:** Orca worker depth limit is now 2 (2026-10-30); the earlier `nested_worker_depth_exceeded`
  blocker is gone. Start the visual-qa reviewers yourself as Orca workers; do not escalate for them.
- **Waiting on the user:** nothing blocking. Not verified: GUI keyboard input in `tools/mesen/Mesen.exe` (needs a
  person). Non-blocking: name spellings picked by agents (D12; alternatives in `glossary.md` Avoid column; D19 took
  the game's own ARFF), the D15 password word, and the D18 labels kept short (Atk/Def/Pad/BWH/Tech).
