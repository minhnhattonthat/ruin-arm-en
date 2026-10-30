# Polish pass (deferred Minor review findings)

Phase-6 reviewers' and phase-9 story reviewers' Minor items, fixed in one pass (translator agent, line by line:
`tools/batches.py redo pNN ids..`, then `check`/`merge`; never a bulk rewrite). Critical/Important were fixed before
merge. Each line is ticked `[x]` as fixed or `waived: reason`; `tools/release.py` refuses to run while any line reads
`- [ ]`. Batches: `work/tl/p01` (story), `p02` (towns, credits), `p03` (D19 place names), `p04` (fields).

## Story (msg10-msg13) - p01
- [x] 1003 Bogan cut off: "Right, everyone's he...!?" - fixed
- [x] 104B "Go away! Go away!"; 1083 "You look suspicious! Get over here!"; 1064 drop the added "Would you?" - fixed
- [x] "you lot" overused (104A, 10A2, 10A3, 10B6): vary; Goldo never says it - fixed (Who the hell are you / It's you!
  / Suspicious characters / It's you, is it)
- [x] 10B6 "So you're the ones who had the nerve to storm Fefus Castle..."; 10B8 untangle Goldo's boast - fixed
- [x] 10C4 "stick-in-the-mud"; 10AA "a group this size"; 10C6 "No... way!?"; 10F7 "Haah." - fixed
- [x] 10FB Nanny "I won't let you go alone, Princess." - fixed
- [x] 1100 "Don't be silly!!"; 1104 "this young man"; 1107 "Never mind that. Let me through!"; 1108 drop stutter - fixed
- [x] 110C, 1115, 1116, 111E, 1122, 1134, 113C, 1149, 114D/114F, 1150, 1165 - fixed as suggested
- [x] 117C 君達 - waived: the 君 is on `{name}` (`{name}君達` = "{name}-kun and co."), so "-kun" stays (D1); the
  English already reads "{name}-kun, you and your friends"
- [x] 1173, 1178, 11AA, 11EB, 11F2 "Please withdraw, Zain-sama.", 11F6, 11FA "Are you awake?", 11FC - fixed
- [x] 1199 - waived: the English matches the JP (Reina has the knife, 119A)
- [x] 121A "Forget it!"; 1243 "Impossible!!"; 1249 "Don't!!"; 1248 "No!"; 1253; 120D - fixed
- [x] 127E "It was Bogan."; 128F "that one line"; 1297 "the humans who betrayed me"; 12C1 "Here I come!!"; 12E1 - fixed
- [x] 12ED, 12F4 "I SHALL KEEP RAISING MY POWER...", 12FA - fixed
- [x] 1330 - waived: already "{name:02}-san, please be careful!"
- [x] 1354; 1321 "!!"; 132F; 136D "We don't have time for this!"; 136E; 1351; 1326 "a woman like you"; 1383 - fixed

## Towns (msg00, msg01) - p02
- [x] 003C/003D choice "Yeah."; 0026 "Allot your stars to suit the situation."; 0022 "That girl"; 0032 "Big bro";
  0038 "rumors"; 0039 "as a veteran"; 0040; 0048; 0057; 0014; 0003 drop "I tell you" - fixed
- [x] 0075; 007E; 00B1; 00B9; 00C0/00C6-00C8 "function"; 00C6-00C9 "Here, take it back." - fixed
- [x] 013A/0156 "you lot"; 0153 "the Earth and Water Generals"; 0146; 0154 "Rest up for now."; 0187 "collapsed";
  018C period inside the quote - fixed
- [x] 018F "PLEASE ENTER THE PASSWORD."; 0195 drop stutter; 01C0/01D4 "you two" -> "you"; 01C2; 01C8; 01E0; 01AE -
  fixed

## Credits
- [x] 0204/S04 "Story Concept"? - waived: 原作 is "Original Story", the credits-heading ruling in glossary.md; block
  `$02` and the staff roll agree
- [x] Staff name readings are best guesses - waived: no published reading exists to check against (D17); the
  readings are recorded in docs/decisions.md D17 as unverified

## Fields (b016-b031)
- [x] D19 world-map spellings - fixed (p03, glossary, `tools/worldmap.py`). The original labels, all thirteen shown by
  `warp.py world_map_labels` on the original ROM: ARFF, LONDIUM, WHAIAL, MARY, RAW, STELM, WARSE, MARTHNAL, RAVENNA,
  LUTEA, TIFNU, MEDIOM, RAIDROID. Renamed everywhere: Rondium -> Londium, Wyall -> Whaial, Maria (village) -> Mary,
  Rau -> Raw, Worth -> Warse, Marsnal -> Marthnal, Rutea -> Lutea, Medeom -> Mediom (the sister default name stays
  Maria). The earlier note's "RAN" was a misreading of RAW.
- [x] place_31/32 Manor vs place_09/40 Mansion - fixed: "Mansion Gate"; place_19 "Ravenna Road" - fixed; place_3F -
  fixed "Lutea Passage"; place_37 - waived: "Fefus Secret Way" is accurate for ぬけ道
- [x] item_C0 - waived: "Plain Clothes" is accurate; item_C7 - waived: "Zenon Fire Armor" keeps both parts;
  item_16 - waived: Breath Ring is right (1149: it lets you breathe in Fubel); item_27 - waived: "Slumber Sword" is fine
- [x] equip_08 - waived: "Light" (32 px) names the 光の矢 shot plainly; "Ray" adds nothing; use_01 - fixed "Don't use"; tactic_01 -
  fixed "Passive" (消極的); status_00 - waived: "Max" reads well in 32 px; status_06 - waived: "KO" is the standard term
- [x] 84CF65 - waived: "Skill" is fine; 84D051 - waived: "Tech" is a D18 last resort; 84D0C4 - fixed "Failed
  inventions"; 84D07E - fixed "Fights, wins"; 84D117 - waived: "Hotblooded" is closer to ねっけつ漢; 84D17B - fixed
  "Competitive"; 84CD98 - waived: "Allot" matches the Allot menu label; Stars stays the ★ term (glossary); 84CC8D
  "Bits" and 84967B "Join" - waived: the phase-8 menu sheets have ok verdicts and no better reading of the JP exists;
  84CEAF/84D686 - waived: Gold (the coin) and Funds (money held) are different JP words; OK vs all right - waived:
  both read naturally where used; 84CDB5 - waived: reads correctly; 84D3E3 - waived: "Combo Special" is the
  glossary term
- [x] Two-record field lines (84E1AD/84E1C6, 84E205/84E220, 84D7D1/84D7E8) - waived: each second record is a
  32-96 px cell; no reflow fits more words there ("the top?" is 44 px against 32)

## Story review (phase 9)
(Minor findings from the chapter story pass are added here.)
