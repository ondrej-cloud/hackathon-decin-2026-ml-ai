"""Vstupy pro Ridge. Řádek = čas vydání předpovědi t (UTC), všechny vstupy jen z hodnot změřených v čase ≤ t.

tym_priznaky(): přesně týmové vstupy (src/features.py, 98 sloupců), jen z vlastní tabulky.
priznaky(T, cil, horizont, **volby): vlastní sada, volby viz ZAKLAD. Vrací X, y a nejstarší použité zpoždění
v hodinách (to potřebuje rozdělení, aby řádky přes hranici splitu vyhodilo).
"""
import numpy as np
import pandas as pd

from stanice import CILE, HYDRO, TYM

ZPOZDENI_H = (0, 1, 2, 3, 6, 12, 24)
ZPOZDENI_Q = (0, 3, 6, 12, 18, 24, 36)


def tym_priznaky(T, cil, horizont, odmocnina=True):
    """odmocnina: průtoky rovnou odmocněné, jako to dělá pipeline týmového Ridge (src/models/ridge.py)."""
    q = np.sqrt if odmocnina else (lambda x: x)
    X = pd.DataFrame(
        {f"{s}_H_{z}": T[f"{s}_H"].shift(z) for s in CILE for z in ZPOZDENI_H}
        | {f"{s}_Q_{z}": q(T[f"{s}_Q"]).shift(z) for s in TYM for z in ZPOZDENI_Q}
    )
    y = T[f"{cil}_H"].shift(-horizont).rename("y")
    ok = X.notna().all(axis=1) & y.notna()
    return X[ok], y[ok], max(ZPOZDENI_H + ZPOZDENI_Q)


ZAKLAD = dict(
    stanice="tym",          # "tym" = 12 týmových stanic, "vse" = všech 31, nebo seznam klíčů
    zpozdeni_h=ZPOZDENI_H,
    zpozdeni_q=ZPOZDENI_Q,
    q="sqrt",               # transformace průtoku: None, "sqrt", "log"
    zmeny_h=(),             # změny stavu cíle za k hodin: H(t) − H(t − k)
    zmeny_q=(),             # změny průtoku za k hodin (po transformaci), všechny vybrané stanice
    zrychleni=False,        # (H(t) − H(t−3)) − (H(t−3) − H(t−6)) pro cíl, totéž pro průtoky
    srazky=(),              # součty denních úhrnů za posledních k ukončených dní po povodích, např. (1, 2, 3, 5)
    snih=False,             # výška sněhu po povodích a její změna za 1 a 3 dny, teplota, tání = sníh × kladná teplota
    jen_tani=False,         # ze sněhu a teploty jen sloupce tani_*
    sezona=False,           # sin/cos dne v roce
    interakce=False,        # stav teď × jeho změna za 6 h (rychlost stoupání závisí na výšce)
    vyplnit_h=0,            # díry ve vstupech vyplnit poslední známou hodnotou, nejvýš k hodin (jen dopředu)
    soucty=(),              # součty průtoků teď přes skupiny stanic, např. (("praha", "kostelec", "louny"),);
                            # model je převede měrnou křivkou Děčína na cm (krivka_*), viz pokus.Krivka
    zpozdeni_soucty=(0,),
    krivka=False,           # přidat surový průtok Děčína teď (decin_Qsurovy_0), jen pro fit měrné křivky v modelu
    rezim=None,             # práh stavu cíle v cm: všechny vstupy ještě jednou vynásobené indikátorem H(t) ≥ práh
                            # (lineární model se dvěma sklony: klid a velká voda)
    rezim_stoupa=None,      # totéž s indikátorem „za posledních 6 h stouplo aspoň o tolik cm“
)


def _q(x, druh):
    if druh == "sqrt":
        return np.sqrt(x.clip(lower=0))
    if druh == "log":
        return np.log1p(x.clip(lower=0))
    return x


def seznam_stanic(volba):
    if volba == "tym":
        return list(TYM)
    if volba == "vse":
        return [k for k, _ in HYDRO.values()]
    return list(volba)


def priznaky(T, cil, horizont, bez_cile=False, **volby):
    """bez_cile=True: nechá i řádky, kde cíl ještě neznáme (posledních `horizont` hodin, pro předpověď v provozu)."""
    v = ZAKLAD | volby
    cilova = T[f"{cil}_H"]
    if v["vyplnit_h"]:  # jen vstupy, cíl zůstává změřený
        T = T.ffill(limit=v["vyplnit_h"])
    stanice = seznam_stanic(v["stanice"])
    sl, nejstarsi = {}, 0
    for s in CILE:
        for z in v["zpozdeni_h"]:
            sl[f"{s}_H_{z}"] = T[f"{s}_H"].shift(z)
    nejstarsi = max(nejstarsi, *v["zpozdeni_h"])
    for s in stanice:
        q = _q(T[f"{s}_Q"], v["q"])
        for z in v["zpozdeni_q"]:
            sl[f"{s}_Q_{z}"] = q.shift(z)
        for k in v["zmeny_q"]:
            sl[f"{s}_dQ_{k}"] = q - q.shift(k)
        if v["zrychleni"]:
            sl[f"{s}_aQ"] = q - 2 * q.shift(3) + q.shift(6)
    nejstarsi = max(nejstarsi, *v["zpozdeni_q"], *v["zmeny_q"], 6 if v["zrychleni"] else 0)
    if v["soucty"] or v["krivka"]:
        sl["decin_Qsurovy_0"] = T["decin_Q"]
    if v["soucty"]:
        for i, skup in enumerate(v["soucty"]):
            q = sum(T[f"{s}_Q"] for s in skup)
            for z in v["zpozdeni_soucty"]:
                sl[f"krivka_{i}_{z}"] = q.shift(z)
        nejstarsi = max(nejstarsi, *v["zpozdeni_soucty"])
    H = T[f"{cil}_H"]
    for k in v["zmeny_h"]:
        sl[f"{cil}_dH_{k}"] = H - H.shift(k)
    if v["zmeny_h"]:
        nejstarsi = max(nejstarsi, *v["zmeny_h"])
    if v["zrychleni"]:
        sl[f"{cil}_aH"] = H - 2 * H.shift(3) + H.shift(6)
    if v["interakce"]:
        sl[f"{cil}_HxdH6"] = H * (H - H.shift(6)) / 100
        nejstarsi = max(nejstarsi, 6)
    if v["srazky"]:
        for c in T.columns[T.columns.str.startswith("sra_")]:
            for k in v["srazky"]:
                # sra_* drží úhrn posledního ukončeného dne; k dní zpět = posuny po 24 h
                sl[f"{c}_{k}d"] = sum(T[c].shift(24 * j) for j in range(k))
        # nejstarší měření v součtu: posun 24·(k−1) h + podržení 23 h + 25 h od začátku měřicího dne (data_ridge)
        nejstarsi = max(nejstarsi, 24 * (max(v["srazky"]) - 1) + 23 + 25)
    if v["snih"]:
        for c in T.columns[T.columns.str.startswith("sce_")]:
            g = c[4:]
            sce = T[c]
            if not v["jen_tani"]:
                sl[c] = sce
                sl[f"{c}_d1"] = sce - sce.shift(24)
                sl[f"{c}_d3"] = sce - sce.shift(72)
            if f"tep_{g}" in T:
                if not v["jen_tani"]:
                    sl[f"tep_{g}"] = T[f"tep_{g}"]
                sl[f"tani_{g}"] = sce * T[f"tep_{g}"].clip(lower=0) / 10
        # změna za 3 dny (72 h) + podržení 23 h + 25 h od pozorování; teplota z termínů je mladší
        nejstarsi = max(nejstarsi, 72 + 23 + 25)
    if v["sezona"]:
        den = T.index.dayofyear.to_numpy()
        sl["sezona_sin"] = pd.Series(np.sin(2 * np.pi * den / 365.25), index=T.index)
        sl["sezona_cos"] = pd.Series(np.cos(2 * np.pi * den / 365.25), index=T.index)
    zakladni = [c for c in sl if not c.startswith("decin_Qsurovy")]
    if v["rezim"] is not None:
        ind = (H >= v["rezim"]).astype(float)
        for c in zakladni:
            sl[f"{c}_x{v['rezim']}"] = sl[c] * ind
    if v["rezim_stoupa"] is not None:
        ind = ((H - H.shift(6)) >= v["rezim_stoupa"]).astype(float).where(H.shift(6).notna())
        for c in zakladni:
            sl[f"{c}_s{v['rezim_stoupa']}"] = sl[c] * ind
        nejstarsi = max(nejstarsi, 6)
    # vyplněná díra prodlužuje historii vstupu o vyplnit_h hodin
    nejstarsi += v["vyplnit_h"]
    X = pd.DataFrame(sl).astype("float32")
    y = cilova.shift(-horizont).rename("y")
    ok = X.notna().all(axis=1) & (y.notna() | bez_cile)
    return X[ok], y[ok], nejstarsi
