"""Natrénuje a vyhodnotí modely ze src/models/ na společném rozdělení a uloží výsledky do results/.

python src/porovnej.py jako_ted ridge      Děčín a Ústí za 12, 24 a 36 h, validace
python src/porovnej.py ridge --rychle      jen Děčín za 24 h
python src/porovnej.py --prehled           poslední výsledek každého modelu vedle sebe
python src/porovnej.py ridge --test        finální test, spouští jen Ondra

Model je soubor src/models/<nazev>.py s funkcí fit(X, y, cil, horizont), která vrátí funkci predict(X).
Volitelně PARAMETRY = {...}, uloží se k výsledku.
"""
import argparse
import importlib
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from evaluate import casti, vyhodnot
from features import tabulka

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
VSE = [(c, h) for c in ("decin", "usti") for h in (12, 24, 36)]
SLOUPCE = ["mae", "mae_povodne", "chyba_vrcholu", "spa2_predstih_h", "spa2_propasnuto", "spa2_plane_poplachy",
           "spa3_predstih_h", "spa3_propasnuto", "trenink_s"]


def spust(nazev, test=False, rychle=False):
    model = importlib.import_module(f"models.{nazev}")
    cast = "test" if test else "val"
    radky, predpovedi = [], []
    for cil, h in [("decin", 24)] if rychle else VSE:
        X, y = tabulka(cil, h)
        c = casti(cil, h, finalni=test).reindex(X.index)
        tr, ev = c == "train", c == cast
        t0 = time.time()
        predict = model.fit(X[tr], y[tr], cil=cil, horizont=h)
        t1 = time.time()
        pred = pd.Series(np.asarray(predict(X[ev]), dtype=float), index=X.index[ev])
        m = vyhodnot(y[ev], pred, cil, h)
        radky.append(dict(model=nazev, cil=cil, horizont=h, **m, trenink_s=round(t1 - t0, 1),
                          predpoved_s=round(time.time() - t1, 2)))
        predpovedi.append(pd.DataFrame({"cil": cil, "horizont": h, "skutecnost": y[ev], "predpoved": pred}))
        print(f"  {nazev} {cil} +{h} h: MAE {m['mae']} cm, na povodních {m['mae_povodne']} cm")

    cas = datetime.now()
    autor = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True).stdout.strip()
    zaznam = dict(autor=autor, cas=cas.isoformat(timespec="minutes"), model=nazev, cast=cast, rychle=rychle,
                  popis=(model.__doc__ or "").strip().split("\n")[0],
                  parametry=getattr(model, "PARAMETRY", {}), vysledky=radky)
    RESULTS.mkdir(exist_ok=True)
    soubor = RESULTS / f"{cas:%Y-%m-%d_%H%M}_{nazev}{'_test' if test else ''}.json"
    soubor.write_text(json.dumps(zaznam, ensure_ascii=False, indent=1))
    if not rychle:
        (RESULTS / "predpovedi").mkdir(exist_ok=True)
        pd.concat(predpovedi).rename_axis("cas_vydani").to_parquet(
            RESULTS / "predpovedi" / f"{nazev}{'_test' if test else ''}.parquet")
    print(f"uloženo {soubor.relative_to(ROOT)}")
    return pd.DataFrame(radky)


def prehled(cast="val"):
    posledni = {}
    for f in sorted(RESULTS.glob("*.json")):
        z = json.loads(f.read_text())
        if z["cast"] == cast and not z.get("rychle"):
            posledni[z["model"]] = z
    if not posledni:
        return pd.DataFrame()
    return pd.DataFrame([r for z in posledni.values() for r in z["vysledky"]])


def tisk(df):
    if df.empty:
        print("zatím žádné výsledky")
        return
    print(df.set_index(["cil", "horizont", "model"]).sort_index()[SLOUPCE].to_string())


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("modely", nargs="*")
    p.add_argument("--rychle", action="store_true")
    p.add_argument("--prehled", action="store_true")
    p.add_argument("--test", action="store_true")
    a = p.parse_args()
    if a.prehled:
        tisk(prehled("test" if a.test else "val"))
    else:
        tisk(pd.concat([spust(m, test=a.test, rychle=a.rychle) for m in a.modely]))
