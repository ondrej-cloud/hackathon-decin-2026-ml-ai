"""Týmový Ridge, předpověď vyhlazená: průměr předpovědí vydaných v t, t − 1 h a t − 2 h (jen minulé, nejistota_dan/KMITANI.md)."""
import pandas as pd

from models import ridge

PARAMETRY = ridge.PARAMETRY | dict(vyhlazeni_vystupu_h=3)


def vyhlad(pred, index):
    """Klouzavý průměr za poslední 3 hodiny podle času vydání (okno (t − 3 h, t]); chybí-li hodiny, průměr z dostupných."""
    return pd.Series(pred, index=index).sort_index().rolling("3h").mean().reindex(index).to_numpy()


def fit(X, y, cil, horizont):
    predict = ridge.fit(X, y, cil, horizont)
    return lambda X: vyhlad(predict(X), X.index)
