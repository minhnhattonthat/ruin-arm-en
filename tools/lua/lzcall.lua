-- Log every LZ decompressor call ($80900E; $808F01 = same format to $7F0000) in FROM..TO with its source,
-- destination and JSL return chain (stack).
--   emu.py ... --script tools/lua/lzcall.lua [--var FROM=0 --var TO=9999] [--var DEPTH=8]
local from, to, depth = FROM or 0, TO or math.huge, DEPTH or 8
local mem = emu.memType.snesMemory
local function rd(a) return emu.read(a, mem) end
L.on_exec(0x808F01, 0x808F01, function()
  if L.frame < from or L.frame > to then return end
  local src = rd(0x97) << 16 | rd(0x96) << 8 | rd(0x95)
  local sp = emu.getState()["cpu.sp"]
  local st = {}
  for i = 1, depth * 3 do st[#st + 1] = string.format("%02X", rd(sp + i)) end
  L.log(string.format("lz7f f%d src=%06X stack=%s", L.frame, src, table.concat(st, " ")))
end)
L.on_exec(0x80900E, 0x80900E, function()
  if L.frame < from or L.frame > to then return end
  local src = rd(0x97) << 16 | rd(0x96) << 8 | rd(0x95)
  local dst = rd(0x9A) << 16 | rd(0x99) << 8 | rd(0x98)
  local sp = emu.getState()["cpu.sp"]
  local st = {}
  for i = 1, depth * 3 do st[#st + 1] = string.format("%02X", rd(sp + i)) end
  L.log(string.format("lz f%d src=%06X dst=%06X stack=%s", L.frame, src, dst, table.concat(st, " ")))
end)
