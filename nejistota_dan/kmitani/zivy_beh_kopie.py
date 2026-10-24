"""Živá ukázka na provozních datech ČHMÚ (hydrology/recent, posledních ~4 týdny): týmový Ridge (24 a 36 h, natrénovaný
jako src/uloz_model.py na trénovací části) a Ridge 30 stanic na 36 h (models/ridge30_<cil>_36.joblib) proti realitě
a oficiální předpovědi ČHMÚ (H_F). Jen ukázka pro porotu, ne varování.

Hodinová tabulka z 10min dat: hodnota v celou hodinu (dt hh:00Z). Srovnání s ČHMÚ: jejich předpověď je v denním
souboru dne D jedna, hodinová od D 11:00Z; bereme ji jako vydanou v 11:00 UTC a náš model vydáváme ve stejný čas
z dat do 11:00 UTC. Cíl 24 h = D+1 11:00, 36 h = D+1 23:00.

python zivy_beh.py
"""
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

ZDE = Path(__file__).resolve().parent
ROOT = ZDE.parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ZDE.parent)]
from data import CILE, PROTI_PROUDU  # noqa: E402
from evaluate import casti  # noqa: E402
from features import ZPOZDENI_H, ZPOZDENI_Q, tabulka  # noqa: E402
from models import ridge  # noqa: E402
from stanice import HYDRO  # noqa: E402

RECENT = ZDE.parent / "cache/hydrology/recent/data"


def nacti_den(f):
    d = json.loads(f.read_text(encoding="utf-8"))["objList"][0]["tsList"]
    return {ts["tsConID"]: pd.Series({pd.Timestamp(v["dt"]): v["value"] for v in ts["tsData"]}, dtype="float64")
            for ts in d if ts["tsData"]}


def provozni_tabulka():
    """Hodinová tabulka ve formátu data_ridge (sloupce <stanice>_H, <stanice>_Q) + předpovědi ČHMÚ pro cíle."""
    rady, predpovedi = {}, {cil: {} for cil in CILE}
    for dbc, (klic, _) in HYDRO.items():
        H, Q = [], []
        for f in sorted(RECENT.glob(f"*_0-203-1-{dbc}.json")):
            d = nacti_den(f)
            H.append(d.get("H", pd.Series(dtype="float64")))
            Q.append(d.get("Q", pd.Series(dtype="float64")))
            if klic in CILE and "H_F" in d:
                predpovedi[klic][f.name[:8]] = d["H_F"]
        for nazev, r in ((f"{klic}_H", H), (f"{klic}_Q", Q)):
            r = [x for x in r if len(x)]
            if r:
                s = pd.concat(r).sort_index()
                s = s[~s.index.duplicated()]
                rady[nazev] = s[s.index.minute == 0]
    T = pd.DataFrame(rady)
    for c in [f"{k}_{v}" for k, _ in HYDRO.values() for v in "HQ"]:
        if c not in T:
            T[c] = np.nan  # stanice bez dané veličiny v provozu (Nymburk Q)
    T = T.reindex(pd.date_range(T.index.min(), T.index.max(), freq="h", tz="UTC"))
    return T, predpovedi


# průtok, který ČHMÚ v provozu nezveřejňuje (Mělník 1–2 hodnoty denně, Nymburk vůbec): bilance přítoků s posunem
# o dobu doběhu, koeficient z tréninkových let 2006–2018 (ověřeno na 2025: Mělník chyba 2,3 %, Nymburk 6,6 %)
BILANCE = {"melnik": (["vranany", "kostelec"], 3), "nymburk": (["prelouc", "sany"], 6)}


def doplnit(T):
    """Doplní chybějící průtok Mělníka a Nymburka bilancí a krátké díry (≤ 2 h) poslední známou hodnotou."""
    import data_ridge
    hist = data_ridge.nacti()["2006":"2018"]
    pocty = {}
    for s, (slozky, posun) in BILANCE.items():
        k = float((hist[f"{s}_Q"] / sum(hist[f"{x}_Q"].shift(posun) for x in slozky)).median())
        odhad = k * sum(T[f"{x}_Q"].shift(posun) for x in slozky)
        pocty[f"{s}_Q bilancí (koef. {k:.3f})"] = int((T[f"{s}_Q"].isna() & odhad.notna()).sum())
        T[f"{s}_Q"] = T[f"{s}_Q"].combine_first(odhad)
    pred = T.isna().sum()
    T = T.ffill(limit=2)
    pocty |= {f"{c} poslední známou": int(v) for c, v in (pred - T.isna().sum()).items() if v}
    return T, pocty


def tym_vstupy(T):
    """Týmových 98 vstupů (src/features.py) z provozní tabulky."""
    return pd.DataFrame({f"{s}_H_{z}": T[f"{s}_H"].shift(z) for s in CILE for z in ZPOZDENI_H}
                        | {f"{s}_Q_{z}": T[f"{s}_Q"].shift(z) for s in CILE | PROTI_PROUDU for z in ZPOZDENI_Q})


def nove_vstupy(T):
    from spolecne import NOVE
    return pd.DataFrame({f"{s}_Q_{z}": T[f"{s}_Q"].shift(z) for s in NOVE for z in ZPOZDENI_Q})


if __name__ == "__main__":
    sys.path.append(str(ZDE.parent / "stanice_vsem"))
    T, F = provozni_tabulka()
    print("provozní tabulka", T.index.min(), "až", T.index.max(), T.shape, "chybí hodin před doplněním:",
          T.isna().sum()[lambda s: s > 0].to_dict())
    T, pocty = doplnit(T)
    print("doplněno:", pocty, "| chybí po doplnění:", T.isna().sum()[lambda s: s > 0].to_dict())
    (ZDE / "zivy_doplneno.json").write_text(json.dumps(pocty, ensure_ascii=False, indent=1), encoding="utf-8")
    X = tym_vstupy(T)
    Xn = pd.concat([X, nove_vstupy(T)], axis=1)
    ok = X.notna().all(axis=1)
    okn = Xn.notna().all(axis=1)
    pred = {}
    for cil in CILE:
        for h in (24, 36):
            Xt, yt = tabulka(cil, h)
            tr = casti(cil, h).reindex(Xt.index) == "train"
            m = ridge.pipeline(ridge.PARAMETRY["alpha"]).fit(Xt[tr], yt[tr])  # jako src/uloz_model.py
            pred[(cil, h, "tym_ridge")] = pd.Series(m.predict(X[ok]), index=X.index[ok])
        r30 = joblib.load(ROOT / f"models/ridge30_{cil}_36.joblib")
        pred[(cil, 36, "ridge30")] = pd.Series(r30.m.predict(Xn[okn]), index=Xn.index[okn])  # pipeline bez pridej_stanice
    radky = []
    for cil in CILE:
        H = T[f"{cil}_H"]
        for den, hf in sorted(F[cil].items()):
            vydani = pd.Timestamp(f"{den[:4]}-{den[4:6]}-{den[6:]} 11:00", tz="UTC")
            for h in (24, 36):
                cas = vydani + pd.Timedelta(hours=h)
                if cas not in H.index or pd.isna(H.get(cas)):
                    continue
                r = dict(cil=cil, h=h, vydani=vydani, cas=cas, realita=H[cas], jako_ted=H.get(vydani),
                         chmu=hf.get(cas, np.nan), tym_ridge=pred[(cil, h, "tym_ridge")].get(vydani, np.nan),
                         ridge30=pred.get((cil, h, "ridge30"), pd.Series(dtype=float)).get(vydani, np.nan))
                radky.append(r)
    S = pd.DataFrame(radky)
    S.to_csv(ZDE / "zivy_srovnani.csv", index=False)
    for (cil, h), g in S.groupby(["cil", "h"]):
        e = {k: round(float((g[k] - g.realita).abs().mean()), 1) for k in ("jako_ted", "chmu", "tym_ridge", "ridge30")
             if g[k].notna().any()}
        print(cil, h, "dní", len(g), "MAE", e, "rozsah reality", int(g.realita.min()), "–", int(g.realita.max()))
    hod = pd.DataFrame({"_".join(map(str, k)): v for k, v in pred.items()})
    hod["decin_H"], hod["usti_H"] = T["decin_H"], T["usti_H"]
    hod.to_parquet(ZDE.parent / "cache/provoz/zive_predpovedi.parquet")
    for cil in CILE:
        pd.DataFrame(F[cil]).to_parquet(ZDE.parent / f"cache/provoz/chmu_hf_{cil}.parquet")
