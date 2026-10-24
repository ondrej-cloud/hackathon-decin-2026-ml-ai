"""LightGBM c na zbytku po Ridge: Ridge dá základ změny stavu, stromy jen opravují, co Ridge nezvládne."""
from lightgbm import LGBMRegressor

from models import lgbm_c, zaklad_ridge

PARAMETRY = lgbm_c.PARAMETRY | dict(zaklad="zaklad_ridge")


def fit(X, y, cil, horizont):
    ridge = zaklad_ridge.fit(X, y, cil, horizont)
    m = LGBMRegressor(**lgbm_c.PARAMETRY).fit(lgbm_c.vstupy(X, cil, horizont), y - ridge(X))
    return lambda X: ridge(X) + m.predict(lgbm_c.vstupy(X, cil, horizont))
