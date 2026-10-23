"""Neuronová síť (MLP 64-32) se silnější regularizací alpha=1 proti přeučení."""
from models import mlp

PARAMETRY = mlp.PARAMETRY | dict(vrstvy=(64, 32), alpha=1.0)


def fit(X, y, cil, horizont):
    return mlp.fit(X, y, cil, horizont, vrstvy=(64, 32), alpha=1.0)
