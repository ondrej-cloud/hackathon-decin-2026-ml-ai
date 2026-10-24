"""Týmový Ridge s vyhlazenými průtoky pod vodními díly (ridge_kmit_vstup) a vyhlazenou předpovědí (ridge_kmit_vystup)."""
from models import ridge_kmit_vstup, ridge_kmit_vystup

PARAMETRY = ridge_kmit_vstup.PARAMETRY | ridge_kmit_vystup.PARAMETRY


def fit(X, y, cil, horizont):
    predict = ridge_kmit_vstup.fit(X, y, cil, horizont)
    return lambda X: ridge_kmit_vystup.vyhlad(predict(X), X.index)
