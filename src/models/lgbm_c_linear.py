"""LightGBM c s přímkou v každém listu (linear_tree), aby uměl pokračovat i za to, co viděl v tréninku."""
from models import lgbm_c

PARAMETRY = lgbm_c.PARAMETRY | dict(linear_tree=True)


def fit(X, y, cil, horizont):
    return lgbm_c.fit(X, y, cil, horizont, PARAMETRY)
