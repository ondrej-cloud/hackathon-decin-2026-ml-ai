"""Fyzikální model: průtok v cíli posunutý o přírůstky vody z bran proti proudu, převedený na hladinu měrnou křivkou."""
import numpy as np
import pandas as pd

from features import ZPOZDENI_Q

PARAMETRY = {
    "vyhlazeni_h": 12,  # klouzavý průměr proti hodinovému kolísání z elektráren
    "zmena_h": 6,  # doba putování podle korelace změn průtoku za tolik hodin
    "max_posun_h": 48,
    "pasem_krivky": 80,  # pásma po stejných krocích v logaritmu průtoku
    "min_hodin_v_pasmu": 6,
    "proti_proudu": True,  # když voda nedotekla ani k bráně, vzít stanice nad ní
}
# větve do Ústí: brána a stanice nad ní (Praha-Chuchle je pod soutokem s Berounkou, Jizera ústí pod Nymburkem)
VETVE = {"vranany": ["praha"], "kostelec": ["nymburk", "jizera"], "louny": []}


def doba_putovani(X, odkud, kam):
    """Posun v hodinách s největší korelací vyhlazených změn průtoku, jen při vyšší vodě."""
    Q = X[[f"{odkud}_Q_0", f"{kam}_Q_0"]].asfreq("h")
    dQ = Q.rolling(PARAMETRY["vyhlazeni_h"], center=True).mean().diff(PARAMETRY["zmena_h"])
    vysoka = Q[f"{kam}_Q_0"] > Q[f"{kam}_Q_0"].quantile(0.75)
    c = dQ[f"{kam}_Q_0"][vysoka]
    r = [c.corr(dQ[f"{odkud}_Q_0"].shift(k)[vysoka]) for k in range(PARAMETRY["max_posun_h"] + 1)]
    return int(np.argmax(r))


def merna_krivka(Q, H):
    """Medián hladiny v pásmech průtoku, jen rostoucí, nad posledním pásmem prodloužená přímkou."""
    hrany = np.geomspace(Q.min(), Q.max() * 1.0001, PARAMETRY["pasem_krivky"] + 1)
    i = np.digitize(Q, hrany)
    n = H.groupby(i).size()
    ok = n[n >= PARAMETRY["min_hodin_v_pasmu"]].index
    q = Q.groupby(i).median()[ok].values
    h = np.maximum.accumulate(H.groupby(i).median()[ok].values)
    sklon = (h[-1] - h[-2]) / (q[-1] - q[-2])

    def f(x):
        x = np.asarray(x, float)
        return np.where(x > q[-1], h[-1] + sklon * (x - q[-1]), np.interp(x, q, h))

    f.body = q, h
    return f


def zpozdeni(z):
    return min(ZPOZDENI_Q, key=lambda k: abs(k - z))


def prirustek(X, stanice, tau, horizont):
    """Kolik víc vody dorazí do h hodin ze stanice s dobou putování tau, jen ze změřených hodnot."""
    return X[f"{stanice}_Q_{zpozdeni(max(tau - horizont, 0))}"] - X[f"{stanice}_Q_{zpozdeni(tau)}"]


def fit(X, y, cil, horizont):
    do_usti = 0 if cil == "usti" else doba_putovani(X, "usti", "decin")
    tau = {b: doba_putovani(X, b, "usti") + do_usti for b in VETVE}
    tau |= {s: doba_putovani(X, s, b) + tau[b] for b, nad in VETVE.items() for s in nad}
    krivka = merna_krivka(X[f"{cil}_Q_0"], X[f"{cil}_H_0"])
    fit.tau, fit.krivka = tau, krivka

    def predict(X):
        Q_ted = X[f"{cil}_Q_0"]
        Q = Q_ted.copy()
        for b, nad in VETVE.items():
            Q += prirustek(X, b, tau[b], horizont)
            zbyva = horizont - tau[b]  # tak dlouho brána pustí vodu, kterou ještě nezměřila
            if PARAMETRY["proti_proudu"] and zbyva > 0:
                for s in nad:
                    Q += prirustek(X, s, tau[s] - tau[b], zbyva)
        return X[f"{cil}_H_0"] + krivka(Q.clip(lower=1)) - krivka(Q_ted)

    return predict
