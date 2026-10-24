"""Kmitání předpovědi při nízké vodě: týmový Ridge proti předem daným variantám (PRUBEH.md, so 05:22):
(a) vyhlazení výstupu (průměr předpovědí z t, t − 1 h, t − 2 h), (b) vyhlazení průtoků pod vodními díly (průměr za
posledních 6 h, model znovu naučený), (c) obojí. Varianty jsou src/models/ridge_kmit_*.py (Ondrova validace je bere
jako moduly), tady se jen hodnotí.

python kmitani.py     kmitani/lofo.csv, kmitani/klid.csv, kmitani/provoz.csv

- LOFO 22 povodní (foldy jako oof.py, Ridge ze součtů): chyba na povodních, začátek vzestupu, zpoždění vrcholu
  (o kolik hodin později než skutečný vrchol má vrchol předpověď, podle času platnosti), varování 2. a 3. SPA.
- Klid: model z trénovací části 2006–2018, validace 2019–2020: chyba a směrodatná odchylka hodinové změny předpovědi
  proti skutečnosti.
- Provoz: provozní data ČHMÚ 24. 9.–23. 10. 2026 (denní soubory z cache ridge worktree, jen čtení; tabulka stejně jako
  ridge_dan/provoz/zivy_beh.py, kopie v kmitani/zivy_beh_kopie.py), stejný model: kmitání a chyba.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("OPENBLAS_NUM_THREADS", "4")
ZDE = Path(__file__).resolve().parent
sys.path[:0] = [str(ZDE.parent / "src"), str(ZDE), str(ZDE / "kandidati"), str(ZDE / "kmitani")]

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import oof as F  # noqa: E402
from data import SPA  # noqa: E402
from evaluate import casti, varovani  # noqa: E402
from features import tabulka  # noqa: E402
from models import ridge, ridge_kmit_vstup, ridge_kmit_vystup  # noqa: E402

VARIANTY = {"tym": (False, False), "a_vystup": (True, False), "b_vstup": (False, True), "c_oboji": (True, True)}
# (d) přidané až po výsledcích (a)–(c), jen pravidlo zobrazení: vyhlazená předpověď (a) jen když je hladina teď i surová
# předpověď pod 1. stupněm, jinak surová; varování (2. a 3. stupeň) se tak z konstrukce nezmění


def zobrazeni(surova, vyhlazena, h0, cil):
    prah = SPA[cil][0]
    return np.where((np.asarray(h0) < prah) & (np.asarray(surova) < prah), vyhlazena, surova)
KOMBINACE = [(c, h) for c in ("decin", "usti") for h in (12, 24, 36)]
VYSL = ZDE / "kmitani"
RECENT = Path("C:/Users/danie/Documents/hackathon-2026-ridge/ridge_dan/cache/hydrology/recent/data")


def matice(X, vstup):
    return ridge.odmocnina_prutoku(ridge_kmit_vstup.vstupy(X) if vstup else X).to_numpy(dtype=np.float64)


def lofo(cil, h):
    X, y = F.radky(cil, h)
    pov = F.foldy(X.index, h)
    yv = y.to_numpy()
    radky, Ds = [], {}
    for nazev, (vystup, vstup) in VARIANTY.items():
        A = matice(X, vstup)
        vse = F.soucty(A, yv)
        cele = []
        for k, p in enumerate(pov):
            m = F.ridge_ze_souctu([a - b for a, b in zip(vse, F.soucty(A[p["mezera"]], yv[p["mezera"]]))],
                                  ridge.PARAMETRY["alpha"])
            idx = np.flatnonzero(p["okno"])
            ext = np.arange(max(idx[0] - 2, 0), idx[-1] + 1)  # o 2 h dřív kvůli průměru předpovědí
            pr = m(A[ext])
            if vystup:
                pr = ridge_kmit_vystup.vyhlad(pr, X.index[ext])
            pr = pd.Series(pr, index=X.index[ext]).reindex(X.index[idx]).to_numpy()
            cele.append(pd.DataFrame({"fold": k, "cas": X.index[idx], "y": yv[idx], "pred": pr,
                                      "h0": X[f"{cil}_H_0"].to_numpy()[idx], "h6": X[f"{cil}_H_6"].to_numpy()[idx]}))
        Ds[nazev] = pd.concat(cele, ignore_index=True)
    Ds["d_zobrazeni"] = Ds["tym"].assign(pred=zobrazeni(Ds["tym"].pred, Ds["a_vystup"].pred, Ds["tym"].h0, cil))
    for nazev, D in Ds.items():
        e = (D.pred - D.y).abs()
        zac = ((D.y - D.h0) >= 50) & ((D.h0 - D.h6) < 10)
        zpozdeni = [(g.cas.iloc[int(g.pred.to_numpy().argmax())] - g.cas.iloc[int(g.y.to_numpy().argmax())])
                    / pd.Timedelta(hours=1) for _, g in D.groupby("fold")]
        r = dict(cil=cil, horizont=h, varianta=nazev, lofo=e.groupby(D.fold).mean().mean(), zacatek=e[zac].mean(),
                 zpozdeni_vrcholu_h=float(np.mean(zpozdeni)), zpozdeni_vrcholu_median_h=float(np.median(zpozdeni)))
        # varování na spojené řadě oken (řádek ve dvou oknech: první výskyt)
        S = D.drop_duplicates("cas").set_index("cas").sort_index()
        for n, prah in zip((2, 3), SPA[cil][1:]):
            v = varovani(S.y, S.pred, prah, h)
            r |= {f"spa{n}_predstih_h": v["predstih_h"], f"spa{n}_propasnuto": v["propasnuto"],
                  f"spa{n}_plane": v["plane_poplachy"]}
        r["po_povodnich"] = e.groupby(D.fold).mean().round(2).tolist()
        radky.append(r)
    return radky


def klid(cil, h):
    X, y = tabulka(cil, h)
    c = casti(cil, h).reindex(X.index)
    tr, va = (c == "train").to_numpy(), (c == "val").to_numpy()
    yv = y.to_numpy()
    klidne = va & (X.index >= pd.Timestamp("2019-01-01", tz="UTC"))
    radky, P = [], {}
    for nazev, (vystup, vstup) in VARIANTY.items():
        A = matice(X, vstup)
        m = F.ridge_ze_souctu(F.soucty(A[tr], yv[tr]), ridge.PARAMETRY["alpha"])
        pr = m(A[klidne])
        if vystup:
            pr = ridge_kmit_vystup.vyhlad(pr, X.index[klidne])
        P[nazev] = pr
    P["d_zobrazeni"] = zobrazeni(P["tym"], P["a_vystup"], X.loc[klidne, f"{cil}_H_0"], cil)
    for nazev, pr in P.items():
        radky.append(dict(cil=cil, horizont=h, varianta=nazev, **kmitani(pd.Series(pr, index=X.index[klidne]),
                                                                         pd.Series(yv[klidne], index=X.index[klidne]))))
    return radky


def kmitani(pred, skut):
    """Chyba a směrodatná odchylka hodinové změny předpovědi a skutečnosti (jen dvojice sousedních hodin)."""
    po_sobe = pred.index.to_series().diff() == pd.Timedelta(hours=1)
    dp, dy = pred.diff()[po_sobe], skut.diff()[po_sobe]
    return dict(mae=float((pred - skut).abs().mean()), sd_zmeny_predpovedi=float(dp.std()),
                sd_zmeny_skutecnosti=float(dy.std()), prumerna_abs_zmena_predpovedi=float(dp.abs().mean()), n=len(pred))


def provoz():
    import zivy_beh_kopie as Z
    Z.RECENT = RECENT
    T, _ = Z.provozni_tabulka()
    T, _ = Z.doplnit(T)
    Tb = T.copy()
    for s in ridge_kmit_vstup.POD_DILY:  # stejné vyhlazení jako ridge_kmit_vstup, jen z provozní tabulky
        Tb[f"{s}_Q"] = T[f"{s}_Q"].rolling(6, min_periods=1).mean()
    radky = []
    for cil, h in KOMBINACE:
        Xt, yt = tabulka(cil, h)
        tr = (casti(cil, h).reindex(Xt.index) == "train").to_numpy()
        yv = yt.to_numpy()
        skut = T[f"{cil}_H"].shift(-h)
        # stejné řádky pro všechny varianty: úplné vstupy z provozní tabulky i z vyhlazené
        ok = (Z.tym_vstupy(T).notna().all(axis=1) & Z.tym_vstupy(Tb).notna().all(axis=1)).to_numpy()
        Ps = {}
        for nazev, (vystup, vstup) in VARIANTY.items():
            m = F.ridge_ze_souctu(F.soucty(matice(Xt, vstup)[tr], yv[tr]), ridge.PARAMETRY["alpha"])
            Xp = Z.tym_vstupy(Tb if vstup else T)[list(Xt.columns)]
            pr = m(ridge.odmocnina_prutoku(Xp[ok]).to_numpy(dtype=np.float64))
            if vystup:
                pr = ridge_kmit_vystup.vyhlad(pr, Xp.index[ok])
            Ps[nazev] = pd.Series(pr, index=Xp.index[ok])
        Ps["d_zobrazeni"] = pd.Series(zobrazeni(Ps["tym"], Ps["a_vystup"], T[f"{cil}_H"].reindex(Ps["tym"].index), cil),
                                      index=Ps["tym"].index)
        for nazev, P in Ps.items():
            s = skut.reindex(P.index)
            j = s.notna()
            radky.append(dict(cil=cil, horizont=h, varianta=nazev, od=str(P.index.min()), do=str(P.index.max()),
                              **kmitani(P[j], s[j])))
    return radky


if __name__ == "__main__":
    VYSL.mkdir(exist_ok=True)
    L = pd.DataFrame([r for cil, h in KOMBINACE for r in lofo(cil, h)])
    L.round(3).to_csv(VYSL / "lofo.csv", index=False, encoding="utf-8")
    print(L.drop(columns="po_povodnich").round(2).to_string(index=False), flush=True)
    K = pd.DataFrame([r for cil, h in KOMBINACE for r in klid(cil, h)])
    K.round(3).to_csv(VYSL / "klid.csv", index=False, encoding="utf-8")
    print(K.round(2).to_string(index=False), flush=True)
    P = pd.DataFrame(provoz())
    P.round(3).to_csv(VYSL / "provoz.csv", index=False, encoding="utf-8")
    print(P.round(2).to_string(index=False), flush=True)
