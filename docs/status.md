# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 6 (translate) done 2026-10-30. Next: phase 7 (insert, fit, check: engine widening + lint/romdiff).
  Every translatable string in `script/*.json` has English (`batches.py` count: 0 untranslated); build
  `build/ruinarm_en.sfc` boots (smoke ok), `tools/jp_reach.py` = 0 reachable Japanese, check green.
- **Done (phase 1-5):** recon, debug warp, identity, extract, VWF engine + marker build + width gate. See
  `docs/re/README.md`, `docs/re/vwf.md` and git history.
- **Done (phase 6):** `tools/batches.py` (split/check/merge/pairs/fit/terms; wraps dialogue at 223 px x 4 rows, `{fd}`
  `{fe}` `{wait}` end a page; lint = `tests/test_batches.py` on every merged string), `glossary.md`, `docs/synopsis.md`,
  `docs/style-reference.md`, D12-D14. New table `name_party` (`$848000` party records, companions' default names).
  37 batches (`work/tl/`, gitignored) translated by 5 translator agents, reviewed by 7 reviewers: 0 Critical; all
  Important fixed before merge; Minors deferred to `docs/polish.md`.
- **Next (phase 7):**
  - **Password entry:** ruin passwords are typed by the player (018F "PLEASE ENTER THE PASSWORD"); English keywords
    are "Kadam" (0147) and "Raidroid Empire" (018C/018D). Find the stored JP keyword(s) and the compare, make them
    English, and give the name entry an alphabet grid (also needed for names). Until then the passwords can't be typed.
  - **Menu widening (LONG fields):** most menu labels are 2 cells = 4 letters (Opts, Stat, Atk, Def, Spd, Rght, Bd, Si,
    Mats, Hgt/Wgt, Us/Ho...). Full forms in the translator report (in `docs/polish.md` §Fields and `batches.LONG`):
    widen records / menu VWF (`docs/re/vwf.md` §Known gaps). `batches.LONG` lists fields whose glossary form doesn't
    fit (place_0E/1B/34, element_00-03 "Earth" for "Earth Element", 84CF94 "Mer" for Merfolk, 84D3E3 "Combo").
  - **Staff roll:** relocate it (`build.py` repacks in place) and restore the full names/headings from msg02 (b014):
    S00-S0C hold initials/surnames only; S05/S06 drop "Shueisha".
  - Credits in msg02 have 5-6 rows per page (JP too): check on the ending screen (debug-tool gap).
  - Dialogue choices (`{choice}`) not seen in a shot; `{fd:xx}` assumed to end a page (JP fits 4 rows only that way;
    otherwise the box scrolls, as in JP).
- **Phase 7 engine items** (unchanged): menu VWF / record widening; code-built red `個`/`枚`; alphabet name-entry
  grid; title katakana (D10); staff roll relocation; lint keeps lines <= 223 px (done: `test_batches.py`).
- **Debug-tool gaps before phase 8** (`docs/re/debug.md` §Open leads): ending scene, game over, save screen, bosses,
  story-flag presets.
- **Open RE items:** `$849B38` per-caller pointer tables; weapon-type records ~026F80; control words FE/FD/FA/F5/F4/F3
  (FD now treated as a page end); event opcode lengths (`$AC8AD6`).
- **Translation notes:** 109A/109B signs have glyphs missing in the JP (written "To Rute." / "To .ede.m"): check if
  intentional. 10A9 says Zieg joins on the branch where he stays behind (JP as written). Staff name readings are
  unverified guesses (`docs/polish.md` §Credits).
- **Inputs:** cold boot: Start at 1500, 2408 title, 2536 title menu, A -> name prompt; mash A -> first control ~f7700.
- **Open bugs:** none.
- **Waiting on the user:** nothing. Not verified: GUI keyboard input in `tools/mesen/Mesen.exe` (needs a person).
  Non-blocking: name spellings picked by agents (D12; alternatives in `glossary.md` Avoid column) - say if any should
  change.
