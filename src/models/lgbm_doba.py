"""LightGBM c s dobou doběhu podle pásma průtoku v Ústí v čase předpovědi (vlna se s průtokem zrychlí nebo zpomalí)."""
import numpy as np
from lightgbm import LGBMRegressor

from doba_dobehu import pasmo
from features import ZPOZDENI_H
from models import lgbm_c, ridge
from models.lgbm_a import nejblizsi

PARAMETRY = lgbm_c.PARAMETRY | dict(doba="podle pásma průtoku v Ústí 0–300 / 300–800 / 800–1500 / nad 1500 m3/s")

# doba doběhu v h pro pásma průtoku v Ústí, src/doba_dobehu.py na trénovací části. Pásmo s korelací pod 0,2 nebo
# s méně než 1000 hodinami má hodnotu ze sousedního pásma (nad 1500 m3/s je v tréninku jen povodeň 2013, 227 h).
DOBA = {
    "decin": dict(usti=(5, 3, 3, 3), louny=(16, 16, 17, 17), melnik=(13, 12, 13, 13), vranany=(13, 13, 12, 12),
                  kostelec=(10, 10, 6, 6), praha=(18, 17, 17, 17), nymburk=(7, 7, 11, 11), jizera=(16, 16, 21, 21),
                  beroun=(22, 22, 20, 20), sazava=(9, 9, 22, 22), prelouc=(16, 16, 18, 18)),
    "usti": dict(louny=(12, 12, 15, 15), melnik=(8, 8, 10, 10), vranany=(9, 9, 9, 9), kostelec=(6, 6, 1, 1),
                 praha=(13, 13, 14, 14), nymburk=(2, 2, 7, 7), jizera=(13, 13, 19, 19), beroun=(19, 19, 18, 18),
                 sazava=(2, 2, 19, 19), prelouc=(12, 12, 16, 16)),
}


def vstupy(X, cil, horizont, doba=DOBA, odmocnina=False):
    """Jako lgbm_c.vstupy, jen doba doběhu každé stanice se vybere podle pásma průtoku v Ústí teď.
    odmocnina: průtoky pod odmocninou ještě před rozdílem (pro Ridge)."""
    p = pasmo(X["usti_Q_0"].to_numpy())
    if odmocnina:
        X = ridge.odmocnina_prutoku(X)
    V = X[[f"{cil}_H_{z}" for z in ZPOZDENI_H]].copy()
    for s, doby in doba[cil].items():
        V[f"{s}_Q"] = np.choose(p, [X[f"{s}_Q_{nejblizsi(max(d - horizont, 0))}"] for d in doby])
        V[f"{s}_dQ"] = V[f"{s}_Q"] - np.choose(p, [X[f"{s}_Q_{nejblizsi(d)}"] for d in doby])
    den = 2 * np.pi * X.index.dayofyear / 365.25
    V["sezona_sin"], V["sezona_cos"] = np.sin(den), np.cos(den)
    V["trend_6h"] = X[f"{cil}_H_0"] - X[f"{cil}_H_6"]
    return V


def fit(X, y, cil, horizont):
    m = LGBMRegressor(**lgbm_c.PARAMETRY).fit(vstupy(X, cil, horizont), y - X[f"{cil}_H_0"])
    return lambda X: X[f"{cil}_H_0"] + m.predict(vstupy(X, cil, horizont))
