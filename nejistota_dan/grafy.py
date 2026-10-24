"""Grafy povodní s pásmem nejistoty (styl slajdů týmu, src/grafy_slajdy.py), jen z uložených LOFO předpovědí.

python grafy.py    uloží grafy/pasmo_<povoden>.png a grafy/pokryti.png

Pásmo v grafu je vnořené: kvantily jen z ostatních 21 povodní, takže graf ukazuje, jak by pásmo vypadalo,
kdyby tuhle povodeň model ani kalibrace nikdy neviděly. Čas na ose = kdy předpověď platí (vydání + 24 h).
"""
import sys
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

ZDE = Path(__file__).resolve().parent
sys.path[:0] = [str(ZDE.parent / "src"), str(ZDE)]
import json  # noqa: E402

import nejistota_dan as N  # noqa: E402
import overeni as O  # noqa: E402

GRAFY = ZDE / "grafy"
MODRA, MODRA_SVETLA, MODRA_NEJSVETLEJSI = "#167c9c", "#9fcad8", "#d9ebf1"
STUPNE = ("#f2c437", "#ef6c00", "#c62828")
INK, INK2, INK3 = "#1f1f1f", "#4d4d4d", "#7a7a7a"
NB = " "
plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Segoe UI", "Helvetica Neue", "Arial", "DejaVu Sans"],
    "font.size": 13, "text.color": INK, "axes.labelsize": 14, "axes.labelcolor": INK2, "axes.edgecolor": "#9a9a9a",
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "axes.grid.axis": "y",
    "axes.axisbelow": True, "grid.color": "#e6e6e6", "xtick.labelsize": 13, "ytick.labelsize": 13,
    "xtick.color": INK2, "ytick.color": INK2, "legend.fontsize": 13, "legend.frameon": False,
    "figure.facecolor": "white", "savefig.facecolor": "white",
})
MESICE = ["ledna", "února", "března", "dubna", "května", "června", "července", "srpna", "září", "října", "listopadu",
          "prosince"]
SPA = (400, 490, 560)


def cislo(x, des=0):
    return f"{float(x):,.{des}f}".replace(",", NB).replace(".", ",")


def slajd(titulek, podtitulek, pata, rect=(0.085, 0.14, 0.80, 0.66)):
    fig = plt.figure(figsize=(12, 6.75))
    fig.text(0.04, 0.955, titulek, fontsize=21, weight="semibold", va="top")
    fig.text(0.04, 0.882, podtitulek, fontsize=14, color=INK2, va="top")
    fig.text(0.04, 0.022, pata, fontsize=11, color=INK3, va="bottom")
    return fig, fig.add_axes(rect)


def graf_povodne(povoden, titulek, model="ridge", cil="decin", h=24, varianta=None):
    varianta = varianta or json.loads(N.KVANTILY.read_text(encoding="utf-8"))["varianta"]
    D = O.nacti(model, cil, h)
    meze = {u: O.vnorene(D, varianta, cil, h, u)[:2] for u in N.UROVNE}
    m = (D.povoden == povoden).to_numpy()
    t = pd.DatetimeIndex(D.cas[m]) + pd.Timedelta(hours=h)
    y, p = D.y[m].to_numpy(), D.pred[m].to_numpy()
    d95, h95 = (a[m] for a in meze[0.95])
    d80, h80 = (a[m] for a in meze[0.8])
    v80 = ((y >= d80) & (y <= h80)).mean()
    v95 = ((y >= d95) & (y <= h95)).mean()
    fig, ax = slajd(titulek, f"Děčín, předpověď na {h} h dopředu (týmová lineární regrese) a pásmo, do kterého má padnout "
                             f"skutečnost v 80{NB}% a 95{NB}% hodin",
                    f"Pásmo z chyb na ostatních povodních 2006–2020 bez této a sousedních (model ani pásmo ji neviděly)"
                    f" · v pásmu 80{NB}%: {cislo(100 * v80)}{NB}% hodin, v pásmu 95{NB}%: {cislo(100 * v95)}{NB}% hodin")
    ax.fill_between(t, d95, h95, color=MODRA_NEJSVETLEJSI, lw=0, label=f"pásmo 95{NB}%")
    ax.fill_between(t, d80, h80, color=MODRA_SVETLA, lw=0, label=f"pásmo 80{NB}%")
    ax.plot(t, p, color=MODRA, lw=2, label=f"předpověď na {h} h")
    ax.plot(t, y, color=INK, lw=2.2, label="skutečnost")
    for prah, barva, n in zip(SPA, STUPNE, (1, 2, 3)):
        if prah < max(h95.max(), y.max()) + 20:
            ax.axhline(prah, color=barva, lw=1.4, ls=(0, (5, 3)), zorder=1)
            ax.text(1.005, prah, f"{n}. stupeň", transform=ax.get_yaxis_transform(), va="center", fontsize=12,
                    color=INK2)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: cislo(v) + " cm"))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
    ax.xaxis.set_major_formatter(plt.FuncFormatter(
        lambda v, _: f"{mdates.num2date(v).day}.{NB}{MESICE[mdates.num2date(v).month - 1]}"))
    ax.set_xlim(t.min(), t.max())
    ax.legend(loc="upper left", ncol=4, bbox_to_anchor=(0, 1.08))
    GRAFY.mkdir(exist_ok=True)
    fig.savefig(GRAFY / f"pasmo_{povoden}.png", dpi=150)
    plt.close(fig)
    return dict(povoden=povoden, v80=round(v80, 3), v95=round(v95, 3))


def graf_pokryti():
    """Pokrytí 80% pásma: dnešní týmové (chyby na tréninku) proti novému, celkem a při rychlém vzestupu."""
    S = pd.read_csv(ZDE / "vysledky/souhrn_variant.csv")
    v = json.loads(N.KVANTILY.read_text(encoding="utf-8"))["varianta"]
    S = S[(S.model == "ridge") & (S.uroven == 0.8)]
    kombinace = [(c, h) for c in ("decin", "usti") for h in (12, 24, 36)]
    hodnota = lambda var, sl: [100 * S[(S.varianta == var) & (S.cil == c) & (S.horizont == h)][sl].iloc[0]  # noqa: E731
                               for c, h in kombinace]
    fig, ax = slajd("Nové pásmo sedí na povodních celkově, při rychlém vzestupu je pořád užší",
                    f"Kolik skutečných hladin se na 22 povodních 2006–2020 vešlo do pásma „80{NB}%“, týmová lineární"
                    " regrese",
                    "Vnořeně: pásmo každé povodně jen z ostatních povodní · dnešní = chyby na učicích datech podle"
                    " výšky hladiny · nové = chyby mimo trénink podle očekávané změny",
                    rect=(0.085, 0.17, 0.89, 0.585))
    x = np.array([0, 1, 2, 3.4, 4.4, 5.4])
    s = 0.27
    rady = [("tym_trenink", "pokryti", "#c9c9c9", "dnešní, všechny hodiny"),
            (v, "pokryti", MODRA, "nové, všechny hodiny"),
            (v, "pokryti_rychly_vzestup", MODRA_SVETLA, "nové, rychlý vzestup (≥ 50 cm)")]
    for i, (var, sl, barva, popis) in enumerate(rady):
        hod = hodnota(var, sl)
        xi = x + (i - 1) * (s + 0.02)
        ax.bar(xi, hod, s, color=barva, label=popis)
        for a, b in zip(xi, hod):
            ax.text(a, b + 1.5, cislo(b), ha="center", va="bottom", fontsize=12)
    ax.axhline(80, color=INK, lw=1.5, ls=(0, (5, 3)), zorder=2)
    ax.text(2.7, 81.5, f"cíl 80{NB}%", ha="center", va="bottom", fontsize=13, weight="semibold")
    ax.set_xticks(x, [f"za {h} h" for _, h in kombinace], fontsize=14, color=INK)
    for xc, nazev in ((1, "Děčín"), (4.4, "Ústí nad Labem")):
        ax.text(xc, 103, nazev, ha="center", va="bottom", fontsize=15, weight="semibold")
    ax.tick_params(axis="x", length=0)
    ax.set_ylim(0, 110)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: cislo(v) + NB + "%"))
    ax.legend(loc="lower left", ncol=3, bbox_to_anchor=(0, 1.0))
    fig.savefig(GRAFY / "pokryti.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    for p, t in (("2011-01-16", "Leden 2011: skutečnost je skoro celou dobu v pásmu"),
                 ("2010-09-28", "Září 2010: déšť nad Děčínem, vzestup přijde rychleji, než model čeká"),
                 ("2013-06-05", "Červen 2013: na rekordní povodni je pásmo moc úzké")):
        print(graf_povodne(p, t))
    graf_pokryti()
