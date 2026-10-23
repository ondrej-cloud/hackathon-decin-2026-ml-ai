"""LightGBM c, v listu stromu aspoň 200 hodin, aby si strom nezapamatoval jednu povodeň z tréninku."""
from models import lgbm_c

PARAMETRY = lgbm_c.PARAMETRY | dict(min_child_samples=200)


def fit(X, y, cil, horizont):
    return lgbm_c.fit(X, y, cil, horizont, PARAMETRY)
