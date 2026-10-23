# Cesta modelu: od čtyř nápadů k lineární regresi

Celý postup na jednom místě, v pořadí, jak šel. Čísla jsou chyba hladiny na povodních v cm, průměr přes Děčín a Ústí a 12, 24 a 36 h (`prumer_povodne`), pokud není napsáno jinak. Podrobnosti ke každému kroku jsou v `docs/POKUSY.md` (pokusy) a `docs/DENIK.md` (rozhodnutí), přehled tabulek v `docs/PREHLED.md`.

## 1. Než vznikl první model (pá 17:30–19:15)

Úloha: předpovědět hladinu Labe v Děčíně a Ústí za 12, 24 a 36 h a včas varovat před 2. a 3. stupněm povodňové aktivity.

Než jsme cokoli trénovali, ověřili jsme si, kde je informace:
- **17:46, lineární model na šesti povodních** (Děčín +24 h): 29,6 cm proti 58,7 cm u „bude jako teď“. LightGBM přitom u povodně 2013 předpověděl vrchol 823 místo 1 072 cm, stromy neumí výš, než viděly. Lineární model byl od začátku první kandidát.
- **18:36, stanice proti proudu podle horizontu**: čím dál dopředu předpovídáme, tím vzdálenější stanice jsou potřeba (Ústí +36 h: jen Ústí 74,2 cm, se vzdálenými stanicemi 36,8 cm).
- **18:44, balíček proti historii a stanicím proti proudu** (Děčín +24 h): jen kraj 2 roky 43,0 cm, kraj a proti proudu 2 roky 28,2, kraj 20 let 38,3, kraj a proti proudu 20 let 24,3 cm. Stanice proti proudu pomohly víc než historie, historie je ale nutná k ověření (v balíčku je jediná povodeň).
- **18:52, malé řeky v kraji**: dá se jen pár hodin dopředu a rozhoduje déšť. Odloženo.

**Společný základ (19:15)**, aby šly modely srovnat:
- data: hodinový archiv ČHMÚ 2006–2025, hladina Děčína a Ústí a průtok 12 stanic (`data/external/labe_hodinove.parquet`),
- vstupy: 98 sloupců, hladiny teď a před 1–24 h, průtoky teď a před 3–36 h (`src/features.py`),
- rozdělení v čase: trénink 2006–2018, validace 4 vynechané povodně (4/2006, 3/2009, 9/2010, 1/2011) a 2019–2020, test 2021–2025 jednou na konci (`src/evaluate.py`),
- metrika: chyba na povodních, předstih varování, propásnuté povodně, plané poplachy,
- laťka „bude jako teď“: 44,3 cm. Každý model ji musí porazit.

## 2. Čtyři modely, každý jiný (pá 19:15–20:15)

Proč čtyři: od nejjednoduššího ke složitému a každý na jiném principu. Kdyby vyhrál složitý, víme, že je co se učit. Kdyby jednoduchý, víme, že složitost nepomáhá. Každý si vzal jeden a ladil ho podle stejných pravidel: jedna změna s důvodem, zlepšení aspoň o 1 cm, po třech neúspěších konec (`docs/UKOL_MODELY.md`).

| Model | Kdo | Jak funguje | Varianty na validaci | Nejlepší |
|---|---|---|---|---|
| lineární regrese (Ridge) | Honza | vážený součet 98 vstupů, průtoky pod odmocninou | v1 17,1; síla regularizace 0,1–100: 17,1–17,5; cíl jako změna hladiny 17,1; stanice podle horizontu 17,6. Tři neúspěchy, konec | **17,1** |
| neuronová síť (MLP) | Ondra | dvě vrstvy neuronů, cíl změna hladiny | 64-32: 26,0 (přeučená, na tréninku 5 cm, na validaci 22 cm); silnější regularizace 18,7; větší síť 128-64: 17,8; váhy na povodně 18,2 | 17,8 |
| LightGBM | Dan | stovky rozhodovacích stromů | ze zadání 66,1 a 40,9 (stromy si pamatují povodně z tréninku); průtoky posunuté o dobu doběhu 24,0 a 22,8; proti přeučení 22,2–23,8; oprava zbytku po Ridge 18,9, ale horší než samotný Ridge | 22,8 |
| fyzikální | Tobias | doby putování vody ze tří větví a měrná křivka | první běh 24,1 (Děčín +24 h), třetí vrstva stanic prošla | 24,8 |

## 3. Kontrola řetězce (pá 20:00)

Nezávislá kontrola úniku dat a vyhodnocení našla chyby ve společném kódu. Opravili jsme je dřív, než jsme modely srovnávali:
- validační okno 16 dní, jinak u Děčína +36 h vypadla povodeň 2006 z varování,
- předstih varování nejvýš tak dlouhý jako horizont a přibyla soustavná chyba (bias), protože nadhodnocování uměle zlepšovalo předstih,
- žádné doplňování děr, bralo hodnotu z budoucnosti,
- výsledky si ukládají otisk verze dat a kódu, staré se s novými nemíchají.

Všechny modely jsme pak přepočítali na jednom počítači.

## 4. Srovnání a výběr (pá 20:15–20:58)

| Model | Chyba na povodních | Menší než „jako teď“ | Zachycené povodně | Plané poplachy |
|---|---|---|---|---|
| lineární regrese | 17,1 | 61 % | 24 z 24 | 0 |
| neuronová síť | 17,8 | 60 % | 24 z 24 | 1 |
| LightGBM | 23,1 | 49 % | 24 z 24 | 0 |
| fyzikální | 24,8 | 44 % | 24 z 24 | 0 |
| „bude jako teď“ | 44,3 | 0 % | 0 z 24 | 0 |

Před rozhodnutím jsme ještě zkusili:
- průměr regrese a sítě: 16,9, o 0,2 cm, jen složitost navíc,
- doba doběhu podle průtoku (Dan): LightGBM 23,1, regrese 21,8, nepomohlo,
- srážky, sníh a teplota z 25 stanic: 17,4, nepomohly,
- kolik let dat (Honza): 8 a 13 let 16,6 a 17,1, 2 roky jen z kraje jako v balíčku 44,6 cm a 12 z 24 propásnutých,
- větší váha povodňových hodin (Honza): 17,2 a 18,5,
- interval nejistoty (Honza): na povodních se do něj vejde 8 z 10 hodnot, je v aplikaci.

**Rozhodnutí v 20:58, zapsané před testem**: finální model je lineární regrese. Nejlepší na validaci, nejjednodušší, bez planých poplachů a každá váha jde ukázat a vysvětlit. Síť je stejně dobrá jen v rámci náhody.

## 5. Finální test 2021–2025 (pá 21:00)

Jednou, na model vybraný předem, natrénovaný na všem do 2020:

| Model | Chyba na povodních | Menší než „jako teď“ |
|---|---|---|
| **lineární regrese (finální)** | **22,4** | **55 %** |
| neuronová síť | 21,3 | 59 % |
| LightGBM | 24,0 | 54 % |
| fyzikální | 27,1 | 45 % |
| „bude jako teď“ | 50,2 | 0 % |

Na testu je chyba větší než na validaci, ale i „jako teď“ je horší (testové povodně stoupaly rychleji), zlepšení proti laťce je podobné. Před 3. stupněm model varoval pokaždé, povodeň Boris 9/2024 hlásil 27 h předem. Síť vyšla o 1,1 cm lépe, výběr jsme podle testu neměnili. Test se už znovu nepouští.

## 6. Po testu: ověřování a pokusy jen na validaci (pá 22:29 – so 0:19)

Test zůstal stranou. Ověřovali jsme, jestli výběr nebyla náhoda, a zkoušeli nápady, které by mohly model posunout.

| Kdy | Pokus | Výsledek | Závěr |
|---|---|---|---|
| 22:29 | dokonalá předpověď deště na dnešní den | 17,1 → 16,3 | ani dokonalá předpověď nepomůže o víc než 0,8 cm |
| 22:32 | dokonalá předpověď deště na 3 dny | 17,1 → 16,1, varování nepřišlo dřív | voda z deště doteče do Děčína většinou až za víc než 36 h |
| 22:46 | srážky na 12–72 h | dešťová povodeň 9/2010 s dokonalou předpovědí o 23 % lépe na 36 h a o 40 % na 72 h, zimní povodně ne; naměřené denní srážky nic | předpověď srážek dává smysl na 2–3 dny u dešťových povodní; na trénink chybí historické předpovědi |
| 23:14 | srážky v reálném čase, horní mez | nejvýš o 1 cm | hodinové srážky má ČHMÚ až od 2018 |
| 23:14 | voda ve sněhu, zvláštní zimní model | 17,8; zimní model se sněhem 18,9 proti celoročnímu 15,6 na zimních povodních | zimní model má jen půlku dat, sníh to nevyrovná |
| 23:27 | **vícenásobná validace**: 8 povodní 2006–2020, každá jednou vynechaná | regrese 20,1 ± 7,7, síť 21,0, LightGBM 22,7, fyzikální 26,7, „jako teď“ 45,2; regrese nejlepší na 4 z 8 | výběr nebyl náhoda, zlepšení 56 % jako na testu (55 %) |
| 23:44 | polynomická regrese 2. stupně | 19,9 a 22,8 | při vysoké vodě se křivka ohne špatně |
| 0:01 | „při prudkém vzestupu ještě prudší“ | 17,0, při náběhu o 1 cm lépe | většina vzestupů nepokračuje (jen 22 %), model rozumně sází na průměr |
| 0:01 | varování podle horní meze nejistoty | o 3–4 h dřív, ale 4 plané poplachy | hodí se jako předběžná výstraha, ne jako předpověď |
| 0:19 | další stanice (horní Ohře, Zbraslav) | validace 17,4, vícenásobná 19,7 | smíšeně, pod 1 cm |

Dan na vlastní větvi (`dan-ridge`) postavil regresi s 30 stanicemi. Pro Děčín +24 h vyšla na jeho validaci uvnitř tréninku 14,2 proti 15,6, na testu 16,1 proti 17,5, na naší validaci 17,8 proti 15,5 (kvůli jarní povodni 2006). Je to nejslibnější směr, ale výsledek je zatím smíšený.

## 7. Proč zůstává lineární regrese

- Fyzika je součet: voda v Děčíně je zhruba Vltava + horní Labe + Ohře, každá posunutá o dobu putování. To je přesně tvar lineární regrese a ohyb měrné křivky dostane přes odmocninu průtoků.
- Velkých povodní je málo (v tréninku dvě nad 3. stupněm). Model s 98 vahami se z nich nepřeučí, síť s 21 tisíci vahami a stromy ano.
- Umí předpovědět výš, než kdy viděla. Stromy ne, polynom se ohne špatně.
- Ověřeno třemi způsoby a pokaždé o 55–61 % lepší než „jako teď“: validace, vícenásobná validace přes 8 povodní, test.
- Devět pokusů o zlepšení po testu skončilo pod 1 cm. Rezervu nemá model, ale vstupy: voda, která v řekách ještě není.
- Porota chce model, kterému rozumíme. Tenhle se vejde na jeden obrázek (`docs/grafy/ridge_vahy_decin.png`).

## 8. Co by model posunulo (co dál)

- Předpověď srážek od ČHMÚ pro předpověď na 2–3 dny u dešťových povodní. Na trénink chybí archiv předpovědí, ten má Open-Meteo až od 2021–2022.
- Hodinové srážky v reálném čase, až bude delší archiv (ČHMÚ od 2018).
- Víc stanic proti proudu (Danových 30), ověřit vícenásobnou validací.
- Dvoustupňové varování: předběžná výstraha podle horní meze nejistoty, ostré podle předpovědi.

## Grafy k jednotlivým krokům

- výběr modelu: `srovnani_ctyr_modelu.png`, `srovnani_procenta.png`, `povoden_2011-01_decin_24h.png`
- jak model rozhoduje: `ridge_vahy_decin.png`, `mlp_dulezitost_stanic.png`, `lgbm_shap.png`, `fyzika_merna_krivka.png`
- test: `test_chybovost.png`, `srovnani_procenta_test.png`, `povoden_2024-09_decin_24h.png`
- po testu: `krizova_validace.png`, `jako_ted_vysvetleni.png`, `boris_dest_prutoky_decin.png`, `kolik_dat.png`
