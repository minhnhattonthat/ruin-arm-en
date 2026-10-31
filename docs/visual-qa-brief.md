# Visual-QA reviewer brief - Ruin Arm (SNES)

You review contact sheets from a translated build's QA tour and give each one a verdict. Read-only on everything
except your one verdict file: no edits to the repo, no git, no subagents.

## Inputs (in your dispatch)
- A chunk file: one `id<TAB>path` line per sheet. Read every sheet in it; none may be skipped.
- Your verdict file: `work/qa/verdicts/<chunk>.tsv`.
- Optional: the original ROM's sheets (`work/qa/tour_jp/`, same ids) and `glossary.md`.

## How to look
- Read each sheet whole first. Where text is small, zoom into it with
  `python -X utf8 $SKILL/scripts/sheet.py SHEET.png --crop x,y,w,h --zoom 3 --out <scratch>.png` and read that.
- When something looks wrong, open the same id from `tour_jp/` (`sheet.py EN.png --compare JP.png`). If the
  original shows the same thing, it is the game's own behaviour: `ok`, with a note.

## Judge
An `issue` is any of:
- Japanese still visible;
- text overflowing a box, clipped by a frame, or running off screen;
- garbage tiles, wrong or missing glyphs, a strike or stray pixels across letters;
- broken line breaks: a word split mid-line, a page ending mid-sentence, a one-word last line;
- an empty box where text belongs;
- a name that differs from `glossary.md`.

Standing non-bugs, `ok` (the controller adds the game's own below):
- text still typing out, a box mid-fade or mid-scroll, a cursor caught mid-blink;
- a map or scene still loading after a warp;
- anything identical in the original's sheet.
- Tiles carry no labels: `sheet.txt` beside each sheet lists the tile names per sheet in row-major order
  (`m_IIII_PP` = message id IIII, page PP; `map_AARR` = map id). Name tiles that way in an issue.
  For the root `scenes*.png` sheets, `scenes.txt` gives the actual scene names in the same order.
- The message tour (`msgs_XX`) opens every message out of context, always over the starting village with the same
  party: a portrait or speaker that doesn't fit the village, a box that opens and closes with nothing in it, or the
  same page shot twice in a row (a choice or timed page the tour waited out) is the tour, not a bug.
- The hero's default name differs between boots (Fang, Greco, ...); any name in the hero's slot is fine.
- `msgs_02` is the ending's staff credits: its pages are timed, so the tour shoots every 40 frames and catches
  names mid-typing or mid-scroll; `0200` "A YEAR LATER" shows an empty box in the field on both ROMs.
- Msg `1384` (msgs_13) is a block of unused slots that never closes; 30 identical shots, same in the original.
- Speaker headers (`Imperial Guard General Zain`, `Wind General Hude`, ...) sit on one row since round 2; a header
  split over two rows is now an issue.
- Short rows before a mid-sentence pause (`{wait}` / timed pause) are fine where the original pauses in the same
  place; compare with the JP shot before flagging.
- Garbled pink portrait of Freed (msg 12CB): the original shows the same.
- Scenes `game_over` (msg 0187 "... and the others have collapsed.") and `game_over_next` (title menu) end the run.
- Short menu labels Atk/Def/Pad/BWH/Tech are a recorded decision (D18), not abbreviation bugs.
- Lower-case and proportional text is the English font (VWF); the Japanese used full-width 16x16 cells.
- File management (`menu_file`, `menu_file_load`): small numbers 1-6 alongside the tabs, blank file names,
  `HP: 0/0`, the file icons and right-edge `F` on empty slots match the original-ROM shots in `tour_jp`.
- Round 3 credits now use the ending castle map and its script to hide the HUD; HUD-covered text is no longer
  an acceptable limitation for `credits_N`. The background itself remains visible behind the white lettering.
- Choice options start with the original's large full-width digits `1`/`2`/`3`, the cursor left of the digit and
  the selected option yellow: that is the original layout.
- A coloured (yellow) word can sit a few pixels further from the word before it than a normal space: colour
  starts at an 8 px tile edge. An issue only if the text runs off the box.
- The signposts `"To Rute-"` / `"To -ede-m"` (msgs 109A/109B) are worn signs with letters missing, as in the
  original (ルテ・へ).
- A short last line of a sentence is fine when the row above could not give it a word (rows are filled to the
  box width); flag it only when a word sits alone on a row whose row above has room for it, or mid-sentence.

## Verdicts
Write your verdict file once you have read every sheet, one line per id in the chunk:
`id<TAB>ok|issue<TAB>what and where` (for an issue: which tile, which text, what is wrong).
Then return a short summary: counts, and the issues one per line.
