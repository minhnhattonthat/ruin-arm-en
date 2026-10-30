# Debug tool (phase 2)

`tools/debug/warp.py SCENE..` boots the ROM cold in MesenCE and lands on a scene from `tools/debug/scenes.lua`
(`warp.lua` does the work in the emulator). `--all` runs every scene plus the map tour and saves
`work/states/<scene>.mss`; `--list` names them. Shots: `work/qa/warp/<scene>/scene.png`, sheet `work/qa/warp/scenes.png`.
Any map is `map_AARR` (hex id), any exit `exit_N`, and `maps` tours all 640 mapped rooms in one boot (`map_AARR.png` each).
No ROM patch: everything is RAM pokes plus one CPU redirect, so it works on any build.
`--all --sheets-only --out work/qa/tour_en` rebuilds full-size scene contact sheets from existing captures;
`scenes.txt` names every tile. A failed emulator/sheet process or a missing screenshot fails the command.
Fresh runs remove only their generated screenshots/sheets/log first, preventing old evidence from passing a failure.
The default ROM is `build/ruinarm_en.sfc`; pass `--rom` explicitly for original-ROM comparisons.

## RAM and code it relies on (all verified by the scene shots unless marked)

| What | Where | How it was found / used |
|---|---|---|
| Game mode | `$0380` (byte) | `$08` field with control; `$18` start map change (`$19`,`$1A`, `$00-$07` load); `$30-$36` message box; `$38-$3B` event running. Dispatcher `$86821A` (JSL'd every frame, `JMP ($8240,x)`) |
| Current / previous map | `$0387` / `$0389` (u16 = area<<8 \| room) | village `$0000`, forest `$1C05`; `$0388` area picks the tileset (`$87CC8E`) |
| Exit (warp) index | `$038D` (u16) | set by the exit check `$8BCD0A`, read by `$80DA80`: table `$9AA093-$9ACC72`, 1872 slots x 6 bytes {map u16, x, y, flags u16}, 640 distinct maps with positions. Empty slots are holes, not terminators: the old tour stopped at slot 447 and missed 453 maps. **Warp = `$038D`=N, `$0380`=`$18`** in the field |
| Start event | `JSL $AC86FE` with A = event id | high byte 0-7 → word table `$AD8B8A`, 8-15 → `$AD8D8A`, 16 → `$AD8D8E`; event `$1025` points at `$ADF12D` (last-battle dialogue). Script ptr `[$DB]`, offset `$10C2`, sets `$0380`=`$38`. warp.lua redirects the CPU from `$86821A` to `$AC86FE` (that frame's dispatch is skipped). For a direct pointer >= `$8000`, it restores A and bank `$AD` at resolver `$ACA6CE`: `$AC870C` otherwise masks bit 15 and misinterprets the pointer as an event-table id |
| Event opcodes | table `$AC8AD6` (3-byte ptrs, `$00-$7D`) | `00` = message (word id → `$0CA4`, `$0380`=`$30`); `1D addr.w bank val` = write byte (`$ACA769`); `23`/`24`/`25` = set/clear/toggle flag bits. Other lengths unknown |
| Open a message directly | `$0CA4` = id, `$0380` = `$30` | what opcode `00` does; works in the field (`msg_bonnie`) |
| Message page state | `$0CA0` (byte) | `3` = page waits for a key (the ▼), `1` typing, `4` timed/portrait wait, `12`/`13` choices (RAM diff over a message; `msgs_XX` tour waits on `3`, else shoots after 400 frames) |
| Other game modes (poked from the field, `work/qa/modes`) | `$0380` | `$0A`-`$12` fade out and return to the title (mode `$00`); `$13`-`$16` a sky/clouds scene; `$17` another field map; `$1B`-`$28` the world map (scene `world_map`); `$09` (set by `$868C45` when `$041B,x` bit `$2000`) stalls in the field |
| Story flags | `$7E1C00-$1CFF` (bit array, 2048 flags) | in the save image; opcodes `23-25` write it (`$1C0D`, `$1C17` bit 7 toggled during the opening). **Which flag = which story point is still open** |
| Save image | table `$85D220` (5-byte {dst24, len16}) | 19 blocks, `$F8C` bytes: `$146A` party (0x300), `$5800` (0x680), `$5E80` (0x140), `$0110`, `$0387`, `$0400`/`$0B80`/`$04A0` objects, `$DD00` (0x100), `$038D`, `$1020`, `$0540`, `$179A`, `$17D6`, `$1C00` flags (0x100), `$141C`, `$1982`, `$0389`, `$1090`. Load `$85D3F8`. SRAM: 2 slots at `$70:0010`/`$70:1000` (0xFF0 each), checksums `$70:1FF0/2` (`$85D3A6`, XOR of words), title check `$85D2FE` |
| Party records | `$146A + 0x80*n` | +0 name (7 glyphs), +0x10 HP, +0x12 max HP; in the field the live HP is the object copy `$041D` (hero, object `$0400`) / `$046D` (sister, `$0450`), copied at `$8790D4` |
| Staff roll | `$03F3` = `$80`\|step, `$03F4` = page 0-12 | per-frame `$B1D1D9` (from field update `$89A8E0`), draws strings `$B1D3E2` onto BG3 buffer `$7EC800`; pages advance by themselves. The ending script initializes it from `$ADF2F3`. `credits_N` first warps through exit `$5BB` to map `$1D02`, then starts that script (hiding the HUD), then selects N after the script initializes the roll. Cold-boot proof: `work/qa/ending_cold/credits_0`, `credits_12`, `ending_credits` |
| Pause menu | Start, ~250 frames before it takes input | cursor starts at 道具; left wraps to 環境; 道具/能力/振分 pick a character first |
| Second pause-menu row | Down from the first tab row | Auto / People / File. File = Start, wait 300, Down, Right, Right, A. Its six tabs are Save/Lock/Copy/Swap/Delete/Load; Left wraps from Save to Load. `$1280` is the menu family, `$1282` the tab, `$1284` the substate (`$829767`, `$829839`, `$82CD28`). Scenes `menu_auto`, `menu_people`, `menu_file`, `menu_file_load` use ordinary inputs |

## Cold boot

Start at 1500 (logo; does not skip it), 2408 (title), 2536 (title menu `開始/続き`), A (name prompt). warp.lua then
mashes A every 20 frames whenever `$0380` is not `$08`, which takes the default names through the opening to first
control in the village at ~f7700 (`field_start`). Stop-at-frame scenes (title, name screens) are frame counts from
power-on with no mashing; everything else waits on `$0380`. The default hero name is picked from
power-on RAM (ファング, グレコ, ... seen with Mesen's random RAM), so `tools/emu-config/settings.json` sets
`Snes.RamPowerOnState` = `AllZeros` (copy it into `tools/mesen/`): names then repeat between boots. Tour shots still
differ in about 6% of tiles by the blink phase of the page-wait ▼, so re-tour only the blocks that changed.

## Text found while building it (for phase 4)

- **Staff roll `$B1D3E2`** (file 18D3E2): 13 pointers (bank `$B1`) to `$FFFF`-terminated glyph-word strings with
  `$8000|pos` tilemap-position words (+ one word after `FFFF`), 18D3FC-18D7D2. Not in the six message blocks; holds the same staff as block
  `$02` plus a special-thanks page (集英社, 月刊Vジャンプ, 週刊少年ジャンプ staff). Must be extracted and inserted.
- Name entry grid, name confirm and the menu sub-pages (items, status, allocation, joy/controls, options) are all
  font-drawn; shots in `work/qa/warp/`.

## Ending coverage and open leads

- **World-map location cards:** `warp.py world_map_all` opens all thirteen bitmap cards and captures both travel
  choices with ordinary A/Right/B input. The idle `world_map` scene alone misses these boxes. Location flags and
  the new English bitmap engine are documented in `worldmap.md`; `tools/lua/worldmap_tour.lua` drives the tour.

- **Full normal ending reached from cold boot** (phase 8): `ending_full` starts `$ADF158`, activates object slot 1
  when map `$2347` loads, and advances dialogue with ordinary A presses. That slot holds id 1 but starts inactive
  (`$0450 = $8001`) in the opening-game fixture. Clearing bit 15 lets its movement script finish at `$ADF241`;
  no script waits are skipped. The route runs the fortress collapse, escape, staff-roll vignettes, forest scene,
  THANKS FOR PLAYING and RUIN ARM / Fin. Capture with `emu.py` plus `scenes.lua`, `warp.lua`,
  `--var "SCENE='ending_full'" --frames 60000 --shot-every 300 --timeout 600`; evidence: `work/qa/ending_full/`.
  `tools/lua/event_trace.lua` records main and per-actor script state when investigating a stall.
- The shop fixture initially lands in character selection. Sell/Repair routes now cancel that selection with B
  before moving the tab cursor; previously Right changed the character selection and both routes captured Buy.
- `warp.py` now permits output folders outside the repository (previously reporting the result raised
  `Path.relative_to` after a successful capture).

- **Ending staff roll reached**: `ending_credits` warps to map `$1D02` through exit `$5BB` and starts `$ADF2F3` after
  the map-loader wait. `credits_0` through `credits_12` use that setup too, without the village HUD obscuring text.
  Earlier direct-pointer attempts failed because `$AC870C` masks bit 15; the debug hook now restores it at the
  resolver. The former `$ADF241` stall in `work/qa/ending_long` is resolved by `ending_full` above; its actor-1
  fixture was inactive. The complete route also visits exit `$742` → map `$1E02`. Block `$02` is toured separately
  (40-frame timed shots); `0200` "A YEAR LATER" is already Latin in the original. Directly injecting `$ADF723`
  passes that timed message and shows `$1348`; it is not a reliable standalone card route and was not added as one.
- **Game over** (reached, phase 8): both party objects at HP 0 with the dead bit `$86ECAE` sets (`$0414`/`$0464` bit
  15), held for a few frames in the forest, gives msg `$0187` "{name} and the others have fallen.", then A returns to
  the title menu; no game-over graphic. Scenes `game_over`, `game_over_next` (`kill = frames` in `scenes.lua`). HP 0
  on one member alone, or in the village, does nothing.
- **Story flags → chapters**: dump `$1C00` at known story points, or read the event scripts' opcode `23` args.
- Additional boss encounter presets need event ids or story flags. The expanded `maps` tour visits 640 mapped
  rooms; no Japanese chapter/area banner was identified in the graphics survey or those captures. NPC events
  need the right position or an `ev` id. Save/load management now has ordinary-input routes.
