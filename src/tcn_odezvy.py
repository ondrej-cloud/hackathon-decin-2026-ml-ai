"""Naučené odezvy stanic v konvoluční síti (TCN) pro Děčín +24 h, srovnané s vahami lineární regrese.

Natrénuje tcn.fit na trénovací části (seed 42), na validačních řádcích přidá jedné stanici průtoku impulz
+1 směrodatnou odchylku (odmocniny průtoku) v jediné hodině t − k a změří, o kolik cm se změní předpověď.
python src/tcn_odezvy.py    uloží docs/grafy/tcn_odezvy.png a vypíše vrchol odezvy každé stanice
"""
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
import torch

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from data import CILE, PROTI_PROUDU, SPA
from evaluate import casti, vyhodnot
from features import tabulka
from grafy_ridge import vahy
from models import tcn

ROOT = Path(__file__).resolve().parents[1]
CIL, H = "decin", 24
NAZEV = {k: v[1] for k, v in (CILE | PROTI_PROUDU).items()}
STANICE = list(CILE) + list(PROTI_PROUDU)


def odezvy(predict, index):
    """Průměrná změna předpovědi v cm, když je průtok stanice o 1 sm. odch. vyšší jen v hodině t − k."""
    W = predict.vstupy(index)
    okno = W.shape[2]
    out = pd.DataFrame(index=range(okno), columns=STANICE, dtype=float)
    with torch.no_grad():
        zaklad = torch.cat([predict.sit(W[i:i + 4096]) for i in range(0, len(W), 4096)])
        for s in STANICE:
            j = predict.rady.index(f"{s}_Q")
            for k in range(okno):
                W2 = W.clone()
                W2[:, j, okno - 1 - k] += 1
                zmena = torch.cat([predict.sit(W2[i:i + 4096]) for i in range(0, len(W2), 4096)]) - zaklad
                out.loc[k, s] = float(zmena.mean()) * predict.cm
    return out


if __name__ == "__main__":
    X, y = tabulka(CIL, H)
    c = casti(CIL, H).reindex(X.index)
    tr = c == "train"
    predict = tcn.fit(X[tr], y[tr], cil=CIL, horizont=H)
    Xv = X[c == "val"]
    m = vyhodnot(y[c == "val"], predict(Xv), CIL, H)
    print(f"kontrola: val na povodních {m['mae_povodne']} cm, MAE {m['mae']} cm")
    # přeučení: chyba při vysoké vodě (hladina za h nad 1. stupněm) na tréninku a na validaci
    for nazev, Xc, yc in (("trénink", X[tr], y[tr]), ("validace", Xv, y[c == "val"])):
        vysoka = yc >= SPA[CIL][0]
        print(f"{nazev}: MAE {np.abs(predict(Xc) - yc).mean():.1f} cm, "
              f"nad 1. stupněm {np.abs(predict(Xc[vysoka]) - yc[vysoka]).mean():.1f} cm")
    vse = odezvy(predict, Xv.index[::3])
    povodne = odezvy(predict, Xv.index[Xv[f"{CIL}_H_0"] >= SPA[CIL][0]])
    print(f"řádků: celá validace {len(Xv[::3])} (každá 3. hodina), nad 1. stupněm {int((Xv[f'{CIL}_H_0'] >= SPA[CIL][0]).sum())}")
    W = vahy(CIL, H)

    fig, axes = plt.subplots(4, 3, figsize=(13, 12), sharex=True)
    for ax, s in zip(axes.flat, STANICE):
        ax.axhline(0, color="#b5b4ae", lw=1)
        ax.plot(vse.index, vse[s], color="#2a78d6", lw=2, label="síť, celá validace")
        ax.plot(povodne.index, povodne[s], color="#eb6834", lw=2, label="síť, hladina nad 1. stupněm")
        r = W.loc[f"{s}_Q"].dropna()
        ax.plot(r.index, r.to_numpy(), "s", color="#52514e", ms=6, label="lineární regrese (váha zpoždění)")
        ax.set_title(NAZEV[s], fontsize=10)
        ax.grid(axis="y", color="#e6e6e6", lw=0.8)
        ax.spines[["top", "right"]].set_visible(False)
    for ax in axes[-1]:
        ax.set_xlabel("impulz před k hodinami")
        ax.set_xticks([0, 6, 12, 18, 24, 36, 47])
    for ax in axes[:, 0]:
        ax.set_ylabel("změna předpovědi (cm)")
    fig.legend(*axes[0, 0].get_legend_handles_labels(), loc="upper center", ncol=3, frameon=False, fontsize=9,
               bbox_to_anchor=(0.5, 0.945))
    fig.suptitle("Děčín +24 h: o kolik se změní předpověď konvoluční sítě, když je průtok stanice o 1 směrodatnou "
                 "odchylku vyšší\njen v jedné hodině před k hodinami. Čtverce: váhy lineární regrese "
                 "(vstup o 1 sm. odch. vyšší, jen zpoždění 0, 3, 6, 12, 18, 24, 36 h).", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(ROOT / "docs/grafy/tcn_odezvy.png", dpi=150)
    plt.close(fig)

    tab = pd.DataFrame({
        "vrchol_val_h": vse.abs().idxmax(), "vrchol_val_cm": [vse[s][vse[s].abs().idxmax()] for s in STANICE],
        "vrchol_povodne_h": povodne.abs().idxmax(),
        "vrchol_povodne_cm": [povodne[s][povodne[s].abs().idxmax()] for s in STANICE],
        "soucet_val_cm": vse.sum(), "soucet_povodne_cm": povodne.sum(),
        "ridge_0h": [W.loc[f"{s}_Q", 0] for s in STANICE], "ridge_soucet": [W.loc[f"{s}_Q"].sum() for s in STANICE],
    }).round(1)
    print(tab.to_string())
    print("\nodezva po hodinách, celá validace (cm):")
    print(vse.round(1).iloc[:25].to_string())
