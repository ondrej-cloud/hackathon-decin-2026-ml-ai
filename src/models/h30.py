"""H30 (průzkumný): Ridge s 30 stanicemi (models/ridge30.py) + ukazatel útlumu vlny v nivě, alpha 1.

Ukazatel = průtok po proudu − součet přítoků nad ním (m³/s, bez odmocniny) pro úseky Kostelec − (Nymburk + Jizera),
Mělník − (Vraňany + Kostelec) a Ústí − (Mělník + Louny), zpoždění 0/6/12/24 h, z týmových vstupů (jen minulost).
Záporný = voda se drží v nivě (povodeň 2006). Předem zapsané v ridge_dan/PRUBEH.md (23:37 a 01:53), bez ladění,
podrobnosti ridge_dan/ZLEPSENI.md (pokus H).
"""
import pandas as pd

from models import ridge, ridge30

USEKY = {"polabi": ("kostelec", ["nymburk", "jizera"]), "melnik": ("melnik", ["vranany", "kostelec"]),
         "usti": ("usti", ["melnik", "louny"])}
ZPOZDENI = (0, 6, 12, 24)
PARAMETRY = ridge.PARAMETRY | dict(stanice="30", utlum="3 úseky × 0/6/12/24 h")


def s_utlumem(X):
    U = pd.DataFrame({f"utlum_{u}_{z}": X[f"{d}_Q_{z}"] - sum(X[f"{n}_Q_{z}"] for n in nad)
                      for u, (d, nad) in USEKY.items() for z in ZPOZDENI}, index=X.index)
    return pd.concat([X, U], axis=1)


def fit(X, y, cil, horizont, nove_stanice=True):
    pridej = (lambda X: s_utlumem(ridge30.pridej_stanice(X))) if nove_stanice else s_utlumem
    predict = ridge.fit(pridej(X), y, cil, horizont)
    return lambda X: predict(pridej(X))
