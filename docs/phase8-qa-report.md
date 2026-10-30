# Phase 8 QA coverage checkpoint — 2026-10-30

Phase 8 remains incomplete. The worker could generate evidence and fix the debug harness, but Orca rejected its
required independent visual-QA helper with `nested_worker_depth_exceeded` (max 1, no effects applied).
The coordinator was sent the ready review chunks and question `msg_44cbabbabd42`; two ten-minute waits expired
without an answer. Do not substitute the implementer's inspections for independent verdicts.

## Verified build

- `build/ruinarm_en.sfc`, 4,194,304 bytes, built 2026-10-30 21:23:11 Australia/Sydney.
- SHA-1: `5331160d42478f6ed0f370d291feb7045983a14a`.
- `python -X utf8 tools/check.py`: 28 passed.
- Smoke: exit 0, final frame has content (`work/qa/smoke`).
- `jp_reach.py build/ruinarm_en.sfc --known script/keep_jp.txt`: 0 reachable Japanese strings.
- No production ROM, assembly, font or translation edits were made in this session.

## Harness corrections

- The exit table has 1872 slots and 640 distinct positioned maps. Slot 447 is an empty hole, not a terminator.
  The prior 187-map tour omitted 453 mapped rooms, including ending rooms. Regression checks now cover the
  holes, ending exits `$5BB`/`$742` and the following pointer-table boundary.
- Direct script injection now restores bit 15 at `$ACA6CE`; `$AC870C` previously converted a direct pointer into
  an event-table id. The ending staff roll is reachable on map `$1D02`, with the HUD hidden by its own script.
- All 13 `credits_N` routes now use the ending setup. `ending_credits` also runs the actual roll segment.
- Added ordinary-input routes for Auto, People, File and Load on the pause menu's second tab row. File menu
  numbers/empty-slot graphics match cold boots of the original ROM.
- `first_dialogue` was on another scene's declaration line and was omitted by the parser; it is now enumerated.
- A failed emulator run cannot reuse old screenshots or a stale READY log. Sheet failures propagate, unsafe
  scene paths are rejected, and `--all --sheets-only` creates named, full-size scene sheets without re-emulating.
  Both a successful 45-scene regeneration and a missing-capture failure (exit 1) were checked.

## Review artifacts

- Fresh message captures: `work/qa/tour_en/msgs_00`, `msgs_01`, `msgs_02`, `msgs_10`, `msgs_11`, `msgs_12`, `msgs_13`.
  All seven tours exited 0 with READY; 276 contact sheets. Completed message logs were checked against PNG page
  numbers and contain no stale pages from earlier tours. STUCK lines also occur in the original's timed messages;
  reviewers must use `docs/visual-qa-brief.md` and compare suspicious pages against `tour_jp`.
- All 45 named scenes have cold-boot screenshots, including the six newly enumerated/added scenes. Root
  `scenes.png`, `scenes_2.png`, `scenes_3.png` cover them at full size; `scenes.txt` identifies each tile.
- Expanded map tour: exit 0, `READY maps 640`, 640 PNGs / 40 contact sheets. Eight entries stalled before capture:
  exit 481 → map `0400`, 509 → `0300`, 612 → `0624`, 618 → `0627`, 622 → `0628`, 643 → `0630`, 654 → `0703`,
  981 → `0B2A`. These captures need inspection and potentially better story-flag presets. All tour processes ended.
- Block-specific chunks already sent to the coordinator: `work/qa/round3/chunks00`, `chunks01`, `chunks02`,
  `chunks10`, `chunks11`, `chunks12`, `chunks13`. Each chunk needs a read-only visual-qa agent. Existing instructions
  named unique outputs under `work/qa/round3/verdicts`; no such verdicts have arrived.
- The canonical release gate uses `work/qa/manifest.tsv` and `work/qa/verdicts`. Keep any received round3 verdict
  files' original timestamps when copying them into that canonical verdict directory; do not rewrite their dates
  or approve entries on the reviewer's behalf.
- Final canonical manifest: **319 sheets** (276 messages + 40 maps + 3 scenes). Fresh full review queue:
  `work/qa/chunks/chunk_000.txt` through `chunk_010.txt`, with unique outputs under `work/qa/verdicts/`.
  `qa_gate.py check work/qa/manifest.tsv work/qa/verdicts` exits **1**: 319 without a current verdict,
  0 not-ok verdicts, 0 images changed since init. Zero not-ok verdicts means no review has arrived, not QA approval.

## Graphics survey

`python -X utf8 tools/gfx_survey.py --raw` generates 2008 sheets under `work/qa/graphics`, plus an indexed audit of
all 80 raw ROM banks and 217 distinct compressed-source candidates (216 decoded, one failed). It renders planar
and linear formats and the game's bitplane interleave, and lists every empty slot, duplicate and skipped byte
range. The title block's converted render was inspected and contains the recognizable original logo.

These sheets are **unreviewed**, and this is not a complete compressed-source enumeration. The `$AF851C` candidate
fails with an out-of-range LZ back-reference; its raw bytes resemble palette data. That source and remaining
compressed loaders still need tracing. Known source-table bounds and the interleave are documented in
`docs/re/compression.md`; the index is `work/qa/graphics/index.tsv`.

## Remaining phase work

1. Coordinator-side independent visual review, findings fixed and re-captured, then a passing QA gate.
2. Review/classify the graphics sheets and finish the remaining compressed-loader survey.
3. Finish complete ending/epilogue and boss/chapter/area-banner coverage. `$ADF158` reaches the fortress ending
   but waits at `$ADF241` for a missing party member. The staff roll is covered independently; `0200` still needs
   a visible epilogue shot. Expanded-map capture stalls must also be inspected rather than assumed successful.
4. Before phase 9, complete the skill's story-review/polish requirements. No release zip was produced or published.

Skill gotchas for `references/emulator-qa.md`: zero-filled exit-table holes can hide most of a game from a tour;
validate table bounds against later event references, not the first empty record. An injected event starter may
mask a pointer's high bit before resolving it, so confirm the resolved script address in RAM.

No files in the shared translation skill were changed.
