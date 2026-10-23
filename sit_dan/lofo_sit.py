"""Leave-one-flood-out CV týmové sítě (src/models/mlp.py beze změny) přes 22 povodní 2006–2020, varianty a / b.

python lofo_sit.py --foldy lofo_foldy.csv --vystup DIR [--dil 1/4] [--horizonty 24] [--seedy 42] [--prace 4]
python lofo_sit.py --foldy lofo_foldy.csv --vystup DIR --jen-vyhodnot        spojí předpovědi a spočítá skóre

Foldy (okno povodně a vyřazená mezera kolem něj) jsou ze session ridge (stanice_vsem/lofo_foldy.csv), aby šly
předpovědi míchat s jejich modely. Řádky jako ridge_dan/zlepseni/lofo.py: Děčín, t + horizont < 2021,
t aspoň 72 h od začátku tabulky, a navíc bez děr v nových stanicích (spolecne.data), pro obě varianty stejné.
Každý fold uloží předpovědi pro své okno (lofo_<varianta>_<seed>_<h>_<fold>.parquet). Test 2021–2025 se nepoužije.
"""
import os

for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[k] = "1"

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
CIL = "decin"
KONEC = pd.Timestamp("2021-01-01", tz="UTC")
NEJDELSI = 72


def nacti_foldy(cesta):
    F = pd.read_csv(cesta)
    for k in F.columns:
        if k.startswith(("okno_", "mezera_", "vrchol")) and k != "vrchol_cm":
            F[k] = pd.to_datetime(F[k], utc=True)
    return F


@cache
def data(h):
    """X (98 týmových), Xn (+ 126 nových stanic), y na společných řádcích LOFO."""
    X, Xn, y, _ = S.data(CIL, h)
    X0, _ = S.tabulka(CIL, h)
    ok = (X.index + pd.Timedelta(hours=h) < KONEC) & (X.index >= X0.index[0] + pd.Timedelta(hours=NEJDELSI))
    return X[ok], Xn[ok], y[ok]


def masky(F, fold, index):
    f = F[F.fold == fold].iloc[0]
    okno = (index >= f.okno_od) & (index <= f.okno_do)
    mezera = (index >= f.mezera_od) & (index <= f.mezera_do)
    return okno, mezera


def soubor(adresar, v, s, h, fold):
    return Path(adresar) / f"lofo_{v}_{s}_{h}_{fold:02d}.parquet"


def trenuj(u):
    v, s, h, fold, cesta_foldy, adresar = u
    X, Xn, y = data(h)
    A = {"a": X, "b": Xn}[v]
    F = nacti_foldy(cesta_foldy)
    F = F[F.horizont == h]
    okno, mezera = masky(F, fold, A.index)
    t = time.time()
    pred = np.asarray(mlp.fit(A[~mezera], y[~mezera], CIL, h, seed=s)(A[okno]), dtype=float)
    assert np.isfinite(pred).all(), u
    pd.DataFrame({"cas": A.index[okno], "cil": CIL, "horizont": h, "varianta": v, "seed": s, "fold": fold,
                  "povoden": F[F.fold == fold].povoden.iloc[0], "predpoved": pred,
                  "skutecnost": y[okno].to_numpy()}).to_parquet(soubor(adresar, v, s, h, fold))
    return u[:4], round(time.time() - t, 1)


def vyhodnot(adresar, horizonty, seedy):
    """Chyba po povodních, průměr přes 22, kolik se jich zlepšilo, začátek vzestupu a povodeň 2006 (b proti a)."""
    from scipy.stats import binomtest
    P = pd.concat([pd.read_parquet(f) for f in sorted(Path(adresar).glob("lofo_*.parquet"))])
    H = data_ridge.nacti()[f"{CIL}_H"]
    out = {}
    for h in horizonty:
        for s in seedy:
            q = P[(P.horizont == h) & (P.seed == s)].copy()
            q["e"] = (q.predpoved - q.skutecnost).abs()
            ted = H.reindex(pd.DatetimeIndex(q.cas)).to_numpy()
            pred6 = H.shift(6).reindex(pd.DatetimeIndex(q.cas)).to_numpy()
            q["zacatek"] = ((q.skutecnost - ted) >= 50) & ((ted - pred6) < 10)
            po = q.groupby(["povoden", "varianta"]).e.mean().unstack()
            zlepseno = int((po.b < po.a).sum())
            z = q[q.zacatek].groupby("varianta").e.mean()
            p2006 = po.loc[[i for i in po.index if str(i).startswith("2006-0")]]
            out[f"h{h}_s{s}"] = dict(
                povodni=len(po), lofo_a=round(float(po.a.mean()), 2), lofo_b=round(float(po.b.mean()), 2),
                rozdil=round(float((po.b - po.a).mean()), 2), zlepseno=zlepseno,
                znamenkovy_test_p=round(float(binomtest(zlepseno, len(po)).pvalue), 3),
                nejvetsi_zhorseni=round(float((po.b - po.a).max()), 1),
                zacatek_a=round(float(z.get("a", np.nan)), 1), zacatek_b=round(float(z.get("b", np.nan)), 1),
                n_zacatek=int(q[q.zacatek & (q.varianta == "a")].shape[0]),
                povoden_2006={str(i): dict(a=round(float(r.a), 1), b=round(float(r.b), 1)) for i, r in p2006.iterrows()},
                po_povodnich={str(i): dict(a=round(float(r.a), 1), b=round(float(r.b), 1)) for i, r in po.iterrows()})
            print(f"+{h} h seed {s}: LOFO a {out[f'h{h}_s{s}']['lofo_a']} / b {out[f'h{h}_s{s}']['lofo_b']}, "
                  f"zlepšeno {zlepseno} z {len(po)}, začátek a {z.get('a', np.nan):.1f} / b {z.get('b', np.nan):.1f}", flush=True)
    (Path(adresar) / "lofo_sit.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return P, out


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--foldy", required=True)
    p.add_argument("--vystup", required=True)
    p.add_argument("--dil", default="1/1", help="i/n: tenhle kernel počítá každý n-tý fold od i-tého")
    p.add_argument("--horizonty", default="24")
    p.add_argument("--seedy", default="42")
    p.add_argument("--prace", type=int, default=4)
    p.add_argument("--jen-vyhodnot", action="store_true")
    a = p.parse_args()
    horizonty = [int(x) for x in a.horizonty.split(",")]
    seedy = [int(x) for x in a.seedy.split(",")]
    Path(a.vystup).mkdir(parents=True, exist_ok=True)
    if not a.jen_vyhodnot:
        F = nacti_foldy(a.foldy)
        i, n = (int(x) for x in a.dil.split("/"))
        seznam = []
        for h in horizonty:
            foldy = sorted(F[F.horizont == h].fold)
            seznam += [(v, s, h, k, a.foldy, a.vystup) for k in foldy if k % n == i - 1 for s in seedy for v in "ab"]
        print(f"díl {a.dil}: {len(seznam)} tréninků, {a.prace} souběžně", flush=True)
        t0 = time.time()
        with Pool(a.prace) as pool:
            for j, (u, sekund) in enumerate(pool.imap_unordered(trenuj, seznam), 1):
                print(f"[{j}/{len(seznam)} {time.time() - t0:.0f} s] {u} {sekund} s", flush=True)
    else:
        vyhodnot(a.vystup, horizonty, seedy)
