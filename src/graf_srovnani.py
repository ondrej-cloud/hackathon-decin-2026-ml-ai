"""Graf srovnání modelů: chyba na povodních pro každý cíl a horizont (poslední výsledky z results/)."""
import sys

import matplotlib.pyplot as plt
import numpy as np

from porovnej import ROOT, prehled

modely = sys.argv[1:] or None
df = prehled()
if modely:
    df = df[df.model.isin(modely)]
poradi = df.groupby("model").mae_povodne.mean().sort_values(ascending=False).index
kombinace = [(c, h) for c in ("decin", "usti") for h in (12, 24, 36)]
nazvy = {"decin": "Děčín", "usti": "Ústí"}
MODELY = {"jako_ted": "„bude jako teď“", "fyzika": "fyzikální (Tobias)", "ridge": "lineární regrese (Honza)",
          "lgbm": "LightGBM (Dan)", "lgbm_c": "LightGBM (Dan)", "mlp": "neuronová síť (Ondra)"}

fig, ax = plt.subplots(figsize=(10, 4.8))
sirka = 0.8 / len(poradi)
barvy = plt.cm.viridis(np.linspace(0.15, 0.85, len(poradi)))
for i, (m, barva) in enumerate(zip(poradi, barvy)):
    r = df[df.model == m].set_index(["cil", "horizont"]).mae_povodne
    hodnoty = [r.get(k, np.nan) for k in kombinace]
    x = np.arange(len(kombinace)) + (i - (len(poradi) - 1) / 2) * sirka
    ax.bar(x, hodnoty, sirka, label=f"{MODELY.get(m, m)}: průměr {np.nanmean(hodnoty):.1f} cm",
           color="#999999" if m == "jako_ted" else barva)
ax.set_xticks(np.arange(len(kombinace)), [f"{nazvy[c]} +{h} h" for c, h in kombinace])
ax.set_ylabel("průměrná chyba na povodních (cm)")
ax.set_title("Chyba předpovědi hladiny na 4 povodních, které modely neviděly (validace)")
ax.legend(fontsize=8)
fig.tight_layout()
nazev = "srovnani_modelu.png" if not modely else f"srovnani_{'_'.join(modely)}.png"
fig.savefig(ROOT / "docs/grafy" / nazev, dpi=150)
print(f"uloženo docs/grafy/{nazev}")
