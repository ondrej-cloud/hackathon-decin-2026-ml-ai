"""Ridge na změnu stavu, odmocnina průtoků, alpha 1. Základ pro srovnání s LightGBM (hlavní lineární model je ridge.py)."""
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

PARAMETRY = {"alpha": 1.0, "cil": "změna stavu"}


def priprav(X):
    return X.assign(**{c: np.sqrt(X[c]) for c in X if "_Q_" in c})


def fit(X, y, cil, horizont):
    m = make_pipeline(StandardScaler(), Ridge(alpha=PARAMETRY["alpha"]))
    m.fit(priprav(X), y - X[f"{cil}_H_0"])
    return lambda X: X[f"{cil}_H_0"] + m.predict(priprav(X))
