"""Pokus: když spojíme všechna malá zlepšení, sečtou se? Lineární regrese a k ní všechno, co na validaci nebo ve vícenásobné
validaci aspoň trochu pomohlo: zrychlení (so 0:01), horní Ohře (so 0:19), naměřené srážky (pá 20:44, 0 cm) a průměr se sítí (pá 20:20).

Hodnotí se na validaci a ve vícenásobné validaci přes 8 povodní, zvlášť na 4 povodních, podle kterých jsme nic nevybírali
(6/2006, 8/2010, 2/2013, 6/2013 byly vždycky v tréninku). Test ne.
python src/pokus_kombinace.py
"""
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

from evaluate import casti, vyhodnot
from features import ZPOZDENI_Q, tabulka
from krizova_validace import BLOKY, casti_blok, chyba_povodne
from meteo import SOUBOR
from models import mlp, ridge
from pokus_dalsi_stanice import prutok
from pokus_nabeh import se_zrychlenim

NOVE = ["2006-06", "2010-08", "2013-02", "2013-06"]
Q = pd.DataFrame({k: prutok(dbc) for k, dbc in {"karlovy_vary": "214000", "zatec": "216000"}.items()})
OHRE = pd.DataFrame({f"{k}_Q_{z}": Q[k].shift(z) for k in Q for z in ZPOZDENI_Q})
SRAZKY = pd.read_parquet(SOUBOR).astype("float64").filter(regex="^(srazky|api30)")


def predpovedi(X, y, tr, ev, cil, h):
    zaklad = [c for c in X if c not in OHRE and c not in SRAZKY]
    s_ohri = zaklad + list(OHRE)
    zrychleni = lambda cols: make_pipeline(FunctionTransformer(se_zrychlenim), StandardScaler(), Ridge(alpha=1.0)) \
        .fit(X[tr][cols], y[tr]).predict(X[ev][cols])
    P = {"ridge": ridge.fit(X[tr][zaklad], y[tr], cil, h)(X[ev][zaklad]),
         "zrychleni": zrychleni(zaklad),
         "horni_ohre": ridge.fit(X[tr][s_ohri], y[tr], cil, h)(X[ev][s_ohri]),
         "kombinace": zrychleni(s_ohri),
         "kombinace_srazky": zrychleni(s_ohri + list(SRAZKY))}
    sit = mlp.fit(X[tr][zaklad], y[tr], cil, h)(X[ev][zaklad])
    P["ridge_a_sit"] = (P["ridge"] + sit) / 2
    P["kombinace_a_sit"] = (P["kombinace"] + sit) / 2
    return {k: pd.Series(np.asarray(v, dtype=float), index=X.index[ev]) for k, v in P.items()}


rows, cv = [], []
for cil in ("decin", "usti"):
    for h in (12, 24, 36):
        X, y = tabulka(cil, h)
        X = X.join(OHRE).join(SRAZKY).dropna()  # všechny varianty na stejných řádcích
        y = y[X.index]
        c = casti(cil, h).reindex(X.index)
        for k, p in predpovedi(X, y, c == "train", c == "val", cil, h).items():
            m = vyhodnot(y[c == "val"], p, cil, h)
            rows.append(dict(cil=cil, h=h, varianta=k, val=m["mae_povodne"],
                             chyby=m["spa2_propasnuto"] + m["spa3_propasnuto"] + m["spa2_plane_poplachy"]))
        for blok, dny in BLOKY.items():
            c = casti_blok(cil, h, dny).reindex(X.index)
            for k, p in predpovedi(X, y, c == "train", c == "val", cil, h).items():
                cv.append(dict(cil=cil, h=h, povoden=blok, varianta=k, chyba=chyba_povodne(y[c == "val"], p, cil)))
        print(cil, h, "hotovo", flush=True)
R, C = pd.DataFrame(rows), pd.DataFrame(cv)
poradi = list(dict.fromkeys(R.varianta))
P = C.groupby(["povoden", "varianta"]).chyba.mean().unstack()[poradi]
souhrn = pd.DataFrame({"validace": R.groupby("varianta").val.mean(), "chyby_varovani": R.groupby("varianta").chyby.sum(),
                       "vicenasobna_8": P.mean(), "jen_4_nove": P.loc[NOVE].mean(),
                       "lepsi_nez_ridge_z_8": (P.lt(P.ridge, axis=0)).sum()}).loc[poradi]
print("\npo povodních:\n" + P.round(1).to_string())
print("\nsouhrn (cm):\n" + souhrn.round(1).to_string())
