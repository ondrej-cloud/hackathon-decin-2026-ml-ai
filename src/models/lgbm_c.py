"""LightGBM c: jako a, navíc roční období (sin a cos dne v roce) a trend stavu za posledních 6 h, bez srážek."""
import numpy as np
from lightgbm import LGBMRegressor

from models import lgbm_a

PARAMETRY = lgbm_a.PARAMETRY


def vstupy(X, cil, horizont):
    V = lgbm_a.vstupy(X, cil, horizont)
    den = 2 * np.pi * X.index.dayofyear / 365.25
    V["sezona_sin"], V["sezona_cos"] = np.sin(den), np.cos(den)
    V["trend_6h"] = X[f"{cil}_H_0"] - X[f"{cil}_H_6"]
    return V


def fit(X, y, cil, horizont, parametry=PARAMETRY, monotonni=False):
    V = vstupy(X, cil, horizont)
    # víc přitékající vody proti proudu nesmí znamenat menší vzestup
    omezeni = [int(monotonni and c.endswith("_dQ")) for c in V.columns]
    m = LGBMRegressor(**parametry, monotone_constraints=omezeni).fit(V, y - X[f"{cil}_H_0"])
    return lambda X: X[f"{cil}_H_0"] + m.predict(vstupy(X, cil, horizont))
