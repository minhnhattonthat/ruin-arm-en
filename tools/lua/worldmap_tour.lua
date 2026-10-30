-- Capture all thirteen world-map location cards and the travel prompt.
-- Load after scenes.lua and before warp.lua; SCENE='world_map_all'.
local mem = emu.memType.snesMemory
local started, first, which = false, 0, 0
L.on_frame(function(n)
  if not started then
    if n > 7800 and emu.read(0x7E0380, mem) == 0x2B then started = true; first = n end
    return
  end
  local phase = n - first
  if phase == 10 then
    emu.write16(0x7E8000, which * 2, mem)
    L.press('a', 6)
  elseif phase == 100 then
    local label = string.format('location_%02d', which)
    L.shot(label .. '.png')
    if DUMP then L.dump_ppu(label); L.dump_ram(label .. '.ram.bin') end
  elseif phase == 120 then L.press('right', 6)
  elseif phase == 164 then
    L.shot(string.format('location_%02d_no.png', which))
    L.log(string.format('WORLD choice %d = %04X', which, emu.read16(0x7E800C, mem)))
  elseif phase == 180 then L.press('b', 6)
  elseif phase == 240 then
    which = which + 1
    if which == 13 then L.log('READY world_map_all 13'); L.finish(0)
    else first = n end
  end
end)
