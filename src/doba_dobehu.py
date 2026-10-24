"""Za kolik hodin doteče změna průtoku ze stanice proti proudu do Děčína a Ústí.

Hledá posun 0–48 h s největší korelací změn průtoku za 6 h (cíl v čase t, stanice v t − posun).
Počítá se jen na trénovací části, celkově i zvlášť pro pásma průtoku v Ústí. `python src/doba_dobehu.py`
"""
import numpy as np
import pandas as pd

from data import CILE, PROTI_PROUDU, nacti
from evaluate import casti

ZMENA_H = 6
MAX_POSUN = 48
PASMA = (0, 300, 800, 1500)  # dolní hranice pásem průtoku v Ústí (m3/s)


def stanice_nad(cil):
    return (["usti"] if cil == "decin" else []) + list(PROTI_PROUDU)


def pasmo(Q_usti):
    return np.searchsorted(PASMA, Q_usti, side="right") - 1


def posun(c, dQ_stanice):
    r = pd.Series({k: c.corr(dQ_stanice.shift(k)) for k in range(MAX_POSUN + 1)})
    return int(r.idxmax()), round(r.max(), 2)


def doby(cil, jen_velka_voda=False):
    D = nacti()
    dQ = D.filter(like="_Q").diff(ZMENA_H)
    ok = casti(cil, 0) == "train"
    if jen_velka_voda:
        ok &= D[f"{cil}_H"] >= 300
    c = dQ[f"{cil}_Q"].where(ok)
    radky = [dict(zip(("stanice", "posun_h", "korelace"), (s, *posun(c, dQ[f"{s}_Q"])))) for s in stanice_nad(cil)]
    return pd.DataFrame(radky).set_index("stanice")


def doby_pasma(cil):
    """Posun a počet trénovacích hodin pro každou stanici a pásmo průtoku v Ústí v čase t."""
    D = nacti()
    dQ = D.filter(like="_Q").diff(ZMENA_H)
    ok = casti(cil, 0) == "train"
    p = pd.Series(pasmo(D["usti_Q"].to_numpy()), index=D.index)
    radky = []
    for s in stanice_nad(cil):
        for i, dolni in enumerate(PASMA):
            v = ok & (p == i) & dQ[f"{cil}_Q"].notna()
            k, r = posun(dQ[f"{cil}_Q"].where(v), dQ[f"{s}_Q"])
            radky.append(dict(stanice=s, pasmo=f"od {dolni}", hodin=int(v.sum()), posun_h=k, korelace=r))
    return pd.DataFrame(radky)


if __name__ == "__main__":
    nazvy = {k: f"{n} ({dbc})" for k, (dbc, n) in (CILE | PROTI_PROUDU).items()}
    for cil in CILE:
        t = doby(cil).join(doby(cil, jen_velka_voda=True).add_suffix("_nad_300cm"))
        t.index = t.index.map(nazvy)
        print(f"\ndo {nazvy[cil]}, trénovací část:\n{t.to_string()}")
    for cil in CILE:
        t = doby_pasma(cil)
        print(f"\ndo {nazvy[cil]} podle pásma průtoku v Ústí (m3/s), posun h (korelace, hodin):")
        print(t.assign(v=t.posun_h.astype(str) + " (" + t.korelace.astype(str) + ", " + t.hodin.astype(str) + ")")
              .pivot(index="stanice", columns="pasmo", values="v")[[f"od {d}" for d in PASMA]].to_string())
