"""Ridge jako ridge.py, hodiny s hladinou teď nad 1. stupněm povodňové aktivity mají při tréninku váhu 20."""
from models import ridge_vahy

PARAMETRY = ridge_vahy.PARAMETRY | dict(vaha=20.0)


def fit(X, y, cil, horizont):
    return ridge_vahy.fit(X, y, cil, horizont, vaha=PARAMETRY["vaha"])
