# Translator brief - Ruin Arm (SNES, 1995)

You translate part of the Japanese script of Ruin Arm into English for a fan patch. Ruin Arm is a fantasy action RPG:
a boy and his younger sister (both player-named) leave their village when an empire's black soldiers attack, gather
companions and fight the empire's generals. Tone: earnest adventure with comic banter between the siblings.
Work only on the batches named in your dispatch, one at a time in the order given, each to a passing check before the
next. Do all translation yourself; do not dispatch subagents.

## Read first
1. `docs/style-reference.md` - character voices and approved example pairs. Match this voice.
2. `build/terms_<batch>.txt` - binding glossary rows for this batch (full table in `glossary.md` if you need more).
3. `docs/synopsis.md` - plot, who is who and the late reveals. Don't give a reveal away early.

## Input: `work/tl/<batch>.tsv`
`id<TAB>speaker<TAB>form<TAB>limit<TAB>Japanese`. Lines are in story order; use neighbours for context.
- `\n` in the Japanese is the game's line break, mostly just the Japanese wrap. `{wait}` = next page (wait for a key);
  `{fe}`/`{fe:10}` = clear the box and continue (often before a new speaker).
- Control codes `{...}` are game commands: copy every one exactly, same count (the check compares them). Keep them
  where they act: `{col:01}` + name + `{spd:..}{f4..}{fa..}` open a speaker's box; `{name}` is the hero's name,
  `{name:01}` the sister's, `{name:02}`-`{name:05}` the companions' (glossary); `{item:1B}`/`{item_v}` insert an
  item name, `{num}` a number. `{col:01}`...`{col}` around a word colours it (keep it around the English word).
  `{fd:11}` is a short pause. `{end}`, `{goto:..}`, `{choice:..}` end the message: keep them last.
- Dictionary words are already written out; nothing to do for them.

## Output: `work/tl/<batch>.out.tsv`, written with your file-write tool (not a shell heredoc)
`id<TAB>English`, every input id exactly once, same order. Plain ASCII: straight quotes, `...`, `--`; no tabs inside
the English, no Japanese or fullwidth characters, no `\uXXXX`. Characters the font lacks: `$ < > @ ^ _ ` { } |`.

Line breaks: **the tool wraps your text** (223 px a row, about 38 characters; 4 rows a page). Write each page as
running text and drop the Japanese `\n`s, except:
- keep `\n` right after a speaker header (`{col:01}Name...{fa:C2}\n`): the name has its own row (the check counts
  these);
- keep the layout of choice boxes (`\n\n  1Yes\n  2No{choice:..}`) and of lines that are visibly laid out (credits,
  a centred title like 「アーフ村へ」, `* {name:01} joined the party!`).
A page holds 4 rows, the speaker row included. If your English for a page runs longer, split it with an extra
`{wait}` at a natural point (allowed; other codes must match). Test a line: `python -X utf8 tools/batches.py fit
"<text>"` prints the rows and their px.

Fixed fields (form = menu, item, place, name...): plain text, no codes. The limit is in letters: `16ch` = 8 cells of
2 letters (spaces count); `name` fields are 7 letters max. Credits (`form=credit`): copy the `{pos:..}` codes; each
run between codes holds 2 letters per Japanese glyph (the limit lists each run). Menu text sits in fixed layouts:
use the limit as a hard cap and keep labels short but whole words. Most menu labels are 2 cells = 4 letters
("Item", "Buy", "Sell", "Save"); when no whole word fits, write the best fit and report
`LONG: id - full: <the label you want>` so the engine pass can widen it. Menus `84967B` and `8496A4` are command
palettes: each 2 Japanese glyphs are one command, so write each command in exactly 4 characters (pad with spaces),
same order, total exactly the limit. `〔ｾｰ〕` and similar bracketed runs are one glyph holding small katakana.

## Validate
Run `python -X utf8 tools/batches.py check <batch>` from the repo root and fix every reported id until it prints OK.

## Style
- Faithful: keep the information and order of ideas; adapt idiom, not meaning. Don't add details the Japanese doesn't
  state; don't summarise or skip. Adapt wordplay so the joke still lands (no translator notes).
- Use names and terms exactly as in the glossary. Never abbreviate to fit (D4): rephrase, or add a `{wait}` page. If
  a field can't fit without losing meaning, keep the meaning and report it as `LONG: id`.
- Honorifics kept, hyphenated, Western name order (D1): `ルシアさん` -> `Lucia-san`, `{name}くん` -> `{name}-kun`,
  `〜様` after a name -> `-sama`, `殿` -> `-dono`. Family words are not honorifics: お兄ちゃん = "big brother" (or the
  sister's pet name for him, see style reference), お父さん = "Father"/"Dad" by speaker. 王様 = "Your Majesty"/"the
  King".
- Punctuation: 「」 -> "...", 『』 -> '...', ・・・ / ・・・・・・ -> `...`, ！？ -> `!?`, ！！ -> `!!`, ＊ -> `*`.
- Placeholders: no suffix glued to a variable ("No. {num}", never "{num}th"); no a/an right before `{name..}` or
  `{item..}` (write "the {item:1B}" or rephrase); `{name}`'s possessive is fine (`{name}'s`).
- Speaker names that are plain text (村長, ラッシュ, 兵士) are translated in the header: "Village Chief", "Rush",
  "Soldier".

## Consistency
Never edit `glossary.md`. For a recurring name or term not in it, pick a form, use it consistently, and report it.

## Notes from earlier batches
(none yet)

## Report (reply with only this)
Files written and entry count; then any lines: `NEW TERM: jp -> en`, `UNSURE: id - note`, `LONG: id - note`.
