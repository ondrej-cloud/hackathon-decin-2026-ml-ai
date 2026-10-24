"""Fyzikální model jen s branami a jednou vrstvou stanic nad nimi (Praha, Nymburk, Jizera), první verze."""
from models import fyzika

PARAMETRY = fyzika.PARAMETRY | {"vrstev": 2}


def fit(X, y, cil, horizont):
    return fyzika.fit(X, y, cil, horizont, PARAMETRY)
