"""Spouští pokusy s Ridge pro Děčín +24 h a zapisuje je do vysledky/pokusy.jsonl.

python pokus.py <nazev> [<nazev> ...]          jen časová křížová validace uvnitř tréninku (hlavní kritérium)
python pokus.py <nazev> --val                  navíc validace (střídmě, počet nahlédnutí se počítá)
Pokusy (nazev → volby) jsou v POKUSY níž. Test se tady spustit nedá, na ten je test_jednou.py.
"""
import argparse
import json
import time
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

ZDE = Path(__file__).resolve().parent
LOG = ZDE / "vysledky/pokusy.jsonl"
CIL, HORIZONT = "decin", 24
ALPHY = (0.1, 1, 3, 10, 30, 100, 300, 1000)


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

    def transform(self, X):
        X = X.drop(columns=["decin_Qsurovy_0"]).copy()
        for c in X.columns[X.columns.str.startswith("krivka_")]:
            q = np.log(X[c].clip(lower=1)).to_numpy()
            h = np.interp(q, self.q_, self.h_)
            nad = q > self.q_[-1]
            h[nad] = self.h_[-1] + self.sklon_ * (q[nad] - self.q_[-1])
            X[c] = h
        return X


def model(alpha, krivka=False):
    kroky = ([Krivka()] if krivka else []) + [StandardScaler(), Ridge(alpha=alpha)]
    return make_pipeline(*kroky)


class Predpoved:
    """Natrénovaný model: vstupy podle voleb → hladina v cm. Stejné rozhraní jako týmové modely (predict(X))."""

    def __init__(self, alpha, zmena, vahy):
        self.alpha, self.zmena, self.vahy = alpha, zmena, vahy

    def fit(self, X, y):
        ted = X[f"{CIL}_H_0"].to_numpy()
        cil = y.to_numpy() - ted if self.zmena else y.to_numpy()
        w = None
        if self.vahy:
            # řádky, kdy hladina za 24 h stoupne aspoň o 50 cm, mají větší váhu
            w = np.where(y.to_numpy() - ted >= 50, self.vahy, 1.0)
        self.m = model(self.alpha, "decin_Qsurovy_0" in X).fit(X, cil, ridge__sample_weight=w)
        self.sloupce = list(X.columns)
        return self

    def predict(self, X):
        p = self.m.predict(X[self.sloupce])
        return p + X[f"{CIL}_H_0"].to_numpy() if self.zmena else p


def pripravit(volby):
    T = data_ridge.nacti()
    if volby.get("tym"):
        X, y, L = tym_priznaky(T, CIL, HORIZONT)
    else:
        X, y, L = priznaky(T, CIL, HORIZONT, **{k: v for k, v in volby.items() if k not in ("alpha", "zmena", "vahy")})
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


def _koeficienty(X, y, w, alphy):
    """Totéž co StandardScaler + Ridge(alpha, sample_weight=w) ze sklearn, ale pro všechny alphy z jedné matice."""
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
        k = np.linalg.solve(G + a * np.eye(len(G)), b)
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


def cv_alphy(X, y, c, zmena=False, vahy=None, alphy=ALPHY):
    """Rychlá varianta cv() pro celou mřížku alph. Výsledky stejné jako cv() (ověřeno v kontrola_cv())."""
    tr = c == "train"
    Xt, yt = X[tr], y[tr]
    ted = Xt[f"{CIL}_H_0"].to_numpy()
    cil = yt.to_numpy() - ted if zmena else yt.to_numpy()
    w_vse = np.where(yt.to_numpy() - ted >= 50, vahy, 1.0) if vahy else None
    pred = {a: pd.Series(np.nan, index=yt.index) for a in alphy}
    for _, f_tr, f_drz in Hd.bloky_cv(Xt.index):
        Xa, Xb = Xt[f_tr], Xt[f_drz]
        if "decin_Qsurovy_0" in X:
            k = Krivka().fit(Xa)
            Xa, Xb = k.transform(Xa), k.transform(Xb)
        f_tr_np = np.asarray(f_tr)
        koef = _koeficienty(Xa, cil[f_tr_np], None if w_vse is None else w_vse[f_tr_np], alphy)
        Xb_np = np.asarray(Xb, dtype=np.float64)
        for a, (mu, sd, k_, b0) in koef.items():
            p_ = ((Xb_np - mu) / sd) @ k_ + b0
            pred[a][f_drz] = p_ + ted[np.asarray(f_drz)] if zmena else p_
    vz = ((yt - Xt[f"{CIL}_H_0"]) >= 50).to_numpy()
    okna = okna_povodni(yt)
    y_np = yt.to_numpy()
    radky = {}
    for a in alphy:
        p_np = pred[a].to_numpy()
        e = np.abs(p_np - y_np)
        udalosti = {k: e[pos].mean() for k, pos in okna.items()}
        radky[a] = dict(cv_povodne=round(float(np.mean(list(udalosti.values()))), 2), cv_mae=round(e.mean(), 2),
                        cv_vzestup=round(e[vz].mean(), 2), cv_bias_vzestup=round((p_np - y_np)[vz].mean(), 2),
                        cv_udalosti={k: round(v, 1) for k, v in udalosti.items()})
    return radky, pred


def nejlepsi_alpha(X, y, c, zmena=False, vahy=None, alphy=ALPHY):
    radky, _ = cv_alphy(X, y, c, zmena, vahy, alphy)
    a = min(radky, key=lambda a: radky[a]["cv_povodne"])
    return a, radky


def validace(T, X, y, c, alpha, zmena=False, vahy=None):
    tr, ev = c == "train", c == "val"
    m = Predpoved(alpha, zmena, vahy).fit(X[tr], y[tr])
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
    zmena, vahy = volby.get("zmena", False), volby.get("vahy")
    if "alpha" in volby:
        alpha, radky = volby["alpha"], cv_alphy(X, y, c, zmena, vahy, (volby["alpha"],))[0]
    else:
        alpha, radky = nejlepsi_alpha(X, y, c, zmena, vahy)
    z = dict(cas=datetime.now().isoformat(timespec="seconds"), nazev=nazev, volby=volby, sloupcu=X.shape[1],
             radku_train=int((c == "train").sum()), alpha=alpha, **radky[alpha],
             cv_alphy={a: r["cv_povodne"] for a, r in radky.items()})
    if s_val:
        _, pred = validace(T, X, y, c, alpha, zmena, vahy)
        s = srovnani(T, y, pred)
        z["val"], z["val_tym"], z["val_jako_ted"] = s["moje"], s["tym"], s["jako_ted"]
        z["val_radky"] = {k: s[k] for k in ("radku", "radku_moje", "radku_tym")}
        z["poradi_nahlednuti_val"] = pocet_val() + 1
    z["sekund"] = round(time.time() - t0, 1)
    zapis(z)
    v = z.get("val", {})
    print(f"{nazev}: {X.shape[1]} sloupců, alpha {alpha}, CV povodně {z['cv_povodne']} cm, CV vzestup {z['cv_vzestup']}, "
          f"CV MAE {z['cv_mae']}" + (f" | VAL povodně {v['mae_povodne']} cm, vzestup {v['mae_vzestup']}, "
                                    f"začátek {v['mae_zacatek']}, klid {v['mae_klid']}" if v else "")
          + (f" | tým {z['val_tym']['mae_povodne']}, jako teď {z['val_jako_ted']['mae_povodne']}" if v else "")
          + f" ({z['sekund']} s)")
    return z


VSE = dict(stanice="vse")
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
}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("nazvy", nargs="+")
    p.add_argument("--val", action="store_true")
    a = p.parse_args()
    for n in a.nazvy:
        spust(n, POKUSY[n], a.val)
