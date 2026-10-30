-- Identify fixed-text callers drawing individual English letters.
local seen = {}
local mem = emu.memType.snesMemory
L.on_exec(0x81E929, 0x81E929, function()
  local s = emu.getState()
  local code = s["cpu.x"]
  if code < 0x0420 or code > 0x047E then return end
  local sp = s["cpu.sp"]
  local caller = emu.read16(sp + 1, mem) | emu.read(sp + 3, mem) << 16
  local ptr = emu.read16(0x10, mem) | emu.read(0x12, mem) << 16
  local key = string.format("%06X/%06X", caller, ptr)
  if seen[key] then return end
  seen[key] = true
  L.log(string.format("NAME caller=%06X src=%06X code=%04X y=%04X dst=%04X", caller, ptr, code,
    s["cpu.y"], emu.read16(0x02, mem)))
end)
