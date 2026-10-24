"""Kontrola přísně vnořeného pásma (jen Ridge a Ridge 30, ze součtů).

python prisne.py      vysledky/prisne_vnorene.csv

V overeni.py se kvantily pro povodeň k berou z chyb povodní j mimo blok k, jenže ty chyby počítal model foldu j, který
trénoval i na povodni k, a hodnocená předpověď povodně k je z modelu bez její vlastní mezery (ne celého bloku).
Přísně: chyby povodně j z modelu bez mezer celého bloku k i bez mezery j, hodnocená předpověď z modelu bez celého
bloku k. Když to vyjde skoro stejně, naznačuje to, že obyčejné vnoření nepřikrašluje; pro LightGBM (G3) by přísná
verze stála 462 fitů na kombinaci a ověřená není.

Druhá část (kontrola_aplikace_prisne): model aplikace (Ridge učený na trénovací části 2006–2018) a kalibrace jen
z 18 tréninkových povodní z modelů učených na trénovací části bez mezery té povodně, tedy nic z kalibrace ani z modelu
validaci (4 povodně a 2019–2020) nevidělo. Hodnotí se na celé validaci.
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
    D = O.nacti(nazev, cil, h).copy()  # řádky a pořadí oken jako obyčejné LOFO
    bl = O.bloky(h)
    dolni, horni = np.empty(len(D)), np.empty(len(D))
    for k, pk in enumerate(pov):
        e, s = [], []
        mezery_bloku = np.logical_or.reduce([p["mezera"] for i, p in enumerate(pov) if bl[i] == bl[k]])
        # hodnocená předpověď povodně k z modelu bez celého bloku k
        mk = F.ridge_ze_souctu([a - b for a, b in zip(vse, F.soucty(A[mezery_bloku], yv[mezery_bloku]))],
                               ridge.PARAMETRY["alpha"])
        r = (D.fold == k).to_numpy()
        assert r.sum() == pk["okno"].sum()
        D.loc[r, "pred"] = mk(A[pk["okno"]])
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
        dolni[r], horni[r] = N.meze(D.pred.to_numpy()[r], N.skupina(varianta, cil, h, D.pred[r], D.h0[r], D.h6[r]), kv)
    return D, dolni, horni


def kontrola_aplikace_prisne(varianta):
    from evaluate import casti
    from features import tabulka
    radky = []
    for cil, h in O.KOMBINACE:
        X, y = tabulka(cil, h)
        c = casti(cil, h).reindex(X.index)
        tr, va = (c == "train").to_numpy(), (c == "val").to_numpy()
        A = ridge.odmocnina_prutoku(X).to_numpy(dtype=np.float64)
        yv = y.to_numpy(dtype=np.float64)
        h0, h6 = X[f"{cil}_H_0"].to_numpy(), X[f"{cil}_H_6"].to_numpy()
        S_tr = F.soucty(A[tr], yv[tr])
        app = F.ridge_ze_souctu(S_tr, ridge.PARAMETRY["alpha"])  # = models/ridge_<cil>_<h>.joblib (app/predikce.py)
        e, s, kal_povodni = [], [], 0
        for p in F.foldy(X.index, h):
            okno = p["okno"] & tr
            if okno.sum() < 0.9 * p["okno"].sum():
                continue  # validační povodně a jejich okolí: do kalibrace ne
            ven = tr & p["mezera"]
            m = F.ridge_ze_souctu([a - b for a, b in zip(S_tr, F.soucty(A[ven], yv[ven]))], ridge.PARAMETRY["alpha"])
            pr = m(A[okno])
            e.append(yv[okno] - pr)
            s.append(N.skupina(varianta, cil, h, pr, h0[okno], h6[okno]))
            kal_povodni += 1
        e, s = np.concatenate(e), np.concatenate(s)
        pred = app(A[va])
        sk = N.skupina(varianta, cil, h, pred, h0[va], h6[va])
        cas = X.index[va]
        povoden = (cas < pd.Timestamp("2019-01-01", tz="UTC"))  # 4 validační povodně 2006–2011, zbytek klid 2019–2020
        for u in N.UROVNE:
            d, hh = N.meze(pred, sk, N.kvantily_skupin(e, s, u))
            uv = (yv[va] >= d) & (yv[va] <= hh)
            radky.append(dict(cil=cil, horizont=h, uroven=u, kalibracnich_povodni=kal_povodni,
                              pokryti_povodne=uv[povoden].mean(), sirka_povodne=(hh - d)[povoden].mean(),
                              pokryti_klid_2019_2020=uv[~povoden].mean(), sirka_klid=(hh - d)[~povoden].mean()))
        print("aplikace přísně", cil, h, flush=True)
    return pd.DataFrame(radky)


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
    K = kontrola_aplikace_prisne(varianta)
    K.round(4).to_csv(ZDE / "vysledky/kontrola_aplikace_prisne.csv", index=False, encoding="utf-8")
    print(K.round(3).to_string(index=False))
