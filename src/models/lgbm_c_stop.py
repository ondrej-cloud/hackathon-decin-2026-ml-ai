"""LightGBM c se zastavením tréninku podle let 2017–2018 z trénovací části (validace se nepoužije)."""
import pandas as pd
from lightgbm import LGBMRegressor, early_stopping

from models import lgbm_c

PARAMETRY = lgbm_c.PARAMETRY | dict(zastaveni="2017–2018, 50 stromů bez zlepšení MAE")


def fit(X, y, cil, horizont):
    V, zmena = lgbm_c.vstupy(X, cil, horizont), y - X[f"{cil}_H_0"]
    stop = X.index >= pd.Timestamp("2017-01-01", tz="UTC")
    m = LGBMRegressor(**lgbm_c.PARAMETRY).fit(V[~stop], zmena[~stop], eval_set=[(V[stop], zmena[stop])],
                                              eval_metric="l1", callbacks=[early_stopping(50, verbose=False)])
    print(f"    zastaveno po {m.best_iteration_} stromech")
    return lambda X: X[f"{cil}_H_0"] + m.predict(lgbm_c.vstupy(X, cil, horizont))
