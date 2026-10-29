-- Log every ROM data read (opcode fetches skipped) between frames FROM..TO, collapsing runs per PC.
--   emu.py ... --script tools/lua/romreads_all.lua --var FROM=130 --var TO=170
local from, to = FROM or 0, TO or math.huge
local last = {}
local function hook(addr, value)
  if L.frame < from or L.frame > to then return end
  local s = emu.getState()
  local pc = (s["cpu.k"] << 16) | s["cpu.pc"]
  if addr >= pc - 4 and addr <= pc + 4 then return end  -- opcode/operand fetch
  if (addr & 0xFFFF) >= 0xFFE0 then return end           -- vectors
  L.log(string.format("f%d pc=%06X %06X off=%06X v=%02X X=%04X Y=%04X", L.frame, pc, addr, L.rom_off(addr), value,
    s["cpu.x"], s["cpu.y"]))
end
for bank = 0, 0xFF do
  if bank < 0x7E or bank > 0x7F then
    emu.addMemoryCallback(L.safe(hook), emu.callbackType.read, (bank << 16) | 0x8000, (bank << 16) | 0xFFFF,
      emu.cpuType.snes, emu.memType.snesMemory)
  end
end
