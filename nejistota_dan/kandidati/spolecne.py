"""Společný základ pro srovnání „beze změny“ vs „+ 18 nových stanic“ u všech čtyř týmových modelů.

Týmové vstupy beze změny (src/features.py nad Ondrovou tabulkou), k nim se podle času UTC připojí průtoky 18 nových
stanic z vlastní tabulky (ridge_dan/tabulka/labe_ridge.parquet) se stejnými zpožděními jako ostatní průtoky.
Rozdělení a metriky jsou týmové (src/evaluate.py). Obě varianty se hodnotí na stejných řádcích.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("OPENBLAS_NUM_THREADS", "4")

ZDE = Path(__file__).resolve().parent
RIDGE_DAN = ZDE  # kopie: pomocné moduly leží vedle
sys.path[:0] = [str(ZDE.parents[1] / "src"), str(ZDE)]

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import data_ridge  # noqa: E402
import hodnoceni as Hd  # noqa: E402
from evaluate import casti, povodne, vyhodnot  # noqa: E402
from features import ZPOZDENI_Q, tabulka  # noqa: E402
from stanice import HYDRO, TYM  # noqa: E402

NOVE = [k for k, _ in HYDRO.values() if k not in TYM]
assert len(NOVE) == 18
# Ploučnice a Bílina se vlévají pod Ústím, do Ústí z nich nic neteče (týmové Ridge a síť ale dávají všechny stanice
# oběma cílům, i Děčín Ústí; u nich se nové přidávají taky všechny, u modelů s dobou doběhu jen ty nad cílem)
POD_USTIM = ["benesov_pl", "struznice", "ceska_lipa", "trmice"]
VSE = [(c, h) for c in ("decin", "usti") for h in (12, 24, 36)]


def nove_sloupce():
    T = data_ridge.nacti()
    return pd.DataFrame({f"{s}_Q_{z}": T[f"{s}_Q"].shift(z) for s in NOVE for z in ZPOZDENI_Q})


def data(cil, horizont):
    """X (týmových 98 sloupců), Xn (98 + 126 nových), y, c; všechno na STEJNÝCH řádcích."""
    X, y = tabulka(cil, horizont)
    N = nove_sloupce().reindex(X.index)
    ok = N.notna().all(axis=1)
    X, y, N = X[ok], y[ok], N[ok]
    c = casti(cil, horizont).reindex(X.index)
    return X, pd.concat([X, N], axis=1), y, c


def val_metriky(y, pred, cil, horizont, H=None):
    """Týmové metriky (vyhodnot) a pro Děčín navíc vzestup, začátek vzestupu, klid a 1. SPA (hodnoceni.metriky)."""
    pred = pd.Series(np.asarray(pred, dtype=float), index=y.index)
    m = vyhodnot(y, pred, cil, horizont)
    if H is not None:
        m = Hd.metriky(y, pred, H, cil, horizont)
    return m


def cv_predikce(fit, X, y, c, cil, horizont):
    """Časová CV v tréninku (bloky let s mezerou 10 dní, hodnoceni.bloky_cv): předpovědi pro tréninkové řádky."""
    tr = c == "train"
    Xt, yt = X[tr], y[tr]
    pred = pd.Series(np.nan, index=yt.index)
    for _, f_tr, f_drz in Hd.bloky_cv(Xt.index):
        predict = fit(Xt[f_tr], yt[f_tr], cil, horizont)
        pred[f_drz] = np.asarray(predict(Xt[f_drz]), dtype=float)
    return yt, pred


def cv_skore(yt, pred, Xt_ted):
    """Stejná čísla jako ridge_dan/pokus.py: průměr přes povodně nad 400 cm (okno 7 dní před až 5 po vrcholu),
    velké povodně nad 490 cm, rychlé stoupání; navíc přestřelení v oknech povodní (pred − y): průměr největších
    přestřelení jednotlivých povodní, 95. percentil přes všechny hodiny oken a největší přestřelení vůbec."""
    e = (pred - yt).abs().to_numpy()
    rozdil = (pred - yt).to_numpy()
    ud, velke, prestrel, v_oknech = {}, [], [], []
    for _, _, f_drz in Hd.bloky_cv(yt.index):
        yy = yt[f_drz]
        for v in povodne(yy, 400):
            pos = np.flatnonzero(np.asarray(f_drz) & (yt.index >= v - Hd.E.PRED) & (yt.index <= v + Hd.E.PO))
            ud[f"{v:%Y-%m-%d}"] = e[pos].mean()
            prestrel.append(rozdil[pos].max())
            v_oknech.append(rozdil[pos])
            if yt.to_numpy()[pos].max() >= 490:
                velke.append(e[pos].mean())
    vz = ((yt - Xt_ted) >= 50).to_numpy()
    return dict(cv_povodne=float(np.mean(list(ud.values()))), cv_velke=float(np.mean(velke)),
                cv_vzestup=float(e[vz].mean()), cv_bias_vzestup=float(rozdil[vz].mean()), cv_mae=float(e.mean()),
                cv_prumer_max_prestreleni=float(np.mean(prestrel)),
                cv_p95_prestreleni=float(np.percentile(np.concatenate(v_oknech), 95)),
                cv_max_prestreleni=float(np.max(prestrel)), cv_udalosti={k: round(float(v), 2) for k, v in ud.items()})


def povoden_2006(y, pred, H):
    """Jarní povodeň 2006 (tání) v Děčíně: chyba v okně, chyba na stoupání a největší přestřelení na stoupání."""
    pred = pd.Series(np.asarray(pred, dtype=float), index=y.index)
    v = povodne(y, 490)[0]
    assert f"{v:%Y-%m}" == "2006-04", v
    okno = (y.index >= v - Hd.E.PRED) & (y.index <= v + Hd.E.PO)
    stoupa = okno & (y.index < v - pd.Timedelta(hours=24))
    d = (pred - y)
    return dict(mae_2006=round(float(d[okno].abs().mean()), 1), mae_2006_stoupani=round(float(d[stoupa].abs().mean()), 1),
                max_prestreleni_2006=round(float(d[stoupa].max()), 1), bias_2006=round(float(d[okno].mean()), 1))
