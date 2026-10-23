"""Pokus: pomohou další stanice proti proudu, které máme stažené, ale model je nebere? Hlavně horní Ohře (Dan to na své
větvi zkoušel s 30 stanicemi). Lineární regrese na validaci a ve vícenásobné validaci přes 8 povodní, vždy na stejných řádcích.

python src/pokus_dalsi_stanice.py
"""
import glob
import json

import numpy as np
import pandas as pd

from data import OD, DO, RAW, nacti
from evaluate import casti, vyhodnot
from features import ZPOZDENI_Q, tabulka
from krizova_validace import BLOKY, casti_blok, chyba_povodne
from models import ridge

# Kadaň (215100) a Postoloprty na Chomutovce (218700) mají v 2006–2025 díry 5 a 7 let, ty bychom museli vyřadit s celými povodněmi
DALSI = {"karlovy_vary": "214000", "zatec": "216000", "zbraslav": "169000"}
VARIANTY = {"tym_12": [], "horni_ohre": ["karlovy_vary", "zatec"], "horni_ohre_zbraslav": list(DALSI)}


def prutok(dbc):
    casti_ = []
    for f in glob.glob(str(RAW / f"H_0-203-1-{dbc}_HQ_*.json")):
        if OD[:4] <= f[-9:-5] <= DO[:4]:
            for ts in json.load(open(f))["tsList"]:
                if ts["tsConID"][0] == "Q":
                    casti_.append(pd.DataFrame(ts["tsData"]["data"]["values"], columns=["t", "v"]))
    d = pd.concat(casti_).assign(t=lambda x: pd.to_datetime(x.t, utc=True)).drop_duplicates("t").set_index("t").v
    return d.sort_index().reindex(nacti().index).astype("float64")


Q = pd.DataFrame({k: prutok(dbc) for k, dbc in DALSI.items()})
print("chybí hodin 2006–2025:", Q.isna().sum().to_dict())
Z = pd.DataFrame({f"{k}_Q_{z}": Q[k].shift(z) for k in Q for z in ZPOZDENI_Q})

rows, cv = [], []
for cil in ("decin", "usti"):
    for h in (12, 24, 36):
        X, y = tabulka(cil, h)
        X = X.join(Z).dropna()  # všechny varianty na stejných řádcích
        y = y[X.index]
        zaklad = [c for c in X if c not in Z]
        sloupce = {v: zaklad + [c for c in Z if c.rsplit("_Q_", 1)[0] in s] for v, s in VARIANTY.items()}
        c = casti(cil, h).reindex(X.index)
        tr, ev = c == "train", c == "val"
        for v, cols in sloupce.items():
            m = vyhodnot(y[ev], ridge.fit(X[tr][cols], y[tr], cil, h)(X[ev][cols]), cil, h)
            rows.append(dict(cil=cil, h=h, varianta=v, val=m["mae_povodne"],
                             chyby=m["spa2_propasnuto"] + m["spa3_propasnuto"] + m["spa2_plane_poplachy"]))
        for blok, dny in BLOKY.items():
            c = casti_blok(cil, h, dny).reindex(X.index)
            tr, ev = c == "train", c == "val"
            for v, cols in sloupce.items():
                pred = pd.Series(np.asarray(ridge.fit(X[tr][cols], y[tr], cil, h)(X[ev][cols])), index=X.index[ev])
                cv.append(dict(cil=cil, h=h, povoden=blok, varianta=v, chyba=chyba_povodne(y[ev], pred, cil)))
        print(cil, h, "hotovo", flush=True)
R = pd.DataFrame(rows)
C = pd.DataFrame(cv)
P = C.groupby(["povoden", "varianta"]).chyba.mean().unstack()[list(VARIANTY)]
print("\nvalidace, chyba na povodních (cm):\n" + R.pivot_table(index=["cil", "h"], columns="varianta", values="val")[list(VARIANTY)].to_string())
print("validace průměr:", R.groupby("varianta").val.mean().round(1).to_dict(), "chyby ve varování:", R.groupby("varianta").chyby.sum().to_dict())
print("\nvícenásobná validace po povodních (průměr 6 kombinací):\n" + P.round(1).to_string())
print("průměr ± odchylka:", {v: f"{P[v].mean():.1f} ± {P[v].std():.1f}" for v in P})
print("kolikrát lepší než tým_12:", {v: int((P[v] < P.tym_12).sum()) for v in P if v != "tym_12"})
