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

Následující pokusy jsou doplněné zpětně (pá 19:35). Všechny byly před společným rozdělením, čísla proto nejdou přímo srovnat s výsledky v `results/`. Podrobnosti v `docs/NAPAD_LABE.md`.
## pá 19:35 · Dan · základy pro LightGBM: lineární trend a Ridge na změnu stavu
- Otázka: jak dopadnou jednoduché základy, se kterými budu LightGBM srovnávat, a funguje u mě řetězec stejně jako u Ondry?
- Data a rozdělení: společná tabulka a rozdělení z `src/evaluate.py`, všech 6 kombinací (Děčín a Ústí, +12 / +24 / +36 h).
- Vstupy: trend jen stav v cíli teď a před 6 h. Ridge všech 98 sloupců, průtoky pod odmocninou.
- Model a nastavení: `zaklad_trend` (stav se dál mění stejně rychle jako za posledních 6 h). `zaklad_ridge` (StandardScaler + Ridge alpha 1, cíl je změna stavu proti teď).
- Kde a jak dlouho: Dan, Yoga 7i, do 2 s.
- Výsledek na val (chyba na povodních, Děčín +12 / +24 / +36 h): „jako teď“ 23,0 / 44,4 / 65,6 cm, trend 18,0 / 36,1 / 60,0 cm, Ridge 9,0 / 15,5 / 26,0 cm. `prumer_povodne`: „jako teď“ 44,3, trend 39,4, Ridge 17,1. Trend nic nepropásl, ale má plané poplachy před 2. stupněm (Děčín 2 / 5 / 16), Ridge žádné.
- Závěr: Ridge na změnu stavu dává na cm stejná čísla jako Ondrův Ridge na stav, řetězec u mě běží stejně. Trend je lepší než „jako teď“ jen díky tomu, že zachytí začínající stoupání, ale přestřeluje a dělá plané poplachy. Laťka pro LightGBM je Ridge se 17,1 cm.
- Soubory: `src/models/zaklad_trend.py`, `src/models/zaklad_ridge.py`, `results/2026-10-23_1933_zaklad_trend.json`, `results/2026-10-23_1933_zaklad_ridge.json`, `results/predpovedi/zaklad_*.parquet`
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

## pá 19:40 · Ondra · přítoky v kraji (Bílina, Ploučnice)
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
## pá 19:56 · Dan · LightGBM c: zbytek po Ridge, přímky v listech, regularizace, zastavení tréninku
- Otázka: dá se přeučení a neschopnost stromů jít nad to, co viděly, obejít jinak než zjednodušením stromů?
- Data a rozdělení: společné rozdělení, všech 6 kombinací. Zastavení tréninku jen na letech 2017–2018 z trénovací části, validace se na něj nepoužije.
- Vstupy: jako c.
- Model a nastavení: (1) stromy se učí jen opravu Ridge, cíl = skutečnost − předpověď `zaklad_ridge`; (2) `linear_tree=True`, v listu přímka místo čísla; (3) 15 listů, `reg_lambda` 10, `colsample_bytree` 0,7; (4) zastavení, když se MAE na 2017–2018 nezlepší 50 stromů. Seed 42.
- Kde a jak dlouho: Dan, Yoga 7i, 2–8 s na model.
- Výsledek na val (`prumer_povodne`, c 22,8, Ridge 17,1): zbytek po Ridge 18,9, přímky v listech 111,8, regularizace 22,2, zastavení 22,4 (zastaveno po 63–212 stromech). Zbytek po Ridge má proti c navíc 2 plané poplachy před 2. stupněm (Děčín 24 a 36 h) a 1 propásnutou povodeň (Ústí 36 h).
- Závěr: neprošlo nic. Nejzajímavější je zbytek po Ridge: proti c pomohl o 3,9 cm, ale samotný Ridge zhoršil o 1,8 cm a přidal plané poplachy. Opravy, které se stromy naučí na povodních z tréninku, na jiné povodně nesedí. Přímky v listech při velké vodě ujely až o 3 m, protože přímka naučená na úzkém kousku dat se za jeho hranou nekontrolovaně prodlouží. Regularizace a zastavení pomohly jen o 0,4–0,6 cm, pod hranicí 1 cm. Zastavení se navíc řídí suchými roky 2017–2018 bez povodně, takže o povodních nic neví. Podle pravidel tady ladění končí, nejlepší LightGBM zůstává c.
- Soubory: `src/models/lgbm_c_ridge.py`, `src/models/lgbm_c_linear.py`, `src/models/lgbm_c_regularizace.py`, `src/models/lgbm_c_stop.py`, `results/2026-10-23_1953_lgbm_c_ridge.json`, `results/2026-10-23_1954_lgbm_c_linear.json`, `results/2026-10-23_1954_lgbm_c_regularizace.json`, `results/2026-10-23_1955_lgbm_c_stop.json`
## pá 19:48 · Tobias · fyzikální model, finální varianta a grafy
- Nejlepší varianta (3 vrstvy stanic) je teď `src/models/fyzika.py`, první verze se dvěma vrstvami zůstává pro srovnání jako `src/models/fyzika_dve_vrstvy.py`. Po přejmenování znovu spuštěno: `prumer_povodne` 24,8 a 26,6 cm, stejně jako předtím.
- `docs/grafy/fyzika_merna_krivka.png`: měrná křivka Děčína se stupni povodňové aktivity. Body z povodní leží přesně na křivce, nad 3 710 m³/s (nejvyšší průtok v tréninku) je křivka prodloužená přímkou.
- `docs/grafy/fyzika_vetve.png`: tři větve (Vltava, Labe, Ohře) s dobami putování mezi stanicemi a do Děčína. Nejdál dopředu vidí Beroun a Přelouč, 24 h.
- `docs/grafy/fyzika_povoden_2006.png`: validační povodeň 2006, Děčín +24 h. Při stoupání model sleduje skutečnost, „jako teď“ se opožďuje o celý den. Těsně před vrcholem model krátce přestřelí asi o 50 cm, při opadání se opožďuje.

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

## pá 21:15 · Ondra · srážky, sníh a teplota z 25 stanic v povodí
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

## pá 20:55 · Honza · kolik let dat model potřebuje (učicí křivka)
- Otázka: proč nestačil balíček pořadatelů (2 roky, jen kraj)? Jak se chyba mění s délkou historie a sadou stanic?
- Data a rozdělení: společné; trénink omezený na posledních N let před validací (2019 − N až 2018), N = 1, 2, 3, 5, 8, 13; validace stejná. Dvě sady vstupů: jen kraj (Děčín, Ústí, Louny, 35 sloupců) a všechny stanice (98 sloupců).
- Model a nastavení: `ridge.fit` beze změn (odmocnina průtoků, StandardScaler, Ridge alpha 1).
- Kde a jak dlouho: notebook, 72 tréninků za minutu.
- Výsledek na val (`prumer_povodne` v cm, v závorce propásnuté nástupy povodní u 2. stupně z 24): jen kraj: 1 rok 39,2 (9), 2 roky 45,1 (12), 3 roky 35,6 (9), 5 let 34,2 (10), 8 let 27,2 (0), 13 let 27,8 (0). Všechny stanice: 1 rok 28,3 (2), 2 roky 26,9 (4), 3 roky 24,8 (3), 5 let 21,0 (3), 8 let 16,6 (0), 13 let 17,1 (0). „Jako teď“ 44,3.
- Závěr: 1) Stanice proti proudu pomohly víc než roky: 2 roky se všemi stanicemi (26,9) jsou lepší než 13 let jen s krajem (27,8). 2) Rozhoduje, jestli je v tréninku velká povodeň: v letech 2014–2018 žádná nad 2. stupněm nebyla, modely z 1–5 let proto propásnou 2–12 nástupů z 24; jakmile je v tréninku povodeň 2013 (8 let, 409 hodin nad 2. stupněm v Děčíně), propásnuté klesnou na 0. 3) Balíček (2 roky, jen kraj) by dal 45 cm, tedy nic lepšího než „jako teď“, a propásl polovinu povodní. 4) 8 let (16,6) a 13 let (17,1) je totéž v rámci náhody. Potvrzuje zjištění z NAPAD_LABE na společném rozdělení.
- Soubory: `src/kolik_dat.py`, `docs/grafy/kolik_dat.png`.
