"""Konvoluční síť po čase (TCN) jako tcn.py, jen seed 43 (kontrola náhody)."""
from models import tcn

PARAMETRY = tcn.PARAMETRY | dict(seed=43)


def fit(X, y, cil, horizont):
    return tcn.fit(X, y, cil, horizont, seed=PARAMETRY["seed"])
