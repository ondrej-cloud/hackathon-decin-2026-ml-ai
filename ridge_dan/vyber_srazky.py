"""Vybere srážkoměrné stanice ČHMÚ s denními úhrny za 2005–2025 a přiřadí je k dílčím povodím nad Děčínem.

Povodí stanice: u srážkoměrů ČHMÚ (WSI 0-203-0-XYYZZ......) je v čísle zakódované číslo hydrologického pořadí
X-YY-ZZ. U ostatních (hlavně profesionální stanice 0-20000-0-…) se vezme pořadí nejbližšího vodoměrného profilu.
Z každého dílčího povodí se vezme nejvýš N stanic co nejdál od sebe, ať pokryjí celé povodí.
Výstup srazkove_stanice.csv. Potřebuje cache/ s metadaty (stahni.py).
"""
import json
import re

import numpy as np
import pandas as pd

import stahni

POCET = {"bilina": 12, "ploucnice": 12, "labe_dolni": 12, "ohre": 8}
POCET_JINAK = 6


def skupina(p):
    if not p.startswith("1-"):
        return None
    a, b = p[:7], p[:4]
    if a in ("1-14-04", "1-14-05") or b in ("1-15", "1-16", "1-17"):
        return None  # pod Děčínem
    if a == "1-14-01":
        return "bilina"
    if a == "1-14-03":
        return "ploucnice"
    if a in ("1-12-03", "1-13-05", "1-14-02"):
        return "labe_dolni"
    if b == "1-13":
        return "ohre"
    if a in ("1-12-01", "1-12-02", "1-09-04", "1-08-05"):
        return "vltava_dolni"
    if b in ("1-10", "1-11"):
        return "berounka"
    if b == "1-09":
        return "sazava"
    if b in ("1-06", "1-07", "1-08"):
        return "vltava_horni"
    if a in ("1-05-01", "1-05-02", "1-05-03"):
        return "jizera"
    if b in ("1-04", "1-05"):
        return "labe_stredni"
    return "labe_horni"


def nejdal_od_sebe(g, n):
    """Hladový výběr: nejdřív profesionální stanice, pak vždy ta nejvzdálenější od už vybraných."""
    g = g.sort_values("wmo", ascending=False)
    xy = np.c_[g.lon * np.cos(np.radians(50)), g.lat]
    vybrane = [0]
    while len(vybrane) < min(n, len(g)):
        d = np.min(np.hypot(*(xy[:, None, :] - xy[None, vybrane, :]).transpose(2, 0, 1)), axis=1)
        d[vybrane] = -1
        # profesionální stanice mají přednost, dokud nějaká zbývá
        d = d + 10 * g.wmo.to_numpy() * (d > 0)
        vybrane.append(int(d.argmax()))
    return g.iloc[vybrane]


if __name__ == "__main__":
    m = pd.read_csv(stahni.ziskej("meteorology/climate/historical_csv/metadata/meta1.csv"))
    m["od"] = pd.to_datetime(m.BEGIN_DATE.str[:10])
    m["do"] = pd.to_datetime(m.END_DATE.str[:10].str.replace("3999", "2100"))
    index = stahni.ziskej("meteorology/climate/historical_csv/data/daily/precipitation/").read_text(encoding="utf-8")
    sra = set(re.findall(r"dly-(.+?)-SRA\.csv", index))
    k = m.groupby("WSI").agg(od=("od", "min"), do=("do", "max"), jmeno=("FULL_NAME", "last"),
                             lon=("GEOGR1", "last"), lat=("GEOGR2", "last"), vyska=("ELEVATION", "last"))
    k = k[k.index.isin(sra) & (k.od <= "2005-01-01") & (k.do >= "2025-12-31")]

    h = json.loads(stahni.ziskej("hydrology/historical/metadata/meta1.json").read_text(encoding="utf-8"))["data"]["data"]
    h = pd.DataFrame(h["values"], columns=h["header"].split(","))
    # v metadatech hydrologie je GEOGR1 šířka a GEOGR2 délka, v meteorologii naopak
    d = np.hypot((k.lon.to_numpy()[:, None] - h.GEOGR2.astype(float).to_numpy()) * np.cos(np.radians(50)),
                 k.lat.to_numpy()[:, None] - h.GEOGR1.astype(float).to_numpy())
    k["hlgp_profil"] = h.HLGP4.to_numpy()[d.argmin(1)]
    kod = k.index.str.extract(r"^0-203-0-(\d)(\d\d)(\d\d)\d{6}$").set_index(k.index)
    k["hlgp"] = np.where(kod[0].notna(), kod[0] + "-" + kod[1] + "-" + kod[2], k.hlgp_profil.str[:7])
    k["skupina"] = k.hlgp.map(skupina)
    k["wmo"] = k.index.str.startswith("0-20000-0-")
    k = k[k.skupina.notna()]
    vyber = pd.concat([nejdal_od_sebe(g, POCET.get(s, POCET_JINAK)) for s, g in k.groupby("skupina")])
    vyber[["jmeno", "lon", "lat", "vyska", "hlgp", "skupina", "wmo"]].rename_axis("wsi").to_csv(
        "srazkove_stanice.csv", encoding="utf-8")
    print(vyber.skupina.value_counts().to_string())
    print(len(vyber), "stanic z", len(k), "kandidátů v povodí")
