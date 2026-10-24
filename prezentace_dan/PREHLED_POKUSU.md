# Přehled všech pokusů (tým + Dan)

Chyba = průměrná chyba hladiny během povodní v cm. **val** = validace (4 vynechané povodně 2006–2011 + klidné 2019–2020),
průměr přes Děčín a Ústí × 12 / 24 / 36 h (`prumer_povodne`), pokud není napsáno jinak. **D24** = jen Děčín +24 h.
**CV** = časová CV v tréninku (18 povodní), **LOFO** = 22 povodní 2006–2020, každá jednou vynechaná. Laťka „bude jako
teď“: val 44,3, D24 44,4. Zlepšení platí až od 1 cm. Test 2021–2025 se pustil jen jednou (pá 21:00).

| # | Co | Proč | Výsledek | Rozhodnutí | Zdroj |
|---|---|---|---|---|---|
| 1 | „bude jako teď“ | laťka, každý model ji musí porazit | val 44,3; D24 44,4; nevaruje před žádnou povodní | základ srovnání | PREHLED |
| 2 | lineární model na 6 povodních (před splitem) | jde předpovídat ze stanic proti proudu? | D24 29,6 proti 58,7; LightGBM vrchol 2013 823 místo 1 072 cm | lineární model první kandidát | CESTA §1 |
| 3 | brány proti proudu (Ústí) | jak daleko proti proudu se dívat | Ústí +36 h: jen Ústí 74,2, se vzdálenými stanicemi 36,8 | čím dál dopředu, tím dál proti proudu | CESTA §1 |
| 4 | balíček × historie × stanice proti proudu | stačí data z balíčku? | D24: kraj 2 roky 43,0; + proti proudu 2 roky 28,2; kraj 20 let 38,3; obojí 24,3 | archiv ČHMÚ 2006–2025 a 12 stanic | CESTA §1 |
| 5 | malé řeky v kraji | jiná úloha? | voda doteče za 0–7 h, rozhoduje déšť | odloženo | CESTA §1 |
| 6 | **lineární regrese (Ridge), Honza** | vážený součet 98 vstupů, odmocnina průtoků | val **17,1** (alpha 0,1–100: 17,1–17,5; cíl změna 17,1; stanice podle horizontu 17,6) | **finální model** | CESTA §2 |
| 7 | neuronová síť (MLP), Ondra | umí zakřivené vztahy | 64-32: 26,0 (přeučená: starší rozbor D24 při velké vodě, trénink 5 / validace 22 cm); 128-64: **17,8**; váhy na povodně 18,2 | stejná jen v rámci náhody | CESTA §2 |
| 8 | LightGBM, Dan | stromy bývají na tabulkách nejsilnější | 98 syrových vstupů 66,8 (stav) / 40,8 (změna); průtoky posunuté o dobu doběhu 24,3; + sezóna a trend **23,1**; proti přeučení 22,1–23,8; přímky v listech 97,8; oprava zbytku po Ridge 18,7 | stromy neumí výš, než viděly | POKUSY pá 19:45–20:15 |
| 9 | fyzikální model, Tobias | co řekne fyzika skoro bez učení | val **24,8** | srovnávací základ | CESTA §2 |
| 10 | nezávislá kontrola řetězce | únik dat, chyby vyhodnocení | okno 16 dní, předstih ≤ horizont, bias, bez doplňování děr, otisk verze | vše přepočítáno | CESTA §3 |
| 11 | průměr regrese + síť | dvě hlavy víc ví | 16,9 proti 17,1 | ne, jen složitost | CESTA §4 |
| 12 | přítoky v kraji (Bílina, Ploučnice) | voda mezi Ústím a Děčínem | o 0,2–0,5 cm horší | ne | PREHLED |
| 13 | doba doběhu podle průtoku, Dan | vlna se při povodni zpomalí | LightGBM 23,1 beze změny; Ridge se stejnými vstupy 21,8 proti 22,2 | ne; nad 1 500 m³/s je v tréninku jen 6/2013 | POKUSY pá 20:45 |
| 14 | srážky, sníh, teplota (25 stanic), Ondra | povodně dělá déšť | regrese 17,1 → 17,4; síť 17,8 → 21,2 | ne | PREHLED |
| 15 | kolik let dat, Honza | potřebujeme historii? | jako balíček (2 roky, jen kraj, napodobeno na 2017–2018) 44,6 a propásnutých 12 z 24 varování; 8 a 13 let 16,6 a 17,1 | celá historie a všechny stanice | CESTA §4 |
| 16 | větší váha povodňových hodin, Honza | víc se učit na povodních | 17,2 a 18,5 | ne | CESTA §4 |
| 17 | nejistota (rozmezí), Honza | jak moc předpovědi věřit | na povodních uvnitř rozmezí 76–88 % (cíl 90 %) | v aplikaci jako „nejspíš od–do“ | POKUSY pá 20:40 |
| 18 | **finální test 2021–2025** (jednou) | nezávislé ověření | regrese **22,4** proti 50,2 (o 55 % méně); síť 21,3; LightGBM 24,0; fyzika 27,1; Boris 3. stupeň 27 h předem | výběr podle testu neměníme | PREHLED |
| 19 | dokonalá předpověď deště (dnes / 3 dny) | horní mez přínosu srážek | 17,1 → 16,3 / 16,1, varování nepřišlo dřív | srážky na 12–36 h nepomáhají | CESTA §6 |
| 20 | srážky na 12–72 h | kdy déšť pomůže | dešťová 9/2010 s dokonalou předpovědí −23 % na 36 h, −40 % na 72 h; naměřené nic | jen do „co dál“ | CESTA §6 |
| 21 | voda ve sněhu, zimní model | tání sněhu | celoročně 17,8; zimní model 18,9 proti 15,6 na zimních povodních | ne | CESTA §6 |
| 22 | **vícenásobná validace** (8 povodní) | nebyla validace šťastná? | regrese 20,1 ± 7,7; síť 21,0; LightGBM 22,7; fyzika 26,7; „jako teď“ 45,2 | výběr potvrzen (o 55 % méně) | PREHLED |
| 23 | polynomická regrese 2. stupně | zakřivení | 19,9 a 22,8 | ne, ohne se špatně | CESTA §6 |
| 24 | prudký vzestup / horní mez nejistoty | dřív varovat | 17,0; varování o 3–4 h dřív, ale 4 plané poplachy | ne / předběžná výstraha | CESTA §6 |
| 25 | další stanice (horní Ohře, Zbraslav) | delší náskok | s horní Ohří val 17,4, vícenásobná 19,7; i se Zbraslaví vícenásobná 19,9 | smíšené, pod 1 cm | CESTA §6 |
| 26 | spojení všech malých zlepšení | sečtou se? | val 17,2, vícenásobná 19,3 | ne | CESTA §6 |
| 27 | konvoluční síť po čase (TCN), Honza | ať si síť vybere hodiny sama | val 20,3, 3 propásnutá varování, trénink 16 min | ne; naučila se skoro stejné váhy jako regrese | POKUSY so 0:45 |
| 28 | přeučuje se regrese?, Ondra | kontrola | D24 trénink 19,7 / val 15,5 (bez regularizace stejně) | obvyklý znak přeučení nemá | POKUSY so 0:48 |
| 29 | **Danův Ridge, 30 stanic** (dan-ridge) | stanice, které vidí vlnu dřív | D24: CV 14,2 / 15,6; val 17,8 / 15,5 (povodeň 2006); test (jednou) 16,1 / 17,5, „jako teď“ 44,8; začátek vzestupu test 27,0 / 32,0 | nejslibnější směr, výsledek smíšený | ridge_dan/ZPRAVA |
| 30 | 18 nových stanic u všech modelů (Dan; fyzika zapojí jen 8) | pomůžou každému? | CV D24: Ridge −1,5, LightGBM −2,0, fyzika −0,7, síť −0,5; začátek vzestupu na val o 5–8 cm lépe u všech | pomáhají hlavně začátku vzestupu | STANICE_VSEM, SIT_VARIANTY |
| 31 | **LOFO-CV 22 povodní** (Dan) | přísnější hodnocení | D24: týmový Ridge 15,29; Ridge 30 14,79; **G3 = ½ Ridge 30 + ½ LightGBM 30: 13,94 (−1,35, lepší 20 z 22)**, ale val 18,2 / 15,5; D36: Ridge 30 23,96 / 26,39 (−2,43, 17 z 22) | finále týmový Ridge, G3 ukázat jako ověřené zlepšení | ridge_dan/ZLEPSENI |
| 32 | G3 ve vícenásobné validaci (Dan) | druhý pohled | 19,6 ± 7,1 proti 20,1 ± 7,7, lepší 6 z 8 (p ≈ 0,29) | není průkazné, finále nemění | VALIDACE_ONDRA |
| 33 | 6h srážky ze SYNOP (NOAA ISD), Dan | srážky známé dřív než denní | LOFO: oba Ridge do 0,1 cm, LightGBM −0,5 (13 z 22); CV LightGBM −0,96 | beze změny, nepoužít | ZPRAVA_SRAZKY |
| 34 | síť s 18 stanicemi / se srážkami na Kaggle (Dan) | platí to i pro síť? | CV −0,5 / +0,4; LOFO D24 +0,98 (stanice); začátek vzestupu −5,7 / −2,9 | beze změny | SIT_VARIANTY |
| 35 | rozhodnutí o nových stanicích pro 24 h (Dan, so 3:30) | G3 vs týmová regrese ve třech hodnoceních | val D24: regrese 15,5, síť 18,4, G3 18,2, Ridge 30 17,8; vícenásobná: G3 19,6 (−0,5, 6 z 8); LOFO D24: G3 13,94 (−1,35, 20 z 22), síť 15,07 | 24 h zůstává týmová regrese | ridge_dan/ROZHODNUTI_G3 |
| 36 | 36 h s 30 stanicemi a H30 (Dan) | delší náskok vzdálených stanic | Ridge 30: vícenásobná Děčín −0,71, Ústí −1,00 (na hraně, 5 z 8), LOFO D36 −2,43 (17 z 22); H30 (průzkumně, + útlum v nivě): vícenásobná −2,1 / −2,3 (6 z 8), LOFO D36 −3,44 (18 z 22), val D36 25,0 / 26,0; na 24 h nic | pro 36 h rozhodne tým (regrese, Ridge 30, nebo H30 s výhradou) | ridge_dan/ROZHODNUTI_G3, RANNI_ZPRAVA |
| 37 | pásmo nejistoty z chyb mimo trénink (Dan) | dnešní pásmo je z tréninku, na povodních moc úzké | vnořeně na 22 povodních: 90% pásmo v aplikaci 72–83 % (80% stejnou metodou 58–72 %), nové 78–80 % a 94–95 % (cíl 80 / 95 %); rychlý vzestup 59–72 %, rekord 6/2013 42 %; šířka 80 % D24: regrese 47, G3 43 cm | připravené jako patch, rozhodne tým | nejistota_dan/ZPRAVA_NEJISTOTA |
| 38 | revize aplikace před demem (Dan) | co může shodit demo | 2 kritické (bez internetu prázdná mapa a animace; Dnešek na špatné Wi-Fi zamrzne), 6 vysokých (text u Borise „model do 2018“, popisek testu, DIBAVOD × DMR, pásmo…); 10 patchů (bezpečné 02, 03, 04, 05, 07, 08); se všemi test 9 z 9, s 01–09 i Dneškem 10 z 10 | aplikace v main beze změny, patche k rozhodnutí | nejistota_dan/REVIZE_APLIKACE |
| 39 | provozní test na živých datech ČHMÚ (Dan, so 5:53) | jak by to fungovalo dnes naživo | data ČHMÚ chodí po 20 min, poslední hodnota stará 10–20 min, celá hodina u všech 30 stanic venku do HH:40; doplnit chybějící poslední hodinu poslední hodnotou zhorší LOFO D24 o 1,8 cm (15,29 → 17,08), při 3 h o 7,0 cm; živě 29 dní nízkého stavu (do 23. 10. 2026): ČHMÚ D24 5,0 cm, náš model 7,5, „jako teď“ 5,0 | počítat v HH:45 z okamžitých hodnot do HH:00 (aplikace bere hodinový průměr, sladit); při nízké vodě naše předpověď kmitá, ČHMÚ je přesnější | ridge_dan/PROVOZ |

Zdroje: `docs/PREHLED.md`, `docs/CESTA_MODELU.md`, `docs/POKUSY.md` (main); `ridge_dan/ZPRAVA.md`, `STANICE_VSEM.md`,
`ZLEPSENI.md`, `VALIDACE_ONDRA.md` (větev dan-ridge); `srazky_dan/ZPRAVA_SRAZKY.md` (dan-srazky);
`sit_dan/SIT_VARIANTY.md` (dan-sit); `ridge_dan/ROZHODNUTI_G3.md`, `RANNI_ZPRAVA.md` (dan-ridge, so 3:30);
`nejistota_dan/ZPRAVA_NEJISTOTA.md`, `REVIZE_APLIKACE.md`, `RANNI_ZPRAVA.md` (dan-nejistota, so 4:46); `ridge_dan/PROVOZ.md` (dan-ridge, so 5:53).

**Jedna věta pro porotu:** čtyři úplně různé modely skončily na validaci na 17–25 cm a žádný další proveditelný pokus
nepřekonal finální regresi (17,1) aspoň o 1 cm (o 1,0 cm jen dokonalá předpověď deště na 3 dny, která v provozu neexistuje). Výsledky tedy naznačují, že strop dělá informace ve vstupech, ne model. Přísným LOFO prošla na D24 jen směs G3 (−1,35 cm) a na D36
Ridge s 30 stanicemi (−2,43 cm), na validaci jsou ale obě horší. Na začátku vzestupu pomáhají hlavně stanice dál proti
proudu (o 5–8 cm), méně i srážky (o 1,9–4,6 cm podle modelu), na celkovou chybu to nestačí.
