"""Leave-one-flood-out CV přes všech 22 povodní 2006–2020 (Děčín, vrchol nad 400 cm) se stejnými řádky pro všechny varianty.

Fold k: drží se okno povodně k (7 dní před až 5 dní po vrcholu, jako týmová metrika), z tréninku se vyřadí okno
± 20 dní; trénuje se na všem ostatním z let 2006–2020 (t + horizont < 2021, test se nepoužívá). Skóre varianty =
průměr chyby přes 22 povodní, k tomu chyby po povodních, kolik se jich proti základu zlepšilo (znaménkový test)
a největší zhoršení. Výběry uvnitř varianty (faktor, stanice) se dělají vnořeně: vnitřní leave-one-flood-out přes
zbylých 21 povodní jen v tréninku foldu k.

Rychlý Ridge: StandardScaler + Ridge(alpha) (= týmová pipeline po odmocnině průtoků) spočítaný ze součtů
n, Σx, Σy, Σxxᵀ, Σxy; součty tréninku foldu = celek − vyřazené okno, takže 22 × 21 vnitřních fitů stojí sekundy.
Shoda se sklearn ověřená v kontrola_sklearn().
"""
import os
import sys
from functools import cache
from pathlib import Path

os.environ.setdefault("OPENBLAS_NUM_THREADS", "4")
ZDE = Path(__file__).resolve().parent
sys.path[:0] = [str(ZDE.parents[1] / "src"), str(ZDE.parent), str(ZDE.parent / "stanice_vsem")]

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.stats import binomtest  # noqa: E402

import data_ridge  # noqa: E402
import hodnoceni as Hd  # noqa: E402
from evaluate import PO, PRED, casti, povodne, varovani  # noqa: E402
from features import ZPOZDENI_H, ZPOZDENI_Q, tabulka  # noqa: E402
from spolecne import NOVE  # noqa: E402

MEZERA = pd.Timedelta(days=20)
KONEC = pd.Timestamp("2021-01-01", tz="UTC")
NEJDELSI = 72  # nejdelší zpoždění, které některá varianta používá (pokus E); řádky jsou pro všechny stejné
CIL = "decin"
SKUPINY = {"ploucnice": ["benesov_pl", "struznice", "ceska_lipa"], "bilina": ["trmice"],
           "ohre_horni": ["zatec", "karlovy_vary"], "berounka_horni": ["zbecno", "liblin", "plzen", "plasy", "litavka"],
           "zbraslav": ["zbraslav"], "sazava_horni": ["kacov", "zruc"], "labe_horni": ["nemosice", "tyniste", "sany"],
           "jizera_horni": ["bakov"]}
DALEKE = SKUPINY["berounka_horni"] + SKUPINY["ohre_horni"] + SKUPINY["sazava_horni"] + ["nemosice", "tyniste"]


# ---------------------------------------------------------------- data a řádky

@cache
def zaklad(horizont):
    """Týmové vstupy X (98 sloupců, surové), y, společné řádky pro všechny varianty, H = stav Děčína (celá řada)."""
    X, y = tabulka(CIL, horizont)
    ok = (X.index + pd.Timedelta(hours=horizont) < KONEC) & (X.index >= X.index[0] + pd.Timedelta(hours=NEJDELSI))
    T = data_ridge.nacti()
    return X[ok], y[ok], T


def matice(horizont, nove=(), zpozdeni_nove=ZPOZDENI_Q, soucty=None, odmocnina=True):
    """Vstupy varianty jako float32 DataFrame na společných řádcích: týmových 98 (průtoky odmocněné jako v týmovém
    Ridge) + nové stanice se zpožděními zpozdeni_nove (dict stanice → zpoždění, nebo jedno pro všechny),
    nebo místo nich soucty = {skupina: [stanice]} → součet odmocnin průtoků skupiny se zpožděními ZPOZDENI_Q."""
    X, y, T = zaklad(horizont)
    q = np.sqrt if odmocnina else (lambda v: v)
    D = X.copy()
    qs = D.columns[D.columns.str.contains("_Q_")]
    D[qs] = q(D[qs].clip(lower=0))
    extra = {}
    for s in nove:
        zp = zpozdeni_nove[s] if isinstance(zpozdeni_nove, dict) else zpozdeni_nove
        for z in zp:
            extra[f"{s}_Q_{z}"] = q(T[f"{s}_Q"].clip(lower=0)).shift(z)
    for g, st in (soucty or {}).items():
        for z in ZPOZDENI_Q:
            extra[f"sum_{g}_Q_{z}"] = sum(np.sqrt(T[f"{s}_Q"].clip(lower=0)).shift(z) for s in st)
    if extra:
        D = pd.concat([D, pd.DataFrame(extra).reindex(D.index)], axis=1)
    assert D.notna().all().all(), "díra ve vstupech"
    return D.astype("float32"), y


@cache
def povodne_lofo(horizont):
    """22 vrcholů a pro každý okno (hodnocení) a mezeru (vyřazení z tréninku) jako boolean masky řádků."""
    X, y, _ = zaklad(horizont)
    vrcholy = povodne(y, 400)
    out = []
    for v in vrcholy:
        okno = (y.index >= v - PRED) & (y.index <= v + PO)
        mezera = (y.index >= v - PRED - MEZERA) & (y.index <= v + PO + MEZERA)
        out.append(dict(nazev=f"{v:%Y-%m-%d}", vrchol=v, okno=okno, mezera=mezera, vrchol_cm=int(y[v])))
    return out


# ---------------------------------------------------------------- rychlý Ridge ze součtů

def soucty(A, yv, maska, w=None):
    """n, Σx, Σy, Σxxᵀ, Σxy přes řádky masky (po kouscích ve float64, ať to nežere paměť)."""
    idx = np.flatnonzero(maska)
    p = A.shape[1]
    n, sx, sy, sxx, sxy = 0.0, np.zeros(p), 0.0, np.zeros((p, p)), np.zeros(p)
    for i in range(0, len(idx), 20000):
        b = idx[i:i + 20000]
        Xb = A[b].astype(np.float64)
        yb = yv[b]
        n += len(b)
        sx += Xb.sum(0)
        sy += yb.sum()
        sxx += Xb.T @ Xb
        sxy += Xb.T @ yb
    return [n, sx, sy, sxx, sxy]


def minus(a, b):
    return [x - y for x, y in zip(a, b)]


def standardizuj(S):
    n, sx, sy, sxx, sxy = S
    mu, ym = sx / n, sy / n
    var = np.diag(sxx) / n - mu ** 2
    sd = np.sqrt(np.clip(var, 0, None))
    sd[sd == 0] = 1
    Gs = (sxx - n * np.outer(mu, mu)) / np.outer(sd, sd)
    bs = (sxy - n * mu * ym) / sd
    return mu, sd, ym, Gs, bs


def ridge_z_souctu(St, alpha=1.0, pen=None, sloupce=None):
    """Koeficienty StandardScaler + Ridge(alpha) z (už standardizovaných) součtů St; pen = násobky penalizace."""
    mu, sd, ym, Gs, bs = St
    i = np.arange(len(mu)) if sloupce is None else np.asarray(sloupce)
    P = np.ones(len(i)) if pen is None else np.asarray(pen)[i]
    k = np.linalg.solve(Gs[np.ix_(i, i)] + alpha * np.diag(P), bs[i])
    return i, mu[i], sd[i], k, ym  # vstupy se při předpovědi centrují, absolutní člen je průměr y


def predikuj(koef, A_okno):
    i, mu, sd, k, b0 = koef
    return ((A_okno[:, i].astype(np.float64) - mu) / sd) @ k + b0


class Motor:
    """Předpočítané součty pro jednu matici vstupů A (numpy float32) a cíl y na společných řádcích."""

    def __init__(self, A, y, horizont):
        self.A, self.y, self.h = A, np.asarray(y, dtype=np.float64), horizont
        self.pov = povodne_lofo(horizont)
        vse = np.ones(len(self.y), bool)
        self.S_vse = soucty(self.A, self.y, vse)
        self.S_mez = [soucty(self.A, self.y, p["mezera"]) for p in self.pov]
        self._vnitrni = {}

    def trenink(self, k):
        """Standardizované součty tréninku foldu k (vše bez mezery k)."""
        return standardizuj(minus(self.S_vse, self.S_mez[k]))

    def vnitrni(self, k, j):
        """Trénink vnitřního foldu (k, j): bez mezer k i j."""
        if (k, j) not in self._vnitrni:
            pk, pj = self.pov[k]["mezera"], self.pov[j]["mezera"]
            jen_j = soucty(self.A, self.y, pj & ~pk)
            self._vnitrni[(k, j)] = standardizuj(minus(minus(self.S_vse, self.S_mez[k]), jen_j))
        return self._vnitrni[(k, j)]

    def okno(self, k):
        return self.A[self.pov[k]["okno"]], self.y[self.pov[k]["okno"]]

    def okno_vnitrni(self, k, j):
        """Okno vnitřní povodně j bez hodin v mezeře vnějšího foldu k (blízké povodně se překrývají, např.
        12/2012 a 1/2013 o 48 h; ty hodiny se při výběru pro fold k nesmí použít)."""
        m = self.pov[j]["okno"] & ~self.pov[k]["mezera"]
        return self.A[m], self.y[m]

    def vnitrni_skore(self, k, alpha=1.0, pen=None, sloupce=None):
        """Průměrná chyba přes vnitřní povodně j ≠ k (jen hodiny mimo mezeru k), každá z modelu bez mezer k a j."""
        e = []
        for j in range(len(self.pov)):
            if j == k:
                continue
            A_o, y_o = self.okno_vnitrni(k, j)
            if len(y_o) == 0:
                continue
            e.append(np.abs(predikuj(ridge_z_souctu(self.vnitrni(k, j), alpha, pen, sloupce), A_o) - y_o).mean())
        return float(np.mean(e))

    def lofo(self, vyber=None, alpha=1.0, pen=None, sloupce=None):
        """Předpovědi oken všech 22 povodní. vyber(motor, k) → dict(alpha, pen, sloupce) vnořeně pro fold k."""
        pred, volby = [], []
        for k in range(len(self.pov)):
            v = dict(alpha=alpha, pen=pen, sloupce=sloupce) | (vyber(self, k) if vyber else {})
            A_o, _ = self.okno(k)
            pred.append(predikuj(ridge_z_souctu(self.trenink(k), v["alpha"], v["pen"], v["sloupce"]), A_o))
            volby.append({kk: vv for kk, vv in v.items() if kk != "pen" or vv is None})
        return pred, volby


# ---------------------------------------------------------------- obecný model (LightGBM, Huber, …)

def lofo_obecne(fit, X, y, horizont, cil=CIL):
    """fit(X_tr, y_tr, cil, horizont) → predict; vrátí předpovědi oken 22 povodní."""
    pov = povodne_lofo(horizont)
    pred = []
    for p in pov:
        tr = ~p["mezera"]
        predict = fit(X[tr], y[tr], cil, horizont)
        pred.append(np.asarray(predict(X[p["okno"]]), dtype=float))
    return pred


# ---------------------------------------------------------------- hodnocení

def skore(pred, horizont, zaklad_pred=None):
    """Chyby po povodních, průměr, a proti základu: rozdíl, kolik zlepšených, největší zhoršení, znaménkový test.
    Navíc z předpovědí oken: začátek vzestupu, povodeň 2006, propásnuté a plané poplachy 2. a 3. SPA."""
    X, y, T = zaklad(horizont)
    pov = povodne_lofo(horizont)
    e = np.array([np.abs(pr - y[p["okno"]].to_numpy()).mean() for pr, p in zip(pred, pov)])
    out = dict(lofo=round(float(e.mean()), 2), po_povodnich={p["nazev"]: round(float(x), 1) for p, x in zip(pov, e)})
    # spojená řada předpovědí: řádek ve dvou oknech bere předpověď foldu s bližším vrcholem
    ser = pd.Series(np.nan, index=y.index)
    vzd = pd.Series(np.inf, index=y.index)
    for pr, p in zip(pred, pov):
        idx = y.index[p["okno"]]
        d = np.abs((idx - p["vrchol"]) / pd.Timedelta(hours=1))
        lepsi = d < vzd[idx].to_numpy()
        ser[idx[lepsi]] = pr[lepsi]
        vzd[idx[lepsi]] = d[lepsi]
    v_oknech = ser.notna()
    yy, pp = y[v_oknech], ser[v_oknech]
    H = T[f"{CIL}_H"]
    ted = H.reindex(yy.index)
    zac = ((yy - ted) >= 50) & ((ted - H.shift(6).reindex(yy.index)) < 10)
    out |= dict(zacatek=round(float((pp - yy)[zac].abs().mean()), 1), n_zacatek=int(zac.sum()),
                povoden_2006=out["po_povodnich"]["2006-04-02"] if "2006-04-02" in out["po_povodnich"] else None)
    for n, prah in ((2, 490), (3, 560)):
        v = varovani(yy, pp, prah, horizont)
        out |= {f"spa{n}_propasnuto": v["propasnuto"], f"spa{n}_plane": v["plane_poplachy"]}
    if zaklad_pred is not None:
        z = np.array([np.abs(pr - y[p["okno"]].to_numpy()).mean() for pr, p in zip(zaklad_pred, pov)])
        d = e - z
        lepsi = int((d < 0).sum())
        out |= dict(rozdil=round(float(d.mean()), 2), zlepseno=lepsi, zhorseno=int((d > 0).sum()),
                    nejhorsi_zhorseni=round(float(d.max()), 1),
                    znamenkovy_p=round(float(binomtest(lepsi, int((d != 0).sum()), 0.5).pvalue), 4),
                    splnuje=bool(d.mean() <= -1.0 and lepsi > len(d) / 2 and d.max() <= 10.0))
    return out


def validace_ridge(A, y, horizont, alpha=1.0, pen=None, sloupce=None, vyber_val=None):
    """Týmové rozdělení (train → val), Děčín: mae_povodne, začátek vzestupu, poplachy (hodnoceni.metriky).
    vyber_val(motor_val, maska_train) → dict voleb vnořeně jen z tréninku (vnitřní LOFO přes jeho povodně)."""
    X, yfull, T = zaklad(horizont)
    c = casti(CIL, horizont).reindex(X.index)
    tr, ev = (c == "train").to_numpy(), (c == "val").to_numpy()
    v = dict(alpha=alpha, pen=pen, sloupce=sloupce) | (vyber_val(A, y, tr, horizont) if vyber_val else {})
    St = standardizuj(soucty(A, np.asarray(y, dtype=np.float64), tr))
    pr = predikuj(ridge_z_souctu(St, v["alpha"], v["pen"], v["sloupce"]), A[ev])
    yy = yfull[ev]
    m = Hd.metriky(yy, pd.Series(pr, index=yy.index), T[f"{CIL}_H"], CIL, horizont)
    return {k: m[k] for k in ("mae_povodne", "mae_zacatek", "spa2_plane_poplachy", "spa3_plane_poplachy",
                              "spa2_propasnuto", "spa3_propasnuto", "spa2_predstih_h")} | povoden_2006_val(yy, pr), v


def povoden_2006_val(yy, pr):
    from spolecne import povoden_2006
    return povoden_2006(yy, pr, None)


def kontrola_sklearn(horizont=24):
    """Rychlý Ridge = týmový ridge.fit (sklearn) na foldu 2006: největší rozdíl předpovědí v cm."""
    from models import ridge
    X, y, T = zaklad(horizont)
    A, _ = matice(horizont)
    m = Motor(A.to_numpy(), y, horizont)
    k = 0
    p_rych = predikuj(ridge_z_souctu(m.trenink(k)), m.okno(k)[0])
    tr = ~m.pov[k]["mezera"]
    p_sk = np.asarray(ridge.fit(X[tr], y[tr], CIL, horizont)(X[m.pov[k]["okno"]]))
    return float(np.abs(p_rych - p_sk).max())


def cekej_na_ram(mb=1500, max_min=20):
    """Před těžkým výpočtem počká, až bude volné RAM aspoň mb (víc běhů najednou se tak samo rozloží)."""
    import subprocess
    import time
    for _ in range(max_min * 4):
        out = subprocess.run(["powershell", "-NoProfile", "-Command",
                              "[int]((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1024)"],
                             capture_output=True, text=True).stdout.strip()
        if out.isdigit() and int(out) >= mb:
            return int(out)
        time.sleep(15)
    return None


def vnitrni_val(A, y, tr, horizont=24):
    """Pro vnořený výběr na týmovém splitu (validace): vnitřní LOFO přes tréninkové povodně (okno celé v tréninku).
    Vrací [(standardizované součty bez mezery j, vstupy okna j, y okna j)]."""
    yv = np.asarray(y, dtype=np.float64)
    S_tr = soucty(A, yv, tr)
    out = []
    for p in povodne_lofo(horizont):
        okno = p["okno"] & tr
        if okno.sum() < 0.9 * p["okno"].sum():
            continue  # validační povodně (mimo trénink)
        out.append((standardizuj(minus(S_tr, soucty(A, yv, tr & p["mezera"]))), A[okno], yv[okno]))
    return out


def skore_vnitrni_val(vnitrni, alpha=1.0, pen=None, sloupce=None):
    return float(np.mean([np.abs(predikuj(ridge_z_souctu(St, alpha, pen, sloupce), Ao) - yo).mean()
                          for St, Ao, yo in vnitrni]))
