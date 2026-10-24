"""Pokus: pomohou srážky, sníh a teplota? Lineární regrese a síť s meteo vstupy a bez nich na stejných řádcích validace.

python src/pokus_meteo.py [--o-den-driv] [--jen-ridge]
"""
import sys

import pandas as pd

from evaluate import casti, vyhodnot
from features import tabulka
from meteo import SOUBOR
from models import mlp, ridge

soubor = SOUBOR.with_name("labe_meteo_o_den_driv.parquet") if "--o-den-driv" in sys.argv else SOUBOR
M = pd.read_parquet(soubor).astype("float64")
skupiny = {"vse": list(M.columns), "jen_srazky": [c for c in M if c.startswith(("srazky", "api30"))],
           "jen_snih_teplota": [c for c in M if c.startswith(("snih", "teplota"))]}
modely = {"ridge": ridge.fit} if "--jen-ridge" in sys.argv else {"ridge": ridge.fit, "mlp": mlp.fit}
rows = []
for cil in ("decin", "usti"):
    for h in (12, 24, 36):
        X, y = tabulka(cil, h)
        X = X.join(M).dropna()
        y = y[X.index]
        c = casti(cil, h).reindex(X.index)
        tr, ev = c == "train", c == "val"
        zaklad = [col for col in X if col not in M]
        for nazev, fit in modely.items():
            r = dict(model=nazev, cil=cil, h=h)
            for sk, cols in ({"bez": []} | skupiny).items():
                if nazev == "mlp" and sk.startswith("jen"):
                    continue
                XX = X[zaklad + cols]
                r[sk] = vyhodnot(y[ev], fit(XX[tr], y[tr], cil, h)(XX[ev]), cil, h)["mae_povodne"]
            rows.append(r)
            print(r, flush=True)
R = pd.DataFrame(rows)
print("\nprumer_povodne:\n" + R.groupby("model")[[c for c in ("bez", *skupiny) if c in R]].mean().round(1).to_string())
