-- Capture decompressed bytes and their prior WRAM contents, once per source.
-- emu.py ROM --script tools/lua/gfx_capture.lua ...
-- Captures are before the optional bitplane interleave.
local mem = emu.memType.snesMemory
local pending, seen = {}, {}
local function rd(a) return emu.read(a, mem) end
local function word(a) return emu.read16(a, mem) end
local function dump(dst, size)
  local bytes = {}
  for i = 0, size - 1 do bytes[#bytes + 1] = string.char(rd(dst + i)) end
  return table.concat(bytes)
end
local function begin(kind, fixed)
  local src = word(0x95) | rd(0x97) << 16
  if seen[src] then return end
  local dst = fixed or (word(0x98) | rd(0x9A) << 16)
  local size = word(src)
  local label = string.format("lz_%06X", src)
  pending[kind] = { dst = dst, size = size, label = label }
  seen[src] = true
  L.write_file(label .. "_before.bin", dump(dst, size))
  L.log(string.format("GFX %s f%d src=%06X dst=%06X size=%d", kind, L.frame, src, dst, size))
end
local function done(kind)
  local p = pending[kind]
  if not p then return end
  L.write_file(p.label .. ".bin", dump(p.dst, p.size))
  pending[kind] = nil
end
L.on_exec(0x808F01, 0x808F01, function() begin("7f", 0x7F0000) end)
L.on_exec(0x808F92, 0x808F92, function() done("7f") end)
L.on_exec(0x80900E, 0x80900E, function() begin("generic") end)
-- The generic routine returns after its output-count comparison.
L.on_exec(0x809095, 0x809095, function() done("generic") end)
