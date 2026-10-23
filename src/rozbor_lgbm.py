"""Rozbor modelů nad výsledky z porovnej.py, jen validace.

python src/rozbor_lgbm.py tabulka jako_ted zaklad_ridge lgbm_a   chyba proti „jako teď“ a varování před 1.–3. stupněm
python src/rozbor_lgbm.py trenink lgbm_a                        chyba na trénovací části proti validaci (přeučení)
python src/rozbor_lgbm.py graf lgbm_a zaklad_ridge              povodeň 1/2011 v Děčíně za 24 h, do docs/grafy/
"""
import importlib
import sys

import matplotlib.pyplot as plt
import pandas as pd

from data import SPA
from evaluate import casti, varovani, vyhodnot
from features import tabulka
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


def graf(modely, cil="decin", h=24, od="2011-01-05", do="2011-01-25"):
    fig, ax = plt.subplots(figsize=(10, 4.5))
    for i, m in enumerate(["jako_ted"] + modely):
        p = pd.read_parquet(RESULTS / "predpovedi" / f"{m}.parquet")
        p = p[(p.cil == cil) & (p.horizont == h)]
        p.index = p.index + pd.Timedelta(hours=h)
        p = p[od:do]
        if i == 0:
            ax.plot(p.index, p.skutecnost, color="black", lw=2, label="skutečnost")
        ax.plot(p.index, p.predpoved, lw=1.3, ls="--" if m == "jako_ted" else "-", label=f"{m} (+{h} h)")
    for n, prah in enumerate(SPA[cil], 1):
        ax.axhline(prah, color="grey", lw=0.6, ls=":")
        ax.text(pd.Timestamp(od, tz="UTC"), prah + 5, f"{n}. SPA", fontsize=8, color="grey")
    ax.set_ylabel("stav v Děčíně (cm)")
    ax.set_title(f"Povodeň 1/2011, předpověď na {h} h dopředu (validace)")
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    soubor = ROOT / "docs/grafy" / f"{modely[0]}_povoden2011.png"
    soubor.parent.mkdir(exist_ok=True)
    fig.savefig(soubor, dpi=120)
    print(f"uloženo {soubor.relative_to(ROOT)}")


if __name__ == "__main__":
    prikaz, *modely = sys.argv[1:]
    {"tabulka": srovnani, "trenink": lambda m: [trenink(x) for x in m], "graf": graf}[prikaz](modely)
