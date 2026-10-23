"""Ridge se vstupy z lgbm_doba: průtoky pod odmocninou posunuté o dobu doběhu podle pásma průtoku v Ústí."""
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from models import lgbm_doba

PARAMETRY = dict(alpha=1.0, odmocnina="průtoky, před rozdílem", cil="hladina", doba="podle pásma průtoku v Ústí")


def fit(X, y, cil, horizont, doba=lgbm_doba.DOBA):
    def vstupy(X):
        return lgbm_doba.vstupy(X, cil, horizont, doba, odmocnina=True)
    m = make_pipeline(StandardScaler(), Ridge(alpha=PARAMETRY["alpha"])).fit(vstupy(X), y)
    return lambda X: m.predict(vstupy(X))
