"""Stáhne denní provozní soubory ČHMÚ hydrology/recent/data/<YYYYMMDD>_0-203-1-<DBC>.json pro 30 stanic
(stanice.py) za zadané dny. Šetrně přes stahni.ziskej: po jednom, pauza 1,5 s, cache, nic dvakrát.

python stahni_recent.py 2026-09-24 2026-10-23
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import stahni  # noqa: E402
from stanice import HYDRO  # noqa: E402

stahni.PAUZA_S = 1.5
if __name__ == "__main__":
    dny = pd.date_range(sys.argv[1], sys.argv[2], freq="D")
    n = chybi = 0
    for den in dny:
        for dbc in HYDRO:
            f = stahni.ziskej(f"hydrology/recent/data/{den:%Y%m%d}_0-203-1-{dbc}.json", povinne=False)
            n += f is not None
            chybi += f is None
        print(f"{den:%Y-%m-%d} hotovo", flush=True)
    print(n, "souborů,", chybi, "chybí")
