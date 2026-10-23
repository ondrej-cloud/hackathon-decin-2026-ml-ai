"""G2 znovu, s opravou z kontroly Codexu (h): vnitřní okna povodní j bez hodin v mezeře vnějšího foldu k.

w·Ridge 30 + (1 − w)·Ridge 12, w z mřížky 0; 0,1; …; 1 striktně vnořeně (vnitřní modely bez mezer k i j,
hodnocení jen na m.okno_vnitrni(k, j)). Původní G2 od Codexu (smesi/experiment_G.py) bral celé okno j.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import lofo as L  # noqa: E402

if __name__ == "__main__":
    L.cekej_na_ram(1200)
    A12, y = L.matice(24)
    A30, _ = L.matice(24, nove=L.NOVE)
    m12, m30 = L.Motor(A12.to_numpy(), y, 24), L.Motor(A30.to_numpy(), y, 24)
    p12, _ = m12.lofo()
    p30, _ = m30.lofo()
    mrizka = np.round(np.arange(0, 1.01, 0.1), 1)
    pred, vahy = [], {}
    for k, pk in enumerate(m12.pov):
        vnitrni = []
        for j in range(len(m12.pov)):
            if j == k:
                continue
            a12, yo = m12.okno_vnitrni(k, j)
            if len(yo) == 0:
                continue
            a30, _ = m30.okno_vnitrni(k, j)
            v12 = L.predikuj(L.ridge_z_souctu(m12.vnitrni(k, j)), a12)
            v30 = L.predikuj(L.ridge_z_souctu(m30.vnitrni(k, j)), a30)
            vnitrni.append((v12, v30, yo))
        chyby = [np.mean([np.abs(w * b + (1 - w) * a - c).mean() for a, b, c in vnitrni]) for w in mrizka]
        w = float(mrizka[int(np.argmin(chyby))])
        vahy[pk["nazev"]] = w
        pred.append(w * p30[k] + (1 - w) * p12[k])
    s = L.skore(pred, 24, p12)
    out = [dict(nazev="G2_oprava", popis="w·Ridge30 + (1 − w)·Ridge12, w striktně vnořeně, vnitřní okna bez mezery k",
                **s, vahy_ridge30=vahy)]
    print({k: v for k, v in s.items() if k != "po_povodnich"}, vahy)
    Path(__file__).with_name("vysledky_G2_oprava.json").write_text(json.dumps(out, ensure_ascii=False, indent=1),
                                                                   encoding="utf-8")
