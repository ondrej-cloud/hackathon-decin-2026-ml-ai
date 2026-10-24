"""Grafy do prezentace v jednom stylu (16:9), jen z uložených výsledků a předpovědí.

python src/grafy_slajdy.py    uloží docs/grafy/slajdy/*.png

Nic netrénuje ani nepřepisuje results/. Jedinou výjimkou jsou váhy (graf 4), ty se počítají
z train části stejně jako v src/grafy_ridge.py.
"""
import json
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import FuncFormatter, MultipleLocator

from data import SPA
from grafy_ridge import RADKY, ZPOZDENI, vahy

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SLAJDY = ROOT / "docs/grafy/slajdy"

SEDA, MODRA, ORANZ = "#666666", "#167c9c", "#cb6c31"
MODRA_SVETLA = "#9fcad8"
STUPNE = ("#f2c437", "#ef6c00", "#c62828")
INK, INK2, INK3 = "#1f1f1f", "#4d4d4d", "#7a7a7a"
NB = " "
PROC = NB + "%"
JAKO_TED = "„bude jako teď“"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Segoe UI", "Helvetica Neue", "Arial", "DejaVu Sans"],
    "font.size": 13,
    "text.color": INK,
    "axes.labelsize": 14,
    "axes.labelcolor": INK2,
    "axes.edgecolor": "#9a9a9a",
    "axes.linewidth": 1,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "axes.grid.axis": "y",
    "axes.axisbelow": True,
    "grid.color": "#e6e6e6",
    "grid.linewidth": 0.9,
    "xtick.labelsize": 13,
    "ytick.labelsize": 13,
    "xtick.color": INK2,
    "ytick.color": INK2,
    "legend.fontsize": 13,
    "legend.frameon": False,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
})


def cislo(x, des=1):
    """Česky: desetinná čárka a mezera u tisíců. Zaokrouhluje stejně jako f-string v ostatních skriptech a docs/."""
    return f"{float(x):,.{des}f}".replace(",", NB).replace(".", ",")


def osa_cisla(ax, osa="y", pripona=""):
    (ax.yaxis if osa == "y" else ax.xaxis).set_major_formatter(FuncFormatter(lambda v, _: cislo(v, 0) + pripona))


def mene(model, zaklad):
    return f"o {cislo(100 * (1 - model / zaklad), 0)}{PROC} méně"


def slajd(titulek, podtitulek, pata, rect=(0.085, 0.14, 0.89, 0.66)):
    fig = plt.figure(figsize=(12, 6.75))
    fig.text(0.04, 0.955, titulek, fontsize=21, weight="semibold", va="top")
    fig.text(0.04, 0.882, podtitulek, fontsize=14, color=INK2, va="top")
    fig.text(0.04, 0.022, pata, fontsize=11, color=INK3, va="bottom")
    return fig, fig.add_axes(rect)


def uloz(fig, nazev):
    cesta = SLAJDY / nazev
    fig.savefig(cesta, dpi=150)
    plt.close(fig)
    print(f"uloženo {cesta.relative_to(ROOT)}")


def posledni(model, cast="val"):
    """Poslední plný běh modelu v results/ (6 kombinací cíle a horizontu), jako porovnej.py --prehled."""
    for f in sorted(RESULTS.glob(f"*_{model}*.json"), reverse=True):
        b = f.read_bytes()
        try:
            z = json.loads(b.decode("utf-8"))
        except UnicodeDecodeError:  # starší výsledky z Windows bez UTF-8
            z = json.loads(b.decode("cp1250"))
        if z["model"] == model and z["cast"] == cast and not z.get("rychle") and len(z["vysledky"]) == 6:
            return z
    raise FileNotFoundError(f"results/: chybí plný běh {model} ({cast})")


def prumer(z):
    """prumer_povodne: průměr mae_povodne přes Děčín a Ústí, 12 / 24 / 36 h."""
    return float(np.mean([r["mae_povodne"] for r in z["vysledky"]]))


def predpovedi(soubor, cil="decin", horizont=24):
    """Uložená předpověď s časem platnosti (cas_vydani + horizont) v českém čase."""
    P = pd.read_parquet(RESULTS / "predpovedi" / f"{soubor}.parquet")
    P = P[(P.cil == cil) & (P.horizont == horizont)]
    platnost = (P.index + pd.Timedelta(hours=horizont)).tz_convert("Europe/Prague")
    return P.set_axis(platnost)


def predstih_3spa(r, od, do, horizont=24, cil="decin"):
    """Kdy skutečnost poprvé překročí 3. stupeň a kdy model poprvé vydal předpověď nad ním.

    Předstih je čas od vydání prvního varování do skutečného překročení, stejně jako v PREHLED.md (Boris 27 h).
    """
    w = r[od:do]
    prah = SPA[cil][2]
    skutecne = w.index[w.skutecnost >= prah][0]
    platnost = w.index[w.predpoved >= prah][0]
    vydano = platnost - pd.Timedelta(hours=horizont)
    return skutecne, platnost, vydano, (skutecne - vydano) / pd.Timedelta(hours=1)


def kdy(t):
    return f"{t.day}. {t.month}. v {t.hour}:{t.minute:02d}"


# 1 ------------------------------------------------------------------------------------------------
def srovnani_modelu():
    # čísla: results/*_<model>.json, poslední plný běh na val; prumer_povodne jako v docs/PREHLED.md
    modely = [("jako_ted", JAKO_TED), ("fyzika", "fyzikální model"), ("lgbm", "LightGBM"),
              ("mlp", "neuronová síť"), ("ridge", "lineární regrese\n(finální)")]
    h = {m: prumer(posledni(m)) for m, _ in modely}
    zaklad = h["jako_ted"]
    fig, ax = slajd(f"Nejjednodušší model chybuje nejméně: {mene(h['ridge'], zaklad)} než „jako teď“",
                    "Průměrná chyba hladiny během povodní (cm), menší je lepší",
                    "Data ČHMÚ 2006–2020 · validace: 4 povodně (2006, 2009, 2010, 2011), které modely při učení neviděly"
                    " · průměr Děčín a Ústí, 12 / 24 / 36 h")
    x = np.arange(len(modely))
    barvy = [SEDA if m == "jako_ted" else MODRA if m == "ridge" else ORANZ for m, _ in modely]
    ax.bar(x, [h[m] for m, _ in modely], 0.62, color=barvy)
    for i, (m, _) in enumerate(modely):
        ax.text(i, h[m] + 0.8, f"{cislo(h[m])} cm", ha="center", va="bottom", fontsize=17, weight="semibold")
        if m != "jako_ted":
            ax.text(i, h[m] + 4.6, mene(h[m], zaklad), ha="center", va="bottom", fontsize=13,
                    color=MODRA if m == "ridge" else INK2, weight="semibold" if m == "ridge" else "normal")
    ax.set_xticks(x, [n for _, n in modely], fontsize=14, color=INK)
    ax.tick_params(axis="x", length=0)
    ax.set_ylim(0, 52)
    ax.set_ylabel("cm")
    ax.yaxis.set_major_locator(MultipleLocator(10))
    osa_cisla(ax)
    uloz(fig, "srovnani_modelu.png")
    return h


# 2 ------------------------------------------------------------------------------------------------
def test_2021_2025(boris_h):
    # čísla: results/*_ridge_test.json a *_jako_ted_test.json (jediný běh testu, pá 21:00);
    # po horizontech průměr Děčína a Ústí, „celkem“ = prumer_povodne přes všech 6 kombinací
    R, J = posledni("ridge", "test"), posledni("jako_ted", "test")
    skupiny = []
    for hz in (12, 24, 36):
        r = np.mean([v["mae_povodne"] for v in R["vysledky"] if v["horizont"] == hz])
        j = np.mean([v["mae_povodne"] for v in J["vysledky"] if v["horizont"] == hz])
        skupiny.append((f"za {hz} h", j, r))
    skupiny.append(("celkem", prumer(J), prumer(R)))
    j_cel, r_cel = skupiny[-1][1:]
    fig, ax = slajd(f"Test 2021–2025: chyba {cislo(r_cel)} cm místo {cislo(j_cel)} cm, {mene(r_cel, j_cel)}",
                    "Průměrná chyba hladiny během povodní (cm), Děčín a Ústí, předpověď na 12, 24 a 36 h dopředu",
                    "Data ČHMÚ · test 2021–2025: povodně 2/2021, 12/2023, 2/2024, 9/2024 · model naučený do 2020"
                    " a vybraný předem, test spuštěn jednou",
                    rect=(0.085, 0.19, 0.89, 0.62))
    x = np.array([0, 1, 2, 3.35])
    s = 0.36
    ax.bar(x - s / 2 - 0.01, [j for _, j, _ in skupiny], s, color=SEDA, label=JAKO_TED)
    ax.bar(x + s / 2 + 0.01, [r for _, _, r in skupiny], s, color=MODRA, label="lineární regrese (finální)")
    for xi, (_, j, r) in zip(x, skupiny):
        ax.text(xi - s / 2 - 0.01, j + 1, cislo(j), ha="center", va="bottom", fontsize=15, weight="semibold")
        ax.text(xi + s / 2 + 0.01, r + 1, cislo(r), ha="center", va="bottom", fontsize=15, weight="semibold")
        ax.annotate(mene(r, j), (xi, 0), xycoords=("data", "axes fraction"), xytext=(0, -36),
                    textcoords="offset points", ha="center", va="top", fontsize=13, color=MODRA)
    ax.set_xticks(x, [n for n, _, _ in skupiny], fontsize=14, color=INK)
    ax.get_xticklabels()[-1].set_weight("semibold")
    ax.tick_params(axis="x", length=0)
    ax.axvline(2.67, color="#d0d0d0", lw=1)
    ax.set_xlim(-0.6, 3.95)
    ax.set_ylim(0, 100)
    ax.set_ylabel("cm")
    ax.yaxis.set_major_locator(MultipleLocator(20))
    osa_cisla(ax)
    ax.legend(loc="upper right", bbox_to_anchor=(1, 1.03))
    ax.text(0.0, 0.985, f"Povodeň Boris 9/2024: 3. stupeň v Děčíně hlášen {cislo(boris_h, 0)} h předem",
            transform=ax.transAxes, fontsize=14, color=INK, va="top",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#eef5f7", edgecolor="none"))
    uloz(fig, "test_2021_2025.png")
    return skupiny


# 3 ------------------------------------------------------------------------------------------------
def kolik_dat():
    # čísla: results/kolik_dat/2026-10-23_204319_kolik_dat.json (src/kolik_dat.py, opravená verze z pá 20:46)
    z = json.loads(sorted((RESULTS / "kolik_dat").glob("*_kolik_dat.json"))[-1].read_text(encoding="utf-8"))
    df = pd.DataFrame(z["souhrn"])
    let = sorted(df["let"].unique())
    zaklad = z["zaklad_prumer_povodne"]
    fig, ax = slajd("Víc stanic pomohlo víc než víc let",
                    "Průměrná chyba hladiny během povodní (cm) podle toho, kolik let a kolik stanic se model učil",
                    "Data ČHMÚ, učení vždy do konce 2018 · validace: 4 povodně (2006, 2009, 2010, 2011) a 2019–2020"
                    " · lineární regrese beze změn · propásne = nástupy povodní z 24",
                    rect=(0.085, 0.14, 0.89, 0.62))
    x = np.arange(len(let))
    ax.axvspan(-0.45, 3.45, color="#f1f1f1", zorder=0, lw=0)
    ax.text(1.5, 56.5, "v tréninku žádná povodeň nad 2. stupněm", ha="center", va="top", fontsize=12, color=INK3)
    ax.axhline(zaklad, color=SEDA, ls=(0, (5, 3)), lw=2, label=f"{JAKO_TED} {cislo(zaklad)} cm")
    for sada, barva, nazev, nahoru in (("kraj", ORANZ, "jen 3 stanice v kraji (Děčín, Ústí, Louny)", True),
                                       ("vsechny", MODRA, "všech 12 stanic", False)):
        b = df[df.sada == sada].set_index("let").loc[let]
        ax.plot(x, b.prumer_povodne, "o-", color=barva, lw=3, ms=10, mec="white", mew=2, label=nazev, zorder=3)
        for xi, (_, r) in zip(x, b.iterrows()):
            radky = [cislo(r.prumer_povodne)]
            if r.spa2_propasnuto:
                radky.append(f"propásne {r.spa2_propasnuto:.0f}")
            text = "\n".join(reversed(radky) if nahoru else radky)
            ax.annotate(text, (xi, r.prumer_povodne), xytext=(0, 12 if nahoru else -12), textcoords="offset points",
                        ha="center", va="bottom" if nahoru else "top", fontsize=13, color=INK, linespacing=1.15,
                        bbox=dict(boxstyle="round,pad=0.15", facecolor="white", edgecolor="none", alpha=0.85),
                        zorder=4)
    ax.text(1.3, 49.5, "← rozsah jako balíček pořadatelů\n    (2 roky, jen stanice v kraji)", fontsize=12,
            color=INK2, va="center", linespacing=1.3)
    vse13 = df[(df.sada == "vsechny") & (df["let"] == 13)].iloc[0]
    ax.annotate("finální model", (5, vse13.prumer_povodne), xytext=(0, -33), textcoords="offset points",
                fontsize=13, color=MODRA, weight="semibold", ha="center", va="top")
    ax.set_xticks(x, [{1: "1 rok", 2: "2 roky", 3: "3 roky"}.get(n, f"{n} let") for n in let], fontsize=14, color=INK)
    ax.set_xlabel("kolik let historie se model učil")
    ax.tick_params(axis="x", length=0)
    ax.set_xlim(-0.45, 5.5)
    ax.set_ylim(0, 58)
    ax.set_ylabel("cm")
    ax.yaxis.set_major_locator(MultipleLocator(10))
    osa_cisla(ax)
    h, l = ax.get_legend_handles_labels()
    ax.legend(h[1:] + h[:1], l[1:] + l[:1], loc="lower left", bbox_to_anchor=(0, 1.0), ncol=3, handlelength=2.4)
    uloz(fig, "kolik_dat.png")
    return df, zaklad


# 4 ------------------------------------------------------------------------------------------------
def vahy_decin_24h():
    # váhy: Ridge naučený na train části (2006–2018 bez validačních povodní), funkce vahy() ze src/grafy_ridge.py
    W = vahy("decin", 24)
    jmena = {"decin": "Děčín", "usti": "Ústí nad Labem", "louny": "Louny (Ohře)", "melnik": "Mělník (Labe)",
             "vranany": "Vraňany (Vltava)", "kostelec": "Kostelec n. L. (Labe)", "praha": "Praha (Vltava)",
             "nymburk": "Nymburk (Labe)", "jizera": "Předměřice (Jizera)", "beroun": "Beroun (Berounka)",
             "sazava": "Nespeky (Sázava)", "prelouc": "Přelouč (Labe)"}
    radky = [f"{jmena[s]}, {'hladina' if v == 'H' else 'průtok'}" for s, v in RADKY]
    praha = W.loc["praha_Q", 0]
    decin = W.loc["decin_H", 0]
    proti_proudu = W.drop(index=["decin_H", "usti_H", "decin_Q", "usti_Q"]).abs().max().max()
    assert praha == proti_proudu, "Praha teď už nemá největší váhu ze stanic proti proudu, uprav nadpis."
    fig, ax = slajd("Hned po Děčíně má největší váhu Praha teď: její voda je v Děčíně za den",
                    "Váhy lineární regrese pro Děčín za 24 h (cm). Modrá předpověď zvedá, oranžová snižuje",
                    "Data ČHMÚ, učení 2006–2018 · váha = o kolik cm stoupne předpověď, když je vstup o 1 směrodatnou"
                    " odchylku vyšší · šedá = takový vstup model nemá",
                    rect=(0.255, 0.145, 0.62, 0.675))
    m = np.nanmax(np.abs(W.to_numpy()))
    cmap = LinearSegmentedColormap.from_list("vahy", [ORANZ, "#f7f7f7", MODRA])
    ax.set_facecolor("#e9e9e9")
    im = ax.imshow(np.ma.masked_invalid(W.to_numpy()), cmap=cmap, vmin=-m, vmax=m, aspect="auto")
    ax.grid(False)
    ax.set_xticks(np.arange(W.shape[1] + 1) - 0.5, minor=True)
    ax.set_yticks(np.arange(W.shape[0] + 1) - 0.5, minor=True)
    ax.grid(which="minor", color="white", lw=2)
    ax.tick_params(which="both", length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    for i in range(W.shape[0]):
        for j in range(W.shape[1]):
            v = W.iat[i, j]
            if not np.isnan(v):
                ax.text(j, i, f"{v:+.0f}".replace("-", "−") if round(v) else "0", ha="center", va="center",
                        fontsize=12, color="white" if abs(v) > 0.5 * m else INK)
    ax.set_xticks(range(len(ZPOZDENI)), ["teď" if z == 0 else f"{z} h" for z in ZPOZDENI], fontsize=13)
    ax.xaxis.set_label_position("bottom")
    ax.set_xlabel("vstup změřený před")
    ax.set_yticks(range(len(radky)), radky, fontsize=13, color=INK)
    i_praha = [f"{s}_{v}" for s, v in RADKY].index("praha_Q")
    for i in (0, i_praha):
        ax.add_patch(plt.Rectangle((-0.5, i - 0.5), 1, 1, fill=False, edgecolor=INK, lw=2.5, zorder=5))
        ax.get_yticklabels()[i].set_weight("semibold")
    cax = fig.add_axes((0.895, 0.145, 0.016, 0.675))
    cb = fig.colorbar(im, cax=cax)
    cb.outline.set_visible(False)
    cb.ax.tick_params(length=0, labelsize=12)
    cb.ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: cislo(v, 0).replace("-", "−")))
    cb.ax.set_title("cm", fontsize=13, color=INK2, loc="left", pad=8)
    uloz(fig, "vahy_decin_24h.png")
    return decin, praha


# 5 a 6 --------------------------------------------------------------------------------------------
def povoden(ridge, jako_ted, od, do, titulek, pata, nazev, cil="decin", horizont=24):
    r, j = predpovedi(ridge, cil, horizont)[od:do], predpovedi(jako_ted, cil, horizont)[od:do]
    skutecne, platnost, vydano, hodin = predstih_3spa(r, od, do, horizont, cil)
    titulek = titulek.format(h=cislo(hodin, 0))
    fig, ax = slajd(titulek, f"Hladina v Děčíně (cm), předpověď vydaná {horizont} h předem", pata,
                    rect=(0.075, 0.14, 0.82, 0.66))
    cas = lambda i: i.tz_localize(None)
    for n, (spa, barva) in enumerate(zip(SPA[cil], STUPNE), 1):
        ax.axhline(spa, color=barva, lw=2, zorder=1)
        ax.text(1.012, spa, f"{n}. stupeň\n{spa} cm", transform=ax.get_yaxis_transform(),
                ha="left", va="center", fontsize=12, color=INK2, linespacing=1.15)
    ax.plot(cas(j.index), j.predpoved, color=SEDA, ls=(0, (5, 3)), lw=2, label=f"{JAKO_TED} (hladina o {horizont} h dřív)")
    ax.plot(cas(r.index), r.skutecnost, color="black", lw=2.8, label="skutečná hladina")
    ax.plot(cas(r.index), r.predpoved, color=MODRA, lw=2.8, label=f"lineární regrese, vydáno {horizont} h předem")
    ax.plot(cas(skutecne), r.skutecnost[skutecne], "o", color="black", ms=10, mec="white", mew=2, zorder=5)
    ax.plot(cas(platnost), r.predpoved[platnost], "o", color=MODRA, ms=11, mec="white", mew=2, zorder=5)
    ax.annotate(f"3. stupeň hlášen {cislo(hodin, 0)} h předem\nvarování vydáno {kdy(vydano)},\n"
                f"voda stupeň překročila {kdy(skutecne)}",
                (cas(platnost), r.predpoved[platnost]), xytext=(0.008, 0.985), textcoords="axes fraction",
                ha="left", va="top", fontsize=13, color=INK, linespacing=1.3,
                bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor="none", alpha=0.9),
                arrowprops=dict(arrowstyle="-", color=INK2, lw=1.2, shrinkA=0, shrinkB=6))
    vrchol = r.skutecnost.idxmax()
    ax.annotate(f"vrchol {cislo(r.skutecnost[vrchol], 0)} cm,\npředpověď {cislo(r.predpoved[vrchol], 0)} cm",
                (cas(vrchol), r.skutecnost[vrchol]), xytext=(14, 10), textcoords="offset points",
                ha="left", va="bottom", fontsize=13, color=INK, linespacing=1.3)
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{mdates.num2date(v).day}. {mdates.num2date(v).month}."))
    ax.set_xlim(cas(r.index[0]), cas(r.index[-1]))
    dole = min(r.skutecnost.min(), j.predpoved.min(), r.predpoved.min())
    ax.set_ylim(np.floor(dole / 100) * 100, max(r.skutecnost.max(), r.predpoved.max()) + 90)
    ax.set_ylabel("cm")
    ax.set_xlabel("datum (český čas)")
    osa_cisla(ax)
    ax.legend(loc="lower right", fontsize=13, handlelength=2.6)
    uloz(fig, nazev)
    return dict(skutecne=skutecne, vydano=vydano, predstih_h=hodin, vrchol=float(r.skutecnost[vrchol]),
                predpoved_vrcholu=float(r.predpoved[vrchol]))


# 7 ------------------------------------------------------------------------------------------------
SRAZKY = 17.4  # docs/POKUSY.md, pá 20:44 Ondra (src/pokus_meteo.py); v results/ JSON k tomu pokusu není


def co_jsme_zkouseli():
    # čísla: results/*_<model>.json (poslední plný běh na val), balíček z results/kolik_dat/, srážky z POKUSY.md
    kd = json.loads(sorted((RESULTS / "kolik_dat").glob("*_kolik_dat.json"))[-1].read_text(encoding="utf-8"))
    balicek = next(r for r in kd["souhrn"] if r["sada"] == "kraj" and r["let"] == 2)
    finalni = prumer(posledni("ridge"))
    polozky = [
        (JAKO_TED, prumer(posledni("jako_ted")), SEDA, "propásne 24 z 24"),
        ("jen 2 roky a 3 stanice v kraji", balicek["prumer_povodne"], ORANZ,
         f"propásne {balicek['spa2_propasnuto']} z {balicek['spa2_povodni']}"),
        ("LightGBM (rozhodovací stromy)", prumer(posledni("lgbm")), ORANZ, None),
        ("povodňové hodiny s váhou 20×", prumer(posledni("ridge_vahy20")), ORANZ, None),
        ("neuronová síť", prumer(posledni("mlp")), ORANZ, None),
        ("+ srážky, sníh a teplota", SRAZKY, ORANZ, None),
        ("lineární regrese (finální)", finalni, MODRA, None),
    ]
    fig, ax = slajd("Nic z vyzkoušeného nesnížilo chybu lineární regrese aspoň o 1 cm",
                    f"Průměrná chyba hladiny během povodní (cm). Modře finální model, oranžově pokusy, šedě {JAKO_TED}",
                    "Data ČHMÚ 2006–2020 · validace: 4 povodně (2006, 2009, 2010, 2011), které modely při učení neviděly"
                    " · průměr Děčín a Ústí, 12 / 24 / 36 h",
                    rect=(0.30, 0.12, 0.66, 0.70))
    y = np.arange(len(polozky))[::-1]
    ax.barh(y, [h for _, h, _, _ in polozky], 0.62, color=[b for _, _, b, _ in polozky])
    for yi, (_, h, _, pozn) in zip(y, polozky):
        ax.text(h + 0.6, yi, f"{cislo(h)} cm", va="center", fontsize=15, weight="semibold")
        if pozn is None and h != finalni:
            pozn = f"horší o {cislo(round(h, 1) - round(finalni, 1))} cm"
        if pozn:
            ax.text(h + 7.4, yi, pozn, va="center", fontsize=14, color=INK2)
    ax.axvline(finalni, color=MODRA, lw=1.5, ls=(0, (4, 3)), zorder=0)
    ax.set_yticks(y, [n for n, _, _, _ in polozky], fontsize=14, color=INK)
    ax.get_yticklabels()[-1].set_weight("semibold")
    ax.tick_params(axis="y", length=0)
    ax.grid(False)
    ax.spines["left"].set_visible(False)
    ax.set_xlim(0, 62)
    ax.xaxis.set_major_locator(MultipleLocator(10))
    osa_cisla(ax, "x")
    uloz(fig, "co_jsme_zkouseli.png")
    return polozky


# 8 ------------------------------------------------------------------------------------------------
def nejistota():
    # čísla: models/ridge_intervaly.json (src/nejistota.py): pokryti_val, pokryti_povodne, sirka_povodne_cm
    I = json.loads((ROOT / "models/ridge_intervaly.json").read_text(encoding="utf-8"))
    kombinace = [(c, h) for c in ("decin", "usti") for h in (12, 24, 36)]
    val = [100 * I[f"{c}_{h}"]["pokryti_val"] for c, h in kombinace]
    pov = [100 * I[f"{c}_{h}"]["pokryti_povodne"] for c, h in kombinace]
    fig, ax = slajd("Rozmezí sedí v klidu, při povodních je užší, než by mělo být",
                    "Kolik skutečných hladin se vešlo do rozmezí „nejspíš od–do“ (%). Pod sloupci šířka rozmezí na povodních",
                    "Rozmezí z chyb na učicích datech ČHMÚ 2006–2018 (5. až 95. percentil podle výšky hladiny) · ověřeno"
                    " na validaci: 4 povodně a 2019–2020",
                    rect=(0.085, 0.17, 0.89, 0.585))
    x = np.array([0, 1, 2, 3.4, 4.4, 5.4])
    s = 0.36
    ax.bar(x - s / 2 - 0.01, val, s, color=MODRA_SVETLA, label="celá validace (hlavně klidná voda)")
    ax.bar(x + s / 2 + 0.01, pov, s, color=MODRA, label="jen povodně")
    ax.axhline(90, color=INK, lw=1.5, ls=(0, (5, 3)), zorder=2)
    stitek = dict(boxstyle="square,pad=0.1", facecolor="white", edgecolor="none")
    for xi, a, b in zip(x, val, pov):
        ax.text(xi - s / 2 - 0.01, a + 1.5, cislo(a, 0) + PROC, ha="center", va="bottom", fontsize=13, bbox=stitek,
                zorder=3)
        ax.text(xi + s / 2 + 0.01, b + 1.5, cislo(b, 0) + PROC, ha="center", va="bottom", fontsize=13,
                weight="semibold", bbox=stitek, zorder=3)
    ax.text(2.7, 91.5, "cíl 90" + PROC, ha="center", va="bottom", fontsize=13, color=INK, weight="semibold")
    ax.set_xticks(x, [f"za {h} h" for _, h in kombinace], fontsize=14, color=INK)
    for xi, (c, h) in zip(x, kombinace):
        ax.annotate(f"šířka {I[f'{c}_{h}']['sirka_povodne_cm']} cm", (xi, 0), xycoords=("data", "axes fraction"),
                    xytext=(0, -32), textcoords="offset points", ha="center", va="top", fontsize=12, color=INK3)
    for xc, nazev in ((1, "Děčín"), (4.4, "Ústí nad Labem")):
        ax.text(xc, 106, nazev, ha="center", va="bottom", fontsize=15, weight="semibold")
    ax.tick_params(axis="x", length=0)
    ax.set_xlim(-0.6, 6.0)
    ax.set_ylim(0, 112)
    ax.set_yticks([0, 25, 50, 75, 100])
    osa_cisla(ax, pripona=PROC)
    ax.legend(loc="lower left", ncol=2, bbox_to_anchor=(0, 1.0))
    uloz(fig, "nejistota.png")
    return val, pov


if __name__ == "__main__":
    SLAJDY.mkdir(parents=True, exist_ok=True)
    h = srovnani_modelu()
    print("  validace prumer_povodne:", {m: cislo(v) for m, v in h.items()})
    boris = povoden("ridge_test", "jako_ted_test", "2024-09-08", "2024-09-24 23:00",
                    "Povodeň Boris 9/2024: model hlásil 3. stupeň v Děčíně {h} h předem",
                    "Data ČHMÚ · test 2021–2025, model tuto povodeň při učení neviděl (naučený do 2020)"
                    " · „jako teď“ = hladina při vydání předpovědi",
                    "boris_2024.png")
    print("  Boris:", boris)
    print("  test:", [(n, cislo(j), cislo(r)) for n, j, r in test_2021_2025(boris["predstih_h"])])
    df, zaklad = kolik_dat()
    print("  kolik dat:", df[["sada", "let", "prumer_povodne", "spa2_propasnuto"]].round(1).to_dict("records"))
    print("  váhy Děčín teď / Praha teď:", vahy_decin_24h())
    print("  1/2011:", povoden("ridge", "jako_ted", "2011-01-08", "2011-01-24 23:00",
                               "Povodeň 1/2011: model hlásil 3. stupeň v Děčíně {h} h předem",
                               "Data ČHMÚ · validační povodeň, model ji při učení neviděl (naučený na 2006–2018 bez ní)"
                               " · „jako teď“ = hladina při vydání předpovědi",
                               "povoden_2011.png"))
    print("  zkoušeli:", [(n, cislo(v)) for n, v, _, _ in co_jsme_zkouseli()])
    print("  nejistota val / povodně:", nejistota())
