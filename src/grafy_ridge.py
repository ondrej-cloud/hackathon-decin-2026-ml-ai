"""Grafy k lineárnímu modelu (ridge): váhy podle stanice a zpoždění, validační povodně, chyba trénink proti validaci.

python src/grafy_ridge.py    uloží docs/grafy/ridge_vahy_<cil>.png a docs/grafy/ridge_povodne_decin_24h.png
"""
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from data import CILE, PROTI_PROUDU, SPA
from evaluate import casti
from features import tabulka
from models import ridge

ROOT = Path(__file__).resolve().parents[1]
GRAFY = ROOT / "docs/grafy"
RADKY = [("decin", "H"), ("usti", "H")] + [(s, "Q") for s in list(CILE) + list(PROTI_PROUDU)]
ZPOZDENI = (0, 1, 2, 3, 6, 12, 18, 24, 36)
NAZEV = {k: v[1] for k, v in (CILE | PROTI_PROUDU).items()}
POVODNE = (("4/2006", "2006-03-25", "2006-04-10"), ("1/2011", "2011-01-08", "2011-01-24"))


def vahy(cil, horizont):
    """Váhy na škálovaných vstupech (cm na jednu směrodatnou odchylku vstupu), tabulka stanice × zpoždění."""
    X, y = tabulka(cil, horizont)
    tr = casti(cil, horizont).reindex(X.index) == "train"
    model = ridge.pipeline(ridge.PARAMETRY["alpha"]).fit(X[tr], y[tr])
    W = pd.DataFrame(np.nan, index=[f"{s}_{v}" for s, v in RADKY], columns=list(ZPOZDENI))
    for c, w in zip(X.columns, model[-1].coef_):
        s, v, z = c.split("_")
        W.loc[f"{s}_{v}", int(z)] = w
    return W


def graf_vah(cil):
    tabulky = {h: vahy(cil, h) for h in (12, 24, 36)}
    m = max(t.abs().max().max() for t in tabulky.values())
    fig, axes = plt.subplots(1, 3, figsize=(16, 7), sharey=True)
    for ax, (h, W) in zip(axes, tabulky.items()):
        ax.set_facecolor("#e6e6e6")
        im = ax.imshow(np.ma.masked_invalid(W.to_numpy()), cmap="RdBu_r", vmin=-m, vmax=m, aspect="auto")
        ax.set_xticks(range(len(ZPOZDENI)), [str(z) for z in ZPOZDENI])
        ax.set_xlabel("vstup změřený před (h)")
        ax.set_title(f"předpověď za {h} h")
        for i in range(W.shape[0]):
            for j in range(W.shape[1]):
                v = W.iat[i, j]
                if not np.isnan(v):
                    ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=7,
                            color="white" if abs(v) > 0.55 * m else "black")
    axes[0].set_yticks(range(len(RADKY)), [f"{NAZEV[s]}, {'hladina' if v == 'H' else 'průtok'}" for s, v in RADKY])
    fig.colorbar(im, ax=axes, shrink=0.8, label="váha (cm): o kolik se změní předpověď, když je vstup o 1 směrodatnou odchylku vyšší")
    fig.suptitle(f"{NAZEV[cil]}: váhy lineárního modelu. Kladná (červená) zvedá předpověď, záporná (modrá) snižuje, "
                 "šedá = zpoždění není ve vstupech")
    fig.savefig(GRAFY / f"ridge_vahy_{cil}.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    return tabulky


def graf_povodni(cil="decin", horizont=24):
    P = {m: pd.read_parquet(ROOT / "results/predpovedi" / f"{m}.parquet") for m in ("ridge", "jako_ted")}
    P = {m: p[(p.cil == cil) & (p.horizont == horizont)] for m, p in P.items()}
    fig, axes = plt.subplots(1, len(POVODNE), figsize=(15, 5.5))
    for ax, (nazev, od, do) in zip(axes, POVODNE):
        r, j = P["ridge"][od:do], P["jako_ted"][od:do]
        t = r.index + pd.Timedelta(hours=horizont)  # předpověď vydaná v cas_vydani platí pro cas_vydani + horizont
        ax.plot(t, r.skutecnost, color="black", lw=2, label="skutečná hladina")
        ax.plot(t, j.predpoved, color="gray", ls="--", label="„bude jako teď“")
        ax.plot(t, r.predpoved, color="tab:blue", lw=1.8, label=f"lineární model, vydáno {horizont} h předem")
        for n, (spa, barva) in enumerate(zip(SPA[cil], ("goldenrod", "darkorange", "red")), 1):
            ax.axhline(spa, color=barva, lw=1, ls=":")
            ax.text(t[0], spa + 6, f"{n}. stupeň povodňové aktivity", color=barva, fontsize=8)
        ax.set_title(f"Povodeň {nazev}, {NAZEV[cil]}")
        ax.set_ylabel("hladina (cm)")
        ax.legend(loc="lower right")
    fig.autofmt_xdate()
    fig.savefig(GRAFY / f"ridge_povodne_{cil}_{horizont}h.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def trenink_proti_validaci():
    radky = []
    for cil in CILE:
        for h in (12, 24, 36):
            X, y = tabulka(cil, h)
            c = casti(cil, h).reindex(X.index)
            tr, va = c == "train", c == "val"
            predict = ridge.fit(X[tr], y[tr], cil, h)
            radky.append(dict(cil=cil, horizont=h, mae_train=round(float(np.abs(predict(X[tr]) - y[tr]).mean()), 1),
                              mae_val=round(float(np.abs(predict(X[va]) - y[va]).mean()), 1)))
    return pd.DataFrame(radky)


if __name__ == "__main__":
    GRAFY.mkdir(exist_ok=True)
    for cil in CILE:
        for h, W in graf_vah(cil).items():
            top = W.stack().abs().sort_values(ascending=False).head(6)
            print(f"{cil} +{h} h, největší váhy:", ", ".join(f"{s}[-{z} h] {W.loc[s, z]:+.0f}" for s, z in top.index))
    graf_povodni()
    print("\nchyba trénink proti validaci (cm, všechny hodiny):")
    print(trenink_proti_validaci().to_string(index=False))
    print(f"\ngrafy v {GRAFY.relative_to(ROOT)}")
