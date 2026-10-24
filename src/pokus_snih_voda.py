"""Pokus: pomůže vodní hodnota sněhu (kolik mm vody je ve sněhu, ČHMÚ ji měří jednou týdně) a její úbytek za týden (roztálo)?
Lineární regrese na validaci, po větvích povodí, každá hodnota až den po změření. Jen validace.

Druhá část: zvláštní zimní model (listopad–duben) učený jen na zimě, hodnocený na zimních povodních 2006, 2009 a 2011.
Navíc „tání“ = voda ve sněhu × průměrná teplota nad nulou, protože sníh taje jen v teple.

python src/pokus_snih_voda.py
"""
import re

import pandas as pd

from data import SPA
from evaluate import PO, PRED, casti, povodne, vyhodnot
from features import tabulka
from meteo import RAW, SOUBOR, STANICE
from models import ridge

RADEK = re.compile(r'\["([^"]+)","(SVH|SCE)","([^"]*)","(20(?:0[5-9]|1\d|2[0-6])-[^"]*)",([^,]*),')
HODINY = pd.date_range("2006-01-01", "2025-12-31 23:00", freq="h", tz="UTC")


def voda_ve_snehu(wsi):
    rows = []
    with open(RAW / f"dly-{wsi}.json", encoding="utf-8") as fh:
        for line in fh:
            m = RADEK.search(line)
            if m:
                rows.append((m.group(2), pd.Timestamp(m.group(4)).normalize(), float(m.group(5).strip("\"") or "nan")))
    d = pd.DataFrame(rows, columns=["el", "den", "val"]).pivot_table(index="den", columns="el", values="val")
    d = d.reindex(pd.date_range(d.index.min(), d.index.max(), freq="D"))
    # bez sněhu je voda ve sněhu 0, jinak platí poslední týdenní měření
    svh = d.SVH.where(d.SVH.notna() | (d.SCE != 0), 0).ffill(limit=7)
    return svh


S = {}
for vetev, stanice in STANICE.items():
    svh = pd.concat({w: voda_ve_snehu(w) for w in stanice}, axis=1)
    print(vetev, "stanic s měřením:", int((svh.max() > 0).sum()), "z", len(stanice))
    svh = svh.mean(axis=1)
    for nazev, s in {f"svh_{vetev}": svh, f"svh_{vetev}_ubytek_7d": (svh.shift(7) - svh).clip(lower=0)}.items():
        # měří se ráno, bereme až od dalšího dne 07:00 UTC jako ostatní denní data
        S[nazev] = s.set_axis(s.index + pd.Timedelta(hours=31)).reindex(HODINY, method="ffill")
S = pd.DataFrame(S)
T = pd.read_parquet(SOUBOR).astype("float64").filter(regex="^teplota")

rows, povodnove = [], []
for cil in ("decin", "usti"):
    for h in (12, 24, 36):
        X, y = tabulka(cil, h)
        X = X.join(S).join(T).dropna()
        y = y[X.index]
        c = casti(cil, h).reindex(X.index)
        tr, ev = c == "train", c == "val"
        zaklad = [x for x in X if x not in S and x not in T]
        varianty = {"bez": zaklad, "voda_ve_snehu": zaklad + list(S), "voda_ve_snehu_teplota": zaklad + list(S) + list(T)}
        P = {k: pd.Series(ridge.fit(X[tr][v], y[tr], cil, h)(X[ev][v]), index=y[ev].index) for k, v in varianty.items()}
        r = dict(cil=cil, h=h)
        for k, p in P.items():
            m = vyhodnot(y[ev], p, cil, h)
            r |= {k: m["mae_povodne"], f"{k}_chyby": m["spa2_propasnuto"] + m["spa3_propasnuto"] + m["spa2_plane_poplachy"]}
        rows.append(r)
        for v in povodne(y[ev], SPA[cil][1]):
            povodnove.append(dict(cil=cil, h=h, povoden=f"{v + pd.Timedelta(hours=h):%Y-%m}")
                             | {k: round(float((p[v - PRED: v + PO] - y[ev][v - PRED: v + PO]).abs().mean()), 1) for k, p in P.items()})
R = pd.DataFrame(rows).set_index(["cil", "h"])
print("\nchyba na povodních (cm) a chyby ve varování:\n" + R.to_string())
print("\nprumer_povodne:", R[list(varianty)].mean().round(1).to_dict())
print("\npo povodních:\n" + pd.DataFrame(povodnove).set_index(["cil", "h", "povoden"]).to_string())

ZIMA = (11, 12, 1, 2, 3, 4)
for vetev in STANICE:
    T[f"tani_{vetev}"] = S[f"svh_{vetev}"] * T[f"teplota_{vetev}"].clip(lower=0)
zimni = []
for cil in ("decin", "usti"):
    for h in (12, 24, 36):
        X, y = tabulka(cil, h)
        X = X.join(S).join(T).dropna()
        y = y[X.index]
        c = casti(cil, h).reindex(X.index)
        zima = X.index.month.isin(ZIMA)
        tr, ev = (c == "train") & zima, (c == "val") & zima
        zaklad = [x for x in X if x not in S and x not in T]
        tani = [f"tani_{v}" for v in STANICE]
        # celoroční modely se učí na celém roce, zimní jen na zimě; hodnotí se všechny jen na zimě
        varianty = {"celorocni_bez": zaklad, "celorocni_tani": zaklad + tani, "zimni_bez": zaklad,
                    "zimni_snih": zaklad + list(S), "zimni_snih_tani": zaklad + list(S) + tani}
        r = dict(cil=cil, h=h)
        for k, v in varianty.items():
            uceni = c == "train" if k.startswith("celorocni") else tr
            p = ridge.fit(X[uceni][v], y[uceni], cil, h)(X[ev][v])
            m = vyhodnot(y[ev], p, cil, h)
            r |= {k: m["mae_povodne"], f"{k}_chyby": m["spa2_propasnuto"] + m["spa3_propasnuto"] + m["spa2_plane_poplachy"]}
        zimni.append(r)
Z = pd.DataFrame(zimni).set_index(["cil", "h"])
print("\njen zima, zimní povodně 2006, 2009, 2011 (cm a chyby ve varování):\n" + Z.to_string())
print("\nprumer:", Z[[k for k in Z if not k.endswith("chyby")]].mean().round(1).to_dict())

print("\nvoda ve sněhu (mm) na začátku validačních povodní:")
for d in ("2006-03-20", "2009-02-25", "2010-09-15", "2011-01-05"):
    print(d, S.loc[d + " 12:00", [c for c in S if not c.endswith("7d")]].round(0).to_dict())
