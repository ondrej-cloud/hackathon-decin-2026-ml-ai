# Pokusy

Každý trénink a pokus, i nepovedený, jako nový záznam na konec souboru. Nic nepřepisovat, jen připisovat. Git záznamy z různých větví spojí sám.

```
## pá 18:40 · Dan · krátký název pokusu
- Otázka: co tímhle pokusem zjišťujeme
- Data a rozdělení: které soubory, jak rozdělené a proč, kolik řádků nebo snímků
- Vstupy: které sloupce nebo jak upravené snímky
- Model a nastavení: model, hlavní parametry, seed
- Kde a jak dlouho: počítač nebo Kaggle, doba tréninku
- Výsledek na val: metrika a srovnání s baseline
- Závěr: co z toho plyne a co dál
- Soubory: results/…, src/… nebo notebook
```

## pá 19:15 · Ondra · základ „bude jako teď“ a kontrola řetězce
- Otázka: funguje společné rozdělení a vyhodnocení a jakou laťku musí modely překonat?
- Data a rozdělení: `data/external/labe_hodinove.parquet`, rozdělení z `src/evaluate.py` (train 2006–2018, val 4 povodně + 2019–2020), asi 108 tisíc řádků train, 18 tisíc val.
- Vstupy: 98 sloupců z `src/features.py` (hladiny Děčín a Ústí, průtoky 12 stanic se zpožděním 0–36 h).
- Model a nastavení: `jako_ted` (hladina za h = hladina teď); pro kontrolu Ridge(alpha=1) s odmocninou jen na průtoky a StandardScaler, seed 42.
- Kde a jak dlouho: MacBook M1, obojí pod sekundu.
- Výsledek na val (chyba na povodních, Děčín +12 / +24 / +36 h): „jako teď“ 23,0 / 44,4 / 65,6 cm, Ridge 9,0 / 15,5 / 26,0 cm. Ridge varoval před 2. stupněm 11 / 16 / 37 h předem, 0 propásnutých, 0 planých poplachů. Ústí vychází skoro stejně. LightGBM na změnu hladiny (500 stromů) dal na povodních 28 / 50 / 56 cm.
- Závěr: řetězec funguje. Lineární model je zatím jasně nejlepší, LightGBM je za 24 h dokonce horší než „jako teď“, Dan zjistí proč. Odmocnina se smí dávat jen na průtoky, na hladině zkazila vrchol 2006 o metr.
- Soubory: `results/2026-10-23_1913_jako_ted.json`, `src/models/jako_ted.py`; Ridge a LightGBM jen jako kontrola, nejsou uložené, udělají je Honza a Dan.

## pá 19:35 · Dan · základy pro LightGBM: lineární trend a Ridge na změnu stavu
- Otázka: jak dopadnou jednoduché základy, se kterými budu LightGBM srovnávat, a funguje u mě řetězec stejně jako u Ondry?
- Data a rozdělení: společná tabulka a rozdělení z `src/evaluate.py`, všech 6 kombinací (Děčín a Ústí, +12 / +24 / +36 h).
- Vstupy: trend jen stav v cíli teď a před 6 h. Ridge všech 98 sloupců, průtoky pod odmocninou.
- Model a nastavení: `zaklad_trend` (stav se dál mění stejně rychle jako za posledních 6 h). `zaklad_ridge` (StandardScaler + Ridge alpha 1, cíl je změna stavu proti teď).
- Kde a jak dlouho: Dan, Yoga 7i, do 2 s.
- Výsledek na val (chyba na povodních, Děčín +12 / +24 / +36 h): „jako teď“ 23,0 / 44,4 / 65,6 cm, trend 18,0 / 36,1 / 60,0 cm, Ridge 9,0 / 15,5 / 26,0 cm. `prumer_povodne`: „jako teď“ 44,3, trend 39,4, Ridge 17,1. Trend nic nepropásl, ale má plané poplachy před 2. stupněm (Děčín 2 / 5 / 16), Ridge žádné.
- Závěr: Ridge na změnu stavu dává na cm stejná čísla jako Ondrův Ridge na stav, řetězec u mě běží stejně. Trend je lepší než „jako teď“ jen díky tomu, že zachytí začínající stoupání, ale přestřeluje a dělá plané poplachy. Laťka pro LightGBM je Ridge se 17,1 cm.
- Soubory: `src/models/zaklad_trend.py`, `src/models/zaklad_ridge.py`, `results/2026-10-23_1933_zaklad_trend.json`, `results/2026-10-23_1933_zaklad_ridge.json`, `results/predpovedi/zaklad_*.parquet`
