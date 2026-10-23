"""LightGBM a: změna stavu, jen stav v cíli a průtoky proti proudu posunuté o dobu doběhu."""
from lightgbm import LGBMRegressor

from features import ZPOZDENI_H, ZPOZDENI_Q

PARAMETRY = dict(n_estimators=500, learning_rate=0.05, num_leaves=31, random_state=42, num_threads=4, verbose=-1)

# doba doběhu v hodinách, spočítaná na trénovací části (src/doba_dobehu.py)
DOBA = {
    "decin": dict(usti=4, louny=16, melnik=13, vranany=13, kostelec=10, praha=17, nymburk=10, jizera=18,
                  beroun=23, sazava=25, prelouc=18),
    "usti": dict(louny=13, melnik=9, vranany=9, kostelec=6, praha=13, nymburk=6, jizera=14, beroun=19,
                 sazava=21, prelouc=13),
}


def nejblizsi(z):
    return min(ZPOZDENI_Q, key=lambda x: abs(x - z))


def vstupy(X, cil, horizont):
    """Ke každé stanici průtok, který do cíle doteče za horizont (když ještě nedotekl ani do stanice, poslední
    známý), a o kolik se liší od průtoku, který do cíle dotéká teď."""
    V = X[[f"{cil}_H_{z}" for z in ZPOZDENI_H]].copy()
    for s, doba in DOBA[cil].items():
        za_h = X[f"{s}_Q_{nejblizsi(max(doba - horizont, 0))}"]
        V[f"{s}_Q"] = za_h
        V[f"{s}_dQ"] = za_h - X[f"{s}_Q_{nejblizsi(doba)}"]
    return V


def fit(X, y, cil, horizont):
    m = LGBMRegressor(**PARAMETRY).fit(vstupy(X, cil, horizont), y - X[f"{cil}_H_0"])
    return lambda X: X[f"{cil}_H_0"] + m.predict(vstupy(X, cil, horizont))
