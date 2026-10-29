-- Log where each reading PC starts a run of ROM data reads inside LO..HI (CPU addresses): finds the readers of a
-- text table and the start address of every string they read. One line per distinct (pc, start).
--   emu.py ... --script tools/lua/textreads.lua [--var LO=0x848000 --var HI=0x85FFFF]
local lo, hi = LO or 0x848000, HI or 0x85FFFF
local last, seen = {}, {}
local function hook(addr, value)
  local s = emu.getState()
  local pc = (s["cpu.k"] << 16) | s["cpu.pc"]
  if addr >= pc - 4 and addr <= pc + 4 then return end
  local l = last[pc]
  last[pc] = addr
  if l and addr > l and addr <= l + 2 then return end
  local key = pc * 0x1000000 + addr
  if seen[key] then return end
  seen[key] = true
  L.log(string.format("f%d read pc=%06X start=%06X", L.frame, pc, addr))
end
for bank = lo >> 16, hi >> 16 do
  local a, b = math.max(lo, (bank << 16) | 0x8000), math.min(hi, (bank << 16) | 0xFFFF)
  emu.addMemoryCallback(L.safe(hook), emu.callbackType.read, a, b, emu.cpuType.snes, emu.memType.snesMemory)
end
