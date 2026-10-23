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

## pá 19:35 · Tobias · doby putování vody pro fyzikální model
- Otázka: za kolik hodin se změna průtoku na stanici proti proudu projeví v Ústí a v Děčíně?
- Data a rozdělení: `labe_hodinove.parquet`, jen train z `src/evaluate.py` (2006–2018 bez validačních povodní).
- Vstupy: průtoky vyhlazené klouzavým průměrem 12 h, z nich změna za 6 h. Pro každou dvojici stanic posun 0–48 h s největší korelací změn. Zvlášť pro celý train a pro vysokou vodu (průtok v Ústí nad 75. percentilem).
- Model a nastavení: žádný model, jen korelace.
- Kde a jak dlouho: MacBook M4, pár sekund.
- Výsledek (vysoká voda): Kostelec → Ústí 5 h (r 0,58), Vraňany → Ústí 10 h (0,59), Louny → Ústí 12 h (0,43), Mělník → Ústí 8 h (0,83), Ústí → Děčín 4 h (0,98). Dál proti proudu: Praha → Vraňany 5 h (0,95), Beroun → Vraňany 12 h, Sázava → Vraňany 8 h, Nymburk → Kostelec 6 h (0,90), Jizera → Kostelec 6 h, Přelouč → Kostelec 16 h (0,80).
- Závěr: bez vyhlazení vycházely korelace jen 0,2–0,46 a Nymburk dokonce rychlejší než Kostelec pod ním, to ruší hodinové kolísání (nejspíš elektrárny na Vltavě). Po vyhlazení časy dávají smysl a sedí na dolní hranu odhadů ze zadání. Ohře má nejslabší vztah, je nejdál a mezi Louny a Ústím ještě něco přitéká. Tyhle časy použije `src/models/fyzika.py`.
- Soubory: zatím jen tenhle zápis, výpočet bude v `src/models/fyzika.py`.

## pá 19:50 · Tobias · fyzikální model, první běh a měrná křivka
- Otázka: kolik umí samotná fyzika bez učení, jen doby putování a měrná křivka?
- Data a rozdělení: společné z `src/evaluate.py`, Děčín +24 h (`--rychle`).
- Vstupy: průtok v cíli teď, průtoky bran Vraňany, Kostelec, Louny a nad nimi Praha, Nymburk, Jizera v zpožděních z `features.py`, hladina v cíli teď.
- Model a nastavení: průtok v cíli za h = průtok teď + přírůstky z bran posunuté o dobu putování (když voda nedotekla ani k bráně, vezme se stanice nad ní). Na hladinu přes měrnou křivku: medián hladiny v 80 pásmech podle logaritmu průtoku, jen rostoucí, nad maximem přímka. Předpověď = hladina teď + rozdíl křivky, takže se zachová, co je na stanici právě jinak. Doby putování si model spočítá z trénovacích dat (do Děčína Vraňany 13 h, Kostelec 8 h, Louny 16 h, Praha 17 h, Nymburk a Jizera 14 h).
- Měrná křivka a odlehlé hodnoty: první pokus s pásmy podle počtu bodů měl na vysoké vodě jedno pásmo 800–3700 m³/s, křivka byla plochá a vrchol 2013 ujel o 6 m. Vypadalo to jako odlehlé body, ale byla to chyba křivky. Opravdu odlehlých hodnot skoro není, typická odchylka od křivky je 1,4 cm (ČHMÚ počítá průtok z hladiny). Minimum hodin v pásmu na val při průtoku nad 1000 m³/s: 6 h dává chybu 2,7 cm, 24 h 6,7 cm, 72 h 23,6 cm (křivka končí na 1080 m³/s). K přeučení nedochází, beru 6. Koryto se za 2006–2018 posunulo jen o ±2 cm.
- Kde a jak dlouho: MacBook M4, trénink 0,1 s.
- Výsledek na val: na povodních 24,1 cm proti 44,4 cm u „jako teď“, celková MAE 11,4 proti 12,7 cm. Před 2. stupněm varoval 26 h předem, 0 propásnutých, 1 planý poplach. Před 3. stupněm 17 h předem, 0 propásnutých.
- Závěr: samotná fyzika chybu na povodních skoro půlí. Proti rychlému lineárnímu modelu (15,5 cm) je horší, nejspíš proto, že neví o přítocích mezi branami a Ústím a doby putování se mezi povodněmi mění. Dál: všech 6 kombinací a varianta bez stanic proti proudu.
- Soubory: `src/models/fyzika.py`, `results/2026-10-23_1931_fyzika.json`.
