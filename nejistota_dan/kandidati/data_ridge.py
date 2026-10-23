"""Vlastní hodinová tabulka 2006–2025 v UTC z otevřených dat ČHMÚ (CC BY 4.0): stavy a průtoky + denní srážky.

python data_ridge.py    postaví tabulka/labe_ridge.parquet (není v Gitu) z cache/ (stahni_hydro.py, stahni_srazky.py)

Sloupce:
- <stanice>_H stav v cm (jen Děčín a Ústí), <stanice>_Q průtok v m3/s, čas měření v UTC (ČHMÚ dává 'Z')
- sra_<povodí>: průměrný denní úhrn srážek v povodí za poslední UKONČENÝ měřicí den, jak by byl známý v čase t.
  Denní hodnota s razítkem D 06:00Z je součet hodinových srážek D 07:00Z … D+1 06:00Z (ověřeno na hodinových
  datech 2019, overeni_srazek()). Do tabulky proto vstupuje až od D+1 07:00 UTC (hodina rezervy) a platí 24 h.
"""
import glob
import json
import re
from functools import cache
from pathlib import Path

import numpy as np
import pandas as pd

from stanice import CILE, HYDRO

ZDE = Path(__file__).resolve().parent
CACHE = ZDE / "cache"
SOUBOR = Path("C:/Users/danie/Documents/hackathon-2026-ridge/ridge_dan/tabulka/labe_ridge.parquet")  # kopie: tabulka není v Gitu, čte se z worktree dan-ridge
OD, DO = "2006-01-01", "2025-12-31"
DOSTUPNE_PO = pd.Timedelta(hours=25)  # od razítka denního úhrnu do chvíle, kdy ho smíme použít


def hydro():
    keys = {dbc: k for dbc, (k, _) in HYDRO.items()}
    parts = {}
    for f in glob.glob(str(CACHE / "hydrology/historical/data/hourly/H_0-203-1-*_HQ_*.json")):
        dbc, rok = re.search(r"1-(\d+)_HQ_(\d{4})", f).groups()
        if dbc not in keys or not OD[:4] <= rok <= DO[:4]:
            continue
        for ts in json.loads(Path(f).read_text(encoding="utf-8"))["tsList"]:
            veliciny = "HQ" if keys[dbc] in CILE else "Q"
            if ts["tsConID"][0] in veliciny:
                v = pd.DataFrame(ts["tsData"]["data"]["values"], columns=["t", "v"])
                parts.setdefault(f"{keys[dbc]}_{ts['tsConID'][0]}", []).append(v)
    D = pd.DataFrame({
        k: pd.concat(v).assign(t=lambda x: pd.to_datetime(x.t, utc=True)).drop_duplicates("t").set_index("t").v
        for k, v in parts.items()
    }).sort_index()
    D = D.reindex(pd.date_range(OD, f"{DO} 23:00", freq="h", tz="UTC"))
    # stejná oprava jako v týmové tabulce: v Děčíně stav až 1 019 cm při průtoku kolem 120 m3/s (led), nebereme
    D.loc["2006-02-05":"2006-02-08 09:00", "decin_H"] = np.nan
    poradi = [f"{k}_{v}" for k in CILE for v in "HQ"] + [f"{k}_Q" for k, _ in HYDRO.values() if k not in CILE]
    return D[[c for c in poradi if c in D]]


def denni(slozka, prvek, wsi):
    """Denní hodnoty prvku po stanicích (index = razítko ČHMÚ v UTC), sloupce wsi. Chybějící soubor přeskočí."""
    out = {}
    for w in wsi:
        f = CACHE / f"meteorology/climate/historical_csv/data/daily/{slozka}/dly-{w}-{prvek}.csv"
        if not f.exists():
            continue
        d = pd.read_csv(f)
        d = d[d.ELEMENT == prvek]
        out[w] = d.assign(DT=pd.to_datetime(d.DT, utc=True)).drop_duplicates("DT").set_index("DT").VALUE
    return pd.DataFrame(out).sort_index()["2005-12-01":]


def teplota_terminy(skupiny, hodiny):
    """Teplota z termínů 06, 13 a 20 UTC (okamžitá měření): průměr posledních tří termínů (≈ posledních 24 h),
    použitelný hodinu po posledním z nich. Denní průměr AVG (razítko D 00:00Z) se nepoužívá."""
    out = {}
    for s in sorted(skupiny.unique()):
        rady = []
        for w in skupiny.index[skupiny == s]:
            f = CACHE / f"meteorology/climate/historical_csv/data/daily/temperature/dly-{w}-T.csv"
            if not f.exists():
                continue
            d = pd.read_csv(f)
            d = d[(d.ELEMENT == "T") & d.TIMEFUNC.isin(["06:00", "13:00", "20:00"])]
            d = d.assign(DT=pd.to_datetime(d.DT, utc=True)).drop_duplicates("DT").set_index("DT").VALUE.sort_index()
            d = d["2005-12-01":]
            # tři po sobě jdoucí termíny musí ležet do 24 h, jinak je v řadě díra
            ok = (d.index.to_series().diff(2) <= pd.Timedelta(hours=24)).to_numpy()
            d = d.rolling(3).mean().where(ok)
            d.index = d.index + pd.Timedelta(hours=1)
            rady.append(d.rename(w))
        if rady:
            out[f"tep_{s}"] = pd.concat(rady, axis=1, sort=True).mean(axis=1).reindex(hodiny, method="ffill", limit=11)
    out = pd.DataFrame(out, index=hodiny)
    # vybrané teploměry Labe pod Mělníkem měří jen do roku 2005, Jizera až od 2015: teplota je plošně hladká,
    # vezme se ze sousedního povodí (Bílina, střední Labe)
    for s, soused in (("labe_dolni", "bilina"), ("jizera", "labe_stredni")):
        out[f"tep_{s}"] = out.get(f"tep_{s}", pd.Series(np.nan, index=hodiny)).combine_first(out[f"tep_{soused}"])
    return out


def srazky_denni():
    S = pd.read_csv(ZDE / "srazkove_stanice.csv")
    return denni("precipitation", "SRA", S.wsi), S.set_index("wsi").skupina


def po_povodich(dny, skupiny, hodiny, predpona, posun):
    """Průměr přes stanice povodí, posunutý o `posun` od razítka (kdy je hodnota známá), podržený 24 h."""
    out = {}
    for s in sorted(skupiny.unique()):
        sl = [w for w in skupiny.index[skupiny == s] if w in dny]
        if not sl:
            continue
        d = dny[sl].mean(axis=1)
        d.index = d.index + posun
        out[f"{predpona}_{s}"] = d.reindex(hodiny, method="ffill", limit=23)
    return pd.DataFrame(out, index=hodiny)


def srazky_hodinove(denni_sra, skupiny, hodiny):
    return po_povodich(denni_sra, skupiny, hodiny, "sra", DOSTUPNE_PO)


def overeni_srazek():
    """Průměrný rozdíl denního úhrnu a součtu hodinových pro různé začátky intervalu (Ústí-Kočkov, 05–08/2019)."""
    fs = sorted(glob.glob(str(CACHE / "meteorology/climate/historical_csv/data/1hour/precipitation/2019/*11502*")))
    h = pd.concat([pd.read_csv(f) for f in fs]).assign(DT=lambda x: pd.to_datetime(x.DT, utc=True)).set_index("DT").VALUE
    d = pd.read_csv(CACHE / "meteorology/climate/historical_csv/data/daily/precipitation/dly-0-20000-0-11502-SRA.csv")
    d = d[d.ELEMENT == "SRA"].assign(DT=lambda x: pd.to_datetime(x.DT, utc=True)).set_index("DT").VALUE
    d = d["2019-05-03":"2019-08-28"]
    c = h.cumsum()
    out = {}
    for p in range(-26, 4):
        s = c.reindex(d.index + pd.Timedelta(hours=24 + p)).to_numpy() - c.reindex(d.index + pd.Timedelta(hours=p)).to_numpy()
        out[p] = round(float(np.nanmean(np.abs(s - d.to_numpy()))), 3)
    return pd.Series(out, name="mm")


def postav():
    D = hydro()
    sra, skupiny = srazky_denni()
    R = srazky_hodinove(sra, skupiny, D.index)
    # výška sněhu: pozorování v 06:00Z, bereme konzervativně až od dalšího dne 07:00Z jako srážky
    snih = po_povodich(denni("snow", "SCE", skupiny.index), skupiny, D.index, "sce", DOSTUPNE_PO)
    teplota = teplota_terminy(skupiny, D.index)
    T = pd.concat([D, R, snih, teplota], axis=1).astype("float32").rename_axis("cas")
    SOUBOR.parent.mkdir(exist_ok=True)
    T.to_parquet(SOUBOR)
    return T


@cache
def nacti():
    return pd.read_parquet(SOUBOR).astype("float64")


if __name__ == "__main__":
    T = postav()
    print(f"{len(T)} hodin, {T.shape[1]} sloupců, {SOUBOR.stat().st_size / 1e6:.1f} MB")
    print("chybí (hodin):", T.isna().sum()[lambda s: s > 0].to_dict())
    o = overeni_srazek()
    print("denní úhrn vs. hodinové, posun začátku intervalu proti razítku (h) → průměrný rozdíl mm:")
    print(o[o.index >= -3].to_string())
