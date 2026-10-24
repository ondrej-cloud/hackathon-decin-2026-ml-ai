"""H12 (průzkumný): týmový Ridge (12 stanic) + ukazatel útlumu vlny v nivě (models/h30.py), alpha 1, bez ladění."""
from models import h30

PARAMETRY = h30.PARAMETRY | dict(stanice="12")


def fit(X, y, cil, horizont):
    return h30.fit(X, y, cil, horizont, nove_stanice=False)
