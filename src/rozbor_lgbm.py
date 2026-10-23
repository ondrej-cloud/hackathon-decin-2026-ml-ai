"""Rozbor modelů nad výsledky z porovnej.py, jen validace.

python src/rozbor_lgbm.py tabulka jako_ted zaklad_ridge lgbm_a   chyba proti „jako teď“ a varování před 1.–3. stupněm
python src/rozbor_lgbm.py trenink lgbm_a                        chyba na trénovací části proti validaci (přeučení)
python src/rozbor_lgbm.py graf lgbm_a zaklad_ridge              povodeň 1/2011 v Děčíně za 24 h, do docs/grafy/
python src/rozbor_lgbm.py shap lgbm                             SHAP pro Děčín za 24 h, do docs/grafy/
"""
import importlib
import sys

import matplotlib.pyplot as plt
import pandas as pd

from data import SPA
from evaluate import casti, varovani, vyhodnot
from features import tabulka
from models.lgbm_a import DOBA, nejblizsi
from porovnej import RESULTS, ROOT, VSE, prehled


def srovnani(modely):
    P = prehled().set_index(["model", "cil", "horizont"])
    radky = []
    for m in modely:
        pr = pd.read_parquet(RESULTS / "predpovedi" / f"{m}.parquet")
        for (cil, h), r in P.loc[m].iterrows():
            p = pr[(pr.cil == cil) & (pr.horizont == h)]
            v1 = varovani(p.skutecnost, p.predpoved, SPA[cil][0], h)
            zaklad = P.loc[("jako_ted", cil, h)]
            radky.append(dict(
                model=m, cil=cil, horizont=h, mae=r.mae, mae_povodne=r.mae_povodne,
                zlepseni_pct=round(100 * (1 - r.mae_povodne / zaklad.mae_povodne)),
                mae_nad_1spa=r.mae_nad_1spa, vrcholy=r.vrcholy_o_kolik,
                # předstih h / propásnuto / plané poplachy
                spa1=f"{v1['predstih_h']}/{v1['propasnuto']}/{v1['plane_poplachy']}",
                spa2=f"{r.spa2_predstih_h}/{r.spa2_propasnuto}/{r.spa2_plane_poplachy}",
                spa3=f"{r.spa3_predstih_h}/{r.spa3_propasnuto}/{r.spa3_plane_poplachy}",
            ))
    df = pd.DataFrame(radky)
    print(df.set_index(["cil", "horizont", "model"]).sort_index().to_string())
    print("\nprumer_povodne:\n" + df.groupby("model").mae_povodne.mean().round(1).sort_values().to_string())


def trenink(nazev):
    model = importlib.import_module(f"models.{nazev}")
    for cil, h in VSE:
        X, y = tabulka(cil, h)
        c = casti(cil, h).reindex(X.index)
        predict = model.fit(X[c == "train"], y[c == "train"], cil=cil, horizont=h)
        m = {k: vyhodnot(y[c == k], predict(X[c == k]), cil, h) for k in ("train", "val")}
        print(f"{nazev} {cil} +{h} h  MAE train {m['train']['mae']} / val {m['val']['mae']} cm, "
              f"na povodních train {m['train']['mae_povodne']} / val {m['val']['mae_povodne']} cm")


BARVY = ["#2a78d6", "#eb6834", "#1baf7a"]
INKOUST, MDLY, MRIZKA = "#0b0b0b", "#898781", "#e1e0d9"
NAZVY = {"usti": "Ústí", "louny": "Louny", "melnik": "Mělník", "vranany": "Vraňany", "kostelec": "Kostelec",
         "praha": "Praha", "nymburk": "Nymburk", "jizera": "Jizera", "beroun": "Beroun", "sazava": "Sázava",
         "prelouc": "Přelouč", "decin": "Děčín"}


def vzhled(ax):
    ax.set_facecolor("#fcfcfb")
    ax.grid(color=MRIZKA, lw=0.6)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#c3c2b7")
    ax.tick_params(colors=MDLY, labelsize=8)


def graf(modely, cil="decin", h=24, od="2011-01-08", do="2011-01-23"):
    fig, ax = plt.subplots(figsize=(10, 4.5), facecolor="#fcfcfb")
    vzhled(ax)
    for i, m in enumerate(["jako_ted"] + modely):
        p = pd.read_parquet(RESULTS / "predpovedi" / f"{m}.parquet")
        p = p[(p.cil == cil) & (p.horizont == h)]
        p.index = p.index + pd.Timedelta(hours=h)
        p = p[od:do]
        if i == 0:
            ax.plot(p.index, p.skutecnost, color=INKOUST, lw=2.5, label="skutečnost")
            ax.plot(p.index, p.predpoved, color=MDLY, lw=1.5, ls="--", label="„jako teď“")
        else:
            ax.plot(p.index, p.predpoved, color=BARVY[i - 1], lw=2, label=m)
    for n, prah in enumerate(SPA[cil], 1):
        ax.axhline(prah, color=MDLY, lw=0.8, ls=":")
        ax.text(pd.Timestamp(od, tz="UTC"), prah + 6, f"{n}. stupeň ({prah} cm)", fontsize=8, color=MDLY)
    ax.set_ylabel("stav v Děčíně (cm)", color=INKOUST)
    ax.set_title(f"Povodeň 1/2011 (validace): předpověď vydaná {h} h předem, vynesená k času, na který platí",
                 fontsize=10, color=INKOUST, loc="left")
    ax.legend(loc="upper left", fontsize=8, frameon=False)
    fig.tight_layout()
    soubor = ROOT / "docs/grafy" / f"{modely[0]}_povoden2011.png"
    soubor.parent.mkdir(exist_ok=True)
    fig.savefig(soubor, dpi=130)
    print(f"uloženo {soubor.relative_to(ROOT)}")


def popis(c, cil, h):
    if c.startswith(f"{cil}_H_"):
        return f"{NAZVY[cil]} stav před {c.split('_')[-1]} h"
    if c in ("sezona_sin", "sezona_cos", "trend_6h"):
        return {"sezona_sin": "roční období (sin)", "sezona_cos": "roční období (cos)", "trend_6h": "trend stavu za 6 h"}[c]
    s, co = c.split("_")
    z = nejblizsi(max(DOBA[cil][s] - h, 0))
    return f"{NAZVY[s]} {'přírůstek průtoku' if co == 'dQ' else 'průtok'} (před {z} h)"


def shap_graf(modely, cil="decin", h=24):
    """Podle čeho model rozhoduje: průměrná absolutní hodnota SHAP na validaci a během povodně 1/2011."""
    import shap
    from lightgbm import LGBMRegressor

    model = importlib.import_module(f"models.{modely[0]}")
    X, y = tabulka(cil, h)
    c = casti(cil, h).reindex(X.index)
    V = model.vstupy(X, cil, h)
    m = LGBMRegressor(**model.PARAMETRY).fit(V[c == "train"], (y - X[f"{cil}_H_0"])[c == "train"])
    ev = V[c == "val"]
    S = pd.DataFrame(shap.TreeExplainer(m).shap_values(ev), index=ev.index, columns=V.columns)
    casti_grafu = {"celá validace": S, "povodeň 1/2011": S["2011-01-03":"2011-01-22"]}
    fig, osy = plt.subplots(1, 2, figsize=(11, 5.5), facecolor="#fcfcfb")
    for ax, (nadpis, s) in zip(osy, casti_grafu.items()):
        vzhled(ax)
        d = s.abs().mean().sort_values().tail(12)
        ax.barh([popis(k, cil, h) for k in d.index], d.values, color=BARVY[0], height=0.7)
        ax.set_title(nadpis, fontsize=10, color=INKOUST, loc="left")
        ax.set_xlabel("průměrný vliv na předpověď změny stavu (cm)", fontsize=8, color=MDLY)
        print(f"{nadpis}: " + ", ".join(f"{popis(k, cil, h)} {v:.1f}" for k, v in d[::-1].head(6).items()))
    fig.suptitle(f"{modely[0]}: podle čeho rozhoduje, {NAZVY[cil]} +{h} h (SHAP)", fontsize=11, color=INKOUST, x=0.01,
                 ha="left")
    fig.tight_layout()
    soubor = ROOT / "docs/grafy" / f"{modely[0]}_shap.png"
    fig.savefig(soubor, dpi=130)
    print(f"uloženo {soubor.relative_to(ROOT)}")


if __name__ == "__main__":
    prikaz, *modely = sys.argv[1:]
    {"tabulka": srovnani, "trenink": lambda m: [trenink(x) for x in m], "graf": graf, "shap": shap_graf}[prikaz](modely)
