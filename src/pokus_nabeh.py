"""Pokus: proč modely na začátku prudkého vzestupu zaostávají a jde to spravit? Jen validace.

- ridge: finální lineární regrese
- zrychleni: navíc kladný vzestup za 6 h u hladin a odmocnin průtoků všech 14 aktuálních hodnot a jeho druhá mocnina
  (když voda stoupá rychle, předpovědět ještě rychlejší vzestup; lineárně to model umí už z 98 zpoždění, tohle je ohyb navíc)
- horni_mez: stejná předpověď, ale varuje se podle horní meze intervalu nejistoty (95. percentil chyby z tréninku, src/nejistota.py)
Chyba při náběhu = průměrná chyba v hodinách, kdy hladina za h hodin stoupne aspoň o 50 cm.

python src/pokus_nabeh.py
"""
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

from evaluate import casti, vyhodnot
from features import tabulka
from models import ridge
from nejistota import intervaly, pasmo


def se_zrychlenim(X):
    X = ridge.odmocnina_prutoku(X)
    ted = [c for c in X if c.endswith("_0")]
    R = {f"{c[:-2]}_vzestup6": (X[c] - X[f"{c[:-2]}_6"]).clip(lower=0) for c in ted}
    R |= {f"{k}^2": v ** 2 for k, v in R.items()}
    return pd.concat([X, pd.DataFrame(R, index=X.index)], axis=1)


if __name__ == "__main__":
    rows = []
    for cil in ("decin", "usti"):
        for h in (12, 24, 36):
            X, y = tabulka(cil, h)
            c = casti(cil, h).reindex(X.index)
            tr, ev = c == "train", c == "val"
            nabeh = (y[ev] - X.loc[ev, f"{cil}_H_0"]) >= 50
            P = {"ridge": ridge.fit(X[tr], y[tr], cil, h)(X[ev]),
                 "zrychleni": make_pipeline(FunctionTransformer(se_zrychlenim), StandardScaler(), Ridge(alpha=1.0))
                 .fit(X[tr], y[tr]).predict(X[ev])}
            q, _ = intervaly(cil, h)
            P["horni_mez"] = P["ridge"] + q.horni.reindex(pasmo(X.loc[ev, f"{cil}_H_0"]).astype(str)).to_numpy()
            for nazev, pred in P.items():
                pred = pd.Series(np.asarray(pred, dtype=float), index=y[ev].index)
                m = vyhodnot(y[ev], pred, cil, h)
                rows.append(dict(cil=cil, h=h, varianta=nazev, povodne=m["mae_povodne"],
                                 nabeh=round(float((pred - y[ev])[nabeh].abs().mean()), 1),
                                 nabeh_bias=round(float((pred - y[ev])[nabeh].mean()), 1), nabeh_hodin=int(nabeh.sum()),
                                 spa2_h=m["spa2_predstih_h"], spa3_h=m["spa3_predstih_h"],
                                 propasnuto=m["spa2_propasnuto"] + m["spa3_propasnuto"], plane=m["spa2_plane_poplachy"]))
    R = pd.DataFrame(rows).set_index(["cil", "h", "varianta"])
    print(R.to_string())
    print("\nprůměr přes 6 kombinací:\n" + R.groupby("varianta")[["povodne", "nabeh", "nabeh_bias", "spa2_h", "spa3_h"]].mean().round(1).to_string()
          + "\n\nsoučet:\n" + R.groupby("varianta")[["propasnuto", "plane"]].sum().to_string())
