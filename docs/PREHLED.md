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
- **test:** 2021–2025 (povodně 12/2023 a 9/2024). Pustí se jednou na finální model, zatím **nespuštěn**.

Hlavní číslo je průměrná chyba hladiny během povodní (`mae_povodne`, průměr přes 6 kombinací cíle a horizontu). K tomu varování před 2. a 3. stupněm (předstih, propásnuté povodně, plané poplachy), podíl předpovědí do ±20 cm a bias. Laťka je „bude jako teď“ (hladina za h hodin = hladina teď). Nezávislá kontrola řetězce dopadla „platí“.

## Výsledky na validaci

| Model | Chyba na povodních | Menší než „jako teď“ | Do ±20 cm (12 / 24 / 36 h) | Zachycené povodně | Plané poplachy |
|---|---|---|---|---|---|
| lineární regrese (Honza) | 17,1 cm | 61 % | 88 / 76 / 51 % | 24 z 24 | 0 |
| neuronová síť (Ondra) | 17,8 cm | 60 % | 90 / 64 / 49 % | 24 z 24 | 1 |
| LightGBM (Dan) | 23,1 cm | 49 % | 85 / 61 / 37 % | 24 z 24 | 0 |
| fyzikální (Tobias) | 24,8 cm | 44 % | 76 / 53 / 35 % | 24 z 24 | 0 |
| „bude jako teď“ | 44,3 cm | 0 % | 51 / 23 / 13 % | 0 z 24 | 0 |

Grafy: `docs/grafy/srovnani_procenta.png`, `srovnani_ctyr_modelu.png`, `povoden_2011-01_decin_24h.png`, `povoden_2006-03_decin_36h.png`. Jak čísla číst a jestli jsou dobrá: `docs/POROZUMENI.md`, sekce Jak číst výsledky.

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
| pá 20:20 | **návrh: finální model lineární regrese** (čeká na potvrzení) | nejlepší, nejjednodušší, bez planých poplachů, každá váha jde vysvětlit; síť je stejná jen v rámci náhody |

## Další kroky a otevřené otázky

- Potvrdit finální model, pak jednou pustit test 2021–2025 (Ondra).
- Srážky, sníh a teplota: vyzkoušeno, nepomohlo (pá 20:44). Honza: kolik let dat (hotovo, pá 20:44, `docs/grafy/kolik_dat.png`). Dan zkouší dobu putování podle průtoku (do 22:00).
- Otázka pro mentory: s jakým zpožděním jsou hodinová data ČHMÚ v provozu dostupná? Zkrátil by se o něj předstih.
- Limity do prezentace: bez srážek nejde dál než den a půl, povodně z dešťů v kraji (8/2010) model nevidí, archivní data jsou zpětně ověřená (v provozu předběžná), validace má jen 4 povodně.
- Aplikace (Honza) a prezentace (Tobias) podle Stavu v `CLAUDE.md`.
