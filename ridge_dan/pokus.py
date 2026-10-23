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
    tr = c == "train"
    Xt, yt = X[tr], y[tr]
    pred = pd.Series(np.nan, index=yt.index)
    vysl = {}
    for nazev, f_tr, f_drz in Hd.bloky_cv(Xt.index):
        m = Predpoved(alpha, zmena, vahy).fit(Xt[f_tr], yt[f_tr])
        pred[f_drz] = m.predict(Xt[f_drz])
        vysl[nazev] = Hd.skore_cv(yt[f_drz], pred[f_drz])
    ted = Xt[f"{CIL}_H_0"]
    vz = (yt - ted) >= 50
    e = (pred - yt).abs()
    okna = pd.Series(False, index=yt.index)
    for nazev, _, f_drz in Hd.bloky_cv(Xt.index):
        yy = yt[f_drz]
        for v in Hd.E.povodne(yy, 400):
            okna[v - Hd.E.PRED: v + Hd.E.PO] = True
    return dict(cv_povodne=round(e[okna].mean(), 2), cv_mae=round(e.mean(), 2), cv_vzestup=round(e[vz].mean(), 2),
                cv_bias_vzestup=round((pred - yt)[vz].mean(), 2),
                cv_bloky={k: round(v["mae_povodne"], 1) for k, v in vysl.items()})


def nejlepsi_alpha(X, y, c, zmena=False, vahy=None, alphy=ALPHY):
    radky = {a: cv(X, y, c, a, zmena, vahy) for a in alphy}
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
        alpha, radky = volby["alpha"], {volby["alpha"]: cv(X, y, c, volby["alpha"], zmena, vahy)}
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


POKUSY = {
    "tym": dict(tym=True, alpha=1.0),
}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("nazvy", nargs="+")
    p.add_argument("--val", action="store_true")
    a = p.parse_args()
    for n in a.nazvy:
        spust(n, POKUSY[n], a.val)
