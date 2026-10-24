"""LightGBM v1: cíl je stav, všech 98 vstupů bez úprav."""
from lightgbm import LGBMRegressor

PARAMETRY = dict(n_estimators=500, learning_rate=0.05, num_leaves=31, random_state=42, num_threads=4, verbose=-1)


def fit(X, y, cil, horizont):
    return LGBMRegressor(**PARAMETRY).fit(X, y).predict
