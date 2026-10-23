"""Rozbor validace po povodních a fázích (stoupání / vrchol / pokles) pro pokusy, které už validací prošly.

python rozbor_val.py tym b_vse     nové nahlédnutí to není: stejné předpovědi jako v pokusy.jsonl, jen rozpad chyby
"""
import sys

import numpy as np
import pandas as pd

import hodnoceni as Hd
import pokus


def predpovedi(nazev):
    volby = pokus.POKUSY[nazev]
    T, X, y, c = pokus.pripravit(volby)
    alpha = volby.get("alpha") or next(z["alpha"] for z in map(__import__("json").loads,
                                                                 pokus.LOG.read_text(encoding="utf-8").splitlines())
                                       if z["nazev"] == nazev and z.get("val"))
    _, pred = pokus.validace(T, X, y, c, alpha, volby.get("zmena", False), volby.get("vahy"), volby.get("prutok", False))
    return T, y[pred.index], pred


def rozpad(T, y, pred):
    H = T["decin_H"]
    radky = []
    for v in Hd.E.povodne(y, 490):
        okno = (y.index >= v - Hd.E.PRED) & (y.index <= v + Hd.E.PO)
        e = (pred - y)[okno]
        ted = H.reindex(y.index)[okno]
        faze = np.where(y[okno].index < v - pd.Timedelta(hours=24), "stoupání",
                        np.where(y[okno].index <= v + pd.Timedelta(hours=24), "vrchol ±24 h", "pokles"))
        faze = np.where((y[okno] - ted) < 10, np.where(faze == "stoupání", "před vlnou", faze), faze)
        d = pd.DataFrame({"e": e, "faze": faze})
        r = dict(povoden=f"{v:%Y-%m-%d}", vrchol=int(y[v]), mae=round(e.abs().mean(), 1), bias=round(e.mean(), 1))
        r |= {f: round(g.e.abs().mean(), 1) for f, g in d.groupby("faze")}
        radky.append(r)
    return pd.DataFrame(radky)


if __name__ == "__main__":
    for n in sys.argv[1:]:
        T, y, p = predpovedi(n)
        print(n)
        print(rozpad(T, y, p).to_string(index=False))
