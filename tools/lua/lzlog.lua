-- Log every call of the LZ decompressor ($80900E, docs/re/compression.md): source and destination, once per source.
--   emu.py ... --script tools/lua/lzlog.lua
local seen = {}
local mem = emu.memType.snesMemory
local function rd(a) return emu.read(a, mem) end
L.on_exec(0x80900E, 0x80900E, function()
  local src = rd(0x97) << 16 | rd(0x96) << 8 | rd(0x95)
  local dst = rd(0x9A) << 16 | rd(0x99) << 8 | rd(0x98)
  if seen[src] then return end
  seen[src] = true
  local s = emu.getState()
  L.log(string.format("lz f%d src=%06X off=%06X dst=%06X caller_sp=%04X", L.frame, src, L.rom_off(src), dst, s["cpu.sp"]))
end)
-- the same format unpacked to $7F:0000 by $808F01 (title logo; docs/re/compression.md); every call: they layer
L.on_exec(0x808F01, 0x808F01, function()
  local src = rd(0x97) << 16 | rd(0x96) << 8 | rd(0x95)
  L.log(string.format("lz7f f%d src=%06X off=%06X dst=7F0000", L.frame, src, L.rom_off(src)))
end)
