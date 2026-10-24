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

## (d) 18 nových stanic ve všech týmových modelech, pá 22:53–22:56 (`codex/kontrola_d_stanice_vsem.md`)
Celkově: na letech 2006–2020 potvrdil shodné řádky obou variant, shodu základních variant s původními modely,
spojení podle času bez budoucích vstupů a strom fyzikálního modelu bez zjevného dvojího počítání vody.

| Nález | Závažnost | Co jsem udělal |
|---|---|---|
| 1. LightGBM: doby doběhu nových stanic odhadnuté z celého tréninku včetně drženého bloku CV, cache sdílená mezi foldy | vysoká | Opraveno: doby se odhadují uvnitř `fit()` jen z hodin, na kterých se model učí (v CV z trénovací části foldu). CV i validace `lgbm_30` přepočítané. Týmové pevné doby `lgbm_a.DOBA` jsou z celého tréninku taky, to je vlastnost týmového modelu a nechávám ji (v CV tedy obě varianty mají u týmových stanic stejnou drobnou výhodu). |
| 2. `cv_max_prestreleni` byl průměr maxim po povodních, slibovaný 95. percentil chyběl | střední | Opraveno: `cv_prumer_max_prestreleni`, `cv_p95_prestreleni` (přes všechny hodiny oken) a `cv_max_prestreleni` (největší vůbec); CV všech variant přepočítaná. |
| 3. Seedy 42/43/44 u LightGBM dávají totožné výsledky, nejsou to tři nezávislá ověření | nízká | Souhlasím: týmový LightGBM nemá náhodný výběr řádků ani vstupů, takže seed nic nemění. Dál jen seed 42, ve zprávě uvedeno „rozptyl 0, model je deterministický“. |

## (e) kontrola čísel ve STANICE_VSEM.md, pá 23:06–23:07 (`codex/kontrola_e_stanice_cisla.md`)
Celkově: čísla včetně stability sedí, oprava doby doběhu u LightGBM nečerpá z drženého bloku, varianty se liší jen
stanicemi, závěr odpovídá hranici 1 cm. Jediný nález (nízký): CV vzestup Ridge s 30 stanicemi je 28,747, tedy
28,7, ne 28,8 (zaokrouhlené dvakrát). Opraveno ve STANICE_VSEM.md a ZPRAVA.md.

## (h) přísné hodnocení zlepšení, so 00:05–00:08 (`codex/kontrola_h_zlepseni.md`)
Dva vysoké nálezy: únik ve vnitřním hodnocení vnořených výběrů (okno j bez ohledu na mezeru k) a H30 jako výsledek
s návrhem z hodnocené povodně. Motor opraven, verdikt přepsán (H30 průzkumně), podrobně v ZLEPSENI.md.
Codex G (směsi) pracoval jako experimentátor se zápisem jen do `ridge_dan/smesi/`, 35 min, G1 a G2.

## (i) moduly g3.py a ridge30.py před Ondrovou vícenásobnou validací, so 01:12–01:14 (`codex/kontrola_i_g3_moduly.md`)
Celkově: rozhraní připravené pro `src/krizova_validace.py`; ověřil shodné indexy (UTC, hodinové), žádné NaN
v připojených 126 sloupcích pro všech 6 kombinací, posuny ani sezónnost bez budoucnosti, LightGBM vynechává 4 stanice
pod Ústím, parametry G3 odpovídají ZLEPSENI.md; fit Ridge30 na nesouvislé podmnožině vrátil správnou délku a vstup nezměnil.

| Nález | Závažnost | Co jsem udělal |
|---|---|---|
| Odhad doby doběhu nových stanic počítá `diff(6)` a `shift(k)` přes okraje tréninku (dvojice, kde část zdrojových časů leží mimo předané tréninkové hodiny) | střední | Opraveno pro G3: `lgbm_stanice.doby(..., prisne=True)` bere do korelace jen dvojice se všemi časy (t, t − 6, t − k, t − k − 6) v tréninku, `g3.py` ji používá. Pohled do budoucnosti řádku to nebyl, 20denní mezera vynechanou povodeň chránila. Na foldu 2006 se tím změnila jen doba z Bíliny (32 → 33 h). Dřívější běhy (STANICE_VSEM, ZLEPSENI) použily volnou variantu, ta zůstává výchozí kvůli opakovatelnosti jejich čísel. |
| Týmové doby doběhu (`lgbm_a.DOBA`) jsou pevné z původního splitu, který obsahuje některé povodně vynechávané v krizova_validace | střední | Zděděná vlastnost týmového LightGBM, týká se stejně Ondrova `lgbm` i G3. Týmový kód se nemění, zapsáno jako výhrada ve VALIDACE_ONDRA.md. |
| Importy mění `sys.path` a nastavují `OPENBLAS_NUM_THREADS`, hrozí kolize jmen modulů | střední | Ověřeno, že žádný modul v `ridge_dan/` a `ridge_dan/stanice_vsem/` nemá stejné jméno jako modul v `src/` (src: data, evaluate, features, …; ridge_dan: data_ridge, hodnoceni, spolecne, …), `ridge30.py` cesty jen přidává na konec. `OPENBLAS_NUM_THREADS` se nastavuje `setdefault` až po načtení numpy v krizova_validace, tedy bez účinku; běh se spouští s 4 vlákny výslovně. Shoda `ridge` a `lgbm` s Ondrovým uloženým během (níž) potvrzuje, že se týmové modely nezměnily. |

## (j) moduly h12.py a h30.py, so 01:47–01:49 (`codex/kontrola_j_h_moduly.md`)
Bez nálezů: odpovídají předem zapsané definici i `zlepseni/pokus_H.py`, bez úniku, rozhraní v pořádku.

## (k) noční zprávy VALIDACE_ONDRA.md a ROZHODNUTI_G3.md, so 03:10–03:12 (`codex/kontrola_k_nocni.md`)
| Nález | Závažnost | Co jsem udělal |
|---|---|---|
| Závěr „G3 nepřekoná nejlepší týmový model o 1 cm“ platí jen pro Ondrovu validaci; v LOFO G3 překoná i síť (−1,13, 17 z 22) | střední | Opraveno, ROZHODNUTI rozlišuje hodnocení (ověřeno: −1,14 po povodních, 17 z 22, nejhorší +9,4). |
| Ridge 30 na 36 h splní pravidlo pro Ústí (−1,00, 5 z 8) | střední | Souhlasím (na hraně, ze zaokrouhlených chyb); doplněny body (a)–(d) pro Ridge 30 na 36 h. |
| Validace G3 18,2 a začátek 27,8 bez uloženého zdroje | střední | Uloženo `zlepseni/vysledky_G3_val.json` (stejný výpočet z uložených validačních předpovědí). |
| Rozsah 0,1–1,1 cm, zvýraznění 36 h, Ridge 2006-06 15,5 vs 15,6, H30 na 24 h −0,3 | nízká | Opraveno (0,04–1,09; Ridge 30 tučně na 36 h; 15,6; Děčín −0,21, Ústí +0,01). |

## (l) druhá nezávislá revize řetězce Ridge 30 na 36 h, so 03:13–03:25 (`codex/kontrola_l_ridge30.md`)
Bez kritických a vysokých nálezů; data (450 zdrojových souborů proti tabulce), stanice, UTC, foldy 36 h i čísla
v ROZHODNUTI_G3.md sedí. Závěr: věrohodné jako retrospektivní CV, převaha aspoň o 1 cm doložená není.
| Nález | Závažnost | Co jsem udělal |
|---|---|---|
| Znaménkový test předpokládá nezávislé povodně, okna 12/2012 a 1/2013 sdílejí 48 h | střední | Zapsáno jako výhrada (p-hodnoty přibližné) v kódu i v ROZHODNUTI; průměry tím nejsou dotčené. |
| `znamenkovy_p: NaN` v JSON (nestandardní) | nízká | `lofo.skore` ukládá `null`, existující `vysledky_*.json` převedené NaN → null. |
