"""Přísnější kontrola srážek: leave-one-flood-out CV (LOFO) přes 22 povodní 2006–2020 v Děčíně.

python lofo_srazky.py ridge_tym|ridge_dan|lgbm [--seedy 42 43 44] [--horizont 24]

Foldy jsou převzaté beze změny z ridge_dan/stanice_vsem/lofo_foldy.csv (worktree hackathon-2026-ridge, 23:19, sha1
ad383c28), kopie ve vysledky/lofo_foldy.csv: fold k drží okno povodně k (7 dní před až 5 dní po vrcholu) a z tréninku
vyřadí okno ± 20 dní, trénuje se na všem ostatním z let 2006–2020 (t + horizont < 2021, test se nepoužije).
Řádky jako tam (t ≥ první řádek + 72 h), navíc jen hodiny se srážkami (obaly.data), stejné pro obě varianty.
Zlepšení platí jen při průměru přes 22 povodní lepším aspoň o 1 cm a zlepšení většiny povodní.
Zápis do vysledky/lofo.jsonl.
"""
import argparse
import json
import time
from datetime import datetime

import numpy as np
import pandas as pd
from scipy.stats import binomtest

import obaly as O
import data_ridge
from evaluate import povodne, varovani

FOLDY = O.S.ZDE / "vysledky/lofo_foldy.csv"
KONEC = pd.Timestamp("2021-01-01", tz="UTC")
LOG = O.S.ZDE / "vysledky/lofo.jsonl"


def radky(model, horizont, sada):
    A, B, y, _ = O.data(model, "decin", horizont, sada)
    X0 = O.data(model, "decin", horizont, sada, puvodni=True)[0]  # první řádek bez ohledu na srážky, jako lofo.py
    ok = (A.index + pd.Timedelta(hours=horizont) < KONEC) & (A.index >= X0.index[0] + pd.Timedelta(hours=72))
    return A[ok], B[ok], y[ok]


def foldy(y, horizont):
    F = pd.read_csv(FOLDY)
    F = F[F.horizont == horizont]
    out = []
    for _, f in F.iterrows():
        cas = lambda s: pd.Timestamp(s)  # noqa: E731
        okno = (y.index >= cas(f.okno_od)) & (y.index <= cas(f.okno_do))
        mezera = (y.index >= cas(f.mezera_od)) & (y.index <= cas(f.mezera_do))
        out.append(dict(nazev=f.povoden, vrchol=cas(f.vrchol_cas_vydani_utc), okno=okno, mezera=mezera))
    # stejné vrcholy jako v souboru foldů i na řádcích se srážkami
    assert [f"{v:%Y-%m-%d %H}" for v in povodne(y, 400)] == [f"{p['vrchol']:%Y-%m-%d %H}" for p in out]
    return out


def predpovedi(fit, X, y, pov, horizont):
    pred = []
    for p in pov:
        tr = ~p["mezera"]
        pred.append(np.asarray(fit(X[tr], y[tr], "decin", horizont)(X[p["okno"]]), dtype=float))
    return pred


def skore(pred, y, pov, horizont, zaklad=None):
    """Stejné jako lofo.skore: chyby po povodních a průměr; ze spojené řady oken začátek vzestupu a poplachy
    (řádek ve dvou oknech bere předpověď foldu s bližším vrcholem); proti základu rozdíl a počet zlepšených."""
    e = np.array([np.abs(pr - y[p["okno"]].to_numpy()).mean() for pr, p in zip(pred, pov)])
    out = dict(lofo=round(float(e.mean()), 2), po_povodnich={p["nazev"]: round(float(x), 2) for p, x in zip(pov, e)})
    ser, vzd = pd.Series(np.nan, index=y.index), pd.Series(np.inf, index=y.index)
    for pr, p in zip(pred, pov):
        idx = y.index[p["okno"]]
        d = np.abs((idx - p["vrchol"]) / pd.Timedelta(hours=1))
        lepsi = d < vzd[idx].to_numpy()
        ser[idx[lepsi]], vzd[idx[lepsi]] = pr[lepsi], d[lepsi]
    v = ser.notna()
    yy, pp = y[v], ser[v]
    H = data_ridge.nacti()["decin_H"]
    ted = H.reindex(yy.index)
    zac = ((yy - ted) >= 50) & ((ted - H.shift(6).reindex(yy.index)) < 10)
    out |= dict(zacatek=round(float((pp - yy)[zac].abs().mean()), 2), n_zacatek=int(zac.sum()))
    for n, prah in ((2, 490), (3, 560)):
        w = varovani(yy, pp, prah, horizont)
        out |= {f"spa{n}_propasnuto": w["propasnuto"], f"spa{n}_plane": w["plane_poplachy"],
                f"spa{n}_predstih_h": w["predstih_h"]}
    if zaklad is not None:
        z = np.array(list(zaklad["po_povodnich"].values()))
        d = e - z
        lepsi = int((d < 0).sum())
        out |= dict(rozdil=round(float(d.mean()), 2), zlepseno=lepsi, zhorseno=int((d > 0).sum()),
                    nejhorsi_zhorseni=round(float(d.max()), 2), nejvetsi_zlepseni=round(float(d.min()), 2),
                    rozdil_zacatek=round(out["zacatek"] - zaklad["zacatek"], 2),
                    znamenkovy_p=round(float(binomtest(lepsi, max(int((d != 0).sum()), 1), 0.5).pvalue), 4),
                    zlepseni_plati=bool(d.mean() <= -1.0 and lepsi > len(d) / 2))
    return out


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("model")
    p.add_argument("--seedy", nargs="+", type=int, default=list(O.SEEDY))
    p.add_argument("--horizont", type=int, default=24)
    p.add_argument("--sada", default="hlavni")
    a = p.parse_args()
    A, B, y = radky(a.model, a.horizont, a.sada)
    pov = foldy(y, a.horizont)
    zaklady = {}
    for varianta, seed, fit in O.varianty(a.model, a.seedy):
        t = time.time()
        X = B if varianta == "srazky" else A
        assert X.index.equals(A.index)
        pr = predpovedi(fit, X, y, pov, a.horizont)
        s = skore(pr, y, pov, a.horizont, zaklady.get(seed) if varianta == "srazky" else None)
        if varianta == "bez":
            zaklady[seed] = s
        z = dict(cas=datetime.now().isoformat(timespec="seconds"), model=a.model, varianta=varianta, seed=seed,
                 sada=a.sada, horizont=a.horizont, radku=len(y), povodni=len(pov), otisk_srazek=O.otisk(O.SRAZKY),
                 **s, sekund=round(time.time() - t, 1))
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(z, ensure_ascii=False) + "\n")
        print(f"{a.model} {varianta} seed {seed}: LOFO {s['lofo']} cm, začátek {s['zacatek']}, "
              f"2. SPA propásnuto/plané {s['spa2_propasnuto']}/{s['spa2_plane']}"
              + (f" | rozdíl {s['rozdil']:+.2f}, zlepšeno {s['zlepseno']}/22, nejhorší {s['nejhorsi_zhorseni']:+.1f}, "
                 f"p {s['znamenkovy_p']}, platí {s['zlepseni_plati']}" if "rozdil" in s else "")
              + f" ({len(y)} řádků, {z['sekund']} s)", flush=True)
