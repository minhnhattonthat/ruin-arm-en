-- Count ROM data reads per reading PC (opcode fetches skipped); log a summary at the end: who reads bulk data.
--   emu.py ... --script tools/lua/readers.lua [--var FROM=0 --var TO=99999]
local from, to = FROM or 0, TO or math.huge
local count, first, last = {}, {}, {}
local function hook(addr, value)
  if L.frame < from or L.frame > to then return end
  local s = emu.getState()
  local pc = (s["cpu.k"] << 16) | s["cpu.pc"]
  if addr >= pc - 4 and addr <= pc + 4 then return end
  if (addr & 0xFFFF) >= 0xFFE0 then return end
  count[pc] = (count[pc] or 0) + 1
  if not first[pc] then first[pc] = addr end
  last[pc] = addr
end
for bank = 0, 0xFF do
  if bank < 0x7E or bank > 0x7F then
    emu.addMemoryCallback(L.safe(hook), emu.callbackType.read, (bank << 16) | 0x8000, (bank << 16) | 0xFFFF,
      emu.cpuType.snes, emu.memType.snesMemory)
  end
end
L.on_frame(function(n)
  if n == (TO or 0) or n % 3000 == 0 then
    for pc, c in pairs(count) do
      if c >= 64 then L.log(string.format("f%d reader pc=%06X n=%d first=%06X last=%06X", n, pc, c, first[pc], last[pc])) end
    end
  end
end)
