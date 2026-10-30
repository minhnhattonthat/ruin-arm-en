# Polish pass (deferred Minor review findings)

Phase-6 reviewers' Minor items, to fix in one pass (translator agent, line by line, `tools/batches.py`; never a bulk
rewrite). Critical/Important were fixed before merge. `id - suggestion`.

## Story (msg10-msg13)
- 1003 Bogan cut off: "Right, everyone's he...!?"
- 104B "Go away! Go away!"; 1083 "You look suspicious! Get over here!"; 1064 drop the added "Would you?"
- "you lot" overused (104A, 10A2, 10A3, 10B6): vary; Goldo never says it
- 10B6 "So you're the ones who had the nerve to storm Fefus Castle..."; 10B8 untangle Goldo's boast
- 10C4 かたぶつ "stick-in-the-mud"; 10AA 三人だと neutral "a group this size"; 10C6 "No... way!?"; 10F7 "Haah."
- 10FB Nanny "I won't let you go alone, Princess."
- 1100 "Don't be silly!!"; 1104 "this young man"; 1107 "Never mind that. Let me through!"; 1108 drop stutter
- 110C, 1115 ("So you mean to settle this by force? Fine by me."), 1116 "Fine! Come at me!!", 111E, 1122 "Aaargh,
  unforgivable!", 1134 "Hey, {name}.", 113C "Come ask for it back anytime!", 1149, 114D/114F, 1150 "Alright!", 1165
- 117C 君達 is not -kun: "{name}, you and your friends"; 1173, 1178, 1199, 11AA "Pleased to meet you", 11EB, 11F2
  "Please withdraw, Zain-sama.", 11F6, 11FA "Are you awake?", 11FC "That's right, {name:03} is in danger!"
- 121A "Forget it!"; 1243 "Impossible!!"; 1249 "Don't!!"; 1248 "No!"; 1253; 120D
- 127E "It was Bogan."; 128F singular "that one line"; 1297 "the humans who betrayed me"; 12C1 "Here I come!!"; 12E1
- 12ED, 12F4 "I SHALL KEEP RAISING MY POWER...", 12FA
- 1330 "{name:02}-san, please be careful!"; 1354; 1321 "!!"; 132F; 136D "We don't have time for this!"; 136E; 1351;
  1326 "a woman like you"; 1383 drop stutter

## Towns (msg00, msg01)
- 003C/003D choice "Yeah." (style reference); 0026 "Allot your stars to suit the situation."; 0022 "That girl";
  0032 "Big bro"; 0038 "rumors"; 0039 Rush "as a veteran"; 0040; 0048; 0057; 0014; 0003 drop "I tell you"
- 0075 "We beastfolk live on the land, and the merfolk in the sea."; 007E; 00B1; 00B9; 00C0/00C6-00C8 "function";
  00C6-00C9 "Here, take it back."
- 013A/0156 "you lot"; 0153 "the Earth and Water Generals"; 0146; 0154 "Rest up for now."; 0187 "collapsed"; 018C
  period inside the quote
- 018F "PLEASE ENTER THE PASSWORD."; 0195 drop stutter; 01C0/01D4 "you two" -> "you"; 01C2; 01C8; 01E0; 01AE

## Credits
- 0204/S04 "Story Concept"? (block `$02` and the staff roll agree since b040: Programming, SWITCH-E, Rokusaku
  Kurodaya, Gakugaku Misaki, Maruko Papa).
- Staff name readings are best guesses (Zumoto/Machida, handles, Jun Katsumata, Benben Den, Rokusaku Kurodaya,
  Yasunobu Okubo, Soji Machida): unverified.

## Fields (b016-b031)
- Reconcile the original Latin world-map spellings under D19 against the glossary and every script occurrence;
  all thirteen labels are now visible in `work/qa/worldmap_flags/scene.png`. Include `tools/worldmap.py` and the
  newly found ラウ / RAN. Examples: LONDIUM versus Rondium, WHAIAL versus Wyall, WARSE versus Worth, MEDIOM versus
  Medeom; verify the remaining labels from the original pixels rather than guessing their spelling.
- place_31/32 Manor vs place_09/40 Mansion; place_19 "Ravenna Road"; place_3F "Rutea Passage"; place_37 "Fefus Back Way"
- item_C0 "Everyday Clothes"; item_C7 "Fire God Zenon"?; item_16 Breath vs Bless Ring (verify in game); item_27 "Sleep Sword"
- equip_08 "Light" (b038) -> "Ray"?; use_01 "Don't" -> "Skip"; tactic_01 "Wary" -> "Timid"; status_00 "Best";
  status_06 "Down"
- 84CF65 "Skill" (b038) vs "Feat"; 84D051/84D0C4 発明 Tech vs gadgets; 84D07E "Fights, wins";
  84D117 "Passionate"; 84D17B "Driven"; 84CD98 "Spend your stat points."; Allot/pt vs Stars (★) terminology;
  84CC8D "Bits" and 84967B "Join" unverified (check the screens); 84CEAF/84D686 Gold vs Funds;
  OK vs all right prompts; 84CDB5 "Change which part?" verify; 84D3E3 "Combo Special" vs "Combo Move"
- Fields now fit by px (D18): two-record lines with slack can be reflowed (84E1AD/84E1C6 "Start again from the" /
  "top?", 84E205/84E220, 84D7D1/84D7E8...).
