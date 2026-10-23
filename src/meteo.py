"""Hodinové vstupy z denní meteorologie ČHMÚ po větvích povodí (Vltava, horní Labe, Ohře).

`python src/meteo.py` je postaví z data/raw/chmu_meteo/ (stáhne src/stahni_chmu_meteo.py) a uloží do
data/external/labe_meteo.parquet. Každá hodnota je v tabulce až od chvíle, kdy byla změřená: denní úhrn srážek
s časem „den D 06:00 UTC“ je déšť za následujících 24 h (ověřeno na hodinových srážkách), takže ho bereme od D+1 07:00.
`--o-den-driv` postaví myšlenkový pokus, jako bychom srážky znali o den dřív (dokonalá předpověď na zítřek).
Do modelu se nesmí, je to únik z budoucnosti.
"""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from stahni_chmu_meteo import STANICE

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/chmu_meteo"
SOUBOR = ROOT / "data/external/labe_meteo.parquet"
RADEK = re.compile(r'\["([^"]+)","(SRA|SCE|T|API30)","([^"]*)","(20(?:0[5-9]|1\d|2[0-6])-[^"]*)",([^,]*),')


def denni(wsi):
    rows = []
    with open(RAW / f"dly-{wsi}.json", encoding="utf-8") as fh:
        for line in fh:
            m = RADEK.search(line)
            if m and (m.group(2) != "T" or m.group(3) == "AVG"):
                rows.append((m.group(2), pd.Timestamp(m.group(4)).normalize(), float(m.group(5).strip("\"") or "nan")))
    return pd.DataFrame(rows, columns=["el", "den", "val"]).pivot_table(index="den", columns="el", values="val")


def postav(zpozdeni_h=25):
    """zpozdeni_h: za kolik hodin po 06:00 dne D je denní hodnota známá."""
    hodiny = pd.date_range("2006-01-01", "2025-12-31 23:00", freq="h", tz="UTC")
    out = {}
    for vetev, stanice in STANICE.items():
        d = {w: denni(w) for w in stanice}
        prumer = lambda el: pd.concat({w: x[el] for w, x in d.items() if el in x}, axis=1).mean(axis=1)
        sra, sce = prumer("SRA"), prumer("SCE")
        tab = {f"srazky_{vetev}_1d": sra, f"srazky_{vetev}_3d": sra.rolling(3, min_periods=2).sum(),
               f"api30_{vetev}": prumer("API30"), f"snih_{vetev}": sce, f"snih_{vetev}_zmena_3d": sce.diff(3)}
        for c, s in tab.items():
            out[c] = s.set_axis(s.index + pd.Timedelta(hours=6 + zpozdeni_h)).reindex(hodiny, method="ffill")
        # průměrná teplota dne D je známá až po jeho konci
        t = prumer("T")
        out[f"teplota_{vetev}"] = t.set_axis(t.index + pd.Timedelta(hours=31)).reindex(hodiny, method="ffill")
    return pd.DataFrame(out).astype("float32").rename_axis("cas")


if __name__ == "__main__":
    vestec = "--o-den-driv" in sys.argv
    M = postav(1 if vestec else 25)
    cil = SOUBOR.with_name("labe_meteo_o_den_driv.parquet") if vestec else SOUBOR
    M.to_parquet(cil)
    print(M.describe().T[["count", "mean", "min", "max"]].round(1).to_string())
    print(f"uloženo {cil.relative_to(ROOT)}, {cil.stat().st_size / 1e6:.1f} MB")
