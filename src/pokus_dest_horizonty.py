"""Pokus: od jakého horizontu pomáhají srážky? Lineární regrese na 12–72 h bez srážek, s naměřenými srážkami
(jen to, co už spadlo a je známé), s deštěm běžícího dne známým hned od jeho začátku (horní mez pro hodinové srážky
v reálném čase, ty vědí jen to, co už spadlo) a s dokonalou předpovědí deště na 3 dny (horní mez, do modelu se nesmí). Jen validace.

python src/pokus_dest_horizonty.py
"""
import pandas as pd

from data import SPA
from evaluate import PO, PRED, casti, povodne, vyhodnot
from features import tabulka
from meteo import SOUBOR
from models import ridge
from pokus_dest_dopredu import dest_dopredu

namerene = pd.read_parquet(SOUBOR).astype("float64").filter(regex="^(srazky|api30)")
# stejné sloupce, jen o den dřív (python src/meteo.py --o-den-driv)
hned = pd.read_parquet(SOUBOR.with_name("labe_meteo_o_den_driv.parquet")).astype("float64").filter(regex="^(srazky|api30)")
hned.columns = [f"{c}_hned" for c in hned]
dopredu = dest_dopredu()
rows, povodnove = [], []
for cil in ("decin", "usti"):
    for h in (12, 24, 36, 48, 72):
        X, y = tabulka(cil, h)
        X = X.join(namerene).join(hned).join(dopredu).dropna()
        y = y[X.index]
        c = casti(cil, h).reindex(X.index)
        tr, ev = c == "train", c == "val"
        zaklad = [x for x in X if x not in namerene and x not in hned and x not in dopredu]
        varianty = {"bez": zaklad, "namerene": zaklad + list(namerene), "hned": zaklad + list(hned),
                    "dokonala_predpoved": zaklad + list(namerene) + list(dopredu)}
        r = dict(cil=cil, h=h, jako_ted=vyhodnot(y[ev], X[ev][f"{cil}_H_0"], cil, h)["mae_povodne"])
        P = {nazev: pd.Series(ridge.fit(X[tr][cols], y[tr], cil, h)(X[ev][cols]), index=y[ev].index)
             for nazev, cols in varianty.items()}
        # chyba zvlášť na každé validační povodni (okno jako v evaluate.py)
        for v in povodne(y[ev], SPA[cil][1]):
            e = {k: (p[v - PRED: v + PO] - y[ev][v - PRED: v + PO]).abs().mean().round(1) for k, p in P.items()}
            povodnove.append(dict(cil=cil, h=h, povoden=f"{v + pd.Timedelta(hours=h):%Y-%m}") | e)
        for nazev, pred in P.items():
            m = vyhodnot(y[ev], pred, cil, h)
            r |= {nazev: m["mae_povodne"], f"{nazev}_spa2_h": m["spa2_predstih_h"],
                  f"{nazev}_chyby": m["spa2_propasnuto"] + m["spa3_propasnuto"] + m["spa2_plane_poplachy"]}
        rows.append(r)
        print(r, flush=True)
R = pd.DataFrame(rows).set_index(["cil", "h"])
print("\nchyba na povodních (cm):\n" + R[["jako_ted", "bez", "namerene", "hned", "dokonala_predpoved"]].to_string())
print("\npředstih před 2. stupněm (h) a chyby ve varování (propásnuté + plané):\n"
      + R[[c for c in R if c.endswith(("_spa2_h", "_chyby"))]].to_string())
print("\nchyba po jednotlivých povodních (cm):\n" + pd.DataFrame(povodnove).set_index(["cil", "h", "povoden"]).to_string())
