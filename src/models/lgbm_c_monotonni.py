"""LightGBM c s monotónním omezením: víc přitékající vody proti proudu nesmí znamenat menší vzestup."""
from models import lgbm_c

PARAMETRY = lgbm_c.PARAMETRY | dict(monotonni="_dQ +1")


def fit(X, y, cil, horizont):
    return lgbm_c.fit(X, y, cil, horizont, lgbm_c.PARAMETRY, monotonni=True)
