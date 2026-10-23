"""Bude jako teď: stav za h hodin je stejný jako stav teď. Základ, se kterým se všechno srovnává."""


def fit(X, y, cil, horizont):
    return lambda X: X[f"{cil}_H_0"]
