"""Fyzikální model (3 vrstvy stanic): průtok v cíli posunutý o přírůstky vody z bran proti proudu, převedený na hladinu měrnou křivkou."""
import numpy as np
import pandas as pd

from features import ZPOZDENI_Q

PARAMETRY = {
    "vyhlazeni_h": 12,  # klouzavý průměr proti hodinovému kolísání z elektráren
    "zmena_h": 6,  # doba putování podle korelace změn průtoku za tolik hodin
    "max_posun_h": 48,
    "pasem_krivky": 80,  # pásma po stejných krocích v logaritmu průtoku
    "min_hodin_v_pasmu": 6,
    "vrstev": 3,  # brány a kolik vrstev stanic nad nimi, když voda nedotekla ani k bráně
}
# brány do Ústí a stanice nad každou stanicí (Praha-Chuchle je pod soutokem s Berounkou, Jizera ústí pod Nymburkem)
BRANY = ["vranany", "kostelec", "louny"]
NAD = {"vranany": ["praha"], "praha": ["beroun", "sazava"], "kostelec": ["nymburk", "jizera"], "nymburk": ["prelouc"]}


def doba_putovani(X, odkud, kam, p):
    """Posun v hodinách s největší korelací vyhlazených změn průtoku, jen při vyšší vodě."""
    Q = X[[f"{odkud}_Q_0", f"{kam}_Q_0"]].asfreq("h")
    dQ = Q.rolling(p["vyhlazeni_h"]).mean().diff(p["zmena_h"])
    vysoka = Q[f"{kam}_Q_0"] > Q[f"{kam}_Q_0"].quantile(0.75)
    c = dQ[f"{kam}_Q_0"][vysoka]
    r = [c.corr(dQ[f"{odkud}_Q_0"].shift(k)[vysoka]) for k in range(p["max_posun_h"] + 1)]
    return int(np.argmax(r))


def merna_krivka(Q, H, p):
    """Medián hladiny v pásmech průtoku, jen rostoucí, nad posledním pásmem prodloužená přímkou."""
    hrany = np.geomspace(Q.min(), Q.max() * 1.0001, p["pasem_krivky"] + 1)
    i = np.digitize(Q, hrany)
    n = H.groupby(i).size()
    ok = n[n >= p["min_hodin_v_pasmu"]].index
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


def fit(X, y, cil, horizont, p=PARAMETRY):
    do_usti = 0 if cil == "usti" else doba_putovani(X, "usti", "decin", p)
    tau = {}  # doba putování každé stanice do cíle

    def projdi(stanice, kam, vrstva):
        for s in stanice:
            tau[s] = doba_putovani(X, s, kam, p) + (tau[kam] if kam in tau else do_usti)
            if vrstva < p["vrstev"]:
                projdi(NAD.get(s, []), s, vrstva + 1)

    projdi(BRANY, "usti", 1)
    krivka = merna_krivka(X[f"{cil}_Q_0"], X[f"{cil}_H_0"], p)
    fit.tau, fit.krivka = tau, krivka

    def pritece(X, s, zbyva, do_s):
        """Přírůstek ze stanice s za zbývající hodiny; co ještě nezměřila, vezme ze stanic nad ní."""
        Q = prirustek(X, s, do_s, zbyva)
        for n in NAD.get(s, []):
            if n in tau and zbyva > do_s:
                Q = Q + pritece(X, n, zbyva - do_s, tau[n] - tau[s])
        return Q

    def predict(X):
        Q_ted = X[f"{cil}_Q_0"]
        Q = Q_ted + sum(pritece(X, b, horizont, tau[b]) for b in BRANY)
        return X[f"{cil}_H_0"] + krivka(Q.clip(lower=1)) - krivka(Q_ted)

    return predict
