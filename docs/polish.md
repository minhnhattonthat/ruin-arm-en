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
- [x] act2 (p05) - fixed 10F4 1104 110D 1122 10ED: Nanny third person "If this old nanny's words are foolish, Princess, then yours are a hundred times
  worse!"; 1104 このお方 "this gentleman"; 110D Lamia Warrior きさま "Who dares come here!?"; 1122 Deene optional
  haughtier tail; 10ED Gilm old-man flavour "drop by whenever you like"
- [x] act2: 0134 Toran speaking in Fubel - waived: the JP speaker code is `{name:03}` (original data)
- [x] act3 (p05) - fixed 1195 11A9 1354 1155 1174 1374; waived: 1176 has no いやです, choice full stops stay
  (the game's lists are mixed: every msg00 list and 109D keep them): Aysod "Forgive me, all of you..." (to the party, not Reina); 11A9 "{name}, we've lost our only lead
  on {name:01}."; 1354 "I can be of some use, eh?"; choice entries 1354/135F drop the full stops; 1155 "first of
  all, {name:01} might be among the people those guys have caught"; 1174/1176 いやです "No thanks"; 1374 おいおい
  "Hey now"
- [x] act1 (p05) - fixed 104C 102C 104E 10B6 10D2 10EB 1002 106B 10B8; waived: 10A6 the JP says 家 (the lab is
  revealed at 10A7), 10EC ・・・・・・ -> "..." is the house rule: "True! But actually it's the other way round..."; 102C "We believe in all of you."; 104E Neil まて
  differs from Lucia's 1048 ("Stop!! I'll take you on myself!"); 10B6 Goldo blunt "So you're the ones who had the
  nerve to storm Fefus Castle."; 10D2 Zain "?" not "!"; 10EB "Bogan, damn him..."; 10EC keep the long pause;
  10A6 "My laboratory is in the castle town."; 1002 cheekier おそいぞ; 106B Gilm old-man colour; 10B8 "If something
  has to be won in battle, then I win it in battle."
- [x] act1_towns (p05) - fixed all (0022 is the sister; 0054 "Our Captain" = Garzack, cf. 004B):
  0022 あの子 may be the sister, not Lucia (check against 0023/1000); 006B/006E うん "Yeah." like
  003C; 00C5 sister's いやだ "No, thanks."; 0025 Toran hearty "Watch yourselves out there!"; 0023 cheekier Lucia;
  0078/0079 Gilm "Sorry, lad..."; 00A3 Zieg "Rest up now, young'un."; 0054 隊長 = which captain (Garzack?); 00B1
  "It just finished."; 007E "boundlessly near the heavens"
- [x] act5 (p06) - fixed 12DC 12CD 12E1 12C6 12E0 12FD 12EA 12D4; waived 12C0 (optional, reads fine):
  12DC stray break leaves "are" alone on a row; 12CD Zain's welcome clumsy; 12E1 "I was reborn the day you
  betrayed me, when I threw myself from a cliff in despair."; 12C6/12E0 Zieg neutral ("young'un", "Bah"); 12FD
  unify with 12F4 "I SHALL KEEP RAISING MY POWER"; 12EA Neil "Won't know till we try."; 12C0 optional; 12D4 dash
- [x] misc (p06) - fixed all, 01D2 now "(blush)":
  019C Margarita's syllable-split thanks tidier; 01B2 "What's Hude-sama going to do with the women he
  brought here?"; 01CA "they say" twice; 01CE cheekier Lucia "Don't let me down, you two!!"; 01A2 Toran hearty;
  01B4/01BA/01DF old-man じゃ touch; 01C8 "What should I do?"; 01D2 "*blush*" vs "*" narration; 01B9 colour span
  only on "L Button"
- [x] act4 (p06) - fixed 11F6 1253 125C 1273 1207 1210 ("that kid's father") 1281 017C; waived: 016B 女王 is
  "queen" in the JP, 016E has none, 1222 "Fine, do what you want!!" already carries もう知らない:
  11F6 Milia taunting "Allow me to play with you!"; 1253 くだらん "Pathetic."; 125C Neil "Out of my way!!";
  1273 Lucia "Fight him one-on-one! Right, {name}?"; 1222 もう知らない "That's it, I give up!!"; 1210 "{name}'s
  father"; 1207 "the enemy attacked us"; 1281 Zieg voice; 016B/016E 女王 vs Fara "Princess"; 017C notice wording
- [x] ending (Important, p06) - fixed: 1321 "{name:01}---------!!", 131C "{name:02}---!!":
  1321 the hero's only line, drawn-out {name:01}ーーー！！, and 131C {name:02}ー！！ keep the
  stretch
- [x] ending (p06) - fixed 131B 1331 1317 1347 ("Bwaahahahaha!!", JP ぐわあ) 1330 132D; waived: 0203 "Voice Cast"
  matches the staff roll (glossary heading updated to it), 0208 handles match staff.json S0B as written:
  131B/1331 けじめ "make amends / atone in his own way"; 1317 doubled ellipsis; 1347 Zieg's mad laugh
  is not Toran's "Gwaahahaha" ("Fuhahahaha!!" like 1345); 1330 はい "Yes." not "Okay."; 132D スマンのう old-man
  tone; 0203 "Voice Cast" vs glossary heading "Cast"; 0208 ・ separator "SWITCH-E" vs "ST.TYPE M"
- [x] round 2, ending/misc: optional 0208 separator, 019C four-beat thanks, 01DF opener - waived: reviewer marks
  them optional; 0208 matches the staff roll
- [x] round 2, act5: 12DC "That is what my master... has decreed", 12E0 grave "You are only being controlled by that
  machine." - fixed (p07)
- [x] round 2, act1/act1_towns/act4: 10EB "Bogan, damn him" - waived: ボーガンめ is a curse; 102C optional; 00B1
  "just" twice - waived: reads naturally; 00C4/00C5 - waived: round 1 asked for the sister's polite "No, thanks.";
  016B - waived: the JP says 女王; Zieg thin in serious Mediom scenes - waived: reviewer marks it acceptable
- [x] round 3, act5: 12ED/12CB wording, 12E2/12FA Zieg neutral - waived: lines passed rounds 1-2, notes optional;
  12D3 space after {fd} - waived: {fd} is an inline pause, the space separates the words
- [x] act3: 1370 Fara calls Toran her brother; 1165/11A7 "strongest"; 0165 Reina after 119D; 0153/117D geography -
  waived: each is the JP's own content
