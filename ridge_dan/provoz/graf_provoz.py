"""Graf živé ukázky: realita, náš model a oficiální předpověď ČHMÚ (H_F), Děčín a Ústí, 24 a 36 h, posledních ~4 týdny.

python graf_provoz.py    → ridge_dan/grafy/provoz_ridge_chmu.png (200 dpi), data z zivy_beh.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

ZDE = Path(__file__).resolve().parent
CACHE = ZDE.parent / "cache/provoz"
PX = 72 / 200
POVRCH, INKOUST, INKOUST_2, MRIZKA = "#fcfcfb", "#0b0b0b", "#52514e", "#e8e7e3"
BARVA = {"tym_ridge": "#2a78d6", "ridge30": "#1baf7a", "chmu": "#eb6834"}
NAZEV = {"decin": "Děčín", "usti": "Ústí nad Labem"}


def c(x):
    return f"{x:.1f}".replace(".", ",")


if __name__ == "__main__":
    P = pd.read_parquet(CACHE / "zive_predpovedi.parquet")
    S = pd.read_csv(ZDE / "zivy_srovnani.csv", parse_dates=["vydani", "cas"])
    plt.rcParams.update({"font.size": 10, "axes.edgecolor": MRIZKA, "axes.labelcolor": INKOUST_2,
                         "xtick.color": INKOUST_2, "ytick.color": INKOUST_2, "text.color": INKOUST})
    fig, osy = plt.subplots(2, 2, figsize=(13, 8.5), facecolor=POVRCH, sharex=True)
    for j, cil in enumerate(("decin", "usti")):
        for i, h in enumerate((24, 36)):
            ax = osy[i, j]
            ax.set_facecolor(POVRCH)
            ax.grid(True, color=MRIZKA, linewidth=PX)
            ax.set_axisbelow(True)
            ax.plot(P.index, P[f"{cil}_H"], color=INKOUST, linewidth=2 * PX, label="realita", zorder=4)
            for model, popis in (("tym_ridge", "týmový Ridge (12 stanic)"), ("ridge30", "Ridge 30 stanic")):
                k = f"{cil}_{h}_{model}"
                if k in P:
                    p = P[k].dropna()
                    ax.plot(p.index + pd.Timedelta(hours=h), p, color=BARVA[model], linewidth=2 * PX,
                            label=f"{popis}, vydáno {h} h předem", zorder=3)
            g = S[(S.cil == cil) & (S.h == h)]
            ax.plot(g.cas, g.chmu, "o", color=BARVA["chmu"], markersize=4.5, markeredgecolor=POVRCH, markeredgewidth=0.6,
                    label=f"ČHMÚ, vydáno v 11:00 UTC, hodnota za {h} h", zorder=5)
            mae = {k: (g[k] - g.realita).abs().mean() for k in ("chmu", "tym_ridge", "ridge30", "jako_ted") if g[k].notna().any()}
            casti = [f"ČHMÚ {c(mae['chmu'])}", f"tým {c(mae['tym_ridge'])}"]
            if "ridge30" in mae:
                casti.append(f"Ridge 30 {c(mae['ridge30'])}")
            casti.append(f"jako teď {c(mae['jako_ted'])}")
            ax.set_title(f"{NAZEV[cil]}, předpověď na {h} h, průměrná chyba ({len(g)} předpovědí z 11:00 UTC)\n"
                         + " · ".join(casti) + " cm", loc="left", fontsize=9.5, color=INKOUST)
            ax.set_ylabel("vodní stav (cm)")
            for s in ("top", "right"):
                ax.spines[s].set_visible(False)
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=4, tz="UTC"))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%d. %m.", tz="UTC"))
    for ax in osy[-1]:
        ax.set_xlabel("datum (UTC), čas, ke kterému předpověď platí")
    h1, l1 = osy[1, 0].get_legend_handles_labels()
    fig.legend(h1, [x.replace(", vydáno 36 h předem", "").replace(", hodnota za 36 h", "") for x in l1], loc="upper center",
               ncol=4, frameon=False, bbox_to_anchor=(0.5, 0.945), fontsize=9.5)
    od, do = P.index.min(), P.index.max()
    fig.suptitle(f"Živá ukázka na provozních datech ČHMÚ ({od:%d. %m.}–{do:%d. %m. %Y}), nízký stav vody", x=0.01, ha="left",
                 y=0.99, fontsize=13, color=INKOUST)
    fig.text(0.01, 0.955, "Data ČHMÚ jsou provozní a neověřená, průtok Mělníka a Nymburka doplněný bilancí. Jen ukázka, "
             "varování vydává ČHMÚ.", fontsize=9, color=INKOUST_2, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.92), h_pad=2.0, w_pad=2.0)
    fig.savefig(ZDE.parent / "grafy/provoz_ridge_chmu.png", dpi=200, facecolor=POVRCH)
