"""LightGBM (týmový lgbm = lgbm_c) beze změny a + nové stanice.

Nové stanice dostanou totéž co týmové v lgbm_a.vstupy: průtok, který do cíle doteče za horizont, a jeho rozdíl proti
průtoku, který do cíle dotéká teď. Doba doběhu stejnou metodou jako src/doba_dobehu.py (posun 0–48 h s největší
korelací změn průtoku za 6 h na trénovací části), jen nad vlastní tabulkou; jen stanice nad cílem.
"""
from functools import cache

import pandas as pd
from lightgbm import LGBMRegressor

import data_ridge
from evaluate import casti
from models import lgbm_a, lgbm_c
from spolecne import NOVE, POD_USTIM

ZMENA_H, MAX_POSUN = 6, 48


@cache
def doby(cil):
    """Doba doběhu do cíle (h) pro všechny stanice z vlastní tabulky, na trénovací části (casti(cil, 0))."""
    T = data_ridge.nacti()
    dQ = T.filter(like="_Q").diff(ZMENA_H)
    ok = (casti(cil, 0) == "train").reindex(T.index, fill_value=False)
    c = dQ[f"{cil}_Q"].where(ok)
    stanice = ([] if cil == "usti" else ["usti"]) + list(lgbm_a.DOBA[cil]) + NOVE
    return {s: int(pd.Series({k: c.corr(dQ[f"{s}_Q"].shift(k)) for k in range(MAX_POSUN + 1)}).idxmax())
            for s in dict.fromkeys(stanice)}


def nove_nad(cil):
    return [s for s in NOVE if not (cil == "usti" and s in POD_USTIM)]


def vstupy(X, cil, horizont):
    V = lgbm_c.vstupy(X, cil, horizont)
    d = doby(cil)
    for s in nove_nad(cil):
        za_h = X[f"{s}_Q_{lgbm_a.nejblizsi(max(d[s] - horizont, 0))}"]
        V[f"{s}_Q"] = za_h
        V[f"{s}_dQ"] = za_h - X[f"{s}_Q_{lgbm_a.nejblizsi(d[s])}"]
    return V


def fit_tym(seed):
    return lambda X, y, cil, horizont: lgbm_c.fit(X, y, cil, horizont, parametry=lgbm_c.PARAMETRY | dict(random_state=seed))


def fit_stanice(seed):
    def fit(X, y, cil, horizont):
        m = LGBMRegressor(**lgbm_c.PARAMETRY | dict(random_state=seed)).fit(vstupy(X, cil, horizont), y - X[f"{cil}_H_0"])
        return lambda X: X[f"{cil}_H_0"] + m.predict(vstupy(X, cil, horizont))
    return fit
