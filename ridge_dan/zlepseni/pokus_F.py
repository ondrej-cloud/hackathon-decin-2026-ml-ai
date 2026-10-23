"""Pokus F: Ridge s Huberovou ztrátou místo čtverců (IRLS), týmové vstupy (F12) a 30 stanic (F30).

StandardScaler bez vah (μ, sd z tréninku foldu, jako týmová pipeline), pak vážený Ridge(alpha 1) jako sklearn
Ridge se sample_weight. Váhy w = min(1, δ/|r|), δ = 1,345·s, s = 1,4826·MAD reziduí, přepočítané v každé iteraci,
start z obyčejného Ridge, nejvýš 10 iterací. Nic se neladí, takže není co vnořovat.
python pokus_F.py
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, r"C:\Users\danie\Documents\hackathon-2026-ridge\ridge_dan\zlepseni")
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import lofo as L  # noqa: E402

ZDE = Path(__file__).resolve().parent
ALPHA, ITERACI, KUS = 1.0, 10, 20000  # konvergence: změna koeficientů < 1e-3


def meritko(A, idx):
    """μ a sd tréninkových řádků bez vah (StandardScaler)."""
    n, sx, sxx = 0, np.zeros(A.shape[1]), np.zeros(A.shape[1])
    for i in range(0, len(idx), KUS):
        Xb = A[idx[i:i + KUS]].astype(np.float64)
        n += len(Xb)
        sx += Xb.sum(0)
        sxx += (Xb ** 2).sum(0)
    mu = sx / n
    sd = np.sqrt(np.clip(sxx / n - mu ** 2, 0, None))
    sd[sd == 0] = 1
    return mu, sd


def vazeny_ridge(A, y, idx, mu, sd, w):
    """sklearn Ridge(alpha, sample_weight=w) na standardizovaných řádcích idx, ze součtů po kouscích."""
    p = A.shape[1]
    W, szw, syw = w.sum(), np.zeros(p), (w * y[idx]).sum()
    G, b = np.zeros((p, p)), np.zeros(p)
    for i in range(0, len(idx), KUS):
        Zb = np.ascontiguousarray((A[idx[i:i + KUS]].astype(np.float64) - mu) / sd)
        wb, yb = w[i:i + KUS], y[idx[i:i + KUS]]
        szw += wb @ Zb
        M = Zb * np.sqrt(wb)[:, None]
        G += M.T @ M
        b += Zb.T @ (wb * yb)
    zw, yw = szw / W, syw / W
    Gc = G - W * np.outer(zw, zw)
    bc = b - W * zw * yw
    beta = np.linalg.solve(Gc + ALPHA * np.eye(p), bc)
    return beta, yw - zw @ beta


def predikce(A, idx, mu, sd, beta, b0):
    out = np.empty(len(idx))
    for i in range(0, len(idx), KUS):
        out[i:i + KUS] = ((A[idx[i:i + KUS]].astype(np.float64) - mu) / sd) @ beta + b0
    return out


def huber_fit(A, y, idx, info=None):
    """IRLS; standardizované řádky foldu se drží v paměti ve float64 (Gram jedním voláním BLAS)."""
    mu, sd = meritko(A, idx)
    Z = np.empty((len(idx), A.shape[1]), dtype=np.float64)
    for i in range(0, len(idx), KUS):
        Z[i:i + KUS] = (A[idx[i:i + KUS]].astype(np.float64) - mu) / sd
    yt = y[idx]
    p = Z.shape[1]

    def fit_w(w):
        W = w.sum()
        zw = (w @ Z) / W
        yw = (w * yt).sum() / W
        M = Z * np.sqrt(w)[:, None]
        G = M.T @ M - W * np.outer(zw, zw)
        del M
        bb = Z.T @ (w * yt) - W * zw * yw
        beta = np.linalg.solve(G + ALPHA * np.eye(p), bb)
        return beta, yw - zw @ beta

    w = np.ones(len(idx))
    beta, b0 = fit_w(w)
    start = (beta.copy(), b0)
    for it in range(ITERACI):
        r = yt - (Z @ beta + b0)
        s = 1.4826 * np.median(np.abs(r - np.median(r)))
        delta = 1.345 * s
        w = np.minimum(1.0, delta / np.maximum(np.abs(r), 1e-12))
        beta_n, b0_n = fit_w(w)
        zmena = np.max(np.abs(beta_n - beta))
        beta, b0 = beta_n, b0_n
        if zmena < 1e-3:
            break
    if info is not None:
        info.update(iteraci=it + 1, delta=float(delta), podil_srazenych=float((w < 1).mean()), start=start, mu=mu, sd=sd, w=w)
    return mu, sd, beta, b0


def kontrola(A, y):
    """Fold 0: (a) start IRLS = obyčejný Ridge z motoru, (b) vážený Ridge = sklearn se sample_weight."""
    from sklearn.linear_model import Ridge
    p = L.povodne_lofo(24)[0]
    idx = np.flatnonzero(~p["mezera"])
    okno = np.flatnonzero(p["okno"])
    info = {}
    mu, sd, beta, b0 = huber_fit(A, y, idx, info)
    m = L.Motor(A, y, 24)
    p_motor = L.predikuj(L.ridge_z_souctu(m.trenink(0)), m.okno(0)[0])
    p_start = predikce(A, okno, mu, sd, *info["start"])
    Xs = (A[idx].astype(np.float64) - mu) / sd
    sk = Ridge(alpha=ALPHA).fit(Xs, y[idx], sample_weight=info["w"])
    del Xs
    Xo = (A[okno].astype(np.float64) - mu) / sd
    # konečná IRLS předpověď proti sklearn se stejnými konečnými vahami
    p_irls = Xo @ beta + b0
    beta_w, b0_w = vazeny_ridge(A, y, idx, mu, sd, info["w"])
    return dict(start_vs_motor=float(np.abs(p_start - p_motor).max()),
                vazeny64_vs_sklearn=float(np.abs(Xo @ beta_w + b0_w - sk.predict(Xo)).max()),
                irls_vs_sklearn=float(np.abs(p_irls - sk.predict(Xo)).max()),
                iteraci=info["iteraci"], delta_cm=round(info["delta"], 2), podil_srazenych=round(info["podil_srazenych"], 3))


def lofo_huber(A, y):
    pred, info = [], []
    for p in L.povodne_lofo(24):
        idx = np.flatnonzero(~p["mezera"])
        i = {}
        mu, sd, beta, b0 = huber_fit(A, y, idx, i)
        pred.append(predikce(A, np.flatnonzero(p["okno"]), mu, sd, beta, b0))
        info.append(dict(povoden=p["nazev"], iteraci=i["iteraci"], delta_cm=round(i["delta"], 2),
                         podil_srazenych=round(i["podil_srazenych"], 3)))
    return pred, info


def validace_huber(A, y):
    X, yfull, T = L.zaklad(24)
    c = L.casti(L.CIL, 24).reindex(X.index)
    tr, ev = np.flatnonzero((c == "train").to_numpy()), np.flatnonzero((c == "val").to_numpy())
    mu, sd, beta, b0 = huber_fit(A, y, tr)
    pr = predikce(A, ev, mu, sd, beta, b0)
    yy = yfull.iloc[ev]
    m = L.Hd.metriky(yy, pd.Series(pr, index=yy.index), T[f"{L.CIL}_H"], L.CIL, 24)
    return {k: m[k] for k in ("mae_povodne", "mae_zacatek", "spa2_plane_poplachy", "spa3_plane_poplachy",
                              "spa2_propasnuto", "spa3_propasnuto", "spa2_predstih_h")} | L.povoden_2006_val(yy, pr)


def jsonable(o):
    if isinstance(o, dict):
        return {k: jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, (np.floating, np.integer, np.bool_)):
        return o.item()
    return o


if __name__ == "__main__":
    t0 = time.time()
    print("RAM volno", L.cekej_na_ram(1500), flush=True)
    A12, y = L.matice(24)
    A12 = A12.to_numpy()
    yv = np.asarray(y, dtype=np.float64)
    print("kontrola (fold 0, 12 stanic):", kontrola(A12, yv), round(time.time() - t0), "s", flush=True)
    m12 = L.Motor(A12, yv, 24)
    p12, _ = m12.lofo()
    vysl = []
    for nazev, nove in (("F12_huber_12", ()), ("F30_huber_30", L.NOVE)):
        L.cekej_na_ram(1500)
        A = A12 if not nove else L.matice(24, nove=nove)[0].to_numpy()
        pred, info = lofo_huber(A, yv)
        s = L.skore(pred, 24, zaklad_pred=p12)
        v = validace_huber(A, yv)
        z = dict(nazev=nazev, popis=f"Ridge s Huberovou ztrátou (IRLS, δ = 1,345·MAD), {'30' if nove else '12'} stanic",
                 **s, val=v, irls=info)
        vysl.append(z)
        print(nazev, {k: z[k] for k in ("lofo", "rozdil", "zlepseno", "nejhorsi_zhorseni", "splnuje", "zacatek",
                                         "povoden_2006", "spa2_plane")}, "val", v["mae_povodne"], round(time.time() - t0), "s", flush=True)
        (ZDE / "vysledky_F.json").write_text(json.dumps(jsonable(vysl), ensure_ascii=False, indent=1), encoding="utf-8")
        del A
    # pro srovnání obyčejný Ridge 30 (stejné skóre jako v ZLEPSENI.md)
    A30 = L.matice(24, nove=L.NOVE)[0].to_numpy()
    p30, _ = L.Motor(A30, yv, 24).lofo()
    s30 = L.skore(p30, 24, zaklad_pred=p12)
    print("ridge_30 (čtverce)", {k: s30[k] for k in ("lofo", "rozdil", "zlepseno", "nejhorsi_zhorseni")}, flush=True)
    vysl.append(dict(nazev="ridge_30_ctverce_pro_srovnani", **s30))
    vysl.insert(0, dict(nazev="ridge_12_zaklad", **L.skore(p12, 24)))
    (ZDE / "vysledky_F.json").write_text(json.dumps(jsonable(vysl), ensure_ascii=False, indent=1), encoding="utf-8")
    print("hotovo", round(time.time() - t0), "s")
