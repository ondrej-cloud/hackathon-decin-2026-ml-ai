# Přehled řešení: Labe

Stav k pá 20:30. Na jednom místě: co předpovídáme, z čeho, co jsme nevzali, jak měříme, výsledky a všechna rozhodnutí. Podrobnosti jsou v odkazovaných souborech. Kdo něco rozhodne nebo změní, doplní to sem i do `docs/DENIK.md`.

## Úloha

Předpovídáme výšku hladiny Labe v cm na vodočtu **Děčín** a zvlášť **Ústí nad Labem** za **12, 24 a 36 hodin**. Z předpovědi poznáme, jestli a kdy voda překročí 2. nebo 3. stupeň povodňové aktivity. Pro město a lidi u řeky to znamená varování den předem místo ve chvíli, kdy voda už stoupá.

Pracovní název prezentace: „Co teče v Praze, bude zítra v Děčíně“.

## Data

Otevřená data ČHMÚ, hodinová hladina a průtok, 2006–2025, 12 stanic (`data/external/labe_hodinove.parquet`, podrobně `docs/DATA.md`, sekce Labe). Inventura všech dat, co z balíčku používáme a proč: `docs/ZDROJE_DAT.md`. Za 2024–2025 jsou na hodinu i na centimetr stejná jako balíček od pořadatelů. Balíček sám nestačí: nejvýš proti proudu má Ústí (4 h před Děčínem) a jedinou povodeň.

## Vstupy modelů (faktory)

**Společná tabulka pro všechny** (`src/features.py`, 98 sloupců, jen to, co je v okamžiku předpovědi už změřené):

| Faktor | Stanice | Kolik hodin zpátky |
|---|---|---|
| hladina (cm) | Děčín, Ústí | 0, 1, 2, 3, 6, 12, 24 |
| průtok (m³/s) | Děčín, Ústí, Louny (Ohře), Mělník, Vraňany (Vltava), Kostelec (Labe), Praha-Chuchle (Vltava), Nymburk (Labe), Předměřice (Jizera), Beroun (Berounka), Nespeky (Sázava), Přelouč (Labe) | 0, 3, 6, 12, 18, 24, 36 |

**Co si z toho bere každý model:**

| Model | Vstupy | Úpravy |
|---|---|---|
| lineární regrese (`ridge`) | všech 98 sloupců | odmocnina průtoků, škálování |
| neuronová síť (`mlp`) | všech 98 sloupců | odmocnina průtoků, škálování; učí se změnu hladiny |
| LightGBM (`lgbm`) | hladina v cíli; ke každé stanici průtok, který do cíle doteče za h hodin (posunutý o změřenou dobu doběhu), a o kolik se liší od toho, co dotéká teď; roční období (den v roce); trend hladiny za 6 h | učí se změnu hladiny |
| fyzikální (`fyzika`) | průtok v cíli teď, průtoky ve třech branách (Vraňany, Kostelec, Louny), a když voda ještě nedotekla ani k bráně, stanice nad nimi (Praha, Beroun, Sázava, Nymburk, Jizera, Přelouč) | doba putování z korelace změn průtoku, měrná křivka průtok → hladina |

**Co ve vstupech není a proč:**

| Nevzali jsme | Proč |
|---|---|
| srážky, teplota, sníh | balíček má počasí jen 2024–2026. ČHMÚ má denní srážky, výšku sněhu a API30 od 1946 (ověřeno), hodinové až od 2018. Největší rezerva, viz Další kroky. Proč nestačí zbytek učebnicových faktorů: `docs/POROZUMENI.md` |
| přítoky v kraji (Bílina, Ploučnice) | vyzkoušeno, na validaci nepomohly (o 0,2–0,5 cm horší). Doteče z nich za pár hodin a přidají 2–13 % vody |
| hladiny stanic proti proudu | hladina je místní (koryto, jezy), průtok se mezi stanicemi sčítá |
| Zbraslav, Žatec, Kadaň, Karlovy Vary, Litoměřice, Hřensko | skoro totéž co jiná stanice, data až od 2017, nebo leží pod Děčínem |
| roky 2002–2005 a 2026 | chybí stanice proti proudu |
| teplota vody, vypouštění přehrad | s povodní souvisí málo / data nejsou volně |

## Rozdělení a vyhodnocení

`src/evaluate.py`, dělení v čase:
- **train:** 2006–2018 bez validačních povodní a 20 dní kolem nich,
- **val:** povodně 4/2006, 3/2009, 9/2010, 1/2011 a klidné roky 2019–2020. Na nich se ladí a porovnává.
- **test:** 2021–2025 (povodně 2/2021, 12/2023, 2/2024, 9/2024). Spuštěn jednou pá 21:00 po výběru modelu, výsledky níž.

Hlavní číslo je průměrná chyba hladiny během povodní (`mae_povodne`, průměr přes 6 kombinací cíle a horizontu). K tomu varování před 2. a 3. stupněm (předstih, propásnuté povodně, plané poplachy), podíl předpovědí do ±20 cm a bias. Laťka je „bude jako teď“ (hladina za h hodin = hladina teď). Nezávislá kontrola řetězce dopadla „platí“.

## Výsledky na validaci

| Model | Chyba na povodních | Menší než „jako teď“ | Do ±20 cm (12 / 24 / 36 h) | Zachycené povodně | Plané poplachy |
|---|---|---|---|---|---|
| lineární regrese (Honza) | 17,1 cm | 61 % | 88 / 76 / 51 % | 24 z 24 | 0 |
| neuronová síť (Ondra) | 17,8 cm | 60 % | 90 / 64 / 49 % | 24 z 24 | 1 |
| LightGBM (Dan) | 23,1 cm | 49 % | 85 / 61 / 37 % | 24 z 24 | 0 |
| fyzikální (Tobias) | 24,8 cm | 44 % | 76 / 53 / 35 % | 24 z 24 | 0 |
| „bude jako teď“ | 44,3 cm | 0 % | 51 / 23 / 13 % | 0 z 24 | 0 |

**Finální test 2021–2025** (model vybraný předem, natrénovaný na všem do 2020):

| Model | Chyba na povodních | Menší než „jako teď“ | Do ±20 cm (12 / 24 / 36 h) | Zachycené povodně | Plané poplachy |
|---|---|---|---|---|---|
| **lineární regrese (finální)** | **22,4 cm** | **55 %** | 89 / 67 / 43 % | 17 z 21 (propásnuté jsou hraniční o pár cm) | 3 |
| neuronová síť | 21,3 cm | 59 % | 94 / 71 / 44 % | 20 z 21 | 2 |
| LightGBM | 24,0 cm | 54 % | 91 / 67 / 41 % | 21 z 21 | 4 |
| fyzikální | 27,1 cm | 45 % | 80 / 64 / 38 % | 21 z 21 | 2 |
| „bude jako teď“ | 50,2 cm | 0 % | 57 / 32 / 20 % | 0 z 21 | 0 |

**Finální model na testu podrobně** (lineární regrese, 2021–2025; povodně = 7 dní před vrcholem až 5 po; klid = hladina pod 1. stupněm; do ±cm a % výšky jen při vodě nad 1. stupněm, 1 061 h v Děčíně a 857 h v Ústí; předstih je průměr a propásnutá povodeň se počítá jako 0):

| Stanice | Za | Chyba na povodních | „Jako teď“ | Menší o | Chyba v klidu | Do ±10 / ±20 / ±30 cm | Chyba v % výšky | Bias | Chyba vrcholu | 2. stupeň: zachyceno, předstih, plané poplachy | 3. stupeň: zachyceno, předstih |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Děčín | 12 h | 10,2 cm | 23,3 cm | 56 % | 5,0 cm | 70 / 91 / 97 % | 1,8 % | −2,7 cm | 13,1 cm | 3 z 4, 5 h, 0 | 3 z 3, 11 h |
| Děčín | 24 h | 17,5 cm | 44,8 cm | 61 % | 7,1 cm | 45 / 70 / 87 % | 3,2 % | −10,5 cm | 21,4 cm | 3 z 4, 12 h, 1 | 3 z 3, 21 h |
| Děčín | 36 h | 29,9 cm | 65,5 cm | 54 % | 10,2 cm | 25 / 46 / 64 % | 6,2 % | −21,7 cm | 21,6 cm | 3 z 4, 14 h, 1 | 3 z 3, 27 h |
| Ústí | 12 h | 14,7 cm | 29,3 cm | 50 % | 5,8 cm | 60 / 87 / 94 % | 2,0 % | −3,0 cm | 21,6 cm | 2 z 3, 7 h, 0 | 3 z 3, 12 h |
| Ústí | 24 h | 24,0 cm | 56,2 cm | 57 % | 8,1 cm | 34 / 63 / 80 % | 3,6 % | −13,2 cm | 22,1 cm | 3 z 3, 19 h, 0 | 3 z 3, 19 h |
| Ústí | 36 h | 38,1 cm | 81,8 cm | 53 % | 11,1 cm | 23 / 40 / 55 % | 6,2 % | −26,6 cm | 25,0 cm | 3 z 3, 21 h, 1 | 3 z 3, 22 h |

Vrcholy testových povodní na 24 h (Děčín 2/2024, 12/2023, 9/2024): o 10, 17 a 38 cm níž. Propásnutý 2. stupeň v Děčíně je únor 2024 (vrchol 496 cm, hranice 490), v Ústí Vánoce 2023 o 2 cm.

Povodeň Boris 9/2024 v Děčíně: 3. stupeň hlášen 27 h předem (předpověď na 24 h), vrchol 649 cm předpovězen na 611 cm. Grafy `docs/grafy/srovnani_procenta_test.png`, `povoden_2024-09_decin_24h.png`, `povoden_2023-12_decin_24h.png`.

Grafy validace: `docs/grafy/srovnani_procenta.png`, `srovnani_ctyr_modelu.png`, `povoden_2011-01_decin_24h.png`, `povoden_2006-03_decin_36h.png`. Jak čísla číst a jestli jsou dobrá: `docs/POROZUMENI.md`, sekce Jak číst výsledky.

## Rozhodnutí a proč

| Kdy | Rozhodnutí | Proč |
|---|---|---|
| pá 17:10 | zvažovali jsme Ovzduší | tři pojetí, ale bez tak silného a ověřitelného výsledku |
| pá 17:33 | Labe s daty ČHMÚ proti proudu | z balíčku jde vidět jen pár hodin dopředu a nejde nic ověřit (jediná povodeň) |
| pá 17:33 | vyřadit chybná data v Děčíně 5.–8. 2. 2006 | hladina 1 019 cm při průtoku 120 m³/s, pak hladina nesedí s průtokem (led) |
| pá 17:46 | lineární model jako první kandidát | na 6 povodních poloviční chyba, LightGBM nepředpoví vrchol nad rámec tréninku (2013: 823 místo 1 072 cm) |
| pá 18:00 | vybraná úloha Labe | měřitelný přínos, fyzikálně vysvětlitelné, jasný uživatel |
| pá 18:36 | stanice na všech třech větvích a v několika vzdálenostech | čím dál dopředu předpovídáme, tím dál proti proudu se musíme dívat |
| pá 18:44 | historie i stanice proti proudu, ne jen balíček | stanice proti proudu pomohly víc než historie, historie je nutná k ověření |
| pá 18:52 | rovnou Labe, ne malé řeky; čtyři modely, každý jiný | na malých řekách rozhoduje déšť, je to jiný problém |
| pá 19:17 | společné vstupy, rozdělení a vyhodnocení pro všechny | jinak by výsledky nešly srovnat |
| pá 19:17 | validace na vynechaných povodních, ne na posledních letech | 2016–2020 nebyla žádná povodeň |
| pá 19:17 | zpoždění 0–36 h, horizonty 12, 24, 36 h | nejvzdálenější stanice ~40 h od Děčína; dál bez srážek nevidíme |
| pá 19:30 | data zkontrolovaná, nic dalšího se nemaže | bilance vody, měrné křivky i časy sedí; povodně nejsou odlehlé hodnoty |
| pá 19:30 | pravidla iterace: jedna změna s důvodem, zlepšení aspoň o 1 cm, konec po 3 neúspěších | validace má jen 4 povodně, nekonečné ladění by našlo náhodu |
| pá 19:40 | přítoky v kraji do modelu nepřidávat | na validaci nepomohly |
| pá 20:00 | opravy vyhodnocení po nezávislé kontrole | povodeň vypadla z varování u 36 h, nadhodnocování zlepšovalo předstih, staré a nové výsledky se míchaly |
| pá 20:00 | všechny modely přepočítat na jednom počítači | srovnání na stejné verzi kódu a dat |
| pá 20:20 | průměr dvou modelů nepoužít | zlepšení 0,2 cm, jen složitost navíc |
| pá 20:44 | trénovat na celé historii a se všemi stanicemi (Honza) | 2 roky jen z kraje jako balíček: 44,6 cm a 12 z 24 propásnutých, stejně špatné jako „jako teď“; stanice proti proudu pomáhají víc než roky, historie s povodní 2013 odstraní propásnutá varování (`docs/grafy/kolik_dat.png`) |
| pá 20:44 | srážky, sníh a teplotu do modelu nepřidávat | lineární regrese 17,1 → 17,4 cm, síť 17,8 → 21,2 cm; ani dokonalá předpověď srážek na den dopředu nepomůže o víc než 0,8 cm |
| pá 20:58 | **finální model lineární regrese**, zapsáno před testem | nejlepší na validaci, nejjednodušší, všechny pokusy o zlepšení pod 1 cm |
| pá 21:00 | test 2021–2025 spuštěn jednou | 22,4 cm, o 55 % méně než „jako teď“; síť o 1,1 cm lepší, výběr podle testu neměníme |
| pá 20:20 | návrh: finální model lineární regrese | nejlepší, nejjednodušší, bez planých poplachů, každá váha jde vysvětlit; síť je stejná jen v rámci náhody |

## Další kroky a otevřené otázky

- Test hotový (pá 21:00). Model pro aplikaci přetrénovat na všech datech do 2025 (`src/uloz_model.py` teď trénuje jen na train).
- Srážky, sníh a teplota: vyzkoušeno, nepomohlo (pá 20:44). Honza: kolik let dat (hotovo, pá 20:44, `docs/grafy/kolik_dat.png`). Dan zkouší dobu putování podle průtoku (do 22:00).
- Otázka pro mentory: s jakým zpožděním jsou hodinová data ČHMÚ v provozu dostupná? Zkrátil by se o něj předstih.
- Limity do prezentace: bez srážek nejde dál než den a půl, povodně z dešťů v kraji (8/2010) model nevidí, archivní data jsou zpětně ověřená (v provozu předběžná), validace má jen 4 povodně.
- Aplikace (Honza) a prezentace (Tobias) podle Stavu v `CLAUDE.md`.
