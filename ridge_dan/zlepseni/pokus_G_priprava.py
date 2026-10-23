"""Podklady pro směsi G: LOFO předpovědi (22 povodní) Ridge 12/30 a LightGBM 30/12 do oof/, skóre do vysledky_lgbm.json.

Formát oof/<model>.parquet: sloupce fold, cas, y, pred; řádky okna foldu v časovém pořadí (= y.index[okno]).
"""
import json
import sys
import time

sys.path.insert(0, r"C:\Users\danie\Documents\hackathon-2026-ridge\ridge_dan\zlepseni")
import lofo as L  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import lgbm_stanice  # noqa: E402

OOF = L.ZDE / "oof"
OOF.mkdir(exist_ok=True)


def uloz(nazev, pred, y, horizont=24):
    pov = L.povodne_lofo(horizont)
    radky = [pd.DataFrame({"fold": k, "cas": y.index[p["okno"]], "y": y[p["okno"]].to_numpy(), "pred": pr})
             for k, (pr, p) in enumerate(zip(pred, pov))]
    pd.concat(radky, ignore_index=True).to_parquet(OOF / f"{nazev}.parquet")
    print("uloženo", nazev, flush=True)


def vycisti(s):
    return {k: (float(v) if isinstance(v, (np.floating,)) else int(v) if isinstance(v, np.integer) else v) for k, v in s.items()}


if __name__ == "__main__":
    L.cekej_na_ram(1500)
    t = time.time()
    A12, y = L.matice(24)
    p12, _ = L.Motor(A12.to_numpy(), y, 24).lofo()
    uloz("ridge_12", p12, y)
    A30, _ = L.matice(24, nove=L.NOVE)
    p30, _ = L.Motor(A30.to_numpy(), y, 24).lofo()
    uloz("ridge_30", p30, y)
    del A12, A30
    print("ridge hotovo", round(time.time() - t), "s", flush=True)

    vysl = []
    L.cekej_na_ram(1500)
    X30 = L.matice(24, nove=L.NOVE, odmocnina=False)[0].astype("float64")
    t = time.time()
    pl30 = L.lofo_obecne(lgbm_stanice.fit_stanice(42), X30, y, 24)
    uloz("lgbm_30", pl30, y)
    print("lgbm_30 hotovo", round(time.time() - t), "s", flush=True)
    del X30
    s30 = L.skore(pl30, 24, zaklad_pred=p12)
    vysl.append(dict(nazev="lgbm_30", popis="LightGBM (lgbm_c) + 18 stanic, seed 42, proti týmovému Ridge", **vycisti(s30)))
    (L.ZDE / "vysledky_lgbm.json").write_text(json.dumps(vysl, ensure_ascii=False, indent=1, default=float), encoding="utf-8")

    L.cekej_na_ram(1500)
    X12 = L.matice(24, odmocnina=False)[0].astype("float64")
    t = time.time()
    pl12 = L.lofo_obecne(lgbm_stanice.fit_tym(42), X12, y, 24)
    uloz("lgbm_12", pl12, y)
    print("lgbm_12 hotovo", round(time.time() - t), "s", flush=True)
    s12 = L.skore(pl12, 24, zaklad_pred=p12)
    s30_12 = L.skore(pl30, 24, zaklad_pred=pl12)
    vysl.append(dict(nazev="lgbm_12", popis="týmový LightGBM (lgbm_c), seed 42, proti týmovému Ridge", **vycisti(s12)))
    vysl.append(dict(nazev="lgbm_30_proti_lgbm_12", popis="LightGBM + 18 stanic proti týmovému LightGBM", **vycisti(s30_12)))
    (L.ZDE / "vysledky_lgbm.json").write_text(json.dumps(vysl, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    for z in vysl:
        print(z["nazev"], {k: z[k] for k in ("lofo", "rozdil", "zlepseno", "nejhorsi_zhorseni", "splnuje", "zacatek", "povoden_2006", "spa2_plane")}, flush=True)
