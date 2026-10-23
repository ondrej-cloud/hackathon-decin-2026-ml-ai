"""Polynomická regrese 2. stupně bez součinů: k 98 vstupům (průtoky pod odmocninou) jejich druhé mocniny, škálování, Ridge(alpha=1)."""
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

from models import ridge

PARAMETRY = ridge.PARAMETRY | dict(polynom="druhé mocniny všech vstupů")


def s_mocninami(X):
    X = ridge.odmocnina_prutoku(X)
    return pd.concat([X, (X ** 2).add_suffix("^2")], axis=1)


def fit(X, y, cil, horizont):
    model = make_pipeline(FunctionTransformer(s_mocninami), StandardScaler(), Ridge(alpha=PARAMETRY["alpha"])).fit(X, y)
    return model.predict
