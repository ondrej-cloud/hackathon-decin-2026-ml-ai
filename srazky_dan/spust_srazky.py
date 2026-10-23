"""Srovnání „beze změny“ vs „+ srážky“ (šestihodinové srážky ze synoptických stanic). Test 2021–2025 se tady nespouští.

python spust_srazky.py ridge_tym|ridge_dan|lgbm [--sada hlavni|povodi] [--srazky CESTA]
    CV v tréninku (Děčín +24 h) a validace (ridge_tym a lgbm všech 6 kombinací jako porovnej.py, ridge_dan jen
    Děčín +24 h), obě varianty na stejných řádcích. Zápis do vysledky/srazky.jsonl, předpovědi Děčín +24 h na validaci
    do vysledky/predpovedi_<model>_<varianta>_<seed>.parquet (sada povodi s příponou _povodi).
python spust_srazky.py <model> --kontrola [--seedy 42]
    jen varianta beze změny na původních řádcích (bez průniku se srážkami), musí dát známá čísla (ZNAMA);
    u lgbm navíc obal pro srážky bez srážkových sloupců, musí dát stejné předpovědi jako lgbm_c.fit.
Cesta ke srážkám jde zadat i proměnnou SRAZKY_6H. --vystup SLOZKA: zkušební běhy mimo vysledky/.
"""
import argparse
import json
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

import obaly as O
import spolecne as S
import data_ridge
from evaluate import casti

# beze změny na původních řádcích: ridge_dan/ZPRAVA.md, stanice_vsem/vysledky.jsonl (ridge_12, ridge_30, lgbm_12)
ZNAMA = {
    "ridge_tym": dict(cv_povodne=15.64, decin24=15.5, prumer_povodne=17.08),
    "ridge_dan": dict(cv_povodne=14.17, decin24=17.8),
    "lgbm": dict(cv_povodne=18.05, decin24=21.3, prumer_povodne=23.07),
}
RADKY = {}


def hlidej(klic, trenink, hodnoceno):
    """Všechny varianty musí trénovat i hodnotit na stejných řádcích."""
    prvni = RADKY.setdefault(klic, (trenink, hodnoceno))
    assert prvni[0].equals(trenink) and prvni[1].equals(hodnoceno), klic


def vstupy(varianta, A, B):
    return B if varianta == "srazky" else A


def cv(a, varianty):
    A, B, y, c = O.data(a.model, "decin", 24, a.sada, a.srazky, a.kontrola)
    H = data_ridge.nacti()["decin_H"]
    for varianta, seed, fit in varianty:
        X = vstupy(varianta, A, B)
        t = time.time()
        yt, pred = S.cv_predikce(fit, X, y, c, "decin", 24)
        assert np.isfinite(pred).all()
        hlidej("cv", X.index[c == "train"], yt.index)
        s = S.cv_skore(yt, pred, X.loc[yt.index, "decin_H_0"]) | O.cv_zacatek(yt, pred, H)
        yield varianta, seed, dict(cast="cv", cil="decin", horizont=24, n_train=len(yt), **s,
                                   sekund=round(time.time() - t, 1))


def val(a, varianty):
    H = data_ridge.nacti()["decin_H"]
    radky = {(v, s): [] for v, s, _ in varianty}
    d24, cas, pred24 = {}, dict.fromkeys(radky, 0.0), {}
    kombinace = [("decin", 24)] if a.jen_decin24 else O.KOMBINACE[a.model]
    for cil, h in kombinace:
        A, B, y, c = O.data(a.model, cil, h, a.sada, a.srazky, a.kontrola)
        if a.kontrola:
            assert c.equals(casti(cil, h).reindex(c.index)), (cil, h)
        tr, ev = c == "train", c == "val"
        for varianta, seed, fit in varianty:
            X = vstupy(varianta, A, B)
            t = time.time()
            pred = pd.Series(np.asarray(fit(X[tr], y[tr], cil, h)(X[ev]), dtype=float), index=X.index[ev])
            assert np.isfinite(pred).all()
            hlidej(("val", cil, h), X.index[tr], pred.index)
            radky[(varianta, seed)].append(dict(cil=cil, horizont=h, n_train=int(tr.sum()), n_val=int(ev.sum()),
                                                **S.vyhodnot(y[ev], pred, cil, h)))
            if (cil, h) == ("decin", 24):
                d24[(varianta, seed)] = (S.Hd.metriky(y[ev], pred, H, cil, h) | S.povoden_2006(y[ev], pred, H)
                                         | O.povoden(y[ev], pred, "2010-09") | dict(povodne=O.val_povodne(y[ev], pred)))
                pred24[(varianta, seed)] = pred
                pd.DataFrame({"y": y[ev], "pred": pred}).to_parquet(
                    a.vystup / f"predpovedi_{a.model}_{varianta}_{seed}{a.pripona}.parquet")
            cas[(varianta, seed)] += time.time() - t
        del A, B
    for (varianta, seed), r in radky.items():
        df = pd.DataFrame(r)
        souhrn = dict(kombinaci=len(df), prumer_povodne=round(df.mae_povodne.mean(), 2), prumer_mae=round(df.mae.mean(), 2),
                      spa2_propasnuto=int(df.spa2_propasnuto.sum()), spa2_plane=int(df.spa2_plane_poplachy.sum()),
                      spa3_propasnuto=int(df.spa3_propasnuto.sum()), spa3_plane=int(df.spa3_plane_poplachy.sum()),
                      spa2_predstih_h=round(df.spa2_predstih_h.mean(), 1),
                      spa3_predstih_h=round(df.spa3_predstih_h.mean(), 1))
        d = d24[(varianta, seed)]
        if varianta == "obal":
            d["rozdil_proti_lgbm_c"] = float((pred24[(varianta, seed)] - pred24[("bez", seed)]).abs().max())
        r24 = next(x for x in r if (x["cil"], x["horizont"]) == ("decin", 24))
        yield varianta, seed, dict(cast="val", n_train=r24["n_train"], n_val=r24["n_val"], **souhrn, decin24=d,
                                   kombinace=r, sekund=round(cas[(varianta, seed)], 1))


def kontrola(z):
    """Porovná variantu beze změny na původních řádcích se známými čísly."""
    zn = ZNAMA[z["model"]]
    if z["cast"] == "cv":
        return f"CV povodně {z['cv_povodne']:.2f} (známé {zn['cv_povodne']})"
    s = f"VAL Děčín +24 {z['decin24']['mae_povodne']} (známé {zn['decin24']})"
    if "prumer_povodne" in zn and z["kombinaci"] == 6:
        s += f", prumer_povodne {z['prumer_povodne']} (známé {zn['prumer_povodne']})"
    if "rozdil_proti_lgbm_c" in z["decin24"]:
        s += f", obal bez srážek proti lgbm_c.fit: největší rozdíl {z['decin24']['rozdil_proti_lgbm_c']:.2g} cm"
    return s


def popis(z):
    if z["cast"] == "cv":
        return (f"CV povodně {z['cv_povodne']:.2f}, začátek {z['cv_zacatek']:.2f}, vzestup {z['cv_vzestup']:.2f}, "
                f"{z['n_train']} řádků")
    d = z["decin24"]
    return (f"VAL prumer_povodne {z['prumer_povodne']}, Děčín +24 {d['mae_povodne']}, začátek {d['mae_zacatek']}, "
            f"2006 {d['mae_2006']}, 9/2010 {d['mae_2010_09']}, 2./3. SPA plané {z['spa2_plane']}/{z['spa3_plane']}, "
            f"propásnuto {z['spa2_propasnuto']}/{z['spa3_propasnuto']}, řádků {z['n_train']}/{z['n_val']}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("model", choices=list(O.KOMBINACE))
    p.add_argument("--sada", choices=("hlavni", "povodi"), default="hlavni")
    p.add_argument("--srazky", type=Path, default=O.SRAZKY)
    p.add_argument("--seedy", type=int, nargs="+", default=list(O.SEEDY))
    p.add_argument("--bez-cv", action="store_true")
    p.add_argument("--jen-decin24", action="store_true", help="validace jen Děčín +24 h (zkouška)")
    p.add_argument("--kontrola", action="store_true")
    p.add_argument("--vystup", type=Path, default=S.ZDE / "vysledky")
    a = p.parse_args()
    a.vystup.mkdir(exist_ok=True)
    varianty = O.varianty(a.model, a.seedy)
    if a.kontrola:
        varianty = [v for v in varianty if v[0] == "bez"]
        if a.model == "lgbm":
            varianty.append(("obal", a.seedy[0], O.fit_lgbm_srazky(a.seedy[0])))
        a.sada, a.pripona, log, otisk = "puvodni", "_puvodni", a.vystup / "kontrola.jsonl", None
    else:
        a.pripona = "" if a.sada == "hlavni" else f"_{a.sada}"
        log, otisk = a.vystup / "srazky.jsonl", O.otisk(a.srazky)
        print(f"srážky {a.srazky} (otisk {otisk}), sada {a.sada}: {O.vyber(O.srazky(a.srazky, a.sada).columns, a.sada)}",
              flush=True)
    casti_behu = ([] if a.bez_cv else [cv]) + [val]
    for cast in casti_behu:
        for varianta, seed, z in cast(a, varianty):
            z = dict(cas=datetime.now().isoformat(timespec="seconds"), model=a.model, varianta=varianta, seed=seed,
                     sada=a.sada, srazky=otisk, nejstarsi_sr=None if a.kontrola else O.NEJSTARSI_SR) | z
            with open(log, "a", encoding="utf-8") as f:
                f.write(json.dumps(z, ensure_ascii=False, default=float) + "\n")
            print(f"{a.model} {varianta} seed {seed}: {kontrola(z) if a.kontrola else popis(z)} ({z['sekund']} s)",
                  flush=True)
