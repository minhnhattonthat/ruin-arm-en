-- Log CPU registers (A X Y D DB P S) each time execution reaches AT (CPU address), at most MAX lines (default 40).
--   emu.py ROM --out DIR [scene scripts] --script tools/lua/regs_at.lua --var AT=0x81E9A4
local n, max = 0, MAX or 40
L.on_exec(AT, AT, function()
  if n >= max then return end
  n = n + 1
  local s = emu.getState()
  local r = function(a) return emu.read(a, emu.memType.snesWorkRam) end
  L.log(string.format("f%d %06X A=%04X X=%04X Y=%04X D=%04X DB=%02X P=%02X S=%04X [$10]=%02X%02X%02X",
    s["ppu.frameCount"] or 0, AT, s["cpu.a"], s["cpu.x"], s["cpu.y"], s["cpu.d"], s["cpu.dbr"], s["cpu.ps"],
    s["cpu.sp"], r(0x12), r(0x11), r(0x10)))
end)
