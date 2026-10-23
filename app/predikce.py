"""Předpověď pro aplikaci: uložené modely (models/<model>_<cil>_<h>.joblib) a vstupy ze src/features.py.

Když modely Ridge chybí, natrénuje je stejně jako src/uloz_model.py (trénovací část, asi 5 s).
"""
import json
import sys
from functools import cache
from pathlib import Path

import joblib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from data import CILE, PROTI_PROUDU, SPA, nacti  # noqa: E402
from features import tabulka  # noqa: E402

MODELS = ROOT / "models"
HORIZONTY = (12, 24, 36)
NAZEV = {k: v[1] for k, v in (CILE | PROTI_PROUDU).items()}
KDE = {"decin": "v Děčíně", "usti": "v Ústí nad Labem"}
STUPNE = ["pod 1. stupněm", "1. stupeň (bdělost)", "2. stupeň (pohotovost)", "3. stupeň (ohrožení)"]
BARVY = ["#2e7d32", "#f2c437", "#ef6c00", "#c62828"]


def modely():
    """Modely, které mají v models/ aspoň jeden soubor; ridge vždy, ten se umí dotrénovat."""
    nazvy = {f.name.rsplit("_", 2)[0] for f in MODELS.glob("*_*_*.joblib")} if MODELS.exists() else set()
    return sorted(nazvy | {"ridge"})


def nacti_model(nazev, cil, h):
    soubor = MODELS / f"{nazev}_{cil}_{h}.joblib"
    if not soubor.exists():
        if nazev != "ridge":
            raise FileNotFoundError(f"chybí {soubor}, uloží ho autor modelu")
        from evaluate import casti
        from models import ridge
        X, y = tabulka(cil, h)
        tr = casti(cil, h).reindex(X.index) == "train"
        MODELS.mkdir(exist_ok=True)
        joblib.dump(ridge.pipeline(ridge.PARAMETRY["alpha"]).fit(X[tr], y[tr]), soubor)
    return joblib.load(soubor)


def vstupy(cil):
    """Vstupy pro všechny hodiny 2006–2025, kde jsou úplné (index UTC). Na horizontu nezávisí."""
    return tabulka(cil, HORIZONTY[0])[0]


def stupen(cil, hladina):
    """0 = bez stupně, 1 až 3 = stupeň povodňové aktivity."""
    return sum(hladina >= p for p in SPA[cil])


def predpoved(nazev, cil, radek):
    """Předpovědi za 12/24/36 h z jednoho řádku vstupů (DataFrame s jedním řádkem): {h: cm}."""
    return {h: float(nacti_model(nazev, cil, h).predict(radek)[0]) for h in HORIZONTY}


@cache
def _intervaly():
    soubor = MODELS / "ridge_intervaly.json"
    return json.loads(soubor.read_text(encoding="utf-8")) if soubor.exists() else None


def interval(nazev, cil, h, hladina_ted, pred):
    """Rozmezí (dolní, horní) v cm, do kterého se vešlo 90 % chyb na tréninku v pásmu hladiny teď; jen pro ridge."""
    z = _intervaly()
    if nazev != "ridge" or not z:
        return None
    z = z[f"{cil}_{h}"]
    i = max(k for k, hranice in enumerate(z["pasma"][:-1]) if hladina_ted >= hranice)
    return pred + z["dolni"][i], pred + z["horni"][i]


def trend(ted, drive):
    return "stoupá" if ted > drive * 1.05 else "klesá" if ted < drive * 0.95 else "drží se"


def vysvetleni(cil, h, ted, pred, radek):
    """Jedna věta pro laika, proč to tak vyšlo: co teče Prahou a Mělníkem."""
    r = radek.iloc[0]
    return (f"Za {h} h bude {KDE[cil]} asi {pred:.0f} cm, to je {STUPNE[stupen(cil, pred)]}; teď je {ted:.0f} cm. "
            f"Vltava v Praze teče {r['praha_Q_0']:.0f} m³/s a {trend(r['praha_Q_0'], r['praha_Q_6'])}, "
            f"Labe v Mělníku {r['melnik_Q_0']:.0f} m³/s a {trend(r['melnik_Q_0'], r['melnik_Q_6'])}. "
            f"Tahle voda doteče do Ústí a Děčína zhruba za půl dne až den.")
