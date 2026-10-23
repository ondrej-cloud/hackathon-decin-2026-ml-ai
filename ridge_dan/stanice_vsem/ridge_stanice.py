"""Ridge: týmový model (src/models/ridge.py) beze změny a rozpad 2 × 2: odmocnina průtoků ano/ne × 12/30 stanic.

Týmový Ridge odmocninu průtoků už má, takže „beze změny“ = odmocnina + 12 stanic. Varianta bez odmocniny je
stejná pipeline bez prvního kroku (StandardScaler + Ridge(alpha 1)).
"""
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from models import ridge


def fit_odmocnina(X, y, cil, horizont):
    return ridge.fit(X, y, cil, horizont)


def fit_bez_odmocniny(X, y, cil, horizont):
    m = make_pipeline(StandardScaler(), Ridge(alpha=ridge.PARAMETRY["alpha"])).fit(X, y)
    return lambda X: m.predict(X)


VARIANTY = {  # název: (fit, nové stanice ano/ne)
    "ridge_bez_odmocniny_12": (fit_bez_odmocniny, False),
    "ridge_12": (fit_odmocnina, False),  # = týmový Ridge
    "ridge_bez_odmocniny_30": (fit_bez_odmocniny, True),
    "ridge_30": (fit_odmocnina, True),
}
