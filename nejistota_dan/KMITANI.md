# Kmitání předpovědi při nízké vodě

Dan, so 24. 10. 2026 05:22–06:30, větev `dan-nejistota`. Varianty zapsané předem v `PRUBEH.md` (05:22), kód
`kmitani.py` a `src/models/ridge_kmit_*.py`, výsledky `kmitani/*.csv` a `results/krizova_validace/2026-10-24_055024.csv`.
Test 2021–2025 se nespouštěl.

## Shrnutí a doporučení

- Provozní test Ridge session (`origin/dan-ridge`, `ridge_dan/PROVOZ.md`): týmový Ridge při nízké vodě kmitá, protože
  přenáší výkyvy průtoků z vodních děl. Na provozních datech 25. 9.–23. 10. 2026 (Děčín +24 h) má hodinová změna
  předpovědi směrodatnou odchylku **6,2 cm, realita 2,2 cm**.
- **Model neměnit.** Žádná ze tří předem daných variant neprojde kritériem „povodně nejvýš o 0,5 cm horší a varování
  ne později“:
  - (a) vyhlazení výstupu kmitání půlí, ale povodně jsou horší o 0,4–1,0 cm (Ondrova validace +0,7) a začátek vzestupu
    o 3–6 cm; předstih 2. stupně klesne o 0,1–1 h a v Ondrově validaci propásne jednu povodeň víc;
  - (b) vyhlazení průtoků pod vodními díly povodně skoro nezmění (+0,04 až +0,24 cm), ale kmitání taky ne (6,2 → 6,1);
  - (c) obojí je horší než (a).
- **Jen pro zobrazení v Dnešku: vyhladit.** Pravidlo (d), přidané až po výsledcích (a)–(c): průměr předpovědí za
  poslední 3 h jen když je hladina teď i předpověď pod 1. stupněm, jinak surová předpověď. Varování od 2. stupně se tím
  z konstrukce nemění. V provozu kmitání klesne na polovinu (6,2 → 3,1 cm) a chyba se zlepší (7,6 → 6,9 cm). Na
  povodních by zobrazená hodnota při začátku vzestupu pod 1. stupněm byla o 0,3–0,7 cm horší (tři ze šesti kombinací
  těsně přes 0,5 cm), proto **jen v Dnešku** (teď nízká voda), ne při přehrávání povodní. Návrh: `patche/11.patch`.

## Varianty (předem, bez ladění)

- **(a) výstup** `src/models/ridge_kmit_vystup.py`: průměr předpovědí vydaných v t, t − 1 h a t − 2 h.
- **(b) vstupy** `src/models/ridge_kmit_vstup.py`: průtoky Praha-Chuchle, Vraňany (pod Vltavskou kaskádou), Mělník
  (pod soutokem s Vltavou) a Louny (pod Nechranicemi) nahrazené průměrem za t − 5 … t, model znovu naučený.
  Zbraslav v týmovém modelu není.
- **(c)** obojí. **(d)** jen zobrazení, po výsledcích: (a), když je hladina teď i surová předpověď pod 1. stupněm.

Vše jen z minulých hodnot (zkontroloval Codex, `codex/kontrola_e_kmitani.md`).

## Výsledky

LOFO 22 povodní 2006–2020 (chyba na povodních v cm, začátek vzestupu v cm, medián zpoždění vrcholu předpovědi za
skutečností v h, předstih varování 2. stupně v h; rozdíl proti týmovému Ridge v závorce):

| cíl, h | týmový Ridge | (a) výstup | (b) vstupy | (c) obojí | (d) zobrazení |
|---|---|---|---|---|---|
| Děčín 12 h | 8,54 / 22,4 / −2,5 / 9,8 | 9,00 (+0,46) / 28,6 / −2,0 / 9,7 | 8,45 (−0,09) / 22,1 / −2,5 / 9,8 | 8,91 (+0,37) / 28,3 / 0,0 / 9,7 | 8,88 (+0,34) / 27,5 / −2,5 / 9,8 |
| Děčín 24 h | 15,28 / 41,9 / 1,0 / 18,2 | 16,09 (+0,81) / 45,2 / 3,0 / 17,3 | 15,43 (+0,15) / 42,6 / 1,5 / 18,2 | 16,23 (+0,95) / 45,9 / 3,0 / 17,3 | 15,76 (+0,48) / 44,9 / 1,0 / 18,2 |
| Děčín 36 h | 26,39 / 66,5 / 4,0 / 22,5 | 27,38 (+0,99) / 69,6 / 5,0 / 21,7 | 26,56 (+0,17) / 67,2 / 11,0 / 22,5 | 27,54 (+1,15) / 70,4 / 12,0 / 21,7 | 26,92 (+0,53) / 68,8 / 4,0 / 22,5 |
| Ústí 12 h | 9,94 / 27,1 / −3,0 / 11,4 | 10,34 (+0,40) / 31,5 / −1,5 / 11,2 | 9,86 (−0,08) / 27,3 / −3,0 / 11,2 | 10,28 (+0,34) / 31,6 / −1,0 / 11,0 | 10,38 (+0,44) / 31,4 / −2,5 / 11,4 |
| Ústí 24 h | 17,30 / 45,5 / −1,5 / 21,6 | 18,16 (+0,86) / 48,6 / 0,0 / 20,6 | 17,51 (+0,21) / 46,2 / 0,0 / 21,6 | 18,38 (+1,08) / 49,4 / 2,5 / 21,2 | 17,96 (+0,66) / 48,1 / −1,5 / 21,6 |
| Ústí 36 h | 28,94 / 71,8 / 5,5 / 24,2 | 29,89 (+0,95) / 74,4 / 7,0 / 23,2 | 29,17 (+0,23) / 72,6 / 8,0 / 24,0 | 30,12 (+1,18) / 75,1 / 13,0 / 23,2 | 29,58 (+0,64) / 73,9 / 5,5 / 24,2 |

Ondrova vícenásobná validace (`src/krizova_validace.py` beze změny, 8 povodní × 6 kombinací, varianty jako moduly;
průměrná chyba, propásnuté + plané poplachy): týmový Ridge **20,12 cm**, 1 / 3; (a) 20,80 (+0,69, horší ve 40 ze 48),
**2** / 3; (b) 20,16 (+0,04, horší ve 29 ze 48), 1 / 3; (c) 20,84 (+0,72), 2 / 3. Pravidlo (d) varování nemění.

Klid 2019–2020 (model z trénovací části, validace týmového splitu; chyba / směrodatná odchylka hodinové změny
předpovědi v cm, realita 1,8 v Děčíně a 2,9 v Ústí):

| cíl, h | týmový Ridge | (a) | (b) | (c) | (d) |
|---|---|---|---|---|---|
| Děčín 24 h | 6,87 / 3,83 | 6,78 / 1,94 | 6,93 / 3,60 | 6,86 / 1,90 | 6,78 / 1,94 |
| Děčín 36 h | 9,65 / 4,81 | 9,51 / 2,46 | 9,68 / 4,65 | 9,57 / 2,42 | 9,51 / 2,46 |
| Ústí 24 h | 7,71 / 4,10 | 7,57 / 2,05 | 7,76 / 3,94 | 7,64 / 2,02 | 7,57 / 2,05 |

Provozní data ČHMÚ 25. 9.–23. 10. 2026 (583 hodin, stejné řádky pro všechny varianty; chyba / směrodatná odchylka
hodinové změny předpovědi v cm, realita 2,2 v Děčíně a 5,1 v Ústí):

| cíl, h | týmový Ridge | (a) | (b) | (c) | (d) |
|---|---|---|---|---|---|
| Děčín 12 h | 5,78 / 4,91 | 5,29 / 2,42 | 5,67 / 4,83 | 5,26 / 2,46 | 5,29 / 2,42 |
| Děčín 24 h | 7,57 / 6,18 | 6,86 / 3,12 | 7,49 / 6,06 | 6,76 / 3,13 | 6,86 / 3,12 |
| Děčín 36 h | 8,08 / 7,14 | 7,20 / 3,63 | 7,76 / 6,81 | 6,96 / 3,47 | 7,20 / 3,63 |
| Ústí 24 h | 9,20 / 6,74 | 8,27 / 3,37 | 8,88 / 6,66 | 8,07 / 3,40 | 8,27 / 3,37 |

Všechny kombinace v `kmitani/klid.csv` a `kmitani/provoz.csv`.

## Co z toho plyne

- Kmitání nejde hlavně ze čtyř stanic pod vodními díly (vyhlazení jejich průtoků ho skoro nezměnilo); model je citlivý
  na hodinové změny mnoha vstupů najednou. Vyhlazení výstupu ho spolehlivě půlí, ale stejně spolehlivě zpozdí reakci
  na začátek vzestupu, a to je u povodňové předpovědi to nejdůležitější.
- Při nízké vodě je vyhlazená předpověď i přesnější (provoz 7,6 → 6,9 cm), protože kmitání je tam čistý šum.
- Proto: model a hodnocení beze změny; v aplikaci jen zobrazení v Dnešku (`patche/11.patch`), s větou v popisku,
  že pod 1. stupněm je předpověď průměrem za poslední 3 hodiny.

## Patch 11 (`patche/11.patch`, jde samostatně i po 01–10)

- `app/predikce.py`: `vyhlad_nizkou_vodu(cil, ted, pred, posledni)` = pravidlo (d).
- `app/aktualni.py`: v Dnešku se k předpovědi z t spočítají i předpovědi vydané v t − 1 h a t − 2 h ze stejné provozní
  tabulky (jen minulé hodiny) a zobrazí se průměr, když jsou hladina i předpověď pod 1. stupněm.
- `app/app.py`: věta v popisku Dneška. Přehrávání historie i záložka „Jak dobře to funguje“ zůstávají surové.

## Slabiny

- Pravidlo (d) vzniklo po výsledcích (a)–(c); je to rozhodnutí o zobrazení, ne vylepšení modelu, a varování nemění.
- Varování v LOFO se počítají na oknech povodní bez 96 h předchozího kontextu, některé začátky tam vypadnou
  (nález Codexu); týká se všech variant stejně, varování proto hlavně podle Ondrovy validace.
- Provozní ukázka je jen jeden měsíc nízké vody (81–106 cm v Děčíně), o povodních nic neříká.
- Moduly (a) a (c) vyhlazují v rámci jednoho volání `predict` (Ondrova validace předává celé okno); v aplikaci je
  historie předávaná výslovně (patch 11).
