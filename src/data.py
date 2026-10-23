"""Hodinová tabulka stavů a průtoků na Labi a přítocích nad Děčínem, 2006–2025.

`python src/data.py` ji postaví z data/raw/chmu_hydro/ (stáhne src/stahni_chmu_hydro.py) a uloží
do data/external/labe_hodinove.parquet. Ten je v Gitu, takže ostatní nic stahovat nemusí a čtou ho přes nacti().
"""
import glob
import json
import re
from functools import cache
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/chmu_hydro"
SOUBOR = ROOT / "data/external/labe_hodinove.parquet"

# klíč stanice: (číslo ČHMÚ, název). U cílů bereme stav i průtok, u ostatních jen průtok.
CILE = {"decin": ("240000", "Děčín (Labe)"), "usti": ("221000", "Ústí nad Labem (Labe)")}
PROTI_PROUDU = {
    "louny": ("219000", "Louny (Ohře)"),
    "melnik": ("204000", "Mělník (Labe)"),
    "vranany": ("203000", "Vraňany (Vltava)"),
    "kostelec": ("104400", "Kostelec nad Labem (Labe)"),
    "praha": ("200100", "Praha-Chuchle (Vltava)"),
    "nymburk": ("080000", "Nymburk (Labe)"),
    "jizera": ("101800", "Předměřice (Jizera)"),
    "beroun": ("198000", "Beroun (Berounka)"),
    "sazava": ("167200", "Nespeky (Sázava)"),
    "prelouc": ("061000", "Přelouč (Labe)"),
}
# stupně povodňové aktivity v cm (metadata ČHMÚ)
SPA = {"decin": (400, 490, 560), "usti": (450, 530, 600)}
OD, DO = "2006-01-01", "2025-12-31"  # Kostelec a průtok v Mělníku a Nymburku začínají až 2006


def postav():
    keys = {dbc: k for k, (dbc, _) in (CILE | PROTI_PROUDU).items()}
    parts = {}
    for f in glob.glob(str(RAW / "H_0-203-1-*_HQ_*.json")):
        dbc, rok = re.search(r"1-(\d+)_HQ_(\d{4})", f).groups()
        if dbc not in keys or not OD[:4] <= rok <= DO[:4]:
            continue
        for ts in json.load(open(f))["tsList"]:
            veliciny = "HQ" if keys[dbc] in CILE else "Q"
            if ts["tsConID"][0] in veliciny:
                v = pd.DataFrame(ts["tsData"]["data"]["values"], columns=["t", "v"])
                parts.setdefault(f"{keys[dbc]}_{ts['tsConID'][0]}", []).append(v)
    D = pd.DataFrame({
        k: pd.concat(v).assign(t=lambda x: pd.to_datetime(x.t, utc=True)).drop_duplicates("t").set_index("t").v
        for k, v in parts.items()
    }).sort_index()
    D = D.reindex(pd.date_range(OD, f"{DO} 23:00", freq="h", tz="UTC"))
    # chyba měření: v Děčíně stav až 1 019 cm při průtoku kolem 120 m3/s, Ústí přitom 161 cm
    D.loc["2006-02-05":"2006-02-07", "decin_H"] = None
    D = D.interpolate(limit=6, limit_area="inside")
    cols = [f"{k}_{v}" for k in CILE for v in "HQ"] + [f"{k}_Q" for k in PROTI_PROUDU]
    D[cols].astype("float32").rename_axis("cas").to_parquet(SOUBOR)
    return D[cols]


@cache
def nacti():
    """Hodinová tabulka, index je čas v UTC, sloupce <stanice>_H (cm) a <stanice>_Q (m3/s)."""
    return pd.read_parquet(SOUBOR).astype("float64")


if __name__ == "__main__":
    D = postav()
    print(f"{len(D)} hodin, {D.shape[1]} sloupců, úplných řádků {int(D.notna().all(axis=1).sum())}")
    print("chybí (hodin):", D.isna().sum()[lambda s: s > 0].to_dict())
    print(f"{SOUBOR.relative_to(ROOT)}: {SOUBOR.stat().st_size / 1e6:.1f} MB")
