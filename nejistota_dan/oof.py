"""LOFO předpovědi mimo trénink (22 povodní 2006–2020) jako podklad pro pásmo nejistoty.

python oof.py ridge|ridge30|lgbm30 [--cil decin usti] [--horizont 12 24 36]

- ridge = týmový finální model (src/models/ridge.py), ridge30 = Ridge s 30 stanicemi (kandidati/ridge30.py),
  lgbm30 = LightGBM s 30 stanicemi přesně jako uvnitř G3 (kandidati/g3.py: lgbm_stanice.fit_stanice(42, prisne=True)
  na vstupech ridge30.pridej_stanice). G3 = ½ ridge30 + ½ lgbm30 se skládá až z uložených předpovědí.
- Foldy kandidati/lofo_foldy.csv (Děčín, podle horizontu, stejné jako ridge_dan/zlepseni/lofo.py): fold k drží okno
  povodně k (7 dní před až 5 dní po vrcholu) a z tréninku vyřadí okno ± 20 dní. Pro Ústí stejné časy oken (tytéž
  povodně, vrchol v Ústí jen pár hodin dřív).
- Řádky jako lofo.zaklad: týmové vstupy features.tabulka(cil, h), t + h < 2021 (test se nepoužije),
  t ≥ první řádek + 72 h.
Uloží oof/<model>_<cil>_<h>.parquet: fold, cas (vydání), y, pred, h0 (stav teď), h6 (stav před 6 h).
Ridge se počítá ze součtů n, Σx, Σy, Σxxᵀ, Σxy (trénink foldu = vše − mezera), jako ridge_dan/zlepseni/lofo.py:
totéž co odmocnina průtoků + StandardScaler + Ridge(alpha 1) ze sklearn (ověřeno: rozdíl < 1e-3 cm, overeni()).
"""
import argparse
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("OPENBLAS_NUM_THREADS", "4")
ZDE = Path(__file__).resolve().parent
sys.path[:0] = [str(ZDE.parent / "src"), str(ZDE / "kandidati")]

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from evaluate import povodne  # noqa: E402
from features import tabulka  # noqa: E402
from models import ridge  # noqa: E402

FOLDY = ZDE / "kandidati/lofo_foldy.csv"
OOF = ZDE / "oof"
KONEC = pd.Timestamp("2021-01-01", tz="UTC")


def radky(cil, horizont):
    X, y = tabulka(cil, horizont)
    ok = (X.index + pd.Timedelta(hours=horizont) < KONEC) & (X.index >= X.index[0] + pd.Timedelta(hours=72))
    return X[ok], y[ok]


def foldy(index, horizont):
    F = pd.read_csv(FOLDY)
    F = F[F.horizont == horizont]
    out = []
    for _, f in F.iterrows():
        okno = (index >= pd.Timestamp(f.okno_od)) & (index <= pd.Timestamp(f.okno_do))
        mezera = (index >= pd.Timestamp(f.mezera_od)) & (index <= pd.Timestamp(f.mezera_do))
        out.append(dict(povoden=f.povoden, vrchol=pd.Timestamp(f.vrchol_cas_vydani_utc), okno=okno, mezera=mezera))
    return out


def soucty(A, y):
    return [len(y), A.sum(0), y.sum(), A.T @ A, A.T @ y]


def ridge_ze_souctu(S, alpha):
    """StandardScaler (směrodatná odchylka bez n − 1) + Ridge(alpha) s neregularizovaným absolutním členem."""
    n, sx, sy, sxx, sxy = S
    mu, ym = sx / n, sy / n
    sd = np.sqrt(np.clip(np.diag(sxx) / n - mu ** 2, 0, None))
    sd[sd == 0] = 1
    G = (sxx - n * np.outer(mu, mu)) / np.outer(sd, sd)
    b = (sxy - n * mu * ym) / sd
    k = np.linalg.solve(G + alpha * np.eye(len(mu)), b)
    return lambda A: ((A - mu) / sd) @ k + ym


def rychly_ridge(nazev, X, y, pov):
    """LOFO předpovědi týmového Ridge (nazev ridge) nebo Ridge 30 ze součtů, bez opakovaného fitu přes celá data."""
    if nazev == "ridge30":
        import ridge30
        X = ridge30.pridej_stanice(X)
    A = ridge.odmocnina_prutoku(X).to_numpy(dtype=np.float64)
    yv = y.to_numpy(dtype=np.float64)
    vse = soucty(A, yv)
    out = []
    for p in pov:
        m = soucty(A[p["mezera"]], yv[p["mezera"]])
        out.append(ridge_ze_souctu([a - b for a, b in zip(vse, m)], ridge.PARAMETRY["alpha"])(A[p["okno"]]))
    return out


def fit_modelu(nazev):
    if nazev == "ridge":
        return ridge.fit
    import ridge30
    if nazev == "ridge30":
        return ridge30.fit
    from lgbm_stanice import fit_stanice

    def fit(X, y, cil, horizont):
        p = fit_stanice(42, prisne=True)(ridge30.pridej_stanice(X), y, cil, horizont)
        return lambda X: p(ridge30.pridej_stanice(X))
    return fit


def spust(nazev, cil, horizont, sklearn=False):
    X, y = radky(cil, horizont)
    pov = foldy(X.index, horizont)
    if cil == "decin":  # vrcholy na řádcích sedí se souborem foldů
        assert [f"{v:%Y-%m-%d %H}" for v in povodne(y, 400)] == [f"{p['vrchol']:%Y-%m-%d %H}" for p in pov]
    if nazev in ("ridge", "ridge30") and not sklearn:
        predpovedi = rychly_ridge(nazev, X, y, pov)
    else:
        fit = fit_modelu(nazev)
        predpovedi = [np.asarray(fit(X[~p["mezera"]], y[~p["mezera"]], cil, horizont)(X[p["okno"]]), dtype=float)
                      for p in pov]
    casti = []
    for k, (p, pred) in enumerate(zip(pov, predpovedi)):
        o = X[p["okno"]]
        casti.append(pd.DataFrame({"fold": k, "povoden": p["povoden"], "cas": o.index, "y": y[p["okno"]].to_numpy(),
                                   "pred": pred, "h0": o[f"{cil}_H_0"].to_numpy(), "h6": o[f"{cil}_H_6"].to_numpy()}))
    D = pd.concat(casti, ignore_index=True)
    OOF.mkdir(exist_ok=True)
    D.to_parquet(OOF / f"{nazev}_{cil}_{horizont}{'_sklearn' if sklearn else ''}.parquet")
    return D


def overeni():
    """Rychlý Ridge proti sklearn (ridge.fit) na Děčíně +24 h: největší rozdíl předpovědí v cm."""
    a = pd.read_parquet(OOF / "ridge_decin_24_sklearn.parquet")
    b = spust("ridge", "decin", 24)
    return float(np.abs(a.pred.to_numpy() - b.pred.to_numpy()).max())


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("model", choices=("ridge", "ridge30", "lgbm30"))
    a.add_argument("--cil", nargs="+", default=["decin", "usti"])
    a.add_argument("--horizont", nargs="+", type=int, default=[12, 24, 36])
    a.add_argument("--overeni", action="store_true")
    a = a.parse_args()
    if a.overeni:
        print(f"rychlý Ridge proti sklearn, Děčín +24 h: největší rozdíl {overeni():.2e} cm")
        sys.exit()
    for cil in a.cil:
        for h in a.horizont:
            t = time.time()
            D = spust(a.model, cil, h)
            print(f"{a.model} {cil} +{h} h: {len(D)} řádků, {D.fold.nunique()} povodní, "
                  f"MAE {np.abs(D.pred - D.y).mean():.2f} cm ({time.time() - t:.0f} s)", flush=True)
