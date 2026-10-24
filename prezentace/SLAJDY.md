# Slajdy a texty řečníků

Deset slajdů na 7:00 včetně dema, pak sedm záložních. Obsah a pořadí jsou podle HTML decku (`web/prezentace/index.html`), čas a řečníci podle kostry (`docs/PREZENTACE_7MIN.md`). Text řečníka je napsaný tak, jak se říká nahlas, na zhruba 130 slov za minutu; počet slov je u každého slajdu. `[mezerník]` znamená další krok decku (odkryje další část slajdu). Body zadání: 1 co řešíme, 2 data, 3 příprava dat, 4 vstupy, 5 model, 6 ověření, 7 limity.

| # | Čas | Řečník | Nadpis | Slov | Bod |
|---|---|---|---|---|---|
| 1 | 0:00–0:25 | Tobias | (video) | 13 | 1 |
| 2 | 0:25–0:55 | Tobias | Den předem víte, kam až voda dosáhne | 51 | 1 |
| 3 | 0:55–1:40 | Ondra | Co teče Prahou teď, je zítra v Děčíně | 85 | 2 |
| 4 | 1:40–2:15 | Honza | Předpověď je součet: kolik centimetrů přidá každá řeka | 65 | 4, 5 |
| 5 | 2:15–2:55 | Dan | Žádná z 11 dalších cest nebyla lepší | 81 | 5 |
| 6 | 2:55–3:30 | Ondra | Ověřujeme třikrát, pokaždé na povodních, které model neviděl | 71 | 3, 6 |
| 7 | 3:30–4:10 | Ondra | Boris: 3. stupeň hlášen 27 hodin předem | 56 | 6 |
| 8 | 4:10–4:40 | Ondra | O 55 % menší chyba na testu i na všech 8 povodních | 55 | 6 |
| 9 | 4:40–5:50 | Honza | Živé demo | 95 | 1, 6 |
| 10 | 5:50–7:00 | Dan, závěr Tobias | Co umíme, co ne a co dál | 132 | 7 |

Celkem 704 slov, při 130 slovech za minutu 5:25 mluvení. Zbytek do 7:00 je video (25 s bez mluvení), klikání v demu a pauzy na kroky decku.

## 1 · Video (0:00–0:25, Tobias)

Na slajdu: video rozlivu Labe v Děčíně při Borisovi, září 2024, přes celou obrazovku, bez zvuku (`web/prezentace/video/boris_decin_720.mp4`). Na konci naskočí věta. Náhled `grafy/video_decin_poster.jpg`.

Text (25 s video bez mluvení, na konci):

> Tohle je Děčín v září 2024. Náš model to hlásil 27 hodin předem.

13 slov. Nic dalšího neříkat, video mluví samo.

## 2 · Den předem víte, kam až voda dosáhne (0:25–0:55, Tobias)

Na slajdu: snímek rozlivu v Děčíně 17. 9. 2024 přes celý slajd (`grafy/boris_decin_110.jpg`, v Canvě `grafy/02_mapa_decin.png`), velké číslo **27 h**, pod ním „3. stupeň v Děčíně hlášen 27 hodin předem · Boris, září 2024“, tři štítky: Povodňová komise, Hasiči, Lidé u řeky.

> Naše aplikace předpovídá hladinu Labe v Děčíně a v Ústí na 12, 24 a 36 hodin dopředu. Varuje před druhým a třetím stupněm povodňové aktivity a v mapě ukáže, kam voda dosáhne. Je pro povodňovou komisi, hasiče a lidi u řeky. Den navíc znamená odvézt auta, postavit pytle a vyklidit sklepy.

51 slov.

## 3 · Co teče Prahou teď, je zítra v Děčíně (0:55–1:40, Ondra)

Na slajdu: mapa 12 stanic na Vltavě, horním Labi a Ohři (v decku kreslená, v Canvě `grafy/03a_mapa_stanic.png`), tři čísla **20 let · 12 stanic · 175 320 hodin měření**, graf `grafy/03b_proc_externi_data.png` (po mezerníku se odkryje třetí sloupec).

> Co teče Prahou teď, je zítra v Děčíně. Z Prahy do Děčína teče voda 17 až 26 hodin. Proto jsme vzali hodinový archiv ČHMÚ: dvanáct stanic na Vltavě, horním Labi a Ohři, dvacet let od roku 2006. Je to stejný zdroj jako balíček od pořadatelů, za roky 2024 a 2025 sedí na centimetr.
>
> [mezerník]
>
> S daty jen z balíčku, dva roky a stanice v kraji, má model chybu 44,6 centimetru. To je stejně špatně jako „bude jako teď“ a polovinu povodní propásne. S našimi daty 17,1.

85 slov.

## 4 · Předpověď je součet: kolik centimetrů přidá každá řeka (1:40–2:15, Honza)

Na slajdu: podtitul „98 vstupů: hladina a průtok teď a za posledních 36 h, jen to, co je změřené“. Vlevo sloupce součtu (v decku animované, v Canvě `grafy/04_predpoved_je_soucet.png`), vpravo číslo, které roste s každým krokem: 198 → 577 cm, nakonec štítek **3. stupeň · nad 560 cm**. Šest kroků mezerníkem.

> Model vidí jen to, co je v tu chvíli změřené: hladinu a průtok teď a za posledních 36 hodin, celkem 98 čísel. Lineární regrese z nich udělá vážený součet. Příklad z Borise, den předem. Začíná na průměru, 198 centimetrů.
>
> [mezerník] Děčín a Ústí přidají 80. [mezerník] Vltava 89. [mezerník] Horní Labe 116. [mezerník] Mělník 96. [mezerník] Ohře ubere 2.
>
> [mezerník] Vyjde 577, nad třetím stupněm, takže model varoval. Skutečně bylo 551.

65 slov. Když bude čas: „třetí stupeň přišel o tři hodiny později“.

## 5 · Žádná z 11 dalších cest nebyla lepší (2:15–2:55, Dan)

Na slajdu: graf `grafy/05_co_jsme_zkouseli.png` (12 vodorovných sloupců, modrý je finální model), vpravo **3 další modely** (neuronová síť, LightGBM, fyzikální model) a **8 úprav přímky**, po mezerníku rámeček „Proč přímka“.

> Zkusili jsme dvanáct cest. Tři další modely: neuronovou síť, LightGBM, to jsou rozhodovací stromy, a fyzikální model. A osm úprav přímky, třeba srážky, sníh, víc stanic, polynom nebo všechna malá zlepšení dohromady. Žádná nebyla lepší než lineární regrese se 17,1 centimetru.
>
> [mezerník]
>
> Proč přímka? Voda v Děčíně je součet Vltavy, Labe a Ohře, každá posunutá o dobu, než doteče. To je přesně vážený součet. A povodně nad třetím stupněm jsou v tréninku jen dvě. Složitý model by se z nich naučil náhodu.

81 slov.

## 6 · Ověřujeme třikrát, pokaždé na povodních, které model neviděl (2:55–3:30, Ondra)

Na slajdu: časová osa 2006–2025 `grafy/06_jak_overujeme.png`, vpravo tři kroky (výběr modelu, vícenásobná validace, test), věta „Dělení v čase, nikdy náhodně“, po mezerníku rámeček „Dvě pasti z budoucnosti“.

> Ověřujeme třikrát, vždy na povodních, které model neviděl. Data dělíme v čase, nikdy náhodně. Model jsme vybrali na čtyřech vynechaných povodních. Pak jsme každou z osmi povodní 2006 až 2020 jednou vynechali a model naučili na zbytku, to je vícenásobná validace. Test na letech 2021 až 2025 jsme pustili jednou, na konci.
>
> [mezerník]
>
> V datech jsme našli dvě pasti, které braly informaci z budoucnosti: doplňování děr a denní srážky. Obě jsme vyřadili.

71 slov. Bod 3 (příprava dat) tu zazní jen pastmi, zbytek je v `OTAZKY.md` (otázka „Jak jste data připravili?“).

## 7 · Boris: 3. stupeň hlášen 27 hodin předem (3:30–4:10, Ondra)

Na slajdu: graf `grafy/07_boris_2024.png` (kreslí se 3 s), vpravo velké **27 h** „před 3. stupněm v Děčíně“, věty o vrcholu.

> Tohle je Boris, září 2024, z testu. Černá je skutečná hladina, modrá naše předpověď vydaná 24 hodin předem. Jde se skutečností. Šedá čárkovaná je „bude jako teď“, ta je vždycky o den pozadu.
>
> [27 h naskočí samo]
>
> Třetí stupeň model hlásil 27 hodin předem. Vrchol 649 centimetrů předpověděl na 611, tedy o 38 níž. A tuhle povodeň model nikdy neviděl.

56 slov.

## 8 · O 55 % menší chyba na testu i na všech 8 povodních (4:10–4:40, Ondra)

Na slajdu: velké **−55 %**, dva grafy `grafy/08a_test_2021_2025.png` a `grafy/08b_vicenasobna_validace.png`, dole „Dvakrát stejné číslo. Není to náhoda.“

> A v číslech. Na testu 2021 až 2025 je průměrná chyba při povodních 22,4 centimetru, „bude jako teď“ má 50,2. To je o 55 procent méně. Vícenásobná validace na osmi povodních: 20,1 proti 45,2, zase o 55 procent méně a na každé povodni zvlášť o 34 až 66 procent. Dvakrát stejné číslo, není to náhoda.

55 slov. Když se nestíhá: slajd přeskočit a na konci slajdu 7 říct jen „na testu i ve vícenásobné validaci je chyba o 55 procent menší“.

## 9 · Živé demo (4:40–5:50, Honza)

Na slajdu: tři odkazy (Boris v aplikaci, Dnešek, Mapa Borise) a tlačítko „Načíst mapu Borise sem“. Demo jede z webu https://field-zero.netlify.app, ne z lokálního serveru (lokální `npx serve` zahazuje parametry v odkazech, viz `README.md`). Aplikace se po otevření ukáže rovnou na Dnešku. Čísla v hranatých závorkách se čtou z obrazovky.

| Čas | Klik | Co říct |
|---|---|---|
| 4:40 | odkaz **Dnešek** (otevře novou kartu) | „Tohle je Děčín teď, živá data ČHMÚ z [hodina]. Hladina je [X] centimetrů. Za 24 hodin podle nás bude [Y], oficiální předpověď ČHMÚ říká [Z]. Modrý pás je rozmezí, kam se skutečnost vejde zhruba osmkrát z deseti.“ |
| 5:00 | zpět na kartu s deckem, odkaz **Boris v aplikaci** (otevře 14. 9. 2024 11:00; přes panel vlevo by se otevřel jiný okamžik a v Dnešku je výběr povodní zamčený) | „A tohle je Boris, 14. září v jedenáct, den před třetím stupněm. Teď 389 centimetrů, za 24 hodin model říká 577. To je třetí stupeň, a to o den dřív, než přišel.“ |
| 5:20 | zpět na deck, **Načíst mapu Borise sem**, v úvodním okně **Přehrát povodeň** | „Mapa ukazuje, kam voda podle hladiny dosáhne. Rozliv je z výškového modelu terénu.“ |
| 5:35 | vlevo přepnout na porovnání s předpovědí | „Na jedné straně rozliv z předpovědi vydané den předem, na druhé ze skutečnosti.“ |
| 5:45 | **Zavřít mapu** vpravo nahoře, šipka na další slajd | (nic, rovnou slajd 10) |

95 slov. Po kliknutí do mapy patří klávesy mapě, na další slajd se jde až po Zavřít mapu.

Když se něco zasekne, neopravovat a jet dál:

- Dnešek se nenačte nebo ukazuje varování o starých datech: „Živá data ČHMÚ teď nedorazila, ukážu povodeň, u které víme, jak dopadla.“ A rovnou Boris.
- Mapa se nenačte (internet, Mapbox): Zavřít mapu, klávesa Home na slajd 1, pustit video: „Takhle vypadá ten rozliv po hodinách.“ Pak End nebo šipkami na slajd 10.
- Nejde internet vůbec: demo vynechat, říct „aplikace běží na field-zero.netlify.app, mapu jste viděli na začátku“ a jet na slajd 10. Ušetřený čas nevadí.

## 10 · Co umíme, co ne a co dál (5:50–7:00, Dan, závěr Tobias)

Na slajdu: čtyři karty (Umíme, Neumíme, Proč ne srážky, Dál), po mezerníku závěrečná věta, Děkujeme a QR kód na repozitář.

Dan:

> Co umíme: hladinu v Děčíně a v Ústí na 12, 24 a 36 hodin, třetí stupeň den předem a rozliv v mapě. Co neumíme: na 36 hodin je chyba skoro dvakrát větší než na 24. Voda, která přijde, ještě neteče žádnou stanicí, je v potocích nebo ještě nespadla. Vrchol vyšší, než jaký model viděl v tréninku, podhodnotí. Srážky na 12 až 36 hodin nepomáhají, ta voda už je v řekách. Archivní data jsou zpětně ověřená, v provozu chodí předběžná a se zpožděním. Historické předpovědi ČHMÚ nemáme, takže se s nimi na povodních srovnat neumíme. Dál bychom přidali předpověď srážek na dva až tři dny a dvoustupňové varování, nejdřív předběžná výstraha, pak ostrá.

Tobias, [mezerník]:

> Z otevřených dat zdarma: o povodni v Děčíně víte den předem, s modelem, který se vejde na jeden obrázek. Děkujeme.

132 slov dohromady (Dan 112, Tobias 20).

## Záložní slajdy

Ukážou se jen na otázku poroty. V decku jsou za Děkujeme, klávesou End se skočí na konec a šipkou zpět na ten, který je potřeba. Na každém je otázka jako nadpis, graf a jedna dvě věty.

### Z1 · Proč jen lineární regrese?

Graf `grafy/Z1_srovnani_ctyr_modelu.png`. Odpovídá Dan nebo Ondra.

Na čtyřech povodních, které model neviděl, vyšla nejlíp: 17,1 cm, neuronová síť 17,8, LightGBM 23,1, fyzikální model 24,8. Nepřeučí se, v Děčíně na 24 h má chybu na tréninku 19,7 cm a na validaci 15,5. Každou váhu umíme vysvětlit fyzikálně.

### Z2 · Co znamená „bude jako teď“?

Graf `grafy/Z2_co_je_jako_ted.png`. Odpovídá Ondra.

Předpověď, že hladina za 24 h bude stejná jako teď. Nakreslená v čase, pro který platí, je to skutečná křivka posunutá o den doprava, takže vzestup ohlásí až den poté, co se stal. Proto má při povodních chybu 44 až 50 cm a každý model ji musí porazit.

### Z3 · Proč ne srážky?

Graf `grafy/Z3_proc_ne_srazky.png`. Odpovídá Dan.

Zkusili jsme horní mez: model dostal skutečný déšť na 3 dny dopředu, jako by předpověď počasí byla dokonalá. Chyba klesla jen o 1 cm (17,1 → 16,1) a varování nepřišlo dřív. První nárůst vody vidíme v průtocích proti proudu 12 až 40 h předem, déšť, který spadne teď, doteče do Děčína většinou až za víc než 36 h.

### Z4 · Jak moc se pletete?

Graf `grafy/Z4_jak_moc_se_pleteme.png`. Odpovídá Honza.

K předpovědi ukazujeme rozmezí od–do. Je spočítané z chyb modelu na tréninku (90 % chyb) podle toho, jak vysoko voda je, a ověřené na validaci: skutečnost se do něj vejde v 8 až 9 z 10 hodin.

### Z5 · Funguje to i na jiné povodni?

Graf `grafy/Z5_povoden_2011.png`. Odpovídá Ondra.

Leden 2011, povodeň z validace, kterou model při učení neviděl: 3. stupeň hlášen 15 hodin předem, vrchol 730 cm. A ve vícenásobné validaci byla chyba menší než u „bude jako teď“ na každé z 8 povodní.

### Z6 · Podle čeho model rozhoduje?

Graf `grafy/Z6_vahy_modelu.png`. Odpovídá Honza.

Každé políčko je váha jednoho vstupu: o kolik centimetrů se předpověď změní, když je hodnota o obvyklý rozkmit vyšší než průměr. Nejvíc váží Děčín teď (+88 cm) a Praha teď (+49 cm). Oranžová políčka vedle modrých znamenají, že model odečítá starší hodnotu od nové, tedy počítá, jestli voda stoupá.

### Z7 · Je rozliv hydraulický model?

Podklad `grafy/mapbox3_decin.jpg`. Odpovídá Honza.

Není. Porovnáváme výšku terénu (ČÚZK DMR 5G, po 10 cm) s výškou hladiny a zaplavíme to, co je níž a spojené s řekou. Ověřeno proti úřední mapě záplavových území: při pětileté vodě náš rozliv 167 ha, úřední 183 ha, průnik 165 ha, shoda 0,89. Zdi a hráze pod rozlišením terénu nevidí.
