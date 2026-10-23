"""Předpověď na teď z operativních dat ČHMÚ (https://opendata.chmi.cz/hydrology/, adresáře now a recent).

- now/data/0-203-1-<stanice>.json: dnešek od 0:00 UTC po 10 minutách, obnovuje se asi každých 20 minut.
- recent/data/<RRRRMMDD>_0-203-1-<stanice>.json: celé předchozí dny od 1. 1. 2026, objeví se po půlnoci UTC.
Data jsou nevalidovaná. Časy jsou v UTC (ověřeno proti hydro.chmi.cz/hpps, kde jsou v českém čase).
Hodinová hodnota v čase t je průměr hodnot t:00 až t:50, stejně jako v hodinovém archivu, ze kterého
se modely učily (ověřeno na Děčíně 2025, docs/DATA.md).

python app/aktualni.py ověří řádek vstupů proti src/features.py a vypíše předpověď na teď.
"""
import json
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import requests

import predikce
from data import CILE, PROTI_PROUDU, nacti
from features import NEJSTARSI, ZPOZDENI_H, ZPOZDENI_Q, tabulka

URL = "https://opendata.chmi.cz/hydrology/"
RAW = predikce.ROOT / "data/raw/chmu_aktualni"
DNU = 3  # celé dny z recent/; i těsně po půlnoci, než se objeví včerejšek, je to přes 48 h
SLOUPCE = [f"{k}_{v}" for k in CILE for v in "HQ"] + [f"{k}_Q" for k in PROTI_PROUDU]
# Průtok v Nymburce ČHMÚ operativně nezveřejňuje a v Mělníku jen dvakrát denně. Dopočteme ho z bilance vody,
# v archivu 2006–2020 sedí: Mělník = Vraňany + Kostelec o hodinu dřív (odchylka 0,5 %),
# Nymburk = Kostelec − Jizera (8 %).
DOPOCET = {
    "melnik_Q": lambda D: (D["vranany_Q"] + D["kostelec_Q"]).shift(1),
    "nymburk_Q": lambda D: (D["kostelec_Q"] - D["jizera_Q"]).clip(lower=0),
}


def _soubor(cesta):
    """JSON z opendata.chmi.cz, kopie jde do data/raw/chmu_aktualni. Celé dny z recent/ se stahují jen jednou."""
    soubor = RAW / cesta.replace("/data/", "_")
    if cesta.startswith("recent") and soubor.exists():
        return json.loads(soubor.read_text(encoding="utf-8"))
    r = requests.get(URL + cesta, timeout=30)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    RAW.mkdir(parents=True, exist_ok=True)
    soubor.write_bytes(r.content)
    return r.json()


def stahni():
    """Hodinová tabulka za poslední 3 až 4 dny, sloupce a jednotky jako data.nacti(), index UTC po hodinách.

    Nic se nedoplňuje: co ČHMÚ nezveřejnilo, je NaN. Hodina se bere, až když je u stanice celá (poslední
    hodnota nejdřív t:45). D.attrs["chybi"] jsou sloupce, kterým chybí nějaká hodina kromě poslední (ta může
    být jen zpožděná). D.attrs["chmu"] je předpověď hladiny od ČHMÚ ({cíl: {čas UTC: cm}}), jen pro srovnání.
    """
    dnes = pd.Timestamp.now(tz="UTC").normalize()
    dny = pd.date_range(end=dnes - pd.Timedelta(days=1), periods=DNU)
    predpony = [f"recent/data/{d:%Y%m%d}_0-203-1-" for d in dny]
    cesty = [(k, p + cislo + ".json") for k, (cislo, _) in (CILE | PROTI_PROUDU).items()
             for p in predpony + ["now/data/0-203-1-"]]
    with ThreadPoolExecutor(8) as pool:
        soubory = list(pool.map(lambda kc: (kc[0], _soubor(kc[1])), cesty))

    casti = {}
    for k, j in soubory:
        for ts in j["objList"][0]["tsList"] if j else []:
            if ts["tsConID"] in ("H", "Q", "H_F") and ts["tsData"]:
                v = pd.DataFrame(ts["tsData"])
                s = pd.Series(pd.to_numeric(v["value"]).to_numpy(), index=pd.to_datetime(v["dt"], utc=True))
                casti.setdefault(f"{k}_{ts['tsConID']}", []).append(s.dropna())
    rady = {}
    for c, seznam in casti.items():
        s = pd.concat(seznam)
        # stejný čas ve více souborech: platí novější soubor (now je v seznamu poslední)
        rady[c] = s[~s.index.duplicated(keep="last")].sort_index()

    hodinove = {}
    for c in SLOUPCE:
        if c in rady and len(rady[c]):
            h = rady[c].resample("h").mean()
            hodinove[c] = h[h.index + pd.Timedelta(minutes=45) <= rady[c].index.max()]
    if not hodinove:
        raise ValueError("ČHMÚ za poslední dny nezveřejnil žádné hodnoty našich stanic.")
    do = max(h.index.max() for h in hodinove.values())
    D = pd.DataFrame(hodinove).reindex(pd.date_range(dnes - pd.Timedelta(days=DNU), do, freq="h"),
                                       columns=SLOUPCE).rename_axis("cas")
    D.attrs["chybi"] = [c for c in SLOUPCE if D[c].iloc[:-1].isna().any()]
    D.attrs["chmu"] = {k: rady.get(f"{k}_H_F", pd.Series(dtype=float)).to_dict() for k in CILE}
    return D


def dopocti(D):
    """Průtok v Mělníku a Nymburce z bilance vody, když v tabulce není celý. Vrátí novou tabulku a co se dopočetlo."""
    D = D.copy()
    dopocteno = [c for c in DOPOCET if D[c].iloc[:-1].isna().any()]
    for c in dopocteno:
        D[c] = DOPOCET[c](D)
    return D, dopocteno


def radek(D, cil):
    """Řádek vstupů jako features.tabulka(cil, h) pro poslední hodinu, kdy jsou všechny vstupy.

    Vstupy jsou pro Děčín i Ústí stejné (jako v features.py), cil je tu kvůli stejnému volání.
    """
    D = D.asfreq("h")
    X = pd.DataFrame(
        {f"{s}_H_{z}": D[f"{s}_H"].shift(z) for s in CILE for z in ZPOZDENI_H}
        | {f"{s}_Q_{z}": D[f"{s}_Q"].shift(z) for s in CILE | PROTI_PROUDU for z in ZPOZDENI_Q}
    ).dropna()
    if X.empty:
        chybi = [_jmeno(c) for c in D if D[c].iloc[-NEJSTARSI - 2:-1].isna().any()]
        raise ValueError(f"V datech není hodina, kdy by byly změřené všechny vstupy modelu "
                         f"(chybí {', '.join(chybi)}).")
    return X.tail(1)


def _jmeno(sloupec):
    k, v = sloupec.rsplit("_", 1)
    return f"{predikce.NAZEV[k]}, {'hladina' if v == 'H' else 'průtok'}"


def predpoved_dnes(nazev="ridge"):
    """Předpověď z nejnovějších dat ČHMÚ. Nikdy nevyhodí výjimku: když to nejde, vrátí ok=False a větu v "chyba".

    Klíče: cas_utc, cas_cesky (hodina vydání t, data t:00 až t:50), stari_h (kolik hodin je to staré),
    upozorneni (věta, když jsou data starší než 3 h, jinak None), chybi a dopocteno (čitelné názvy),
    hladiny (změřená hodinová hladina Děčín a Ústí) a pro "decin" a "usti": ted, stupen_ted,
    predpoved {12: cm, 24: cm, 36: cm}, stupen {h: 0 až 3}, chmu {h: cm nebo None} a radek (vstupy modelu).
    """
    try:
        D = stahni()
        D2, dopocteno = dopocti(D)
        cas = radek(D2, "decin").index[0]
        cesky = cas.tz_convert("Europe/Prague")
        stari = (pd.Timestamp.now(tz="UTC") - cas) / pd.Timedelta(hours=1)
        out = dict(ok=True, chyba=None, model=nazev, cas_utc=cas, cas_cesky=cesky, stari_h=round(stari, 1),
                   upozorneni=(f"Nejnovější úplná data ČHMÚ jsou z {cesky:%d. %m. %H:%M}, tedy {stari:.0f} h stará."
                               if stari > 3 else None),
                   chybi=[_jmeno(c) for c in D.attrs["chybi"]],
                   dopocteno=[_jmeno(c) for c in dopocteno], hladiny=D[[f"{k}_H" for k in CILE]])
        for cil in CILE:
            X = radek(D2, cil)
            ted = float(X[f"{cil}_H_0"].iloc[0])
            pred = predikce.predpoved(nazev, cil, X)
            chmu = D.attrs["chmu"][cil]
            out[cil] = dict(ted=ted, stupen_ted=predikce.stupen(cil, ted), predpoved=pred,
                            stupen={h: predikce.stupen(cil, p) for h, p in pred.items()},
                            chmu={h: chmu.get(cas + pd.Timedelta(hours=h)) for h in pred}, radek=X)
        return out
    except requests.RequestException as e:
        return dict(ok=False, chyba=f"Aktuální data ČHMÚ se nepodařilo stáhnout z opendata.chmi.cz "
                                    f"({type(e).__name__}). Zkuste to za chvíli, mezitím jde přehrávat historie.")
    except Exception as e:  # aplikace má ukázat větu, ne spadnout
        return dict(ok=False, chyba=f"Předpověď z aktuálních dat nejde spočítat: {e}")


if __name__ == "__main__":
    import numpy as np

    # 1) radek z 48 h historie musí dát totéž co features.tabulka
    H = nacti()
    for cil in CILE:
        X = tabulka(cil, 12)[0]
        casy = list(pd.to_datetime(["2011-01-15 08:00", "2013-06-05 12:00", "2025-12-31 11:00"], utc=True))
        casy += list(X.index[np.random.default_rng(42).choice(len(X), 20, replace=False)])
        for t in casy:
            r = radek(H.loc[t - pd.Timedelta(hours=47): t], cil)
            pd.testing.assert_frame_equal(r, X.loc[[t]], check_freq=False)
        print(f"{cil}: radek = features.tabulka v {len(casy)} časech, {X.shape[1]} sloupců ve stejném pořadí")

    # 2) dnešek
    D = stahni()
    print(f"\nstaženo {D.index[0]:%d. %m. %H:%M} až {D.index[-1]:%d. %m. %H:%M} UTC, {len(D)} hodin")
    print("chybí (hodin):", {c: int(D[c].isna().sum()) for c in D.attrs["chybi"]})
    print(D.tail(3).round(1).T.to_string())
    D2, dopocteno = dopocti(D)
    X = radek(D2, "decin")
    assert list(X.columns) == list(tabulka("decin", 12)[0].columns) and X.notna().all(axis=None)
    print(f"řádek vstupů: {X.shape[1]} sloupců jako features.tabulka, bez NaN, dopočteno {dopocteno}")

    for nazev in [m for m in ("ridge", "ridge_vse") if m in predikce.modely()]:
        P = predpoved_dnes(nazev)
        if not P["ok"]:
            print("\nCHYBA:", P["chyba"])
            continue
        print(f"\nPředpověď vydaná {P['cas_cesky']:%d. %m. %Y %H:%M} českého času ({P['cas_utc']:%H:%M} UTC, "
              f"stáří {P['stari_h']} h), model {P['model']}")
        print("chybí:", P["chybi"], "| dopočteno:", P["dopocteno"], "| upozornění:", P["upozorneni"])
        for cil in CILE:
            p = P[cil]
            print(f"{predikce.NAZEV[cil]}: teď {p['ted']:.0f} cm ({predikce.STUPNE[p['stupen_ted']]}); "
                  + ", ".join(f"za {h} h {v:.0f} cm ({predikce.STUPNE[p['stupen'][h]]}, ČHMÚ "
                              f"{'?' if p['chmu'][h] is None else round(p['chmu'][h])})"
                              for h, v in p["predpoved"].items()))
