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

## pá 19:35 · Ondra · jak dlouho trvá trénink
- Otázka: stačí počítače, nebo je potřeba Kaggle?
- Výsledek (MacBook M1, Děčín +24 h, 108 tisíc řádků): lineární regrese 0,2 s, LightGBM asi 7 s, MLP (64, 32) 17 s (82 epoch).
- Závěr: všechno lokálně, Kaggle by jen zdržel nahráváním a frontou.

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
## pá 20:05 · Ondra · přítoky v kraji (Bílina, Ploučnice)
- Otázka: pomůže modelu průtok přítoků, které do Labe ústí mezi Ústím a Děčínem?
- Data a rozdělení: společné rozdělení (`src/evaluate.py`), navíc průtok Bílina-Trmice a Ploučnice-Benešov z ČHMÚ, zpoždění 0, 3, 6 a 12 h.
- Model a nastavení: Ridge(alpha=1), odmocnina průtoků, StandardScaler, seed 42 (stejný jako kontrola řetězce).
- Výsledek na val (chyba na povodních bez / s přítoky): Děčín +6 h 4,6 / 4,8 cm, +12 h 9,0 / 9,5, +24 h 15,5 / 16,0; Ústí +6 h 7,3 / 7,5, +12 h 9,6 / 10,1, +24 h 15,7 / 16,2. Při vrcholech povodní přidaly přítoky 2–13 % vody, nejvíc v 8/2010.
- Závěr: nepomohly, do společných vstupů je nepřidáváme. Jejich voda doteče za pár hodin a na delší horizont rozhoduje déšť. Limit: povodeň z lokálních dešťů v kraji (jako 8/2010) model bez srážek dopředu nevidí.
- Soubory: jen kontrola, model není uložený.

## pá 19:48 · Tobias · fyzikální model, finální varianta a grafy
- Nejlepší varianta (3 vrstvy stanic) je teď `src/models/fyzika.py`, první verze se dvěma vrstvami zůstává pro srovnání jako `src/models/fyzika_dve_vrstvy.py`. Po přejmenování znovu spuštěno: `prumer_povodne` 24,8 a 26,6 cm, stejně jako předtím.
- `docs/grafy/fyzika_merna_krivka.png`: měrná křivka Děčína se stupni povodňové aktivity. Body z povodní leží přesně na křivce, nad 3 710 m³/s (nejvyšší průtok v tréninku) je křivka prodloužená přímkou.
- `docs/grafy/fyzika_vetve.png`: tři větve (Vltava, Labe, Ohře) s dobami putování mezi stanicemi a do Děčína. Nejdál dopředu vidí Beroun a Přelouč, 24 h.
- `docs/grafy/fyzika_povoden_2006.png`: validační povodeň 2006, Děčín +24 h. Při stoupání model sleduje skutečnost, „jako teď“ se opožďuje o celý den. Těsně před vrcholem model krátce přestřelí asi o 50 cm, při opadání se opožďuje.
