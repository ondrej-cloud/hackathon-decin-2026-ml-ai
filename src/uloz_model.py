"""Uloží modely Ridge pro aplikaci: models/ridge_<cil>_<h>.joblib, objekt s metodou predict(X).

python src/uloz_model.py    trénuje na trénovací části (stejně jako porovnej.py) a uloží 6 souborů
"""
from pathlib import Path

import joblib

from evaluate import casti
from features import tabulka
from models import ridge

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / "models"

if __name__ == "__main__":
    MODELS.mkdir(exist_ok=True)
    for cil in ("decin", "usti"):
        for h in (12, 24, 36):
            X, y = tabulka(cil, h)
            tr = casti(cil, h).reindex(X.index) == "train"
            model = ridge.pipeline(ridge.PARAMETRY["alpha"]).fit(X[tr], y[tr])
            soubor = MODELS / f"ridge_{cil}_{h}.joblib"
            joblib.dump(model, soubor)
            print(f"{soubor.relative_to(ROOT)}: {soubor.stat().st_size / 1e3:.0f} kB, "
                  f"poslední řádek {X.index[-1]:%Y-%m-%d %H:%M} → {model.predict(X.tail(1))[0]:.0f} cm")
