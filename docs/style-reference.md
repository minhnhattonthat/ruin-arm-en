# Style reference - Ruin Arm

Voices and approved example pairs. Plot and who is who: `docs/synopsis.md`. Terms: `glossary.md`.

## Voices
| Character | Japanese register | English voice |
|---|---|---|
| Hero `{name}` | silent; choice answers only (うん / いやだ) | plain boy: "Yeah." / "No way." |
| Sister `{name:01}` | お兄ちゃん, feminine わ/ね; bossy with her brother, polite to adults | lively, bossy little sister: "Honestly, big brother!"; polite "Mr./Ms." tone to adults through -san |
| Lucia | bratty, teasing, きゃははっ | cheeky sprite: "Kyahaha!", teasing, short sentences |
| Bogan | firm, warm father; おまえ達 | dad voice: direct, kind, a little gruff ("you two") |
| Zieg `{name:02}` | old man ワシ, じゃ, のじゃ, おぬし | eccentric old inventor: "Bah!", "young'un", "I'll have you know"; light, never Ye-Olde |
| Toran `{name:03}` | rough, hearty, ガッハッハ, だぜ | big laughing bruiser: "Gwahahaha!", "Don't sweat it!" |
| Posena `{name:04}` | princess: commanding なさい to foes, warm わ/ね to the hero | regal with enemies ("Stand aside!"), warm and teasing with the hero |
| Neil `{name:05}` | harsh 俺, きさま, てめぇ | curt, cold soldier: "You.", "Out of my way." |
| Zain | cold, arrogant 私, きさま, おろかな | icy villain: "Fools.", measured contempt |
| Bolboza | 我; katakana machine lines | machine lines in capitals: "EXTERMINATE HUMANITY." |
| Generals | Goldo honourable 俺; Deene haughty オーホッホッ; Hude sneering polite keigo + manic laughs; Freed poetic, stoic | Goldo blunt warrior; Deene "Ohohoho!"; Hude oily politeness then "Hyahahaha!"; Freed solemn |
| Milia | taunting あーはっはっ, わよ | mocking: "Ahahaha!" |
| Old men (Caesar, Gilm) | ワシ, じゃ, がはは | like Zieg, lighter |
| Knights (Garzack), Hanutu | formal 貴殿, 殿, もうす | formal: "Sir {name}"-style respect is kept as -dono per D1: "{name}-dono" |
| Villagers, soldiers | casual / gruff | everyday English, contractions |

## Example pairs (pilot, b001; the house style for every batch)
| id | Japanese | English |
|---|---|---|
| 1000 | {col:01}ボーガン{spd:01}{f4}{f4:64}{fa:81}\n{name}、\nそろそろ晩メシにするから{wait}{name:01}を呼んで\nきてくれ。{fd}{fe:10}{goto:00:1001} | {col:01}Bogan{spd:01}{f4}{f4:64}{fa:81}\n{name}, dinner's almost ready.{wait}Go and fetch {name:01} for me, would you?{fd}{fe:10}{goto:00:1001} |
| 1001 | {fe:10}{col:01}ルシア{f4:A2}{fa:A2}\nあっ、{name}。\n私もいっしょにいくよ！{fe}＊ルシアが仲間になった！{end} | {fe:10}{col:01}Lucia{f4:A2}{fa:A2}\nOh, {name}! I'm coming with you!{fe}* Lucia joined the party!{end} |
| 1004 | ...\nよお、ボーガン！{wait}久しぶりだなぁ、元気に\nしてたか？{wait}どうした？\n変なかおして・・・ | ...\nYo, Bogan!{wait}Long time no see! You been keeping well?{wait}What's with the funny face...? |
| 1006 | ...\nお・・・{fd:11}その声は・・・{wait}おお、{name:03}か！\nどうした、その頭は？ | ...\nHm...? {fd:11}That voice...{wait}Why, it's {name:03}! What happened to your head? |
| 1007 | ...\nガッハッハッハッハッ！\nまあ、いろいろあってな！{wait}こまかい事は気にするなよ！ | ...\nGwahahahaha! Oh, this and that!{wait}Don't sweat the small stuff! |
| 1014 | ...\nお父さんの言ってた剣って\nこれの事ね・・・{wait}でも精霊がよわまってるから\nこのままじゃ使えないね。 | ...\nSo this is the sword Dad told us about...{wait}But its spirit has grown weak. We can't use it like this. |
| 1015 | ＊{col:01}{item:30}{col}を\n 手に入れた。{end} | * Got the {col:01}{item:30}{col}!{end} |

Corrected example (from the pilot): 1001 first read "Lucia became your companion!" - the stock join line is always
`* <Name> joined the party!` (same wording for every companion).

## Stock phrases
- ＊〜が仲間になった！ -> `* X joined the party!`; ＊〜を手に入れた -> `* Got the X!` / `* Received X!` (no a/an before a
  variable); 「〜へ」 area cards -> `To Aaf Village` (keep the quotes off: the card is a title).
- ・・・ alone -> `...`; ！！ -> `!!`. Laughs keep their length roughly (ガッハッハッハッハッ -> Gwahahahaha).
