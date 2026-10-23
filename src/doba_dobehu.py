"""Za kolik hodin doteče změna průtoku ze stanice proti proudu do Děčína a Ústí.

Hledá posun 0–48 h s největší korelací změn průtoku za 6 h (cíl v čase t, stanice v t − posun).
Počítá se jen na trénovací části. `python src/doba_dobehu.py`
"""
import pandas as pd

from data import CILE, PROTI_PROUDU, nacti
from evaluate import casti

ZMENA_H = 6
MAX_POSUN = 48


def stanice_nad(cil):
    return (["usti"] if cil == "decin" else []) + list(PROTI_PROUDU)


def doby(cil, jen_velka_voda=False):
    D = nacti()
    dQ = D.filter(like="_Q").diff(ZMENA_H)
    ok = casti(cil, 0) == "train"
    if jen_velka_voda:
        ok &= D[f"{cil}_H"] >= 300
    c = dQ[f"{cil}_Q"].where(ok)
    radky = []
    for s in stanice_nad(cil):
        r = pd.Series({k: c.corr(dQ[f"{s}_Q"].shift(k)) for k in range(MAX_POSUN + 1)})
        radky.append(dict(stanice=s, posun_h=int(r.idxmax()), korelace=round(r.max(), 2)))
    return pd.DataFrame(radky).set_index("stanice")


if __name__ == "__main__":
    nazvy = {k: f"{n} ({dbc})" for k, (dbc, n) in (CILE | PROTI_PROUDU).items()}
    for cil in CILE:
        t = doby(cil).join(doby(cil, jen_velka_voda=True).add_suffix("_nad_300cm"))
        t.index = t.index.map(nazvy)
        print(f"\ndo {nazvy[cil]}, trénovací část:\n{t.to_string()}")
