# Deník týmu

Rozhodnutí, změny postupu a problémy, chronologicky. Nový záznam na konec, nic nepřepisovat. Git záznamy z různých větví spojí sám.

```
## pá 18:40 · Ondra
- Co: co se rozhodlo nebo změnilo
- Proč: důvod jednou dvěma větami
- Problém: co nefunguje nebo je špatně a jak to řešíme (jen když je)
- Otázka pro mentory: (jen když je)
```

Po každém dokončeném kusu práce rozbor, aby ho pochopil i ten, kdo u toho nebyl:

```
## pá 19:20 · Dan · Rozbor: první model
- Co jsme udělali:
- Jak to funguje, jednoduše:
- Proč tak a ne jinak:
- Výsledek a co znamená:
- Slabiny a co může být špatně:
- Otázka poroty a odpověď:
```

## pá 19:20 · Ondra
- Co: jdeme rovnou na Labe, ne na malé řeky. Každý zkusí jiný model na stejném úkolu: Tobias fyzikální model, Honza lineární regresi, Dan LightGBM, Ondra neuronovou síť. Zadání pro všechny je v `docs/UKOL_MODELY.md`, srovnání ve 21:00.
- Proč: výsledek, který ukážeme, je na Labi, a model vybraný na malé řece by se pro Labe musel vybírat znovu. Srovnání čtyř přístupů je samo o sobě obsah prezentace.
- Společný základ je hotový: tabulka 2006–2025 (`data/external/labe_hodinove.parquet`), vstupy (`src/features.py`), rozdělení a vyhodnocení (`src/evaluate.py`), spouštění (`src/porovnej.py`), základ „bude jako teď“.
- Problém: mezi 2016 a 2020 nebyla povodeň, takže validace nemůže být jen poslední roky před testem. Validujeme na čtyřech vynechaných povodních a klidných letech 2019–2020.

## pá 19:20 · Ondra · Rozbor: společný základ a první srovnání
- Co jsme udělali: jedna tabulka pro všechny, stejné rozdělení a vyhodnocení, základ „bude jako teď“ a rychlá kontrola celého řetězce lineárním modelem.
- Jak to funguje, jednoduše: v každé hodině vezmeme hladiny v Děčíně a Ústí a průtoky na 12 stanicích teď a před pár hodinami a model z nich odhadne hladinu za 12, 24 a 36 h.
- Proč tak a ne jinak: hodnotíme hlavně chybu během povodní a varování před 2. a 3. stupněm, protože na klidné řece je skoro dokonalá i předpověď „bude jako teď“.
- Výsledek a co znamená: Děčín za 24 h, chyba na povodních: „jako teď“ 44,4 cm, lineární model 15,5 cm. Lineární model varoval před 2. stupněm v průměru 15,5 h předem, nic nepropásl a neměl planý poplach. „Jako teď“ propásl všechny.
- Slabiny a co může být špatně: ve validaci jsou jen 4 povodně, čísla berte jako směr. Odmocnina na hladinu (místo jen na průtok) zkazila vrchol 2006 o metr, pozor na to v každém modelu.
- Otázka poroty a odpověď: „Proč netestujete na náhodně vybraných hodinách?“ Sousední hodiny jsou skoro stejné, model by je znal z tréninku a výsledek by byl falešně dobrý. Proto dělíme v čase a kolem validačních povodní vynecháváme 20 dní.

## pá 19:45 · Ondra
- Co: zkontroloval jsem správnost dat (shoda s balíčkem pořadatelů, bilance vody mezi stanicemi, měrné křivky, časy, odlehlé hodnoty). Data jsou v pořádku, nic se neměnilo. Podrobnosti v `docs/DATA.md`, sekce Labe.
- Co: do zadání modelů přibyla pravidla, jak dlouho iterovat (jedna změna s důvodem, zlepšení aspoň o 1 cm v `prumer_povodne`, konec po 3 neúspěšných variantách, 10 variantách nebo ve 20:50).
- Proč: validace má jen 4 povodně, nekonečné ladění by našlo variantu, která na nich vyjde náhodou dobře.
