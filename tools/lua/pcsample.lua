-- Log the CPU PC every EVERY frames from frame FROM on (default 0 / 30): where a hang or crash sits.
--   emu.py ROM --out DIR [scene scripts] --script tools/lua/pcsample.lua --var FROM=9000
local from, every = FROM or 0, EVERY or 30
L.on_frame(function(f)
  if f >= from and f % every == 0 then L.log(string.format("f%d pc=%06X", f, L.pc())) end
end)
