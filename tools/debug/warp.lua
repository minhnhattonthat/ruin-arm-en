-- Reach a scene from tools/debug/scenes.lua from a cold boot (or from --state-in): docs/re/debug.md.
--   run through tools/debug/warp.py, or: emu.py ROM --out D --script tools/debug/scenes.lua --script tools/debug/warp.lua
--     --var "SCENE='menu_items'" --frames 20000 [--var "SAVE=[[C:/abs/work/states/x.mss]]"]
-- Writes <out>/scene.png (and SAVE) when the scene is ready, logs "READY <scene> f<n>", then stops the run.
-- SCENE='maps' tours every map of the exit table in one boot: <out>/map_AARR.png each.
local mem = emu.memType.snesMemory
local function rd(a) return emu.read(a, mem) end
local function rd16(a) return emu.read16(a, mem) end
local function wr(a, v) emu.write(a, v, mem) end
local function wr16(a, v) emu.write16(a, v, mem) end
local function mode() return rd(0x7E0380) end
local FIELD = 0x08

-- Exit table $9AA093-$9ACC72: 1872 slots, including zero-filled holes (not a terminator).
local EXITS = 1872
local function exit_map(i) return rd16(0x9AA093 + i * 6) end
local function exit_for(map)
  for i = 0, EXITS - 1 do
    if exit_map(i) == map and rd16(0x9AA095 + i * 6) ~= 0 then return i end
  end
  error(string.format("no exit leads to map %04X", map))
end
local function all_maps()
  local seen, list = {}, {}
  for i = 0, EXITS - 1 do
    local m = exit_map(i)
    if not seen[m] and rd16(0x9AA095 + i * 6) ~= 0 then seen[m] = true; list[#list + 1] = { map = m, exit = i } end
  end
  return list
end

local name = assert(SCENE, "set --var \"SCENE='name'\"")
local sc = SCENES[name]
if not sc and name:match("^map_%x%x%x%x$") then sc = { map = tonumber(name:sub(5), 16) } end
if not sc and name:match("^exit_%d+$") then sc = { exit = tonumber(name:sub(6)) } end
if not sc and name == "maps" then sc = { tour = true } end
-- msgs_XX: open every message id in MSGS (a list file warp.py writes) and shoot each page: <out>/m_IIII_PP.png
if not sc and name:match("^msgs_") then sc = { tour = true, msgs = assert(MSGS, "MSGS list missing") } end
-- block $02 (ending credits) pages never wait for a key ({wait:10}/{end:10} are timed): shoot every 40 frames instead
if name == "msgs_02" then sc.every = 40 end
assert(sc, "unknown scene " .. name .. " (tools/debug/scenes.lua)")
if sc.map then sc.exit = exit_for(sc.map) end

-- mash A while the game is not in the field (title, name prompt, dialogue); never in the field itself
local mashing = not sc.stop_at
local activated = false
L.on_frame(function(n)
  if mashing and mode() ~= FIELD and n % 20 == 0 and L.route_done() then L.press("a", 6) end
  if sc.advance and mode() >= 0x30 and mode() <= 0x36 and n % 20 == 0 and L.route_done() then L.press("a", 6) end
  if sc.activate and not activated and rd16(0x7E0387) == sc.activate.map then
    local obj = 0x7E0400 + sc.activate.slot * 0x50
    wr16(obj, rd16(obj) & 0x7FFF)
    activated = true
    L.log(string.format("ACTIVATE object %d map %04X", sc.activate.slot, sc.activate.map))
  end
end)

-- event injection: on entry of the per-frame mode dispatcher $86821A (JSL'd, ends PLP/RTL), jump to the
-- "start event A" routine $AC86FE instead; it returns to the dispatcher's caller, so one field frame is skipped.
local pending_ev, direct_script
local pending_credits
L.on_frame(function()
  if pending_credits ~= nil and rd(0x7E03F3) & 0x80 ~= 0 then
    wr(0x7E03F4, pending_credits)
    wr(0x7E03F3, 0x80)
    pending_credits = nil
  end
end)
L.on_exec(0x86821A, 0x86821A, function()
  if not pending_ev or mode() ~= FIELD then return end
  L.log(string.format("INJECT %04X f%d", pending_ev, L.frame))
  if pending_ev >= 0x8000 then direct_script = pending_ev end
  local s = emu.getState()
  s["cpu.k"], s["cpu.pc"], s["cpu.a"] = 0xAC, 0x86FE, pending_ev
  emu.setState(s)
  pending_ev = nil
end)
-- $AC870C clears bit 15 before the resolver. Restore a requested direct pointer at the resolver entry;
-- setting only the bank before $AC86FE accidentally interpreted the pointer as a table event id.
L.on_exec(0xACA6CE, 0xACA6CE, function()
  if not direct_script then return end
  wr(0x7E00DD, 0xAD)
  local s = emu.getState()
  s["cpu.a"] = direct_script
  emu.setState(s)
  direct_script = nil
end)

-- game over: HP 0 plus the dead bit $86ECAE sets ($0414/$0464 bit 15) on hero and sister, held while `kill` frames run
local kill_until = 0
L.on_frame(function(n)
  if n >= kill_until or mode() ~= FIELD then return end
  wr16(0x7E041D, 0); wr16(0x7E046D, 0)
  wr(0x7E0415, rd(0x7E0415) | 0x80); wr(0x7E0465, rd(0x7E0465) | 0x80)
end)

local function finish(shot)
  L.shot(shot or "scene.png")
  L.log(string.format("READY %s f%d map=%04X mode=%02X", name, L.frame, rd16(0x7E0387), mode()))
  if SAVE then L.save_state(SAVE, function() L.finish(0) end) else L.finish(0) end
end

-- step machine
local step, t0, left, tour, ti = "boot", 0, 0, nil, 0
local page, since
local function go(s) step, t0 = s, L.frame end
local function warp(exit) wr16(0x7E038D, exit); wr(0x7E0380, 0x18); go("warping") end

if not STATE_IN then
  for _, p in ipairs({ { "-", 1500 }, { "start", 8 }, { "-", 900 }, { "start", 8 }, { "-", 120 }, { "start", 8 } }) do
    L.press(p[1], p[2])
  end
  for st in (sc.boot or ""):gmatch("[^;]+") do
    local f, b = st:match("^%s*(%d+)%s+(%S+)%s*$")
    L.press(b, tonumber(f))
  end
end

L.on_frame(function(n)
  local m = mode()
  if step == "boot" then
    if sc.stop_at then if n >= sc.stop_at then go("done"); finish() end return end
    if sc.until_mode then if m == sc.until_mode then mashing = false; go("ready") end return end
    if m == FIELD and n > 30 then go("field") end
  elseif step == "field" then
    mashing = false
    for _, w in ipairs(sc.writes or {}) do if w[3] == 2 then wr16(w[1], w[2]) else wr(w[1], w[2]) end end
    if sc.tour then
      -- each map starts from this first-control state, so an entry event left running can't break the next warp
      tour = sc.msgs or all_maps(); go("wait")
      L.save_state(OUT .. "tour_base.mss", function() go("tour") end)
    elseif sc.exit then warp(sc.exit)
    else go("arrived") end
  elseif step == "warping" then
    if m ~= FIELD then mashing = true; go("loading") end
  elseif step == "loading" then
    if m == FIELD and n - t0 > 20 then mashing = false; go(tour and "tourshot" or "arrived")
    elseif n - t0 > 1500 then
      L.log(string.format("STUCK %s exit %d mode=%02X", name, tour and tour[ti].exit or sc.exit, m))
      if tour then go("tourshot") else go("arrived") end
    end
  elseif step == "tour" then
    ti = ti + 1
    if ti > #tour then go("done"); L.log("READY " .. name .. " " .. #tour); L.finish(0) return end
    go("wait")
    L.load_state(OUT .. "tour_base.mss", function() go(sc.msgs and "toopen" or "towarp") end)
  elseif step == "towarp" then
    if n - t0 >= 2 then warp(tour[ti].exit) end
  elseif step == "toopen" then
    if n - t0 >= 2 then wr16(0x7E0CA4, tour[ti]); wr(0x7E0380, 0x30); page, since = 0, nil; go("reading") end
  elseif step == "reading" then
    -- $0CA0 = 3 while a page waits for a key (docs/re/debug.md); shoot once it has held 8 frames, then press A
    local waiting = m >= 0x30 and m <= 0x36 and rd(0x7E0CA0) == 3
    if waiting then since = since or n else since = nil end
    local id = tour[ti]
    if m == FIELD and n - t0 > 20 then
      L.log(string.format("msg %04X pages %d f%d", id, page, n)); go("tour")
    elseif sc.every then
      if n - t0 >= sc.every then
        page = page + 1; L.shot(string.format("m_%04X_%02d.png", id, page))
        if page >= 30 then L.log(string.format("msg %04X stopped at %d pages", id, page)); go("tour") else go("reading") end
      end
    elseif (waiting and n - t0 >= 12 and n - since >= 8) or n - t0 > 400 then
      if not waiting then L.log(string.format("STUCK msg %04X page %d mode=%02X ca0=%d", id, page + 1, m, rd(0x7E0CA0))) end
      page = page + 1
      L.shot(string.format("m_%04X_%02d.png", id, page))
      if page >= 30 then L.log(string.format("msg %04X stopped at %d pages", id, page)); go("tour")
      else L.press("a", 6); go("reading") end
    end
  elseif step == "tourshot" then
    if n - t0 >= 60 then
      L.shot(string.format("map_%04X.png", tour[ti].map))
      L.log(string.format("map %04X exit %d f%d mode=%02X", tour[ti].map, tour[ti].exit, n, m))
      go("tour")
    end
  elseif step == "arrived" then
    if sc.ev then pending_ev = sc.ev end
    if sc.kill then kill_until = n + sc.kill end
    if sc.msg then wr16(0x7E0CA4, sc.msg); wr(0x7E0380, 0x30) end
    if sc.credits then
      if sc.ev then pending_credits = sc.credits
      else wr(0x7E03F4, sc.credits); wr(0x7E03F3, 0x80) end
    end
    if sc.route then
      for st in sc.route:gmatch("[^;]+") do
        local f, b = st:match("^%s*(%d+)%s+(%S+)%s*$")
        L.press(b, tonumber(f))
      end
    end
    go("settle")
  elseif step == "settle" then
    if L.route_done() then go("ready") end
  elseif step == "ready" then
    if n - t0 >= (sc.wait or 90) then go("done"); finish() end
  end
end)
