# Ruin Arm (SNES) English translation

Skill: translate-retro-game; `python tools/skill.py` prints its folder (`$SKILL` below). Read its SKILL.md before ROM, text or QA work. `"$(python tools/skill.py)"` works in bash and PowerShell; never paste a `plugins/cache/<hash>` path.

## Commands (run from repo root)
- Build:    `python -X utf8 tools/build.py`  -> build/ruinarm_en.sfc (checks the dump against `rom.sha1` first; not written yet)
- Check:    `python -X utf8 tools/check.py`  (tests + lint; the pre-commit hook runs this)
- Smoke:    `python -X utf8 "$(python tools/skill.py)/scripts/emu.py" build/ruinarm_en.sfc --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Warp:     `python -X utf8 tools/debug/warp.py <scene>.. [--rom build/ruinarm_en.sfc] [--save]` (cold boot → `work/qa/warp/<scene>/scene.png`; `--list`, `--all` regenerates every state in `work/states/`, `maps` tours all 187 maps, `map_AARR`/`exit_N` any map; scenes: `tools/debug/scenes.lua`, RAM map: `docs/re/debug.md`; never ask the user to play to a scene)
- Release:  `python -X utf8 tools/release.py` (patch + verify; never publish without the user; not written yet)
- Clean:    `python -X utf8 tools/clean.py` (published projects: lists rebuildable/downloadable files; `--yes` deletes)

## Paths
- Original ROM: `rom/Ruin Arm (Japan).sfc` (gitignored; 2,621,440 bytes, no copier header; SHA-1 in `rom.sha1`, checked by `tools/check_rom.py`).
- Emulator: this repo's own MesenCE in `tools/mesen/` (release 2.2.1, https://github.com/nesdev-org/MesenCE/releases/download/2.2.1/Mesen_2.2.1_Windows.zip; gitignored; settings copy in `tools/emu-config/`). Savestates: `work/states/`.
- Text: `script/` (format TBD in phase 4). Tables: `tbl/`. Glossary: `glossary.md`. RE notes index: `docs/re/README.md`. Fonts and their licences: `docs/fonts.md`.
- Build-time copies of skill code: `tools/tbl.py`, `tools/bps.py`, `tools/romdiff.py` (so a clone builds without the skill).

## Rulings
- Edit source files (.py .lua .asm .tbl .json) only with the file-edit tool; scripts here read and analyse, never `.replace()` and write back.
- Subagents: dispatch the `.claude/agents/` types (translator, reviewer, visual-qa, playtester), never general-purpose: their short tool list cuts each agent's start-up context from ~43k to ~9k tokens.
- The user's decisions, with the options and reasons: `docs/decisions.md`. Read it before asking the user anything; add each new ruling there the same session.
- Player bug reports: GitHub issues (`gh issue list --label bug`). Copy the attached save into `work/states/`, reproduce in the emulator, fix, commit with `Fixes #N`, and update `docs/status.md`.
- `fetch_emu.py` on this machine needs `SSL_CERT_FILE=$(python -c "import certifi;print(certifi.where())")` (system CA store fails).
- Intro: Start at ~frame 1500 skips to the title (title up by ~2100).

## Status
`docs/status.md`: done, next, open bugs. Update it at the end of every session.
