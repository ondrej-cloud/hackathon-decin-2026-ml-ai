"""Souřadnice a stupně povodňové aktivity našich 12 stanic z metadat ČHMÚ (balíček pořadatelů, meta1-*.json).

python src/stanice_hydro.py <cesta k meta1-*.json>    uloží data/external/stanice_hydro.csv (je v Gitu)
"""
import json
import sys

import pandas as pd

from data import CILE, PROTI_PROUDU, ROOT

SOUBOR = ROOT / "data/external/stanice_hydro.csv"

if __name__ == "__main__":
    z = json.load(open(sys.argv[1], encoding="utf-8"))["data"]["data"]
    M = pd.DataFrame(z["values"], columns=z["header"].split(","))
    klice = {dbc: k for k, (dbc, _) in (CILE | PROTI_PROUDU).items()}
    M = M[M.DBC.astype(str).isin(klice)].assign(klic=lambda m: m.DBC.astype(str).map(klice))
    out = M[["klic", "DBC", "STATION_NAME", "STREAM_NAME", "GEOGR1", "GEOGR2", "SPA1H", "SPA2H", "SPA3H"]].rename(
        columns=dict(DBC="cislo", STATION_NAME="stanice", STREAM_NAME="tok", GEOGR1="lat", GEOGR2="lon",
                     SPA1H="spa1_cm", SPA2H="spa2_cm", SPA3H="spa3_cm"))
    out = out.set_index("klic").loc[list(klice.values())]  # pořadí jako v data.py
    out.to_csv(SOUBOR, encoding="utf-8")
    print(out.to_string())
