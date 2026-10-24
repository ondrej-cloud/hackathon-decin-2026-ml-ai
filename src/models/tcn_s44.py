"""Konvoluční síť po čase (TCN) jako tcn.py, jen seed 44 (kontrola náhody)."""
from models import tcn

PARAMETRY = tcn.PARAMETRY | dict(seed=44)


def fit(X, y, cil, horizont):
    return tcn.fit(X, y, cil, horizont, seed=PARAMETRY["seed"])
