"""Rozdělení a metriky, stejné jako týmové src/evaluate.py, jen na vlastní tabulce.

evaluate.casti() si stav Děčína čte z Ondrovy tabulky, proto je tady převzaté řádek po řádku (stejné konstanty
z evaluate.py), jen se mu stav podá. overeni_splitu() kontroluje, že dává stejné značky jako originál.
Metriky povodní a varování bere přímo z evaluate.py (vyhodnot, varovani, povodne), ty jsou na datech nezávislé.

Otisk evaluate.py: git blob 5fde7d8d (commit 418debf, Ondra pá 19:58), stejný na Windows i Macu.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))  # kopie: o složku hlouběji
import evaluate as E  # noqa: E402
from data import SPA  # noqa: E402

OTISK_EVALUATE = "5fde7d8d4a406c2034e9e08cf3d2547b6825be10"


def casti(H, horizont, nejstarsi, finalni=False):
    """Stejné jako evaluate.casti(), H = stav cíle (hodinová řada v UTC), nejstarsi = nejstarší zpoždění vstupů."""
    c = pd.Series("train", index=H.index)
    if not finalni:
        vrcholy = [H[pd.Timestamp(d, tz="UTC") - pd.Timedelta(days=3):][:144].idxmax() for d in E.POVODNE_VAL]
        for v in vrcholy:
            c[v - E.OKNO_VAL - E.VYNECHAT: v + E.PO + E.VYNECHAT] = ""
        c[E.KLID_VAL[0]:E.KLID_VAL[1]] = "val"
        for v in vrcholy:
            c[v - E.OKNO_VAL: v + E.PO] = "val"
    c[E.TEST_OD:] = "test"
    ok = (c == c.shift(-horizont)) & (c == c.shift(nejstarsi))
    return c.where(ok, "")


def overeni_splitu(H, horizont=24):
    """Porovná značky s originálem evaluate.casti() (ten čte Ondrovu tabulku, jen pro kontrolu)."""
    moje = casti(H, horizont, 36)
    jeho = E.casti("decin", horizont)
    spolecne = moje.index.intersection(jeho.index)
    return int((moje[spolecne] != jeho[spolecne]).sum()), len(spolecne)


def metriky(y, pred, H, cil="decin", horizont=24):
    """Týmové metriky (vyhodnot) + klid, vzestup a varování pro všechny tři stupně.

    y: skutečný stav v t + horizont, pred: předpověď, index = čas vydání t. H: celá hodinová řada stavu cíle.
    """
    pred = pd.Series(np.asarray(pred, dtype=float), index=y.index)
    m = E.vyhodnot(y, pred, cil, horizont)
    e = (pred - y).abs()
    ted = H.reindex(y.index)
    zmena = y - ted
    klid = ((y.index >= pd.Timestamp(E.KLID_VAL[0], tz="UTC"))
            & (y.index < pd.Timestamp(E.KLID_VAL[1], tz="UTC") + pd.Timedelta(days=1)))
    # rychlé stoupání: za horizont hodin stoupne aspoň o 50 cm; začátek: v posledních 6 h ještě skoro nestoupalo
    vzestup = zmena >= 50
    zacatek = vzestup & ((ted - H.shift(6).reindex(y.index)) < 10)
    nizko = (y < 300) & (ted < 300)  # klid použitelný i pro test (tam nejsou roky 2019–2020)
    m |= dict(mae_klid=round(e[klid].mean(), 1) if klid.any() else None, mae_pod_300=round(e[nizko].mean(), 1),
              mae_vzestup=round(e[vzestup].mean(), 1), bias_vzestup=round((pred - y)[vzestup].mean(), 1),
              n_vzestup=int(vzestup.sum()),
              mae_zacatek=round(e[zacatek].mean(), 1), bias_zacatek=round((pred - y)[zacatek].mean(), 1),
              n_zacatek=int(zacatek.sum()))
    for n, prah in zip((1, 2, 3), SPA[cil]):
        v = E.varovani(y, pred, prah, horizont)
        m |= {f"spa{n}_{k}": x for k, x in v.items()}
    return m


def bloky_cv(index_train):
    """Časová křížová validace uvnitř tréninku: bloky po letech, kolem drženého bloku mezera 10 dní."""
    bloky = [(2006, 2007), (2008, 2009), (2010, 2011), (2012, 2013), (2014, 2015), (2016, 2018)]
    mezera = pd.Timedelta(days=10)
    out = []
    for a, b in bloky:
        od, do = pd.Timestamp(f"{a}-01-01", tz="UTC"), pd.Timestamp(f"{b}-12-31 23:00", tz="UTC")
        drz = (index_train >= od) & (index_train <= do)
        tr = (index_train < od - mezera) | (index_train > do + mezera)
        out.append((f"{a}-{b}", tr, drz))
    return out


def skore_cv(y, pred, prah=400):
    """Chyba v oknech kolem vrcholů nad 1. stupněm (7 dní před až 5 po) v drženém bloku; víc povodní než nad 2. SPA."""
    pred = pd.Series(np.asarray(pred, dtype=float), index=y.index)
    okno = pd.Series(False, index=y.index)
    for v in E.povodne(y, prah):
        okno[v - E.PRED: v + E.PO] = True
    e = (pred - y).abs()
    return dict(mae=e.mean(), mae_povodne=e[okno].mean() if okno.any() else np.nan, n_okno=int(okno.sum()))
