"""Stáhne denní výšku sněhu (SCE) a průměrnou denní teplotu (T) pro část srážkoměrů ze srazkove_stanice.csv.

Proč: tři ze čtyř validačních povodní (3/2006, 3/2009, 1/2011) byly s táním sněhu. Z blízkých povodí (Bílina,
Ploučnice, Labe pod Mělníkem, Ohře) víc stanic, z dalekých dvě. Teplota tři stanice na povodí. Pořadí stanic
v CSV je už „nejdál od sebe, profesionální napřed“, bere se prvních N, které veličinu mají.
"""
import re

import pandas as pd

import stahni

stahni.PAUZA_S = 1.5
BLIZKO = ("bilina", "ploucnice", "labe_dolni", "ohre")
ADR = "meteorology/climate/historical_csv/data/daily/"


def vyber():
    S = pd.read_csv("srazkove_stanice.csv")
    sn = set(re.findall(r"dly-(.+?)-SCE\.csv", stahni.ziskej(ADR + "snow/").read_text(encoding="utf-8")))
    te = set(re.findall(r"dly-(.+?)-T\.csv", stahni.ziskej(ADR + "temperature/").read_text(encoding="utf-8")))
    sce = pd.concat([g[g.wsi.isin(sn)].head(6 if s in BLIZKO else 2) for s, g in S.groupby("skupina", sort=False)])
    t = pd.concat([g[g.wsi.isin(te)].head(3) for s, g in S.groupby("skupina", sort=False)])
    return sce, t


if __name__ == "__main__":
    sce, t = vyber()
    for w in sce.wsi:
        stahni.ziskej(f"{ADR}snow/dly-{w}-SCE.csv")
    for w in t.wsi:
        stahni.ziskej(f"{ADR}temperature/dly-{w}-T.csv")
    print(len(sce), "sníh,", len(t), "teplota")
