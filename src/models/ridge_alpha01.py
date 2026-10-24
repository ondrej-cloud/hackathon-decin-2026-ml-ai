"""Ridge, alpha 0,1: slabší regularizace než v1."""
from models import ridge

PARAMETRY = ridge.PARAMETRY | dict(alpha=0.1)


def fit(X, y, cil, horizont):
    return ridge.fit(X, y, cil, horizont, alpha=PARAMETRY["alpha"])
