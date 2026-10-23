# Průběh: vlastní Ridge pro Děčín +24 h

Čas a jedna věta na krok, nejnovější dole.

- pá 20:29 · start, worktree `hackathon-2026-ridge` na nové větvi `dan-ridge` z `origin/main` (b9d263c), upstream na main odpojený, push jen `origin dan-ridge`.
- pá 20:35 · přečtené `src/evaluate.py`, `data.py`, `features.py`, `models/ridge.py`: split závisí na Ondrově tabulce (`casti()` volá `nacti()`), proto ho převezmu do vlastního kódu a ověřím, že dává stejné řádky; `vyhodnot()` je čistá funkce, tu jen importuji.
- pá 20:35 · pozor na čísla: týmový Ridge má Děčín +24 h na val povodních 15,5 cm, 17,1 je průměr přes 6 kombinací (Děčín/Ústí × 12/24/36 h); srovnávat budu na Děčín +24 h a uvedu obojí.
- pá 20:33 · metadata ČHMÚ: Děčín (1-14-04-0010, 50 974 km²) je POD soutokem s Ploučnicí (1-14-03) i Bílinou (1-14-01), obě se vlévají mezi Ústím a Děčínem; Terezín (dolní Ohře) a Litoměřice mají data až od 2013/2017, proto nejdou.
- pá 20:34 · hodinové srážky ČHMÚ začínají až 2018 → beru denní úhrny (jeden soubor na stanici za celou historii); ověřeno na hodinových datech 05–08/2019 Ústí-Kočkov, že denní hodnota s razítkem D 06:00Z je součet D 07:00Z…D+1 06:00Z (rozdíl 0,02 mm), takže smí vstoupit až od D+1 07:00 UTC.
- pá 20:35 · start šetrného stahování hydrologie: 31 stanic (12 týmových + Ploučnice ×3, Bílina, Ohře ×2, Berounka ×5, Vltava Zbraslav, Sázava ×2, horní Labe ×4, Jizera Bakov) × 2006–2025, po jednom souboru, pauza 1,5 s, log STAZENO.csv.
- pá 20:37 · výběr 84 srážkoměrů s řadou 2005–2025 v 11 dílčích povodích (povodí podle čísla hydrologického pořadí zakódovaného ve WSI, jinak podle nejbližšího vodoměru), blízká povodí (Bílina, Ploučnice, Labe Mělník–Děčín) hustěji.
- pá 20:40 · napsané data_ridge.py (tabulka), hodnoceni.py (split převzatý z evaluate.py + metriky klid/vzestup/začátek/poplachy 400/490/560), priznaky.py, pokus.py (časová CV po blocích let s mezerou 10 dní).
- pá 20:44 · kontrola tabulky: 12 týmových sloupců z mého stahování je přesně shodných s `data/external/labe_hodinove.parquet` (rozdíl 0, stejné díry); můj split dává pro +12/24/36 h stejné značky jako `evaluate.casti()` (0 rozdílů z 175 320 hodin).
- pá 20:44 · reprodukce na stejných řádcích (19 264 val hodin): týmový Ridge Děčín +24 h na mé tabulce 15,5 cm (předpovědi shodné s týmovým kódem na Ondrově tabulce na 1e-5), „jako teď“ 44,4 cm; 17,1 cm je průměr týmového Ridge přes všech 6 kombinací cíl × horizont, pro Děčín +24 h je laťka 15,5.
