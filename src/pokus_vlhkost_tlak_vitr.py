"""Pokus: pomůže vlhkost, tlak nebo vítr? Lineární regrese s denními hodnotami po větvích povodí a bez nich, jen validace.

python src/pokus_vlhkost_tlak_vitr.py
Denní průměr dne D je známý až po jeho konci, bereme ho jako teplotu v src/meteo.py od D+1 07:00 UTC.
Varianta „předem“ je myšlenkový pokus, jako bychom hodnoty dne D znali už o půlnoci (dokonalá předpověď na den).
"""
import re

import numpy as np
import pandas as pd

from evaluate import casti, vyhodnot
from features import tabulka
from meteo import RAW
from models import ridge
from stahni_chmu_meteo import STANICE

RADEK = re.compile(r'\["([^"]+)","(H|P|F|D10)","([^"]*)","(20(?:0[5-9]|1\d|2[0-6])-[^"]*)",([^,]*),')


def denni(wsi):
    rows = []
    with open(RAW / f"dly-{wsi}.json", encoding="utf-8") as fh:
        for line in fh:
            m = RADEK.search(line)
            if m and (m.group(2) == "D10" or m.group(3) == "AVG"):
                rows.append((m.group(2), pd.Timestamp(m.group(4)).normalize(), float(m.group(5).strip("\"") or "nan")))
    d = pd.DataFrame(rows, columns=["el", "den", "val"])
    # směr větru nemá denní průměr, průměrujeme tři pozorování jako vektory
    smer = np.deg2rad(d[d.el == "D10"].set_index("den").val)
    out = d[d.el != "D10"].pivot_table(index="den", columns="el", values="val")
    out["Dsin"], out["Dcos"] = np.sin(smer).groupby(level=0).mean(), np.cos(smer).groupby(level=0).mean()
    return out


def postav(posun_h):
    hodiny = pd.date_range("2006-01-01", "2025-12-31 23:00", freq="h", tz="UTC")
    out = {}
    for vetev, stanice in STANICE.items():
        d = {w: denni(w) for w in stanice}
        prumer = lambda el: pd.concat({w: x[el] for w, x in d.items() if el in x}, axis=1).mean(axis=1)
        tab = {f"vlhkost_{vetev}": prumer("H"), f"tlak_{vetev}": prumer("P"), f"tlak_{vetev}_zmena_1d": prumer("P").diff(),
               f"vitr_{vetev}": prumer("F"), f"vitr_smer_sin_{vetev}": prumer("Dsin"),
               f"vitr_smer_cos_{vetev}": prumer("Dcos")}
        for c, s in tab.items():
            out[c] = s.set_axis(s.index + pd.Timedelta(hours=posun_h)).reindex(hodiny, method="ffill")
    return pd.DataFrame(out).astype("float64")


if __name__ == "__main__":
    varianty = {"zname": postav(31), "predem": postav(0)}
    for k, M in varianty.items():
        print(k, M.shape, "chybí", round(M.isna().mean().max() * 100, 1), "%", flush=True)
    skupiny = {"vlhkost": "vlhkost", "tlak": "tlak", "vitr": "vitr"}
    rows = []
    for cil in ("decin", "usti"):
        for h in (12, 24, 36):
            X, y = tabulka(cil, h)
            X = X.join(varianty["zname"]).join(varianty["predem"].add_suffix("_predem")).dropna()
            y = y[X.index]
            c = casti(cil, h).reindex(X.index)
            tr, ev = c == "train", c == "val"
            zaklad = [col for col in X if not col.startswith(("vlhkost", "tlak", "vitr"))]
            nove = [col for col in X if col not in zaklad and not col.endswith("_predem")]
            sady = {"bez": zaklad, "vse": zaklad + nove, "vse_predem": zaklad + [f"{x}_predem" for x in nove]}
            sady |= {s: zaklad + [x for x in nove if x.startswith(p)] for s, p in skupiny.items()}
            r = dict(cil=cil, h=h)
            for s, cols in sady.items():
                r[s] = vyhodnot(y[ev], ridge.fit(X.loc[tr, cols], y[tr], cil, h)(X.loc[ev, cols]), cil, h)["mae_povodne"]
            rows.append(r)
            print({k: round(v, 2) if isinstance(v, float) else v for k, v in r.items()}, flush=True)
    R = pd.DataFrame(rows)
    print("\nprumer_povodne (cm):\n" + R.drop(columns=["cil", "h"]).mean().round(2).to_string())
