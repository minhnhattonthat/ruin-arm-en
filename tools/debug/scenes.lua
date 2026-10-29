-- Scene list for tools/debug/warp.lua (docs/re/debug.md). name -> steps, applied in this order once the field is up:
--   stop_at = N     cold boot only: shoot at frame N and stop (title, intro screens); no mashing
--   boot = "..."    cold boot only: route steps pressed after the standard title presses (before stop_at)
--   until_mode = M  cold boot only: ready the first time game mode $0380 == M (e.g. $33 = message box)
--   writes = {{addr, value[, 2]}..}  WRAM pokes (story flags $7E1C00.., party, items); 2 = 16-bit
--   exit = N        warp through exit N of the table $9AA093 (map id, x, y); map = 0xAARR picks the first exit to it
--   ev = id         start event script id (< $8000: table $AD8B57; >= $8000: pointer in bank $AD)
--   msg = id        open message id (block << 8 | index) directly
--   credits = page  staff-roll overlay page 0-10 ($B1D3E2 strings, $03F4 / $03F3)
--   route = "..."   emu.py route steps pressed after arrival
--   wait = frames   frames between "ready" and the shot (default 90)
-- Every map also has an implicit scene "map_AARR" (hex map id), and "maps" tours them all in one cold boot.
SCENES = {
  title          = { stop_at = 2500 },
  title_menu     = { stop_at = 2800 },
  name_prompt    = { boot = "300 -;8 a", stop_at = 3000 },
  name_entry     = { boot = "300 -;8 a;160 -;8 right;30 -;8 a", stop_at = 3300 },
  name_confirm   = { boot = "300 -;8 a;160 -;8 a", stop_at = 3300 },
  first_dialogue = { until_mode = 0x33, wait = 150 },
  field_start    = {},
  -- pause menu (Start; takes ~250 frames to take input); tabs 道具 能力 振分 ジョイ 環境, cursor at 道具 after a
  -- cold boot, left wraps to 環境. 道具/能力/振分 first pick a character (A), then open that character's page (A).
  menu           = { route = "6 start;300 -" },
  menu_items     = { route = "6 start;300 -;6 a;60 -;6 a;120 -" },
  menu_status    = { route = "6 start;300 -;6 right;30 -;6 a;60 -;6 a;120 -" },
  menu_alloc     = { route = "6 start;300 -;6 right;30 -;6 right;30 -;6 a;60 -;6 a;120 -" },
  menu_joy       = { route = "6 start;300 -;6 left;30 -;6 left;30 -;6 a;120 -" },
  menu_joy_ctrl  = { route = "6 start;300 -;6 left;30 -;6 left;30 -;6 a;60 -;6 a;120 -" },
  menu_config    = { route = "6 start;300 -;6 left;30 -;6 a;120 -" },
  -- shop: event $22 (script $AD9222: msg $0057, opcode $57 shop 8, msg $00CA); shop UI is game mode $10-$12
  -- (300-frame gaps: English pages print slower than the 150 the Japanese needed)
  shop           = { ev = 0x0022, route = "300 -;6 a;300 -;6 a;300 -;6 a;300 -;6 a;300 -" },
  shop_buy       = { ev = 0x0022, route = "300 -;6 a;300 -;6 a;300 -;6 a;300 -;6 a;300 -;6 a;120 -;6 a;120 -" },
  shop_sell      = { ev = 0x0022, route = "300 -;6 a;300 -;6 a;300 -;6 a;300 -;6 a;300 -;6 right;30 -;6 a;120 -;6 a;120 -" },
  shop_repair    = { ev = 0x0022, route = "300 -;6 a;300 -;6 a;300 -;6 a;300 -;6 a;300 -;6 right;30 -;6 right;30 -;6 right;30 -;6 a;120 -;6 a;120 -" },
  -- events and messages
  ev_village_hint = { ev = 0x0010, wait = 150 },
  msg_bonnie     = { msg = 0x1032, wait = 150 },
  -- width gate: the marker build's msg 1032 is the stress message (tools/marker.py GATE); pages 2 and 3
  gate_p2        = { msg = 0x1032, wait = 150, route = "6 a;150 -" },
  gate_p3        = { msg = 0x1032, wait = 150, route = "6 a;150 -;6 a;200 -" },
  -- staff roll overlay ($B1D3E2 strings) drawn over the field: the HUD panels cover part of it; the ending scene's
  -- own screen setup (script near $ADF2F4) is not reached yet. Same for the block $02 ending messages (0x0200
  -- "A YEAR LATER", 0x0201-0209): they open but draw nothing outside that setup (docs/re/debug.md, open leads).
  credits_0      = { credits = 0, wait = 100 },
  credits_1      = { credits = 1, wait = 100 },
  credits_2      = { credits = 2, wait = 100 },
  credits_3      = { credits = 3, wait = 100 },
  credits_4      = { credits = 4, wait = 100 },
  credits_5      = { credits = 5, wait = 100 },
  credits_6      = { credits = 6, wait = 100 },
  credits_7      = { credits = 7, wait = 100 },
  credits_8      = { credits = 8, wait = 100 },
  credits_9      = { credits = 9, wait = 100 },
  credits_10     = { credits = 10, wait = 100 },
  credits_11     = { credits = 11, wait = 100 },
  credits_12     = { credits = 12, wait = 100 },
  -- a few places by map id (the full list is the "maps" tour)
  forest         = { map = 0x1C05 },
}
