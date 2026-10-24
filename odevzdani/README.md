# Kolik vody přiteče do Děčína a Ústí

Předpověď hladiny Labe ve vodočtech Děčín a Ústí nad Labem na 12, 24 a 36 hodin dopředu a varování před 2. a 3. stupněm povodňové aktivity. Model se učí z průtoků na Vltavě, horním Labi a Ohři, protože voda, která teče Prahou teď, je zhruba za den v Děčíně. Je to pro povodňovou komisi města, hasiče a lidi u řeky: den navíc stačí na odvezení aut, pytle s pískem a vyklizení sklepů.

- Úloha: KSI-3 „Dokážete předpovědět Labe?“, Hackathon ML/AI 2026, FJFI ČVUT Děčín
- Web s předpovědí na dnešek a přehráváním povodní: https://field-zero.netlify.app
- Prezentace: https://field-zero.netlify.app/prezentace/ (texty a grafy i ve složce `prezentace/`)
- Tým: Ondra (vedení, ověřování výsledků, neuronová síť), Dan (LightGBM), Honza (lineární regrese, aplikace, web), Tobias (fyzikální model, prezentace)

## Výsledky v kostce

Finální model je lineární regrese (Ridge) s 98 vstupy. Srovnáváme s nejjednodušší předpovědí „bude jako teď“ (hladina za h hodin = hladina teď).

| Ověření | Na čem | Lineární regrese | „Bude jako teď“ | Chyba menší o |
|---|---|---|---|---|
| validace (výběr modelu) | 4 povodně 2006–2011 a klidné roky 2019–2020 | 17,1 cm | 44,3 cm | 61 % |
| vícenásobná validace | 8 povodní 2006–2020, každá jednou vynechaná | 20,1 ± 7,7 cm | 45,2 cm | 55 % |
| test (jednou na konci) | 2021–2025, povodně 2/2021, 12/2023, 2/2024, 9/2024 | 22,4 cm | 50,2 cm | 55 % |

Chyba je průměrná odchylka hladiny v cm během povodní (7 dní před vrcholem až 5 dní po něm), průměr přes Děčín a Ústí a horizonty 12, 24 a 36 h.

Povodeň Boris v září 2024 (z testu, model ji nikdy neviděl): překročení 3. stupně v Děčíně model ohlásil 27 hodin předem a vrchol 649 cm předpověděl 24 hodin předem na 611 cm. Na testu varoval před 3. stupněm pokaždé.

## Co je v repozitáři

| Cesta | Co tam je |
|---|---|
| `src/data.py` | hodinová tabulka hladin a průtoků 2006–2025, načítá se přes `nacti()` |
| `src/features.py` | 98 vstupů a cíl, stejné pro všechny modely |
| `src/evaluate.py` | společné rozdělení v čase a metriky (chyba na povodních, předstih varování, propásnuté povodně, plané poplachy) |
| `src/porovnej.py` | natrénuje a vyhodnotí modely, výsledek uloží do `results/` |
| `src/models/*.py` | modely: `jako_ted`, `ridge` (finální), `mlp`, `lgbm`, `fyzika` a všechny zkoušené varianty |
| `src/krizova_validace.py` | vícenásobná validace přes 8 povodní |
| `src/pokus_*.py` | pokusy po výběru modelu (srážky, sníh, náběh povodně, další stanice, vlhkost, tlak a vítr, spojení zlepšení) |
| `src/stahni_chmu_*.py`, `src/meteo.py`, `src/stanice_hydro.py` | stažení a příprava dat |
| `src/uloz_model.py`, `src/nejistota.py` | uložení modelů pro aplikaci a rozmezí nejistoty |
| `src/graf*.py`, `src/grafy_*.py` | grafy v `docs/grafy/` a `prezentace/grafy/` |
| `src/export_web.py`, `src/dnesek_export.py` | data pro web a živá předpověď na dnešek |
| `src/export_csv.py` | CSV výstupy v `results/csv/` |
| `app/` | aplikace ve Streamlitu (Teď, Jak dobře to funguje, Mapa povodí, Animace povodně), návod v `app/README.md` |
| `web/` | statický web (field-zero.netlify.app) a HTML prezentace `web/prezentace/` |
| `prezentace/` | slajdy s texty řečníků, otázky poroty, grafy |
| `docs/` | podrobná dokumentace a grafy (odkazy na konci) |
| `results/` | výsledek každého běhu jako JSON (autor, čas, popis, metriky, parametry), `kolik_dat/`, `krizova_validace/`, `csv/` |
| `models/ridge_intervaly.json` | rozmezí nejistoty předpovědi |
| `data/external/README.md`, `data/external/nahled/` | popis všech dat a ukázky v CSV; samotná data v repozitáři nejsou |

## Jak to spustit

Potřeba je Python 3.11 nebo novější. Z kořene repozitáře:

```
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Na Windows před spouštěním skriptů `$env:PYTHONUTF8=1`, jinak spadne zápis JSON na kódování. Na Macu potřebuje LightGBM `brew install libomp`.

**1. Data** (v repozitáři nejsou, stahují se z otevřených dat ČHMÚ):

```
python src/stahni_chmu_hydro.py      # hodinové hladiny a průtoky do data/raw/chmu_hydro/ (asi 280 MB)
python src/data.py                   # postaví data/external/labe_hodinove.parquet, ze kterého se všechno učí
```

Pro pokusy se srážkami, sněhem a teplotou navíc `python src/stahni_chmu_meteo.py` (denní data meteostanic do `data/raw/chmu_meteo/`) a `python src/meteo.py` (postaví `data/external/labe_meteo.parquet`, s přepínačem `--o-den-driv` myšlenkový pokus s dokonalou předpovědí).

Aplikace potřebuje ještě podklady pro mapy. Každý si postaví jeho skript:

| Soubor v `data/external/` | Příkaz | Zdroj |
|---|---|---|
| `stanice_hydro.csv` | `python src/stanice_hydro.py <cesta k meta1-*.json>` | metadata stanic ČHMÚ z balíčku pořadatelů |
| `n_lete_vody.csv`, `zaplavova_uzemi.geojson` | `python app/rozliv.py --priprav` | N-leté průtoky ČHMÚ, záplavová území DIBAVOD (asi 750 MB ke stažení) |
| `reky.geojson` | `python app/animace.py reky` | OpenStreetMap |
| `rozliv_dem_decin.geojson`, `rozliv_dem_usti.geojson` | `python app/rozliv_dem.py --priprav` | ČÚZK DMR 5G (asi 3 minuty) |
| `budovy_decin.json`, `budovy_usti.json` | `python app/budovy.py --priprav` | OpenStreetMap |

**2. Trénink a vyhodnocení:**

```
python src/porovnej.py jako_ted ridge      # Děčín a Ústí za 12, 24 a 36 h na validaci, výsledek do results/
python src/porovnej.py ridge --rychle      # jen Děčín za 24 h
python src/porovnej.py --prehled           # poslední výsledek každého modelu vedle sebe
python src/krizova_validace.py ridge mlp lgbm fyzika
```

Přepínač `--test` pustí finální test 2021–2025. Ten jsme spustili jednou, v pátek ve 21:00, na model vybraný předem (`python src/porovnej.py jako_ted ridge fyzika lgbm mlp --test`), a pak už ne. Podle testu jsme nic neladili ani neměnili.

**3. Aplikace:**

```
python src/uloz_model.py             # ridge učený do 2018, pro přehrávání historie
python src/uloz_model.py --vse       # ridge_vse učený na všem 2006–2025, pro předpověď na dnešek
streamlit run app/app.py
```

Aplikace se otevře na Dnešku: stáhne operativní data ČHMÚ a ukáže předpověď na 12, 24 a 36 h vedle oficiální předpovědi ČHMÚ. Po vypnutí přepínače přehrává povodně z archivu. Satelitní mapa potřebuje veřejný token Mapboxu v `.env` (`MAPBOX_TOKEN=...`), bez něj se použije podklad OpenStreetMap. Kontrola aplikace bez prohlížeče: `python app/test_app.py` (s přepínačem `--dnesek` i živá data).

**4. Web:** `python src/export_web.py --jen-data` (s `--vse` i stránky map, ty potřebují token), `python src/dnesek_export.py` (živá předpověď do `web/data/dnesek.json`) a `npx serve web`. Podrobně v `docs/WEB.md`.

## Data

**Hlavní zdroj:** hodinový archiv ČHMÚ (https://opendata.chmi.cz/hydrology/historical/data/hourly/), 2006–2025, 175 320 hodin. Hladina v Děčíně a Ústí a průtok na 12 stanicích ve třech větvích povodí:

| Větev | Stanice (doba doběhu do Děčína) |
|---|---|
| Labe v kraji | Ústí nad Labem (4 h), Děčín |
| Vltava | Praha-Chuchle (17 h), Vraňany (13 h), Beroun na Berounce (23 h), Nespeky na Sázavě (25 h) |
| horní Labe | Mělník (13 h), Kostelec (10 h), Nymburk (10 h), Přelouč (18 h), Předměřice na Jizeře (18 h) |
| Ohře | Louny (16 h) |

**Proč ne jen balíček od pořadatelů:** balíček má dva roky a stanice v kraji, nejvýš proti proudu je Ústí, 4 hodiny před Děčínem, a v datech je jediná povodeň. Lineární regrese jen se stanicemi z kraje a dvěma roky dat dala na validaci 44,6 cm, stejně jako „bude jako teď“, a propásla polovinu povodní (12 z 24). Se všemi stanicemi a celou historií 17,1 cm. Archiv ČHMÚ je stejný zdroj, za roky 2024 a 2025 se s balíčkem shoduje na hodinu i na centimetr.

**Operativní data pro Dnešek:** https://opendata.chmi.cz/hydrology/ (adresáře `now` a `recent`), 10minutové hodnoty zprůměrované na hodiny stejně jako v archivu. Průtok v Mělníku a Nymburce ČHMÚ operativně nezveřejňuje, dopočítáváme ho z bilance vody: Mělník = Vraňany + Kostelec o hodinu dřív (v archivu odchylka 0,5 %), Nymburk = Kostelec − Jizera (8 %). Data chodí se zpožděním 1 až 3 hodiny.

**Úpravy:** díry se nedoplňují (doplňování bralo hodnotu z budoucnosti). Vyřazená je jen chyba měření v Děčíně 5.–8. 2. 2006 (hladina 1 019 cm při průtoku 120 m³/s, nejspíš led), 82 hodin. Bilance vody, měrné křivky a časy jsme zkontrolovali, povodně nejsou odlehlé hodnoty a nic dalšího se nemaže.

**Rozdělení v čase, nikdy náhodně** (`src/evaluate.py`):
- trénink 2006–2018 bez validačních povodní a 20 dní kolem nich,
- validace: povodně 4/2006, 3/2009, 9/2010, 1/2011 (16 dní před vrcholem až 5 po) a klidné roky 2019–2020,
- test 2021–2025, spuštěný jednou na konci. Finální model se pro test učil na všem do konce 2020.

Validace je na vynechaných povodních, ne na posledních letech, protože v letech 2016–2020 žádná povodeň nebyla.

## Model a vstupy

**Vstupy** (`src/features.py`), jen to, co je v okamžiku předpovědi už změřené:
- hladina v Děčíně a Ústí teď a před 1, 2, 3, 6, 12 a 24 h (14 sloupců),
- průtok všech 12 stanic teď a před 3, 6, 12, 18, 24 a 36 h (84 sloupců).

**Model** (`src/models/ridge.py`): odmocnina z průtoků (hladina roste s průtokem zhruba jako odmocnina, tak to dává měrná křivka), standardizace a Ridge s alpha = 1. Cíl je hladina v cm za 12, 24 nebo 36 h, pro každý cíl a horizont jeden model (6 modelů). Předpověď je vážený součet vstupů, takže je vidět, kolik centimetrů přidá každá řeka.

**Proč lineární regrese:** voda v Děčíně je zhruba součet Vltavy, horního Labe a Ohře, každá posunutá o dobu, než doteče, a to je přesně tvar lineární regrese. Povodní nad 3. stupněm jsou v tréninku jen dvě, model s 98 vahami se z nich nepřeučí, síť s 21 tisíci vahami a stromy ano. Lineární regrese navíc umí předpovědět výš, než kdy viděla, stromy ne.

**Metriky** (`src/evaluate.py`): hlavní je `mae_povodne`, průměrná chyba hladiny během povodní (7 dní před vrcholem až 5 po). K tomu předstih varování před 2. a 3. stupněm (Děčín 490 a 560 cm, Ústí 530 a 600 cm), propásnuté povodně, plané poplachy, bias a podíl předpovědí do ±20 cm. Laťka je „bude jako teď“.

**Pravidla ladění:** jedna změna s důvodem, zlepšení aspoň o 1 cm na validaci, po třech neúspěších konec. Validace má jen 4 povodně a nekonečné ladění by našlo náhodu.

## Váhy modelů

Váhy v repozitáři nejsou. Lineární regrese se natrénuje za pár sekund:

```
python src/uloz_model.py             # models/ridge_<cil>_<h>.joblib, učený 2006–2018
python src/uloz_model.py --vse       # models/ridge_vse_<cil>_<h>.joblib, učený 2006–2025
```

Koeficienty finálního modelu jsou čitelně v `web/data/model_ridge_vse_*.json` (názvy vstupů, průměry a směrodatné odchylky pro standardizaci, váhy a absolutní člen). Hotové soubory `.joblib` jsou ke stažení jako příloha releasu v GitLabu (sekce Releases, soubor `vahy_modelu.zip`). Rozmezí nejistoty je v `models/ridge_intervaly.json`.

## CSV výstupy

| Soubor | Co obsahuje |
|---|---|
| `results/csv/souhrn_modelu.csv` | poslední plný běh každého modelu a varianty (36): model, část (val, test), cíl, horizont, `mae_povodne` (chyba při povodních), `mae` (chyba všech hodin), `chyba_vrcholu`, předstih varování před 2. a 3. stupněm, propásnuté povodně, plané poplachy, autor, čas běhu a popis |
| `results/csv/predpovedi_validace.csv` | každá hodina validace: `cas_vydani` (UTC, kdy se předpověď vydala), `cil` (decin, usti), `horizont` (h), `skutecnost` a předpovědi `jako_ted`, `ridge`, `mlp`, `lgbm`, `fyzika` v cm, zaokrouhleno na 1 desetinné místo; předpověď platí pro čas `cas_vydani + horizont` |
| `results/csv/predpovedi_test.csv` | totéž pro test 2021–2025 |
| `results/krizova_validace/*.csv` | vícenásobná validace: cíl, horizont, povodeň, model, chyba, propásnuto, plané poplachy |
| `results/*.json` | každý běh zvlášť: autor, čas, popis, parametry, otisk verze dat a kódu, všechny metriky po cílech a horizontech |

## Rozšiřující výsledky

### Čtyři modely

Každý z nás vzal jeden model na jiném principu a ladil ho podle stejných pravidel. Kdyby vyhrál složitý, víme, že je co se učit; kdyby jednoduchý, víme, že složitost nepomáhá.

| Model | Jak funguje | Validace | Menší než „jako teď“ | Zachycené povodně / plané poplachy | Test |
|---|---|---|---|---|---|
| lineární regrese (finální) | vážený součet 98 vstupů, průtoky pod odmocninou | **17,1 cm** | 61 % | 24 z 24 / 0 | **22,4 cm** (55 %) |
| neuronová síť (MLP) | dvě vrstvy neuronů, učí se změnu hladiny | 17,8 cm | 60 % | 24 z 24 / 1 | 21,3 cm (59 %) |
| LightGBM | rozhodovací stromy, průtoky posunuté o dobu doběhu | 23,1 cm | 49 % | 24 z 24 / 0 | 24,0 cm (54 %) |
| fyzikální | doby putování ze tří větví a měrná křivka průtok → hladina | 24,8 cm | 44 % | 24 z 24 / 0 | 27,1 cm (45 %) |
| „bude jako teď“ | hladina zůstane stejná | 44,3 cm | 0 % | 0 z 24 / 0 | 50,2 cm |

Finální model jsme zapsali v pátek ve 20:58, před testem: nejlepší na validaci, nejjednodušší, bez planých poplachů a každá váha jde ukázat. Síť vyšla na testu o 1,1 cm lépe, na validaci o 0,7 cm hůř a ve vícenásobné validaci o 0,9 cm hůř. Rozdíl je v rámci náhody a výběr jsme podle testu neměnili, jinak by test přestal být nezávislý.

Proč ostatní prohrály: LightGBM neumí předpovědět výš, než viděl (u povodně 2013 dal vrchol 823 místo 1 072 cm) a pamatuje si povodně z tréninku. Síť se snadno přeučí (verze 64-32 měla na tréninku 5 cm a na validaci 22 cm). Fyzikální model má jednu pevnou dobu putování na stanici, jenže ta se mezi povodněmi mění (Mělník → Ústí 6 až 11 h).

### Vícenásobná validace po povodních

Každou z 8 povodní 2006–2020 jsme jednou vynechali (16 dní před vrcholem až 5 po), model naučili na zbytku bez 20 dní kolem ní a změřili chybu na ní. Test se nepoužil. 240 tréninků.

| Povodeň | „Jako teď“ | Lineární regrese | Síť | LightGBM | Fyzikální | Regrese proti „jako teď“ |
|---|---|---|---|---|---|---|
| 4/2006 | 54,6 | 18,4 | 22,4 | 23,8 | 28,5 | −66 % |
| 6/2006 | 35,4 | 15,6 | 18,8 | 18,5 | 17,4 | −56 % |
| 3/2009 | 28,4 | 11,2 | 9,8 | 12,6 | 16,1 | −61 % |
| 8/2010 | 43,2 | 28,6 | 30,9 | 27,6 | 30,2 | −34 % |
| 9/2010 | 45,5 | 21,6 | 23,5 | 24,4 | 28,3 | −53 % |
| 1/2011 | 48,6 | 17,3 | 17,5 | 22,0 | 27,6 | −64 % |
| 2/2013 | 33,6 | 14,3 | 12,8 | 13,4 | 18,3 | −57 % |
| 6/2013 | 72,2 | 33,9 | 32,4 | 39,5 | 46,8 | −53 % |
| **průměr** | **45,2** | **20,1 ± 7,7** | 21,0 ± 8,0 | 22,7 ± 8,6 | 26,7 ± 10,0 | **−55 %** |

Lineární regrese byla nejlepší na 4 povodních z 8, síť na 3, LightGBM na 1. Varování přes 48 běhů: regrese 1 propásnutí a 3 plané poplachy, síť 4 a 5, LightGBM 0 a 4, fyzikální 0 a 4, „jako teď“ 72 propásnutí. Skoro všechny plané poplachy jsou Ústí 6/2006, kdy voda vystoupala 5 cm pod 2. stupeň. Chyba víc záleží na povodni (11 až 34 cm) než na modelu: 6/2013 je nejtěžší, protože když se vynechá, model tak vysokou vodu (1 072 cm) nikdy neviděl, a 8/2010 byl déšť blízko Děčína, který stanice proti proudu nevidí.

### Finální model na testu podrobně

Test 2021–2025, model učený na všem do 2020. Do ±20 cm a bias jsou při vodě nad 1. stupněm, předstih je průměr a propásnutá povodeň se počítá jako 0.

| Stanice | Za | Chyba na povodních | „Jako teď“ | Chyba v klidu | Do ±20 cm | Bias | 2. stupeň: zachyceno, předstih, plané | 3. stupeň: zachyceno, předstih |
|---|---|---|---|---|---|---|---|---|
| Děčín | 12 h | 10,2 cm | 23,3 cm | 5,0 cm | 91 % | −2,7 cm | 3 z 4, 5 h, 0 | 3 z 3, 11 h |
| Děčín | 24 h | 17,5 cm | 44,8 cm | 7,1 cm | 70 % | −10,5 cm | 3 z 4, 12 h, 1 | 3 z 3, 21 h |
| Děčín | 36 h | 29,9 cm | 65,5 cm | 10,2 cm | 46 % | −21,7 cm | 3 z 4, 14 h, 1 | 3 z 3, 27 h |
| Ústí | 12 h | 14,7 cm | 29,3 cm | 5,8 cm | 87 % | −3,0 cm | 2 z 3, 7 h, 0 | 3 z 3, 12 h |
| Ústí | 24 h | 24,0 cm | 56,2 cm | 8,1 cm | 63 % | −13,2 cm | 3 z 3, 19 h, 0 | 3 z 3, 19 h |
| Ústí | 36 h | 38,1 cm | 81,8 cm | 11,1 cm | 40 % | −26,6 cm | 3 z 3, 21 h, 1 | 3 z 3, 22 h |

Propásnutá varování jsou hraniční: tři jsou únor 2024 v Děčíně, kdy voda 2. stupeň (490 cm) přesáhla jen o 6 cm a model předpověděl 474–489 cm, čtvrté Ústí +12 h o Vánocích 2023 (předpověď 528 cm, hranice 530). Na testu je chyba větší než na validaci, ale i „jako teď“ je horší (50,2 proti 44,3 cm), testové povodně stoupaly rychleji. Zlepšení proti laťce je podobné.

### Povodně Boris 2024 a leden 2011

- **Boris 9/2024 (test), Děčín:** 3. stupeň překročen 15. 9. 2024 ve 14:00 (12:00 UTC). Model varoval 10 h (předpověď na 12 h), 27 h (na 24 h) a 30 h (na 36 h) předem. Vrchol 649 cm předpověděl 24 h předem na 611 cm. Předpověď vydaná 14. 9. v 11:00 na 15. 9. v 11:00: z průměrné hladiny 198 cm přičetl Děčín a Ústí +80, Vltava +89, horní Labe +116, Mělník +96, Ohře −2, vyšlo 577 cm, nad 3. stupněm (560 cm). Skutečně bylo 551 cm.
- **Vánoce 2023 (test), Děčín:** 3. stupeň varován 13, 21 a 29 h předem, vrchol 624 cm předpovězen na 614 cm.
- **Leden 2011 (validace), Děčín:** 3. stupeň hlášen 15 h předem (předpověď na 24 h), vrchol 730 cm.
- **Červen 2013 (největší povodeň v datech, 1 072 cm), Děčín:** je v tréninku, proto ji na webu, v mapě i v úvodním videu prezentace přehráváme modelem učeným na všem do 2020 bez této povodně a 20 dní kolem ní (`ridge_bez2013` v `app/predikce.py`, nejvyšší hladina, kterou při učení viděl, byla 875 cm). Výsledek na 24 h: 3. stupeň hlášen 18 h předem, vrchol předpovězen na 952 cm (o 120 cm méně), chyba při povodni 47,7 cm proti 97,4 cm u „jako teď“ (o 51 % méně); na 2. stupeň varoval jen 2 až 4 h předem, nástup byl rychlý. Čísla jsou v `web/data/metriky.json` (`2013-06`).

Grafy `docs/grafy/povoden_2024-09_decin_24h.png`, `povoden_2023-12_decin_24h.png`, `povoden_2011-01_decin_24h.png`.

### Všechno, co jsme zkoušeli

Chyba na povodních na validaci (`mae_povodne`), finální model 17,1 cm. Test se pro žádný z pokusů nepoužil.

| Pokus | Výsledek | Závěr |
|---|---|---|
| jen stanice v kraji a 2 roky dat (jako balíček) | 44,6 cm, 12 z 24 povodní propásnuto | nestačí; 2 roky se všemi stanicemi 26,9, 8 let 16,6, 13 let 17,1 |
| přítoky v kraji (Bílina, Ploučnice) | o 0,2–0,5 cm horší | doteče z nich za pár hodin a přidají 2–13 % vody |
| síla regularizace alpha 0,1 až 100 | 17,1–17,5 cm | alpha 1 |
| cíl jako změna hladiny místo hladiny | 17,1 cm | beze změny |
| jiné stanice pro každý horizont | 17,6 cm | horší |
| průměr regrese a sítě | 16,9 cm | o 0,2 cm, jen složitost navíc |
| doba doběhu podle průtoku | regrese 21,8 cm, LightGBM 23,1 cm | nad 1 500 m³/s je v tréninku jen jedna povodeň (2013) |
| větší váha povodňových hodin (5× a 20×) | 17,2 a 18,5 cm | model se naučí „vysoká voda, bude klesat“ a víc podhodnocuje stoupání |
| srážky, sníh a teplota z 25 meteostanic | 17,4 cm (jen srážky 17,1, sníh a teplota 17,3); síť 21,2 | voda z deště je na 12–36 h už v řekách a model ji vidí v průtocích |
| voda ve sněhu | 17,8 cm | horší; zimní model se sněhem 18,9 proti celoročnímu 15,6 na zimních povodních |
| hodinové srážky v reálném čase (horní mez) | nejvýš o 1 cm lépe | hodinový archiv ČHMÚ je až od 2018, na trénink krátký |
| dokonalá předpověď deště na 1 den / 3 dny (myšlenkový pokus) | 16,3 / 16,1 cm | ani dokonalá předpověď nepomůže na 12–36 h o víc než 1 cm |
| vlhkost, tlak, vítr (rychlost a směr) | 17,2 / 17,0 / 17,0 cm, vše 17,1, vše známé den předem 17,0 | do řeky vodu nepřidají, jsou jen náznakem deště |
| polynom 2. stupně (druhé mocniny / se součiny) | 22,8 / 19,9 cm | při vysoké vodě se ohne špatně, ohyb měrné křivky už dává odmocnina |
| „při prudkém vzestupu ještě prudší“ | 17,0 cm, při náběhu povodně 35,2 → 34,1 cm | po vzestupu o 30 cm za 6 h pokračovalo stoupání o víc než 50 cm jen ve 22 % případů |
| varování podle horní meze nejistoty | o 3–4 h dřív, ale 4 plané poplachy | hodí se jako předběžná výstraha, ne jako předpověď |
| konvoluční síť po čase (TCN) na surových 48 h | 20,3 cm, 3 propásnutá varování, 16 min tréninku | naučila se skoro stejné váhy jako regrese (hlavně „průtok v Praze teď“) |
| další stanice (horní Ohře, Zbraslav) | 17,4 cm, vícenásobná validace 19,7 | smíšené, pod 1 cm |
| spojení malých zlepšení (zrychlení, horní Ohře, srážky, průměr se sítí) | 17,2 cm, vícenásobná 19,3, na 4 povodních, podle kterých se nikdy nevybíralo, 21,5 proti 23,1 | sečte se jen zčásti (0,8–1,6 cm), na validaci nic |

Neuronová síť a LightGBM jsou nelineární a nevyhrály, polynom taky ne. Rezerva není v tvaru modelu, ale ve vstupech: voda, která v řekách ještě není.

### Rozpracovaná varianta s 30 stanicemi

Lineární regrese se 30 stanicemi místo 12. Pro Děčín +24 h vyšla na validaci uvnitř tréninku lépe (14,2 proti 15,6 cm), na naší validaci hůř (17,8 proti 15,5 cm, kvůli jarní povodni 2006). Výsledek je smíšený, do finálního modelu nešla. Ověřit ji vícenásobnou validací je jeden z dalších kroků.

### Přeučení

Děčín +24 h, chyba na trénovacích povodních / na validačních: bez regularizace 19,7 / 15,5 cm, Ridge alpha 1 (finální) 19,7 / 15,5, alpha 100 20,5 / 16,1. Na tréninku tedy není lepší, opak přeučení (validační povodně jsou nižší než 2013 v tréninku). 98 vah se odhaduje ze 108 tisíc hodin. Pro srovnání přeučené modely: síť 64-32 na velké vodě 5 / 22 cm, LightGBM v2 4,7 / 27,8 cm. Sousední zpoždění jsou skoro stejná (průtok v Praze teď a před 3 h má korelaci 0,998), proto má model velké kladné a záporné váhy vedle sebe: odečítá starší hodnotu od nové a počítá tím trend. Regularizace je zmenší (největší váha 104 → 88), výsledek se nezmění.

### Rozmezí nejistoty

K předpovědi ukazujeme „nejspíš od–do“: 5. a 95. percentil chyb na tréninku podle pásma hladiny teď (0–300, 300–450, 450–600, nad 600 cm), `src/nejistota.py`. Na validaci, kterou při odhadu model neviděl, se do rozmezí vešlo 89–92 % hodnot celkem a 76–88 % na povodních (12 h 87–88 %, 24 h 79–84 %, 36 h 76–78 %). Na povodních je rozmezí o něco užší, než by mělo, protože validační povodně jsou vyšší než trénovací; říkáme proto „8 z 10“. Šířka na povodních: Děčín 33 / 53 / 72 cm, Ústí 61 / 77 / 82 cm.

### Doba doběhu a proč jen 36 hodin

Posun s největší korelací změn průtoku za 6 h, jen trénovací část (`src/doba_dobehu.py`): do Děčína Ústí 4 h (korelace 0,93), Kostelec a Nymburk 10 h, Mělník a Vraňany 13 h, Louny 16 h, Praha-Chuchle 17 h, Předměřice a Přelouč 18 h, Beroun 23 h, Nespeky 25 h. Do Ústí o 3–4 h méně. Při velké vodě vychází skoro stejně, jen silnější korelace. Mezi povodněmi se doba mění (vrchol z Vraňan do Ústí jednou za 12 h, jindy za 45 h), proto model dostává od každé stanice víc zpoždění a správné si vybere sám.

Vodu, která ještě neteče žádnou stanicí, z měření na řece nevidí nikdo. Proto chyba na 36 h je skoro dvakrát větší než na 24 h (test, Děčín 17,5 → 29,9 cm). Srážky by pomohly až dál: s dokonale známým deštěm Děčín na 36 h 26,0 → 24,0 cm, na 48 h 40,3 → 36,8, na 72 h 78,0 → 69,1 cm; naměřené srážky skoro nic (26,2, 40,5, 76,9). Na dešťové povodni 9/2010 by dokonalá předpověď ubrala 23 % chyby na 36 h a 40 % na 72 h, na zimních povodních nic. Historické předpovědi srážek na trénink ale nemáme.

### Rozliv v mapě

Rozliv v Děčíně a Ústí počítáme z výškového modelu terénu ČÚZK DMR 5G (2 m): zaplavené je všechno pod hladinou, co je spojené s korytem, hladina podél řeky se sklonem, po 10 cm (`app/rozliv_dem.py`). Není to hydraulický model, nemá proudění ani objem vlny a zdi a hráze pod rozlišením terénu nevidí. Proti oficiálním záplavovým územím DIBAVOD (Q5, Q20, Q100) vychází shoda IoU 0,82–0,90, například Děčín Q5 (hladina 707 cm): náš rozliv 167 ha, DIBAVOD 183 ha, průnik 165 ha, IoU 0,89. Rozdíly: náš rozliv zatéká navíc do údolí přítoků (hlavně Bíliny v Ústí), DIBAVOD má navíc úzké pásy podél břehů.

## Limity

- Na 36 h je chyba skoro dvakrát větší než na 24 h, voda, která přijde, ještě neteče žádnou stanicí.
- Vrchol vyšší, než jaký model viděl v tréninku, podhodnotí. Všechny modely na testu podhodnocují vrcholy, nejvíc na 36 h (bias až −27 cm).
- Povodně z deště blízko kraje (8/2010) stanice proti proudu nevidí.
- Na začátku prudkého vzestupu je předpověď o několik hodin pozadu, model sází na průměrné pokračování.
- Archivní data jsou zpětně ověřená, v provozu chodí předběžná a se zpožděním 1–3 h. Mělník a Nymburk se v provozu dopočítávají.
- Historické předpovědi ČHMÚ nemáme, takže se s nimi na starých povodních srovnat neumíme. V aplikaci je oficiální předpověď jen vedle naší pro dnešek.
- Validace má jen 4 povodně, vícenásobná 8, test 4. Velkých povodní nad 3. stupněm je v tréninku jen dvě.

## Co dál

- Předpověď srážek pro předpověď na 2–3 dny u dešťových povodní. Na trénink chybí archiv předpovědí (Open-Meteo ho má až od 2021–2022).
- Hodinové srážky v reálném čase, až bude delší archiv (ČHMÚ od 2018).
- Víc stanic proti proudu (varianta s 30 stanicemi), ověřit vícenásobnou validací.
- Dvoustupňové varování: předběžná výstraha podle horní meze nejistoty, ostré podle předpovědi.

## Podrobná dokumentace

| Soubor | Co v něm je |
|---|---|
| `docs/PREHLED.md` | úloha, vstupy, co jsme nevzali a proč, rozdělení, výsledky, všechna rozhodnutí |
| `docs/CESTA_MODELU.md` | celá cesta od čtyř nápadů k lineární regresi a co jsme zkoušeli po testu |
| `docs/POKUSY.md` | každý trénink a pokus: otázka, data, model, výsledek proti laťce, závěr |
| `docs/DENIK.md` | rozhodnutí v čase a proč |
| `docs/DATA.md` | data, stanice, doby doběhu, chyby v datech, operativní data, rozliv |
| `docs/POROZUMENI.md` | úloha a pojmy našimi slovy, jak číst výsledky, otázky poroty |
| `docs/WEB.md` | web a jeho nasazení |
| `docs/grafy/` | všechny grafy |
| `prezentace/SLAJDY.md`, `prezentace/OTAZKY.md` | prezentace s texty a odpovědi na otázky poroty |
