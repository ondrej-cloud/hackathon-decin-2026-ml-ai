"""Společné rozdělení na train / val / test a vyhodnocení. Nikdo ho nemění jen pro svůj model.

- train: 2006–2018 bez validačních povodní a 20 dní kolem nich
- val: 4 vynechané povodně (16 dní před vrcholem až 5 dní po něm) a klidné roky 2019–2020
- test: 2021–2025 (povodně 12/2023 a 9/2024), pouští se jednou na konci, rozhoduje Ondra.
  Finální model se pak trénuje na všem do konce 2020.
"""
import numpy as np
import pandas as pd

from data import SPA, nacti
from features import NEJSTARSI

POVODNE_VAL = ["2006-04-03", "2009-03-07", "2010-09-29", "2011-01-17"]
KLID_VAL = ("2019-01-01", "2020-12-31")
TEST_OD = "2021-01-01"
OKNO_VAL, PRED, PO, VYNECHAT = pd.Timedelta(days=16), pd.Timedelta(days=7), pd.Timedelta(days=5), pd.Timedelta(days=20)


def povodne(H, prah):
    """Vrcholy povodní, kdy stav přešel práh (víc než 7 dní od sebe = různé povodně)."""
    s = H[H >= prah]
    useky = []
    for t in s.index:
        if useky and t - useky[-1][1] <= pd.Timedelta(days=7):
            useky[-1][1] = t
        else:
            useky.append([t, t])
    return [H[a:b].idxmax() for a, b in useky]


def casti(cil, horizont, finalni=False):
    """Pro každou hodinu 'train', 'val', 'test' nebo '' (nepoužít)."""
    H = nacti()[f"{cil}_H"]
    c = pd.Series("train", index=H.index)
    if not finalni:
        vrcholy = [H[pd.Timestamp(d, tz="UTC") - pd.Timedelta(days=3):][:144].idxmax() for d in POVODNE_VAL]
        for v in vrcholy:
            c[v - OKNO_VAL - VYNECHAT: v + PO + VYNECHAT] = ""
        c[KLID_VAL[0]:KLID_VAL[1]] = "val"
        for v in vrcholy:
            c[v - OKNO_VAL: v + PO] = "val"
    c[TEST_OD:] = "test"
    # vstupy (až 36 h zpět) i cíl (t + horizont) musí ležet ve stejné části, jinak řádek vynecháme
    ok = (c == c.shift(-horizont)) & (c == c.shift(NEJSTARSI))
    return c.where(ok, "")


def varovani(y, pred, prah, horizont):
    """Varování před překročením prahu. y a pred: index je čas vydání t, hodnota je stav v t + horizont.

    Předstih je nejvýš horizont: dřívější varování znamená, že model ohlásil povodeň dřív, než mohla přijít.
    Propásnutá povodeň se do průměrného předstihu počítá jako 0.
    """
    hodiny = pd.date_range(y.index.min(), y.index.max(), freq="h")
    y, pred = y.reindex(hodiny), pred.reindex(hodiny)
    alarm = (pred >= prah).astype(int)
    # začátek povodně: skutečný stav přejde práh a 4 dny předtím byl změřený a pod ním
    pod = (y < prah).astype(float).where(y.notna())
    zacatky = hodiny[(y >= prah) & (pod.shift(1).rolling(96, min_periods=96).min() == 1)]
    predstih, propasnuto = [], 0
    for t in zacatky:
        vydane = alarm[t - pd.Timedelta(hours=48): t + pd.Timedelta(hours=horizont - 1)]
        if vydane.any():
            predstih.append(min(horizont, horizont - (vydane.idxmax() - t) / pd.Timedelta(hours=1)))
        else:
            predstih.append(0.0)
            propasnuto += 1
    # planý poplach: souvislý úsek varování (mezery do 6 h spojíme), během kterého ani den po něm
    # skutečný stav práh nepřekročil (y[t] je stav v t + horizont, proto od s - horizont)
    a = alarm.rolling(7, min_periods=1).max()
    starty = hodiny[(a == 1) & (a.shift(1, fill_value=0) == 0)]
    konce = hodiny[(a == 1) & (a.shift(-1, fill_value=0) == 0)]
    plane = sum(not (y[s - pd.Timedelta(hours=horizont): e + pd.Timedelta(hours=24)] >= prah).any()
                for s, e in zip(starty, konce))
    return dict(povodni=len(zacatky), predstih_h=round(float(np.mean(predstih)), 1) if predstih else None,
                propasnuto=propasnuto, plane_poplachy=int(plane))


def vyhodnot(y, pred, cil, horizont):
    """Metriky jedné předpovědi (stav v cm). y a pred mají stejný index, čas vydání předpovědi."""
    pred = pd.Series(np.asarray(pred, dtype=float), index=y.index)
    e = (pred - y).abs()
    spa1, spa2, spa3 = SPA[cil]
    okno = pd.Series(False, index=y.index)
    vrcholy = []
    for v in povodne(y, spa2):
        okno[v - PRED: v + PO] = True
        # předpověď vydaná horizont hodin před vrcholem, kladná = nadhodnotil
        vrcholy.append(pred[v] - y[v])
    out = dict(
        mae=round(e.mean(), 1),
        mae_povodne=round(e[okno].mean(), 1),
        # kladná = model na povodních soustavně nadhodnocuje (pozor, nadhodnocování zlepšuje předstih)
        bias_povodne=round((pred - y)[okno].mean(), 1),
        mae_nad_1spa=round(e[y >= spa1].mean(), 1),
        chyba_vrcholu=round(float(np.mean(np.abs(vrcholy))), 1),
        vrcholy_o_kolik=[round(float(v)) for v in vrcholy],
        radku=len(y),
    )
    for n, prah in ((2, spa2), (3, spa3)):
        out |= {f"spa{n}_{k}": v for k, v in varovani(y, pred, prah, horizont).items()}
    return out
