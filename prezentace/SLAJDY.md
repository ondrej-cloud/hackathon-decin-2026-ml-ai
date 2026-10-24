# Slajdy a texty řečníků

Deset slajdů na 6:40, rezerva 20 s do 7:00, pak deset záložních. Živé demo neděláme, aplikace je na slajdu 9 jako snímek, aby nic nespadlo; web otevíráme až při otázkách. Text řečníka je napsaný tak, jak se říká nahlas, na zhruba 130 slov za minutu; u každého slajdu je počet slov a strop pro jeho délku. `[mezerník]` znamená další krok decku. Body zadání: 1 co řešíme, 2 data, 3 příprava dat, 4 vstupy, 5 model, 6 ověření, 7 limity.

| # | Čas | Řečník | Nadpis | Slov / strop | Bod |
|---|---|---|---|---|---|
| 1 | 0:00–0:25 | Tobias | (video) | 13 / 54 | 1 |
| 2 | 0:25–0:50 | Tobias | Den předem víte, kam až voda dosáhne | 51 / 54 | 1 |
| 3 | 0:50–1:30 | Ondra | Co teče Prahou teď, je zítra v Děčíně | 78 / 87 | 2 |
| 4 | 1:30–2:20 | Dan | Co model bere a co ne | 106 / 108 | 3, 4 |
| 5 | 2:20–3:10 | Honza | Od 44 cm k 17: jak jsme došli k přímce | 100 / 108 | 5 |
| 6 | 3:10–3:45 | Honza | Předpověď je součet: kolik centimetrů přidá každá řeka | 55 / 76 | 5 |
| 7 | 3:45–4:20 | Ondra | Ověřujeme třikrát, na povodních, které model neviděl | 71 / 76 | 3, 6 |
| 8 | 4:20–5:10 | Ondra | Boris: 3. stupeň hlášen 27 h předem, chyba o 55 % menší | 95 / 108 | 6 |
| 9 | 5:10–5:40 | Honza | Aplikace: Děčín dnes a za 24 hodin | 50 / 65 | 1 |
| 10 | 5:40–6:40 | Dan, závěr Tobias | Co umíme, co ne a co dál | 109 / 130 | 7 |

Celkem 728 slov, při 130 slovech za minutu 5:36 mluvení. Zbytek do 6:40 je video (25 s, mluví se až na konci) a pauzy na kroky decku.

## 1 · Video (0:00–0:25, Tobias)

Na slajdu: video rozlivu Labe v Děčíně při Borisovi, září 2024, přes celou obrazovku, bez zvuku (`web/prezentace/video/boris_decin_720.mp4`, náhled `grafy/video_decin_poster.jpg`). Na konci naskočí věta.

Text (video běží bez mluvení, věta až na konci):

> Tohle je Děčín v září 2024. Náš model to hlásil 27 hodin předem.

13 slov. Nic dalšího neříkat.

## 2 · Den předem víte, kam až voda dosáhne (0:25–0:50, Tobias)

Na slajdu: snímek rozlivu v Děčíně přes celý slajd (`grafy/02_mapa_decin.png`, v HTML decku fotka `grafy/boris_decin_110.jpg`), velké číslo **27 h**, tři štítky: Povodňová komise, Hasiči, Lidé u řeky.

> Naše aplikace předpovídá hladinu Labe v Děčíně a v Ústí na 12, 24 a 36 hodin dopředu. Varuje před druhým a třetím stupněm povodňové aktivity a v mapě ukáže, kam voda dosáhne. Je pro povodňovou komisi, hasiče a lidi u řeky. Den navíc znamená odvézt auta, postavit pytle a vyklidit sklepy.

51 slov.

## 3 · Co teče Prahou teď, je zítra v Děčíně (0:50–1:30, Ondra)

Na slajdu: vlevo mapa 12 stanic na Vltavě, horním Labi a Ohři (`grafy/03a_mapa_stanic.png`), tři čísla **20 let · 12 stanic · 175 320 hodin**. Po mezerníku vpravo graf `grafy/03b_doba_dobehu.png` (za kolik hodin doteče voda z každé stanice do Děčína, svislá čára 24 h).

> Co teče Prahou teď, je zítra v Děčíně. Proto jsme vzali hodinový archiv ČHMÚ: dvanáct stanic na Vltavě, horním Labi a Ohři, dvacet let od roku 2006. Je to stejný zdroj jako balíček od pořadatelů, jen delší a s víc stanicemi.
>
> [mezerník]
>
> Tady je, za kolik hodin doteče voda do Děčína: z Ústí za 4, z Prahy za 17, ze Sázavy za 25. Proto předpovídáme den dopředu. Vodu, která ještě neteče žádnou stanicí, z měření na řece nevidí nikdo.

78 slov. Čísla jsou z korelace změn průtoku na trénovací části (`docs/DATA.md`, doba doběhu do Děčína).

## 4 · Co model bere a co ne (1:30–2:20, Dan)

Na slajdu: vlevo krátce **Bereme:** hladina Děčín a Ústí, průtok na 12 stanicích, teď a až 36 h zpátky = 98 čísel. Vpravo graf `grafy/04_co_model_bere.png` (o kolik se změní chyba na validaci proti finálním 17,1 cm, když přidáme další vstup; čára −1 cm je naše pravidlo). Dole jedna věta: „Co přijde do 36 h, už teče řekou.“

> Model bere jen to, co je v tu chvíli změřené na řece: hladinu v Děčíně a v Ústí a průtok na dvanácti stanicích, teď a až 36 hodin zpátky. Dohromady 98 čísel. Průtok dáváme pod odmocninu, protože hladina roste s průtokem zhruba jako odmocnina.
>
> [mezerník]
>
> Co nebereme, i když by to dávalo smysl? Srážky, sníh, teplotu vzduchu, vlhkost, tlak ani vítr. Všechno jsme zkusili a nic nepomohlo ani o centimetr. Déšť, který padá teď, doteče do Děčína většinou až za víc než 36 hodin. Co přijde dřív, už teče řekou a vidíme to v průtoku. I kdybychom déšť na tři dny dopředu znali přesně, chyba klesne jen o centimetr.

106 slov. Kdyby se porota zeptala na teplotu vody: s povodní nesouvisí, nezkoušeli jsme ji.

Čísla v grafu (validace, chyba na povodních, finální model 17,1 cm): naměřené srážky 17,1; teplota vzduchu a sníh 17,3; voda ve sněhu 17,8; vlhkost 17,2; tlak 17,0; vítr 17,0; víc stanic proti proudu (horní Ohře) 17,4; myšlenkový pokus, déšť na 3 dny dopředu přesně 16,1. Tlak a vítr jsou o desetinu lepší, to je v rámci náhody a daleko od našeho pravidla 1 cm. Zdroje: `docs/POKUSY.md` pá 20:44, pá 22:32, pá 23:14, so 0:19, so 8:42.

## 5 · Od 44 cm k 17: jak jsme došli k přímce (2:20–3:10, Honza)

Na slajdu: graf `grafy/05_cesta_k_modelu.png`, tři skupiny sloupců. Začátek: „bude jako teď“ 44,3, jen data jako v balíčku 44,6. Čtyři modely: fyzikální 24,8, LightGBM 23,1, neuronová síť 17,8, lineární regrese 17,1. Úpravy přímky: doba putování podle průtoku 21,8, polynom 19,9, váhy na povodně 17,2, spojení malých zlepšení 17,2. Po posledním mezerníku rámeček s citátem ze zadání.

> Začali jsme laťkou „bude jako teď“: 44 centimetrů chyby při povodních. Se stanicemi jen z kraje a dvěma lety dat, jako v balíčku, vyšlo totéž. Teprve stanice proti proudu a dvacet let historie dávají výsledek.
>
> [mezerník]
>
> Pak čtyři modely od nejjednoduššího po složitý, každý dělal jeden z nás a pravidlo bylo stejné: změna musí zlepšit aspoň o centimetr. Fyzikální 25, LightGBM 23, neuronová síť 18, lineární regrese 17. Vybrali jsme ji před testem.
>
> [mezerník]
>
> Pak úpravy přímky: polynom, váhy na povodně, spojení všech malých zlepšení. Nic nebylo lepší o víc než centimetr.
>
> [mezerník]
>
> A zadání samo říká: cílem není vytvořit co nejsložitější model.

100 slov. Když padne „proč přímka“: voda v Děčíně je součet Vltavy, Labe a Ohře, každá posunutá o dobu, než doteče, a velké povodně nad třetím stupněm jsou v tréninku jen dvě (víc na slajdu 6 a v Z1).

## 6 · Předpověď je součet: kolik centimetrů přidá každá řeka (3:10–3:45, Honza)

Na slajdu: sloupce součtu (`grafy/06_predpoved_je_soucet.png`, v HTML decku animované), vpravo číslo, které roste s každým krokem: 198 → 577 cm, nakonec štítek **3. stupeň · nad 560 cm**. Šest kroků mezerníkem.

> Lineární regrese z těch 98 čísel udělá vážený součet. Příklad z Borise, předpověď vydaná den předem. Začíná na průměru, 198 centimetrů.
>
> [mezerník] Děčín a Ústí přidají 80. [mezerník] Vltava 89. [mezerník] Horní Labe 116. [mezerník] Mělník 96. [mezerník] Ohře ubere 2.
>
> [mezerník] Vyjde 577, nad třetím stupněm, takže model varoval. Skutečně bylo 551 a třetí stupeň přišel o tři hodiny později.

55 slov.

## 7 · Ověřujeme třikrát, na povodních, které model neviděl (3:45–4:20, Ondra)

Na slajdu: časová osa 2006–2025 `grafy/07_jak_overujeme.png`, vpravo tři kroky (výběr modelu, vícenásobná validace, test), věta „Dělení v čase, nikdy náhodně“, po mezerníku rámeček „Dvě pasti z budoucnosti“.

> Ověřujeme třikrát, vždy na povodních, které model neviděl. Data dělíme v čase, nikdy náhodně. Model jsme vybrali na čtyřech vynechaných povodních. Pak jsme každou z osmi povodní 2006 až 2020 jednou vynechali a model naučili na zbytku, to je vícenásobná validace. Test na letech 2021 až 2025 jsme pustili jednou, na konci.
>
> [mezerník]
>
> V datech jsme našli dvě pasti, které braly informaci z budoucnosti: doplňování děr a denní srážky. Obě jsme vyřadili.

71 slov.

## 8 · Boris: 3. stupeň hlášen 27 h předem, chyba o 55 % menší (4:20–5:10, Ondra)

Na slajdu: vlevo graf `grafy/08_boris_2024.png`, vpravo dvě velká čísla **27 h** („před 3. stupněm v Děčíně“) a **−55 %** („test 22,4 proti 50,2 cm · vícenásobná validace 20,1 proti 45,2 cm“).

> Tohle je Boris, září 2024, z testu, takže ho model nikdy neviděl. Černá je skutečná hladina, modrá naše předpověď vydaná 24 hodin předem a jde se skutečností. Šedá čárkovaná je „bude jako teď“, ta je vždycky o den pozadu. Třetí stupeň model hlásil 27 hodin předem a vrchol 649 centimetrů předpověděl na 611.
>
> [mezerník]
>
> V číslech: na testu 2021 až 2025 je chyba při povodních 22,4 centimetru proti 50,2 u „bude jako teď“, o 55 procent méně. Ve vícenásobné validaci na osmi povodních 20,1 proti 45,2, zase o 55 procent. Dvakrát stejné číslo, není to náhoda.

95 slov.

## 9 · Aplikace: Děčín dnes a za 24 hodin (5:10–5:40, Honza)

Na slajdu: snímek webu na Dnešku `grafy/09_aplikace_dnes.png` přes celý slajd (vodočet, za 12, 24 a 36 h, vedle oficiální ČHMÚ), dole adresa field-zero.netlify.app a QR kód. Živé demo neděláme, web otevřeme až při otázkách, když o něj porota stojí.

> Takhle to vypadá v aplikaci, tohle je dnešní ráno. Děčín v šest hodin 84 centimetrů, za 24 hodin podle nás 94, oficiální předpověď ČHMÚ 90. Modrý pás je rozmezí, kam se skutečnost vejde zhruba osmkrát z deseti. Data bere živě od ČHMÚ. K tomu mapa rozlivu a přehrávání starých povodní.

50 slov. Čísla jsou ze snímku (vydáno 24. 10. v 6:00); když se snímek obnoví, přepsat je podle něj.

## 10 · Co umíme, co ne a co dál (5:40–6:40, Dan, závěr Tobias)

Na slajdu: čtyři karty (Umíme, Neumíme, Proč ne srážky, Dál), po mezerníku závěrečná věta, Děkujeme a QR kód na repozitář.

Dan:

> Co umíme: hladinu v Děčíně a v Ústí na 12, 24 a 36 hodin, třetí stupeň den předem a rozliv v mapě. Co neumíme: na 36 hodin je chyba skoro dvakrát větší než na 24, voda, která přijde, ještě neteče žádnou stanicí. Vrchol vyšší, než jaký model viděl v tréninku, podhodnotí. V provozu chodí data se zpožděním jedné až tří hodin. S oficiální předpovědí ČHMÚ se na starých povodních srovnat neumíme. Dál bychom přidali předpověď srážek na dva až tři dny a dvoustupňové varování: nejdřív předběžná výstraha, pak ostrá.

Tobias, [mezerník]:

> Z otevřených dat zdarma: o povodni v Děčíně víte den předem, s modelem, který se vejde na jeden obrázek. Děkujeme.

109 slov dohromady (Dan 89, Tobias 20). „Skoro dvakrát“: na testu v Děčíně 17,5 cm na 24 h a 29,9 cm na 36 h, tedy 1,7krát.

## Záložní slajdy

Ukážou se jen na otázku poroty. V decku jsou za Děkujeme, klávesou End se skočí na konec a šipkou zpět na ten, který je potřeba. Na každém je otázka jako nadpis, graf a jedna dvě věty.

### Z1 · Proč jen lineární regrese?

Graf `grafy/Z1_srovnani_ctyr_modelu.png`. Odpovídá Dan nebo Ondra.

Na čtyřech povodních, které model neviděl, vyšla nejlíp: 17,1 cm, neuronová síť 17,8, LightGBM 23,1, fyzikální model 24,8. Voda v Děčíně je součet řek posunutých o dobu, než doteče, a velké povodně jsou v tréninku jen dvě, složitý model by se z nich naučil náhodu. Nepřeučí se: v Děčíně na 24 h má chybu na tréninku 19,7 cm a na validaci 15,5. Nic z dalšího zkoušení nebylo lepší o víc než 1 cm.

### Z2 · Co znamená „bude jako teď“?

Graf `grafy/Z2_co_je_jako_ted.png`. Odpovídá Ondra.

Předpověď, že hladina za 24 h bude stejná jako teď. Nakreslená v čase, pro který platí, je to skutečná křivka posunutá o den doprava, takže vzestup ohlásí až den poté, co se stal. Proto má při povodních chybu 44 až 50 cm a každý model ji musí porazit.

### Z3 · Proč ne srážky?

Graf `grafy/Z3_proc_ne_srazky.png`. Odpovídá Dan.

Zkusili jsme horní mez: model dostal skutečný déšť na 3 dny dopředu, jako by předpověď počasí byla dokonalá. Chyba klesla jen o 1 cm (17,1 → 16,1) a varování nepřišlo dřív. První nárůst vody vidíme v průtocích proti proudu 12 až 40 h předem, déšť, který spadne teď, doteče do Děčína většinou až za víc než 36 h. Pomohl by na 2 až 3 dny u dešťových povodní, jenže archiv starých předpovědí na trénink nemáme.

### Z4 · Jak moc se pletete?

Graf `grafy/Z4_jak_moc_se_pleteme.png`. Odpovídá Honza.

K předpovědi ukazujeme rozmezí od–do. Je spočítané z chyb modelu na tréninku (90 % chyb) podle toho, jak vysoko voda je, a ověřené na validaci: na klidné vodě se do něj skutečnost vejde v 9 z 10 hodin, na povodních asi v 8 z 10.

### Z5 · Funguje to i na jiné povodni?

Graf `grafy/Z5_povoden_2011.png`. Odpovídá Ondra.

Leden 2011, povodeň z validace, kterou model při učení neviděl: 3. stupeň hlášen 15 hodin předem, vrchol 730 cm. A ve vícenásobné validaci byla chyba menší než u „bude jako teď“ na každé z 8 povodní.

### Z6 · Podle čeho model rozhoduje?

Graf `grafy/Z6_vahy_modelu.png`. Odpovídá Honza.

Každé políčko je váha jednoho vstupu: o kolik centimetrů se předpověď změní, když je hodnota o obvyklý rozkmit vyšší než průměr. Nejvíc váží Děčín teď (+88 cm) a Praha teď (+49 cm). Oranžová políčka vedle modrých znamenají, že model odečítá starší hodnotu od nové, tedy počítá, jestli voda stoupá.

### Z7 · Je rozliv hydraulický model?

Podklad `grafy/mapbox3_decin.jpg`. Odpovídá Honza.

Není. Porovnáváme výšku terénu (ČÚZK DMR 5G) s výškou hladiny a zaplavíme to, co je níž a spojené s řekou. Ověřeno proti úřední mapě záplavových území: při pětileté vodě náš rozliv 167 ha, úřední 183 ha, průnik 165 ha, shoda 0,89. Zdi a hráze pod rozlišením terénu nevidí.

### Z8 · Jak dopadl test?

Graf `grafy/Z8_test_2021_2025.png`. Odpovídá Ondra.

Test 2021 až 2025 jsme pustili jednou, na model vybraný předem a naučený na všem do 2020. Chyba při povodních 22,4 cm proti 50,2 u „bude jako teď“, o 55 % méně, a před 3. stupněm model varoval pokaždé. Neuronová síť tam vyšla o 1,1 cm lépe, výběr jsme podle testu neměnili, jinak by test přestal být nezávislý.

### Z9 · Není výsledek jen náhoda výběru validace?

Graf `grafy/Z9_vicenasobna_validace.png`. Odpovídá Ondra.

Každou z 8 povodní 2006 až 2020 jsme jednou vynechali a model naučili na ostatních. Chyba 20,1 ± 7,7 cm proti 45,2 u „bude jako teď“, o 55 % méně, stejně jako na testu, a na každé povodni zvlášť o 34 až 66 % méně. Chyba víc záleží na povodni než na modelu.

### Z10 · Proč jste brali data mimo balíček?

Graf `grafy/Z10_proc_externi_data.png`. Odpovídá Ondra.

Balíček má dva roky a stanice v kraji, nejvýš proti proudu je Ústí, 4 hodiny před Děčínem. Se stanicemi jen z kraje a dvěma lety dat vyšla chyba 44,6 cm, stejně jako „bude jako teď“, a model propásl polovinu povodní; s 12 stanicemi a 20 lety 17,1. Archiv ČHMÚ je stejný zdroj, za 2024 a 2025 sedí s balíčkem na centimetr.
