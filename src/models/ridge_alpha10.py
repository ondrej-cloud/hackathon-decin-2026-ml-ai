"""Ridge, alpha 10: silnější regularizace než v1."""
from models import ridge

PARAMETRY = ridge.PARAMETRY | dict(alpha=10.0)


def fit(X, y, cil, horizont):
    return ridge.fit(X, y, cil, horizont, alpha=PARAMETRY["alpha"])
