"""Vstupy a cíl pro předpověď stavu v Děčíně nebo v Ústí za `horizont` hodin. Stejné pro všechny modely.

Řádek je okamžik t, kdy předpověď vydáváme (index, UTC). Sloupce:
- decin_H_<z>, usti_H_<z>: stav v cm před z hodinami
- <stanice>_Q_<z>: průtok v m3/s před z hodinami, všech 12 stanic (seznam v data.py)
y je stav v cm v čase t + horizont. Ve vstupech je jen to, co je v čase t už změřené.
"""
import pandas as pd

from data import CILE, PROTI_PROUDU, nacti

ZPOZDENI_H = (0, 1, 2, 3, 6, 12, 24)
ZPOZDENI_Q = (0, 3, 6, 12, 18, 24, 36)
NEJSTARSI = max(ZPOZDENI_H + ZPOZDENI_Q)


def tabulka(cil, horizont):
    D = nacti()
    X = pd.DataFrame(
        {f"{s}_H_{z}": D[f"{s}_H"].shift(z) for s in CILE for z in ZPOZDENI_H}
        | {f"{s}_Q_{z}": D[f"{s}_Q"].shift(z) for s in CILE | PROTI_PROUDU for z in ZPOZDENI_Q}
    )
    y = D[f"{cil}_H"].shift(-horizont).rename("y")
    ok = X.notna().all(axis=1) & y.notna()
    return X[ok], y[ok]
