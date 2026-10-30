# Story reviewer brief - Ruin Arm

You read one chapter of a JP->English fan translation straight through, in story order, the way a player
meets it. Per-batch reviewers already judged single lines with +-2 lines of context; your job is what they can't see.
Read-only: no edits, no git, no subagents. Return the report as your final message; the controller saves it.

## Inputs (paths in your dispatch)
- Chapter file `work/qa/story/chapters/<chapter>.txt`: every line of the chapter, `>> id | speaker | JP` then the
  stored English (its line breaks are the game's wrap; `{wait}` = next page, `{fe}` = clear box). Story lines come
  first in id order, then that act's town NPC lines (`*_towns`, `misc`: NPC and system lines in id order). Read ALL
  of it, in passes if large, before judging.
- `docs/synopsis.md` (plot, who is who, late reveals), `docs/style-reference.md` (voice per character),
  `glossary.md` (rulings at the top; place names follow the original world-map labels under D19: Londium, Whaial,
  Mary, Raw, Warse, Marthnal, Lutea, Mediom, Arff).
- Control codes `{...}` are game commands; `{name}` is the hero, `{name:01}` the sister, `{name:02}`-`{name:05}`
  Zieg, Toran, Posena, Neil. Ignore codes except where they change meaning.

## Judge, across the whole chapter
- Continuity: each line follows from the one before; setups, callbacks and references back are kept; who knows what
  stays coherent; nothing gives a later reveal away early (synopsis marks each REVEAL).
- Voice: each character sounds like the same person all chapter and matches their style-reference row: speech quirks,
  register, how they address others. Name the line where a voice drifts or goes neutral.
- Emotion: anger, fear, grief and comedy beats are as strong as the Japanese; a running gag keeps its punchline.
- Things users caught before: a joke losing half its gag; "1st" shown as "1th"; a name off by one letter; awkward
  stock phrases.
- Accuracy only where a line breaks one of the above; single-line accuracy was reviewed already.

## Report
### Issues
#### Critical (continuity break, reveal given away, wrong speaker)
#### Important (voice drift or flattened, emotional beat lost, setup or callback dropped, joke dead)
#### Minor (deferred to the polish pass)
Each: `id - JP gist - problem - suggested EN`.
### Assessment
`ok` (no Critical/Important) | `issue` - one sentence why. The controller writes this word into the chapter's verdict.
