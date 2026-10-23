"""Pokus A: proč Ridge s 30 stanicemi přestřelí v povodni 2006 (a 2011). Příspěvky stanic v čase, kontrola dat.

python pokus_A.py   → vysledky_A.json, prispevky_A_2006.csv, prispevky_A_2011.csv (jen rozbor, nic se neladí)
Příspěvek sloupce = k_i · (x_i − mu_i) / sd_i (StandardScaler + Ridge alpha 1 jako týmová pipeline, z lofo.py).
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, r"C:\Users\danie\Documents\hackathon-2026-ridge\ridge_dan\zlepseni")
import lofo as L  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ZDE = Path(__file__).resolve().parent
CACHE = ZDE.parent / "cache/hydrology/historical/data/hourly"
SKUPINA = {s: g for g, st in L.SKUPINY.items() for s in st} | {
    "decin": "Děčín+Ústí (cíl)", "usti": "Děčín+Ústí (cíl)", "praha": "Vltava tým (Praha, Vraňany)",
    "vranany": "Vltava tým (Praha, Vraňany)", "melnik": "Labe tým (Mělník, Kostelec, Nymburk, Přelouč)",
    "kostelec": "Labe tým (Mělník, Kostelec, Nymburk, Přelouč)", "nymburk": "Labe tým (Mělník, Kostelec, Nymburk, Přelouč)",
    "prelouc": "Labe tým (Mělník, Kostelec, Nymburk, Přelouč)", "louny": "Ohře Louny", "beroun": "Berounka Beroun",
    "sazava": "Sázava Nespeky", "jizera": "Jizera Předměřice"}


def stanice(c):
    return re.sub(r"_(H|Q)_\d+$", "", c)


def model(A, y, maska):
    return L.ridge_z_souctu(L.standardizuj(L.soucty(A, np.asarray(y, dtype=np.float64), maska)))


def prispevky(koef, A_df, casy):
    i, mu, sd, k, b0 = koef
    Z = (A_df.loc[casy].to_numpy(np.float64)[:, i] - mu) / sd * k
    P = pd.DataFrame(Z, index=casy, columns=A_df.columns[i])
    return P.T.groupby(P.columns.map(lambda c: SKUPINA[stanice(c)])).sum().T, P.sum(axis=1) + b0, \
        P.T.groupby(P.columns.map(stanice)).sum().T


def rozbor(od, do, nazev, vysledky, povoden):
    X, y, T = L.zaklad(24)
    A12, _ = L.matice(24)
    A30, _ = L.matice(24, nove=L.NOVE)
    c = L.casti("decin", 24).reindex(X.index)
    tr_val = (c == "train").to_numpy()
    pov = L.povodne_lofo(24)
    k_lofo = next(i for i, p in enumerate(pov) if p["nazev"] == povoden)
    tr_lofo = ~pov[k_lofo]["mezera"]
    casy = y.index[(y.index >= pd.Timestamp(od, tz="UTC")) & (y.index <= pd.Timestamp(do, tz="UTC"))][::6]
    out = {}
    tabulky = []
    for split, tr in (("val", tr_val), ("lofo", tr_lofo)):
        g12, p12, s12 = prispevky(model(A12.to_numpy(), y, tr), A12, casy)
        g30, p30, s30 = prispevky(model(A30.to_numpy(), y, tr), A30, casy)
        # změna příspěvků proti prvnímu času; rozdíl modelů 30 − 12 po skupinách
        d = (g30 - g30.iloc[0]).add_suffix(" [30]")
        roz = g30.sub(g12, fill_value=0.0)
        tab = pd.concat([pd.DataFrame({"y_za24h": y[casy], "pred12": p12, "pred30": p30}), d,
                         roz.add_prefix("30−12: ")], axis=1)
        tab.insert(0, "split", split)
        tabulky.append(tab)
        cas_max = (p30 - y[casy]).idxmax()
        out[split] = dict(
            max_prestreleni_30=round(float((p30 - y[casy]).max()), 1), cas_max_30=str(cas_max),
            max_prestreleni_12=round(float((p12 - y[casy]).max()), 1),
            mae_30=round(float((p30 - y[casy]).abs().mean()), 1), mae_12=round(float((p12 - y[casy]).abs().mean()), 1),
            v_case_max_rozdil_30_12_po_skupinach=roz.loc[cas_max].round(1).sort_values().to_dict(),
            v_case_max_stanice_30_12={k: round(float(v), 1) for k, v in
                                      s30.loc[cas_max].sub(s12.loc[cas_max], fill_value=0).sort_values().items()
                                      if abs(v) >= 5},
            pred30_minus_pred12_v_case_max=round(float(p30[cas_max] - p12[cas_max]), 1))
    pd.concat(tabulky).round(1).to_csv(ZDE / f"prispevky_A_{nazev}.csv", encoding="utf-8")
    vysledky[nazev] = out


def raw_hq(dbc, roky):
    """Surové hodinové stavy a průtoky jedné stanice z cache (HH, QH)."""
    parts = {"H": [], "Q": []}
    for r in roky:
        f = CACHE / f"H_0-203-1-{dbc}_HQ_{r}.json"
        if not f.exists():
            continue
        for ts in json.loads(f.read_text(encoding="utf-8"))["tsList"]:
            v = pd.DataFrame(ts["tsData"]["data"]["values"], columns=["t", "v"])
            parts[ts["tsConID"][0]].append(v)
    return pd.DataFrame({k: pd.concat(v).assign(t=lambda x: pd.to_datetime(x.t, utc=True)).drop_duplicates("t")
                        .set_index("t").v for k, v in parts.items() if v}).sort_index()


def kontrola_dat(vysledky):
    T = L.zaklad(24)[2]
    d = T.loc["2006-03-15":"2006-04-10"].resample("D").mean()
    bil = pd.DataFrame({
        "Praha": d.praha_Q, "Zbraslav+Beroun": d.zbraslav_Q + d.beroun_Q,
        "Nespeky (Sázava)": d.sazava_Q, "Kácov": d.kacov_Q, "Zruč": d.zruc_Q,
        "Louny": d.louny_Q, "Žatec": d.zatec_Q, "K. Vary": d.karlovy_vary_Q,
        "Nymburk": d.nymburk_Q, "Přelouč+Cidlina": d.prelouc_Q + d.sany_Q, "Přelouč": d.prelouc_Q,
        "Orlice+Chrudimka": d.tyniste_Q + d.nemosice_Q, "Beroun": d.beroun_Q, "Zbečno+Litavka": d.zbecno_Q + d.litavka_Q,
        "Mělník": d.melnik_Q, "Vraňany+Kostelec": d.vranany_Q + d.kostelec_Q,
        "Ústí": d.usti_Q, "Mělník+Louny": d.melnik_Q + d.louny_Q, "Děčín": d.decin_Q,
    }).round(0)
    bil.to_csv(ZDE / "bilance_A_2006.csv", encoding="utf-8")
    vysledky["bilance_2006_denni"] = {str(k.date()): v for k, v in bil.iloc[::3].to_dict("index").items()}
    # stav vs průtok podezřelých stanic: odchylka stavu v 3–4/2006 od mediánu stavu při stejném průtoku v jiných letech
    hq = {}
    for dbc, kl in (("165000", "kacov"), ("161000", "zruc"), ("169000", "zbraslav"), ("037000", "tyniste"),
                    ("059000", "nemosice"), ("075000", "sany"), ("216000", "zatec"), ("214000", "karlovy_vary"),
                    ("194500", "zbecno"), ("098000", "bakov")):
        D = raw_hq(dbc, range(2006, 2019)).dropna()
        if "H" not in D or len(D) < 1000:
            hq[kl] = "bez stavu"
            continue
        ref = D[D.index.year >= 2007]
        pasma = np.quantile(ref.Q, np.linspace(0, 1, 41))
        ref_med = ref.groupby(np.clip(np.searchsorted(pasma, ref.Q), 1, 40)).H.median()
        u = D.loc["2006-03-15":"2006-04-10"]
        ocek = ref_med.reindex(np.clip(np.searchsorted(pasma, u.Q), 1, 40)).to_numpy()
        odch = u.H.to_numpy() - ocek
        hq[kl] = dict(median_odchylka_stavu_cm=round(float(np.nanmedian(odch)), 1),
                      max_odchylka_cm=round(float(np.nanmax(np.abs(odch))), 1),
                      hodin=len(u), konstantni_hodnoty_max_h=int(u.Q.groupby((u.Q.diff() != 0).cumsum()).size().max()))
    vysledky["stav_vs_prutok_2006"] = hq


if __name__ == "__main__":
    L.cekej_na_ram(1500)
    vysledky = {}
    rozbor("2006-03-20", "2006-04-08", "2006", vysledky, "2006-04-02")
    rozbor("2011-01-05", "2011-01-22", "2011", vysledky, "2011-01-16")
    kontrola_dat(vysledky)
    (ZDE / "vysledky_A.json").write_text(json.dumps(vysledky, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: v for k, v in vysledky.items() if k != "bilance_2006_denni"}, ensure_ascii=False, indent=1, default=str))
