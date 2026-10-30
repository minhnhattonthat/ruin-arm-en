# Phase 8 emulator QA — 2026-10-31

Phase 8 is complete: all five visual gates pass, covering 2943 sheets with current independent verdicts.
Build, tests, smoke and Japanese-reachability checks pass. Phase 9 owns story review, polish and packaging.

## Verified build

- `build/ruinarm_en.sfc`, 4,194,304 bytes, built 2026-10-31 00:25:34 Australia/Sydney.
- SHA-1 `1ae1af8d69579754474a86a38409e5c5e98ee368`.
- `python -X utf8 tools/check.py`: **34 passed**, including insertion ranges, text lint, LZ edge cases,
  native map-font extent/icon preservation, and verification that city graphics change only eleven marker tiles.
- Smoke exit 0: `work/qa/smoke`; `jp_reach.py ... --known script/keep_jp.txt`: **0 reachable Japanese strings**.

## Coverage and independent review

| Manifest under work/qa/ | Sheets | Verdict directory | State |
|---|---:|---|---|
| manifest.tsv | 319 | verdicts/ | All current verdicts ok |
| ending-manifest.tsv | 11 | ending-verdicts/ | All current verdicts ok |
| graphics-manifest.tsv | 2053 | graphics-verdicts/ | All current verdicts ok |
| graphics-maps-manifest.tsv | 555 | graphics-maps-verdicts/ | All current verdicts ok/fixed; four findings resolved |
| graphics-fixes-manifest.tsv | 5 | graphics-fixes-verdicts/ | All current verdicts ok |

The gameplay manifest contains 276 message sheets, 40 map sheets and 3 named-scene sheets. Seven message blocks
cover all extracted dialogue including conditional branches. All 45 normal named scenes have cold-boot captures;
the revised menus, shop routes and credits were toured again after the engine/text fixes. The complete ending
has a separate eleven-sheet sequence, sampled every 300 frames through frame 52500. `ending_full` reaches its
READY checkpoint at frame 52653, map $1C05, after the RUIN ARM / Fin screen.

Reviewers use `.claude/agents/visual-qa.md` and `docs/visual-qa-brief.md`, inspect images and write unique TSV files.
The implementer does not manufacture approvals. Manifests retain hashes and changed-at timestamps; re-captured
sheets require newer independent verdicts.
Final repair verdicts are `ending-verdicts/vram_fixed.tsv`, `graphics-fixes-verdicts/vram_fixed.tsv` and
`graphics-maps-verdicts/vram_fixed.tsv`; msg 1341's final verdict is `verdicts/final_1341.tsv`.
Every gate reports zero missing verdicts, zero unacceptable verdicts and zero changed sheets since init.

## Findings fixed

- **Menu names:** editable ASCII codes previously occupied one 16-pixel cell each. The $849B63 hook now composes
  the eight-code dynamic field proportionally inside its existing cleared 512-byte allocation. Static slice
  fields and name editing keep their original rendering. Cold boots cover name confirmation, status, People
  and shops, including seven-letter Michael. `docs/re/vwf.md` records the hook and WRAM use.
- **Credits:** staff S0C now shows Supervisors on one row, retaining the following position control. D20 records
  the layout refinement. The ending's own map setup hides the HUD, allowing all staff lines to be reviewed.
- **Dialogue:** msg 1361 now reads `This spell is called ...` without the awkward mid-sentence hard break. The
  shorter wording fits the measured 223-pixel budget. The entire msg13 block was toured again. A final review
  caught msg 1341's lone `all.`; `after all.` now stays together. All three affected entry points were cold-boot
  toured, their eleven captures replaced, and the one changed sheet independently approved.
- **Shop coverage:** the route must press B to leave character selection before moving between tabs. Sell and
  Repair now reach their intended tabs; earlier captures had both shown Buy.
- **World-map cards:** pressing A revealed thirteen Japanese location cards and a travel confirmation. An English
  alphabet in the original glyph slots, redirected tile lists and wider window translate the interface without
  abbreviating names. All 26 Yes/No states were cold-boot captured; No is selected with Right and its state
  `$800C=0101` logged. Eight No screenshots catch the arrow's normal blink-off interval; the five visible
  No arrows and all thirteen logged states verify selection. Service icons match the original pixels.
  See `docs/re/worldmap.md`.
- **World-map regression:** independent city and ending reviews caught garbage from an initial font upload to
  VRAM `$9000`, which holds cached normal-map art. The final hook replaces only the original font's decompressed
  glyph slots, preserving the native DMA range and reserved border/icon tiles. Narrow letters are centered in
  their cells. Independent review of fresh field, city, all-card and complete-ending captures confirms the
  repaired implementation, with no remaining corruption or spacing issue.
- **City placeholders:** eleven アキ marker tiles now spell FREE. The compressed stream is relocated through
  its actual graphics-table pointer; all non-marker art is byte-identical. All ten city maps were recaptured.

The original ROM confirms the shop Use/Hold icon overlap and file-menu tab numbers/empty-slot icons. Eight
debug map entries also stall or show uninitialized scenery in the original: 0400, 0300, 0624, 0627, 0628, 0630,
0703, 0B2A (exit slots 481, 509, 612, 618, 622, 643, 654, 981). These are fixture limitations, not newly introduced
patch failures. Out-of-context timed messages and unused msg 1384 likewise repeat in the original; the reviewer
brief explains those artifacts.

## Ending and graphics

The former $ADF241 ending stall was actor slot 1 waiting inactive ($0450 = $8001) in the opening-game fixture.
On map $2347, `ending_full` clears that actor's inactive bit and uses ordinary A presses to advance dialogue.
No script wait is bypassed. The route covers fortress collapse, escape, staff-roll vignettes, forest scene,
THANKS FOR PLAYING, RUIN ARM and Fin. `tools/lua/event_trace.lua` records event/actor state.
Msg 0200 A YEAR LATER is Latin already; direct injection is not a reliable standalone card route. The complete
ending sequence and separate timed block-02 tour provide the ending evidence instead.

The static survey covers all 80 raw ROM banks and known menu, portrait, object and party tables, plus direct
loader sources. Its 2053 sheets include planar, linear and bitplane-interleaved views. The title's Japanese
katakana is removed. The later decompressed-map sweep found the hidden cards and unused markers above; their
original-source sheets remain intact and are adjudicated against the English build evidence. No separate
Japanese chapter or area banner was found. See `docs/re/graphics.md` for the element ledger.

`tools/lua/gfx_capture.lua` records each source's initial destination RAM and decompressed output. It captured
boot/title, the full original-ROM 640-map tour (READY maps 640, frame 223603), and the ending lead-in.
`tools/gfx_capture_survey.py` packs 1317 additional sources into 555 sheets with exact offset/source indexes:
1313 reproduce offline, while $00A800/$00B800/$00D800/$00F400 cross the source index's 16-bit bank boundary.
Those four streams use actual emulator output and their index rows say `runtime-source-bank-wrap`.
Skipped non-ROM pointers, duplicates and verification failures are explicit; the final survey reports 0 failures.

The prior $AF851C failure was a real compressed stream. Correct decoding needs prior WRAM for distance-zero
references, the 65816's eight-bit negative-fill counter, and signed 16-bit source position. All 15 boot/title
captures now match offline decoding. Four regression tests cover these semantics and overlapping references.

## Next phase and reproduction

Phase 9 must finish the chapter story-review gate and every unticked `docs/polish.md` item before packaging,
including D19 reconciliation of newly revealed Latin map labels with earlier name choices in the glossary,
scripts and `tools/worldmap.py`. That language review is separate from this phase's bitmap/rendering fixes.
`tools/release.py` now checks all five visual manifests and the story manifest, then creates and re-applies the
BPS patch and produces a patch-plus-README zip. No release zip was produced in phase 8; nothing was published.
The debug tool remains emulator Lua, absent from the built ROM.

Commands and scenes are in `AGENTS.md` and `docs/re/debug.md`. Images, manifests, runtime dumps and verdicts are
local gitignored evidence under `work/qa/`; source tools and this report are committed.

Skill gotchas for `references/platform-snes.md`: distance-zero LZ copies can read old destination WRAM; emulate
the CPU's signed position and eight-bit counter, not an abstract LZSS decoder. For `references/emulator-qa.md`:
an ending actor can exist but be inactive in a cold-boot fixture, shop tabs may first need to leave character
selection, and an idle Latin world map can hide Japanese A-button cards. VRAM unused by one special screen can
still cache art for later maps; preserve the native allocation or prove its lifecycle. No shared skill files
were modified.
