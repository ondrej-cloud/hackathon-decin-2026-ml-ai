# G3 v Ondrově vícenásobné validaci

Dan, větev `dan-ridge`, so 24. 10. 2026 01:10–01:45. Skript `src/krizova_validace.py` beze změny (8 povodní
2006–2020 nad 2. SPA v Děčíně, každá jednou vynechaná i s 20 dny kolem, Děčín i Ústí, horizonty 12/24/36 h,
chyba v okně kolem vrcholů nad 1. SPA, průměr přes 6 kombinací). Test 2021–2025 se nepoužil.

## Verdikt

**G3 (½ Ridge 30 stanic + ½ LightGBM 30 stanic) má 19,6 ± 7,1 cm, Ondrův nejlepší model (lineární regrese)
20,1 ± 7,7 cm: G3 je v průměru o 0,5 cm lepší a lepší v 6 z 8 povodní.** Nejlepší je v 5 z 8 povodní (Ridge
ve 2, Ridge 30 v 1). Horší je u obou povodní s táním sněhu: duben 2006 +5,7 cm a leden 2011 +1,9 cm. Nejvíc pomůže
v červnu 2013 (−3,3 cm). G3 je lepší než lineární regrese ve všech 6 kombinacích cíl × horizont, ale jen o 0,04–1,09 cm
(na 36 h je v obou cílech nejlepší Ridge 30). Má o jeden
planý poplach víc (4 proti 3), propásnutá varování stejně (1).

Zlepšení 0,5 cm je pod hranicí 1 cm, kterou jsme si dali v přísném hodnocení, a 6 z 8 povodní je ve znaménkovém
testu v rámci náhody (p ≈ 0,29). Těchto 8 povodní je navíc podmnožinou 22 povodní, na kterých byl G3 vybrán
(LOFO-CV v `ZLEPSENI.md`), takže to není nezávislé potvrzení, jen jiný pohled na stejná data (víc cílů a horizontů).
Závěr: G3 je v Ondrově validaci o kousek lepší než lineární regrese, ale ne průkazně; pro finále to rozhodnutí
nemění.

## Po povodních (průměr přes 6 kombinací, cm; tučně nejlepší bez „jako teď“)

| Povodeň | jako teď | ridge | mlp | lgbm | fyzika | ridge30 | g3 | nejlepší |
|---|---|---|---|---|---|---|---|---|
| 2006-04 | 54,6 | **18,4** | 22,4 | 23,8 | 28,5 | 24,5 | 24,1 | ridge |
| 2006-06 | 35,4 | 15,6 | 18,8 | 18,5 | 17,4 | 14,9 | **13,4** | g3 |
| 2009-03 | 28,4 | 11,2 | 9,8 | 12,6 | 16,1 | **9,6** | 11,0 | ridge30 |
| 2010-08 | 43,2 | 28,6 | 30,9 | 27,6 | 30,2 | 27,2 | **25,7** | g3 |
| 2010-09 | 45,5 | 21,6 | 23,5 | 24,4 | 28,3 | 21,3 | **21,2** | g3 |
| 2011-01 | 48,6 | **17,3** | 17,5 | 22,0 | 27,6 | 17,7 | 19,2 | ridge |
| 2013-02 | 33,6 | 14,3 | 12,8 | 13,4 | 18,3 | 11,9 | **11,7** | g3 |
| 2013-06 | 72,2 | 33,9 | 32,4 | 39,5 | 46,8 | 34,6 | **30,6** | g3 |
| **průměr ± sm. odch.** | 45,2 ± 13,9 | 20,1 ± 7,7 | 21,0 ± 8,0 | 22,7 ± 8,6 | 26,7 ± 10,0 | 20,2 ± 8,4 | **19,6 ± 7,1** | |

Kolikrát byl model nejlepší (z 8 povodní, bez „jako teď“): G3 5, ridge 2, ridge30 1, mlp, lgbm a fyzika 0.
Jen mezi Ondrovými modely: ridge 4, mlp 3, lgbm 1.

Po kombinacích (průměr přes 8 povodní, cm):

| | Děčín 12 h | Děčín 24 h | Děčín 36 h | Ústí 12 h | Ústí 24 h | Ústí 36 h |
|---|---|---|---|---|---|---|
| ridge | 10,5 | 18,5 | 29,8 | 11,6 | 19,2 | 31,1 |
| ridge30 | 11,0 | 19,1 | **29,0** | 12,0 | 20,0 | **30,1** |
| g3 | **9,9** | **18,1** | 29,7 | **10,5** | **18,6** | 30,8 |

## Varování (součet přes 8 povodní × 6 kombinací)

| Model | propásnutá varování (2. + 3. SPA) | plané poplachy (2. SPA) |
|---|---|---|
| jako teď | 72 | 0 |
| ridge | 1 | 3 |
| mlp | 4 | 5 |
| lgbm | 0 | 4 |
| fyzika | 0 | 4 |
| ridge30 | 1 | 5 |
| g3 | 1 | 4 |

## Jak se počítalo

- Do `dan-ridge` sloučen aktuální `origin/main` (4437a3e). Ondrovy soubory (`krizova_validace.py`, `evaluate.py`,
  `features.py`, `data.py`, `src/models/*`) se neměnily, přibyly jen `src/models/ridge30.py` a `src/models/g3.py`
  se stejným rozhraním `fit(X, y, cil, horizont)` → `predict(X)`.
- `ridge30`: týmový `models.ridge` (odmocnina průtoků, škálování, alpha 1) na 98 týmových vstupech + průtocích
  18 nových stanic se zpožděními 0/3/6/12/18/24/36 h, připojených podle času UTC z `ridge_dan/tabulka/labe_ridge.parquet`
  (není v Gitu, postaví `ridge_dan/data_ridge.py`), pro Děčín i Ústí stejně.
- `g3`: ½ `ridge30` + ½ LightGBM 30 (týmový `lgbm_c` + nové stanice nad cílem, seed 42, týmové parametry, doba
  doběhu nových stanic jen z tréninkových hodin, v přísné podobě po kontrole Codexu). Ploučnice a Bílina se vlévají pod
  Ústím, LightGBM je proto dostává jen pro Děčín.
- Spuštěno `python src/krizova_validace.py ridge lgbm ridge30 g3`, výsledek `results/krizova_validace/2026-10-24_014113.csv`,
  log `ridge_dan/validace_ondra_beh.log`. Síť a fyzika se znovu netrénovaly, jejich čísla jsou z Ondrova
  `results/krizova_validace/2026-10-23_232649.csv`.
- **Reprodukce:** `jako_ted`, `ridge` i `lgbm` dávají ve všech 48 řádcích přesně stejnou chybu jako Ondrův běh
  (rozdíl 0,00 cm) a stejné počty propásnutých a planých poplachů.
- Souhrn `ridge_dan/validace_ondra.py`.

## Kontrola Codexu (i, jen čtení, před během; `codex/kontrola_i_g3_moduly.md`)

Rozhraní v pořádku, bez pohledu do budoucnosti, stanice připojené správně (stejné časy, bez NaN, LightGBM bez stanic
pod Ústím). Tři střední nálezy: (1) odhad doby doběhu nových stanic bral i dvojice přes okraje tréninku → pro G3
opraveno přísnou variantou; (2) týmové doby doběhu `lgbm_a.DOBA` jsou pevné z původního splitu, který obsahuje
některé povodně vynechávané v této validaci → zděděná výhrada, týká se stejně Ondrova `lgbm` i LightGBM části G3;
(3) importy mění `sys.path` → ověřeno, že nehrozí kolize jmen, a přesná shoda `ridge`/`lgbm` s Ondrovým během to
potvrzuje. Podrobně v `NALEZY_CODEX.md`.

## Průzkumně: ukazatel útlumu v nivě (H12, H30), so 01:49–03:09

Předem zapsané (PRUBEH 23:37 a 01:53), bez ladění, Codex (j) bez nálezů. H12 = týmový Ridge + ukazatel útlumu,
H30 = Ridge 30 stanic + ukazatel (průtok po proudu − součet přítoků ve třech úsecích Polabí, zpoždění 0/6/12/24 h).
Moduly `src/models/h12.py`, `h30.py`, výsledek `results/krizova_validace/2026-10-24_030330.csv` (`jako_ted` shodné
s Ondrou; první běh se zasekl na prioritě procesu, druhý dal v prvních 125 řádcích přesně stejná čísla).

| Povodeň | ridge | h12 | ridge30 | h30 | g3 |
|---|---|---|---|---|---|
| 2006-04 | **18,4** | 20,8 | 24,5 | 25,3 | 24,1 |
| 2006-06 | 15,6 | 15,0 | 14,9 | 14,2 | **13,4** |
| 2009-03 | 11,2 | 11,6 | **9,6** | 9,7 | 11,0 |
| 2010-08 | 28,6 | 29,1 | 27,2 | 27,3 | **25,7** |
| 2010-09 | 21,6 | 22,6 | 21,3 | 22,1 | **21,2** |
| 2011-01 | 17,3 | **16,3** | 17,7 | 17,5 | 19,2 |
| 2013-02 | 14,3 | 14,0 | 11,9 | **11,4** | 11,7 |
| 2013-06 | 33,9 | 31,7 | 34,6 | 31,2 | **30,6** |
| průměr ± sm. odch. | 20,1 ± 7,7 | 20,1 ± 7,3 | 20,2 ± 8,4 | 19,8 ± 7,9 | **19,6 ± 7,1** |

H30 proti Ridge −0,28 cm (lepší v 5 z 8), H12 +0,01 (4 z 8): v průměru 6 kombinací nic (H30 na 24 h: Děčín −0,21,
Ústí +0,01). Plané poplachy H30 3,
H12 5 (Ridge 3). **Na horizontu 36 h je ale H30 výrazně lepší:** Děčín 27,6 proti 29,8 (−2,1 cm, 6 z 8 povodní,
nejhorší +3,0), Ústí 28,8 proti 31,1 (−2,3 cm, 6 z 8, nejhorší +1,5). Tentýž pevný model pro Děčín +36 h
v LOFO 22 (`zlepseni/pokus_H36.py`): 22,95 proti 26,39 týmového Ridge (−3,44 cm, 18 z 22, nejhorší +3,1),
na validaci 25,0 proti 26,0. Všechno **průzkumné**: nápad vznikl z rozboru povodně 2006 a 36 h jsem vybral až
po pohledu na rozpad po horizontech; 8 povodní je podmnožina 22.
