"""LightGBM c s menšími stromy (7 listů místo 31), aby si nepamatoval vzácné kombinace z několika povodní v tréninku."""
from models import lgbm_c

PARAMETRY = lgbm_c.PARAMETRY | dict(num_leaves=7)


def fit(X, y, cil, horizont):
    return lgbm_c.fit(X, y, cil, horizont, PARAMETRY)
