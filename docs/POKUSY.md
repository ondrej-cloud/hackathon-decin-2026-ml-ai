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
Následující pokusy jsou doplněné zpětně (pá 19:35). Všechny byly před společným rozdělením, čísla proto nejdou přímo srovnat s výsledky v `results/`. Podrobnosti v `docs/NAPAD_LABE.md`.
## pá 19:28 · Tobias · doby putování vody pro fyzikální model
- Otázka: za kolik hodin se změna průtoku na stanici proti proudu projeví v Ústí a v Děčíně?
- Data a rozdělení: `labe_hodinove.parquet`, jen train z `src/evaluate.py` (2006–2018 bez validačních povodní).
- Vstupy: průtoky vyhlazené klouzavým průměrem 12 h, z nich změna za 6 h. Pro každou dvojici stanic posun 0–48 h s největší korelací změn. Zvlášť pro celý train a pro vysokou vodu (průtok v Ústí nad 75. percentilem).
- Model a nastavení: žádný model, jen korelace.
- Kde a jak dlouho: MacBook M4, pár sekund.
- Výsledek (vysoká voda): Kostelec → Ústí 5 h (r 0,58), Vraňany → Ústí 10 h (0,59), Louny → Ústí 12 h (0,43), Mělník → Ústí 8 h (0,83), Ústí → Děčín 4 h (0,98). Dál proti proudu: Praha → Vraňany 5 h (0,95), Beroun → Vraňany 12 h, Sázava → Vraňany 8 h, Nymburk → Kostelec 6 h (0,90), Jizera → Kostelec 6 h, Přelouč → Kostelec 16 h (0,80).
- Závěr: bez vyhlazení vycházely korelace jen 0,2–0,46 a Nymburk dokonce rychlejší než Kostelec pod ním, to ruší hodinové kolísání (nejspíš elektrárny na Vltavě). Po vyhlazení časy dávají smysl a sedí na dolní hranu odhadů ze zadání. Ohře má nejslabší vztah, je nejdál a mezi Louny a Ústím ještě něco přitéká. Tyhle časy použije `src/models/fyzika.py`.
- Soubory: zatím jen tenhle zápis, výpočet bude v `src/models/fyzika.py`.

## pá 19:31 · Tobias · fyzikální model, první běh a měrná křivka
- Otázka: kolik umí samotná fyzika bez učení, jen doby putování a měrná křivka?
- Data a rozdělení: společné z `src/evaluate.py`, Děčín +24 h (`--rychle`).
- Vstupy: průtok v cíli teď, průtoky bran Vraňany, Kostelec, Louny a nad nimi Praha, Nymburk, Jizera v zpožděních z `features.py`, hladina v cíli teď.
- Model a nastavení: průtok v cíli za h = průtok teď + přírůstky z bran posunuté o dobu putování (když voda nedotekla ani k bráně, vezme se stanice nad ní). Na hladinu přes měrnou křivku: medián hladiny v 80 pásmech podle logaritmu průtoku, jen rostoucí, nad maximem přímka. Předpověď = hladina teď + rozdíl křivky, takže se zachová, co je na stanici právě jinak. Doby putování si model spočítá z trénovacích dat (do Děčína Vraňany 13 h, Kostelec 8 h, Louny 16 h, Praha 17 h, Nymburk a Jizera 14 h).
- Měrná křivka a odlehlé hodnoty: první pokus s pásmy podle počtu bodů měl na vysoké vodě jedno pásmo 800–3700 m³/s, křivka byla plochá a vrchol 2013 ujel o 6 m. Vypadalo to jako odlehlé body, ale byla to chyba křivky. Opravdu odlehlých hodnot skoro není, typická odchylka od křivky je 1,4 cm (ČHMÚ počítá průtok z hladiny). Minimum hodin v pásmu na val při průtoku nad 1000 m³/s: 6 h dává chybu 2,7 cm, 24 h 6,7 cm, 72 h 23,6 cm (křivka končí na 1080 m³/s). K přeučení nedochází, beru 6. Koryto se za 2006–2018 posunulo jen o ±2 cm.
- Kde a jak dlouho: MacBook M4, trénink 0,1 s.
- Výsledek na val: na povodních 24,1 cm proti 44,4 cm u „jako teď“, celková MAE 11,4 proti 12,7 cm. Před 2. stupněm varoval 26 h předem, 0 propásnutých, 1 planý poplach. Před 3. stupněm 17 h předem, 0 propásnutých.
- Závěr: samotná fyzika chybu na povodních skoro půlí. Proti rychlému lineárnímu modelu (15,5 cm) je horší, nejspíš proto, že neví o přítocích mezi branami a Ústím a doby putování se mezi povodněmi mění. Dál: všech 6 kombinací a varianta bez stanic proti proudu.
- Soubory: `src/models/fyzika.py`, `results/2026-10-23_1931_fyzika.json`.
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

## pá 19:30 · Ondra · jak dlouho trvá trénink
- Otázka: stačí počítače, nebo je potřeba Kaggle?
- Výsledek (MacBook M1, Děčín +24 h, 108 tisíc řádků): lineární regrese 0,2 s, LightGBM asi 7 s, MLP (64, 32) 17 s (82 epoch).
- Závěr: všechno lokálně, Kaggle by jen zdržel nahráváním a frontou.

## pá 19:45 · Dan · LightGBM v1 a v2 ze zadání: stav proti změně stavu
- Otázka: jak dopadne LightGBM na všech 98 vstupech, když se učí stav (v1) a když změnu stavu proti teď (v2)?
- Data a rozdělení: společné rozdělení, všech 6 kombinací.
- Vstupy: všech 98 sloupců bez úprav.
- Model a nastavení: LGBMRegressor(n_estimators 500, learning_rate 0,05, num_leaves 31), seed 42, num_threads 4.
- Kde a jak dlouho: Dan, Yoga 7i, 15–20 s na model.
- Výsledek na val (chyba na povodních, Děčín +12 / +24 / +36 h): v1 57,7 / 69,6 / 73,7 cm, v2 27,8 / 49,4 / 55,6 cm, „jako teď“ 23,0 / 44,4 / 65,6. `prumer_povodne` v1 66,1, v2 40,9, „jako teď“ 44,3. Vrchol povodně 2006 (875 cm) obě přestřelily, v1 o 128–152 cm, v2 o 69–110 cm. v2 propásla před 2. stupněm 1–3 povodně.
- Závěr: obě jsou na povodních horší nebo stejné jako „jako teď“, Ondrova kontrola řetězce (28 / 50 / 56 cm) sedí. Na trénovacích povodních má v2 chybu jen 4,7 / 6,3 / 8,1 cm, na validaci 6× větší: stromy si pamatují povodně z tréninku (hlavně 2013) a na syrových průtocích je pak přenesou na jinou povodeň, kde neplatí.
- Soubory: `src/models/lgbm_v1.py`, `src/models/lgbm_v2.py`, `results/2026-10-23_1938_lgbm_v1.json`, `results/2026-10-23_1940_lgbm_v2.json`

## pá 19:45 · Dan · LightGBM a a c: průtoky posunuté o dobu doběhu
- Otázka: pomůže stromům, když místo 98 syrových sloupců dostanou fyzikálně připravené vstupy?
- Data a rozdělení: společné rozdělení, všech 6 kombinací.
- Vstupy: a) stav v cíli (teď až 24 h zpět) a ke každé stanici proti proudu průtok, který do cíle doteče za horizont (zpoždění doba doběhu − horizont, když je záporné, tak poslední známý), a rozdíl proti průtoku, který do cíle dotéká teď. Doby doběhu z `src/doba_dobehu.py`, zaokrouhlené na zpoždění v X. Průtok v cíli záměrně ne, hladina stačí. c) navíc sin a cos dne v roce a trend stavu za 6 h. Varianta b) se srážkami nejde, srážky v datech nemáme (balíček pořadatelů je jen u Ondry).
- Model a nastavení: stejné jako v2, cíl je změna stavu.
- Kde a jak dlouho: Dan, Yoga 7i, 5–7 s na model.
- Výsledek na val (Děčín +12 / +24 / +36 h): a 10,6 / 22,0 / 37,5 cm, c 10,4 / 21,7 / 36,4 cm. `prumer_povodne` a 24,0, c 22,8 (Ridge 17,1, „jako teď“ 44,3). c nic nepropásl a nemá planý poplach, a měl 1 planý poplach před 2. stupněm na 24 a 36 h.
- Závěr: připravené vstupy chybu na povodních skoro půlí (40,9 → 24,0) a c je o 1,2 cm lepší než a, nejlepší LightGBM zatím. Pořád je ale o 5,7 cm horší než Ridge. Přeučení zůstává: na trénovacích povodních 5,1 / 6,5 / 8,7 cm, na validaci 2–4× víc. Ridge má na tréninku i validaci skoro stejně. Nejvíc ztrácí na povodních 2006 a 2011, které jsou vyšší než všechno v tréninku kromě 2013 (Děčín +24 h: 2006 31 cm proti 16 u Ridge, 2011 23 proti 15). Při stoupání v průměru nepodhodnocuje, chyba je skákání předpovědi, ne soustavný posun. Povodeň 9/2010 podhodnotí o 25 cm všechny modely včetně Ridge, voda nejspíš přišla z deště blízko kraje.
- Soubory: `src/models/lgbm_a.py`, `src/models/lgbm_c.py`, `results/2026-10-23_1941_lgbm_a.json`, `results/2026-10-23_1942_lgbm_c.json` (po úpravě kódu znovu `_1947_`, stejná čísla), `src/rozbor_lgbm.py` (tabulka, trénink proti validaci)

## pá 19:52 · Dan · LightGBM c: proti přeučení list 200 hodin, monotónní omezení, menší stromy
- Otázka: zmenší se přeučení c, když stromy zjednoduším? Vždy jen jedna změna proti c.
- Data a rozdělení: společné rozdělení, všech 6 kombinací.
- Vstupy: jako c.
- Model a nastavení: c + `min_child_samples` 200 (list aspoň 200 hodin, jedna povodeň se do něj nevejde); c + monotónní omezení (víc přitékající vody nesmí dát menší vzestup, ze zadání); c + `num_leaves` 7.
- Kde a jak dlouho: Dan, Yoga 7i, 4–10 s na model.
- Výsledek na val (`prumer_povodne`, c 22,8): list 200 hodin 22,2, monotónní 23,8, 7 listů 23,4 (a 2 plané poplachy před 2. stupněm na 24 h).
- Závěr: nic neprošlo. List 200 hodin je lepší jen o 0,6 cm, pod hranicí 1 cm. Monotónní omezení a menší stromy jsou horší. Zjednodušení stromů nestačí, problém je spíš v tom, že strom dává schody a nad tím, co viděl, neumí pokračovat.
- Soubory: `src/models/lgbm_c_list200.py`, `src/models/lgbm_c_monotonni.py`, `src/models/lgbm_c_list7.py`, `results/2026-10-23_1948_lgbm_c_list200.json`, `results/2026-10-23_1950_lgbm_c_monotonni.json`, `results/2026-10-23_1951_lgbm_c_list7.json`
## pá 19:40 · Ondra · přítoky v kraji (Bílina, Ploučnice)
## pá 19:36 · Tobias · fyzikální model, všech 6 kombinací a třetí vrstva stanic
- Otázka: proč model podhodnocuje vrcholy a pomůže víc stanic proti proudu?
- Data a rozdělení: společné z `src/evaluate.py`, všech 6 kombinací.
- Úprava podle nových pravidel: doby putování se měří s vyhlazením jen z minulosti (dřív vycentrované, ovlivňovalo jen odhad doby putování na trénovacích datech). Výsledek se nezměnil.
- Základ `fyzika` (brány + jedna vrstva nad nimi): `prumer_povodne` 26,6 cm, „jako teď“ zhruba 44 cm. Na povodních Děčín 13,5 / 24,1 / 42,3 cm na 12 / 24 / 36 h, Ústí 14,4 / 23,8 / 41,5 cm. Žádná propásnutá povodeň, 1 planý poplach (Děčín +24 h).
- Přeučení: chyba na tréninku je vyšší než na validaci (Děčín +24 h na povodních 30,6 proti 24,1 cm, v tréninku je povodeň 2013), model má jen doby putování a křivku, nemá se co naučit nazpaměť.
- Kde chybuje: `vrcholy_o_kolik` je skoro všude záporné, vrcholy podhodnocuje, nejvíc na 36 h. Nejdelší doba putování do Děčína je 17 h (Praha), takže na 36 h model víc než polovinu času předpokládá, že se průtok proti proudu nezmění. Při stoupající povodni ale voda dál přibývá.
- Varianta `fyzika_tri_vrstvy`: navíc Beroun a Sázava nad Prahou a Přelouč nad Nymburkem, známá část se prodlouží na 21–25 h. `prumer_povodne` 24,8 cm (−1,8 cm). Na 36 h Děčín 38,5 a Ústí 37,5 cm (−4 cm), na 12 h beze změny (tam stačí brány). Propásnuté 0, plané poplachy 0. Varování před 2. stupněm v Děčíně ale přichází později (+24 h: 17,5 místo 26 h předem).
- Závěr: varianta prošla (zlepšení přes 1 cm, varování nehorší). Potvrzuje Ondrovo zjištění, že na delší horizont pomáhá každá vrstva stanic. Na 36 h je pořád velká chyba, protože ani třetí vrstva nesahá na 36 h dopředu.
- Soubory: `src/models/fyzika.py`, `src/models/fyzika_tri_vrstvy.py`, `results/` (fyzika a fyzika_tri_vrstvy).
## pá 19:36 · Honza · lineární regrese (Ridge) v1
- Otázka: jak dobře předpovídá lineární model a sedí to s Ondrovou kontrolou řetězce?
- Data a rozdělení: společné (`src/evaluate.py`), train 2006–2018 bez validačních povodní, val 4 povodně a 2019–2020, asi 108 tisíc řádků train.
- Vstupy: všech 98 sloupců z `src/features.py`. Odmocnina jen na průtoky (`_Q_`), hladiny beze změny, pak `StandardScaler`. Obojí uvnitř `Pipeline`, takže se učí jen na trénovacích datech.
- Model a nastavení: `Ridge(alpha=1)`. Bez náhody, lineární regrese má jediné řešení.
- Kde a jak dlouho: Honzův notebook, půl sekundy na jednu kombinaci.
- Výsledek na val (chyba na povodních +12 / +24 / +36 h): Děčín 9,0 / 15,5 / 26,0 cm, Ústí 9,6 / 15,7 / 26,7 cm. „Jako teď“ Děčín 23,0 / 44,4 / 65,6, Ústí 23,4 / 44,2 / 65,1. Průměr přes 6 kombinací (`prumer_povodne`) 17,1 cm proti 44,3 cm. Varování před 2. stupněm: Děčín 11 / 15,5 / 36,7 h předem, Ústí 16,8 / 20,8 / 21,5 h; všude 0 propásnutých a 0 planých poplachů („jako teď“ propásne všechny). Chyba trénink proti validaci (všechny hodiny, Děčín): 5,5 / 7,3 / 10,1 proti 5,2 / 7,5 / 10,9 cm, model se neučí nazpaměť.
- Závěr: sedí s kontrolou řetězce (15,5 cm). Vrcholy (`vrcholy_o_kolik`, Děčín +24 h): 2006 o 22 cm níž, 2009 o 9 výš, 2010 o 19 výš, 2011 o 7 níž. V Ústí model vrcholy spíš podhodnocuje (−15 až −21 cm na 24 h). Na 36 h je chyba na povodních skoro dvojnásobná proti 24 h: voda, která bude v Děčíně za 36 h, z velké části ještě neteče ani Prahou.
- Soubory: `results/2026-10-23_1938_ridge.json`, `results/predpovedi/ridge.parquet`, `src/models/ridge.py`.

## pá 19:38 · Honza · síla regularizace alpha
- Otázka: záleží na alpha (0,1 / 1 / 10 / 100)? Regularizace (zmenšování vah) má bránit tomu, aby model spoléhal na jeden vstup.
- Data, vstupy a model: jako v1, mění se jen alpha.
- Výsledek na val (`prumer_povodne`): 17,1 / 17,1 / 17,1 / 17,5 cm. Alpha 100 navíc zkracuje předstih varování o půl hodiny.
- Závěr: při 108 tisících řádků a 98 vstupech regularizace skoro nic nemění, rozdíl pod 1 cm. Zůstává alpha 1.
- Soubory: `results/2026-10-23_1938_ridge_alpha01.json`, `..._ridge_alpha10.json`, `..._ridge_alpha100.json`, `src/models/ridge_alpha01.py`, `ridge_alpha10.py`, `ridge_alpha100.py`.

## pá 19:39 · Honza · cíl jako změna hladiny
- Otázka: pomůže učit změnu (hladina za h hodin minus hladina teď) místo samotné hladiny? U LightGBM to Ondra zkoušel.
- Data, vstupy a model: jako v1, jen cíl je y − hladina teď a k předpovědi se hladina teď přičte zpět.
- Výsledek na val: do desetiny cm stejné jako v1 (17,1 cm), stejné předstihy.
- Závěr: u lineárního modelu, který má hladinu teď mezi vstupy, je to totéž. Váha u „hladiny teď“ se jen posune o jedničku, zbytek rovnice je stejný; liší se jen regularizace té jedné váhy a ta je zanedbatelná. U stromů to totéž není, tam změna cíle smysl mít může.
- Soubory: `results/2026-10-23_1939_ridge_zmena.json`, `src/models/ridge_zmena.py`.

## pá 19:39 · Honza · brány podle horizontu
- Otázka: platí i pro Ridge, že na 12 h stačí blízké stanice a vzdálené jen přidávají šum (`docs/NAPAD_LABE.md`, Brány proti proudu)?
- Vstupy: 12 h jen Děčín, Ústí, Louny, Mělník, Vraňany a Kostelec; 24 h navíc Praha, Nymburk a Jizera; 36 h všechny (stejné jako v1). Hladiny Děčína a Ústí vždy.
- Výsledek na val: `prumer_povodne` 17,6 cm (v1 17,1). Na 12 h je chyba o 0,4–0,6 cm menší (Děčín 8,4, Ústí 9,2), ale varování přijde později (Děčín 2. stupeň 9,2 h místo 11 h předem, Ústí 3. stupeň 4 h místo 9 h). Na 24 h horší o 2 cm (17,3 / 17,8).
- Závěr: pro Ridge ne. Regularizace dá vzdáleným stanicím malé váhy sama (viz graf vah) a ruční výběr modelu jen bere informaci, i na 12 h pomáhá vědět, co teče Prahou. Zjištění z NAPAD_LABE platilo pro regresi bez regularizace a jiné rozdělení. Tři varianty po sobě bez zlepšení o 1 cm, podle pravidel končím. Finální je v1.
- Soubory: `results/2026-10-23_1939_ridge_brany.json`, `src/models/ridge_brany.py`.

## pá 19:50 · Honza · vysvětlení: váhy a graf povodní
- Otázka: podle čeho model rozhoduje a dělá fyzikálně rozumnou věc?
- Graf `docs/grafy/ridge_vahy_decin.png` (a `ridge_vahy_usti.png`): váha každé stanice a zpoždění pro 12, 24 a 36 h, v cm na jednu směrodatnou odchylku vstupu. Co ukazuje:
  - Největší váhu má hladina v cíli teď (Děčín +24 h: +88) a hned za ní průtok v Praze teď (+49). Voda z Prahy doteče do Děčína zhruba za den, takže průtok v Praze teď je skoro přímo hladina v Děčíně za 24 h.
  - Čím delší horizont, tím větší váhu mají vzdálené stanice: na 12 h rozhoduje Mělník (+15) a Praha má jen +8, na 24 h Praha +49, na 36 h Praha +50 a k tomu Beroun +26, Louny +25, Sázava +20, Přelouč +16, Jizera +14. Stejné zjištění jako v NAPAD_LABE („čím dál dopředu, tím dál proti proudu“), jen si ho model našel sám přes váhy.
  - Záporné váhy u téže veličiny o pár hodin dřív (hladina před 1 h −31, Praha před 3 h −15) znamenají, že model počítá rozdíl, tedy trend: stoupá, nebo klesá, a jak rychle.
  - Průtok a hladina na téže stanici mají opačná znaménka (Děčín hladina +88, průtok −11): nesou skoro stejnou informaci (měrná křivka) a model si je navzájem dorovnává. Jednotlivé váhy se proto nečtou samostatně, jen jako celek.
- Graf `docs/grafy/ridge_povodne_decin_24h.png`: povodně 4/2006 a 1/2011 v Děčíně, skutečnost, „jako teď“ a předpověď vydaná 24 h předem. Model kopíruje stoupání i vrchol, „jako teď“ je o den pozadu. V 2011 se model na prudkém stoupání 14.–15. 1. opožďuje o několik hodin a vrchol 2006 (875 cm) má o 20 cm níž; 3. stupeň přesto hlásí den předem.
- Soubory: `src/grafy_ridge.py` (pustit `python src/grafy_ridge.py`), `docs/grafy/`.

## pá 19:56 · Dan · LightGBM c: zbytek po Ridge, přímky v listech, regularizace, zastavení tréninku
- Otázka: dá se přeučení a neschopnost stromů jít nad to, co viděly, obejít jinak než zjednodušením stromů?
- Data a rozdělení: společné rozdělení, všech 6 kombinací. Zastavení tréninku jen na letech 2017–2018 z trénovací části, validace se na něj nepoužije.
- Vstupy: jako c.
- Model a nastavení: (1) stromy se učí jen opravu Ridge, cíl = skutečnost − předpověď `zaklad_ridge`; (2) `linear_tree=True`, v listu přímka místo čísla; (3) 15 listů, `reg_lambda` 10, `colsample_bytree` 0,7; (4) zastavení, když se MAE na 2017–2018 nezlepší 50 stromů. Seed 42.
- Kde a jak dlouho: Dan, Yoga 7i, 2–8 s na model.
- Výsledek na val (`prumer_povodne`, c 22,8, Ridge 17,1): zbytek po Ridge 18,9, přímky v listech 111,8, regularizace 22,2, zastavení 22,4 (zastaveno po 63–212 stromech). Zbytek po Ridge má proti c navíc 2 plané poplachy před 2. stupněm (Děčín 24 a 36 h) a 1 propásnutou povodeň (Ústí 36 h).
- Závěr: neprošlo nic. Nejzajímavější je zbytek po Ridge: proti c pomohl o 3,9 cm, ale samotný Ridge zhoršil o 1,8 cm a přidal plané poplachy. Opravy, které se stromy naučí na povodních z tréninku, na jiné povodně nesedí. Přímky v listech při velké vodě ujely až o 3 m, protože přímka naučená na úzkém kousku dat se za jeho hranou nekontrolovaně prodlouží. Regularizace a zastavení pomohly jen o 0,4–0,6 cm, pod hranicí 1 cm. Zastavení se navíc řídí suchými roky 2017–2018 bez povodně, takže o povodních nic neví. Podle pravidel tady ladění končí, nejlepší LightGBM zůstává c.
- Soubory: `src/models/lgbm_c_ridge.py`, `src/models/lgbm_c_linear.py`, `src/models/lgbm_c_regularizace.py`, `src/models/lgbm_c_stop.py`, `results/2026-10-23_1953_lgbm_c_ridge.json`, `results/2026-10-23_1954_lgbm_c_linear.json`, `results/2026-10-23_1954_lgbm_c_regularizace.json`, `results/2026-10-23_1955_lgbm_c_stop.json`
## pá 20:00 · Ondra · neuronová síť (MLP), varianty v1–v4
- Otázka: přidá neuronová síť něco, co lineární model neumí?
- Data a rozdělení: společné rozdělení, opravená verze vyhodnocení (validační okna 16 dní, předstih nejvýš horizont, bias na povodních).
- Vstupy: všech 98 sloupců, odmocnina průtoků, StandardScaler. Cíl je změna hladiny (y − hladina teď), škálovaná.
- Model a nastavení: `MLPRegressor`, early stopping, max 300 epoch, seed 42. MacBook M1, 10–40 s na jeden trénink.
- Výsledek na val (`prumer_povodne`, propásnuto + plané poplachy u 2. stupně, součet přes 6 kombinací):
  - „jako teď“: 44,3 cm, propásne všech 24 nástupů povodní
  - v1 `mlp_v1` (64-32, alpha 0,0001): 26,0 cm, 4. Přeučená: na tréninku při velké vodě chyba 5 cm, na validaci 22 cm (Děčín +24 h).
  - v2 `mlp_alpha1` (alpha 1 proti přeučení): 18,7 cm, 2. Zlepšení o 7,3 cm.
  - v3 `mlp` (větší síť 128-64): 17,8 cm, 1. Zlepšení jen o 0,9 cm, pod hranicí 1 cm.
  - v4 `mlp_vahy` (hodiny nad 1. stupněm s váhou 5, protože síť na povodních podhodnocovala): 18,2 cm, 1. Bez zlepšení.
  - mřížka na Děčín +24 h (3 velikosti × alpha 0,0001–10): nejlepší alpha 1, alpha 10 už je málo přizpůsobivá.
  - stabilita v3, seedy 42 / 43 / 44: 18,1 / 19,0 / 18,3 cm (před opravou vyhodnocení), rozptyl 0,9 cm.
- Závěr: hlavní byl boj s přeučením, regularizace pomohla nejvíc. v2 a v3 jsou v rámci náhody stejné. Jako hlavní necháváme v3, protože má méně chyb ve varování a menší podhodnocení na 36 h. v2 je rovnocenná jednodušší záloha. Po dvou variantách bez zlepšení konec ladění. Síť nejvíc používá hladinu v Děčíně a Ústí a průtok v Praze, Vraňanech, Lounech, Mělníku a Kostelci, vzdálené přítoky málo (`docs/grafy/mlp_dulezitost_stanic.png`). Graf povodně 1/2011 (`docs/grafy/mlp_povoden_2011.png`): síť stoupání předbíhá o 24 h, „jako teď“ je o 24 h pozadu.
- Soubory: `src/models/mlp.py`, `mlp_v1.py`, `mlp_alpha1.py`, `mlp_vahy.py`, `src/vysvetli_mlp.py`, `results/*_mlp*.json`.
## pá 19:48 · Tobias · fyzikální model, finální varianta a grafy
- Nejlepší varianta (3 vrstvy stanic) je teď `src/models/fyzika.py`, první verze se dvěma vrstvami zůstává pro srovnání jako `src/models/fyzika_dve_vrstvy.py`. Po přejmenování znovu spuštěno: `prumer_povodne` 24,8 a 26,6 cm, stejně jako předtím.
- `docs/grafy/fyzika_merna_krivka.png`: měrná křivka Děčína se stupni povodňové aktivity. Body z povodní leží přesně na křivce, nad 3 710 m³/s (nejvyšší průtok v tréninku) je křivka prodloužená přímkou.
- `docs/grafy/fyzika_vetve.png`: tři větve (Vltava, Labe, Ohře) s dobami putování mezi stanicemi a do Děčína. Nejdál dopředu vidí Beroun a Přelouč, 24 h.
- `docs/grafy/fyzika_povoden_2006.png`: validační povodeň 2006, Děčín +24 h. Při stoupání model sleduje skutečnost, „jako teď“ se opožďuje o celý den. Těsně před vrcholem model krátce přestřelí asi o 50 cm, při opadání se opožďuje.

## pá 20:00 · Dan · LightGBM finální varianta (lgbm = c), seedy a SHAP
- Otázka: je výsledek c stabilní a podle čeho model rozhoduje?
- Data a rozdělení: společné rozdělení, všech 6 kombinací; SHAP pro Děčín +24 h na validaci.
- Vstupy: jako c.
- Model a nastavení: `src/models/lgbm.py` je c (500 stromů, learning_rate 0,05, 31 listů), seedy 42, 43, 44.
- Kde a jak dlouho: Dan, Yoga 7i, 5–7 s na model, SHAP pár sekund.
- Výsledek na val: `prumer_povodne` 22,8 se všemi třemi seedy na desetinu stejně (bez náhodného výběru řádků a vstupů v LightGBM náhoda není). Regularizace se seedy 22,0–22,2, takže její zlepšení o 0,6–0,8 cm je skutečné, ale pod hranicí 1 cm. Chyba „jen při vysoké vodě“ (nad 1. stupněm, Děčín +12 / +24 / +36 h): 10,8 / 24,3 / 42,3 cm, Ridge 9,0 / 16,8 / 29,6, „jako teď“ 25,7 / 51,0 / 74,5. Varování před 1. stupněm (400 cm) nic nepropásl, předstih 8 / 21 / 46 h.
- Závěr: SHAP ukazuje, že model dělá fyzikálně rozumnou věc. Pro Děčín za 24 h rozhoduje hlavně přírůstek průtoku v Praze (voda, která Prahou už protekla a do Děčína ještě nedotekla), při povodni 2011 v průměru 19 cm vlivu, pak Přelouč, Louny a Ústí. Za klidu rozhoduje hlavně stav v Děčíně za poslední hodiny. Graf povodně 2011 ukazuje slabinu: při rychlém stoupání LightGBM přestřelí asi o 70 cm (800 proti 730 cm) a skáče, Ridge jde hladce.
- Soubory: `src/models/lgbm.py`, `results/2026-10-23_2000_lgbm.json`, `docs/grafy/lgbm_shap.png` (podle čeho rozhoduje, celá validace a povodeň 2011), `docs/grafy/lgbm_c_povoden2011.png` (skutečnost, „jako teď“, c, Ridge a zbytek po Ridge při povodni 2011, +24 h)
## pá 20:15 · Ondra · srovnání čtyř modelů na jednom počítači
- Otázka: který ze čtyř přístupů předpovídá hladinu na povodních nejlíp?
- Data a rozdělení: společné rozdělení, opravená verze vyhodnocení. Nejlepší varianta každého přepočítaná na MacBooku M1 z kódu v Gitu: `ridge` (Honza), `mlp` (Ondra), `lgbm_c` (Dan), `fyzika` (Tobias), `jako_ted`.
- Výsledek na val (průměr přes 6 kombinací cíle a horizontu; propásnuto a plané poplachy jsou součet u 2. stupně):

  | Model | Chyba na povodních | Chyba celkem | Bias na povodních | Propásnuto | Plané poplachy | Předstih 2. stupně | Trénink všech 6 |
  |---|---|---|---|---|---|---|---|
  | lineární regrese | 17,1 cm | 8,2 cm | −5,1 cm | 0 | 0 | 17,4 h | 1 s |
  | neuronová síť | 17,8 | 8,3 | −7,5 | 0 | 1 | 19,5 h | 99 s |
  | LightGBM | 23,1 | 9,4 | −6,2 | 0 | 0 | 14,2 h | 21 s |
  | fyzikální | 24,8 | 11,9 | −5,0 | 0 | 0 | 16,2 h | 3 s |
  | „jako teď“ | 44,3 | 12,8 | −14,7 | 24 z 24 | 0 | 0 h | 0 s |

  Podíl předpovědí do ±20 cm při vodě nad 1. stupněm (+12 / +24 / +36 h): lineární 88 / 76 / 51 %, síť 90 / 64 / 49 %, LightGBM 85 / 61 / 37 %, fyzikální 76 / 53 / 35 %, „jako teď“ 51 / 23 / 13 %.
- Závěr: všechny čtyři modely jsou na povodních zhruba o polovinu lepší než „jako teď“ a žádný nepropásl povodeň. Lineární regrese a síť jsou v rámci náhody stejné (rozdíl 0,7 cm, rozptyl sítě mezi seedy 0,9 cm). Lineární regrese je ale nejjednodušší, nejrychlejší, nemá planý poplach a každou váhu vysvětlíme. LightGBM přestřeluje vrcholy nad rámec tréninku (1/2011 o 60 cm na 24 h, `docs/grafy/povoden_2011-01_decin_24h.png`). Fyzikální model ukazuje, že učené modely nedělají nic magického, jen fyziku zpřesňují. Na 36 h jsou všechny výrazně horší, bez srážek dál nevidíme.
- Soubory: `results/*.json` (otisk verze v JSON), `docs/grafy/srovnani_ctyr_modelu.png`, `docs/grafy/povoden_2011-01_decin_24h.png`, `docs/grafy/povoden_2006-03_decin_36h.png`, skripty `src/graf_srovnani.py` a `src/graf_povoden.py`.

## pá 20:15 · Dan · LightGBM a základy znovu na opravené verzi dat a vyhodnocení
- Otázka: platí moje výsledky i po Ondrově opravě dat a vyhodnocení (pá 19:58)?
- Data a rozdělení: nová verze (Děčín 5.–8. 2. 2006 vyřazen, bez doplňování děr, validační okno 16 dní před vrcholem, předstih nejvýš horizont). Všech 14 mých modelů a „jako teď“ znovu.
- Vstupy, model a nastavení: beze změny, seed 42.
- Kde a jak dlouho: Dan, Yoga 7i, všechno po sobě 10 min.
- Výsledek na val (`prumer_povodne`): „jako teď“ 44,3, trend 39,4, Ridge 17,1, LightGBM v1 66,8, v2 40,8, a 24,3, c 23,1 (stejně jako Ondrovi na Macu), zbytek po Ridge 18,7, list 200 hodin 22,1, regularizace 22,2, zastavení 22,2, 7 listů 23,0, monotónní 23,8, přímky v listech 97,8. Děčín, chyba na povodních +12 / +24 / +36 h: c 10,2 / 21,3 / 36,4 cm, Ridge 9,0 / 15,5 / 26,0, „jako teď“ 23,0 / 44,4 / 65,6.
- Závěr: závěry platí. List 200 hodin je teď lepší o 0,97 cm (bez zaokrouhlení 23,08 → 22,11), tedy těsně pod hranicí 1 cm, a v Děčíně přidal plané poplachy před 1. a 3. stupněm, takže neprošel. Nejlepší LightGBM je c, na povodních o 6,0 cm horší než Ridge. Grafy `lgbm_c_povoden2011.png` a `lgbm_shap.png` jsou překreslené z nové verze.
- Soubory: `results/2026-10-23_2004*` až `_2015*` (otisk verze v JSON). Moje starší `results/*.json` byly zapsané v kódování cp1250 a nový `porovnej.py` je nepřečetl, převedl jsem je do UTF-8 beze změny obsahu.
## pá 20:00 · Dan · LightGBM finální varianta (lgbm = c), seedy a SHAP
- Otázka: je výsledek c stabilní a podle čeho model rozhoduje?
- Data a rozdělení: společné rozdělení, všech 6 kombinací; SHAP pro Děčín +24 h na validaci.
- Vstupy: jako c.
- Model a nastavení: `src/models/lgbm.py` je c (500 stromů, learning_rate 0,05, 31 listů), seedy 42, 43, 44.
- Kde a jak dlouho: Dan, Yoga 7i, 5–7 s na model, SHAP pár sekund.
- Výsledek na val: `prumer_povodne` 22,8 se všemi třemi seedy na desetinu stejně (bez náhodného výběru řádků a vstupů v LightGBM náhoda není). Regularizace se seedy 22,0–22,2, takže její zlepšení o 0,6–0,8 cm je skutečné, ale pod hranicí 1 cm. Chyba „jen při vysoké vodě“ (nad 1. stupněm, Děčín +12 / +24 / +36 h): 10,8 / 24,3 / 42,3 cm, Ridge 9,0 / 16,8 / 29,6, „jako teď“ 25,7 / 51,0 / 74,5. Varování před 1. stupněm (400 cm) nic nepropásl, předstih 8 / 21 / 46 h.
- Závěr: SHAP ukazuje, že model dělá fyzikálně rozumnou věc. Pro Děčín za 24 h rozhoduje hlavně přírůstek průtoku v Praze (voda, která Prahou už protekla a do Děčína ještě nedotekla), při povodni 2011 v průměru 19 cm vlivu, pak Přelouč, Louny a Ústí. Za klidu rozhoduje hlavně stav v Děčíně za poslední hodiny. Graf povodně 2011 ukazuje slabinu: při rychlém stoupání LightGBM přestřelí asi o 70 cm (800 proti 730 cm) a skáče, Ridge jde hladce.
- Soubory: `src/models/lgbm.py`, `results/2026-10-23_2000_lgbm.json`, `docs/grafy/lgbm_shap.png` (podle čeho rozhoduje, celá validace a povodeň 2011), `docs/grafy/lgbm_c_povoden2011.png` (skutečnost, „jako teď“, c, Ridge a zbytek po Ridge při povodni 2011, +24 h)

## pá 20:20 · Ondra · finální srovnání čtyř modelů v procentech a průměr dvou nejlepších
- Otázka: jak dopadne Danův finální LightGBM (`lgbm`) a pomůže zprůměrovat dva nejlepší modely?
- Data a rozdělení: společné rozdělení, aktuální verze vyhodnocení, vše přepočítané na MacBooku M1.
- Výsledek na val: `lgbm` 23,1 cm (stejné jako varianta c, ze které vychází). Pořadí: lineární regrese 17,1, síť 17,8, LightGBM 23,1, fyzikální 24,8, „jako teď“ 44,3. Do ±20 cm při vodě nad 1. stupněm: 72 / 67 / 61 / 55 / 29 %. Všechny čtyři modely zachytily 24 z 24 nástupů povodní. Průměr lineární regrese a sítě: 16,9 cm, 71 % do ±20 cm, tedy zlepšení o 0,2 cm, pod hranicí 1 cm.
- Závěr: lineární regrese vede. Průměrování modelů nepomáhá a jen by přidalo složitost. Čtyři různé přístupy na stejných vstupech skončily blízko sebe, takže rezervu nemá model, ale vstupy (chybí srážky).
- Soubory: `src/procenta.py`, `docs/grafy/srovnani_procenta.png`, `docs/grafy/srovnani_ctyr_modelu.png`, `results/*_lgbm.json`.

## pá 20:45 · Dan · doba doběhu podle průtoku (lgbm_doba, ridge_doba)
- Otázka: zlepší předpověď, když doba doběhu z každé stanice nebude stálá, ale bude záviset na průtoku v Ústí v čase předpovědi (při povodni se vlna rozlije do nivy a zpomalí)?
- Data a rozdělení: společné rozdělení, všech 6 kombinací. Doby změřené jen na trénovací části (`src/doba_dobehu.py`, největší korelace změn průtoku za 6 h zvlášť v pásmech průtoku v Ústí 0–300, 300–800, 800–1500 a nad 1500 m³/s).
- Ověření Ondrovy tabulky na trénovací části (Mělník, Praha, Louny → Ústí a Ústí → Děčín, pásma zleva doprava): Mělník 8 / 8 / 10 / 17 h (Ondra 8 / 9 / 10 / 16), Praha 13 / 13 / 14 / 39 (stejně), Louny 13 / 12 / 15 / 10 (Ondra 13 / 12 / 14 / 23), Ústí → Děčín 5 / 3 / 3 / 2 (Ondra 5 / 4 / 3 / 3). Nad 1500 m³/s je v tréninku jen 227 hodin a všechny z června 2013, povodně 2006 a 2011 jsou ve validaci. Několik stanic tam má nejlepší posun na hraně 48 h, číslo je tedy spíš tvar jedné povodně než doba doběhu. Pod 300 m³/s mají vzdálené stanice korelaci jen 0,05–0,11 (malé změny přehluší jezy) a vychází nesmysly jako Kostelec → Děčín 0 h.
- Vstupy: jako c, jen „průtok, který dorazí za h hodin“ a „průtok, který dotéká teď“ se berou se zpožděním podle pásma (zaokrouhleno na zpoždění v X). Pásmo s korelací pod 0,2 nebo s méně než 1 000 hodinami dostalo dobu ze sousedního pásma, takže nad 1 500 m³/s platí doby z pásma 800–1500. Kontrola: se stálou dobou ve všech pásmech dávají vstupy přesně `lgbm_c`. Po zaokrouhlení se zpoždění změní u 20–43 % vstupů, hlavně u vedlejších stanic (Kostelec, Nymburk, Sázava, Beroun) a u Ústí při klidné vodě.
- Model a nastavení: `lgbm_doba` = c s dobou podle pásma. `ridge_doba` = stejné vstupy, průtoky pod odmocninou ještě před rozdílem, StandardScaler + Ridge alpha 1, cíl hladina jako `ridge.py`. `ridge_doba_stala` = totéž se stálou dobou, aby šlo oddělit, co přinese samotné pásmo. Seed 42.
- Kde a jak dlouho: Dan, Yoga 7i, LightGBM 5–6 s, Ridge pod 1 s na model.
- Výsledek na val (`prumer_povodne`): `lgbm_doba` 23,1 proti `lgbm_c` 23,1, varování stejná (nic nepropásl, žádný planý poplach). `ridge_doba` 21,8 proti `ridge_doba_stala` 22,2, obojí výrazně horší než `ridge.py` 17,1, hlavně v Ústí (bias na povodních −17 až −30 cm). Před 2. stupněm propásl `ridge_doba` 1 povodeň (Ústí +36 h), `ridge_doba_stala` 3 (Ústí +12, +24 a +36 h) a 1 planý poplach (Děčín +24 h), `ridge.py` žádnou.
- Závěr: doba podle průtoku nepomohla. U LightGBM vůbec nic, u Ridge 0,4 cm, pod hranicí 1 cm. Fyzikálně čekané zpomalení vlny při povodni z trénovacích dat změřit nejde, nad 1 500 m³/s je jediná povodeň (2013). Do 1 500 m³/s se doby mění jen o 1–4 h, přitom zpoždění v X jsou po 3–12 h. LightGBM si navíc umí rozdělit data podle průtoku v Ústí sám. Druhé zjištění: lineární model je lepší s 98 syrovými zpožděními (17,1) než s jedním ručně vybraným zpožděním na stanici (22,2). Váhy přes všechna zpoždění si dobu doběhu najdou samy a zachytí i roztažení vlny, výběr jednoho zpoždění tuhle informaci zahodí.
- Soubory: `src/doba_dobehu.py` (funkce `doby_pasma`), `src/models/lgbm_doba.py`, `src/models/ridge_doba.py`, `src/models/ridge_doba_stala.py`, `results/2026-10-23_204029_lgbm_doba.json`, `results/2026-10-23_204113_ridge_doba_stala.json`, `results/2026-10-23_204122_ridge_doba.json`
## pá 20:44 · Ondra · srážky, sníh a teplota z 25 stanic v povodí
- Otázka: pomůže modelu informace o vodě, která v řece ještě není (déšť, sníh, tání)?
- Data a rozdělení: denní archiv ČHMÚ, 25 stanic (10 Vltava, 9 horní Labe, 6 Ohře), 2006–2025. Pro každou větev průměr stanic: srážky za poslední den a 3 dny, index předchozích srážek API30, výška sněhu, změna sněhu za 3 dny, průměrná teplota. 18 sloupců, každá hodnota až od chvíle, kdy byla změřená (denní úhrn s časem D 06:00 je déšť do D+1 06:00, bereme ho od D+1 07:00; ověřeno na hodinových srážkách v Praze). Společné rozdělení.
- Model a nastavení: `ridge` a `mlp` beze změn, jen s 18 sloupci navíc.
- Výsledek na val (`prumer_povodne`): lineární regrese bez meteo 17,1 cm, se vším 17,4, jen srážky 17,1, jen sníh a teplota 17,3. Neuronová síť bez meteo 17,8, se vším 21,2 (přeučila se, na 36 h 25,7 → 31,7 cm a přibyly 3 chyby ve varování).
- Myšlenkový pokus, jako bychom srážky znali o den dřív (dokonalá předpověď na zítřek, do modelu se nesmí): lineární regrese 16,3 cm, zlepšení jen o 0,8 cm.
- Závěr: nepomohlo, do společných vstupů meteo nepřidáváme. Většinu vlivu deště a sněhu už model vidí v průtocích proti proudu, protože na horizontech 12–36 h je voda z velkých dešťů už v řekách. Denní srážky jako průměr za povodí jsou navíc hrubé. Ani dokonalá předpověď na den dopředu nepřekročí naši hranici 1 cm. Síť s víc vstupy a stejným počtem povodní se přeučí. Pomoct by mohly hodinové srážky (ČHMÚ je má až od 2018, na trénink málo) a víc povodní.
- Soubory: `src/stahni_chmu_meteo.py`, `src/meteo.py`, `src/pokus_meteo.py`, `data/external/labe_meteo.parquet`, `data/external/labe_meteo_o_den_driv.parquet` (jen myšlenkový pokus).
## pá 20:40 · Honza · odhad nejistoty předpovědi
- Otázka: jak široké rozmezí máme k předpovědi říkat, aby se do něj skutečnost většinou vešla?
- Data a rozdělení: společné. Chyby Ridge na trénovací části podle pásma hladiny teď (0–300, 300–450, 450–600, nad 600 cm), 5. a 95. percentil. Pokrytí ověřeno na validaci, kterou při odhadu rozmezí model nevidí.
- Výsledek na val: do rozmezí se vešlo 89–92 % hodnot celkem, na povodních 76–88 % (12 h 87–88 %, 24 h 79–84 %, 36 h 76–78 %). Šířka rozmezí na povodních: Děčín 33 / 53 / 72 cm, Ústí 61 / 77 / 82 cm. Pásmo nad 600 cm v Ústí má v tréninku málo řádků (hlavně 2013), proto je tam dolní mez −83 až −91 cm.
- Závěr: na klidné vodě rozmezí sedí (9 z 10), na povodních je o něco užší, než by mělo (8 z 10), protože validační povodně jsou vyšší než trénovací. Tak to i říkáme. V aplikaci „nejspíš od–do“ u každé předpovědi a modrý pás v grafu.
- Soubory: `src/nejistota.py`, `models/ridge_intervaly.json`, `app/predikce.py` (`interval`).

## pá 20:44 · Honza · kolik let dat a které stanice potřebuje Ridge
- Otázka: stačí dvě léta a tři stanice z kraje, nebo pomůže delší historie a stanice proti proudu?
- Data a rozdělení: společná tabulka a `casti`, stejná validace pro všech 12 variant (4 vynechané povodně 2006–2011 a klid 2019–2020). Trénink posledních 1, 2, 3, 5, 8 a 13 let do konce 2018, vždy jen část `train`. Do okna musí vejít i nejstarší vstup 36 h zpět a cílová hladina; u krátkých oken proto vypadne prvních 36 hodin. Test 2021–2025 nepoužit.
- Vstupy: jen kraj = Děčín, Ústí, Louny (35 sloupců); všechny stanice = 98 sloupců. Úplné řádky i validace jsou pro obě sady stejné. Dva roky jsou 2017–2018, nikoli skutečný balíček 2024–2026.
- Model a nastavení: nezměněný `ridge.fit`, odmocnina průtoků, StandardScaler a Ridge(alpha=1), přímá předpověď hladiny. Bez ladění parametrů, seed 42 (Ridge je zde deterministický).
- Kde a jak dlouho: Honzův Windows notebook, 72 tréninků, celý běh včetně vyhodnocení 17,4 s.
- Výsledek na val: chyba je průměr `mae_povodne` přes 6 kombinací cíle a horizontu; varování jsou součty pro 2. stupeň.

  | Let | Trénovací roky | Jen kraj, cm | Všechny stanice, cm | Propásnuto kraj / všechny | Plané poplachy kraj / všechny |
  |---|---|---|---|---|---|
  | 1 | 2018 | 39,1 | 29,2 | 9 / 2 | 0 / 0 |
  | 2 | 2017–2018 | 44,6 | 26,9 | 12 / 4 | 0 / 0 |
  | 3 | 2016–2018 | 35,6 | 25,0 | 9 / 3 | 1 / 0 |
  | 5 | 2014–2018 | 34,2 | 21,0 | 10 / 3 | 1 / 0 |
  | 8 | 2011–2018 | 27,2 | 16,6 | 0 / 0 | 2 / 0 |
  | 13 | 2006–2018 | 27,8 | 17,1 | 0 / 0 | 2 / 0 |

  „Bude jako teď“: 44,3 cm, propásne 24 z 24 případů, žádný planý poplach. Jmenovatel 24 znamená 4 povodně × 2 cíle × 3 horizonty, nikoli 24 různých povodní. Kontrola `jako_ted --rychle`: Děčín +24 h 44,4 cm, jak má být.
- Závěr: dva roky všech stanic mají podobnou chybu jako 13 let jen z kraje (26,9 proti 27,8 cm, rozdíl pod 1 cm), ale ještě propásnou 4 varování. Stanice proti proudu tedy pomáhají výrazně; dlouhá historie navíc přináší zkušenost s vysokou vodou. Všechna okna do pěti let nemají v tréninku ani jednu hodinu na 2. stupni, osmileté a třináctileté okno zahrnuje povodeň 2013. Se všemi stanicemi má 8 i 13 let nulová propásnutí i plané poplachy, proti základu je chyba menší zhruba o 62 %.
- Slabiny: 8 let proti 13 zlepšilo chybu jen o 0,47 cm, pod naší hranicí 1 cm; finální model ani délku jeho tréninku podle toho neměníme. Počet let zároveň mění zastoupení povodní, nejde o čistý účinek počtu hodin. Validace má jen čtyři vynechané povodně, které mohou být starší než trénink; jde o retrospektivní srovnání, ne dopředný test ani důkaz, že všude stačí osm let. Krátké modely mají na tréninku celkovou chybu 4,9–11,6 cm a na celé validaci 5,2–17,2 cm; tyto převážně klidné hodiny samy neříkají, jak dopadnou povodně.
- Ověření: nezávislá kontrola masek všech 36 kombinací okna/cíle/horizontu, stejné indexy validace, 13 let přesně odpovídá celému train a reprodukuje Ridge 17,1 cm. Společné moduly i model zůstaly beze změn. Verze vyhodnocení na Windows `69a6db32`; JSON navíc ukládá otisky zdrojů se sjednocenými konci řádků.
- Soubory: `src/kolik_dat.py`, `docs/grafy/kolik_dat.png`, `results/kolik_dat/2026-10-23_204319_kolik_dat.json` a `.csv`, kontrola `results/2026-10-23_204140_jako_ted.json`. Spuštění `python src/kolik_dat.py`; samotný graf z uloženého výsledku přes `--graf-ze <JSON>`. Výsledky pokusu jsou v podsložce, aby nepřepsaly oficiální Ridge v `porovnej.py --prehled`.
## pá 20:55 · Honza · kolik let dat model potřebuje (učicí křivka)
- Otázka: proč nestačil balíček pořadatelů (2 roky, jen kraj)? Jak se chyba mění s délkou historie a sadou stanic?
- Data a rozdělení: společné; trénink omezený na posledních N let před validací (2019 − N až 2018), N = 1, 2, 3, 5, 8, 13; validace stejná. Dvě sady vstupů: jen kraj (Děčín, Ústí, Louny, 35 sloupců) a všechny stanice (98 sloupců).
- Model a nastavení: `ridge.fit` beze změn (odmocnina průtoků, StandardScaler, Ridge alpha 1).
- Kde a jak dlouho: notebook, 72 tréninků za minutu.
- Výsledek na val (`prumer_povodne` v cm, v závorce propásnuté nástupy povodní u 2. stupně z 24): jen kraj: 1 rok 39,2 (9), 2 roky 45,1 (12), 3 roky 35,6 (9), 5 let 34,2 (10), 8 let 27,2 (0), 13 let 27,8 (0). Všechny stanice: 1 rok 28,3 (2), 2 roky 26,9 (4), 3 roky 24,8 (3), 5 let 21,0 (3), 8 let 16,6 (0), 13 let 17,1 (0). „Jako teď“ 44,3.
- Závěr: 1) Stanice proti proudu pomohly víc než roky: 2 roky se všemi stanicemi (26,9) jsou lepší než 13 let jen s krajem (27,8). 2) Rozhoduje, jestli je v tréninku velká povodeň: v letech 2014–2018 žádná nad 2. stupněm nebyla, modely z 1–5 let proto propásnou 2–12 nástupů z 24; jakmile je v tréninku povodeň 2013 (8 let, 409 hodin nad 2. stupněm v Děčíně), propásnuté klesnou na 0. 3) Balíček (2 roky, jen kraj) by dal 45 cm, tedy nic lepšího než „jako teď“, a propásl polovinu povodní. 4) 8 let (16,6) a 13 let (17,1) je totéž v rámci náhody. Potvrzuje zjištění z NAPAD_LABE na společném rozdělení.
- Soubory: `src/kolik_dat.py`, `docs/grafy/kolik_dat.png`.

## pá 20:46 · Honza · sjednocení dvou běhů učicí křivky
- Při synchronizaci se sešly dva nezávislé běhy stejného úkolu. Verze v záznamu „20:55“ omezila rok vydání předpovědi, takže u 1, 2, 3 a 5 let ještě prvních 36 řádků čerpalo z předchozího roku. Verze v tabulce „20:44“ hlídá i nejstarší vstup a tyto řádky vynechává; tu používá výsledný skript a graf. Žádná z verzí netrénovala na validaci ani testu.
- Proto se krátká okna mírně liší: dva roky jen kraje 45,1 → 44,6 cm, jeden rok všech stanic 28,3 → 29,2 cm. U 8 a 13 let jsou výsledky stejné a počet propásnutí je stejný všude. Ve výsledném grafu zůstávají i popisky propásnutých varování ze souběžné verze.
- Upřesnění závěru pro porotu: 26,9 proti 27,8 cm je rozdíl pod 1 cm, takže říkáme „podobná chyba“, nikoli jasné vítězství. Hodnota 44,6 cm patří krajským stanicím v letech 2017–2018, ne skutečnému balíčku 2024–2026; z tohoto pokusu nelze tvrdit, jak by dopadlo učení na samotném balíčku. Delší historie nám také dovoluje ověřovat na více povodních.
- Uloženy jsou všechny metriky a otisky pro opakování pokusu v `results/kolik_dat/2026-10-23_204319_kolik_dat.json`; graf lze překreslit bez trénování. Společný model zůstává beze změny.

## pá 20:50 · Honza · Ridge s větší váhou povodňových hodin
- Otázka: hodnotíme chybu na povodních, ale model se učí na všech hodinách a nad 1. stupněm povodňové aktivity je v tréninku jen 2,2 % hodin (Děčín) a 1,5 % (Ústí). Pomůže, když jim při tréninku dáme větší váhu?
- Data a rozdělení: společné rozdělení, všech 6 kombinací, verze vyhodnocení `69a6db32`.
- Vstupy: 98 sloupců jako `ridge`.
- Model a nastavení: postup z `ridge.py` (odmocnina průtoků, StandardScaler, Ridge alpha 1), Ridge navíc dostane váhy řádků (`sample_weight`): 1, když je hladina teď pod 1. stupněm (Děčín 400 cm, Ústí 450 cm), jinak 5 (`ridge_vahy`) nebo 20 (`ridge_vahy20`). Škálování se váhami neřídí.
- Kde a jak dlouho: Honzův notebook, pod sekundu na model.
- Výsledek na val (chyba na povodních, Děčín +12 / +24 / +36 h, Ústí +12 / +24 / +36 h):
  - `ridge`: 9,0 / 15,5 / 26,0, Ústí 9,6 / 15,7 / 26,7; `prumer_povodne` 17,1 cm, `mae` 8,2 cm, bias na povodních −5,1 cm
  - váha 5: 8,9 / 15,2 / 26,9, Ústí 9,3 / 15,3 / 27,4; 17,2 cm, `mae` 8,4 cm (o 0,2 horší), bias −8,1 cm
  - váha 20: 9,7 / 16,3 / 29,5, Ústí 9,9 / 16,4 / 29,4; 18,5 cm, `mae` 8,9 cm (o 0,7 horší), bias −11,2 cm
  - varování: obě varianty 0 propásnutých povodní a 0 planých poplachů jako `ridge`, ale předstih 2. stupně 16,8 a 16,4 h místo 17,4 h a chyba vrcholu 11,8 a 15,8 cm místo 10,0 cm. „Jako teď“ 44,3 cm.
- Proč to nepomohlo (ověřeno): hodiny s vysokou hladinou teď jsou hlavně kolem vrcholu a při opadání. V tréninku z nich hladina v Děčíně za 24 h v 71 % případů klesne (průměrně o 12 cm), za 36 h v 76 % (o 22 cm). Váha model naučí „vysoká voda teď, bude klesat“ a posune předpovědi na povodních dolů o 2–5 cm. Při opadání to trochu pomůže, při stoupání podhodnocuje ještě víc: Děčín +24 h bias při stoupání −7 cm u `ridge`, −12 cm s váhou 5.
- Kde dělá chybu (váha 5, u `ridge` skoro stejně): největší díl chyby na povodních má povodeň 9/2010 (33 %, průměrná chyba 22 cm), pak 1/2011 (25 %, 17 cm), 4/2006 (24 %, 17 cm) a 3/2009 (18 %, 12 cm). V 9/2010 model soustavně podhodnocuje (Děčín +24 h o 18 cm, +36 h o 31 cm), nejspíš déšť blízko kraje, který stanice proti proudu nevidí (domněnka). Podle horizontu dělá 36 h 53 % chyby, 24 h 30 % a 12 h 18 %. Váha 5 pomohla jen povodni 4/2006 (17,7 → 16,6 cm), ostatním mírně uškodila.
- Závěr: neprošlo. Váha 5 je proti `ridge` v rámci náhody stejná (+0,1 cm), váha 20 je horší o 1,4 cm a obě zhoršily klidnou vodu, předstih a vrcholy. Finální zůstává `ridge`. Kdyby se to zkoušelo znovu, váha by se dala odvodit od skutečné hladiny za h hodin místo hladiny teď, pak by se zvýraznilo i stoupání (nezkoušeno).
- Soubory: `src/models/ridge_vahy.py`, `src/models/ridge_vahy20.py`, `results/2026-10-23_204657_ridge_vahy.json`, `results/2026-10-23_204702_ridge_vahy20.json`, `results/predpovedi/ridge_vahy.parquet`, `results/predpovedi/ridge_vahy20.parquet`.

## pá 21:00 · Ondra · finální test 2021–2025
- Otázka: jak finální model (lineární regrese, vybraná pá 20:58 před testem) funguje na povodních, které nikdo z nás neviděl ani při ladění?
- Data a rozdělení: model natrénovaný na všem do konce 2020 (train i validace), test 2021–2025: povodně 2/2021, 12/2023, 2/2024 a 9/2024. Spuštěno jednou (`python src/porovnej.py jako_ted ridge fyzika lgbm mlp --test`). Ostatní tři přístupy jen pro srovnání, výběr se podle testu nemění.
- Výsledek na testu (`prumer_povodne`; do ±20 cm při vodě nad 1. stupněm; zachycené nástupy povodní před 2. stupněm; plané poplachy):
  - lineární regrese (finální): 22,4 cm, o 55 % méně než „jako teď“, 66 % do ±20 cm (12 / 24 / 36 h: 89 / 67 / 43 %), zachyceno 17 z 21, 3 plané poplachy
  - neuronová síť: 21,3 cm, 59 %, 70 %, 20 z 21, 2
  - LightGBM: 24,0 cm, 54 %, 66 %, 21 z 21, 4
  - fyzikální: 27,1 cm, 45 %, 61 %, 21 z 21, 2
  - „jako teď“: 50,2 cm, 0 %, 36 %, 0 z 21
- Propásnutá varování lineární regrese jsou hraniční: 3 z 4 jsou únor 2024 v Děčíně, kdy voda 2. stupeň (490 cm) přesáhla jen o 6 cm a model předpověděl 474–489 cm. Čtvrté je Ústí +12 h o Vánocích 2023 (předpověď 528 cm, hranice 530). Před 3. stupněm varoval pokaždé.
- Povodeň Boris 9/2024, Děčín: 3. stupeň překročen 15. 9. 12:00 UTC, model varoval 10 h (předpověď na 12 h), 27 h (24 h) a 30 h (36 h) předem. Vrchol 649 cm předpověděl 24 h předem na 611 cm. Vánoce 2023: 3. stupeň varován 13 / 21 / 29 h předem, vrchol 624 cm předpovězen na 614 cm.
- Závěr: na testu je chyba o 5 cm větší než na validaci (22,4 proti 17,1 cm), ale i „jako teď“ je na testu horší (50,2 proti 44,3), testové povodně stoupaly rychleji. Zlepšení proti laťce je podobné (55 % proti 61 %), model tedy na nových povodních funguje. Síť vyšla na testu o 1,1 cm lépe než lineární regrese, na validaci o 0,7 cm hůř. Rozdíl mezi nimi je náhoda, výběr neměníme. Všechny modely na testu podhodnocují vrcholy (bias −3 až −27 cm), nejvíc na 36 h.
- Soubory: `results/*_test.json`, `results/predpovedi/*_test.parquet`, `docs/grafy/srovnani_procenta_test.png`, `docs/grafy/povoden_2024-09_decin_24h.png`, `docs/grafy/povoden_2023-12_decin_24h.png`.

## pá 22:29 · Ondra · dokonalá předpověď deště po horizontech
- Otázka: pomohla by předpověď srážek aspoň na delším horizontu, kde chyba roste nejvíc? Pokus z pá 20:44 jsme měli jen jako průměr.
- Data a rozdělení: stejné jako pá 20:44, `data/external/labe_meteo_o_den_driv.parquet` (srážky o den dřív, než je známe, tedy jako dokonalá předpověď na zítřek, do modelu se nesmí). Jen validace, test se nepouštěl.
- Model a nastavení: `ridge` beze změny, `python src/pokus_meteo.py --o-den-driv --jen-ridge`.
- Kde a jak dlouho: MacBook M1, pár sekund.
- Výsledek na val (chyba na povodních, bez meteo → s dokonalými srážkami): Děčín +12 h 9,0 → 8,7, +24 h 15,5 → 14,6, +36 h 26,0 → 24,9 cm; Ústí 9,6 → 9,4, 15,7 → 14,8, 26,7 → 25,6 cm. Sníh a teplota s dokonalou znalostí model zhoršily o 0,0–0,5 cm.
- Závěr: i na 36 h by dokonalá předpověď deště ubrala jen 1,1 cm z 26 cm (4 %). Déšť, který spadne zítra, dorazí do Děčína většinou až za víc než 36 h, protože musí stéct do potoků a pak 1–2 dny téct po Labi a Vltavě. První nárůst vody model vidí v průtocích proti proudu (Beroun, Praha, Přelouč) 12–40 h předem. Vlastní předpověď deště by byla horší než dokonalá, takže by přinesla ještě méně. Srážky by pomohly na předpověď na 2–5 dní a na malých řekách v kraji.
- Soubory: `src/pokus_meteo.py`, `data/external/labe_meteo_o_den_driv.parquet`

## pá 22:32 · Ondra · dokonalá předpověď deště na 1–3 dny dopředu
- Otázka: když déšť předpovíme a dáme ho do modelu, pozná model nárůst hladiny dřív a přesněj? Pokus z pá 22:29 dával jen déšť běžícího dne, tady model zná celý déšť až na 3 dny dopředu.
- Data a rozdělení: denní srážky ČHMÚ z 25 stanic (`data/raw/chmu_meteo/`), průměr za každou větev (Vltava, horní Labe, Ohře). V čase t model zná skutečný úhrn běžícího srážkového dne (od 6:00 do 6:00 UTC) a součet se zítřkem a pozítřkem, 9 sloupců navíc. Je to horní mez, žádná skutečná předpověď počasí nebude lepší než skutečný déšť. Do modelu se nesmí. Jen validace.
- Model a nastavení: `ridge` beze změny, 98 + 9 vstupů.
- Kde a jak dlouho: MacBook M1, pár sekund.
- Výsledek na val (chyba na povodních, bez deště → s dokonale známým deštěm): Děčín +12 / +24 / +36 h 9,0 → 8,8, 15,5 → 14,5, 26,0 → 24,2 cm; Ústí 9,6 → 9,5, 15,7 → 14,7, 26,7 → 24,8 cm; průměr 17,1 → 16,1 cm. Varování nepřišlo dřív: předstih před 2. stupněm v Děčíně +36 h 25,8 → 22,8 h, před 3. stupněm stejný nebo o 0,5 h kratší. Chyba vrcholu se zhoršila (Děčín +36 h 10,2 → 14,1 cm). Nic nepropásl, žádný planý poplach.
- Závěr: ani dokonalá předpověď srážek na 3 dny dopředu chybu nezmenší o víc než 1,9 cm (7 % na 36 h) a varování neposune dřív. Skutečná předpověď deště se v množství i místě plete, takže by přinesla ještě méně. Domněnka, proč: první nárůst model vidí v průtocích proti proudu a stejný úhrn deště jednou skončí povodní a jindy se vsákne podle nasycení půdy, takže lineárnímu modelu déšť přidá spíš šum. Netestovali jsme hodinové srážky z radaru, ty mohou dopadnout jinak. Vlastní model předpovědi deště dělat nebudeme.
- Soubory: `src/pokus_dest_dopredu.py`

## pá 22:46 · Ondra · srážky na horizontech 12–72 h, naměřené i dokonale předpovězené
- Otázka: déšť známe dřív než průtok. Pomůže, když předpovídáme dál dopředu (48 a 72 h), a na kterých povodních?
- Data a rozdělení: denní srážky ČHMÚ, 25 stanic po větvích. Naměřené: srážky za den a 3 dny a index předchozích srážek API30, každá hodnota až od chvíle, kdy je známá (denní úhrn ráno po konci dne, 9 sloupců). Dokonalá předpověď: navíc skutečný déšť běžícího dne a dvou dalších (9 sloupců, horní mez, do modelu se nesmí). Společné rozdělení, jen validace.
- Model a nastavení: `ridge` beze změny, horizonty 12, 24, 36, 48, 72 h.
- Kde a jak dlouho: MacBook M1, asi minuta.
- Výsledek na val, Děčín (chyba na povodních, jako teď / bez srážek / naměřené / dokonalá předpověď): 36 h 65,6 / 26,0 / 26,2 / 24,0 cm; 48 h 86,1 / 40,3 / 40,5 / 36,8 cm; 72 h 123,2 / 78,0 / 76,9 / 69,1 cm. Ústí skoro stejně. Předstih varování se nezlepšil, na 72 h s dokonalou předpovědí se v Děčíně zkrátil (32,5 → 24,5 h).
- Po povodních, Děčín (bez srážek → dokonalá předpověď): dešťová povodeň 9/2010 36 h 31,6 → 24,4 cm (−23 %), 48 h 46,1 → 31,5 (−32 %), 72 h 79,7 → 48,0 (−40 %). Zimní a jarní povodně 4/2006, 3/2009 a 1/2011 se zlepšily nejvýš o 2–6 cm a některé zhoršily (3/2009 na 36 h 18,0 → 20,4 cm).
- Závěr: řetězec déšť → průtok → hladina funguje, ale jen pro povodně z deště a jen s předpovědí deště, ne s naměřenými denními srážkami. Ty známe až ráno po konci dne, a to už voda teče v řekách proti proudu, proto nepomáhají ani na 72 h. Hodinové srážky v reálném čase by mohly být o hodiny dřív, nezkoušeli jsme (archiv až od 2018). Povodně z tání sněhu déšť nevysvětlí, na ty by byla potřeba vodní hodnota sněhu a předpověď teploty. Ve validaci jsou tři povodně z tání a jedna dešťová, proto průměr vychází malý. Dešťová povodeň je jen jedna, číslo −40 % je tedy jeden případ. Skutečná předpověď deště se plete, takže reálný přínos bude menší. Finální model se nemění (test už proběhl), do prezentace jako „co dál“.
- Soubory: `src/pokus_dest_horizonty.py`, `src/pokus_dest_dopredu.py` (funkce `dest_dopredu`)

## pá 23:14 · Ondra · vodní hodnota sněhu, celoročně i zvláštní zimní model
- Otázka: pomůže, když model ví, kolik vody je ve sněhu a jestli taje? A pomůže aspoň v zimě, když je sníh jen sezónní?
- Data a rozdělení: denní archiv ČHMÚ, vodní hodnota sněhu (mm vody ve sněhu, měří se jednou týdně v pondělí, má ji všech 25 stanic). Bez sněhu 0, jinak platí poslední měření nejvýš 7 dní, bereme ji až den po změření. Průměr po větvích (Vltava, horní Labe, Ohře), k tomu úbytek za 7 dní (roztálo) a „tání“ = voda ve sněhu × průměrná teplota nad nulou. Na začátku povodně 2006 bylo v horním Labi 239 mm vody ve sněhu, 2009 147 mm, 2011 93 mm, 2010 nic. Společné rozdělení, jen validace.
- Model a nastavení: `ridge` beze změny. Zimní model = stejný model učený jen na listopadu až dubnu.
- Kde a jak dlouho: MacBook M1, asi minuta.
- Výsledek na val, celý rok (`prumer_povodne`): bez sněhu 17,1, s vodou ve sněhu 17,8, i s teplotou 17,8 cm. Nejvíc zhoršila jarní tání 2006 (Děčín +24 h 16,0 → 19,4 cm), 3/2009 a 1/2011 skoro beze změny.
- Výsledek jen na zimě (zimní povodně 2006, 2009, 2011, průměr přes 6 kombinací): celoroční model bez sněhu 15,6 cm, celoroční s „táním“ 16,1, zimní model bez sněhu 19,7, se sněhem 19,1, se sněhem a táním 18,9 (na 36 h o 1,8–2,3 cm lépe než zimní bez sněhu). Ve varování žádná chyba.
- Závěr: v samotném zimním modelu sníh trochu pomáhá, hlavně na 36 h. Zimní model je ale o 4 cm horší než celoroční, protože má jen polovinu dat a nevidí velké letní povodně (2013). Nejlepší zůstává celoroční model bez sněhu. Domněnka, proč sníh nepomáhá víc: zásoba sněhu říká, kolik vody může přijít během týdnů, ne za 36 h. Kdy roztaje, rozhoduje počasí, a roztátou vodu model vidí v průtocích proti proudu dřív, než doteče do Děčína.
- Soubory: `src/pokus_snih_voda.py`

## pá 23:14 · Ondra · horní mez pro hodinové srážky v reálném čase
- Otázka: denní srážky známe až ráno po konci dne. Pomohly by srážky, které známe hned, jak spadnou (hodinové z automatických stanic)?
- Data a rozdělení: hodinové srážky má ČHMÚ v archivu až od 2018, na trénink 2006–2018 nestačí. Místo nich horní mez: denní úhrn běžícího dne známý už od jeho začátku (`labe_meteo_o_den_driv.parquet`). Ten ví víc než hodinové srážky v reálném čase, protože zná i zbytek dne, takže hodinové srážky můžou pomoct nejvýš tolik. Jen validace.
- Model a nastavení: `ridge`, horizonty 12–72 h, `src/pokus_dest_horizonty.py` (varianta `hned`).
- Výsledek na val, Děčín (bez srážek → horní mez): 12 h 9,0 → 8,7, 24 h 15,5 → 14,6, 36 h 26,0 → 24,9, 48 h 40,3 → 39,4, 72 h 78,0 → 76,8 cm. Na dešťové povodni 9/2010 víc: 24 h 20,8 → 17,8, 36 h 31,6 → 26,6, 72 h 79,7 → 69,8 cm.
- Závěr: srážky v reálném čase by v průměru pomohly nejvýš o 1 cm, na dešťové povodni o 3–10 cm. Zkusit je pořádně nejde, archiv je krátký. Do prezentace jako „co dál“ spolu s předpovědí srážek.
- Soubory: `src/pokus_dest_horizonty.py`

## pá 23:27 · Ondra · vícenásobná validace, každá povodeň jednou vynechaná
- Otázka: vyhrává lineární regrese jen díky tomu, které čtyři povodně jsme dali do validace, nebo obecně? A jak moc se chyba liší mezi povodněmi?
- Data a rozdělení: 8 povodní nad 2. stupněm v Děčíně 2006–2020 (4/2006, 6/2006, 3/2009, 8/2010, 9/2010, 1/2011, 2/2013, 6/2013 se dvěma vrcholy jako jeden blok). Pro každou: validace = 16 dní před vrcholem až 5 po, trénink = zbytek 2006–2020 bez 20 dní kolem ní, stejná ochranná pásma jako v `evaluate.py`. Test 2021–2025 se nepoužil. Model se učí i na povodních, které přišly po vynechané, u fyzikálních vztahů v řece to nevadí.
- Vstupy: 98 společných sloupců, modely beze změny (`jako_ted`, `ridge`, `mlp`, `lgbm`, `fyzika`).
- Model a nastavení: 8 povodní × 2 cíle × 3 horizonty × 5 modelů = 240 tréninků, seed 42.
- Kde a jak dlouho: MacBook M1, asi 18 minut.
- Výsledek (chyba v okně kolem vrcholu, průměr 6 kombinací, pak přes povodně, ± směrodatná odchylka): lineární regrese 20,1 ± 7,7 cm, síť 21,0 ± 8,0, LightGBM 22,7 ± 8,6, fyzikální 26,7 ± 10,0, „jako teď“ 45,2 ± 13,9. Lineární regrese je o 56 % lepší než „jako teď“ (validace 61 %, test 55 %). Nejlepší byla na 4 povodních z 8, síť na 3, LightGBM na 1. Proti síti vyhrála 5 z 8, proti LightGBM 6 z 8. Nejlehčí povodeň 3/2009 (11,2 cm), nejtěžší 6/2013 (33,9 cm, vrchol 1 072 cm, když se vynechá, model nikdy tak vysokou vodu neviděl) a 8/2010 (28,6 cm, déšť blízko Děčína).
- Varování (součet přes 48 běhů): lineární regrese 1 propásnutí (Děčín +12 h, 8/2010) a 3 plané poplachy, síť 4 a 5, LightGBM 0 a 4, fyzikální 0 a 4, „jako teď“ 72 propásnutí. Skoro všechny plané poplachy jsou Ústí 6/2006, kdy voda vystoupala na 525 cm, 5 cm pod 2. stupeň.
- Závěr: pořadí z validace platí i přes 8 povodní, lineární regrese je nejlepší v průměru i v nejvíc párových srovnáních a má nejmíň chyb ve varování mezi učenými modely. Rozdíl proti síti (0,9 cm) je ale menší než rozdíly mezi povodněmi, takže jsou prakticky stejně dobré. Chyba záleží víc na povodni (11 až 34 cm) než na modelu. Graf `docs/grafy/krizova_validace.png`.
- Soubory: `src/krizova_validace.py`, `src/graf_krizova_validace.py`, `results/krizova_validace/2026-10-23_232649.csv`

## pá 23:44 · Ondra · polynomická regrese 2. stupně
- Otázka: nebyla by křivka (polynom) lepší než lineární regrese?
- Data a rozdělení: společné, validace.
- Vstupy: 98 společných sloupců (průtoky pod odmocninou) a navíc buď druhé mocniny všech 98 (`ridge_polynom`, 196 sloupců), nebo druhé mocniny a součiny 14 aktuálních hodnot z času t (`ridge_polynom_soucin`, 203 sloupců). Plný polynom 2. stupně by měl 4 949 sloupců, to by se na 2 velkých povodních v tréninku jen přeučilo.
- Model a nastavení: StandardScaler + Ridge(alpha=1), seed nehraje roli.
- Kde a jak dlouho: MacBook M1, pod sekundu na model.
- Výsledek na val (`prumer_povodne`): lineární regrese 17,1 cm, s druhými mocninami 22,8 cm, se součiny 19,9 cm. V klidu stejné (Děčín +24 h 7,5 / 7,8 / 7,7 cm), na povodních horší, hlavně na 36 h (Děčín 26,0 → 35,2 a 34,8 cm). Polynomy víc podhodnocují (bias na povodních Děčín +36 h −29 cm proti −11 u lineární) a chyba vrcholu je větší (Děčín +24 h 14,4 → 31,9 a 14,3 cm).
- Závěr: polynom nepomohl. Ohyb křivky se určí z běžné vody, které je 99 %, a při vysoké vodě, kde máme jen pár povodní, se ohne špatným směrem. Potřebný ohyb (měrná křivka) už má lineární regrese v odmocnině průtoků. Neuronová síť a LightGBM jsou taky nelineární a taky nevyhrály, takže víc ohybů tu nepomáhá.
- Soubory: `src/models/ridge_polynom.py`, `src/models/ridge_polynom_soucin.py`, `results/2026-10-23_234433_ridge_polynom.json`, `results/2026-10-23_234438_ridge_polynom_soucin.json`

## so 0:01 · Ondra · zpoždění na začátku prudkého vzestupu
- Otázka: proč všechny modely na začátku nejprudšího stoupání zaostávají, a dá se to spravit, třeba tak, že při rychlém vzestupu předpovíme ještě rychlejší?
- Data a rozdělení: společné, jen validace. „Náběh“ = hodiny, kdy hladina za h hodin stoupne aspoň o 50 cm (Děčín +24 h 598 hodin).
- Vstupy a modely: `ridge` (finální); `zrychleni` = ridge a k tomu kladný vzestup za 6 h u 14 aktuálních hodnot (hladiny, odmocniny průtoků) a jeho druhá mocnina, tedy ohyb „čím rychleji stoupá, tím víc přidej“; `horni_mez` = stejná předpověď jako ridge, ale varuje se podle horní meze intervalu nejistoty (95. percentil chyby z tréninku, `src/nejistota.py`).
- Kde a jak dlouho: MacBook M1, asi minuta.
- Výsledek na val (průměr 6 kombinací): při náběhu ridge podhodnocuje o 29 cm (chyba 35,2 cm, na 36 h až −42 cm). `zrychleni`: chyba na povodních 17,1 → 17,0, při náběhu 35,2 → 34,1 cm, podhodnocení −29 → −27 cm, předstih varování 17,4 → 18,0 h (2. stupeň) a 15,8 → 16,5 h (3. stupeň), žádný planý poplach. `horni_mez`: varování o 4,4 h dřív před 2. stupněm (21,8 h) a o 3 h dřív před 3. stupněm (18,8 h), ale 4 plané poplachy místo 0. Jako číslo je horní mez špatná předpověď (33,7 cm), hodí se jen jako spouštěč varování.
- Proč modely zaostávají: v tréninku po vzestupu Děčína aspoň o 30 cm za 6 h stoupla voda za dalších 24 h o víc než 50 cm jen ve 22 % případů a v 51 % začala klesat. Model se učí průměr, takže na začátku vzestupu sází na mírné pokračování. Na začátku povodně navíc část vody ještě neteče žádnou naší stanicí (déšť, malé přítoky). Všechny čtyři typy modelů zaostávají na stejných místech, takže chybí informace ve vstupech, ne tvar modelu.
- Závěr: „ještě prudší“ pomáhá jen málo (1 cm při náběhu, pod hranicí 1 cm na hlavní metrice) a model neměníme. Dřívější varování jde koupit planými poplachy: dvoustupňové varování, předběžná výstraha podle horní meze a varování podle předpovědi. Aplikace interval už ukazuje. Víc by pomohla jen informace o vodě, která v řekách ještě není (srážky).
- Soubory: `src/pokus_nabeh.py`

## so 00:45 · Honza · konvoluční síť po čase (TCN) na surových hodinových řadách
- Otázka: pomůže síť, která si sama hledá, které hodiny z minulosti jsou důležité (konvoluční síť po čase, TCN), místo ručně vybraných zpoždění 0–36 h? Ověřovací pokus jen na validaci. Finální model se nemění, test se nepouštěl.
- Data a rozdělení: společné rozdělení z `src/evaluate.py`, stejné řádky train a val jako u ostatních, všech 6 kombinací. Na zastavení tréninku se oddělí posledních 10 % trénovacích řádků v čase (8. 10. 2017 – 30. 12. 2018), validace ne. V téhle části není ani hodina nad 1. stupněm (Děčín nejvýš 362 cm), takže zastavení se řídí jen klidnou vodou.
- Vstupy: **jiné než společné vstupy.** Síť nebere 98 sloupců z `features.tabulka`, ale pro každý čas vydání t celé surové hodinové řady za posledních 48 h (t − 47 … t) všech 14 řad z `nacti()`: hladina Děčín a Ústí a odmocnina průtoku 12 stanic, škálované průměrem a směrodatnou odchylkou z trénovací části uvnitř `fit`. Z X bere jen čas vydání a hladinu teď. Díra v Děčíně 2/2006 je doplněná poslední známou hodnotou, tedy jen z minulosti. Kontrola úniku na třech řádcích (20. 3. 2006 10:00, 14. 1. 2011 12:00, 16. 5. 2019 16:00): okno končí přesně v čase vydání a hodnoty v něm se shodují se sloupci X (Praha 0 a 36 h, Louny 12 h, hladina Děčín 0 h, Ústí 24 h).
- Model a nastavení: `src/models/tcn.py`, PyTorch na procesoru. Kauzální dilatované konvoluce (každá hodina vidí jen sebe a starší hodiny): vstup na 16 kanálů, 5 reziduálních bloků s jádrem 3 a dilatacemi 1, 2, 4, 8, 16 (dosah 63 h, celé okno), ReLU, dropout 0,1, z poslední hodiny lineární výstup. Cíl je změna hladiny y − hladina teď, škálovaná jako u `mlp`. Adam (lr 0,001, weight decay 1e-4), batch 512, nejvýš 30 epoch, konec po 5 epochách bez zlepšení na zastavovací části a vrátí se nejlepší epocha. Seed 42, Děčín +24 h i 43 a 44 (`tcn_s43.py`, `tcn_s44.py`). Nejdřív jsem pustil 32 kanálů podle zadání: Děčín +24 h 15,7 cm, ale trénink trval 6 min a limit byl 5 min na kombinaci, proto 16 kanálů.
- Kde a jak dlouho: Honzův notebook (Ryzen 5 3600X, 6 jader). Jedna kombinace 78–264 s, nejlepší epocha 3–21, všech 6 kombinací 16 min (lineární regrese 1 s, síť MLP 99 s). Seedy 43 a 44 trvaly 292 a 227 s.
- Výsledek na val (chyba na povodních v cm, Děčín +12 / +24 / +36 h, Ústí +12 / +24 / +36 h; `prumer_povodne`; propásnuté nástupy a plané poplachy u 2. stupně z 24; předstih 2. stupně):
  - TCN: 10,5 / 18,2 / 34,3, Ústí 12,1 / 14,8 / 32,1; **20,3 cm**; propásnuto 3 (Ústí +24 h jednou, +36 h dvakrát), 0 planých; 13,5 h. Bias na povodních −26,0 až +3,4 cm, chyba celkem 8,5 cm.
  - lineární regrese (`ridge`, finální): 9,0 / 15,5 / 26,0, Ústí 9,6 / 15,7 / 26,7; 17,1 cm; 0 a 0; 17,4 h. Bias −11,6 až −0,3 cm, chyba celkem 8,2 cm.
  - síť MLP (`mlp`): 9,3 / 18,4 / 25,7, Ústí 9,0 / 16,5 / 28,1; 17,8 cm; 0 a 1; 19,5 h.
  - „jako teď“: 44,3 cm, propásne 24 z 24.
  - Seedy, Děčín +24 h: 18,2 / 17,2 / 15,2 cm (42 / 43 / 44), průměr 16,9, rozpětí 3,0 cm, všechny bez propásnutí a planého poplachu. Lineární regrese 15,5 cm.
- Kde prohrává: hlavně povodeň 4/2006 (875 cm, výš než všechno v tréninku kromě 2013). Na 36 h Děčín 47,1 cm proti 26,8 u lineární regrese, Ústí 50,3 proti 28,8 (podhodnocuje o 48 cm), na 12 h naopak přestřelí (Děčín o +11 cm, Ústí o +17 cm). Na povodni 1/2011 je stejná nebo lepší (Ústí +36 h 20,9 proti 27,0 cm). Přeučení: Děčín +24 h při hladině nad 1. stupněm chyba na tréninku 11,1 cm, na validaci 19,4 cm.
- Vysvětlení, naučené odezvy (`docs/grafy/tcn_odezvy.png`, `python src/tcn_odezvy.py`): pro model Děčín +24 h (seed 42, kontrola: stejných 18,2 cm) jsem na validaci přidal jedné stanici průtok o 1 směrodatnou odchylku vyšší jen v jedné hodině t − k a měřil změnu předpovědi, průměr přes každou 3. validační hodinu (6 422 řádků) a zvlášť přes hodiny nad 1. stupněm (820). Čtverce v grafu jsou váhy lineární regrese ve stejných jednotkách.
  - U 10 z 12 stanic je vrchol odezvy v nejnovější hodině (k = 0) a síť tam našla skoro stejné číslo jako lineární regrese: Praha +50,0 cm (regrese +49,3), Beroun +17,0 (+14,1), Louny +14,2 (+18,3), Jizera +12,9 (+11,6), Sázava +11,5 (+10,1), Přelouč +10,9 (+11,6), Mělník +8,1 (+15,5), průtok v Děčíně −24,6 (−11,0). Vraňany a Kostelec mají v síti nejvýš 2 cm, regrese dává Kostelci +9,6. Ústí má −5,5 cm v hodině 4.
  - Starší hodiny mají odezvu do ±6 cm a malé zuby v hodinách 4, 8, 16 a 32. To jsou dilatace sítě, ne fyzika.
  - Doby putování (Praha asi 20 h, Mělník 12 h, Ústí 4 h) se jako posunutý vrchol neukážou a pro +24 h by ani neměly: všechny jsou kratší než horizont, voda, která bude v Děčíně za 24 h, ještě žádnou z těch stanic neprotekla, takže nejvíc řekne nejnovější hodina (čekaný vrchol max(0, doba − 24) = 0 h). Stejně to vypadá u regrese. Doplňkově jsem změřil i Děčín +12 h, kde by vrchol Prahy měl být kolem 8 h: síť má i tam vrchol v hodině 0 (+5,9 cm) a v hodině 8 jen +0,4 cm. Domněnka: průtok se mění pomalu, sousední hodiny nesou skoro stejnou informaci a skok v jediné hodině síť při tréninku nikdy neviděla, takže tenhle test doby putování spolehlivě neukáže. Doby doběhu vidíme spíš v tom, které stanice pro který horizont dostanou váhu.
- Závěr: neprošlo. TCN je proti lineární regresi o 3,2 cm horší, proti MLP o 2,5 cm, propásla 3 varování a trénuje 16 min místo 1 s. Rozdíl mezi seedy (3 cm na jedné kombinaci) je stejně velký jako rozdíl proti regresi, takže ani nejlepší seed není jasné zlepšení. Slabiny pokusu: jen 16 kanálů kvůli času, zastavení tréninku na klidných letech 2017–2018 a jedna sada nastavení bez ladění. Pro porotu: síť, která si z 48 hodin surových dat sama vybírá důležité hodiny, nebyla lepší než lineární regrese s ručně vybranými zpožděními a naučila se skoro stejné váhy (hlavně „průtok v Praze teď“), takže jednoduchý model žádnou důležitou informaci nezahazuje.
- Soubory: `src/models/tcn.py`, `src/models/tcn_s43.py`, `src/models/tcn_s44.py`, `src/tcn_odezvy.py`, `docs/grafy/tcn_odezvy.png`, `results/2026-10-24_000506_tcn.json` (32 kanálů, jen Děčín +24 h), `results/2026-10-24_002127_tcn.json`, `results/2026-10-24_002623_tcn_s43.json`, `results/2026-10-24_003011_tcn_s44.json`, `results/predpovedi/tcn.parquet`. PyTorch (verze pro procesor) je jen v místním `.venv`, ostatní modely ho nepotřebují.
