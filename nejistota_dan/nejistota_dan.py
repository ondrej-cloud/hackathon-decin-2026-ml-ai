"""Pásmo nejistoty předpovědi stavu v Děčíně a Ústí (12/24/36 h) z chyb mimo trénink.

Navazuje na src/nejistota.py (tým): tam jsou kvantily chyby na TRÉNINKU podle pásma hladiny teď, tady kvantily chyby
e = skutečnost − předpověď z LOFO předpovědí mimo trénink (oof.py, 22 povodní 2006–2020) zvlášť podle režimu.
Režim je známý v čase vydání předpovědi:
- vzestup: model čeká vzestup, předpověď − stav teď ≥ PRAH (10 / 20 / 30 cm pro 12 / 24 / 36 h),
- pokles: předpověď − stav teď ≤ −PRAH,
- klid: jinak;
případně jemněji v 6 pásmech předpovězené změny (zmena6) nebo i podle výšky hladiny teď (pod / nad 1. stupněm,
Děčín 400 cm, Ústí 450 cm). Kterou variantu aplikace použije, vybírá overeni.py předem daným pravidlem.
Pásmo = [předpověď + dolní kvantil, předpověď + horní kvantil], pořadí kvantilu s opravou (n + 1) jako u konformní
předpovědi. Hodiny jedné povodně ale nejsou nezávislé a chyby jsou z 22 různých LOFO modelů, takže to žádnou záruku
nedává: pokrytí je empirické, ověřené vnořeně po blocích povodní (overeni.py).

Pro aplikaci: pasmo(model, cil, horizont, pred, hladina_ted, hladina_pred_6h, uroven) → (dolní, horní) v cm,
model "ridge" (týmový), "ridge30" nebo "g3"; kvantily čte z kvantily.json (overeni.py, ze všech 22 povodní).
"""
import json
from functools import cache
from pathlib import Path

import numpy as np
import pandas as pd

ZDE = Path(__file__).resolve().parent
KVANTILY = ZDE / "kvantily.json"
UROVNE = (0.8, 0.95)
# modely aplikace (app/predikce.py) → kalibrace: ridge i ridge_vse jsou týmový Ridge, jen učený na jiných letech
MODELY_APLIKACE = {"ridge_vse": "ridge"}
PRAH_ZMENY = {12: 10, 24: 20, 36: 30}
PRAH_VYSKY = {"decin": 400, "usti": 450}  # 1. stupeň povodňové aktivity
SKUPINY = {
    "globalni": "jedno pásmo pro všechny hodiny",
    "rezim": "vzestup / pokles / klid podle předpovězené změny",
    "rezim_vyska": "vzestup / pokles / klid × pod / nad 1. stupněm",
    "trend6": "stoupá / klesá / drží se podle změny hladiny za posledních 6 h (±5 cm)",
    "zmena6": "6 pásem předpovězené změny: ≤ −P, −P až −P/3, ±P/3, P/3 až P, P až 2P, ≥ 2P",
}


def skupina(varianta, cil, horizont, pred, h0, h6):
    """Režim pro každou hodinu (pole řetězců), jen z hodnot známých v čase vydání."""
    pred, h0, h6 = np.broadcast_arrays(*(np.asarray(v, dtype=float) for v in (pred, h0, h6)))
    if varianta == "globalni":
        return np.full(pred.shape, "vse", dtype=object)
    if varianta == "trend6":
        d = h0 - h6
        return np.where(d >= 5, "stoupa", np.where(d <= -5, "klesa", "drzi"))
    d, p = pred - h0, PRAH_ZMENY[horizont]
    if varianta == "zmena6":
        return np.array(["z" + str(i) for i in np.digitize(d, [-p, -p / 3, p / 3, p, 2 * p])], dtype=object)
    r = np.where(d >= p, "vzestup", np.where(d <= -p, "pokles", "klid")).astype(object)
    if varianta == "rezim":
        return r
    return r + np.where(h0 >= PRAH_VYSKY[cil], "_nad", "_pod")


def kvantil(e, q):
    """Konformní kvantil chyb e: pořadí ⌈(n + 1) q⌉ (horní), ⌊(n + 1) q⌋ (dolní), aby pokrytí nebylo pod nominálem."""
    e = np.sort(np.asarray(e, dtype=float))
    n = len(e)
    if n == 0 or not np.isfinite(e).all():
        raise ValueError("kvantil z prázdných nebo neplatných chyb")
    k = int(np.ceil((n + 1) * q)) if q > 0.5 else int(np.floor((n + 1) * q))
    return float(e[min(max(k, 1), n) - 1])


def kvantily_skupin(e, skupiny, uroven, min_n=200):
    """{skupina: (dolní, horní)}; skupina s méně než min_n chybami dostane kvantily ze všech chyb."""
    a = (1 - uroven) / 2
    e, skupiny = np.asarray(e, dtype=float), np.asarray(skupiny)
    vse = (kvantil(e, a), kvantil(e, 1 - a))
    out = {"vse": vse}
    for s in pd.unique(skupiny):
        es = e[skupiny == s]
        out[s] = (kvantil(es, a), kvantil(es, 1 - a)) if len(es) >= min_n else vse
    return out


def meze(pred, skupiny, kv):
    pred = np.asarray(pred, dtype=float)
    d = np.array([kv.get(s, kv["vse"])[0] for s in skupiny], dtype=float)
    h = np.array([kv.get(s, kv["vse"])[1] for s in skupiny], dtype=float)
    return pred + d, pred + h


@cache
def _ulozene():
    return json.loads(KVANTILY.read_text(encoding="utf-8"))


def pasmo(model, cil, horizont, pred, hladina_ted, hladina_pred_6h, uroven=0.8):
    """Dolní a horní mez (cm) předpovědi pred stavu za horizont hodin. Funguje pro čísla i pole."""
    z = _ulozene()
    klic = f"{MODELY_APLIKACE.get(model, model)}_{cil}_{horizont}"
    kv = {s: tuple(m) for s, m in z["kvantily"][klic][str(uroven)].items()}
    vstupy = (pred, hladina_ted, hladina_pred_6h)
    p, h0, h6 = np.broadcast_arrays(*(np.atleast_1d(np.asarray(x, dtype=float)) for x in vstupy))
    d, h = meze(p, skupina(z["varianta"], cil, horizont, p, h0, h6), kv)
    spatne = ~(np.isfinite(p) & np.isfinite(h0) & np.isfinite(h6))  # bez vstupů žádné zdánlivě platné pásmo
    d[spatne], h[spatne] = np.nan, np.nan
    return (float(d[0]), float(h[0])) if all(np.ndim(x) == 0 for x in vstupy) else (d, h)
