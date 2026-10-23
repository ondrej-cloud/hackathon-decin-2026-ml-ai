"""Srovnání modelů v procentech z uložených předpovědí na validaci (results/predpovedi/).

python src/procenta.py ridge mlp lgbm fyzika jako_ted
"""
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from data import SPA
from evaluate import vyhodnot
from porovnej import ROOT

NAZVY = {"jako_ted": "„bude jako teď“", "fyzika": "fyzikální", "ridge": "lineární regrese",
         "lgbm": "LightGBM", "mlp": "neuronová síť"}
modely = sys.argv[1:]
rows = []
for m in modely:
    P = pd.read_parquet(ROOT / "results/predpovedi" / f"{m}.parquet")
    for (cil, h), g in P.groupby(["cil", "horizont"]):
        v = vyhodnot(g.skutecnost, g.predpoved, cil, h)
        hi = g[g.skutecnost >= SPA[cil][0]]
        e = (hi.predpoved - hi.skutecnost).abs()
        rows.append(dict(model=m, cil=cil, h=h, mae_povodne=v["mae_povodne"], do_10=100 * (e <= 10).mean(),
                         do_20=100 * (e <= 20).mean(), povodni=v["spa2_povodni"], propasnuto=v["spa2_propasnuto"],
                         plane=v["spa2_plane_poplachy"]))
R = pd.DataFrame(rows)
R["druh"] = R.model.str.removesuffix("_test")
zaklad = R[R.druh == "jako_ted"].set_index(["cil", "h"]).mae_povodne
R["snizeni"] = 100 * (1 - R.mae_povodne / R.set_index(["cil", "h"]).index.map(zaklad).to_numpy())

S = R.groupby("model", sort=False).agg(chyba=("mae_povodne", "mean"), snizeni=("snizeni", "mean"), do_10=("do_10", "mean"),
                                       do_20=("do_20", "mean"), povodni=("povodni", "sum"), propasnuto=("propasnuto", "sum"),
                                       plane=("plane", "sum"))
S["zachyceno"] = 100 * (1 - S.propasnuto / S.povodni)
S = S.sort_values("chyba")
print("| Model | Chyba na povodních | O kolik menší než „jako teď“ | Do ±10 cm | Do ±20 cm | Zachycené povodně | Plané poplachy |")
print("|---|---|---|---|---|---|---|")
for m, r in S.iterrows():
    print(f"| {NAZVY.get(m.removesuffix('_test'), m)} | {r.chyba:.1f} cm | {r.snizeni:.0f} % | {r.do_10:.0f} % | {r.do_20:.0f} % | "
          f"{r.zachyceno:.0f} % ({r.povodni - r.propasnuto:.0f} z {r.povodni:.0f}) | {r.plane:.0f} |")
H = R.groupby(["model", "h"]).do_20.mean().unstack().loc[S.index]
print("\nDo ±20 cm podle horizontu (%):\n" + H.round(0).to_string())

fig, axs = plt.subplots(1, 2, figsize=(12, 4.5))
uceni = [m for m in S.index if m.removesuffix("_test") != "jako_ted"]
x = np.arange(3)
sirka = 0.8 / len(S.index)
for i, m in enumerate(S.index):
    barva = "#999999" if m.removesuffix("_test") == "jako_ted" else plt.cm.viridis(0.15 + 0.7 * uceni.index(m) / max(1, len(uceni) - 1))
    axs[0].bar(x + (i - (len(S) - 1) / 2) * sirka, H.loc[m], sirka, color=barva, label=NAZVY.get(m.removesuffix("_test"), m))
    if m.removesuffix("_test") != "jako_ted":
        sn = R[R.model == m].groupby("h").snizeni.mean()
        axs[1].bar(x + (uceni.index(m) - (len(uceni) - 1) / 2) * 0.8 / len(uceni), sn, 0.8 / len(uceni), color=barva, label=NAZVY.get(m.removesuffix("_test"), m))
for ax in axs:
    ax.set_xticks(x, ["za 12 h", "za 24 h", "za 36 h"])
    ax.set_ylim(0, 100)
axs[0].set_title("Předpovědi přesné do ±20 cm při vodě nad 1. stupněm (%)")
axs[1].set_title("O kolik menší chyba na povodních než „bude jako teď“ (%)")
axs[0].legend(fontsize=8)
test = all(m.endswith("_test") for m in modely)
fig.suptitle("Test 2021–2025: povodně 2021, 2023 a 2024 (Děčín a Ústí dohromady)" if test else
             "Validace: 4 povodně, které modely při tréninku neviděly (Děčín a Ústí dohromady)")
fig.tight_layout()
nazev = "srovnani_procenta_test.png" if test else "srovnani_procenta.png"
fig.savefig(ROOT / "docs/grafy" / nazev, dpi=150)
print(f"\nuloženo docs/grafy/{nazev}")
