-- Ruin password check ($8296F0, asm/vwf.asm `password`) on test words: each case writes the name-entry buffer $140C,
-- runs the check in place of one field frame's dispatcher $86821A (as warp.lua does) and logs $1816 (18 = match).
--   emu.py build/ruinarm_en.sfc --state-in work/states/field_start.mss --script tools/lua/password.lua --frames 200
local mem = emu.memType.snesMemory
local CASES = {
  { "RAIDROID", 0x18 }, { "Raidroid", 0x18 }, { "raidroid", 0x18 }, { "RAIDROIX", 0x08 }, { "RAIDRO", 0x08 },
}
local i, waiting, bad = 1, false, 0

local function put_word(s)
  for k = 0, 7 do
    local c = s:byte(k + 1)
    emu.write16(0x7E140C + 2 * k, c and 0x400 + c or 0, mem)
  end
end

L.on_exec(0x86821A, 0x86821A, function()
  if waiting or i > #CASES or emu.read(0x7E0380, mem) ~= 0x08 then return end
  put_word(CASES[i][1])
  emu.write16(0x7E1816, 0, mem)
  local s = emu.getState()
  s["cpu.k"], s["cpu.pc"], s["cpu.ps"] = 0x82, 0x96F0, s["cpu.ps"] & ~0x30
  emu.setState(s)
  waiting = true
end)

L.on_frame(function()
  if not waiting then return end
  local got = emu.read16(0x7E1816, mem)
  local ok = got == CASES[i][2]
  if not ok then bad = bad + 1 end
  L.log(string.format("%s %-8s -> %02X", ok and "ok  " or "FAIL", CASES[i][1], got))
  i, waiting = i + 1, false
  if i > #CASES then
    L.log(bad == 0 and "PASSWORD OK" or "PASSWORD FAIL")
    L.finish(bad == 0 and 0 or 1)
  end
end)
