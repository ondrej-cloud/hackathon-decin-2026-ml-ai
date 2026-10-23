"""LightGBM v2: cíl je změna stavu proti teď, všech 98 vstupů bez úprav."""
from lightgbm import LGBMRegressor

PARAMETRY = dict(n_estimators=500, learning_rate=0.05, num_leaves=31, random_state=42, num_threads=4, verbose=-1)


def fit(X, y, cil, horizont):
    m = LGBMRegressor(**PARAMETRY).fit(X, y - X[f"{cil}_H_0"])
    return lambda X: X[f"{cil}_H_0"] + m.predict(X)
