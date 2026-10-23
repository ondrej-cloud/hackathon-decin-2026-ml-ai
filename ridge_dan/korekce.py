"""Aktualizace předpovědi podle poslední známé chyby (v hydrologii běžné „updating“).

V čase t už známe skutečný stav H(t) i předpověď p1 vydanou v t − 24 h na čas t. Chyba e(t) = H(t) − p1(t − 24)
říká, jestli model v téhle povodni soustavně přestřeluje, nebo podstřeluje. Druhý krok:
    předpověď = p1(t) + b1·e(t) + b2·ē6(t),   ē6 = průměr chyb za posledních 6 h
b1, b2 a absolutní člen se učí Ridge na tréninku. Aby se b neučily na chybách, které jsou v tréninku podezřele malé,
počítá se p1 na tréninkových řádcích mimo vlastní blok let (vnořená časová CV), stejně jako by to bylo v provozu.
"""
import numpy as np
import pandas as pd

import hodnoceni as Hd
import pokus

H24 = 24


def _fit_predict(Xa, ya, Xb, alpha, brzda=None):
    pen = pokus.nasobky_brzdy(Xa.columns, brzda) ** -2 if brzda else None
    mu, sd, k, b0 = pokus._koeficienty(Xa, ya.to_numpy(), None, (alpha,), pen)[alpha]
    return ((np.asarray(Xb, dtype=np.float64) - mu) / sd) @ k + b0


def p1_mimo_blok(X, y, radky_tr, alpha, brzda=None):
    """Předpovědi prvního modelu pro tréninkové řádky, každý blok let z modelu bez něj (bloky jako v CV)."""
    Xt, yt = X[radky_tr], y[radky_tr]
    p = pd.Series(np.nan, index=Xt.index)
    for _, f_tr, f_drz in Hd.bloky_cv(Xt.index):
        p[f_drz] = _fit_predict(Xt[f_tr], yt[f_tr], Xt[f_drz], alpha, brzda)
    return p


def chyby(X, p1):
    """e(t) = H(t) − p1(t − 24) a průměr za 6 h; p1 indexované časem vydání. Chybějící = 0 a příznak."""
    hod = pd.date_range(X.index.min(), X.index.max(), freq="h")
    p = p1.reindex(hod)
    H = X["decin_H_0"].reindex(hod)
    e = H - p.shift(H24)
    e6 = e.rolling(6, min_periods=1).mean()
    out = pd.DataFrame({"e": e, "e6": e6}).reindex(X.index)
    out["chybi"] = out.e.isna().astype(float)
    return out.fillna(0.0)


def druhy_krok_fit(E, r, alpha=1.0):
    from sklearn.linear_model import Ridge
    return Ridge(alpha=alpha).fit(E[["e", "e6"]], r)


def cv_korekce(X, y, c, alpha, brzda=None):
    """Vnořená CV celé dvoukrokové předpovědi na tréninkových řádcích. Vrací stejná čísla jako pokus.cv_alphy."""
    tr = c == "train"
    Xt, yt = X[tr], y[tr]
    pred = pd.Series(np.nan, index=yt.index)
    pred1 = pd.Series(np.nan, index=yt.index)
    for _, f_tr, f_drz in Hd.bloky_cv(Xt.index):
        Xa, ya = Xt[f_tr], yt[f_tr]
        # p1 na vnějším tréninku mimo vnitřní blok, na drženém bloku z modelu na celém vnějším tréninku
        p_a = p1_mimo_blok(Xa, ya, pd.Series(True, index=Xa.index), alpha, brzda)
        p_b = pd.Series(_fit_predict(Xa, ya, Xt[f_drz], alpha, brzda), index=Xt.index[f_drz])
        Ea, Eb = chyby(Xa, p_a), chyby(Xt[f_drz], p_b)
        m2 = druhy_krok_fit(Ea, ya - p_a)
        pred[f_drz] = p_b + m2.predict(Eb[["e", "e6"]])
        pred1[f_drz] = p_b
    return pred, pred1


def skore(X, y, c, pred):
    tr = c == "train"
    yt, Xt = y[tr], X[tr]
    okna = pokus.okna_povodni(yt)
    e = np.abs(pred.to_numpy() - yt.to_numpy())
    vz = ((yt - Xt["decin_H_0"]) >= 50).to_numpy()
    ud = {k: e[pos].mean() for k, pos in okna.items()}
    velke = [ud[k] for k, pos in okna.items() if yt.to_numpy()[pos].max() >= 490]
    return dict(cv_povodne=round(float(np.mean(list(ud.values()))), 2), cv_velke=round(float(np.mean(velke)), 2),
                cv_vzestup=round(e[vz].mean(), 2), cv_mae=round(e.mean(), 2),
                cv_udalosti={k: round(v, 1) for k, v in ud.items()})


class Dvoukrokova:
    """Finální podoba: první model (pokus.Predpoved) + oprava podle chyby předpovědi vydané před 24 h."""

    def __init__(self, alpha, brzda=None):
        self.alpha, self.brzda = alpha, brzda

    def fit(self, X, y):
        p_tr = p1_mimo_blok(X, y, pd.Series(True, index=X.index), self.alpha, self.brzda)
        self.m1 = pokus.Predpoved(self.alpha, False, None, brzda=self.brzda).fit(X, y)
        self.m2 = druhy_krok_fit(chyby(X, p_tr), y - p_tr)
        return self

    def predict(self, X):
        """X musí obsahovat i řádky 24 h před prvním řádkem, pro který chceme opravenou předpověď."""
        p1 = pd.Series(self.m1.predict(X), index=X.index)
        return (p1 + self.m2.predict(chyby(X, p1)[["e", "e6"]])).to_numpy()
