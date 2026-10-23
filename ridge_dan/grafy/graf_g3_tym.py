"""Realita vs týmový Ridge (12 stanic) vs G3 (½ Ridge 30 + ½ LightGBM 30), Děčín +24 h, 6 největších povodní 2006–2020.

python graf_g3_tym.py    → srovnani_g3_tym_povodne.png (200 dpi)

Předpovědi jsou out-of-fold z LOFO-CV (zlepseni/oof/*.parquet): každou povodeň předpověděly modely natrénované bez ní
(a bez ± 20 dní kolem). Okno 7 dní před vrcholem až 5 dní po, osa x je čas, ke kterému předpověď platí
(vydání + 24 h). Chyba v nadpisu = průměrná absolutní chyba v okně, stejná jako v ZLEPSENI.md / vysledky_*.json.
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ZDE = Path(__file__).resolve().parent
OOF = ZDE.parent / "zlepseni/oof"
sys.path.insert(0, str(ZDE.parent / "zlepseni"))
import lofo as L  # noqa: E402

H = 24
PX = 72 / 200  # 1 px při 200 dpi v bodech
POVRCH, INKOUST, INKOUST_2, MRIZKA = "#fcfcfb", "#0b0b0b", "#52514e", "#e8e7e3"
MESICE = ["leden", "únor", "březen", "duben", "květen", "červen", "červenec", "srpen", "září", "říjen", "listopad",
          "prosinec"]


def oof(nazev):
    d = pd.read_parquet(OOF / f"{nazev}.parquet")
    return {k: g.sort_values("cas") for k, g in d.groupby("fold")}


def cislo(x):
    return f"{x:.1f}".replace(".", ",")


if __name__ == "__main__":
    pov = L.povodne_lofo(H)
    r12, r30, g30 = oof("ridge_12"), oof("ridge_30"), oof("lgbm_30")
    nejvetsi = sorted(range(len(pov)), key=lambda k: -pov[k]["vrchol_cm"])[:6]

    # kontrola proti uloženým výsledkům (stejná čísla jako v ZLEPSENI.md)
    tym_json = next(r for r in json.loads((ZDE.parent / "zlepseni/vysledky_C.json").read_text(encoding="utf-8"))
                    if r["nazev"] == "ridge_12")["po_povodnich"]
    g3_json = next(r for r in json.loads((ZDE.parent / "zlepseni/vysledky_G34.json").read_text(encoding="utf-8"))
                   if r["nazev"].startswith("G3"))["po_povodnich"]

    plt.rcParams.update({"font.size": 10, "axes.edgecolor": MRIZKA, "axes.labelcolor": INKOUST_2,
                         "xtick.color": INKOUST_2, "ytick.color": INKOUST_2, "text.color": INKOUST})
    fig, osy = plt.subplots(3, 2, figsize=(13, 11.5), facecolor=POVRCH)
    for ax, k in zip(osy.flat, nejvetsi):
        p = pov[k]
        a, b, c = r12[k], r30[k], g30[k]
        assert (a.cas.to_numpy() == b.cas.to_numpy()).all() and (a.cas.to_numpy() == c.cas.to_numpy()).all()
        cas = pd.to_datetime(a.cas) + pd.Timedelta(hours=H)
        y, tym, g3 = a.y.to_numpy(), a.pred.to_numpy(), 0.5 * b.pred.to_numpy() + 0.5 * c.pred.to_numpy()
        e_tym, e_g3 = np.abs(tym - y).mean(), np.abs(g3 - y).mean()
        assert abs(round(e_tym, 1) - tym_json[p["nazev"]]) < 0.051 and abs(round(e_g3, 1) - g3_json[p["nazev"]]) < 0.051

        ax.set_facecolor(POVRCH)
        ax.grid(True, color=MRIZKA, linewidth=1 * PX)
        ax.set_axisbelow(True)
        okraj = max(1, len(y) // 5)  # popisek prahu na tu stranu, kde jsou čáry od prahu dál (ať se nepřekrývají)
        for prah, text in ((490, "2. SPA 490 cm"), (560, "3. SPA 560 cm")):
            ax.axhline(prah, color="#9a9994", linewidth=1 * PX, zorder=1)
            kraje = [np.concatenate([v[:okraj] for v in (y, tym, g3)]), np.concatenate([v[-okraj:] for v in (y, tym, g3)])]
            vlevo = np.abs(kraje[0] - prah - 12).min() >= np.abs(kraje[1] - prah - 12).min()
            ax.text(0.005 if vlevo else 0.995, prah, text, transform=ax.get_yaxis_transform(),
                    ha="left" if vlevo else "right", va="bottom", fontsize=8, color=INKOUST_2, zorder=6,
                    bbox=dict(boxstyle="square,pad=0.1", fc=POVRCH, ec="none", alpha=0.85))
        ax.plot(cas, y, color=INKOUST, linewidth=2 * PX, label="realita", zorder=4)
        ax.plot(cas, tym, color="#8a8984", linewidth=2 * PX, linestyle=(0, (5, 3)),
                label="týmový Ridge (12 stanic)", zorder=3)
        ax.plot(cas, g3, color="#2a78d6", linewidth=2 * PX, label="G3 = ½ Ridge 30 + ½ LightGBM 30 stanic",
                zorder=5)
        v = p["vrchol"] + pd.Timedelta(hours=H)
        ax.set_title(f"{MESICE[v.month - 1]} {v.year} (vrchol {p['vrchol_cm']} cm)\n"
                     f"průměrná chyba: tým {cislo(e_tym)} cm, G3 {cislo(e_g3)} cm", fontsize=10.5, loc="left",
                     color=INKOUST)
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=2, tz="UTC"))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d. %m.", tz="UTC"))
        ax.set_ylabel("hladina (cm)")
        lo, hi = min(y.min(), tym.min(), g3.min()), max(y.max(), tym.max(), g3.max(), 575)
        ax.set_ylim(lo - 0.05 * (hi - lo), hi + 0.06 * (hi - lo))
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        print(p["nazev"], p["vrchol_cm"], "tým", cislo(e_tym), "G3", cislo(e_g3))
    for ax in osy[-1]:
        ax.set_xlabel("datum (UTC), čas, ke kterému předpověď platí")
    h, lab = osy.flat[0].get_legend_handles_labels()
    fig.legend(h, lab, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 0.955), fontsize=10)
    fig.suptitle("Děčín, předpověď hladiny 24 h předem na 6 největších povodních 2006–2020", x=0.01, ha="left",
                 y=0.99, fontsize=13, color=INKOUST)
    fig.text(0.01, 0.962, "Předpovědi z leave-one-flood-out CV: každou povodeň předpověděly modely natrénované bez ní.",
             fontsize=9, color=INKOUST_2, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.93), h_pad=2.2, w_pad=2.0)
    fig.savefig(ZDE / "srovnani_g3_tym_povodne.png", dpi=200, facecolor=POVRCH)
