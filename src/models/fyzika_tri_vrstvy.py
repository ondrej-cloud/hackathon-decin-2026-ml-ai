"""Fyzikální model se třemi vrstvami stanic proti proudu (navíc Beroun, Sázava, Přelouč), aby na 36 h víc vody bylo změřené."""
from models import fyzika

PARAMETRY = fyzika.PARAMETRY | {"vrstev": 3}


def fit(X, y, cil, horizont):
    return fyzika.fit(X, y, cil, horizont, PARAMETRY)
