"""Předpověď pro aplikaci.

Zatím FALEŠNÁ: jednoduchá pravidla místo modelu, ať aplikace funguje,
než bude hotový skutečný model. Ten nahradí funkci predikuj() se stejným
rozhraním a vrátí ukazka=False.
"""


def predikuj(spotreba_kwh: float) -> dict:
    """Bere roční spotřebu v kWh (číslo >= 0).

    Vrací slovník:
        kategorie  – co předpověď říká (krátký text)
        vysvetleni – jedna věta pro laika, proč to tak vyšlo
        ukazka     – True, dokud jde o falešnou předpověď
    """
    if spotreba_kwh < 0:
        raise ValueError("Spotřeba nemůže být záporná.")

    if spotreba_kwh < 2000:
        kategorie = "nízká spotřeba"
        vysvetleni = "Spotřeba je pod 2 000 kWh za rok, to odpovídá malému bytu."
    elif spotreba_kwh < 5000:
        kategorie = "běžná spotřeba"
        vysvetleni = "Spotřeba je mezi 2 000 a 5 000 kWh za rok, to je běžná domácnost."
    else:
        kategorie = "vysoká spotřeba"
        vysvetleni = "Spotřeba je nad 5 000 kWh za rok, to odpovídá velkému domu nebo firmě."

    return {"kategorie": kategorie, "vysvetleni": vysvetleni, "ukazka": True}
