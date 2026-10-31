# Status

Updated 2026-10-31. History is in git; phase evidence is in `docs/phase8-qa-report.md`.

- **Phase:** 9 (release) complete. Release v1.0 published 2026-10-31.
- **Release v1.0:** `release/1.0/Ruin_Arm_EN_v1.0.zip` (patch + README only), built 2026-10-31 21:57
  Australia/Sydney by `tools/release.py --version 1.0`: build, 34 tests, smoke, 0 reachable Japanese, all six
  QA gates (321 gameplay, 11 ending, 2053 static gfx, 555 map gfx, 5 gfx fixes, 8 story chapters), patch
  re-applied to a clean original and matched. Patched ROM SHA-1 `fa4f014a85e58feecef5ec4336626bb1960d23a0`,
  CRC32 91D3D19B; patch SHA-1 `e22111db5127374c70de846be22b17981f3b4ea9`. Debug tool is Lua only, not in the ROM.
- **Phase 9 done:** story pass (8 chapters ok/fixed), `docs/polish.md` fully ticked, gameplay tour re-captured
  after the story fixes and all 321 sheets re-reviewed (149 in the final round; the 12D2 "has decided." row is a
  forced break, 225 px > 223).
- **Done (phases 1-7):** recon, debug warp, identity, extraction, VWF and marker width gate, full English script
  (37 reviewed batches), insertion/fit checks, menu slices (D18), staff roll, name entry and password.
- **Done this phase:**
  - Reviewed all 319 gameplay sheets (seven message blocks, 45 named scenes, 640 mapped rooms). Fixed findings:
    compact hero/sister menu names, the Supervisors heading, msg 1361/1341 line breaks, and shop routes that
    previously showed Buy instead of Sell/Repair. Changed scenes and msg13 were captured again from cold boot.
  - Reached the complete normal ending through Fin without skipping script waits. The actor at the old
    $ADF241 stall was inactive in the opening-game fixture; `ending_full` activates it on map $2347.
    The full ending was captured again on the final build; all 11 sheets have independent ok verdicts.
  - All 2053 static graphics sheets have independent ok verdicts. Captured decompression through all 640
    original-ROM maps and the ending lead-in: 1317 additional sources, 555 indexed sheets, all reviewed.
    Four flagged sheets exposed Japanese world-map cards and unused city markers; both are translated.
  - New world-map bitmap engine: all thirteen location cards, Travel here?, Yes/No, a wider window preserving
    complete names and service icons. `warp.py world_map_all` captures both choices; Right selects No ($800C=0101).
    Eleven city marker tiles now spell FREE; all other art is unchanged. All five graphics-fix sheets are ok,
    and all four original-source findings have independent fixed verdicts.
    Independent review caught a VRAM-cache collision in the first font upload; the fix reuses the original
    Japanese glyph slots and DMA range. Fresh field, city and complete-ending captures independently verify
    the correction. All five phase-8 gates pass: 2943 sheets, no missing, bad or stale verdicts.
  - Fixed the LZ decoder's signed position, eight-bit zero-fill counter and distance-zero references. All 15
    boot/title captures and 1313 additional streams match exactly. Four source-bank wraps use actual emulator
    output in the survey and are marked explicitly; none are silently treated as verified decoding.
  - Original-ROM comparisons confirmed the eight debug map stalls, shop icon overlap, file-menu icons/numbers
    and several blank/timed messages are original behavior. See `docs/visual-qa-brief.md`.
  - Release script now requires all five visual manifests plus the story-review manifest.
- **Verified build:** `build/ruinarm_en.sfc` = the v1.0 release above.
- **Published 2026-10-31:** repo public; owner created release v1.0
  (https://github.com/minhnhattonthat/ruin-arm-en/releases/tag/v1.0, notes `release/1.0/notes.md`).
- **Next:** player bug reports via GitHub issues.
- **Open bugs:** none identified after the final independent phase-8 reviews.
- **Remaining RE leads (not release blockers by themselves):** story-flag presets for boss events, opcode lengths
  at $AC8AD6, weapon-type records near 026F80, controls FE/FA/F5/F4/F3, ruin-terminal map location.
- **Translation notes:** msg 10A9 follows the Japanese branch wording; `docs/polish.md` holds story questions.
  D19/D22 world-map place names reconciled in phase 9. D20 joins the Supervisors heading.
- **Inputs:** cold boot Start at 1500, 2408 title, 2536 title menu, A to name prompt; first control around f7700.
  `warp.py` defaults to the English build. Tools use the repo's MesenCE with zero-filled power-on RAM.
- **Waiting on the user:** nothing blocking. GUI keyboard input has not been tested by a person. Name choices
  (D12), the password word (D15), and short labels Atk/Def/Pad/BWH/Tech (D18) remain recorded defaults.
