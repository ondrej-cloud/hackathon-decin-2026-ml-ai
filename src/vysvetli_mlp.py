"""Podle čeho rozhoduje neuronová síť: důležitost stanic (permutace na validaci) a graf povodně 1/2011."""
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from data import CILE, PROTI_PROUDU
from evaluate import casti, vyhodnot
from features import tabulka
from models import mlp as model

ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]
NAZVY = {k: n for k, (_, n) in (CILE | PROTI_PROUDU).items()}
cil, h = "decin", 24

X, y = tabulka(cil, h)
c = casti(cil, h).reindex(X.index)
tr, ev = c == "train", c == "val"
predict = model.fit(X[tr], y[tr], cil=cil, horizont=h)
zaklad = vyhodnot(y[ev], predict(X[ev]), cil, h)["mae_povodne"]

# všechna zpoždění jedné stanice zamícháme naráz: o kolik se zhorší chyba na povodních
rng = np.random.default_rng(42)
dulezitost = {}
for s in NAZVY:
    for velicina in "HQ":
        cols = [col for col in X if col.startswith(f"{s}_{velicina}_")]
        if not cols:
            continue
        zhorseni = []
        for _ in range(3):
            Xp = X[ev].copy()
            Xp[cols] = Xp[cols].to_numpy()[rng.permutation(len(Xp))]
            zhorseni.append(vyhodnot(y[ev], predict(Xp), cil, h)["mae_povodne"] - zaklad)
        dulezitost[f"{NAZVY[s]}, {'hladina' if velicina == 'H' else 'průtok'}"] = np.mean(zhorseni)
d = pd.Series(dulezitost).sort_values()
print(f"chyba na povodních {zaklad} cm, zhoršení po zamíchání stanice:\n{d.round(1)[::-1].to_string()}")

fig, ax = plt.subplots(figsize=(7, 5))
ax.barh(d.index, d.values, color="#3b6ea5")
ax.set_xlabel("o kolik cm se zhorší chyba na povodních, když stanici zamícháme")
ax.set_title(f"Neuronová síť, Děčín za {h} h: které stanice používá")
fig.tight_layout()
fig.savefig(ROOT / "docs/grafy/mlp_dulezitost_stanic.png", dpi=150)

P = pd.read_parquet(ROOT / "results/predpovedi/mlp.parquet")
P = P[(P.cil == cil) & (P.horizont == h)]
P.index = P.index + pd.Timedelta(hours=h)  # kreslíme v čase, pro který předpověď platí
okno = P["2011-01-08":"2011-01-22"]
ted = X[f"{cil}_H_0"].shift(h, freq="h").reindex(okno.index)
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.plot(okno.index, okno.skutecnost, color="black", lw=2, label="skutečnost")
ax.plot(okno.index, ted, color="#999999", ls="--", label="„bude jako teď“ (o 24 h pozadu)")
ax.plot(okno.index, okno.predpoved, color="#d0632b", lw=1.5, label="neuronová síť, předpověď 24 h předem")
for prah, n in zip((400, 490, 560), (1, 2, 3)):
    ax.axhline(prah, color="#3b6ea5", lw=0.8, alpha=0.6)
    ax.text(okno.index[0], prah + 5, f"{n}. stupeň", color="#3b6ea5", fontsize=8)
ax.set_ylabel("hladina v Děčíně (cm)")
ax.set_title("Povodeň 1/2011, kterou model při tréninku neviděl")
ax.legend(loc="upper left", fontsize=8)
fig.tight_layout()
fig.savefig(ROOT / "docs/grafy/mlp_povoden_2011.png", dpi=150)
print("uloženo docs/grafy/mlp_dulezitost_stanic.png a docs/grafy/mlp_povoden_2011.png")
