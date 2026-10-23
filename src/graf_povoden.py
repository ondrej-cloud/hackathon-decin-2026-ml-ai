"""Graf jedné validační povodně: skutečnost a předpovědi vybraných modelů vydané h hodin předem.

python src/graf_povoden.py 2011-01-08 2011-01-22 decin 24 jako_ted fyzika ridge lgbm_c mlp
"""
import sys

import matplotlib.pyplot as plt
import pandas as pd

from data import SPA
from porovnej import ROOT

od, do, cil, h, *modely = sys.argv[1:]
h = int(h)
NAZVY = {"jako_ted": "„bude jako teď“", "fyzika": "fyzikální (Tobias)", "ridge": "lineární regrese (Honza)",
         "lgbm_c": "LightGBM (Dan)", "mlp": "neuronová síť (Ondra)"}
fig, ax = plt.subplots(figsize=(10, 5))
for i, m in enumerate(modely):
    P = pd.read_parquet(ROOT / "results/predpovedi" / f"{m}.parquet")
    P = P[(P.cil == cil) & (P.horizont == h)]
    P.index = P.index + pd.Timedelta(hours=h)  # čas, pro který předpověď platí
    P = P[od:do]
    if i == 0:
        ax.plot(P.index, P.skutecnost, color="black", lw=2.5, label="skutečnost")
    ax.plot(P.index, P.predpoved, lw=1.3, ls="--" if m == "jako_ted" else "-",
            color="#999999" if m == "jako_ted" else None, label=NAZVY.get(m, m))
for n, prah in enumerate(SPA[cil], 1):
    ax.axhline(prah, color="#3b6ea5", lw=0.8, alpha=0.5)
    ax.text(pd.Timestamp(od, tz="UTC"), prah + 5, f"{n}. stupeň", color="#3b6ea5", fontsize=8)
ax.set_ylabel(f"hladina {'v Děčíně' if cil == 'decin' else 'v Ústí'} (cm)")
ax.set_title(f"Povodeň {pd.Timestamp(od):%m/%Y}, předpověď {h} h předem (model ji při tréninku neviděl)")
ax.legend(fontsize=8, loc="upper left")
fig.tight_layout()
soubor = ROOT / "docs/grafy" / f"povoden_{od[:7]}_{cil}_{h}h.png"
fig.savefig(soubor, dpi=150)
print(f"uloženo {soubor.relative_to(ROOT)}")
