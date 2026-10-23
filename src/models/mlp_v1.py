"""První verze sítě (MLP 64-32, alpha=0,0001), přeučovala se."""
from models import mlp

PARAMETRY = mlp.PARAMETRY | dict(vrstvy=(64, 32), alpha=1e-4)


def fit(X, y, cil, horizont):
    return mlp.fit(X, y, cil, horizont, vrstvy=(64, 32), alpha=1e-4)
