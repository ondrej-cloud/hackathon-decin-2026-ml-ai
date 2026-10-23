"""Ridge, alpha 100: velmi silná regularizace."""
from models import ridge

PARAMETRY = ridge.PARAMETRY | dict(alpha=100.0)


def fit(X, y, cil, horizont):
    return ridge.fit(X, y, cil, horizont, alpha=PARAMETRY["alpha"])
