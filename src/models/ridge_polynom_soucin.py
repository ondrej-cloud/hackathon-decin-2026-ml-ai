"""Polynomická regrese 2. stupně jen na aktuálních hodnotách: k 98 vstupům druhé mocniny a součiny 14 hodnot z času t (105 sloupců), Ridge(alpha=1)."""
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

from models import ridge

PARAMETRY = ridge.PARAMETRY | dict(polynom="druhé mocniny a součiny 14 aktuálních hodnot")


def se_soucinem(X):
    X = ridge.odmocnina_prutoku(X)
    ted = [c for c in X if c.endswith("_0")]
    S = {f"{a}*{b}": X[a] * X[b] for i, a in enumerate(ted) for b in ted[i:]}
    return pd.concat([X, pd.DataFrame(S, index=X.index)], axis=1)


def fit(X, y, cil, horizont):
    model = make_pipeline(FunctionTransformer(se_soucinem), StandardScaler(), Ridge(alpha=PARAMETRY["alpha"])).fit(X, y)
    return model.predict
