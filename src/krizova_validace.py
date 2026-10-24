"""Vícenásobná validace: každou povodeň 2006–2020 nad 2. stupněm v Děčíně jednou vynecháme, model naučíme na zbytku
2006–2020 (bez 20 dní kolem vynechané povodně) a změříme chybu na ní. Test 2021–2025 se nepoužívá.

python src/krizova_validace.py ridge mlp lgbm fyzika
Výsledky do results/krizova_validace/<čas>.csv, souhrn do konzole.
"""
import importlib
import sys
from datetime import datetime

import numpy as np
import pandas as pd

from data import SPA, nacti
from evaluate import NEJSTARSI, OKNO_VAL, PO, PRED, TEST_OD, VYNECHAT, povodne, vyhodnot
from features import tabulka
from porovnej import RESULTS

# povodně nad 2. stupněm v Děčíně 2006–2020; dva vrcholy v červnu 2013 jsou 21 dní od sebe, proto jeden blok
BLOKY = {"2006-04": ["2006-04-03"], "2006-06": ["2006-06-01"], "2009-03": ["2009-03-07"], "2010-08": ["2010-08-09"],
         "2010-09": ["2010-09-29"], "2011-01": ["2011-01-17"], "2013-02": ["2013-02-02"],
         "2013-06": ["2013-06-06", "2013-06-27"]}


def casti_blok(cil, horizont, dny):
    H = nacti()[f"{cil}_H"]
    c = pd.Series("train", index=H.index)
    vrcholy = [H[pd.Timestamp(d, tz="UTC") - pd.Timedelta(days=3):][:144].idxmax() for d in dny]
    for v in vrcholy:
        c[v - OKNO_VAL - VYNECHAT: v + PO + VYNECHAT] = ""
    for v in vrcholy:
        c[v - OKNO_VAL: v + PO] = "val"
    c[TEST_OD:] = ""
    ok = (c == c.shift(-horizont)) & (c == c.shift(NEJSTARSI))
    return c.where(ok, "")


def chyba_povodne(y, pred, cil):
    """Průměrná chyba v okně kolem vrcholů nad 1. stupněm (stejné okno jako v evaluate.py)."""
    okno = pd.Series(False, index=y.index)
    for v in povodne(y, SPA[cil][0]):
        okno[v - PRED: v + PO] = True
    return round(float((pred - y)[okno].abs().mean()), 1)


if __name__ == "__main__":
    modely = ["jako_ted"] + sys.argv[1:]
    rows = []
    for cil in ("decin", "usti"):
        for h in (12, 24, 36):
            X, y = tabulka(cil, h)
            for blok, dny in BLOKY.items():
                c = casti_blok(cil, h, dny).reindex(X.index)
                tr, ev = c == "train", c == "val"
                for nazev in modely:
                    pred = pd.Series(np.asarray(importlib.import_module(f"models.{nazev}").fit(
                        X[tr], y[tr], cil=cil, horizont=h)(X[ev]), dtype=float), index=X.index[ev])
                    m = vyhodnot(y[ev], pred, cil, h)
                    rows.append(dict(cil=cil, h=h, povoden=blok, model=nazev, chyba=chyba_povodne(y[ev], pred, cil),
                                     propasnuto=m["spa2_propasnuto"] + m["spa3_propasnuto"], plane=m["spa2_plane_poplachy"]))
                    print(rows[-1], flush=True)
    R = pd.DataFrame(rows)
    (RESULTS / "krizova_validace").mkdir(exist_ok=True)
    soubor = RESULTS / "krizova_validace" / f"{datetime.now():%Y-%m-%d_%H%M%S}.csv"
    R.to_csv(soubor, index=False)
    P = R.pivot_table(index=["cil", "h", "povoden"], columns="model", values="chyba")
    print("\nchyba na povodni (cm), každý řádek jedna vynechaná povodeň:\n" + P[modely].to_string())
    prumer = R.groupby(["povoden", "model"]).chyba.mean().unstack()[modely]
    print("\nprůměr přes 6 kombinací po povodních:\n" + prumer.round(1).to_string())
    print("\nprůměr ± směrodatná odchylka přes povodně:\n"
          + (prumer.mean().round(1).astype(str) + " ± " + prumer.std().round(1).astype(str)).to_string())
    print("\nkolikrát byl model nejlepší (z povodní):\n" + prumer.drop(columns="jako_ted").idxmin(axis=1).value_counts().to_string())
    print("\npropásnuté + plané poplachy celkem:\n" + R.groupby("model")[["propasnuto", "plane"]].sum().to_string())
    print(f"uloženo {soubor.relative_to(RESULTS.parent)}")
