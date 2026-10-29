-- Log every write that changes a byte in WLOG_LO..WLOG_HI (WRAM): frame, pc, address, old -> new.
--   emu.py ... --script tools/lua/wlog.lua --var WLOG_LO=0x7E000B [--var WLOG_HI=0x7E000B] [--var FROM=0 --var TO=9999]
local lo = assert(WLOG_LO, "set --var WLOG_LO=0x7E....")
local hi, from, to = WLOG_HI or lo, FROM or 0, TO or math.huge
local last = {}
local mem = emu.memType.snesMemory
L.on_write(lo, hi, function(addr, value)
  if L.frame < from or L.frame > to then return end
  local a = 0x7E0000 | (addr & 0x1FFFF)
  if (addr & 0xFF0000) < 0x7E0000 then a = 0x7E0000 | (addr & 0xFFFF) end
  local old = last[a]
  if old == nil then old = emu.read(a, mem) end
  if old ~= value then L.log(string.format("f%d pc=%06X %06X %02X->%02X", L.frame, L.pc(), a, old, value)) end
  last[a] = value
end)
