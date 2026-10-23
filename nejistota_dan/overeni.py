"""Vnořené ověření pásma nejistoty a uložení kvantilů pro aplikaci.

python overeni.py      tabulky do vysledky/, výběr varianty (předem dané pravidlo), kvantily.json (ze všech 22 povodní)

Vnořeně: pro povodeň k se kvantily berou jen z chyb ostatních 21 povodní (LOFO předpovědi mimo trénink, oof.py)
a hodnotí se na oknech povodně k (7 dní před až 5 dní po vrcholu). Měří se pokrytí (podíl hodin, kdy je skutečnost
v pásmu), šířka a intervalové skóre (šířka + 2/α × o kolik skutečnost pásmo minula; menší = lepší, trestá úzké pásmo,
které míjí, i zbytečně široké). Pravidlo výběru varianty (předem): nejmenší průměrné intervalové skóre přes modely,
cíle, horizonty a obě úrovně, pokud celkové pokrytí žádné kombinace neklesne o víc než 3 p. b. pod nominál.
Základ pro srovnání: dnešní týmové pásmo (src/nejistota.py: kvantily chyb na tréninku podle pásma hladiny teď).
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("OPENBLAS_NUM_THREADS", "4")
ZDE = Path(__file__).resolve().parent
sys.path[:0] = [str(ZDE.parent / "src"), str(ZDE)]

import json  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import nejistota_dan as N  # noqa: E402

OOF = ZDE / "oof"
VYSL = ZDE / "vysledky"
MODELY = ("ridge", "ridge30", "g3")
KOMBINACE = [(c, h) for c in ("decin", "usti") for h in (12, 24, 36)]
VARIANTY = ("globalni", "trend6", "rezim", "rezim_vyska", "zmena6")


def nacti(model, cil, h):
    if model != "g3":
        return pd.read_parquet(OOF / f"{model}_{cil}_{h}.parquet")
    a, b = (pd.read_parquet(OOF / f"{m}_{cil}_{h}.parquet") for m in ("ridge30", "lgbm30"))
    assert (a[["fold", "cas", "y"]].to_numpy() == b[["fold", "cas", "y"]].to_numpy()).all()
    return a.assign(pred=0.5 * a.pred.to_numpy() + 0.5 * b.pred.to_numpy())  # = src/models/g3.py


def tym_trenink(cil, h, uroven):
    """Dnešní týmové pásmo: kvantily chyb týmového Ridge na trénovací části (in-sample) podle pásma hladiny teď."""
    from evaluate import casti
    from features import tabulka
    from models import ridge
    from nejistota import pasmo as pasmo_tym
    X, y = tabulka(cil, h)
    tr = (casti(cil, h).reindex(X.index) == "train").to_numpy()
    m = ridge.pipeline(ridge.PARAMETRY["alpha"]).fit(X[tr], y[tr])
    e = y[tr] - m.predict(X[tr])
    a = (1 - uroven) / 2
    return e.groupby(pasmo_tym(X.loc[tr, f"{cil}_H_0"]), observed=False).quantile([a, 1 - a]).unstack()


def skutecny_vyvoj(D, h):
    """Co se opravdu stalo (pro hodnocení, ne pro pásmo): pokles, klid, vzestup, rychlý vzestup (≥ 50 cm), začátek."""
    d, p = D.y - D.h0, N.PRAH_ZMENY[h]
    s = np.where(d >= 50, "rychly_vzestup", np.where(d >= p, "vzestup", np.where(d <= -p, "pokles", "klid")))
    zac = (d >= 50) & ((D.h0 - D.h6) < 10)
    return s, zac.to_numpy()


def hodnoceni(D, dolni, horni, uroven):
    y = D.y.to_numpy()
    a = 1 - uroven
    uvnitr = (y >= dolni) & (y <= horni)
    skore = (horni - dolni) + 2 / a * (np.clip(dolni - y, 0, None) + np.clip(y - horni, 0, None))
    return uvnitr, horni - dolni, skore


def vnorene(D, varianta, cil, h, uroven):
    """Meze pro každou hodinu okna povodně k z kvantilů chyb ostatních povodní."""
    dolni, horni = np.empty(len(D)), np.empty(len(D))
    s = N.skupina(varianta, cil, h, D.pred, D.h0, D.h6)
    e = (D.y - D.pred).to_numpy()
    f = D.fold.to_numpy()
    for k in np.unique(f):
        kv = N.kvantily_skupin(e[f != k], s[f != k], uroven)
        dolni[f == k], horni[f == k] = N.meze(D.pred.to_numpy()[f == k], s[f == k], kv)
    return dolni, horni, s


def radky_vysledku(D, model, cil, h, varianta, uroven, dolni, horni, s):
    uvnitr, sirka, skore = hodnoceni(D, dolni, horni, uroven)
    skut, zac = skutecny_vyvoj(D, h)
    zakl = dict(model=model, cil=cil, horizont=h, varianta=varianta, uroven=uroven)
    souhrn = zakl | dict(pokryti=uvnitr.mean(), sirka=sirka.mean(), skore=skore.mean(),
                         pokryti_min_povoden=pd.Series(uvnitr).groupby(D.fold.to_numpy()).mean().min(),
                         pokryti_zacatek=uvnitr[zac].mean(), sirka_zacatek=sirka[zac].mean(), n_zacatek=int(zac.sum()))
    for r in ("pokles", "klid", "vzestup", "rychly_vzestup"):
        souhrn[f"pokryti_{r}"] = uvnitr[skut == r].mean()
    povodne = [zakl | dict(povoden=p, pokryti=uvnitr[m].mean(), sirka=sirka[m].mean(), skore=skore[m].mean())
               for p, m in ((p, (D.povoden == p).to_numpy()) for p in D.povoden.unique())]
    rezimy = [zakl | dict(druh="v čase vydání", rezim=r, n=int((s == r).sum()), pokryti=uvnitr[s == r].mean(),
                          sirka=sirka[s == r].mean()) for r in pd.unique(s)]
    rezimy += [zakl | dict(druh="skutečný vývoj", rezim=r, n=int((skut == r).sum()), pokryti=uvnitr[skut == r].mean(),
                           sirka=sirka[skut == r].mean()) for r in ("pokles", "klid", "vzestup", "rychly_vzestup")]
    rezimy += [zakl | dict(druh="skutečný vývoj", rezim="zacatek_vzestupu", n=int(zac.sum()),
                           pokryti=uvnitr[zac].mean(), sirka=sirka[zac].mean())]
    return souhrn, povodne, rezimy


if __name__ == "__main__":
    VYSL.mkdir(exist_ok=True)
    souhrny, povodne, rezimy = [], [], []
    for model in MODELY:
        for cil, h in KOMBINACE:
            D = nacti(model, cil, h)
            for uroven in N.UROVNE:
                for v in VARIANTY:
                    d, u, s = vnorene(D, v, cil, h, uroven)
                    a, b, c = radky_vysledku(D, model, cil, h, v, uroven, d, u, s)
                    souhrny.append(a), povodne.extend(b), rezimy.extend(c)
                if model == "ridge":  # dnešní týmové pásmo z chyb na tréninku
                    q = tym_trenink(cil, h, uroven)
                    from nejistota import pasmo as pasmo_tym
                    p = pasmo_tym(D.h0).astype(str).to_numpy()
                    d = D.pred.to_numpy() + q.iloc[:, 0].reindex(p).to_numpy()
                    u = D.pred.to_numpy() + q.iloc[:, 1].reindex(p).to_numpy()
                    a, b, c = radky_vysledku(D, model, cil, h, "tym_trenink", uroven, d, u, p)
                    souhrny.append(a), povodne.extend(b), rezimy.extend(c)
            print(model, cil, h, "hotovo", flush=True)
    S = pd.DataFrame(souhrny)
    S.round(4).to_csv(VYSL / "souhrn_variant.csv", index=False, encoding="utf-8")
    pd.DataFrame(povodne).round(4).to_csv(VYSL / "pokryti_povodne.csv", index=False, encoding="utf-8")
    pd.DataFrame(rezimy).round(4).to_csv(VYSL / "pokryti_rezimy.csv", index=False, encoding="utf-8")
    # výběr varianty podle předem daného pravidla
    K = S[S.varianta.isin(VARIANTY)]
    ok = K.groupby("varianta").apply(lambda g: bool((g.pokryti >= g.uroven - 0.03).all()), include_groups=False)
    skore = K.groupby("varianta").skore.mean()
    vybrana = skore[ok[ok].index].idxmin()
    print("intervalové skóre (průměr):", skore.round(2).to_dict(), "| pokrytí v toleranci:", ok.to_dict())
    print("vybraná varianta:", vybrana)
    # kvantily pro aplikaci ze všech 22 povodní
    out = dict(varianta=vybrana, popis=N.SKUPINY[vybrana], urovne=list(N.UROVNE), prah_zmeny=N.PRAH_ZMENY,
               prah_vysky=N.PRAH_VYSKY, zdroj="LOFO předpovědi mimo trénink, 22 povodní 2006–2020 (oof.py)", kvantily={})
    for model in MODELY:
        for cil, h in KOMBINACE:
            D = nacti(model, cil, h)
            s = N.skupina(vybrana, cil, h, D.pred, D.h0, D.h6)
            e = (D.y - D.pred).to_numpy()
            out["kvantily"][f"{model}_{cil}_{h}"] = {
                str(u): {k: [round(v[0], 1), round(v[1], 1)] for k, v in N.kvantily_skupin(e, s, u).items()}
                for u in N.UROVNE}
    N.KVANTILY.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("uloženo", N.KVANTILY.name)
