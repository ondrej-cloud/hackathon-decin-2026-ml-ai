"""Týmová neuronová síť (src/models/mlp.py, beze změny) s různými vstupy: CV v tréninku a validace. Test 2021–2025 ne.

python beh_sit.py --prace 4 --vystup DIR               natrénuje všechno a vyhodnotí (na Kaggle)
python beh_sit.py --jen-vyhodnot --vystup DIR          jen vyhodnotí stažené předpovědi
python beh_sit.py --zkouska --prace 1 --vystup DIR     rychlá zkouška celého řetězce (3 epochy, Děčín +24 h)

Varianty se liší jen vstupy, řádky jsou pro všechny stejné (spolecne.data). Každý trénink je samostatná úloha,
uloží jen předpověď (pred_<varianta>_<seed>_<cast>_<cil>_<h>[_<blok>].parquet), metriky se z nich počítají potom.
Pořadí úloh: nejdřív validace varianty a se seedem 42, aby byla reprodukce týmového čísla (17,83 cm) vidět hned.
"""
import os

for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[k] = "1"  # několik tréninků souběžně, každý na jednom jádře

import argparse  # noqa: E402
import json  # noqa: E402
import time  # noqa: E402
import warnings  # noqa: E402
from functools import cache  # noqa: E402
from multiprocessing import Pool  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import spolecne as S  # noqa: E402
import data_ridge  # noqa: E402
from evaluate import povodne  # noqa: E402
from models import mlp  # noqa: E402

warnings.filterwarnings("ignore")
SEEDY = (42, 43, 44)
VARIANTY = {"a": "beze změny (98 týmových vstupů)", "b": "+ průtoky 18 nových stanic (224 vstupů)",
            "c": "+ srážky (98 + 10 sloupců sr_blizko_*, sr_dal_*, surové mm)"}
SRAZKY = None  # cesta k srazky_6h.parquet; když je, běží a, b i c jen na hodinách se srážkami
NEJSTARSI_SR = 78  # nejstarší srážkové měření v příznacích (t − 78 h), jako srazky_dan/obaly.py
TYM_42 = 17.83  # results/2026-10-23_195305_mlp.json, Ondra, verze 9a31181e
ZKOUSKA = False


def nacti_data(cil, h):
    """X, Xn (+ stanice), Xs (+ srážky, jen se SRAZKY), y, c; pro všechny varianty STEJNÉ řádky."""
    X, Xn, y, c = S.data(cil, h)
    if SRAZKY is None:
        return X, Xn, None, y, c
    Sr = pd.read_parquet(SRAZKY).filter(regex=r"^sr_(blizko|dal)_")
    assert Sr.shape[1] == 10 and str(Sr.index.tz) == "UTC"
    Sr = Sr.reindex(X.index).astype("float64")
    ok = Sr.notna().all(axis=1)
    # hranice částí s nejstarším srážkovým měřením t − 78 h (stejně jako srazky_dan/obaly.data)
    c = S.Hd.casti(data_ridge.nacti()[f"{cil}_H"], h, max(36, NEJSTARSI_SR)).reindex(X.index)
    return X[ok], Xn[ok], pd.concat([X, Sr], axis=1)[ok], y[ok], c[ok]


data = cache(nacti_data)  # při tréninku; vyhodnocení si drží jen osa(), ne celé matice vstupů


def vstupy(varianta, cil, h):
    X, Xn, Xs, y, c = data(cil, h)
    return {"a": X, "b": Xn, "c": Xs}[varianta], y, c


@cache
def osa(cil, h):
    """Pro vyhodnocení stačí y, rozdělení, stav teď a počty vstupů (řádky jsou pro všechny varianty stejné)."""
    X, Xn, Xs, y, c = nacti_data(cil, h)
    n = {"a": X.shape[1], "b": Xn.shape[1], "c": None if Xs is None else Xs.shape[1]}
    return y, c, X[f"{cil}_H_0"], n


def ulohy(varianty, seedy, kombinace=S.VSE, bloky=range(6)):
    prvni = [(varianty[0], seedy[0], "val", cil, h, None) for cil, h in kombinace]
    ostatni = [(v, s, "val", cil, h, None) for v in varianty for s in seedy for cil, h in kombinace]
    ostatni += [(v, s, "cv", "decin", 24, k) for v in varianty for s in seedy for k in bloky]
    return prvni + [u for u in ostatni if u not in prvni]


def soubor(adresar, u):
    v, s, cast, cil, h, k = u
    return Path(adresar) / f"pred_{v}_{s}_{cast}_{cil}_{h}{'' if k is None else f'_{k}'}.parquet"


def trenuj(u, adresar):
    v, s, cast, cil, h, k = u
    if ZKOUSKA:
        mlp.PARAMETRY["max_iter"] = 3
    A, y, c = vstupy(v, cil, h)
    t = time.time()
    if cast == "val":
        tr, ev = c == "train", c == "val"
        pred, idx = mlp.fit(A[tr], y[tr], cil, h, seed=s)(A[ev]), A.index[ev]
    else:
        tr = c == "train"
        At, yt = A[tr], y[tr]
        _, f_tr, f_drz = S.Hd.bloky_cv(At.index)[k]
        pred, idx = mlp.fit(At[f_tr], yt[f_tr], cil, h, seed=s)(At[f_drz]), At.index[f_drz]
    pred = np.asarray(pred, dtype=float)
    assert np.isfinite(pred).all(), u
    pd.DataFrame({"pred": pred}, index=idx).to_parquet(soubor(adresar, u))
    return u, round(time.time() - t, 1)


def _trenuj(arg):
    return trenuj(*arg)


def _nastav(zkouska, srazky):
    global ZKOUSKA, SRAZKY
    ZKOUSKA, SRAZKY = zkouska, srazky


def nacti_pred(adresar, u, index):
    p = pd.read_parquet(soubor(adresar, u)).pred
    assert p.index.equals(index), u
    return p


def povoden(y, pred, mesic):
    """Stejné jako spolecne.povoden_2006, pro libovolnou validační povodeň nad 2. SPA (např. '2010-09')."""
    v = next(v for v in povodne(y, 490) if f"{v:%Y-%m}" == mesic)
    okno = (y.index >= v - S.Hd.E.PRED) & (y.index <= v + S.Hd.E.PO)
    stoupa = okno & (y.index < v - pd.Timedelta(hours=24))
    d = pred - y
    r = mesic[:4]
    return {f"mae_{r}": round(float(d[okno].abs().mean()), 1), f"mae_{r}_stoupani": round(float(d[stoupa].abs().mean()), 1),
            f"max_prestreleni_{r}": round(float(d[stoupa].max()), 1), f"bias_{r}": round(float(d[okno].mean()), 1)}


def vyhodnot_val(adresar, v, s, kombinace=S.VSE):
    H = data_ridge.nacti()["decin_H"]
    radky, d24 = [], {}
    for cil, h in kombinace:
        y, c, _, _ = osa(cil, h)
        ye = y[c == "val"]
        pred = nacti_pred(adresar, (v, s, "val", cil, h, None), ye.index)
        radky.append(dict(cil=cil, horizont=h, **S.vyhodnot(ye, pred, cil, h)))
        if (cil, h) == ("decin", 24):
            d24 = S.Hd.metriky(ye, pred, H, cil, h) | S.povoden_2006(ye, pred, H) | povoden(ye, pred, "2010-09")
            assert d24["mae_2006"] == povoden(ye, pred, "2006-04")["mae_2006"]
    df = pd.DataFrame(radky)
    return dict(prumer_povodne=round(df.mae_povodne.mean(), 2), prumer_mae=round(df.mae.mean(), 2),
                spa2_propasnuto=int(df.spa2_propasnuto.sum()), spa2_plane=int(df.spa2_plane_poplachy.sum()),
                spa3_propasnuto=int(df.spa3_propasnuto.sum()), spa3_plane=int(df.spa3_plane_poplachy.sum()),
                spa2_predstih_h=round(df.spa2_predstih_h.mean(), 1), spa3_predstih_h=round(df.spa3_predstih_h.mean(), 1),
                decin24=d24, kombinace=radky)


def vyhodnot_cv(adresar, v, s, bloky=range(6)):
    y, c, ted, _ = osa("decin", 24)
    yt = y[c == "train"]
    casti = []
    for k in bloky:
        _, _, f_drz = S.Hd.bloky_cv(yt.index)[k]
        casti.append(nacti_pred(adresar, (v, s, "cv", "decin", 24, k), yt.index[f_drz]))
    pred = pd.concat(casti).reindex(yt.index)
    assert pred.notna().all()
    return S.cv_skore(yt, pred, ted.loc[yt.index])


def vyhodnot(adresar, varianty, seedy, kombinace=S.VSE, bloky=range(6)):
    vysledky = []
    for v in varianty:
        for s in seedy:
            z = dict(varianta=v, popis=VARIANTY[v], seed=s, vstupu=osa("decin", 24)[3][v],
                     radku_val_decin24=int((osa("decin", 24)[1] == "val").sum()))
            z |= {"val": vyhodnot_val(adresar, v, s, kombinace), "cv": vyhodnot_cv(adresar, v, s, bloky)}
            vysledky.append(z)
            d = z["val"]["decin24"]
            print(f"{v} seed {s}: CV povodně {z['cv']['cv_povodne']:.2f}, VAL prumer_povodne {z['val']['prumer_povodne']}, "
                  f"začátek vzestupu {d['mae_zacatek']}, 2006 {d['mae_2006']}, 2010 {d['mae_2010']}, "
                  f"2. SPA propásnuto/plané {z['val']['spa2_propasnuto']}/{z['val']['spa2_plane']}", flush=True)
    with open(Path(adresar) / "vysledky_sit.json", "w", encoding="utf-8") as f:
        json.dump(vysledky, f, ensure_ascii=False, indent=1, default=float)
    return vysledky


def kontrola_radku():
    """Všechny varianty mají stejné řádky a varianta a stejné jako týmová tabulka (features.tabulka)."""
    for cil, h in S.VSE:
        X, Xn, Xs, y, c = data(cil, h)
        Xt, _ = S.tabulka(cil, h)
        assert X.index.equals(Xn.index) and X.equals(Xt.loc[X.index]), (cil, h)
        assert SRAZKY is not None or len(X) == len(Xt), (cil, h)
        assert Xs is None or (Xs.index.equals(X.index) and Xs[X.columns].equals(X)), (cil, h)
        print(f"řádky {cil} +{h} h: {len(X)} (týmová tabulka {len(Xt)}), vstupy a {X.shape[1]}, b {Xn.shape[1]}, "
              f"c {None if Xs is None else Xs.shape[1]}, train {int((c == 'train').sum())}, val {int((c == 'val').sum())}", flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--vystup", required=True)
    p.add_argument("--prace", type=int, default=4)
    p.add_argument("--varianty", default=None)
    p.add_argument("--jen-vyhodnot", action="store_true")
    p.add_argument("--zkouska", action="store_true")
    p.add_argument("--dil", default="1/1", help="i/n: jen každá n-tá úloha od i-té (víc kernelů souběžně)")
    p.add_argument("--srazky", help="srazky_6h.parquet: pustí i variantu c, všechny jen na hodinách se srážkami")
    a = p.parse_args()
    ZKOUSKA, SRAZKY = a.zkouska, a.srazky
    varianty = a.varianty.split(",") if a.varianty else (["a", "b", "c"] if SRAZKY else ["a", "b"])
    kombinace, bloky, seedy = (([("decin", 24)], range(6), (42,)) if a.zkouska else (S.VSE, range(6), SEEDY))
    Path(a.vystup).mkdir(parents=True, exist_ok=True)
    if not a.zkouska and not a.jen_vyhodnot:
        kontrola_radku()
    if not a.jen_vyhodnot:
        i, n = (int(x) for x in a.dil.split("/"))
        seznam = [u for j, u in enumerate(ulohy(varianty, seedy, kombinace, bloky)) if j % n == i - 1]
        print(f"{len(seznam)} tréninků, {a.prace} souběžně", flush=True)
        t0, hotovo, prvni = time.time(), 0, {}
        with Pool(a.prace, initializer=_nastav, initargs=(ZKOUSKA, SRAZKY)) as pool:
            for u, sekund in pool.imap_unordered(_trenuj, [(u, a.vystup) for u in seznam]):
                hotovo += 1
                print(f"[{hotovo}/{len(seznam)} {time.time() - t0:.0f} s] {u} {sekund} s", flush=True)
                if n == 1 and u[:3] == (varianty[0], seedy[0], "val"):
                    prvni[u[3:5]] = u
                    if len(prvni) == len(kombinace):
                        z = vyhodnot_val(a.vystup, varianty[0], seedy[0], kombinace)
                        print(f"REPRODUKCE: {varianty[0]} seed {seedy[0]} prumer_povodne {z['prumer_povodne']} "
                              f"(tým {TYM_42}), po kombinacích {[r['mae_povodne'] for r in z['kombinace']]}", flush=True)
    if a.dil == "1/1" or a.jen_vyhodnot:
        vyhodnot(a.vystup, varianty, seedy, kombinace, bloky)
