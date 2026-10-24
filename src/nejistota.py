"""Odhad nejistoty předpovědi Ridge: rozptyl chyb na tréninku podle pásma hladiny teď, pokrytí ověřené na validaci.

python src/nejistota.py    uloží models/ridge_intervaly.json (5. a 95. percentil chyby pro každé pásmo)
                           a vypíše, kolik skutečných hodnot se do intervalu vešlo na validaci a na povodních
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from data import CILE
from evaluate import PO, PRED, SPA, casti, povodne
from features import tabulka
from models import ridge

ROOT = Path(__file__).resolve().parents[1]
SOUBOR = ROOT / "models/ridge_intervaly.json"
PASMA = [0, 300, 450, 600, 10_000]  # hranice pásem hladiny teď (cm): klid, zvýšená, kolem 1.–2. stupně, nad 3.
KVANTILY = (0.05, 0.95)


def pasmo(hladina):
    return pd.cut(hladina, PASMA, labels=[f"{a}-{b}" for a, b in zip(PASMA[:-1], PASMA[1:])])


def intervaly(cil, horizont):
    X, y = tabulka(cil, horizont)
    c = casti(cil, horizont).reindex(X.index)
    tr, va = c == "train", c == "val"
    model = ridge.pipeline(ridge.PARAMETRY["alpha"]).fit(X[tr], y[tr])
    e_tr = y[tr] - model.predict(X[tr])
    q = e_tr.groupby(pasmo(X.loc[tr, f"{cil}_H_0"]), observed=False).quantile(KVANTILY).unstack()
    q.columns = ["dolni", "horni"]
    # pokrytí na validaci: skutečnost uvnitř [předpověď + dolní, předpověď + horní]
    pred = pd.Series(model.predict(X[va]), index=X.index[va])
    p = pasmo(X.loc[va, f"{cil}_H_0"]).astype(str)
    dolni, horni = pred + q.dolni.reindex(p).to_numpy(), pred + q.horni.reindex(p).to_numpy()
    uvnitr = (y[va] >= dolni) & (y[va] <= horni)
    okno = pd.Series(False, index=y[va].index)
    for v in povodne(y[va], SPA[cil][1]):
        okno[v - PRED: v + PO] = True
    return q, dict(pokryti_val=round(float(uvnitr.mean()), 3), pokryti_povodne=round(float(uvnitr[okno].mean()), 3),
                   sirka_povodne_cm=round(float((horni - dolni)[okno].mean())), radku_povodne=int(okno.sum()))


if __name__ == "__main__":
    out = {}
    for cil in CILE:
        for h in (12, 24, 36):
            q, k = intervaly(cil, h)
            out[f"{cil}_{h}"] = dict(pasma=PASMA, dolni=[round(float(v)) for v in q.dolni],
                                     horni=[round(float(v)) for v in q.horni], **k)
            print(f"{cil} +{h} h: dolní {out[f'{cil}_{h}']['dolni']}, horní {out[f'{cil}_{h}']['horni']} cm; "
                  f"pokrytí validace {k['pokryti_val']:.0%}, na povodních {k['pokryti_povodne']:.0%}, "
                  f"šířka na povodních {k['sirka_povodne_cm']} cm")
    SOUBOR.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"uloženo {SOUBOR.relative_to(ROOT)}")
