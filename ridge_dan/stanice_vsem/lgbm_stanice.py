"""LightGBM (týmový lgbm = lgbm_c) beze změny a + nové stanice.

Nové stanice dostanou totéž co týmové v lgbm_a.vstupy: průtok, který do cíle doteče za horizont, a jeho rozdíl proti
průtoku, který do cíle dotéká teď. Doba doběhu stejnou metodou jako src/doba_dobehu.py (posun 0–48 h s největší
korelací změn průtoku za 6 h), jen nad vlastní tabulkou a jen stanice nad cílem. Odhaduje se uvnitř fit() z hodin,
na kterých se model učí (v CV jen z trénovací části foldu, ne z drženého bloku). Týmové doby (lgbm_a.DOBA) zůstávají
pevné jako v týmovém modelu.
"""
import numpy as np
import pandas as pd
from lightgbm import LGBMRegressor

import data_ridge
from evaluate import casti
from models import lgbm_a, lgbm_c
from spolecne import NOVE, POD_USTIM

ZMENA_H, MAX_POSUN = 6, 48


def doby(cil, hodiny=None, prisne=False):
    """Doba doběhu do cíle (h) pro stanice z vlastní tabulky. hodiny: na kterých hodinách (index), jinak celá
    trénovací část (casti(cil, 0)), to jen pro kontrolu proti týmovým lgbm_a.DOBA.
    prisne: do korelace jen dvojice, jejichž všechny zdrojové časy (t, t − 6 h, t − k, t − k − 6 h) leží v hodinách
    tréninku (kontrola Codexu i); bez toho se rozdíly a posuny počítají i přes okraje tréninku (dřívější běhy)."""
    T = data_ridge.nacti()
    dQ = T.filter(like="_Q").diff(ZMENA_H)
    ok = (casti(cil, 0) == "train").reindex(T.index, fill_value=False) if hodiny is None else T.index.isin(hodiny)
    ok = pd.Series(np.asarray(ok, dtype=bool), index=T.index)
    if prisne:
        ok &= ok.shift(ZMENA_H, fill_value=False)
    c = dQ[f"{cil}_Q"].where(ok)
    stanice = ([] if cil == "usti" else ["usti"]) + list(lgbm_a.DOBA[cil]) + NOVE

    ck = [c.where(ok.shift(k, fill_value=False) & ok.shift(k + ZMENA_H, fill_value=False)) if prisne else c
          for k in range(MAX_POSUN + 1)]

    def r(s, k):
        return ck[k].corr(dQ[f"{s}_Q"].shift(k))

    return {s: int(pd.Series({k: r(s, k) for k in range(MAX_POSUN + 1)}).idxmax()) for s in dict.fromkeys(stanice)}


def nove_nad(cil):
    return [s for s in NOVE if not (cil == "usti" and s in POD_USTIM)]


def vstupy(X, cil, horizont, d):
    V = lgbm_c.vstupy(X, cil, horizont)
    for s in nove_nad(cil):
        za_h = X[f"{s}_Q_{lgbm_a.nejblizsi(max(d[s] - horizont, 0))}"]
        V[f"{s}_Q"] = za_h
        V[f"{s}_dQ"] = za_h - X[f"{s}_Q_{lgbm_a.nejblizsi(d[s])}"]
    return V


def fit_tym(seed):
    return lambda X, y, cil, horizont: lgbm_c.fit(X, y, cil, horizont, parametry=lgbm_c.PARAMETRY | dict(random_state=seed))


def fit_stanice(seed, prisne=False):
    def fit(X, y, cil, horizont):
        d = doby(cil, X.index, prisne)
        fit.doby = d
        m = LGBMRegressor(**lgbm_c.PARAMETRY | dict(random_state=seed)).fit(vstupy(X, cil, horizont, d), y - X[f"{cil}_H_0"])
        return lambda X: X[f"{cil}_H_0"] + m.predict(vstupy(X, cil, horizont, d))
    return fit
