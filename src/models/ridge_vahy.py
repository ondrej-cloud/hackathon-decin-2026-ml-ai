"""Ridge jako ridge.py, hodiny s hladinou teď nad 1. stupněm povodňové aktivity mají při tréninku váhu 5."""
from data import SPA
from models import ridge

PARAMETRY = ridge.PARAMETRY | dict(vaha=5.0, vaha_od="hladina teď nad 1. SPA")


def fit(X, y, cil, horizont, vaha=PARAMETRY["vaha"]):
    """Hodin nad 1. stupněm je v tréninku jen asi 2 %, váha je zvýrazní. Škálování se váhami neřídí, jen Ridge."""
    w = (X[f"{cil}_H_0"] >= SPA[cil][0]).map({True: vaha, False: 1.0})
    model = ridge.pipeline(ridge.PARAMETRY["alpha"]).fit(X, y, ridge__sample_weight=w.to_numpy())
    return model.predict
