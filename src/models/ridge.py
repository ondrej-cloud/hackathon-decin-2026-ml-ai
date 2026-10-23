"""Lineární regrese (Ridge): odmocnina z průtoků, škálování, Ridge(alpha=1). Cíl je hladina za h hodin."""
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

PARAMETRY = dict(alpha=1.0, odmocnina="jen průtoky", cil="hladina", stanice="všechny")


def odmocnina_prutoku(X):
    """Odmocnina jen na průtoky (_Q_). Na hladině zkazila vrchol povodně 2006 o metr."""
    X = X.copy()
    q = X.columns[X.columns.str.contains("_Q_")]
    X[q] = np.sqrt(X[q])
    return X


def pipeline(alpha):
    return make_pipeline(FunctionTransformer(odmocnina_prutoku, feature_names_out="one-to-one"),
                         StandardScaler(), Ridge(alpha=alpha))


def fit(X, y, cil, horizont, alpha=PARAMETRY["alpha"], zmena=False, sloupce=None):
    """zmena: model se učí y − hladina teď a ta se k předpovědi přičte zpět. sloupce: podmnožina vstupů."""
    sloupce = list(X.columns) if sloupce is None else sloupce
    ted = f"{cil}_H_0"
    model = pipeline(alpha).fit(X[sloupce], y - X[ted] if zmena else y)
    if zmena:
        return lambda X: model.predict(X[sloupce]) + X[ted].to_numpy()
    return lambda X: model.predict(X[sloupce])
