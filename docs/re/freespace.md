# Free space

**Candidates only** (runs of `$FF` >= 1 KB in the original ROM). None is proven free yet: before using one, fill it with a
trap byte, tour the game with the debug tool, and search code for pointers into it (`docs/re/README.md`).

ROM is 2.5 MB (20 Mbit) but the header size byte is `$0C` (4 MB): expanding to 4 MB (file 280000-3FFFFF, banks
`$D0-$FF` / `$50-$7D`) is an option the header already allows; that space is free by construction.

| File | Size | CPU | Note |
|---|---|---|---|
| 20A000-240000 | 221184 | `$C1:A000-$C7:FFFF` | largest; banks `$C1-$C7` (also `$41-$47`) |
| 0B18A3-0C0000 | 59229 | `$96:98A3-$97:FFFF` | |
| 27800C-280000 | 32756 | `$CF:800C-$CF:FFFF` | last bank of the ROM |
| 202E3F-208000 | 20929 | `$C0:AE3F-$C0:FFFF` | |
| 0C5764-0C8000 | 10396 | `$98:D764-$98:FFFF` | right after script blocks `$00/$13` (same bank: 16-bit pointers reach it) |
| 1FE654-200000 | 6572 | `$BF:E654` | |
| 25E6DB-260000 | 6437 | `$CB:E6DB` | |
| 0068B0-007FB0 | 5888 | `$80:E8B0` | bank `$80` code bank: hooks |
| 18EB54-190000 | 5292 | `$B1:EB54` | |
| 05EB6C-060000 | 5268 | `$8B:EB6C` | |
| 01EEA4-020000 | 4444 | `$83:EEA4` | right after script block `$11` (same bank) |
| others | 1-4 KB each | | bank tails `$8A $8C $8E $8F $90 $91 $9A $9B $9E $A0 $A2-$A7 $AF $B2 $B3 $B5 $B9 $BC` (`tools` scan, see git history of this file) |

Text banks hold no spare room beyond the tails above: an English script longer than the Japanese one (2-byte words, but
1 byte per letter once a VWF/8-bit encoding exists) is a phase-5 decision (re-encode or relocate blocks; the block table
is 24-bit, so any bank works).
