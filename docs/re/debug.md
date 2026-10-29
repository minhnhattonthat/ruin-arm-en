# Debug tool (phase 2)

`tools/debug/warp.py SCENE..` boots the ROM cold in MesenCE and lands on a scene from `tools/debug/scenes.lua`
(`warp.lua` does the work in the emulator). `--all` runs every scene plus the map tour and saves
`work/states/<scene>.mss`; `--list` names them. Shots: `work/qa/warp/<scene>/scene.png`, sheet `work/qa/warp/scenes.png`.
Any map is `map_AARR` (hex id), any exit `exit_N`, and `maps` tours all 187 maps in one boot (`map_AARR.png` each).
No ROM patch: everything is RAM pokes plus one CPU redirect, so it works on any build.

## RAM and code it relies on (all verified by the scene shots unless marked)

| What | Where | How it was found / used |
|---|---|---|
| Game mode | `$0380` (byte) | `$08` field with control; `$18` start map change (`$19`,`$1A`, `$00-$07` load); `$30-$36` message box; `$38-$3B` event running. Dispatcher `$86821A` (JSL'd every frame, `JMP ($8240,x)`) |
| Current / previous map | `$0387` / `$0389` (u16 = area<<8 \| room) | village `$0000`, forest `$1C05`; `$0388` area picks the tileset (`$87CC8E`) |
| Exit (warp) index | `$038D` (u16) | set by the exit check `$8BCD0A`, read by `$80DA80`: table `$9AA093`, 447 entries x 6 bytes {map u16, x, y, flags u16}, 187 distinct maps. **Warp = `$038D`=N, `$0380`=`$18`** in the field |
| Start event | `JSL $AC86FE` with A = event id | ids < `$8000`: high byte 0-7 → word table `$AD8B8A` (256), 8-15 → `$AD8D8A` (2); ids >= `$8000`: script pointer in bank `$AD`. Script ptr `[$DB]`, offset `$10C2`, sets `$0380`=`$38`. warp.lua redirects the CPU from `$86821A` to `$AC86FE` (that frame's dispatch is skipped) |
| Event opcodes | table `$AC8AD6` (3-byte ptrs, `$00-$7D`) | `00` = message (word id → `$0CA4`, `$0380`=`$30`); `1D addr.w bank val` = write byte (`$ACA769`); `23`/`24`/`25` = set/clear/toggle flag bits. Other lengths unknown |
| Open a message directly | `$0CA4` = id, `$0380` = `$30` | what opcode `00` does; works in the field (`msg_bonnie`) |
| Story flags | `$7E1C00-$1CFF` (bit array, 2048 flags) | in the save image; opcodes `23-25` write it (`$1C0D`, `$1C17` bit 7 toggled during the opening). **Which flag = which story point is still open** |
| Save image | table `$85D220` (5-byte {dst24, len16}) | 19 blocks, `$F8C` bytes: `$146A` party (0x300), `$5800` (0x680), `$5E80` (0x140), `$0110`, `$0387`, `$0400`/`$0B80`/`$04A0` objects, `$DD00` (0x100), `$038D`, `$1020`, `$0540`, `$179A`, `$17D6`, `$1C00` flags (0x100), `$141C`, `$1982`, `$0389`, `$1090`. Load `$85D3F8`. SRAM: 2 slots at `$70:0010`/`$70:1000` (0xFF0 each), checksums `$70:1FF0/2` (`$85D3A6`, XOR of words), title check `$85D2FE` |
| Party records | `$146A + 0x80*n` | +0 name (7 glyphs), +0x10 HP, +0x12 max HP; in the field the live HP is the object copy `$041D` (hero, object `$0400`) / `$046D` (sister, `$0450`), copied at `$8790D4` |
| Staff roll | `$03F3` = `$80`\|step, `$03F4` = page 0-10 | per-frame `$B1D1D9` (from field update `$89A8E0`), draws strings `$B1D3E2` onto BG3 buffer `$7EC800`; pages advance by themselves. The ending script writes these at `$ADF2F4`/`$ADFBC6` (opcode `1D`) |
| Pause menu | Start, ~250 frames before it takes input | cursor starts at 道具; left wraps to 環境; 道具/能力/振分 pick a character first |

## Cold boot

Start at 1500 (logo; does not skip it), 2408 (title), 2536 (title menu `開始/続き`), A (name prompt). warp.lua then
mashes A every 20 frames whenever `$0380` is not `$08`, which takes the default names through the opening to first
control in the village at ~f7700 (`field_start`). Stop-at-frame scenes (title, name screens) are frame counts from
power-on with no mashing; everything else waits on `$0380`.

## Text found while building it (for phase 4)

- **Staff roll `$B1D3E2`** (file 18D3E2): 11 pointers (bank `$B1`) to `$FFFF`-terminated glyph-word strings with
  `$8000|pos` tilemap-position words, 18D3FC-18D7xx. Not in the six message blocks; holds the same staff as block
  `$02` plus a special-thanks page (集英社, 月刊Vジャンプ, 週刊少年ジャンプ staff). Must be extracted and inserted.
- Name entry grid, name confirm and the menu sub-pages (items, status, allocation, joy/controls, options) are all
  font-drawn; shots in `work/qa/warp/`.

## Open leads (not reachable yet)

- **Ending scene**: the script around `$ADF2F4` (and a second copy `$ADFBC6`) sets up the screen and runs the staff
  roll; its entry point and the map it runs on are not found. Injecting mid-script pointers did not reproduce it. The
  block `$02` messages need that screen setup (they open an empty box in the field).
- **Game over**: HP 0 alone does nothing; damage goes through `$7EA820,x` (pending flag) / `$A822,x` (amount) into
  `$86EC91` (HP − damage; `<= 0` → `$86ECAE`). Poking those in the village did nothing (no damage processing
  there?). Try on a map with enemies.
- **Story flags → chapters**: dump `$1C00` at known story points, or read the event scripts' opcode `23` args.
- Shops, bosses, save screen: need their event ids or maps (shop text is in block `$13`). The `maps` tour reaches
  every room; NPC events need the right position or an `ev` id.
