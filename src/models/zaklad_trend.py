"""Lineární trend: stav se bude dál měnit stejně rychle jako za posledních 6 h."""

PARAMETRY = {"okno_h": 6}


def fit(X, y, cil, horizont):
    k = PARAMETRY["okno_h"]
    return lambda X: X[f"{cil}_H_0"] + (X[f"{cil}_H_0"] - X[f"{cil}_H_{k}"]) * horizont / k
