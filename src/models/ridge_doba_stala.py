"""Ridge se stejnými vstupy jako ridge_doba, ale se stálou dobou doběhu. Kontrola, co přinese samotné pásmo průtoku."""
from models import ridge_doba
from models.lgbm_a import DOBA

STALA = {cil: {s: (d,) * 4 for s, d in doby.items()} for cil, doby in DOBA.items()}
PARAMETRY = ridge_doba.PARAMETRY | dict(doba="stálá, jako lgbm_a")


def fit(X, y, cil, horizont):
    return ridge_doba.fit(X, y, cil, horizont, STALA)
