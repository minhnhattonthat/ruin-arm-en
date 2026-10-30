# Glossary - Ruin Arm

Binding for every translator and reviewer. Agents propose additions in reports; only the controller edits this file.
`tools/batches.py check` enforces the tables: when a row's JP occurs in an entry (katakana terms as whole runs only),
one of its EN forms (alternatives separated by ` / `, case-insensitive) must appear in the English; the Avoid column
fails the check. Story context: `docs/synopsis.md`.

## Rulings (asked of the user once; options and reasons in docs/decisions.md)
- Honorifics: kept, hyphenated (Lucia-san). Name order: Western (given name first).
- Romanisation source: official English names where they exist (only the title, RUIN ARM), else an earlier fan patch
  (none found), else the intended Western name for katakana loanwords, else Hepburn without macrons (D12).
- Credits: English, staff names in Western order (given name first).
- Register / flavour: plain modern fantasy English, light on archaisms; each character's voice per
  `docs/style-reference.md`. Sound effects and laughs: English equivalents ("Gwahahaha!", "Ohohoho!", "Hmph!").
- Abbreviations: full names and terms everywhere, prefer engine changes over shortening; abbreviate only as a flagged
  last resort.

## Style rules
- Punctuation map: 「」 -> "...", 『』 -> '...', ・・・ -> ..., ！？ -> !?.
- Voices: `docs/style-reference.md`.
- お兄ちゃん (the sister to the hero) = "big brother" / "Brother"; 兄様 (Fara) = "Brother"; お父さん = "Dad" (children)
  or "your father".
- Bolboza's katakana lines (machine voice) are written in capitals: "EXTERMINATE HUMANITY."

## Characters
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| ボーガン | Bogan | | the hero's father, ex-captain of the Londium Knights | Borgan, Vaughan |
| ルシア | Lucia | 7 | small winged girl, party member (name_party_04) | Rucia |
| ジーク | Zieg | 7 | `{name:02}` default; old inventor, secretly king of Kadam | Sieg, Zeke |
| トーラン | Toran | 7 | `{name:03}` default; tiger-masked giant, elder prince of Mediom | |
| ポセナ | Posena | 7 | `{name:04}` default; mermaid princess of Marthnal | |
| ネイル | Neil | 7 | `{name:05}` default; Imperial commander, really prince Neiran | Nail |
| ネーラン | Neiran | | Neil's real name | |
| ザイン | Zain | | Imperial Guard General, founder of the Empire | Sein |
| ボルボーザ | Bolboza | | humanoid machine, the emperor | Volvoza |
| ゴルドー | Goldo | | Earth General | |
| ディーネ | Deene | | Water General (from Undine) | Dine |
| ヒュード | Hude | | Wind General | Hyude |
| フリード | Freed | | Flame General | Fried |
| ミリア | Milia | | Dark Princess Knight | Miria |
| ラミアウォリアー | Lamia Warrior | | Deene's lieutenant | |
| ファーラ | Fara | | princess of Mediom | |
| サーラ | Saara | | queen of Marthnal, Posena's mother | Sarah |
| サラ | Sara | | village girl, Roa's daughter | |
| ロア | Roa | | Sara's mother | |
| エイソッド | Aysod | | Lord Aysod, Resistance leader (ロバート・エイソッド = Robert Aysod) | |
| レイナ | Reina | | Aysod's daughter | |
| ガルザック | Garzack | | Londium knight | |
| シーザー | Caesar | | King Caesar of Londium (シーザー王) | |
| メファウス | Mephaus | | Londium court magician | |
| ギルム | Gilm | | Londium blacksmith | |
| ハヌトゥ | Hanutu | | Marthnal blacksmith | |
| オギリン | Ogilin | | beastfolk fortune-teller | |
| メイヤ | Meiya | | beastfolk girl (メイア at 0077 = same girl) | |
| エディア | Edia | | Whaial girl | |
| ロイ | Roy | | Edia's brother | |
| ヴォルサムリー | Volsamry | | Duke of Stelm | |
| マルガリータ | Margarita | | lady ruler of Tifnu | |
| ラッシュ | Rush | | Rush Ironfang (ラッシュ・アイアンファング), adventurer | |
| シンシア | Cynthia | | minor NPC | |
| ばあや | Nanny | | Posena's old nanny | |

Default names offered at the name entry (name_hero / name_sister, 7 letters max): hero フレイ Frey, カーマイン Carmine,
リック Rick, シーネ Shine, グレコ Greco, セイ Sei, ルーク Luke, ジール Zeal, あきら Akira, ニール Neal, マイケル Michael,
クライド Clyde, ヘンゼル Hansel, アーム Arm, シオン Sion, ファング Fang; sister フレイヤ Freya, リトル Little,
レイチェル Rachel, ドロシー Dorothy, マリア Maria, エリカ Erika, レイア Leia, リンダ Linda, なぎさ Nagisa, イライザ Eliza,
ジャネット Janet, ボニー Bonnie, グレーテル Gretel, ルイン Ruin, ティルファ Tilfa, ルナ Luna.

## Places
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| アーフ | Arff | 16 | home village (アーフ村 = Arff Village); the game's own world-map label reads ARFF (D19) | Aaf, Arf |
| ワイアル | Whaial | 16 | ワイアルの村 = Whaial Village; map label WHAIAL (D19) | Wyall |
| ラベンナ | Ravenna | 16 | village and ruins; map label RAVENNA | |
| マリア | Mary / Maria | 16 | the village is Mary (マリアの村 = Mary Village, map label MARY, D19); the sister default name stays Maria | |
| ワース | Warse | 16 | ワースの村 = Warse Village; map label WARSE (D19) | Worth |
| ロンディウム | Londium | 16 | Kingdom of Londium; map label LONDIUM (D19) | Rondium |
| ステルム | Stelm | 16 | Stelm Duchy; ステルムの町 = Stelm Town | |
| フェフス | Fefus | 16 | フェフス城 = Fefus Castle | |
| ゴッドホープ | Godhope | 16 | ゴッドホープ岬 = Cape Godhope | |
| ヴェルダー | Velder | | ヴェルダーの大森林 = the Great Velder Forest | Welder |
| ヴェルダの大森林 | Velder Forest | 16 | place.json form | |
| 獣人村 | Beastfolk Village / Beast Village | 16 | place.json: Beast Village (16 max) | |
| ラウ | Raw | | beastfolk village (獣人村ラウ = Beastfolk Village Raw); map label RAW (D19) | Rau |
| ルテア | Lutea | 16 | ルテア自治領 = Lutea Region; ルテア屋敷 = Lutea Mansion; map label LUTEA (D19) | Rutea |
| ティフヌ | Tifnu | 16 | ティフヌ領 = Tifnu Region; map label TIFNU | |
| メディオム | Mediom | 16 | Kingdom of Mediom; map label MEDIOM (D19) | Medeom |
| マースナル | Marthnal | 16 | merfolk Kingdom of Marthnal; map label MARTHNAL (D19) | Marsnal |
| サライ | Sarai | 16 | サライ城 = Sarai Castle | |
| フーベル | Fubel | 16 | フーベルの大地 = the Land of Fubel (undersea) | |
| ケムル海底基地 | Kemul Sea Base | 16 | place.json | |
| 海底基地 | Undersea Base / Sea Base | 16 | the Empire's base in Fubel | |
| カダム | Kadam | 16 | destroyed kingdom | |
| アーノゥン | Arnoun | 16 | アーノゥン地方 = the Arnoun region | |
| バルドア | Baldoa | 16 | バルドア城 = Baldoa Castle; 巨神城バルドア = Titan Castle Baldoa | |
| トンネル洞窟 | Tunnel Cave | 16 | | |
| 妖しい洞窟 | Eerie Cave | 16 | | |
| キラキラ洞窟 | Glitter Cave | 16 | | |
| 海辺の洞窟 | Seaside Cave | 16 | | |

## Factions and titles
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| ライドロイド | Raidroid | | ライドロイド帝国 = the Raidroid Empire | Ridroid |
| レジスタンス | Resistance | | also 反乱軍 = rebel army | |
| カダムの雷 | Thunder of Kadam | | the Resistance's name | |
| 帝国特殊部隊 | Imperial Special Forces | | | |
| 四魔将 | Four Dark Generals | | 四天王 = Four Heavenly Kings (Goldo's boast, same group) | |
| 魔将 | General | | 地/水/風/炎魔将 = Earth/Water/Wind/Flame General; alone = Dark General | |
| 近衛魔将 | Imperial Guard General | | Zain | |
| 闇姫騎士 | Dark Princess Knight | | read ダーク プリンセスナイト in-text | |
| 騎士団 | Knights | | 騎士団長 = Captain of the Knights | |

## Items / skills / terms
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| ルインアーム | Ruin Arm | | official title logo | |
| 聖剣 | holy sword | | 三聖剣 = the Three Holy Swords | |
| 聖盾 | Holy Shield | | | |
| 宝玉 | gem | | the four gems holding the machine's energy | |
| 緑玉 | Emerald | | ダリアの緑玉 = Dahlia Emerald (item) | |
| 黄玉 | Topaz | | モースの黄玉 = Mohs Topaz (item); トパーズ = Topaz | |
| 青玉 | Sapphire | | ガルフの青玉 = Gulf Sapphire (item); サファイア = Sapphire | |
| 紅玉 | Ruby | | ルルスの紅玉 = Lulus Ruby (item) | |
| メビウスリング | Mobius Ring | 16 | | |
| キズナの剣 | Bond Sword | 16 | the holy sword | |
| コールマインド | Call Mind | 16 | memory potion | |
| 謎の宝石 | Mystery Gem | 16 | | |
| 命の花 | Flower of Life | 16 | | |
| 帰心石 | Homing Stone | 16 | | |
| ジャンプブーツ | Jump Boots | 16 | | |
| ジークランチャー | Zieg Launcher | 16 | | |
| ジークショット | Zieg Shot | | | |
| ボーガンの手紙 | Bogan's Letter | 16 | | |
| ムーブ | Move | 16 | teleport spell | |
| キカイ | machine | | ancient tech; 人型キカイ = humanoid machine | |
| 超文明 | super-civilization | | | |
| サークル | circle | | ruin teleport pad | |
| オペレーションルーム | control room | | | |
| クリーチャー | creature | | monsters | |
| 獣人 | beastfolk / Beast | | 獣人族 = beastfolk | |
| 人魚 | merfolk / mermaid / merman | | 人魚族 = merfolk | |
| 翼人 | winged | | 翼人族 = winged folk | |
| 錬金術 | alchemy / alchemist | | 錬金術師 = Alchemist | |
| 元素 | element | | 土/火/水/空気の元素 = Earth/Fire/Water/Air Element | |
| インゴット | Ingot | | | |
| 必殺技 | special | | 協力必殺技 = combo special | |
| ゴールド | gold | | currency | |
| 村長 | Chief | | Village Chief (speaker header) | |
| 宿屋 | inn | | 宿屋の主人 = Innkeeper | |
| 合い言葉 | password | | also キーワード / パスワード (the ruin password) | |
| 洞窟の鍵 | Cave Key | | | |
| 協力必殺技 | combo special | | タメ = charge | |
| 特殊部隊 | Special Forces | | | |

## Decisions from earlier batches
- Speaker headers carry the full title: "Earth General Goldo", "Water General Deene", "Wind General Hude", "Flame
  General Freed", "Imperial Guard General Zain", "Dark Princess Knight Milia", "King Caesar". 手紙 header = "Letter",
  隊長 = "Captain", 国王 / 助手 / 勇者 (narration in Zieg's story) = "King" / "Assistant" / "Hero".
- 四天王が一人 = "one of the Four Heavenly Kings". はっ (soldier answering) = "Yes, sir!".
- 持ち物がいっぱいです = "* X's inventory is full." / "* Your inventory is full."
- 様 after a name stays -sama (Fara-sama, Neil-sama); 王女様 alone = "Your Highness" / "the Princess".
  {name:02}じいちゃん = "Grandpa {name:02}"; おばさん (to an adult woman) = "Auntie".
- ★ (stat points, no ★ in the font) = "Stars", coloured as in the JP.
- Bolboza / machine katakana lines in capitals; 01AC's backwards katakana is written backwards in capitals.
- Credits headings: Production Manager, Producers, Director, Advisors, Cast, Character Design, Original Story, Special
  Thanks, Assistance, Game Design, Program, Graphic Design, Sound Engineers, Supervisors; 集英社 = Shueisha, 月刊Vジャンプ
  = Monthly V Jump, 週刊少年ジャンプ = Weekly Shonen Jump. Full staff names live in msg02 (b014); the staff roll (b015)
  holds shortened forms until the phase-7 relocation (LONG list in docs/status.md).
