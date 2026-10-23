# Nálezy Codexu a co s nimi

Codex CLI (`codex exec -s read-only`, pravidla v promptu: nic neměnit, nečíst .env ani údaje Kaggle, výstup =
nálezy se souborem, řádkem a závažností). Prompty a plné odpovědi jsou v `codex/`.

## (a) po sestavení dat, pá 21:03–21:06 (`codex/kontrola_a_data.md`)
Celkově: přímý únik budoucích měření nenašel, posun denních srážek potvrdil jako správný.

| Nález | Závažnost | Co jsem udělal |
|---|---|---|
| `priznaky.py`: `nejstarsi` nezahrnuje stáří denních dat (srážkový součet až 47 h + posuny, sníh 48 h), takže řádek na začátku validace může obsahovat srážky z tréninkového období | střední | Opraveno: u srážek se přičítá 24·(k−1) + 23 + 25 h, u sněhu 72 + 23 + 25 h. Není to únik z budoucnosti (data jsou starší než t), ale porušovalo to pravidlo „řádky přes hranici splitu vyhodit“. Pokusy se srážkami a sněhem jsem pustil znovu. |
| `priznaky.py`: `vyplnit_h` (ffill) prodlužuje historii vstupu, ale `nejstarsi` se nezvětší | střední | Opraveno: `nejstarsi += vyplnit_h`. Volba zatím nebyla použitá. |

## (b) v polovině, protokol a přeladění validace, pá 21:37–21:39 (`codex/kontrola_b_protokol.md`)
Celkově: přímý únik nenašel; před testem je potřeba napravit evidenci validace a doložit výběr.

| Nález | Závažnost | Co jsem udělal |
|---|---|---|
| 1. Evidence validace neúplná (reprodukce 20:44, rozbor po povodních), validace ovlivnila směr hledání | vysoká | Souhlasím. V POKUSY_RIDGE.md (21:43) je seznam všech 4 nahlédnutí včetně zkušebního běhu a rozboru a přiznané adaptivní použití; pokusy, které rozbor motivoval, rozhodovala CV a žádný nebyl ponechán. |
| 2. `l_tym_plus_2` je v CV horší než ponechaný `b_vse` (14,41 vs 14,17, vzestup 30,3 vs 28,8), změna základu neodpovídá pravidlu | vysoká | Souhlasím. Pravidlo pro zjednodušení je teď výslovně v protokolu, `l_tym_plus_2` jím neprojde, finální model je zpět `b_vse`. |
| 3. Mnohonásobné porovnávání (69 běhů), přínos horního Labe nejistý | střední | Hlavní tvrzení (30 stanic proti týmu) jsem ověřil po blocích: −1,56 ± 0,62, lepší ve 4 z 5 bloků. Plnou vnořenou CV celého výběru jsem nedělal (výběr stanic ručně po skupinách, nejde zopakovat automaticky); finální model nakonec nepoužívá žádný jemný výběr, jen „všechny stanice s úplnými řadami“. |
| 4. Povodně nejsou nezávislé (překryv 12/2012 a 1/2013, společné bloky) | střední | Přidaná nejistota přes epizody (17) a bloky (5), tabulka v POKUSY_RIDGE.md. |
| 5. Alpha z čísel zaokrouhlených na 0,01, při shodě vyhrála nejmenší | střední | Opraveno: výběr z nezaokrouhlených hodnot, ze shod (do 0,01 cm) největší alpha. Finální alpha 1 místo 0,01, CV i val beze změny (14,17 / 17,8). |
| 6. Protokol nesedí s evidencí (d_srazky po opravě 14,17, korekce není v JSONL, „0,36 do 30 stanic“ patří k 203 sloupcům, chybí otisky) | střední | Opraveno v textu (níž), každý nový záznam v `pokusy.jsonl` má `otisk` (commit, neuložené změny, otisk tabulky a evaluate.py). Korekce běžela mimo `pokus.py`, čísla jsou v POKUSY_RIDGE.md. |
| 7. Stanice vybrané podle úplnosti řad až do 2025 (znalost testovacího období) | nízká | Ověřeno: žádná vodoměrná stanice nevypadla kvůli dírám v testu, všechna vyřazení byla kvůli dírám v tréninku/validaci (Kadaň, Terezín, Litoměřice, Děčín-Březiny, Ústí-Bílina, Postoloprty, Blšanka 2006–2012; Němčice 10/2020). Srážkoměry vybrané s koncem řady ≥ 2025 ve finálním modelu nejsou. |
| 8. Jednorázovost testu není atomická | střední | Opraveno: značka `vysledky/TEST_HOTOVO.json` se zakládá výhradně (mód „x“) před výpočtem, s konfigurací a otiskem; druhé ani souběžné spuštění neprojde. |

## (c) na konci, nezávislá revize kódu a čísel před testem, pá 21:47–21:50 (`codex/kontrola_c_revize.md`)
Celkově: „test_jednou.py je podle zkontrolované logiky připravený na jednorázový test“; ověřil na letech 2006–2020
finální konfiguraci, týmových 98 vstupů, split, týmové předpovědi a čísla CV a validace (17,8 / 15,5 / 44,4).
Přímý únik nenašel, StandardScaler se učí jen na tréninku.

| Nález | Závažnost | Co jsem udělal |
|---|---|---|
| 1. `model_ridge.py` při uložení předpovídal i řádky 2021–2025 (poslední řádek a kontrola konečnosti), mimo ochranu testu | střední | Opraveno, kontrola jen na řádcích do konce 2020. Dřív se vypsala jediná předpověď pro 31. 12. 2025 (114 cm) bez srovnání se skutečností, o přesnosti nic neříká. |
| 2. Aplikace (`app/predikce.py`) nový model sama nenačte: nepřidá `ridge_dan/` do `sys.path`, hledá jinde a dává 98 týmových vstupů | střední | Aplikaci podle zadání neměním; v ZPRAVA.md je popsaný adaptér (přidat `ridge_dan` do `sys.path`, `joblib.load`, `predikuj(T)` z tabulky `data_ridge`). |
| 3. Otisk běhu má jen commit a příznak změn, ne obsahové hashe | střední | Opraveno pro test: značka i výsledek testu obsahují sha1 všech použitých souborů (konce řádků sjednocené na LF) a tabulky; před testem je vše commitnuté. |
| 4. Alpha 100 v textu 14,46, v záznamech 14,45 | nízká | Opraveno. |
