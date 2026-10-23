"""Finální Ridge pro Děčín +24 h a jeho uložení pro aplikaci.

python model_ridge.py    natrénuje na trénovací části (2006–2018 bez val povodní, stejně jako uloz_model.py)
                         a uloží modely/ridge_dan_decin_24.joblib (není v Gitu)

Objekt má predict(X) jako týmové modely, jen X jsou jeho vlastní sloupce (RidgeDecin24.sloupce, 224), které
postaví priznaky.priznaky(T, "decin", 24, **FINALNI) z hodinové tabulky T ve formátu data_ridge (průtoky 30 stanic
a stavy Děčína a Ústí). Pohodlnější je predikuj(T): vrátí předpověď stavu za 24 h pro každou hodinu tabulky.
"""
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

import hodnoceni as Hd
from priznaky import priznaky

ZDE = Path(__file__).resolve().parent
SOUBOR = ZDE / "modely/ridge_dan_decin_24.joblib"

# vybráno časovou CV v tréninku (POKUSY_RIDGE.md, pokus b_vse): všech 30 stanic se zpožděními jako v týmu,
# odmocnina průtoků; alpha 1 = největší alpha do 0,01 cm od nejlepší v CV (0,01 / 0,1 / 1 vycházejí stejně)
FINALNI = dict(stanice="vse")
ALPHA = 1.0


class RidgeDecin24:
    """StandardScaler + Ridge na odmocninách průtoků a stavech; predict(X) vrací stav Děčína v cm za 24 h."""

    def __init__(self, volby=FINALNI, alpha=ALPHA):
        self.volby, self.alpha = volby, alpha

    def fit(self, X, y):
        from sklearn.linear_model import Ridge
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
        self.sloupce = list(X.columns)
        self.m = make_pipeline(StandardScaler(), Ridge(alpha=self.alpha)).fit(X, y)
        return self

    def predict(self, X):
        return self.m.predict(X[self.sloupce])

    def predikuj(self, T):
        """T = hodinová tabulka (index UTC). Vrátí Series: čas vydání → předpověď stavu v čase vydání + 24 h."""
        X, _, _ = priznaky(T, "decin", 24, bez_cile=True, **self.volby)
        return pd.Series(self.predict(X), index=X.index, name="decin_H_za_24h")

    def vahy(self):
        """Váha každého vstupu v cm na jednu směrodatnou odchylku (jako docs/grafy/ridge_vahy_decin.png)."""
        return pd.Series(self.m.named_steps["ridge"].coef_, index=self.sloupce)


def trenink(T, finalni=False):
    """finalni=False: trénink 2006–2018 bez val povodní; True: vše do konce 2020 (jako porovnej.py --test)."""
    X, y, L = priznaky(T, "decin", 24, **FINALNI)
    c = Hd.casti(T["decin_H"], 24, max(L, 36), finalni=finalni).reindex(X.index)
    return RidgeDecin24().fit(X[c == "train"], y[c == "train"]), X, y, c


if __name__ == "__main__":
    import data_ridge
    import model_ridge  # ať se třída uloží jako model_ridge.RidgeDecin24, ne __main__.RidgeDecin24
    T = data_ridge.nacti()
    m, X, y, c = model_ridge.trenink(T)
    SOUBOR.parent.mkdir(exist_ok=True)
    joblib.dump(m, SOUBOR)
    p = m.predict(X.tail(1))[0]
    print(f"{SOUBOR.relative_to(ZDE)}: {SOUBOR.stat().st_size / 1e3:.0f} kB, {len(m.sloupce)} vstupů, "
          f"poslední řádek {X.index[-1]:%Y-%m-%d %H:%M} UTC → {p:.0f} cm za 24 h")
    print("největší váhy:", m.vahy().abs().sort_values().tail(8).round(1).to_dict())
    assert np.isfinite(m.predict(X)).all()
