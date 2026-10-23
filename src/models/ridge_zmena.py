"""Ridge, cíl je změna hladiny (y − hladina teď), k předpovědi se hladina teď přičte zpět."""
from models import ridge

PARAMETRY = ridge.PARAMETRY | dict(cil="změna hladiny")


def fit(X, y, cil, horizont):
    return ridge.fit(X, y, cil, horizont, zmena=True)
