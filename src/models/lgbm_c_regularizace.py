"""LightGBM c se silnější regularizací: 15 listů, L2 10 a každý strom vidí jen 70 % vstupů."""
from models import lgbm_c

PARAMETRY = lgbm_c.PARAMETRY | dict(num_leaves=15, reg_lambda=10, colsample_bytree=0.7)


def fit(X, y, cil, horizont):
    return lgbm_c.fit(X, y, cil, horizont, PARAMETRY)
