"""Uloží Ridge 30 stanic pro horizont 36 h: models/ridge30_<cil>_36.joblib (joblib s predict(X), jako src/uloz_model.py).

python ridge_dan/uloz_ridge30.py    trénuje na všech řádcích 2006–2025 (test je spotřebovaný, finální model se učí
na všem), pro Děčín i Ústí. X = 98 týmových vstupů z features.tabulka(cil, 36); nové stanice si model připojí sám
z ridge_dan/tabulka/labe_ridge.parquet. Soubory nejsou v Gitu (models/*.joblib je v .gitignore).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import joblib  # noqa: E402
import numpy as np  # noqa: E402

from features import tabulka  # noqa: E402
from models import ridge30  # noqa: E402

if __name__ == "__main__":
    (ROOT / "models").mkdir(exist_ok=True)
    for cil in ("decin", "usti"):
        X, y = tabulka(cil, 36)
        m = ridge30.Model().fit(X, y)
        soubor = ROOT / "models" / f"ridge30_{cil}_36.joblib"
        joblib.dump(m, soubor)
        p = m.predict(X.tail(48))
        assert np.isfinite(p).all() and len(p) == 48
        print(f"{soubor.relative_to(ROOT)}: {soubor.stat().st_size / 1e3:.0f} kB, trénink {X.index[0]:%Y-%m-%d} až "
              f"{X.index[-1]:%Y-%m-%d %H:%M} UTC ({len(X)} řádků), poslední předpověď {p[-1]:.0f} cm")
