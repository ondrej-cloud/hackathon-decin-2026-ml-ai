"""G3 = ½ Ridge 30 + ½ LightGBM 30 (pevně); G4 = w·Ridge 30 + (1 − w)·LightGBM 30, w z mřížky podle chyby na ostatních
21 oknech z jejich LOFO předpovědí – jen PŘIBLIŽNĚ vnořené (LightGBM pro fold j viděl povodeň k). Zadání G pro Codex,
dopočteno zde, protože LOFO předpovědi LightGBM doběhly až po konci Codexu."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import lofo as L  # noqa: E402
from pokus_G5 import nacti_oof  # noqa: E402

if __name__ == "__main__":
    X, y, T = L.zaklad(24)
    pov = L.povodne_lofo(24)
    p12, p30, g30 = (nacti_oof(f"oof/{n}.parquet") for n in ("ridge_12", "ridge_30", "lgbm_30"))
    yo = [y[p["okno"]].to_numpy() for p in pov]
    assert all(len(a) == len(b) for a, b in zip(g30, yo))
    mrizka = np.round(np.arange(0, 1.01, 0.1), 1)
    G4, vahy = [], []
    for k in range(len(pov)):
        chyby = [np.mean([np.abs(w * p30[j] + (1 - w) * g30[j] - yo[j]).mean() for j in range(len(pov)) if j != k]) for w in mrizka]
        w = float(mrizka[int(np.argmin(chyby))])
        vahy.append(w)
        G4.append(w * p30[k] + (1 - w) * g30[k])
    out = []
    for n, pr in (("lgbm_30", g30), ("G3_pul_ridge30_lgbm30", [0.5 * a + 0.5 * b for a, b in zip(p30, g30)]),
                  ("G4_vaha_priblizne_vnorena", G4)):
        s = L.skore(pr, 24, p12)
        out.append(dict(nazev=n, **s) | ({"vahy_ridge30": vahy} if n.startswith("G4") else {}))
        print(n, {k: v for k, v in s.items() if k != "po_povodnich"}, flush=True)
    print("váhy Ridge 30 po foldech:", vahy)
    Path(__file__).with_name("vysledky_G34.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
