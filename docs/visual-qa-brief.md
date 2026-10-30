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
- The message tour (`msgs_XX`) opens every message out of context, always over the starting village with the same
  party: a portrait or speaker that doesn't fit the village, a box that opens and closes with nothing in it, or the
  same page shot twice in a row (a choice or timed page the tour waited out) is the tour, not a bug.
- The hero's default name differs between boots (Fang, Greco, ...); any name in the hero's slot is fine.
- Short menu labels Atk/Def/Pad/BWH/Tech are a recorded decision (D18), not abbreviation bugs.
- Lower-case and proportional text is the English font (VWF); the Japanese used full-width 16x16 cells.

## Verdicts
Write your verdict file once you have read every sheet, one line per id in the chunk:
`id<TAB>ok|issue<TAB>what and where` (for an issue: which tile, which text, what is wrong).
Then return a short summary: counts, and the issues one per line.
