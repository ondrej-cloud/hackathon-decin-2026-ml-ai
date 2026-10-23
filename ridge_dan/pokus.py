"""Spouští pokusy s Ridge pro Děčín +24 h a zapisuje je do vysledky/pokusy.jsonl.

python pokus.py <nazev> [<nazev> ...]          jen časová křížová validace uvnitř tréninku (hlavní kritérium)
python pokus.py <nazev> --val                  navíc validace (střídmě, počet nahlédnutí se počítá)
Pokusy (nazev → volby) jsou v POKUSY níž. Test se tady spustit nedá, na ten je test_jednou.py.
"""
import os

os.environ.setdefault("OPENBLAS_NUM_THREADS", "4")  # 22 vláken se na sdíleném notebooku přetahuje, 4× pomalejší

import argparse  # noqa: E402
import json  # noqa: E402
import time  # noqa: E402
from datetime import datetime
from functools import cache
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

import data_ridge
import hodnoceni as Hd
from priznaky import priznaky, tym_priznaky
from stanice import HYDRO, TYM

ZDE = Path(__file__).resolve().parent
LOG = ZDE / "vysledky/pokusy.jsonl"
CIL, HORIZONT = "decin", 24
ALPHY = (0.01, 0.1, 1, 3, 10, 30, 100, 300, 1000)


class Krivka(BaseEstimator, TransformerMixin):
    """Měrná křivka Děčína (průtok → stav) z tréninkových řádků: medián stavu v úzkých pásmech log průtoku.

    Sloupce krivka_* (součty průtoků proti proudu) převede na „stav, jaký by v Děčíně odpovídal tomuto průtoku“.
    Sloupec decin_Qsurovy_0 slouží jen k fitu a ven nejde.
    """

    def fit(self, X, y=None):
        q, h = np.log(X["decin_Qsurovy_0"].clip(lower=1)), X["decin_H_0"]
        hrany = np.quantile(q, np.linspace(0, 1, 201))
        pas = np.clip(np.searchsorted(hrany, q) - 1, 0, 199)
        g = pd.DataFrame({"q": q.to_numpy(), "h": h.to_numpy(), "p": pas}).groupby("p").median()
        self.q_, self.h_ = g.q.to_numpy(), np.maximum.accumulate(g.h.to_numpy())
        # nad nejvyšším průtokem v tréninku prodloužit přímkou v log průtoku podle horních 10 % křivky
        k = max(len(self.q_) // 10, 2)
        self.sklon_ = np.polyfit(self.q_[-k:], self.h_[-k:], 1)[0]
        return self

    def stav(self, q):
        """Průtok (m3/s) → stav (cm) podle křivky, nad rozsahem tréninku přímka v log průtoku."""
        lq = np.log(np.clip(q, 1, None))
        h = np.interp(lq, self.q_, self.h_)
        nad = lq > self.q_[-1]
        h[nad] = self.h_[-1] + self.sklon_ * (lq[nad] - self.q_[-1])
        return h

    def prutok(self, h):
        """Opak stav(): stav (cm) → průtok (m3/s)."""
        h = np.asarray(h, dtype=float)
        lq = np.interp(h, self.h_, self.q_)
        nad = h > self.h_[-1]
        lq[nad] = self.q_[-1] + (h[nad] - self.h_[-1]) / self.sklon_
        return np.exp(lq)

    def transform(self, X):
        X = X.drop(columns=["decin_Qsurovy_0"]).copy()
        for c in X.columns[X.columns.str.startswith("krivka_")]:
            q = np.log(X[c].clip(lower=1)).to_numpy()
            h = np.interp(q, self.q_, self.h_)
            nad = q > self.q_[-1]
            h[nad] = self.h_[-1] + self.sklon_ * (q[nad] - self.q_[-1])
            X[c] = h
        return X


class Brzda(BaseEstimator, TransformerMixin):
    """Po standardizaci vynásobí sloupce vybraných stanic 1/k: Ridge je pak u nich penalizuje k² víc."""

    def __init__(self, nasob):
        self.nasob = nasob

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X * self.nasob


def nasobky_brzdy(sloupce, brzda):
    """brzda = (k, [stanice]) → vektor násobků 1/k pro sloupce těch stanic, jinak 1."""
    k, stanice = brzda
    return np.array([1 / k if any(c.startswith(f"{s}_") for s in stanice) else 1.0 for c in sloupce])


def model(alpha, krivka=False, nasob=None):
    kroky = ([Krivka()] if krivka else []) + [StandardScaler()] + ([Brzda(nasob)] if nasob is not None else [])
    return make_pipeline(*kroky, Ridge(alpha=alpha))


class Predpoved:
    """Natrénovaný model: vstupy podle voleb → hladina v cm. Stejné rozhraní jako týmové modely (predict(X))."""

    def __init__(self, alpha, zmena, vahy, prutok=False, brzda=None):
        self.alpha, self.zmena, self.vahy, self.prutok, self.brzda = alpha, zmena, vahy, prutok, brzda

    def fit(self, X, y):
        ted = X[f"{CIL}_H_0"].to_numpy()
        cil = y.to_numpy() - ted if self.zmena else y.to_numpy()
        w = None
        if self.vahy:
            # řádky, kdy hladina za 24 h stoupne aspoň o 50 cm, mají větší váhu
            w = np.where(y.to_numpy() - ted >= 50, self.vahy, 1.0)
        if self.prutok:
            # model se učí průtok v Děčíně za 24 h (průtoky se sčítají), na stav ho převede měrná křivka z tréninku
            self.krivka = Krivka().fit(X)
            cil = self.krivka.prutok(y.to_numpy())
        sl = [c for c in X.columns if c != "decin_Qsurovy_0"]
        nasob = nasobky_brzdy(sl, self.brzda) if self.brzda else None
        self.m = model(self.alpha, "decin_Qsurovy_0" in X, nasob).fit(X, cil, ridge__sample_weight=w)
        self.sloupce = list(X.columns)
        return self

    def predict(self, X):
        p = self.m.predict(X[self.sloupce])
        if self.prutok:
            return self.krivka.stav(p)
        return p + X[f"{CIL}_H_0"].to_numpy() if self.zmena else p


MODEL_VOLBY = ("alpha", "zmena", "vahy", "prutok", "brzda")


def pripravit(volby):
    T = data_ridge.nacti()
    if volby.get("tym"):
        X, y, L = tym_priznaky(T, CIL, HORIZONT)
    else:
        X, y, L = priznaky(T, CIL, HORIZONT, **{k: v for k, v in volby.items() if k not in MODEL_VOLBY})
    c = Hd.casti(T[f"{CIL}_H"], HORIZONT, max(L, 36)).reindex(X.index)
    return T, X, y, c


def cv(X, y, c, alpha, zmena=False, vahy=None):
    """Bloky let uvnitř tréninku. Hlavní číslo cv_povodne = průměr přes povodně (vrchol nad 400 cm) chyby v okně
    7 dní před až 5 dní po vrcholu; každá povodeň má stejnou váhu, ať výsledek neurčuje jen červen 2013."""
    tr = c == "train"
    Xt, yt = X[tr], y[tr]
    pred = pd.Series(np.nan, index=yt.index)
    udalosti = {}
    for nazev, f_tr, f_drz in Hd.bloky_cv(Xt.index):
        m = Predpoved(alpha, zmena, vahy).fit(Xt[f_tr], yt[f_tr])
        pred[f_drz] = m.predict(Xt[f_drz])
        yy, e = yt[f_drz], (pred[f_drz] - yt[f_drz]).abs()
        for v in Hd.E.povodne(yy, 400):
            udalosti[f"{v:%Y-%m-%d}"] = e[v - Hd.E.PRED: v + Hd.E.PO].mean()
    ted = Xt[f"{CIL}_H_0"]
    vz = (yt - ted) >= 50
    e = (pred - yt).abs()
    return dict(cv_povodne=round(float(np.mean(list(udalosti.values()))), 2), cv_mae=round(e.mean(), 2),
                cv_vzestup=round(e[vz].mean(), 2), cv_bias_vzestup=round((pred - yt)[vz].mean(), 2),
                cv_udalosti={k: round(v, 1) for k, v in udalosti.items()})


def _koeficienty(X, y, w, alphy, pen=None):
    """Totéž co StandardScaler + Ridge(alpha, sample_weight=w) ze sklearn, ale pro všechny alphy z jedné matice.
    pen: násobky penalizace pro jednotlivé sloupce (brzda), jinak všude 1."""
    X = np.asarray(X, dtype=np.float64)
    mu, sd = X.mean(0), X.std(0)
    sd[sd == 0] = 1
    Xs = (X - mu) / sd
    w = np.ones(len(y)) if w is None else w
    xw, yw = (w @ Xs) / w.sum(), (w @ y) / w.sum()
    Z = (Xs - xw) * np.sqrt(w)[:, None]
    G = Z.T @ Z  # stejné rozložení v paměti u obou činitelů, jinak je numpy tady 100× pomalejší
    b = Z.T @ (np.sqrt(w) * (y - yw))
    out = {}
    for a in alphy:
        k = np.linalg.solve(G + a * np.diag(np.ones(len(G)) if pen is None else pen), b)
        out[a] = (mu, sd, k, yw - xw @ k)
    return out


def okna_povodni(yt):
    """Pro každý držený blok a povodeň (vrchol nad 400 cm) pozice řádků v okně 7 dní před až 5 dní po vrcholu."""
    okna = {}
    for _, _, f_drz in Hd.bloky_cv(yt.index):
        yy = yt[f_drz]
        for v in Hd.E.povodne(yy, 400):
            v_okne = np.asarray(f_drz) & (yt.index >= v - Hd.E.PRED) & (yt.index <= v + Hd.E.PO)
            okna[f"{v:%Y-%m-%d}"] = np.flatnonzero(v_okne)
    return okna


def cv_alphy(X, y, c, zmena=False, vahy=None, alphy=ALPHY, prutok=False, brzda=None):
    """Rychlá varianta cv() pro celou mřížku alph, stejné výsledky jako StandardScaler + Ridge ze sklearn."""
    tr = c == "train"
    Xt, yt = X[tr], y[tr]
    ted = Xt[f"{CIL}_H_0"].to_numpy()
    cil = yt.to_numpy() - ted if zmena else yt.to_numpy()
    w_vse = np.where(yt.to_numpy() - ted >= 50, vahy, 1.0) if vahy else None
    pred = {a: pd.Series(np.nan, index=yt.index) for a in alphy}
    for _, f_tr, f_drz in Hd.bloky_cv(Xt.index):
        Xa, Xb = Xt[f_tr], Xt[f_drz]
        f_tr_np = np.asarray(f_tr)
        cil_a = cil[f_tr_np]
        if "decin_Qsurovy_0" in X:
            k = Krivka().fit(Xa)
            Xa, Xb = k.transform(Xa), k.transform(Xb)
            if prutok:
                cil_a = k.prutok(yt.to_numpy()[f_tr_np])
        pen = nasobky_brzdy(Xa.columns, brzda) ** -2 if brzda else None
        koef = _koeficienty(Xa, cil_a, None if w_vse is None else w_vse[f_tr_np], alphy, pen)
        Xb_np = np.asarray(Xb, dtype=np.float64)
        for a, (mu, sd, k_, b0) in koef.items():
            p_ = ((Xb_np - mu) / sd) @ k_ + b0
            if prutok:
                p_ = k.stav(p_)
            pred[a][f_drz] = p_ + ted[np.asarray(f_drz)] if zmena else p_
    vz = ((yt - Xt[f"{CIL}_H_0"]) >= 50).to_numpy()
    okna = okna_povodni(yt)
    y_np = yt.to_numpy()
    radky = {}
    for a in alphy:
        p_np = pred[a].to_numpy()
        e = np.abs(p_np - y_np)
        udalosti = {k: e[pos].mean() for k, pos in okna.items()}
        velke = [udalosti[k] for k, pos in okna.items() if y_np[pos].max() >= 490]
        radky[a] = dict(cv_povodne=round(float(np.mean(list(udalosti.values()))), 2), cv_mae=round(e.mean(), 2),
                        cv_povodne_presne=float(np.mean(list(udalosti.values()))),
                        cv_velke=round(float(np.mean(velke)), 2),
                        cv_vzestup=round(e[vz].mean(), 2), cv_bias_vzestup=round((p_np - y_np)[vz].mean(), 2),
                        cv_udalosti={k: round(v, 1) for k, v in udalosti.items()})
    return radky, pred


def nejlepsi_alpha(X, y, c, zmena=False, vahy=None, alphy=ALPHY, prutok=False, brzda=None):
    radky, _ = cv_alphy(X, y, c, zmena, vahy, alphy, prutok, brzda)
    # z nezaokrouhlených hodnot; co je do 0,01 cm od nejlepší, bere se ta největší alpha (víc regularizace)
    nej = min(r["cv_povodne_presne"] for r in radky.values())
    a = max(a for a, r in radky.items() if r["cv_povodne_presne"] <= nej + 0.01)
    return a, radky


def validace(T, X, y, c, alpha, zmena=False, vahy=None, prutok=False, brzda=None):
    tr, ev = c == "train", c == "val"
    m = Predpoved(alpha, zmena, vahy, prutok, brzda).fit(X[tr], y[tr])
    pred = pd.Series(m.predict(X[ev]), index=X.index[ev])
    return m, pred


@cache
def tym_val():
    """Týmový Ridge (stejné vstupy a nastavení jako src/models/ridge.py, alpha 1) na vlastní tabulce, val řádky."""
    T, X, y, c = pripravit(dict(tym=True))
    _, pred = validace(T, X, y, c, 1.0)
    return pred, X.loc[pred.index, f"{CIL}_H_0"], y[pred.index]


def srovnani(T, y, pred):
    """Můj model, týmový Ridge a „jako teď“ na STEJNÝCH řádcích (průnik val řádků obou modelů)."""
    p_tym, ted, y_tym = tym_val()
    spol = pred.index.intersection(p_tym.index)
    H = T[f"{CIL}_H"]
    return dict(radku=len(spol), radku_moje=len(pred), radku_tym=len(p_tym),
                moje=Hd.metriky(y[spol], pred[spol], H, CIL, HORIZONT),
                tym=Hd.metriky(y_tym[spol], p_tym[spol], H, CIL, HORIZONT),
                jako_ted=Hd.metriky(y_tym[spol], ted[spol], H, CIL, HORIZONT))


@cache
def otisk():
    """Commit, ze kterého se pouští, příznak neuložených změn v ridge_dan/ a otisk tabulky."""
    import hashlib
    import subprocess
    git = lambda *a: subprocess.run(["git", *a], capture_output=True, text=True, cwd=ZDE).stdout.strip()  # noqa: E731
    return dict(commit=git("rev-parse", "--short", "HEAD"), zmeny=bool(git("status", "--porcelain", "--", ".")),
                tabulka=hashlib.sha1(data_ridge.SOUBOR.read_bytes()).hexdigest()[:8],
                evaluate=Hd.OTISK_EVALUATE[:8])


def zapis(zaznam):
    LOG.parent.mkdir(exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(zaznam, ensure_ascii=False, default=str) + "\n")


def pocet_val():
    if not LOG.exists():
        return 0
    return sum(1 for r in LOG.read_text(encoding="utf-8").splitlines() if json.loads(r).get("val"))


def spust(nazev, volby, s_val=False):
    t0 = time.time()
    T, X, y, c = pripravit(volby)
    zmena, vahy, prutok = volby.get("zmena", False), volby.get("vahy"), volby.get("prutok", False)
    brzda = volby.get("brzda")
    if "alpha" in volby:
        alpha, radky = volby["alpha"], cv_alphy(X, y, c, zmena, vahy, (volby["alpha"],), prutok, brzda)[0]
    else:
        alpha, radky = nejlepsi_alpha(X, y, c, zmena, vahy, prutok=prutok, brzda=brzda)
    z = dict(cas=datetime.now().isoformat(timespec="seconds"), nazev=nazev, volby=volby, otisk=otisk(), sloupcu=X.shape[1],
             radku_train=int((c == "train").sum()), alpha=alpha, **radky[alpha],
             cv_alphy={a: r["cv_povodne"] for a, r in radky.items()})
    if s_val:
        _, pred = validace(T, X, y, c, alpha, zmena, vahy, prutok, brzda)
        s = srovnani(T, y, pred)
        z["val"], z["val_tym"], z["val_jako_ted"] = s["moje"], s["tym"], s["jako_ted"]
        z["val_radky"] = {k: s[k] for k in ("radku", "radku_moje", "radku_tym")}
        z["poradi_nahlednuti_val"] = pocet_val() + 1
    z["sekund"] = round(time.time() - t0, 1)
    zapis(z)
    v = z.get("val", {})
    print(f"{nazev}: {X.shape[1]} sloupců, alpha {alpha}, CV povodně {z['cv_povodne']} cm, velké {z['cv_velke']}, "
          f"CV vzestup {z['cv_vzestup']}, "
          f"CV MAE {z['cv_mae']}" + (f" | VAL povodně {v['mae_povodne']} cm, vzestup {v['mae_vzestup']}, "
                                    f"začátek {v['mae_zacatek']}, klid {v['mae_klid']}" if v else "")
          + (f" | tým {z['val_tym']['mae_povodne']}, jako teď {z['val_jako_ted']['mae_povodne']}" if v else "")
          + f" ({z['sekund']} s)")
    return z


VSE = dict(stanice="vse")
VSECHNY_ = [k for k, _ in HYDRO.values()]
NOVE = [s for s in VSECHNY_ if s not in TYM]
# disjunktní povodí nad Děčínem: Vltava v Praze + Labe v Kostelci + Ohře v Lounech + Bílina + Ploučnice (92 % plochy),
# Mělník místo Prahy a Kostelce (95 %), Ústí + Bílina + Ploučnice (skoro celé povodí, jen 3–6 h nad Děčínem)
SOUCTY = (("praha", "kostelec", "louny", "trmice", "benesov_pl"), ("melnik", "louny", "trmice", "benesov_pl"),
          ("usti", "trmice", "benesov_pl"))
ZMENY = dict(zmeny_h=(1, 3, 6, 12), zmeny_q=(1, 3, 6, 12), zrychleni=True)
POKUSY = {
    "tym": dict(tym=True, alpha=1.0),
    "tym_cv": dict(tym=True),
    "tym_zmena": dict(tym=True, zmena=True),
    "a_tym_moje": dict(stanice="tym"),
    "b_vse": VSE,
    "c_vse_zmeny": VSE | ZMENY,
    "c_vse_log": VSE | dict(q="log"),
    "c_vse_bez_transformace": VSE | dict(q=None),
    "d_srazky": VSE | dict(srazky=(1, 2, 3, 5)),
    "d_snih": VSE | dict(snih=True),
    "d_sezona": VSE | dict(sezona=True),
    "d_interakce": VSE | dict(interakce=True),
    "d_soucty": VSE | dict(soucty=SOUCTY, zpozdeni_soucty=(0, 6, 12)),
    "d_vahy2": VSE | dict(vahy=2),
    "d_vahy5": VSE | dict(vahy=5),
    "d_dlouhe": VSE | dict(zpozdeni_q=(0, 3, 6, 12, 18, 24, 36, 48, 60)),
    "d_huste": VSE | dict(zpozdeni_q=(0, 1, 2, 3, 6, 9, 12, 18, 24, 36)),
    "e_prutok_raw": VSE | dict(q=None, krivka=True, prutok=True),
    "e_prutok_sqrt": VSE | dict(krivka=True, prutok=True),
    "e_prutok_raw_zmeny": VSE | ZMENY | dict(q=None, krivka=True, prutok=True),
    "f_huste_zmeny": VSE | ZMENY | dict(zpozdeni_q=(0, 1, 2, 3, 6, 9, 12, 18, 24, 36)),
    "h_rezim250": VSE | dict(rezim=250),
    "h_rezim350": VSE | dict(rezim=350),
    "h_stoupa5": VSE | dict(rezim_stoupa=5),
    "h_stoupa15": VSE | dict(rezim_stoupa=15),
    "j_ridke_q": VSE | dict(zpozdeni_q=(0, 6, 12, 24)),
    "j_ridke_q36": VSE | dict(zpozdeni_q=(0, 12, 24, 36)),
    "j_bez_q_cilu": dict(stanice=[s for s in VSECHNY_ if s not in ("decin", "usti")]),
    "k_brzda10": VSE | dict(brzda=(10, NOVE)),
    "k_brzda30": VSE | dict(brzda=(30, NOVE)),
    "k_brzda100": VSE | dict(brzda=(100, NOVE)),
}

VSECHNY = [k for k, _ in HYDRO.values()]
SKUPINY_STANIC = {
    "ploucnice": ["benesov_pl", "struznice", "ceska_lipa"], "bilina": ["trmice"], "ohre_horni": ["zatec", "karlovy_vary"],
    "berounka_horni": ["zbecno", "liblin", "plzen", "plasy", "litavka"], "vltava_zbraslav": ["zbraslav"],
    "sazava_horni": ["kacov", "zruc"], "labe_horni": ["nemosice", "tyniste", "sany"], "jizera_horni": ["bakov"],
}
for g, sl in SKUPINY_STANIC.items():
    POKUSY[f"g_bez_{g}"] = dict(stanice=[s for s in VSECHNY if s not in sl])
    POKUSY[f"g_tym_plus_{g}"] = dict(stanice=TYM + sl)

BEZ = lambda *g: [s for s in VSECHNY if not any(s in SKUPINY_STANIC[x] for x in g)]  # noqa: E731
POKUSY |= {
    "i_bez_pl_saz_zbr": dict(stanice=BEZ("ploucnice", "sazava_horni", "vltava_zbraslav")),
    "i_jen_uzitecne": dict(stanice=TYM + SKUPINY_STANIC["ohre_horni"] + SKUPINY_STANIC["labe_horni"]
                           + SKUPINY_STANIC["berounka_horni"] + SKUPINY_STANIC["jizera_horni"]),
    "i_jen_uzitecne_bilina": dict(stanice=TYM + SKUPINY_STANIC["ohre_horni"] + SKUPINY_STANIC["labe_horni"]
                                  + SKUPINY_STANIC["berounka_horni"] + SKUPINY_STANIC["jizera_horni"] + ["trmice"]),
}

CESTA = ["ohre_horni", "labe_horni", "berounka_horni", "jizera_horni", "bilina", "vltava_zbraslav", "sazava_horni"]
for i in range(2, len(CESTA) + 1):
    POKUSY[f"l_tym_plus_{i}"] = dict(stanice=TYM + [s for g in CESTA[:i] for s in SKUPINY_STANIC[g]])

L2 = POKUSY["l_tym_plus_2"]
POKUSY |= {
    "m_huste": L2 | dict(zpozdeni_q=(0, 1, 2, 3, 6, 9, 12, 18, 24, 36)),
    "m_zmeny": L2 | ZMENY,
    "m_sezona": L2 | dict(sezona=True),
    "m_vahy2": L2 | dict(vahy=2),
    "m_srazky": L2 | dict(srazky=(1, 2, 3, 5)),
    "m_snih": L2 | dict(snih=True),
    "m_dlouhe": L2 | dict(zpozdeni_q=(0, 3, 6, 12, 18, 24, 36, 48)),
}

POKUSY["finalni"] = VSE | dict(alpha=1.0)  # = model_ridge.FINALNI, ALPHA

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("nazvy", nargs="+")
    p.add_argument("--val", action="store_true")
    a = p.parse_args()
    for n in a.nazvy:
        spust(n, POKUSY[n], a.val)
