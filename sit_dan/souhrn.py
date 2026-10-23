"""Souhrn variant sítě: průměr a rozptyl přes seedy, rozdíl proti variantě a (po seedech, párově) a verdikt.

python souhrn.py DIR        čte DIR/vysledky_sit.json (z beh_sit.py), vypíše tabulky v Markdownu

Rozhoduje CV povodně (jako u ostatních modelů v ridge_dan), zlepšení až od 1 cm a bez víc planých poplachů
a propásnutých povodní na validaci. Validace, začátek vzestupu a povodně 2006 a 2010 jsou vedle pro kontrolu.
"""
import json
import sys
from pathlib import Path

import pandas as pd

PRAH = 1.0
SLOUPCE = {
    "cv_povodne": "CV povodně", "cv_vzestup": "CV vzestup", "val_povodne": "val. povodně (6 komb.)",
    "zacatek": "začátek vzestupu", "p2006": "povodeň 2006", "p2010": "povodeň 2010",
    "plane": "plané poplachy 2.+3. st.", "propasnuto": "propásnuto 2.+3. st.",
}


def radky(vysledky):
    out = []
    for z in vysledky:
        v, d, c = z["val"], z["val"]["decin24"], z["cv"]
        out.append(dict(varianta=z["varianta"], popis=z["popis"], seed=z["seed"], cv_povodne=c["cv_povodne"],
                        cv_vzestup=c["cv_vzestup"], val_povodne=v["prumer_povodne"], zacatek=d["mae_zacatek"],
                        p2006=d["mae_2006"], p2010=d["mae_2010"], plane=v["spa2_plane"] + v["spa3_plane"],
                        propasnuto=v["spa2_propasnuto"] + v["spa3_propasnuto"]))
    return pd.DataFrame(out)


def fmt(m, s, des=2):
    return f"{m:.{des}f} ± {s:.{des}f}".replace(".", ",")


def tabulky(df):
    t = ["| varianta | " + " | ".join(SLOUPCE.values()) + " |", "|---" * (len(SLOUPCE) + 1) + "|"]
    for v, g in df.groupby("varianta", sort=True):
        t.append(f"| {v}: {g.popis.iloc[0]} | " + " | ".join(
            fmt(g[k].mean(), g[k].std(ddof=0), 1 if k in ("plane", "propasnuto") else 2) for k in SLOUPCE) + " |")
    a = df[df.varianta == "a"].set_index("seed")
    r = ["| rozdíl proti a (po seedech) | " + " | ".join(SLOUPCE.values()) + " | verdikt |",
         "|---" * (len(SLOUPCE) + 2) + "|"]
    for v, g in df[df.varianta != "a"].groupby("varianta"):
        d = g.set_index("seed")[list(SLOUPCE)] - a[list(SLOUPCE)]
        dm = d.mean()
        horsi_varovani = dm.plane > 0 or dm.propasnuto > 0
        if dm.cv_povodne <= -PRAH and not horsi_varovani:
            verdikt = "lepší"
        elif dm.cv_povodne >= PRAH or (dm.cv_povodne <= -PRAH and horsi_varovani):
            verdikt = "horší" if dm.cv_povodne >= PRAH else "beze změny (CV lepší, ale horší varování)"
        else:
            verdikt = "beze změny"
        r.append(f"| {v} − a | " + " | ".join(
            fmt(dm[k], d[k].std(ddof=0), 1 if k in ("plane", "propasnuto") else 2) for k in SLOUPCE) + f" | {verdikt} |")
    s = ["| varianta | seed | " + " | ".join(SLOUPCE.values()) + " |", "|---" * (len(SLOUPCE) + 2) + "|"]
    for _, x in df.sort_values(["varianta", "seed"]).iterrows():
        s.append(f"| {x.varianta} | {x.seed} | " + " | ".join(f"{x[k]:.2f}".replace(".", ",") for k in SLOUPCE) + " |")
    return "\n".join(t), "\n".join(r), "\n".join(s)


if __name__ == "__main__":
    df = radky(json.loads((Path(sys.argv[1]) / "vysledky_sit.json").read_text(encoding="utf-8")))
    for blok in tabulky(df):
        print(blok + "\n")
