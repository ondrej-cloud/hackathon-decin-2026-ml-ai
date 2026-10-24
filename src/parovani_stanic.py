"""Ke každé stanici ovzduší najde nejbližší meteostanici, která měří teplotu i vítr.

Polohy meteostanic jsou z otevřených dat ČHMÚ (data/external/chmu_meteo_meta1-20261023.json,
https://opendata.chmi.cz/meteorology/climate/now/metadata/), v balíčku chybí.
"""
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AIR = ROOT / "data/raw/ovzdusi/uloha_2/Hlavní dataset"
METEO_CSV = ROOT / "data/raw/ovzdusi/uloha_2/Doplňkové datasety/meteorologie_hodinove_wide.csv"
EXT = ROOT / "data/external"


def dms(text):
    # "50° 35´ 8.757 sš" -> 50.585766
    d, m, s = map(float, re.findall(r"[\d.]+", text)[:3])
    return round(d + m / 60 + s / 3600, 6)


def km(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, (lat1, lon1, lat2, lon2))
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 6371 * 2 * np.arcsin(np.sqrt(a))


codes = set(pd.read_csv(AIR / "ovzdusi_hodinove_wide.csv", usecols=["station"]).station)
localities = json.load(open(AIR / "metadata/metadata.json"))["data"]["Localities"]
air = pd.DataFrame(
    [
        {"kod": l["LocalityCode"], "nazev": l["Name"],
         "lat": dms(l["Localization"]["Lat"]), "lon": dms(l["Localization"]["Lon"])}
        for l in localities if l["LocalityCode"] in codes
    ]
)

m = json.load(open(EXT / "chmu_meteo_meta1-20261023.json"))["data"]["data"]
meteo = pd.DataFrame(m["values"], columns=m["header"].split(","))
# Pozor: u meteostanic je GEOGR1 zeměpisná délka, v hydrologických metadatech je to šířka
meteo = meteo.rename(columns={"GEOGR1": "lon", "GEOGR2": "lat"}).drop_duplicates("WSI")
measured = pd.read_csv(METEO_CSV, usecols=["station", "T", "Fprum"]).groupby("station").agg(lambda s: s.notna().mean())
meteo = meteo.merge(measured, left_on="WSI", right_index=True)
full = meteo[(meteo["T"] > 0.5) & (meteo["Fprum"] > 0.5)]

pairs = []
for _, r in air.iterrows():
    dist = km(r.lat, r.lon, full.lat.astype(float), full.lon.astype(float))
    j = dist.idxmin()
    pairs.append({"stanice_ovzdusi": r.kod, "nazev": r.nazev, "meteo_WSI": full.loc[j, "WSI"],
                  "meteo_nazev": full.loc[j, "FULL_NAME"], "meteo_vyska_m": full.loc[j, "ELEVATION"],
                  "vzdalenost_km": round(float(dist[j]), 1)})

air.to_csv(EXT / "stanice_ovzdusi.csv", index=False)
pd.DataFrame(pairs).to_csv(EXT / "parovani_ovzdusi_meteo.csv", index=False)
print(pd.DataFrame(pairs).to_string(index=False))
