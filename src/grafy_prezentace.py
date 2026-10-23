"""Grafy do prezentace na 7 minut (docs/PREZENTACE_7MIN.md), pojmenované podle slajdu. Bez nadpisů, podtitulků a patiček,
nadpis je na slajdu. Styl, barvy a data jako src/grafy_slajdy.py, jen větší písmo a méně textu.

python src/grafy_prezentace.py    uloží docs/grafy/prezentace/*.png
"""
import json
import shutil

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import FuncFormatter, MultipleLocator

import grafy_slajdy as gs
from data import SPA, nacti
from grafy_ridge import RADKY, ZPOZDENI, vahy
from grafy_slajdy import (INK, INK2, INK3, JAKO_TED, MODRA, MODRA_SVETLA, ORANZ, PROC, RESULTS, ROOT, SEDA, STUPNE,
                          cislo, osa_cisla, posledni, predpovedi, predstih_3spa, prumer)
from krizova_validace import BLOKY
from meteo import STANICE, denni

CIL = ROOT / "docs/grafy/prezentace"
GRAFY = ROOT / "docs/grafy"
plt.rcParams.update({"font.size": 16, "axes.labelsize": 16, "xtick.labelsize": 16, "ytick.labelsize": 16,
                     "legend.fontsize": 16})
NASE = "náš model"


def plocha(rect=(0.08, 0.12, 0.9, 0.84)):
    fig = plt.figure(figsize=(12, 6.75))
    return fig, fig.add_axes(rect)


def uloz(fig, nazev):
    fig.savefig(CIL / nazev, dpi=150)
    plt.close(fig)
    print(f"uloženo {(CIL / nazev).relative_to(ROOT)}")


def hodnoty_nad(ax, x, h, des=1, **kw):
    for xi, v in zip(x, h):
        ax.text(xi, v + 0.8, cislo(v, des), ha="center", va="bottom", fontsize=kw.get("fontsize", 17), weight="semibold")


def s03b_kolik_dat():
    z = json.loads(sorted((RESULTS / "kolik_dat").glob("*_kolik_dat.json"))[-1].read_text(encoding="utf-8"))
    balicek = next(r for r in z["souhrn"] if r["sada"] == "kraj" and r["let"] == 2)
    polozky = [(JAKO_TED, prumer(posledni("jako_ted")), SEDA, "propásne 24 z 24 povodní"),
               ("jen data z balíčku\n2 roky, 3 stanice", balicek["prumer_povodne"], ORANZ,
                f"propásne {balicek['spa2_propasnuto']} z 24 povodní"),
               ("naše data\n20 let, 12 stanic", prumer(posledni("ridge")), MODRA, "propásne 0 z 24 povodní")]
    fig, ax = plocha((0.1, 0.17, 0.86, 0.78))
    x = np.arange(len(polozky))
    ax.bar(x, [h for _, h, _, _ in polozky], 0.58, color=[b for _, _, b, _ in polozky])
    for xi, (_, h, _, pozn) in zip(x, polozky):
        ax.text(xi, h + 1, f"{cislo(h)} cm", ha="center", va="bottom", fontsize=24, weight="semibold")
        ax.text(xi, h + 5.2, pozn, ha="center", va="bottom", fontsize=16, color=INK2)
    ax.set_xticks(x, [n for n, _, _, _ in polozky], fontsize=17, color=INK)
    ax.tick_params(axis="x", length=0)
    ax.set_ylim(0, 56)
    ax.set_ylabel("chyba během povodní (cm)")
    ax.yaxis.set_major_locator(MultipleLocator(10))
    osa_cisla(ax)
    uloz(fig, "03b_proc_externi_data.png")


def s04_vahy():
    W = vahy("decin", 24)
    jmena = {"decin": "Děčín", "usti": "Ústí", "louny": "Louny", "melnik": "Mělník", "vranany": "Vraňany",
             "kostelec": "Kostelec", "praha": "Praha", "nymburk": "Nymburk", "jizera": "Jizera", "beroun": "Beroun",
             "sazava": "Sázava", "prelouc": "Přelouč"}
    radky = [f"{jmena[s]} {'hladina' if v == 'H' else 'průtok'}" for s, v in RADKY]
    fig, ax = plocha((0.2, 0.1, 0.66, 0.82))
    m = np.nanmax(np.abs(W.to_numpy()))
    cmap = LinearSegmentedColormap.from_list("vahy", [ORANZ, "#f7f7f7", MODRA])
    ax.set_facecolor("#ececec")
    im = ax.imshow(np.ma.masked_invalid(W.to_numpy()), cmap=cmap, vmin=-m, vmax=m, aspect="auto")
    ax.grid(False)
    ax.set_xticks(np.arange(W.shape[1] + 1) - 0.5, minor=True)
    ax.set_yticks(np.arange(W.shape[0] + 1) - 0.5, minor=True)
    ax.grid(which="minor", color="white", lw=2)
    ax.tick_params(which="both", length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    klice = [f"{s}_{v}" for s, v in RADKY]
    for i in (klice.index("decin_H"), klice.index("praha_Q")):
        ax.add_patch(plt.Rectangle((-0.5, i - 0.5), 1, 1, fill=False, edgecolor=INK, lw=3, zorder=5))
        ax.text(0, i, f"+{W.iat[i, 0]:.0f}", ha="center", va="center", fontsize=15, color="white", weight="semibold")
    ax.set_xticks(range(len(ZPOZDENI)), ["teď" if z == 0 else f"{z} h" for z in ZPOZDENI], fontsize=15)
    ax.set_xlabel("změřeno před")
    ax.set_yticks(range(len(radky)), radky, fontsize=15, color=INK)
    for i in (klice.index("decin_H"), klice.index("praha_Q")):
        ax.get_yticklabels()[i].set_weight("semibold")
    cax = fig.add_axes((0.89, 0.1, 0.018, 0.82))
    cb = fig.colorbar(im, cax=cax)
    cb.outline.set_visible(False)
    cb.ax.tick_params(length=0, labelsize=14)
    cb.ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: cislo(v, 0).replace("-", "−")))
    cb.ax.text(0.5, 1.02, "zvedá", transform=cb.ax.transAxes, ha="center", va="bottom", fontsize=14, color=MODRA)
    cb.ax.text(0.5, -0.02, "snižuje", transform=cb.ax.transAxes, ha="center", va="top", fontsize=14, color=ORANZ)
    uloz(fig, "04_vahy_modelu.png")


def s05_co_jsme_zkouseli():
    polozky = [  # validace, prumer_povodne; bez results/ běhu čísla z docs/POKUSY.md
        ("fyzikální model", prumer(posledni("fyzika"))),
        ("LightGBM (stromy)", prumer(posledni("lgbm"))),
        ("polynom", prumer(posledni("ridge_polynom"))),
        ("doba putování podle průtoku", 21.8),  # pá 20:45
        ("polynom se součiny", prumer(posledni("ridge_polynom_soucin"))),
        ("větší váha povodní", prumer(posledni("ridge_vahy20"))),
        ("neuronová síť", prumer(posledni("mlp"))),
        ("+ voda ve sněhu", 17.8),  # pá 23:14
        ("+ srážky, sníh, teplota", 17.4),  # pá 20:44
        ("+ víc stanic (horní Ohře)", 17.4),  # so 0:19
        ("všechna malá zlepšení", 17.2),  # so 0:43
        ("lineární regrese", prumer(posledni("ridge"))),
    ]
    finalni = polozky[-1][1]
    fig, ax = plocha((0.31, 0.12, 0.66, 0.85))
    y = np.arange(len(polozky))[::-1]
    ax.barh(y, [h for _, h in polozky], 0.68, color=[ORANZ] * (len(polozky) - 1) + [MODRA])
    for yi, (_, h) in zip(y, polozky):
        ax.text(h + 0.4, yi, cislo(h), va="center", fontsize=15, weight="semibold" if h == finalni else "normal")
    ax.axvline(finalni, color=MODRA, lw=1.5, ls=(0, (4, 3)), zorder=0)
    ax.set_yticks(y, [n for n, _ in polozky], fontsize=15, color=INK)
    ax.get_yticklabels()[-1].set_weight("semibold")
    ax.get_yticklabels()[-1].set_color(MODRA)
    ax.tick_params(axis="y", length=0)
    ax.grid(False)
    ax.spines["left"].set_visible(False)
    ax.set_xlim(0, 28)
    ax.set_xlabel("chyba během povodní (cm)")
    ax.xaxis.set_major_locator(MultipleLocator(5))
    osa_cisla(ax, "x")
    uloz(fig, "05_co_jsme_zkouseli.png")


def s06_jak_overujeme():
    t = lambda d: mdates.date2num(pd.Timestamp(d))
    fig, ax = plocha((0.2, 0.1, 0.77, 0.78))
    vys = 0.52
    radky = [("1. výběr modelu", [("2006", "2019", MODRA_SVETLA), ("2019", "2021", ORANZ)],
              ["2006-04-03", "2009-03-07", "2010-09-29", "2011-01-17"], "4 povodně a roky 2019–2020 stranou"),
             ("2. vícenásobná\nvalidace", [("2006", "2021", MODRA_SVETLA)], [d[0] for d in BLOKY.values()],
              "každá z 8 povodní jednou stranou"),
             ("3. test", [("2006", "2021", MODRA_SVETLA), ("2021", "2026", MODRA)], [], "jednou, na konci")]
    for y, (_, useky, povodne, text) in zip((2, 1, 0), radky):
        for od, do, barva in useky:
            ax.barh(y, t(f"{do}-01-01") - t(f"{od}-01-01"), vys, left=t(f"{od}-01-01"), color=barva)
        for d in povodne:
            ax.barh(y, 45, vys, left=t(d) - 22, color=ORANZ)
        ax.text(t("2006-01-01"), y + vys / 2 + 0.05, text, ha="left", va="bottom", fontsize=16, color=INK2)
    ax.set_yticks([2, 1, 0], [r[0] for r in radky], fontsize=17, color=INK)
    ax.tick_params(axis="y", length=0)
    ax.xaxis_date()
    ax.set_xticks([t(d) for d in ("2006-01-01", "2019-01-01", "2021-01-01", "2025-12-31")], ["2006", "2019", "2021", "2025"])
    ax.set_xlim(t("2005-09-01"), t("2026-02-01"))
    ax.set_ylim(-0.5, 2.8)
    ax.grid(False)
    ax.spines["left"].set_visible(False)
    for barva, nazev in ((MODRA_SVETLA, "učení"), (ORANZ, "ověření"), (MODRA, "test")):
        ax.barh(np.nan, 0, color=barva, label=nazev)
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=3, handlelength=1.2)
    uloz(fig, "06_jak_overujeme.png")


def s07_boris():
    od, do = "2024-09-10", "2024-09-22 23:00"
    r, j = predpovedi("ridge_test")[od:do], predpovedi("jako_ted_test")[od:do]
    skutecne, platnost, vydano, hodin = predstih_3spa(r, od, do)
    cas = lambda i: i.tz_localize(None)
    fig, ax = plocha((0.08, 0.1, 0.83, 0.86))
    for n, (spa, barva) in enumerate(zip(SPA["decin"], STUPNE), 1):
        ax.axhline(spa, color=barva, lw=2, zorder=1)
        ax.text(1.01, spa, f"{n}. stupeň", transform=ax.get_yaxis_transform(), ha="left", va="center", fontsize=14,
                color=INK2)
    ax.plot(cas(j.index), j.predpoved, color=SEDA, ls=(0, (5, 3)), lw=2.2, label=JAKO_TED)
    ax.plot(cas(r.index), r.skutecnost, color="black", lw=3.2, label="skutečnost")
    ax.plot(cas(r.index), r.predpoved, color=MODRA, lw=3.2, label=f"{NASE}, 24 h předem")
    ax.plot(cas(platnost), r.predpoved[platnost], "o", color=MODRA, ms=13, mec="white", mew=2, zorder=5)
    ax.annotate(f"varování {cislo(hodin, 0)} h předem", (cas(platnost), r.predpoved[platnost]), xytext=(-24, 40),
                textcoords="offset points", ha="right", fontsize=18, weight="semibold", color=MODRA,
                arrowprops=dict(arrowstyle="-", color=MODRA, lw=1.5))
    vrchol = r.skutecnost.idxmax()
    ax.annotate(f"vrchol {cislo(r.skutecnost[vrchol], 0)} cm\npředpověď {cislo(r.predpoved[vrchol], 0)} cm",
                (cas(vrchol), r.skutecnost[vrchol]), xytext=(10, 12), textcoords="offset points", fontsize=15,
                color=INK, linespacing=1.3)
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{mdates.num2date(v).day}. 9."))
    ax.set_xlim(cas(r.index[0]), cas(r.index[-1]))
    ax.set_ylim(0, 760)
    ax.set_ylabel("hladina v Děčíně (cm)")
    osa_cisla(ax)
    ax.legend(loc="lower right", handlelength=2.4)
    uloz(fig, "07_boris_2024.png")


def s08a_test():
    R, J = posledni("ridge", "test"), posledni("jako_ted", "test")
    skupiny = [(f"za {hz} h", np.mean([v["mae_povodne"] for v in J["vysledky"] if v["horizont"] == hz]),
                np.mean([v["mae_povodne"] for v in R["vysledky"] if v["horizont"] == hz])) for hz in (12, 24, 36)]
    skupiny.append(("celkem", prumer(J), prumer(R)))
    fig, ax = plocha((0.09, 0.17, 0.88, 0.78))
    x = np.array([0, 1, 2, 3.35])
    s = 0.36
    ax.bar(x - s / 2 - 0.01, [a for _, a, _ in skupiny], s, color=SEDA, label=JAKO_TED)
    ax.bar(x + s / 2 + 0.01, [b for _, _, b in skupiny], s, color=MODRA, label=NASE)
    for xi, (_, a, b) in zip(x, skupiny):
        ax.text(xi - s / 2 - 0.01, a + 1, cislo(a), ha="center", va="bottom", fontsize=17, weight="semibold")
        ax.text(xi + s / 2 + 0.01, b + 1, cislo(b), ha="center", va="bottom", fontsize=17, weight="semibold")
        ax.annotate(f"−{cislo(100 * (1 - b / a), 0)}{PROC}", (xi, 0), xycoords=("data", "axes fraction"),
                    xytext=(0, -40), textcoords="offset points", ha="center", va="top", fontsize=19, color=MODRA,
                    weight="semibold")
    ax.set_xticks(x, [n for n, _, _ in skupiny], fontsize=17, color=INK)
    ax.get_xticklabels()[-1].set_weight("semibold")
    ax.tick_params(axis="x", length=0)
    ax.axvline(2.67, color="#d0d0d0", lw=1)
    ax.set_xlim(-0.6, 3.95)
    ax.set_ylim(0, 85)
    ax.set_ylabel("chyba během povodní (cm)")
    ax.yaxis.set_major_locator(MultipleLocator(20))
    osa_cisla(ax)
    ax.legend(loc="upper left")
    uloz(fig, "08a_test_2021_2025.png")


def s08b_vicenasobna():
    R = pd.read_csv(sorted((RESULTS / "krizova_validace").glob("*.csv"))[-1])
    P = R.groupby(["povoden", "model"]).chyba.mean().unstack()
    P = P.loc[sorted(P.index)]
    fig, ax = plocha((0.09, 0.2, 0.88, 0.75))
    x = np.arange(len(P) + 1) * 1.0
    x[-1] += 0.5
    a, b = list(P.jako_ted) + [P.jako_ted.mean()], list(P.ridge) + [P.ridge.mean()]
    s = 0.38
    ax.bar(x - s / 2 - 0.01, a, s, color=SEDA, label=JAKO_TED)
    ax.bar(x + s / 2 + 0.01, b, s, color=MODRA, label=NASE)
    for xi, aa, bb in zip(x, a, b):
        ax.annotate(f"−{cislo(100 * (1 - bb / aa), 0)}{PROC}", (xi, 0), xycoords=("data", "axes fraction"),
                    xytext=(0, -40), textcoords="offset points", ha="center", va="top", fontsize=16, color=MODRA,
                    weight="semibold")
    ax.text(x[-1] + s / 2 + 0.01, b[-1] + 1, cislo(b[-1]), ha="center", va="bottom", fontsize=17, weight="semibold")
    ax.text(x[-1] - s / 2 - 0.01, a[-1] + 1, cislo(a[-1]), ha="center", va="bottom", fontsize=17, weight="semibold")
    ax.set_xticks(x, [f"{p[5:].lstrip('0')}/{p[2:4]}" for p in P.index] + ["průměr"], fontsize=16, color=INK)
    ax.get_xticklabels()[-1].set_weight("semibold")
    ax.tick_params(axis="x", length=0)
    ax.axvline(x[-2] + 0.75, color="#d0d0d0", lw=1)
    ax.set_xlim(-0.6, x[-1] + 0.6)
    ax.set_ylim(0, 80)
    ax.set_ylabel("chyba během povodně (cm)")
    ax.yaxis.set_major_locator(MultipleLocator(20))
    osa_cisla(ax)
    ax.legend(loc="upper left", ncol=2)
    uloz(fig, "08b_vicenasobna_validace.png")


def z1_srovnani_modelu():
    modely = [("jako_ted", JAKO_TED), ("fyzika", "fyzikální"), ("lgbm", "LightGBM"), ("mlp", "neuronová síť"),
              ("ridge", "lineární regrese")]
    h = [prumer(posledni(m)) for m, _ in modely]
    fig, ax = plocha((0.09, 0.12, 0.88, 0.84))
    x = np.arange(len(modely))
    ax.bar(x, h, 0.6, color=[SEDA, ORANZ, ORANZ, ORANZ, MODRA])
    for xi, v in zip(x, h):
        ax.text(xi, v + 0.8, cislo(v), ha="center", va="bottom", fontsize=20, weight="semibold")
    ax.set_xticks(x, [n for _, n in modely], fontsize=17, color=INK)
    ax.tick_params(axis="x", length=0)
    ax.set_ylim(0, 50)
    ax.set_ylabel("chyba během povodní (cm)")
    ax.yaxis.set_major_locator(MultipleLocator(10))
    osa_cisla(ax)
    uloz(fig, "Z1_srovnani_ctyr_modelu.png")


def z2_jako_ted():
    skutecnost = nacti().decin_H["2024-09-12":"2024-09-21"].tz_convert("Europe/Prague").tz_localize(None)
    jako_ted = skutecnost.shift(24, freq="h")[:skutecnost.index[-1]]
    fig, ax = plocha((0.08, 0.1, 0.9, 0.86))
    ax.plot(skutecnost.index, skutecnost, color="black", lw=3.2, label="skutečnost")
    ax.plot(jako_ted.index, jako_ted, color=SEDA, lw=2.4, ls=(0, (5, 3)), label=f"{JAKO_TED}: hladina z doby předpovědi")
    for t in pd.to_datetime(["2024-09-13 14:00", "2024-09-14 08:00", "2024-09-15 02:00"]):
        h, pak = skutecnost[t], skutecnost[t + pd.Timedelta(hours=24)]
        ax.annotate("", xy=(t + pd.Timedelta(hours=24), h), xytext=(t, h),
                    arrowprops=dict(arrowstyle="-|>", color=SEDA, lw=1.8, mutation_scale=18))
        ax.plot([t], [h], "o", color="black", ms=8, zorder=4)
        ax.annotate("", xy=(t + pd.Timedelta(hours=24), pak - 6), xytext=(t + pd.Timedelta(hours=24), h + 6),
                    arrowprops=dict(arrowstyle="<->", color=ORANZ, lw=1.8))
        ax.text(t + pd.Timedelta(hours=27), (h + pak) / 2, f"chyba {cislo(pak - h, 0)} cm", va="center", fontsize=15,
                color=ORANZ, weight="semibold", bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="none"))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{mdates.num2date(v).day}. 9."))
    ax.set_ylim(0, 760)
    ax.set_ylabel("hladina v Děčíně (cm)")
    osa_cisla(ax)
    ax.legend(loc="upper left")
    uloz(fig, "Z2_co_je_jako_ted.png")


def z3_srazky():
    od, do = "2024-09-10", "2024-09-21"
    D = nacti()[od:do]
    fig = plt.figure(figsize=(12, 6.75))
    a1, a2, a3 = fig.add_axes((0.1, 0.7, 0.86, 0.27)), fig.add_axes((0.1, 0.39, 0.86, 0.27)), \
        fig.add_axes((0.1, 0.08, 0.86, 0.27))
    sra = pd.concat({w: denni(w)["SRA"] for st in STANICE.values() for w in st}, axis=1).mean(axis=1)[od:do]
    a1.bar(sra.index + pd.Timedelta(hours=18), sra, width=pd.Timedelta(hours=18), color=MODRA_SVETLA)
    a2.plot(D.index, D.melnik_Q, color=MODRA, lw=2.6)
    a3.plot(D.index, D.decin_H, color="black", lw=2.6)
    konec, vrchol = pd.Timestamp("2024-09-17 06:00", tz="UTC"), D.decin_H.idxmax()
    for a, popis in ((a1, "déšť (mm za den)"), (a2, "Mělník (m³/s)"), (a3, "Děčín (cm)")):
        a.axvspan(konec, vrchol, color="#eeeeec", zorder=0)
        a.set_xlim(pd.Timestamp(od, tz="UTC"), pd.Timestamp(do, tz="UTC"))
        a.text(0.005, 0.95, popis, transform=a.transAxes, va="top", fontsize=15, color=INK, weight="semibold")
        a.xaxis.set_major_locator(mdates.DayLocator(interval=2))
        a.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{mdates.num2date(v).day}. 9."))
        osa_cisla(a)
    for a in (a1, a2):
        a.tick_params(labelbottom=False)
    a1.text(konec + (vrchol - konec) / 2, a1.get_ylim()[1] * 0.75, "už neprší", ha="center", fontsize=15, color=INK)
    a3.text(konec + (vrchol - konec) / 2, D.decin_H.min() + 40, "a Děčín ještě\n36 h stoupá", ha="center", fontsize=15,
            color=INK)
    uloz(fig, "Z3_proc_ne_srazky.png")


def z_honzovy_bez_nadpisu():
    """Nejistota a povodeň 2011 z src/grafy_slajdy.py, jen bez nadpisu, podtitulku a patičky."""
    puvodni = gs.slajd, gs.uloz
    jmena = {"nejistota.png": "Z4_jak_moc_se_pleteme.png", "povoden_2011.png": "Z5_povoden_2011.png"}

    def slajd(titulek, podtitulek, pata, rect=(0.085, 0.14, 0.89, 0.66)):
        l, b, w, h = rect
        return plocha((l, b - 0.03, w, 0.95 - b))
    gs.slajd = slajd
    gs.uloz = lambda fig, nazev: uloz(fig, jmena[nazev])
    try:
        gs.nejistota()
        gs.povoden("ridge", "jako_ted", "2011-01-08", "2011-01-24 23:00", "", "", "povoden_2011.png")
    finally:
        gs.slajd, gs.uloz = puvodni


if __name__ == "__main__":
    CIL.mkdir(exist_ok=True)
    shutil.copy(GRAFY / "mapbox2_porovnani.png", CIL / "02_mapa_decin.png")
    shutil.copy(GRAFY / "mapbox_povodi.png", CIL / "03a_mapa_stanic.png")
    for f in (s03b_kolik_dat, s04_vahy, s05_co_jsme_zkouseli, s06_jak_overujeme, s07_boris, s08a_test, s08b_vicenasobna,
              z1_srovnani_modelu, z2_jako_ted, z3_srazky, z_honzovy_bez_nadpisu):
        f()
