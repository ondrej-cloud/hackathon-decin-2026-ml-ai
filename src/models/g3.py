"""G3: průměr Ridge s 30 stanicemi a LightGBM s 30 stanicemi, pevná váha ½ + ½ (ridge_dan/ZLEPSENI.md).

Ridge 30 = models/ridge30.py. LightGBM 30 = týmový lgbm (lgbm_c: změna stavu, průtoky posunuté o dobu doběhu,
sezónnost, trend 6 h, stejné parametry, seed 42) + nové stanice nad cílem stejným postupem
(ridge_dan/stanice_vsem/lgbm_stanice.py; doba doběhu nových stanic se odhaduje jen z hodin, na kterých se model učí,
v přísné podobě: rozdíly i posuny v korelaci jen uvnitř tréninku).
Ploučnice a Bílina se vlévají pod Ústím, LightGBM je proto dostává jen pro Děčín, Ridge 30 pro oba cíle.
"""
import numpy as np

from models import ridge30

PARAMETRY = dict(vaha_ridge30=0.5, vaha_lgbm30=0.5, seed_lgbm=42)
VAHA_RIDGE = 0.5


def fit(X, y, cil, horizont):
    from lgbm_stanice import fit_stanice
    p_ridge = ridge30.fit(X, y, cil, horizont)
    p_lgbm = fit_stanice(42, prisne=True)(ridge30.pridej_stanice(X), y, cil, horizont)

    def predict(X):
        a = np.asarray(p_ridge(X), dtype=float)
        b = np.asarray(p_lgbm(ridge30.pridej_stanice(X)), dtype=float)
        return VAHA_RIDGE * a + (1 - VAHA_RIDGE) * b

    return predict
