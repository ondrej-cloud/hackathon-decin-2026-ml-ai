"""Týmový Ridge na vyhlazených průtocích stanic pod vodními díly: průměr za posledních 6 h (t − 5 … t), znovu naučený
(nejistota_dan/KMITANI.md). Ostatní vstupy beze změny. Průtoky bere z hodinové tabulky data.nacti() podle času řádku."""
from functools import cache

from data import nacti
from features import ZPOZDENI_Q
from models import ridge

POD_DILY = ("praha", "vranany", "melnik", "louny")  # Vltavská kaskáda, soutok s Vltavou, Nechranice
PARAMETRY = ridge.PARAMETRY | dict(vyhlazeni_vstupu_h=6, stanice=POD_DILY)


@cache
def _vyhlazene():
    D = nacti()
    return {s: D[f"{s}_Q"].rolling(6, min_periods=1).mean() for s in POD_DILY}  # okno t − 5 … t, jen minulé hodnoty


def vstupy(X):
    X = X.copy()
    for s, q in _vyhlazene().items():
        for z in ZPOZDENI_Q:
            X[f"{s}_Q_{z}"] = q.shift(z).reindex(X.index).to_numpy()
    return X


def fit(X, y, cil, horizont):
    predict = ridge.fit(vstupy(X), y, cil, horizont)
    return lambda X: predict(vstupy(X))
