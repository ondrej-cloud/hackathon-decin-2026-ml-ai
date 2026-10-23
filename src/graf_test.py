"""Graf chybovosti finálního modelu na testu 2021–2025: Děčín a Ústí, 12 / 24 / 36 h.

python src/graf_test.py ridge
"""
import json
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from data import SPA
from porovnej import RESULTS, ROOT

model = sys.argv[1] if len(sys.argv) > 1 else "ridge"


def metriky(m):
    z = json.loads(sorted(RESULTS.glob(f"*_{m}_test.json"))[-1].read_text(encoding="utf-8"))
    return {(r["cil"], r["horizont"]): r for r in z["vysledky"]}


R, J = metriky(model), metriky("jako_ted")
P = pd.read_parquet(RESULTS / "predpovedi" / f"{model}_test.parquet")
kombinace = [(c, h) for c in ("decin", "usti") for h in (12, 24, 36)]
popisky = [f"{'Děčín' if c == 'decin' else 'Ústí'}\nza {h} h" for c, h in kombinace]
do20, klid = [], []
for c, h in kombinace:
    g = P[(P.cil == c) & (P.horizont == h)]
    nad = g.skutecnost >= SPA[c][0]
    do20.append(100 * ((g.predpoved - g.skutecnost).abs()[nad] <= 20).mean())
    klid.append((g.predpoved - g.skutecnost).abs()[~nad].mean())
povodne = [R[k]["mae_povodne"] for k in kombinace]
laťka = [J[k]["mae_povodne"] for k in kombinace]

x = np.arange(len(kombinace))
fig, axs = plt.subplots(1, 3, figsize=(15, 4.8))
axs[0].bar(x - 0.2, laťka, 0.4, color="#999999", label="„bude jako teď“")
axs[0].bar(x + 0.2, povodne, 0.4, color="#3b6ea5", label="lineární regrese")
for i, (a, b) in enumerate(zip(laťka, povodne)):
    axs[0].text(i + 0.2, b + 1, f"{b:.0f}\n−{100 * (1 - b / a):.0f} %", ha="center", fontsize=7)
axs[0].set_title("Průměrná chyba během povodní (cm)")
axs[0].legend(fontsize=8)
axs[1].bar(x, do20, 0.6, color="#3b6ea5")
for i, v in enumerate(do20):
    axs[1].text(i, v + 1, f"{v:.0f} %", ha="center", fontsize=8)
axs[1].set_ylim(0, 100)
axs[1].set_title("Předpovědi přesné do ±20 cm při vodě nad 1. stupněm")
axs[2].bar(x - 0.2, klid, 0.4, color="#8fb3d9", label="klidná voda (pod 1. stupněm)")
axs[2].bar(x + 0.2, povodne, 0.4, color="#3b6ea5", label="povodně")
axs[2].set_title("Chyba v klidu a při povodni (cm)")
axs[2].legend(fontsize=8)
for ax in axs:
    ax.set_xticks(x, popisky, fontsize=8)
fig.suptitle("Finální model na testu 2021–2025 (povodně 2/2021, 12/2023, 2/2024, 9/2024), model je při tréninku neviděl")
fig.tight_layout()
soubor = ROOT / "docs/grafy/test_chybovost.png"
fig.savefig(soubor, dpi=150)
print(f"uloženo {soubor.relative_to(ROOT)}")
