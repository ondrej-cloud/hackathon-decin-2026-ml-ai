"""Obaly modelů pro srovnání „beze změny“ vs „+ srážky“ (šestihodinové srážky ze synoptických stanic, srazky.py).

Varianty se liší jen tím, jestli ke vstupům přibudou sloupce sr_* z data/srazky_6h.parquet (surové mm, neodmocňují se):
- ridge_tym: src/models/ridge.py (fit) na 98 týmových vstupech z features.tabulka
- ridge_dan: ridge_dan/model_ridge.py, 224 vstupů z priznaky(**FINALNI), StandardScaler + Ridge alpha 1; jen Děčín +24 h
- lgbm: src/models/lgbm.py (= lgbm_c.fit); + srážky = stejné vstupy lgbm_c.vstupy, k nim sloupce sr_*, jinak totéž
Obě varianty mají vždy stejné řádky: vyhodí se hodiny bez srážek a značky částí počítají s nejstarším srážkovým
měřením (NEJSTARSI_SR ze srazky.py). Sady: hlavni = blizko + dal (10 sloupců, verdikt), povodi = blizko + dílčí
povodí (citlivost).
"""
import hashlib
import os
import re
import sys
from functools import cache
from pathlib import Path

import numpy as np
import pandas as pd
from lightgbm import LGBMRegressor

import spolecne as S
import data_ridge
import model_ridge
from features import NEJSTARSI, tabulka
from models import lgbm_c, ridge
from priznaky import priznaky

sys.path.insert(0, str(S.ZDE))
from srazky import NEJSTARSI_SR  # noqa: E402  nejstarší srážkové měření, které příznak v hodině t použije

SRAZKY = Path(os.environ.get("SRAZKY_6H", S.ZDE / "data/srazky_6h.parquet"))
SEEDY = (42, 43, 44)
KOMBINACE = {"ridge_tym": S.VSE, "lgbm": S.VSE, "ridge_dan": [("decin", 24)]}
POVODNE_VAL = ("2006-04", "2009-03", "2010-09", "2011-01")


def vyber(sloupce, sada):
    if sada == "hlavni":
        return [c for c in sloupce if re.match(r"^sr_(blizko|dal)_", c)]
    return [c for c in sloupce if c.startswith("sr_blizko_") or re.match(r"^sr_(?!blizko|dal)", c)]


@cache
def srazky(cesta, sada):
    Sr = pd.read_parquet(cesta)
    assert str(Sr.index.tz) == "UTC", Sr.index.tz  # jinak by reindex na index tabulek dal samé NaN
    sl = vyber(Sr.columns, sada)
    assert len(sl) == 10 if sada == "hlavni" else len(sl) > 5, sl
    assert not any("_Q_" in c for c in sl)
    return Sr[sl]


def otisk(cesta):
    return hashlib.sha1(Path(cesta).read_bytes()).hexdigest()[:8]


def data(model, cil, horizont, sada="hlavni", cesta=SRAZKY, puvodni=False):
    """A (vstupy beze změny), B (+ srážky), y, c na STEJNÝCH řádcích.

    puvodni=True: řádky a značky jako dřív (bez průniku se srážkami, nejstarší zpoždění 36 h), B = None; jen na
    kontrolu, že obal dává známá čísla."""
    T = data_ridge.nacti()
    if model == "ridge_dan":
        X, y, L = priznaky(T, cil, horizont, **model_ridge.FINALNI)
    else:
        X, y = tabulka(cil, horizont)
        L = NEJSTARSI
    if puvodni:
        return X, None, y, S.Hd.casti(T[f"{cil}_H"], horizont, max(L, 36)).reindex(X.index)
    Sr = srazky(cesta, sada).reindex(X.index).astype(X.dtypes.iloc[0])
    ok = Sr.notna().all(axis=1)
    c = S.Hd.casti(T[f"{cil}_H"], horizont, max(L, 36, NEJSTARSI_SR)).reindex(X.index)
    A, B = X[ok], pd.concat([X, Sr], axis=1)[ok]
    assert A.index.equals(B.index) and not B.columns.duplicated().any()
    return A, B, y[ok], c[ok]


def fit_ridge_dan(X, y, cil, horizont):
    return model_ridge.RidgeDecin24().fit(X, y).predict


def fit_lgbm(seed):
    return lambda X, y, cil, horizont: lgbm_c.fit(X, y, cil, horizont,
                                                  parametry=lgbm_c.PARAMETRY | dict(random_state=seed))


def vstupy_lgbm(X, cil, horizont):
    """lgbm_c.vstupy a k nim srážkové sloupce, jak jsou."""
    return pd.concat([lgbm_c.vstupy(X, cil, horizont), X.filter(regex="^sr_")], axis=1)


def fit_lgbm_srazky(seed):
    # monotone_constraints jsou v lgbm_c.fit nulové, bez nich je to tentýž model
    def fit(X, y, cil, horizont):
        m = LGBMRegressor(**lgbm_c.PARAMETRY | dict(random_state=seed)).fit(vstupy_lgbm(X, cil, horizont),
                                                                            y - X[f"{cil}_H_0"])
        return lambda X: X[f"{cil}_H_0"] + m.predict(vstupy_lgbm(X, cil, horizont))
    return fit


def varianty(model, seedy=SEEDY):
    """[(varianta, seed, fit)]: "bez" = model beze změny na vstupech A, "srazky" = tentýž model na vstupech B."""
    if model == "ridge_tym":
        return [("bez", None, ridge.fit), ("srazky", None, ridge.fit)]
    if model == "ridge_dan":
        return [("bez", None, fit_ridge_dan), ("srazky", None, fit_ridge_dan)]
    if model == "lgbm":
        return [v for s in seedy for v in (("bez", s, fit_lgbm(s)), ("srazky", s, fit_lgbm_srazky(s)))]
    raise ValueError(model)


def cv_zacatek(yt, pred, H, horizont=24):
    """Začátek vzestupu v CV (definice z hodnoceni.metriky): za horizont stoupne ≥ 50 cm a posledních 6 h < 10 cm."""
    ted = H.reindex(yt.index)
    zac = ((yt - ted) >= 50) & ((ted - H.shift(6).reindex(yt.index)) < 10)
    d = (pred - yt)[zac]
    return dict(cv_zacatek=float(d.abs().mean()), cv_bias_zacatek=float(d.mean()), cv_n_zacatek=int(zac.sum()))


def povoden(y, pred, mesic):
    """Validační povodeň s vrcholem v daném měsíci: chyba a bias v okně 7 dní před až 5 po vrcholu a na stoupání
    (okno před vrcholem bez posledních 24 h, jako spolecne.povoden_2006)."""
    pred = pd.Series(np.asarray(pred, dtype=float), index=y.index)
    v = y.loc[mesic].idxmax()
    okno = (y.index >= v - S.Hd.E.PRED) & (y.index <= v + S.Hd.E.PO)
    stoupa = okno & (y.index < v - pd.Timedelta(hours=24))
    d = pred - y
    k = mesic.replace("-", "_")
    return {f"mae_{k}": round(float(d[okno].abs().mean()), 1), f"bias_{k}": round(float(d[okno].mean()), 1),
            f"mae_{k}_stoupani": round(float(d[stoupa].abs().mean()), 1),
            f"bias_{k}_stoupani": round(float(d[stoupa].mean()), 1),
            f"max_prestreleni_{k}": round(float(d[stoupa].max()), 1), f"vrchol_{k}": f"{v:%Y-%m-%d %H:%M}"}


def val_povodne(y, pred):
    """Chyba v okně každé ze 4 validačních povodní zvlášť (Děčín +24 h)."""
    return {m: povoden(y, pred, m)[f"mae_{m.replace('-', '_')}"] for m in POVODNE_VAL}
