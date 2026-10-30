Ruin Arm - English translation patch v{version}
===============================================

Unofficial English fan translation of Ruin Arm (Super Famicom, Bandai / Plex, 1995).

Translation status
------------------
  Dialogue and narration ........ English (variable-width font)
  Menus, items, shops, status ... English
  Name entry and password ....... English
  Title screen .................. English (the original's English logo; the small katakana above it removed)
  Ending text and staff credits . English
  Graphics with text ............ none left in Japanese that we know of

Patching
--------
Apply {patch} to your own dump of the Japanese cartridge with any BPS patcher
(Floating IPS / flips, beat, or https://www.marcrobinson.co.uk/rompatcher or RomPatcher.js in a browser).
The patched ROM is 4 MB (the original is 2.5 MB); the patcher handles that.

Base ROM (No-Intro: Ruin Arm (Japan)), headerless:
  Size   {o[size]} bytes
  CRC32  {o[crc]}
  MD5    {o[md5]}
  SHA-1  {o[sha1]}

Patched ROM:
  Size   {p[size]} bytes
  CRC32  {p[crc]}
  SHA-1  {p[sha1]}

A ROM with a 512-byte copier header (2,621,952 bytes) must have the header removed first.

Playing
-------
Tested in Mesen (MesenCE 2.2.1). Start the patched game from a cold boot: savestates made with the Japanese
game or an older patch carry the old text and will show garbage. Start a new game rather than loading a
save made with the Japanese game.

Known issues
------------
- The shop's Use/Hold comparison label is partly covered by the item icon, as in the Japanese game.
- A few menu labels are abbreviated to fit the original cells (Atk, Def, Pad, BWH, Tech).
- Place names follow the game's own Latin world-map labels (Arff, Londium, Whaial, Mary, Raw, Warse,
  Marthnal, Lutea, Mediom), not a fresh romanisation.
Report anything else at https://github.com/minhnhattonthat/ruin-arm-en/issues
(a savestate or screenshot helps most).

Credits
-------
Translation, hacking and tools: minhnhattonthat, with extensive AI assistance (Claude by Anthropic).
Corrections are very welcome. Fonts and their licences: docs/fonts.md in the repository.

This is an unofficial fan work, not affiliated with the original developers or publishers.
Ruin Arm is (c) Plex / Bandai 1995. Do not distribute pre-patched ROMs.
