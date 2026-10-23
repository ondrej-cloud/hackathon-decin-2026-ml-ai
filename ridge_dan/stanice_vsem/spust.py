"""Srovnání „beze změny“ vs „+ 18 stanic“ pro týmové modely. Test 2021–2025 se tady nespouští.

python spust.py ridge|lgbm|fyzika      CV (Děčín +24 h) a validace (všech 6 kombinací jako porovnej.py)
Neuronová síť se tady nepočítá (jeden trénink 2–5 min na notebooku), srovnání sítě běží zvlášť na Kaggle (větev dan-sit).
Zápis do stanice_vsem/vysledky.jsonl, předpovědi Děčín +24 h na validaci do stanice_vsem/predpovedi_<varianta>.parquet.
"""
import argparse
import json
import time
from datetime import datetime
from functools import cache

import numpy as np
import pandas as pd

import spolecne as S
import data_ridge

# LightGBM v týmovém nastavení nemá náhodný výběr řádků ani vstupů: seedy 42/43/44 dávaly přesně stejné výsledky
# (vysledky.jsonl, běh 22:43–22:52), proto už jen seed 42
SEEDY = (42,)
LOG = S.ZDE / "vysledky.jsonl"


@cache
def data(cil, horizont):
    return S.data(cil, horizont)


def varianty(model):
    """[(varianta, seed, fit, nové stanice ano/ne)]"""
    if model == "ridge":
        import ridge_stanice as R
        return [(n, None, f, nove) for n, (f, nove) in R.VARIANTY.items()]
    if model == "lgbm":
        import lgbm_stanice as L
        return [v for s in SEEDY for v in (("lgbm_12", s, L.fit_tym(s), False), ("lgbm_30", s, L.fit_stanice(s), True))]
    if model == "fyzika":
        import fyzika_stanice as F
        return [("fyzika_12", None, F.fit_tym, False), ("fyzika_30", None, F.fit_stanice, True)]
    raise ValueError(model)


def zapis(z):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(z, ensure_ascii=False, default=float) + "\n")


def cv(varianta, seed, fit, nove):
    X, Xn, y, c = data("decin", 24)
    A = Xn if nove else X
    t = time.time()
    yt, pred = S.cv_predikce(fit, A, y, c, "decin", 24)
    s = S.cv_skore(yt, pred, A.loc[yt.index, "decin_H_0"])
    return dict(cast="cv", **s, sekund=round(time.time() - t, 1))


def val(varianta, seed, fit, nove, kombinace=S.VSE):
    H = data_ridge.nacti()["decin_H"]
    t = time.time()
    radky, d24 = [], {}
    for cil, h in kombinace:
        X, Xn, y, c = data(cil, h)
        A = Xn if nove else X
        tr, ev = c == "train", c == "val"
        pred = pd.Series(np.asarray(fit(A[tr], y[tr], cil, h)(A[ev]), dtype=float), index=A.index[ev])
        assert np.isfinite(pred).all()
        m = S.vyhodnot(y[ev], pred, cil, h)
        radky.append(dict(cil=cil, horizont=h, **m))
        if (cil, h) == ("decin", 24):
            d24 = S.Hd.metriky(y[ev], pred, H, cil, h) | S.povoden_2006(y[ev], pred, H)
            pd.DataFrame({"y": y[ev], "pred": pred}).to_parquet(S.ZDE / f"predpovedi_{varianta}_{seed}.parquet")
    df = pd.DataFrame(radky)
    souhrn = dict(prumer_povodne=round(df.mae_povodne.mean(), 2), prumer_mae=round(df.mae.mean(), 2),
                  spa2_propasnuto=int(df.spa2_propasnuto.sum()), spa2_plane=int(df.spa2_plane_poplachy.sum()),
                  spa3_propasnuto=int(df.spa3_propasnuto.sum()), spa3_plane=int(df.spa3_plane_poplachy.sum()),
                  spa2_predstih_h=round(df.spa2_predstih_h.mean(), 1), spa3_predstih_h=round(df.spa3_predstih_h.mean(), 1))
    return dict(cast="val", **souhrn, decin24=d24, kombinace=radky, sekund=round(time.time() - t, 1))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("model")
    p.add_argument("--bez-cv", action="store_true")
    p.add_argument("--jen-cv", action="store_true")
    p.add_argument("--varianta", help="jen tuto variantu")
    a = p.parse_args()
    for varianta, seed, fit, nove in varianty(a.model):
        if a.varianta and varianta != a.varianta:
            continue
        zakl = dict(cas=datetime.now().isoformat(timespec="seconds"), model=a.model, varianta=varianta, seed=seed,
                    nove_stanice=nove)
        if not a.bez_cv:
            z = zakl | cv(varianta, seed, fit, nove)
            zapis(z)
            print(f"{varianta} seed {seed}: CV povodně {z['cv_povodne']:.2f}, velké {z['cv_velke']:.2f}, "
                  f"vzestup {z['cv_vzestup']:.2f} ({z['sekund']} s)", flush=True)
        if a.jen_cv:
            continue
        z = zakl | val(varianta, seed, fit, nove)
        zapis(z)
        d = z["decin24"]
        print(f"{varianta} seed {seed}: VAL prumer_povodne {z['prumer_povodne']}, Děčín +24 {d['mae_povodne']}, "
              f"začátek {d['mae_zacatek']}, 2006 {d['mae_2006']} (přestřelení {d['max_prestreleni_2006']}), "
              f"2. SPA propásnuto/plané {z['spa2_propasnuto']}/{z['spa2_plane']} ({z['sekund']} s)", flush=True)
