# Zadání 2026

Pět úloh: tři od KSI s otevřenými daty z Ústeckého kraje a dvě od Ústavu fyziky plazmatu AV ČR (ÚFP) s daty z tokamaků. Celé texty jsou v `.md` souborech vedle (převedené z PDF), obrázky jen v PDF.

## KSI 1: Jak se mění obce Ústeckého kraje? (`ksi-1-obce`)

- **Data:** 354 obcí, vývoj počtu obyvatel, narození a úmrtí, stěhování, věková struktura, nezaměstnanost, základní údaje o obcích, hranice obcí. Propojení přes identifikátory obcí. Můžeme přidat další otevřená data se zdrojem.
- **Co řešit:** volné. Například skupiny podobných obcí, obce s neobvyklým vývojem, stárnutí, vztah demografie a nezaměstnanosti, predikce ukazatele, mapa.
- **Výstup:** model, clustering, mapa, dashboard nebo aplikace.
- **Pozor:** souvislost neznamená příčinu. Hodnotí se smysluplnost, práce s daty, interpretace a prezentace, ne složitost modelu.
- **V prezentaci musí být:** otázka, data, příprava dat, metoda, zjištění, limity.

## KSI 2: Co nám prozradí měření ovzduší? (`ksi-2-ovzdusi`)

- **Data:** hodinová měření PM10, PM2,5, NO₂, NOx, O₃, SO₂, případně CO. Metadata stanic (poloha, výška, typ, okolí). Podle dostupnosti meteorologická data.
- **Co řešit:** předpověď koncentrace na další hodiny, neobvyklé hodnoty, srovnání stanic, denní, týdenní a sezónní vzory, rozpoznání období se špatným ovzduším, vztah k počasí.
- **Výstup:** predikční model, detektor anomálií, klasifikátor, vizualizace, mapa, aplikace.
- **Pozor:** rozdělení dat v čase, model se nesmí testovat na datech, která viděl.
- **V prezentaci musí být:** problém, data a stanice, jak řešíme chybějící a neplatné hodnoty, vstupy modelu, jak jsme ověřili kvalitu, co model umí a co z dat určit nejde.

## KSI 3: Dokážete předpovědět Labe? (`ksi-3-labe`)

- **Data:** historická a aktuální data z měřicích profilů na Labi (čas, vodní stav, průtok, teplota vody, stanice). Podle dostupnosti meteorologická data. Informace o stanicích a jejich poloze.
- **Co řešit:** předpověď vodního stavu nebo průtoku, rychlé změny, jak se změna výš po toku projeví níž, vztah k počasí, teplota vody, včasné varování.
- **Výstup:** predikční model, detekce anomálií, klasifikace situací, dashboard, aplikace.
- **Pozor:** časové pořadí. Pro předpověď nepoužívat nic, co v okamžiku předpovědi ještě nebylo známé.
- **V prezentaci musí být:** problém, data, příprava dat, vstupní proměnné, model, ověření kvality, limity.

## ÚFP 1: Tvar a poloha plazmatu (ekvilibrium) (`ufp-ekvilibrium`)

- **Data (tokamak COMPASS):** `equil_data.csv`. Vstupy jsou sloupce začínající `IPR` a `FL` (magnetické cívky a smyčky). Cíle jsou parametry tvaru a polohy: elongace, horní a dolní triangularita, R a Z středu, X-bod, strike pointy, `plasma_current`, `R_limiter`/`Z_limiter`. Navíc několik tisíc snímků z kamery (`img/`, `camera_data.csv`), sloupec `mode` (L-mód, H-mód, ELM) a zašuměná data `equil_data_noisy.csv`.
- **Cíle:**
  1. Model z magnetických měření (lehčí) nebo ze snímků (těžší).
  2. Dal by se použít v reálném čase (jednotky až desítky ms, na GPU)?
  3. Přesnost po jednotlivých parametrech a stabilita výstupu v čase.
  4. Jak se přesnost změní s méně vstupy? Které cívky nebo části obrazu jsou důležité?
- **Bonusy:** druhý zdroj dat nebo multimodální model, závislost na počtu dat, černobílá kamera, časový vývoj, posun kamery, odolnost vůči šumu a driftu, co model „sleduje“, nové tvary mimo korelace v datech.
- **Pozor:** `discharge` a `time` nejsou vstupy, jen indexy. Dělit **po celých výbojích** (`discharge`), jinak vyjde přesnost moc optimisticky. Pořadí strike pointů 1 a 2 se mezi řádky mění. Tvary jsou zastoupené nerovnoměrně.
- **Výstup:** Jupyter notebooky (i Colab) s modely, grafy a všemi závěry a prezentace. Aplikace není nutná.
- **Ukázka načtení:** https://repo.tok.ipp.cas.cz/seidl/cvut-ml-hackaton-2026-compass/-/blob/master/notebooks/uloha-1-ekvilibrium-nacteni-dat.ipynb

## ÚFP 2: Ubíhající elektrony z infračervené kamery (`ufp-ubihajici-elektrony`)

- **Data:** syntetické snímky (ray tracing SERECH), u každého `parameters.csv` se sedmi parametry rozdělovací funkce: `momentum_mean`, `momentum_std`, `pitch_decay`, `ne_magaxis`, `ne_lcfs`, `concavity`, `convexity`. Sloupec `run_name` je název obrázku ve složce `pictures`. Čtyři datasety od nejlehčího:

  | Dataset | Odrazy od stěny | momentum_mean a pitch_decay | Ostatní parametry |
  |---|---|---|---|
  | A | ne | mřížka | pevné |
  | B | ano | mřížka | pevné |
  | C | ano | mřížka | náhodné |
  | D | ano | náhodné | náhodné |

- **Úlohy:**
  1. Neuronová síť na A: snímek → `momentum_mean` a `pitch_decay`, přesnost na testovací části.
  2. Totéž pro B, C, D. U C a D všech sedm parametrů.
  3. Přenos: síť z A na B (vliv odrazů), z B na C a D, z C na D.
  4. Kolik snímků stačí: z D postupně ubírat, dokud přesnost výrazně neklesne.
- **Pozor:** zadání výslovně chce neuronovou síť. Naše poznámka, ne ze zadání: u A–C leží parametry na mřížce, takže stejné hodnoty jsou v trénovací i testovací části a síť se může naučit jen „poznat bod mřížky“. Skutečnou přesnost ukáže až D.
- **Ukázka načtení:** https://repo.tok.ipp.cas.cz/seidl/cvut-ml-hackaton-2026-compass/-/blob/master/notebooks/uloha-2-ubihajici_elektrony-nacteni-dat.ipynb

## Data ÚFP jsou důvěrná

U obou úloh ÚFP platí: data se nesmí bez svolení ÚFP zveřejnit ani zpřístupnit nikomu mimo účastníky hackathonu. Nikdy do Gitu. Na Kaggle nebo jinam do cloudu jen se svolením mentora z ÚFP (zadání samo zmiňuje Google Colab). Data KSI jsou otevřená.
