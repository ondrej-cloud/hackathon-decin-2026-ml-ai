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
Následující pokusy jsou doplněné zpětně (pá 19:55). Všechny byly před společným rozdělením, čísla proto nejdou přímo srovnat s výsledky v `results/`. Podrobnosti v `docs/NAPAD_LABE.md`.

## pá 17:46 · Ondra · lineární model na šesti povodních
- Otázka: funguje předpověď z Ústí, Mělníka a Prahy na povodních, které model neviděl?
- Data a rozdělení: ČHMÚ 2004–2025, pro každou povodeň trénink bez ±20 dní kolem ní, test týden před vrcholem a 5 dní po něm.
- Vstupy: hladina a průtok Děčín, průtok Ústí, Mělník a Praha se zpožděním, průtoky jako odmocnina.
- Model a nastavení: lineární regrese.
- Výsledek (Děčín +24 h, průměr 6 povodní): 29,6 cm proti 58,7 cm u „jako teď“, varování před 3. stupněm 12–29 h předem. LightGBM u povodně 2013 vrchol 823 cm místo 1 072.
- Závěr: lineární model je dobrý kandidát, stromy mají problém s vrcholy nad rámec tréninku.

## pá 18:36 · Ondra · brány proti proudu pro Ústí
- Otázka: které stanice proti proudu pomáhají a na jak dlouhý horizont?
- Data a rozdělení: ČHMÚ 2005–2025, 5 povodní v Ústí nad 3. stupněm, každá vynechaná z tréninku i s 20 dny kolem.
- Vstupy: Ústí a postupně blízké (Mělník, Vraňany, Kostelec), střední (Praha, Nymburk, Jizera) a vzdálené stanice (Beroun, Sázava, Přelouč, Louny), zpoždění 0–36 h, odmocnina průtoků.
- Model a nastavení: lineární regrese.
- Výsledek (chyba na povodních +12 / +24 / +36 h): jen Ústí 26,8 / 49,9 / 74,2 cm, + blízké 17,0 / 31,4 / 51,6, + střední 21,0 / 31,9 / 44,3, + vzdálené 18,0 / 26,9 / 36,8. „Jako teď“ 30,9 / 59,4 / 86,3.
- Závěr: čím delší horizont, tím vzdálenější stanice jsou potřeba. Na 12 h vzdálené stanice jen přidají šum.

## pá 18:44 · Ondra · balíček proti stanicím proti proudu a historii
- Otázka: stačí data z kraje, jaká jsou v balíčku, nebo potřebujeme stanice proti proudu a historii?
- Data a rozdělení: ČHMÚ, 6 povodní v Děčíně, každá vynechaná z tréninku. Varianta „balíček“ = Děčín, Ústí a Louny za 2024–2025.
- Model a nastavení: lineární regrese, odmocnina průtoků.
- Výsledek (Děčín +12 / +24 h): „jako teď“ 30,3 / 58,0 cm, kraj 2 roky 23,0 / 43,0, kraj + proti proudu 2 roky 17,2 / 28,2, kraj 20 let 19,0 / 38,3, kraj + proti proudu 20 let 13,7 / 24,3.
- Závěr: stanice proti proudu pomohly víc než historie. Historie je ale nutná k ověření, v balíčku je jediná povodeň.

## pá 18:52 · Ondra · malé řeky v kraji
- Otázka: dá se na malých řekách předpovídat z horní stanice a hodí se na výběr modelu?
- Data a rozdělení: ČHMÚ 2004–2025, trénink do 2016, test 2017–2025, chyba při průtoku nad 95. percentilem.
- Výsledek (+3 h, „jako teď“ / vlastní historie / + horní stanice, m³/s): Kamenice 1,10 / 0,88 / 0,39, Ohře Žatec → Louny 1,72 / 1,55 / 1,05, Chomutovka 0,28 / 0,27 / 0,23, Bílina 0,58 / 0,53 / 0,52, Mandava 1,04 / 0,71 / 0,63. Voda z horní stanice doteče za 0–7 h.
- Závěr: na malých řekách jde předpovídat jen pár hodin dopředu a rozhoduje déšť. Jako start se nehodí, jako druhá zkouška modelů ano (Kamenice).

## pá 19:35 · Ondra · jak dlouho trvá trénink
- Otázka: stačí počítače, nebo je potřeba Kaggle?
- Výsledek (MacBook M1, Děčín +24 h, 108 tisíc řádků): lineární regrese 0,2 s, LightGBM asi 7 s, MLP (64, 32) 17 s (82 epoch).
- Závěr: všechno lokálně, Kaggle by jen zdržel nahráváním a frontou.
