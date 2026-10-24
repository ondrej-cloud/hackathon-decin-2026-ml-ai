"""Ridge s 30 stanicemi: týmový Ridge (odmocnina průtoků, škálování, alpha 1) + průtoky 18 nových stanic ČHMÚ.

Nové stanice mají stejná zpoždění jako ostatní průtoky (0/3/6/12/18/24/36 h) a připojují se podle času UTC
z ridge_dan/tabulka/labe_ridge.parquet (postaví ridge_dan/data_ridge.py, není v Gitu), pro Děčín i Ústí stejně.
Posuny jsou jen do minulosti, v řádku t jsou průtoky změřené nejpozději v t. Podrobnosti ridge_dan/STANICE_VSEM.md.
"""
import sys
from functools import cache
from pathlib import Path

import pandas as pd

from models import ridge

_RIDGE_DAN = Path(__file__).resolve().parents[2] / "ridge_dan"
for _p in (_RIDGE_DAN, _RIDGE_DAN / "stanice_vsem"):
    if str(_p) not in sys.path:
        sys.path.append(str(_p))

PARAMETRY = ridge.PARAMETRY | dict(stanice="30 (12 týmových + 18 nových)")


@cache
def _nove():
    from spolecne import nove_sloupce
    return nove_sloupce()


def pridej_stanice(X):
    """K týmovým vstupům připojí průtoky 18 nových stanic ve stejných časech (index X = čas vydání t)."""
    N = _nove().reindex(X.index)
    assert N.notna().all().all(), "nové stanice nemají hodnotu pro některý řádek"
    return pd.concat([X, N], axis=1)


def fit(X, y, cil, horizont):
    predict = ridge.fit(pridej_stanice(X), y, cil, horizont)
    return lambda X: predict(pridej_stanice(X))


class Model:
    """Uložitelná podoba pro aplikaci (jako src/uloz_model.py): predict(X) z 98 týmových vstupů ze features.tabulka,
    nové stanice si připojí sám. Potřebuje ridge_dan/tabulka/labe_ridge.parquet s řádky pro časy v X."""

    def __init__(self, alpha=ridge.PARAMETRY["alpha"]):
        self.alpha = alpha

    def fit(self, X, y):
        self.m = ridge.pipeline(self.alpha).fit(pridej_stanice(X), y)
        return self

    def predict(self, X):
        return self.m.predict(pridej_stanice(X))
