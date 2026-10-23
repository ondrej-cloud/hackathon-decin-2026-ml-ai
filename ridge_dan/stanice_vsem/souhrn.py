"""Souhrnná tabulka z vysledky.jsonl: model × varianta × (CV, validace, začátek vzestupu, 2006, poplachy).

python souhrn.py    poslední záznam každé varianty a seedu; u seedů průměr a rozptyl (směrodatná odchylka)
"""
import json

import numpy as np
import pandas as pd

import spolecne as S

BLOKY = {(2006, 2007): "2006–07", (2008, 2009): "2008–09", (2010, 2011): "2010–11", (2012, 2013): "2012–13",
         (2014, 2015): "2014–15", (2016, 2018): "2016–18"}
DVOJICE = [("ridge_12", "ridge_30"), ("ridge_bez_odmocniny_12", "ridge_bez_odmocniny_30"),
           ("ridge_bez_odmocniny_12", "ridge_12"), ("lgbm_12", "lgbm_30"), ("fyzika_12", "fyzika_30")]


def nacti():
    posl = {}
    for r in (S.ZDE / "vysledky.jsonl").read_text(encoding="utf-8").splitlines():
        z = json.loads(r)
        if z["seed"] in (None, 42):  # LightGBM po opravě jen seed 42 (43 a 44 dávaly totéž)
            posl[(z["varianta"], z["seed"], z["cast"])] = z
    return posl


def radek(zz):
    """Hodnoty jedné varianty přes seedy: průměr, a když je seedů víc, i směrodatná odchylka."""
    cv = [z for z in zz if z["cast"] == "cv"]
    va = [z for z in zz if z["cast"] == "val"]
    hodnoty = {
        "CV povodně": [z["cv_povodne"] for z in cv], "CV velké": [z["cv_velke"] for z in cv],
        "CV vzestup": [z["cv_vzestup"] for z in cv],
        "CV přestřelení p95/max": [f"{z['cv_p95_prestreleni']:.0f}/{z['cv_max_prestreleni']:.0f}" for z in cv
                                   if "cv_p95_prestreleni" in z],
        "VAL prumer_povodne": [z["prumer_povodne"] for z in va],
        "VAL Děčín +24": [z["decin24"]["mae_povodne"] for z in va],
        "VAL začátek vzestupu": [z["decin24"]["mae_zacatek"] for z in va],
        "VAL vzestup": [z["decin24"]["mae_vzestup"] for z in va],
        "VAL 2006": [z["decin24"]["mae_2006"] for z in va],
        "VAL 2006 přestřelení": [z["decin24"]["max_prestreleni_2006"] for z in va],
        "2./3. SPA propásnuto": [f"{z['spa2_propasnuto']}/{z['spa3_propasnuto']}" for z in va],
        "2./3. SPA plané": [f"{z['spa2_plane']}/{z['spa3_plane']}" for z in va],
        "2./3. SPA předstih h": [f"{z['spa2_predstih_h']}/{z['spa3_predstih_h']}" for z in va],
        "seedů": [len(va)],
    }
    out = {}
    for k, v in hodnoty.items():
        if v and isinstance(v[0], str):
            out[k] = v[0] if len(set(v)) == 1 else " | ".join(v)
        elif v:
            out[k] = f"{np.mean(v):.2f}" + (f" ± {np.std(v, ddof=1):.2f}" if len(v) > 1 else "")
    return out


def stabilita(posl):
    """Rozdíl CV povodně (+ stanice − beze změny) přes povodně a přes bloky let, směrodatná chyba, kolik bloků lepších."""
    def ud(v):
        zz = [z for (n, s, c), z in posl.items() if n == v and c == "cv"]
        return pd.DataFrame([z["cv_udalosti"] for z in zz]).mean() if zz else None
    radky = []
    for a, b in DVOJICE:
        A, B = ud(a), ud(b)
        if A is None or B is None:
            continue
        d = B - A
        blok = pd.Series([next(v for (x, y), v in BLOKY.items() if x <= int(k[:4]) <= y) for k in d.index], index=d.index)
        db = d.groupby(blok).mean()
        radky.append(dict(srovnani=f"{b} − {a}", pres_povodne=f"{d.mean():+.2f} ± {d.std() / np.sqrt(len(d)):.2f}",
                          pres_bloky=f"{db.mean():+.2f} ± {db.std() / np.sqrt(len(db)):.2f}",
                          lepsi_bloku=f"{int((db < 0).sum())} z {len(db)}"))
    return pd.DataFrame(radky)


if __name__ == "__main__":
    posl = nacti()
    varianty = list(dict.fromkeys(n for n, _, _ in posl))
    t = pd.DataFrame({v: radek([z for (n, s, c), z in posl.items() if n == v]) for v in varianty}).T
    pd.set_option("display.width", 250)
    print(t.to_string())
    print()
    print(stabilita(posl).to_string(index=False))
