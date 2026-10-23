# Společný základ: týmové modely + 18 nových stanic

Pro další session (srážky, síť). Čte se odsud, nic z toho nemění týmový kód.

- `spolecne.py`: `data(cil, horizont)` → `X` (98 týmových sloupců z `features.tabulka`), `Xn` (+ 126 sloupců:
  průtoky 18 nových stanic z `ridge_dan/tabulka/labe_ridge.parquet` se zpožděními 0/3/6/12/18/24/36 h, spojené
  podle času UTC), `y`, `c` (`evaluate.casti`). Obě varianty mají vždy stejné řádky (nové stanice nemají díry).
  `cv_predikce(fit, X, y, c, cil, h)` a `cv_skore(...)`: časová CV v tréninku (6 bloků let, mezera 10 dní), hlavní
  číslo `cv_povodne` = průměr přes 18 povodní nad 400 cm. `val_metriky`, `povoden_2006` pro validaci.
- `spust.py <model>`: CV (Děčín +24 h) a validace všech 6 kombinací jako `porovnej.py`, zápis do `vysledky.jsonl`.
  Test 2021–2025 se tady nespouští.
- Vlastní tabulka není v Gitu: `python ridge_dan/stahni_hydro.py`, `stahni_srazky.py`, `stahni_snih.py`
  a `python ridge_dan/data_ridge.py` (asi 25 min stahování, šetrně, cache).
- Na Windows `PYTHONUTF8=1`.

## LOFO-CV foldy (`lofo_foldy.csv`, kód `ridge_dan/zlepseni/lofo.py`)

22 povodní 2006–2020 v Děčíně (vrchol cíle nad 400 cm, `evaluate.povodne` na y = stav v t + horizont, index = čas
vydání t, UTC). Fold k: hodnotí se okno `okno_od`–`okno_do` (7 dní před až 5 dní po vrcholu), z tréninku se vyřadí
`mezera_od`–`mezera_do` (okno ± 20 dní), trénuje se na všech ostatních řádcích. Řádky (stejné pro všechny varianty):
řádky `features.tabulka("decin", h)` (všech 98 týmových vstupů známých), t + h < 2021-01-01 (test se nepoužívá)
a t ≥ první řádek + 72 h (rezerva pro zpoždění až 72 h); `radku_celkem` je jejich počet. Skóre = průměr MAE přes
22 oken, k tomu chyby po povodních a znaménkový test proti základu (týmový Ridge).
