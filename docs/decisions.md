# Decisions

The user's rulings on scope, style and trade-offs, newest last. Read before asking the user anything; if a later
decision replaces one, mark the old one "replaced by D<n>" instead of deleting it. Binding term spellings live in
`glossary.md`; this file holds the why.

All of D1-D8 came from the owner's standing answers injected into the one-shot run (2026-10-30).

| # | Date | Question | Options offered | Decision and reason |
|---|---|---|---|---|
| D1 | 2026-10-30 | Honorifics and name order | keep (-san), drop; JP or Western order | Keep honorifics; Western order (given name first). Owner's standing answer. |
| D2 | 2026-10-30 | Romanization source for names | official art, earlier patch, Hepburn | Official English names where they exist (e.g. the title logo "RUIN ARM"), else an earlier fan patch, else Hepburn without macrons. |
| D3 | 2026-10-30 | Credits | stay Japanese, translate | English. |
| D4 | 2026-10-30 | Abbreviations | engine work first (default), abbreviate | Default: full names and terms; engine work (wider box, VWF, relocation) before abbreviating; abbreviation only as a flagged last resort. |
| D5 | 2026-10-30 | Graphics text left in Japanese | none (default), list | Translate all of it (titles, menus, banners, cards); keep the original Japanese logo only if it has no official English version. The title already carries an English "RUIN ARM" logo; the small katakana ルインアーム above it is a candidate to remove/keep (decide in phase 5). |
| D6 | 2026-10-30 | Specs and plans | need approval, pre-approved | Pre-approved: keep going through checkpoints, report at the end. |
| D7 | 2026-10-30 | Existing saves / savestates | user's saves, none | None provided; build the debug tool as usual. |
| D8 | 2026-10-30 | Git identity | ask, existing | Already set (minhnhattonthat); do not change it. |
| D9 | 2026-10-30 | Dictionary (`F8xx`) in English text | translate the dictionary and keep `{d:XX}` refs; write English in full | Agent default under D6: English written in full, no `{d:}` refs; the JP dictionary stays JP-only (its entries mix names with grammar endings that have no English equivalent). `jp` shows refs as `{d:XX|word}` so the source reads whole. If space runs short, an English dictionary/DTE is engine work for phase 5/7, applied by the build, not by translators. |
