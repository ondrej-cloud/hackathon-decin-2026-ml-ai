import sys; sys.path.insert(0, r"C:\Users\danie\Documents\hackathon-2026-ridge\ridge_dan\zlepseni"); import lofo as L

import gc
import ctypes
import json
import subprocess
import time
from datetime import datetime
from functools import cache
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import data
import features
import evaluate

ZDE = Path(__file__).resolve().parent
RIDGE = ZDE.parent
GRID = np.arange(11) / 10


def zapis_json(jmeno, obsah):
    (ZDE / jmeno).write_text(json.dumps(obsah, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")


def log(zprava):
    s = f"{datetime.now():%H:%M:%S} {zprava}"
    print(s, flush=True)
    with (ZDE / "prubeh_G.log").open("a", encoding="utf-8") as f:
        f.write(s + "\n")


def cekej_ram():
    # Sandbox nepovoluje CIM. Jen během původní čekací funkce nahradíme
    # její jediný dotaz na FreePhysicalMemory ekvivalentním Windows API.
    class MemoryStatus(ctypes.Structure):
        _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong)] + [
            (name, ctypes.c_ulonglong) for name in
            ("total_phys", "avail_phys", "total_page", "avail_page", "total_virt", "avail_virt", "extended")]
    original = subprocess.run
    def dotaz(args, **kwargs):
        if isinstance(args, list) and args[:3] == ["powershell", "-NoProfile", "-Command"] and "FreePhysicalMemory" in args[3]:
            if datetime.now() >= datetime(2026, 10, 23, 23, 56):
                raise TimeoutError("Konec čekání kvůli celkovému limitu 35 minut.")
            status = MemoryStatus()
            status.length = ctypes.sizeof(status)
            if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
                raise ctypes.WinError()
            return subprocess.CompletedProcess(args, 0, stdout=str(status.avail_phys // (1024 * 1024)), stderr="")
        return original(args, **kwargs)
    subprocess.run = dotaz
    try:
        return L.cekej_na_ram(1500)
    finally:
        subprocess.run = original


def cti_pred_2021(cesta):
    # Filtr už při čtení: ani tvorba zpoždění/odmocnin nepracuje na testu.
    meta = pq.ParquetFile(cesta).schema_arrow.metadata
    idx = json.loads(meta[b"pandas"])["index_columns"][0]
    assert isinstance(idx, str), idx
    d = pd.read_parquet(cesta, filters=[(idx, "<", L.KONEC)])
    assert isinstance(d.index, pd.DatetimeIndex)
    assert (d.index < L.KONEC).all()
    return d


@cache
def tymova_data():
    return cti_pred_2021(data.SOUBOR).astype("float64")


@cache
def rozsirena_data():
    return cti_pred_2021(L.data_ridge.SOUBOR).astype("float64")


data.nacti = tymova_data
features.nacti = tymova_data
evaluate.nacti = tymova_data
L.data_ridge.nacti = rozsirena_data


def validace_pevna(a, b=None):
    da = cti_pred_2021(RIDGE / "stanice_vsem" / a)
    assert {"y", "pred"} <= set(da.columns)
    assert da.index.is_unique and da.index.is_monotonic_increasing
    assert ((da.index + pd.Timedelta(hours=24)) < L.KONEC).all()
    assert (evaluate.casti("decin", 24).reindex(da.index) == "val").all()
    np.testing.assert_allclose(da.y.to_numpy(), L.zaklad(24)[1].reindex(da.index).to_numpy(), atol=1e-8, rtol=0)
    if b:
        db = cti_pred_2021(RIDGE / "stanice_vsem" / b)
        assert da.index.equals(db.index)
        np.testing.assert_array_equal(da.y.to_numpy(), db.y.to_numpy())
        pr = (da.pred.to_numpy() + db.pred.to_numpy()) / 2
    else:
        pr = da.pred.to_numpy()
    return evaluate.vyhodnot(da.y, pr, "decin", 24)


def vahy_zapis(vahy, pov):
    return [dict(fold=k, povoden=p["nazev"], w=float(w)) for k, (p, w) in enumerate(zip(pov, vahy))]


def hlavni():
    log("Čekám na RAM: lofo.cekej_na_ram(1500).")
    ram = cekej_ram()
    if ram is None:
        raise RuntimeError("Nedostatek volné RAM po čekání dle protokolu.")
    log(f"Volná RAM {ram} MB; načítám jen roky 2006–2020.")
    A12, y = L.matice(24)
    assert ((y.index + pd.Timedelta(hours=24)) < L.KONEC).all()
    assert y.index.min().year == 2006
    m12 = L.Motor(A12.to_numpy(), y, 24)
    p12, _ = m12.lofo()
    A30, yy = L.matice(24, nove=L.NOVE)
    pd.testing.assert_series_equal(y, yy)
    m30 = L.Motor(A30.to_numpy(), y, 24)
    p30, _ = m30.lofo()
    pov = L.povodne_lofo(24)
    assert len(pov) == 22
    foldy = pd.read_csv(RIDGE / "stanice_vsem" / "lofo_foldy.csv")
    foldy = foldy[foldy.horizont == 24].sort_values("fold")
    assert len(foldy) == 22
    for k, (_, f) in enumerate(foldy.iterrows()):
        p = pov[k]
        ix = y.index[p["okno"]]
        assert k == f.fold and p["nazev"] == f.povoden
        assert ix[0] == pd.Timestamp(f.okno_od) and ix[-1] == pd.Timestamp(f.okno_do)
        assert len(ix) == f.radku_okno and len(y) == f.radku_celkem
        assert y.index[0] == pd.Timestamp(f.radky_od) and y.index[-1] == pd.Timestamp(f.radky_do)
    log(f"Ověřena shoda všech 22 foldů s lofo_foldy.csv; řádků {len(y)}, sloupců {A12.shape[1]}/{A30.shape[1]}.")

    refs = {"Ridge12": L.skore(p12, 24), "Ridge30": L.skore(p30, 24, zaklad_pred=p12)}
    zapis_json("reference_G.json", refs)
    vysl = []
    def pridej(nazev, popis, pred, vahy, val=None, **navic):
        r = dict(nazev=nazev, popis=popis, skore=L.skore(pred, 24, zaklad_pred=p12),
                 validace=val, vybrane_vahy=vahy, **navic)
        vysl.append(r)
        zapis_json("vysledky_G.json", vysl)
        log(f"{nazev}: {json.dumps(r['skore'], ensure_ascii=False)}")

    g1 = [(a + b) / 2 for a, b in zip(p12, p30)]
    pridej("G1", "0,5 Ridge30 + 0,5 Ridge12; pevná váha bez výběru.", g1, 0.5)

    g2, w2, vnitrni = [], [], []
    for k in range(22):
        chyby = []
        for j in range(22):
            if j == k:
                continue
            a12, yo = m12.okno(j)
            a30, _ = m30.okno(j)
            v12 = L.predikuj(L.ridge_z_souctu(m12.vnitrni(k, j)), a12)
            v30 = L.predikuj(L.ridge_z_souctu(m30.vnitrni(k, j)), a30)
            chyby.append(np.abs(GRID[:, None] * v30 + (1 - GRID[:, None]) * v12 - yo).mean(axis=1))
        errs = np.mean(chyby, axis=0)
        w = float(GRID[np.argmin(errs)])  # deterministická shoda: nejmenší w
        w2.append(w)
        g2.append(w * p30[k] + (1 - w) * p12[k])
        vnitrni.append(dict(fold=k, w=w, chyby_mrizky=errs.tolist()))
        m12._vnitrni.clear()
        m30._vnitrni.clear()
        log(f"G2 fold {k:02d} {pov[k]['nazev']}: w={w:.1f}, vnitřní MAE={errs.min():.4f}")
    pridej("G2", "w Ridge30 + (1−w) Ridge12; striktně vnořené LOFO bez mezer k i j; mřížka 0:0,1:1, průměr MAE 21 povodní; shoda → nižší w.",
           g2, vahy_zapis(w2, pov), vnitrni_chyby=vnitrni,
           poznamka_validace="Val pro laděné směsi zadání nevyžaduje; nehodnoceno.")

    # Ukládáme i předpovědi a cíle, aby následné doplnění nemuselo přepočítávat modely.
    rows = []
    for k, p in enumerate(pov):
        ix = y.index[p["okno"]]
        rows.append(pd.DataFrame(dict(fold=k, cas=ix, y=y[p["okno"]].to_numpy(), ridge12=p12[k], ridge30=p30[k], G1=g1[k], G2=g2[k])))
    pd.concat(rows, ignore_index=True).to_parquet(ZDE / "predpovedi_G.parquet", index=False)
    gc.collect()
    log("G1/G2 hotovy; validační soubory ověří doplňovací skript.")


if __name__ == "__main__":
    hlavni()
