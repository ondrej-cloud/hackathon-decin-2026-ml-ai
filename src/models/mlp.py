"""Neuronová síť (MLP 128-64, alpha=1) na změnu hladiny, odmocnina průtoků, škálované vstupy i cíl."""
import numpy as np
from sklearn.compose import TransformedTargetRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

from data import SPA

PARAMETRY = dict(vrstvy=(128, 64), alpha=1.0, early_stopping=True, max_iter=300, seed=42, cil="změna hladiny")


def odmocnina_prutoku(X):
    return X.assign(**{c: np.sqrt(X[c].clip(lower=0)) for c in X if "_Q_" in c})


def fit(X, y, cil, horizont, vrstvy=PARAMETRY["vrstvy"], alpha=PARAMETRY["alpha"], seed=PARAMETRY["seed"],
        vaha_povodni=1.0):
    sit = MLPRegressor(hidden_layer_sizes=vrstvy, alpha=alpha, early_stopping=True,
                       max_iter=PARAMETRY["max_iter"], random_state=seed)
    m = TransformedTargetRegressor(
        make_pipeline(FunctionTransformer(odmocnina_prutoku), StandardScaler(), sit),
        transformer=StandardScaler(),
    )
    # hodiny nad 1. stupněm povodňové aktivity můžou mít při tréninku větší váhu
    vahy = np.where(y >= SPA[cil][0], vaha_povodni, 1.0)
    m.fit(X, y - X[f"{cil}_H_0"], mlpregressor__sample_weight=vahy)
    return lambda X: X[f"{cil}_H_0"] + m.predict(X)
