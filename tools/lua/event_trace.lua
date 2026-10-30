-- Sample event and object-script state for debug-warp investigations.
local mem = emu.memType.snesMemory
L.on_frame(function(n)
  if n % (EVERY or 120) ~= 0 then return end
  local parts = {}
  for i = 0, 5 do
    local p = 0x7E10F7 + i * 16
    local obj = 0x7E0400 + i * 0x50
    parts[#parts + 1] = string.format("%d:%04X/%04X/%04X obj=%04X xy=%04X,%04X", i,
      emu.read16(p, mem), emu.read16(p + 2, mem), emu.read16(p + 4, mem),
      emu.read16(obj, mem), emu.read16(obj + 5, mem), emu.read16(obj + 8, mem))
  end
  L.log(string.format("EVENT f%d mode=%02X map=%04X script=%02X%04X+%04X actors=%s", n,
    emu.read(0x7E0380, mem), emu.read16(0x7E0387, mem), emu.read(0x7E00DD, mem),
    emu.read16(0x7E00DB, mem), emu.read16(0x7E10C2, mem), table.concat(parts, " ")))
end)
