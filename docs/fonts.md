# Fonts

Every font or glyph sheet the build reads ends up inside the released patch, so its licence must allow that. One row
per file; a font with no known licence doesn't go into a release.

| File | Source (URL, version) | Licence | Redistributable in a patch | Used for | Changes made |
|---|---|---|---|---|---|
| fonts/vwf.txt | drawn for the Dual Orb fan translation by the same owner (minhnhattonthat), copied 2026-10-30 | MIT (that repo's LICENSE, same owner) | yes | all English text: dialogue VWF singles, menu digraph cells (tools/font.py) | header rewritten; `[ ] # *` added; rows placed at cell rows 2-13, no shadow |
| original font cells `$9F8000` | the game's font | game data, already in the player's ROM | not shipped (kept in place) | Japanese symbols still drawn (○ × ▶ ▼, digits in menus) | none |
