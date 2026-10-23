"""Kolik let dat model potřebuje: chyba Ridge na validačních povodních podle délky tréninku a sady stanic.

Trénink je posledních N let před validací (2019 − N až 2018 z části train), validace je stejná jako v porovnej.py.
Sada „jen kraj“ jsou stanice z balíčku pořadatelů (Děčín, Ústí, Louny), „všechny stanice“ je všech 98 sloupců.

python src/kolik_dat.py    uloží docs/grafy/kolik_dat.png a vypíše tabulku
"""
from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from data import CILE, SPA, nacti
from evaluate import casti, vyhodnot
from features import tabulka
from models import ridge

ROOT = Path(__file__).resolve().parents[1]
GRAF = ROOT / "docs/grafy/kolik_dat.png"
LETA = (1, 2, 3, 5, 8, 13)
KRAJ = ("decin", "usti", "louny")
SADY = {"jen kraj (Děčín, Ústí, Louny, jako balíček)": lambda sl: [c for c in sl if c.split("_")[0] in KRAJ],
        "všechny stanice (12, i Vltava a horní Labe)": lambda sl: list(sl)}
JAKO_TED = 44.3


def spocitej():
    H = nacti()["decin_H"]
    radky = []
    for cil in CILE:
        for h in (12, 24, 36):
            X, y = tabulka(cil, h)
            c = casti(cil, h).reindex(X.index)
            tr, va = c == "train", c == "val"
            for n in LETA:
                trn = tr & (X.index >= pd.Timestamp(f"{2019 - n}-01-01", tz="UTC"))
                nad2 = int((H.reindex(X.index[trn]) >= SPA["decin"][1]).sum())
                for sada, vyber in SADY.items():
                    predict = ridge.fit(X[trn], y[trn], cil, h, sloupce=vyber(X.columns))
                    m = vyhodnot(y[va], predict(X[va]), cil, h)
                    radky.append(dict(cil=cil, horizont=h, let=n, sada=sada, radku=int(trn.sum()),
                                      hodin_nad_2spa_decin=nad2, mae_povodne=m["mae_povodne"],
                                      spa2_propasnuto=m["spa2_propasnuto"], spa2_plane=m["spa2_plane_poplachy"]))
    return pd.DataFrame(radky)


def graf(T):
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for (sada, t), barva in zip(T.groupby(level="sada"), ("tab:gray", "tab:blue")):
        t = t.droplevel("sada")
        ax.plot(t.index, t.prumer_povodne, marker="o", color=barva, lw=2, label=sada)
        for n, v in t.prumer_povodne.items():
            ax.annotate(f"{v:.0f}", (n, v), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9, color=barva)
            if t.propasnuto[n]:
                ax.annotate(f"propásne {int(t.propasnuto[n])} z 24", (n, v), textcoords="offset points", xytext=(0, -14),
                            ha="center", fontsize=7, color=barva, style="italic")
    ax.axhline(JAKO_TED, color="black", ls="--", lw=1)
    ax.text(LETA[-1], JAKO_TED - 1, "„bude jako teď“ (44,3 cm, propásne všechny)", ha="right", va="top", fontsize=9)
    ax.set_xticks(LETA)
    ax.set_xlabel("roky historie v tréninku (před validací, 2019 − N až 2018)")
    ax.set_ylabel("chyba na povodních (cm, průměr 6 kombinací)")
    ax.set_title("Kolik let dat model potřebuje: víc stanic pomohlo víc než víc let")
    ax.set_ylim(0, max(JAKO_TED, T.prumer_povodne.max()) * 1.15)
    ax.grid(alpha=0.3)
    ax.legend(loc="lower left")
    fig.savefig(GRAF, dpi=150, bbox_inches="tight")


if __name__ == "__main__":
    df = spocitej()
    T = df.groupby(["sada", "let"]).agg(prumer_povodne=("mae_povodne", "mean"), propasnuto=("spa2_propasnuto", "sum"),
                                        plane_poplachy=("spa2_plane", "sum"), radku=("radku", "min"),
                                        hodin_nad_2spa_decin=("hodin_nad_2spa_decin", "min")).round(1)
    print(T.to_string())
    graf(T)
    print(f"\ngraf {GRAF.relative_to(ROOT)}")
