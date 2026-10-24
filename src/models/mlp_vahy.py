"""Neuronová síť (MLP 128-64, alpha=1), hodiny nad 1. stupněm povodňové aktivity mají při tréninku váhu 5."""
from models import mlp

PARAMETRY = mlp.PARAMETRY | dict(vaha_povodni=5.0)


def fit(X, y, cil, horizont):
    return mlp.fit(X, y, cil, horizont, vaha_povodni=5.0)
