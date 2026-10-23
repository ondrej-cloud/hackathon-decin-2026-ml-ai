"""Graf vícenásobné validace: chyba každého modelu na každé vynechané povodni (průměr Děčín a Ústí, 12–36 h).

python src/graf_krizova_validace.py   (čte nejnovější results/krizova_validace/*.csv)
"""
import matplotlib.pyplot as plt
import pandas as pd

from data import nacti
from porovnej import ROOT

soubor = sorted((ROOT / "results/krizova_validace").glob("*.csv"))[-1]
R = pd.read_csv(soubor)
P = R.groupby(["povoden", "model"]).chyba.mean().unstack()
P = P.sort_values("ridge")
H = nacti().decin_H
vrchol = {p: int(H[p].max()) for p in P.index}

MODELY = {"jako_ted": ("„bude jako teď“", "#999999", "o"), "fyzika": ("fyzikální", "#eda100", "s"),
          "lgbm": ("LightGBM", "#1baf7a", "^"), "mlp": ("neuronová síť", "#eb6834", "D"),
          "ridge": ("lineární regrese", "#2a78d6", "o")}
radky = list(P.index) + ["průměr"]
P.loc["průměr"] = P.mean()
fig, ax = plt.subplots(figsize=(10, 6))
for i in range(len(radky)):
    ax.axhline(i, color="#e4e4e1", lw=0.6, zorder=0)
for m, (nazev, barva, znacka) in MODELY.items():
    ax.scatter(P.loc[radky, m], range(len(radky)), color=barva, marker=znacka, s=60 if m == "ridge" else 42,
               edgecolor="white", linewidth=1, zorder=3, label=f"{nazev}: {P.loc['průměr', m]:.1f} cm")
ax.axhline(len(radky) - 1.5, color="#52514e", lw=0.8)
ax.set_yticks(range(len(radky)), [f"{p[5:].lstrip('0')}/{p[:4]}, vrchol {vrchol[p]} cm" for p in P.index[:-1]] + ["průměr 8 povodní"])
ax.invert_yaxis()
ax.set_xlim(0, P.max().max() * 1.08)
ax.set_xlabel("průměrná chyba hladiny během povodně (cm), Děčín a Ústí, 12, 24 a 36 h dopředu")
ax.spines[["top", "right", "left"]].set_visible(False)
ax.tick_params(axis="y", length=0)
ax.legend(fontsize=8, loc="upper right", frameon=False)
ax.set_title("Vícenásobná validace: každá povodeň 2006–2020 jednou vynechaná, model učený na ostatních",
             fontsize=11, loc="left")
fig.tight_layout()
cil = ROOT / "docs/grafy/krizova_validace.png"
fig.savefig(cil, dpi=150)
print(f"uloženo {cil.relative_to(ROOT)}")
