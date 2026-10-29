# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** Step 0 (repo setup) done 2026-10-30. Next: phase 1 (research and recon). No build yet.
- **Done:** template files filled; `rom.sha1` pinned (31f6eac2..., 2,621,440 bytes, headerless); MesenCE 2.2.1 in `tools/mesen/`; smoke boots the original ROM to the title (`work/qa/smoke-orig`), Start skips the intro, Lua probe `tools/lua/hello.lua` logs; pre-commit hook runs `tools/check.py` and rejects a failing test; plugin guard hook blocks `sed -i`; `tools/skill.py`, `tbl.py`, `bps.py`, `romdiff.py` copied; subagent briefs in `docs/*-brief.md`.
- **Next:** phase 1: earlier patches/docs, header (LoROM/HiROM, 20 Mbit), compression, text encoding, pointer tables, control codes, free space, graphics-text survey -> `docs/re/`.
- **Open bugs:** none.
- **Waiting on the user:** nothing. Not verified: GUI keyboard input in `tools/mesen/Mesen.exe` (needs a person; emu.py wrote default key mappings).
