# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 4 (extract) done 2026-10-30. Next: phase 5 (engine spike + marker build). Build = original bytes
  (sha1 `31f6eac203c7e35fb973729c6b596d937f022829`) with every `en` empty, smoke ok.
- **Done (phase 1):** see `docs/re/README.md`. Text encoding/pointers/dictionary/font/LZ/free space/graphics survey.
- **Done (phase 2):** `tools/debug/warp.py` + `scenes.lua` + `warp.lua` (RAM map and mechanisms: `docs/re/debug.md`).
  From a cold boot, no ROM patch: title, title menu, name prompt, name entry grid, name confirm, first dialogue,
  first control (`field_start`), pause menu + every tab page (items, status, allocation, joy, joy controls, options),
  shop (main, buy, sell, repair), an event (`ev`), a message by id (`msg`), staff roll pages (`credits_N`), any map
  (`map_AARR`, `exit_N`), and the `maps` tour (187 maps, each from a first-control base state). `--all` regenerates
  `work/states/<scene>.mss`. `tests/test_debug.py` pins the exit table, scene list and staff-roll strings.
- **Done (phase 3):** `tools/pack.py` (unpack/pack of dictionary, message blocks `$00 $02 $10 $11 $12 $13`, staff
  roll; shared slots, unused slots → next table, orphans kept) + `tools/build.py` (rom check, wipe each range to FF,
  repack, header checksum) → byte-identical ROM, `tests/test_identity.py`. `tools/bps.py` checksum fixed for the
  2.5 MB size (mirrored tail). No LZ data is repacked (the packer isn't byte-identical; copy untouched blocks).
- **Done (phase 4):** `tools/extract.py` → `script/*.json` (23 files: dict, msg00/01/02/10/11/12/13, staff, menu,
  item, place, name_hero/sister, ingot, equip, tactic, pad, use, act, element, heat, status). Codec
  `Script.text/encode` (`tools/textdump.py`); fixed fields `tools/fixed.py` (menu lists by `$849B38`, found with the
  read probe `tools/lua/textreads.lua` + a structural sweep). Build applies `en` (`extract.apply`). New: block `$01`
  at `$83867E` (193 messages; `$03-$0F` alias it) was missed in phase 1. D9: English written in full, no `{d:}`.
  Tests `tests/test_extract.py` (roundtrip of every string/field, no overlaps, script/ = ROM, en reaches ROM).
- **Next:** phase 5: VWF (fixed 16 px, 14 glyphs/line now, `$81E195`/`$81E929`), font, marker build (`[id]` in every
  string and field; confirm the two glyph-palette menu records and the `ingot`/`status` Latin entries are text),
  width gate per box. Space: English won't fit in place: build stops if a block grows; relocate blocks to free space
  / the 4 MB expansion (`freespace.md`), and fixed fields need relocation or engine work (item names 8 glyphs, menu
  records exact counts; pointer tables beside each list). Name entry grid → alphabet grid. Not extracted yet: weapon
  type records ~026F80, debug `type000..` strings 027025-027FF0 (`docs/re/text.md` §Fixed text).
- **Debug-tool gaps to close before phase 8** (leads in `docs/re/debug.md` §Open leads): the ending scene (script near
  `$ADF2F4`; the block `$02` messages and the staff roll need its screen setup, the overlay alone is half under the
  HUD), game over (damage path `$7EA820,x` → `$86EC91`), the save screen (inn script `$ADC2FA` stalls when injected
  without its NPC), bosses, and story-flag presets (`$7E1C00` bits) for mid-game chapters.
- **Open RE items (carry into phase 5):** per-caller pointer tables of the `$849B38` lists (needed to relocate them);
  weapon-type records; meanings of control words FE/FD/FA/F5/F4/F3; other
  graphics loaders (intro path via `$B9DB35`, `$808FA8`), LZ tables `$80B00F`, `$94DC1A`, `$90E395`, map loader
  `$87CC8E` (`$8C816B` table); static graphics sweep; event opcode lengths (table `$AC8AD6`).
- **Inputs:** cold boot: Start at 1500 (no skip), 2408 title, 2536 title menu, A → name prompt; mash A → first
  control ~f7700. Pause menu needs ~250 frames after Start. Savestates (gitignored) from `warp.py --all`.
- **Open bugs:** none.
- **Waiting on the user:** nothing. Not verified: GUI keyboard input in `tools/mesen/Mesen.exe` (needs a person).
