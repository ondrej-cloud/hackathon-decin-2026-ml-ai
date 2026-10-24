"""Kontrola přísně vnořeného pásma (jen Ridge a Ridge 30, ze součtů).

python prisne.py      vysledky/prisne_vnorene.csv

V overeni.py se kvantily pro povodeň k berou z chyb povodní j mimo blok k, jenže ty chyby počítal model foldu j, který
trénoval i na povodni k. Přísně: chyby povodně j z modelu bez mezer celého bloku k i bez mezery j. Když pokrytí
a šířka vyjdou skoro stejně, je obyčejné vnoření v overeni.py v pořádku i pro LightGBM, kde by přísná verze stála
462 fitů na kombinaci.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("OPENBLAS_NUM_THREADS", "4")
ZDE = Path(__file__).resolve().parent
sys.path[:0] = [str(ZDE.parent / "src"), str(ZDE), str(ZDE / "kandidati")]

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import nejistota_dan as N  # noqa: E402
import oof as F  # noqa: E402
import overeni as O  # noqa: E402
from models import ridge  # noqa: E402


def prisne_meze(nazev, cil, h, varianta, uroven):
    X, y = F.radky(cil, h)
    pov = F.foldy(X.index, h)
    if nazev == "ridge30":
        import ridge30
        X = ridge30.pridej_stanice(X)
    A = ridge.odmocnina_prutoku(X).to_numpy(dtype=np.float64)
    yv = y.to_numpy(dtype=np.float64)
    h0, h6 = X[f"{cil}_H_0"].to_numpy(), X[f"{cil}_H_6"].to_numpy()
    vse = F.soucty(A, yv)
    D = O.nacti(nazev, cil, h)  # obyčejné LOFO předpovědi: na nich se hodnotí povodeň k
    bl = O.bloky(h)
    dolni, horni = np.empty(len(D)), np.empty(len(D))
    for k, pk in enumerate(pov):
        e, s = [], []
        mezery_bloku = np.logical_or.reduce([p["mezera"] for i, p in enumerate(pov) if bl[i] == bl[k]])
        for j, pj in enumerate(pov):
            if bl[j] == bl[k]:
                continue
            ven = mezery_bloku | pj["mezera"]
            m = F.ridge_ze_souctu([a - b for a, b in zip(vse, F.soucty(A[ven], yv[ven]))], ridge.PARAMETRY["alpha"])
            o = pj["okno"]
            pr = m(A[o])
            e.append(yv[o] - pr)
            s.append(N.skupina(varianta, cil, h, pr, h0[o], h6[o]))
        kv = N.kvantily_skupin(np.concatenate(e), np.concatenate(s), uroven)
        r = (D.fold == k).to_numpy()
        dolni[r], horni[r] = N.meze(D.pred.to_numpy()[r], N.skupina(varianta, cil, h, D.pred[r], D.h0[r], D.h6[r]), kv)
    return D, dolni, horni


if __name__ == "__main__":
    import json
    varianta = json.loads(N.KVANTILY.read_text(encoding="utf-8"))["varianta"] if N.KVANTILY.exists() else "zmena6"
    radky = []
    for nazev in ("ridge", "ridge30"):
        for cil, h in O.KOMBINACE:
            for u in N.UROVNE:
                D, d, hh = prisne_meze(nazev, cil, h, varianta, u)
                d0, h0_, _ = O.vnorene(D, varianta, cil, h, u)
                for druh, (a, b) in (("prisne", (d, hh)), ("obycejne", (d0, h0_))):
                    uv, sirka, skore = O.hodnoceni(D, a, b, u)
                    skut, zac = O.skutecny_vyvoj(D, h)
                    radky.append(dict(model=nazev, cil=cil, horizont=h, uroven=u, vnoreni=druh, pokryti=uv.mean(),
                                      sirka=sirka.mean(), skore=skore.mean(),
                                      pokryti_rychly_vzestup=uv[skut == "rychly_vzestup"].mean()))
            print(nazev, cil, h, flush=True)
    R = pd.DataFrame(radky)
    R.round(4).to_csv(ZDE / "vysledky/prisne_vnorene.csv", index=False, encoding="utf-8")
    print(R.groupby(["uroven", "vnoreni"])[["pokryti", "sirka", "skore", "pokryti_rychly_vzestup"]].mean().round(3))
