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
