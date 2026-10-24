"""Grafy do prezentace na 7 minut (docs/PREZENTACE_7MIN.md), pojmenované podle slajdu. Všechny stejně: 16:9, krátký
nadpis vlevo nahoře, popisky os s jednotkami, legenda jen když je víc řad, žádné podtitulky ani patičky.
Barvy a data jako src/grafy_slajdy.py.

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

from data import SPA, nacti
from evaluate import casti
from features import tabulka
from grafy_ridge import RADKY, ZPOZDENI, vahy
from grafy_slajdy import (INK, INK2, JAKO_TED, MODRA, MODRA_SVETLA, ORANZ, PROC, RESULTS, ROOT, SEDA, STUPNE, cislo,
                          osa_cisla, posledni, predpovedi, predstih_3spa, prumer)
from krizova_validace import BLOKY
from meteo import STANICE, denni
from models import ridge

CIL = ROOT / "docs/grafy/prezentace"
GRAFY = ROOT / "docs/grafy"
NASE = "náš model"
CHYBA = "průměrná chyba během povodní (cm)"
plt.rcParams.update({"font.size": 16, "axes.labelsize": 16, "xtick.labelsize": 15, "ytick.labelsize": 15,
                     "legend.fontsize": 15, "axes.labelpad": 8})
PLOCHA = (0.09, 0.13, 0.88, 0.72)


def graf(titulek, rect=PLOCHA):
    fig = plt.figure(figsize=(12, 6.75))
    fig.text(0.04, 0.95, titulek, fontsize=24, weight="semibold", color=INK, va="top")
    return fig, fig.add_axes(rect)


def uloz(fig, nazev):
    fig.savefig(CIL / nazev, dpi=150)
    plt.close(fig)
    print(f"uloženo {(CIL / nazev).relative_to(ROOT)}")


def popis_sloupcu(ax, x, h, des=1, posun=0.6):
    for xi, v in zip(x, h):
        ax.text(xi, v + posun, cislo(v, des), ha="center", va="bottom", fontsize=16, weight="semibold", color=INK)


def osa_x_kategorie(ax, x, popisky):
    ax.set_xticks(x, popisky, color=INK)
    ax.tick_params(axis="x", length=0)


def dny(ax, mesic=9):
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{mdates.num2date(v).day}. {mesic}."))


def stupne(ax, cil="decin"):
    for n, (spa, barva) in enumerate(zip(SPA[cil], STUPNE), 1):
        ax.axhline(spa, color=barva, lw=2, zorder=1)
        ax.text(1.01, spa, f"{n}. stupeň", transform=ax.get_yaxis_transform(), ha="left", va="center", fontsize=14,
                color=INK2)


# hlavní slajdy ------------------------------------------------------------------------------------------------------
def s02b_doba_dobehu():
    # src/doba_dobehu.py, posun s největší korelací změn průtoku, trénink; docs/DATA.md (Doba doběhu do Děčína)
    stanice = [("Ústí nad Labem (Labe)", 4), ("Kostelec (Labe)", 10), ("Nymburk (Labe)", 10), ("Mělník (Labe)", 13),
               ("Vraňany (Vltava)", 13), ("Louny (Ohře)", 16), ("Praha (Vltava)", 17), ("Předměřice (Jizera)", 18),
               ("Přelouč (Labe)", 18), ("Beroun (Berounka)", 23), ("Nespeky (Sázava)", 25)]
    fig, ax = graf("Za kolik hodin doteče voda do Děčína", (0.27, 0.13, 0.7, 0.74))
    y = np.arange(len(stanice))[::-1]
    ax.barh(y, [h for _, h in stanice], 0.62, color=MODRA)
    for yi, (_, h) in zip(y, stanice):
        ax.text(h + 0.4, yi, f"{h} h", va="center", fontsize=15, weight="semibold", color=INK, zorder=3,
                bbox=dict(boxstyle="square,pad=0.1", facecolor="white", edgecolor="none"))
    ax.axvline(24, color=INK, lw=1.4, ls=(0, (5, 3)))
    ax.text(24.4, y[0] + 0.5, "předpověď\nna 24 h", va="center", fontsize=14, color=INK)
    ax.set_yticks(y, [n for n, _ in stanice], color=INK)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="y", visible=False)
    ax.spines["left"].set_visible(False)
    ax.set_xlim(0, 30)
    ax.set_ylim(-0.6, len(stanice) + 0.2)
    ax.set_xlabel("doba doběhu (h)")
    ax.xaxis.set_major_locator(MultipleLocator(6))
    osa_cisla(ax, "x")
    uloz(fig, "02b_doba_dobehu.png")


def s03_co_model_bere():
    # validace, prumer_povodne; docs/POKUSY.md pá 20:44, pá 22:32, so 23:14, so 0:19, so 8:42
    finalni = prumer(posledni("ridge"))
    polozky = [("srážky (naměřené)", 17.1, ORANZ), ("teplota vzduchu a sníh", 17.3, ORANZ),
               ("voda ve sněhu", 17.8, ORANZ), ("vlhkost vzduchu", 17.2, ORANZ), ("tlak vzduchu", 17.0, ORANZ),
               ("vítr (rychlost a směr)", 17.0, ORANZ), ("víc stanic proti proudu", 17.4, ORANZ),
               ("déšť na 3 dny dopředu,\nkdyby ho někdo znal přesně", 16.1, MODRA_SVETLA)]
    fig, ax = graf("Co se stane s chybou, když přidáme další vstup", (0.3, 0.13, 0.67, 0.72))
    y = np.arange(len(polozky))[::-1]
    ax.axvline(finalni, color=MODRA, lw=2.4, zorder=1)
    ax.text(finalni, len(polozky) - 0.25, f"finální model {cislo(finalni)} cm", ha="center", va="bottom", fontsize=15,
            weight="semibold", color=MODRA)
    ax.axvline(finalni - 1, color=INK2, lw=1.4, ls=(0, (5, 3)), zorder=1)
    ax.text(finalni - 1, len(polozky) - 0.25, "o 1 cm lépe (naše laťka)", ha="center", va="bottom", fontsize=15,
            color=INK2)
    for yi, (_, h, barva) in zip(y, polozky):
        ax.plot([finalni, h], [yi, yi], color="#d0d0d0", lw=2, zorder=2)
        ax.plot([h], [yi], "o", ms=13, color=barva, zorder=3)
        ax.text(h + (0.12 if h >= finalni else -0.12), yi, cislo(h), ha="left" if h >= finalni else "right",
                va="center", fontsize=15, weight="semibold", color=INK)
    ax.set_yticks(y, [n for n, _, _ in polozky], color=INK)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="y", visible=False)
    ax.spines["left"].set_visible(False)
    ax.set_xlim(15.5, 18.5)
    ax.set_ylim(-0.6, len(polozky) - 0.2)
    ax.set_xlabel(CHYBA)
    ax.xaxis.set_major_locator(MultipleLocator(1))
    osa_cisla(ax, "x")
    uloz(fig, "03_co_model_bere.png")


def s04_cesta_k_modelu():
    z = json.loads(sorted((RESULTS / "kolik_dat").glob("*_kolik_dat.json"))[-1].read_text(encoding="utf-8"))
    balicek = next(r for r in z["souhrn"] if r["sada"] == "kraj" and r["let"] == 2)["prumer_povodne"]
    skupiny = [  # validace, prumer_povodne; bez results/ běhu čísla z docs/POKUSY.md
        ("začátek", [(JAKO_TED, prumer(posledni("jako_ted")), SEDA), ("data jen z balíčku", balicek, ORANZ)]),
        ("čtyři modely", [("fyzikální model", prumer(posledni("fyzika")), ORANZ),
                          ("LightGBM (stromy)", prumer(posledni("lgbm")), ORANZ),
                          ("neuronová síť", prumer(posledni("mlp")), ORANZ),
                          ("lineární regrese", prumer(posledni("ridge")), MODRA)]),
        ("úpravy přímky", [("doba putování podle průtoku", 21.8, ORANZ),  # pá 20:45
                           ("polynom 2. stupně", prumer(posledni("ridge_polynom_soucin")), ORANZ),
                           ("větší váha povodní", prumer(posledni("ridge_vahy")), ORANZ),
                           ("malá zlepšení dohromady", 17.2, ORANZ)]),  # so 0:43
    ]
    fig, ax = graf("Od 44 cm k 17 cm: cesta k finálnímu modelu", (0.3, 0.12, 0.67, 0.74))
    y, radky, nadpisy = 0, [], []
    for nazev, polozky in skupiny:
        nadpisy.append((nazev, y))
        y -= 1
        for n, h, barva in polozky:
            radky.append((y, n, h, barva))
            y -= 1
        y -= 0.4
    ax.barh([r[0] for r in radky], [r[2] for r in radky], 0.66, color=[r[3] for r in radky])
    for yi, _, h, _ in radky:
        ax.text(h + 0.4, yi, cislo(h), va="center", fontsize=15, weight="semibold", color=INK)
    for nazev, yi in nadpisy:
        ax.text(-0.01, yi, nazev, transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=15,
                weight="semibold", color=INK2)
    ax.set_yticks([r[0] for r in radky], [r[1] for r in radky], color=INK)
    ax.get_yticklabels()[[r[1] for r in radky].index("lineární regrese")].set_weight("semibold")
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="y", visible=False)
    ax.spines["left"].set_visible(False)
    ax.set_xlim(0, 50)
    ax.set_ylim(y + 0.6, 0.6)
    ax.set_xlabel(CHYBA)
    ax.xaxis.set_major_locator(MultipleLocator(10))
    osa_cisla(ax, "x")
    uloz(fig, "04_cesta_k_modelu.png")


def s05_soucet_rek():
    # finální model (učený do 2020) a předpověď vydaná 14. 9. 2024 v 11:00 SELČ, se kterou varoval před 3. stupněm
    X, y = tabulka("decin", 24)
    tr = casti("decin", 24, finalni=True).reindex(X.index) == "train"
    m = ridge.pipeline(ridge.PARAMETRY["alpha"]).fit(X[tr], y[tr])
    t = pd.Timestamp("2024-09-14 09:00", tz="UTC")
    pris = pd.Series(m[-1].coef_ * np.asarray(m[:-1].transform(X.loc[[t]]))[0], index=X.columns)
    pris = pris.groupby(lambda c: c.split("_")[0]).sum()
    skupiny = {"Děčín\na Ústí": ["decin", "usti"], "Vltava": ["praha", "vranany", "beroun", "sazava"],
               "horní\nLabe": ["kostelec", "nymburk", "jizera", "prelouc"], "Mělník": ["melnik"], "Ohře": ["louny"]}
    kroky = [(k, pris[s].sum()) for k, s in skupiny.items()]
    zaklad, predpoved = m[-1].intercept_, m.predict(X.loc[[t]])[0]
    assert abs(zaklad + sum(v for _, v in kroky) - predpoved) < 0.01
    fig, ax = graf("Voda v Děčíně je součet řek", (0.09, 0.13, 0.82, 0.72))
    x = np.arange(len(kroky) + 2)
    ax.bar(0, zaklad, 0.6, color=SEDA)
    ax.text(0, zaklad + 8, cislo(zaklad, 0), ha="center", va="bottom", fontsize=16, weight="semibold")
    dosud = zaklad
    for xi, (_, v) in zip(x[1:-1], kroky):
        ax.bar(xi, v, 0.6, bottom=dosud, color=MODRA_SVETLA if v >= 0 else ORANZ)
        # popisky z rozdílů zaokrouhlených mezisoučtů, aby celá čísla dala dohromady předpověď
        krok = round(dosud + v) - round(dosud)
        ax.text(xi, max(dosud, dosud + v) + 8, f"{'+' if krok >= 0 else '−'}{abs(krok)}", ha="center",
                va="bottom", fontsize=16, weight="semibold")
        dosud += v
    ax.bar(x[-1], predpoved, 0.6, color=MODRA)
    ax.text(x[-1], predpoved + 8, cislo(predpoved, 0), ha="center", va="bottom", fontsize=16, weight="semibold")
    stupne(ax)
    osa_x_kategorie(ax, x, ["průměrná\nhladina"] + [k for k, _ in kroky] + ["předpověď\nna 15. 9."])
    ax.get_xticklabels()[-1].set_weight("semibold")
    ax.set_ylim(0, 700)
    ax.set_ylabel("hladina v Děčíně za 24 h (cm)")
    ax.yaxis.set_major_locator(MultipleLocator(100))
    osa_cisla(ax)
    uloz(fig, "05_soucet_rek.png")
    return dict(zaklad=round(zaklad, 1), predpoved=round(predpoved, 1), kroky=[(k, round(v, 1)) for k, v in kroky])


def s06_jak_overujeme():
    t = lambda d: mdates.date2num(pd.Timestamp(d))
    fig, ax = graf("Tři ověření, pokaždé na povodních, které model neviděl", (0.26, 0.13, 0.71, 0.68))
    vys = 0.55
    radky = [("1. výběr modelu\n4 povodně", [("2006", "2019", MODRA_SVETLA), ("2019", "2021", ORANZ)],
              ["2006-04-03", "2009-03-07", "2010-09-29", "2011-01-17"]),
             ("2. vícenásobná validace\n8 povodní", [("2006", "2021", MODRA_SVETLA)], [d[0] for d in BLOKY.values()]),
             ("3. test\njednou na konci", [("2006", "2021", MODRA_SVETLA), ("2021", "2026", MODRA)], [])]
    for yy, (_, useky, povodne) in zip((2, 1, 0), radky):
        for od, do, barva in useky:
            ax.barh(yy, t(f"{do}-01-01") - t(f"{od}-01-01"), vys, left=t(f"{od}-01-01"), color=barva)
        for d in povodne:
            ax.barh(yy, 45, vys, left=t(d) - 22, color=ORANZ)
    ax.set_yticks([2, 1, 0], [r[0] for r in radky], color=INK)
    ax.tick_params(axis="y", length=0)
    ax.set_xticks([t(d) for d in ("2006-01-01", "2019-01-01", "2021-01-01", "2025-12-31")],
                  ["2006", "2019", "2021", "2025"])
    ax.set_xlim(t("2005-09-01"), t("2026-02-01"))
    ax.set_ylim(-0.5, 2.5)
    ax.set_xlabel("rok")
    ax.grid(False)
    ax.spines["left"].set_visible(False)
    for barva, nazev in ((MODRA_SVETLA, "učení"), (ORANZ, "ověření"), (MODRA, "test")):
        ax.barh(np.nan, 0, color=barva, label=nazev)
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=3, handlelength=1.2, frameon=False)
    uloz(fig, "06_jak_overujeme.png")


def povoden(titulek, ridge_soubor, jako_ted_soubor, od, do, nazev, mesic):
    r, j = predpovedi(ridge_soubor)[od:do], predpovedi(jako_ted_soubor)[od:do]
    hodin = predstih_3spa(r, od, do)[3]
    cas = lambda i: i.tz_localize(None)
    fig, ax = graf(titulek.format(h=cislo(hodin, 0)), (0.09, 0.13, 0.82, 0.72))
    stupne(ax)
    ax.plot(cas(j.index), j.predpoved, color=SEDA, ls=(0, (5, 3)), lw=2.2, label=JAKO_TED)
    ax.plot(cas(r.index), r.skutecnost, color="black", lw=3, label="skutečnost")
    ax.plot(cas(r.index), r.predpoved, color=MODRA, lw=3, label=f"{NASE}, 24 h předem")
    dny(ax, mesic)
    ax.set_xlim(cas(r.index[0]), cas(r.index[-1]))
    ax.set_ylim(0, 800)
    ax.set_ylabel("hladina v Děčíně (cm)")
    ax.yaxis.set_major_locator(MultipleLocator(100))
    osa_cisla(ax)
    ax.legend(loc="upper left", handlelength=2.4, frameon=False)
    uloz(fig, nazev)
    return hodin


def s07_boris():
    return povoden("Boris 2024: varování {h} hodin předem", "ridge_test", "jako_ted_test", "2024-09-10",
                   "2024-09-22 23:00", "07_boris_2024.png", 9)


def dvojice_sloupcu(ax, x, a, b, s=0.36):
    ax.bar(x - s / 2 - 0.01, a, s, color=SEDA, label=JAKO_TED)
    ax.bar(x + s / 2 + 0.01, b, s, color=MODRA, label=NASE)


# záložní slajdy -----------------------------------------------------------------------------------------------------
def z1_srovnani_modelu():
    modely = [("jako_ted", JAKO_TED), ("fyzika", "fyzikální"), ("lgbm", "LightGBM"), ("mlp", "neuronová síť"),
              ("ridge", "lineární regrese")]
    h = [prumer(posledni(m)) for m, _ in modely]
    fig, ax = graf("Čtyři modely na validaci: vyhrál nejjednodušší")
    x = np.arange(len(modely))
    ax.bar(x, h, 0.56, color=[SEDA, ORANZ, ORANZ, ORANZ, MODRA])
    popis_sloupcu(ax, x, h)
    osa_x_kategorie(ax, x, [n for _, n in modely])
    ax.set_ylim(0, 50)
    ax.set_ylabel(CHYBA)
    ax.yaxis.set_major_locator(MultipleLocator(10))
    osa_cisla(ax)
    uloz(fig, "Z1_srovnani_ctyr_modelu.png")


def z2_jako_ted():
    skutecnost = nacti().decin_H["2024-09-12":"2024-09-21"].tz_convert("Europe/Prague").tz_localize(None)
    jako_ted = skutecnost.shift(24, freq="h")[:skutecnost.index[-1]]
    fig, ax = graf("„Bude jako teď“ je vždycky o den pozadu")
    ax.plot(skutecnost.index, skutecnost, color="black", lw=3, label="skutečnost")
    ax.plot(jako_ted.index, jako_ted, color=SEDA, lw=2.4, ls=(0, (5, 3)), label=JAKO_TED)
    for t in pd.to_datetime(["2024-09-13 14:00", "2024-09-14 08:00", "2024-09-15 02:00"]):
        h, pak = skutecnost[t], skutecnost[t + pd.Timedelta(hours=24)]
        ax.annotate("", xy=(t + pd.Timedelta(hours=24), h), xytext=(t, h),
                    arrowprops=dict(arrowstyle="-|>", color=SEDA, lw=1.8, mutation_scale=18))
        ax.plot([t], [h], "o", color="black", ms=8, zorder=4)
        ax.annotate("", xy=(t + pd.Timedelta(hours=24), pak - 6), xytext=(t + pd.Timedelta(hours=24), h + 6),
                    arrowprops=dict(arrowstyle="<->", color=ORANZ, lw=1.8))
        ax.text(t + pd.Timedelta(hours=27), (h + pak) / 2, f"{cislo(pak - h, 0)} cm", va="center", fontsize=15,
                color=ORANZ, weight="semibold", bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="none"))
    dny(ax)
    ax.set_ylim(0, 800)
    ax.set_ylabel("hladina v Děčíně (cm)")
    ax.yaxis.set_major_locator(MultipleLocator(100))
    osa_cisla(ax)
    ax.legend(loc="upper left", frameon=False)
    uloz(fig, "Z2_co_je_jako_ted.png")


def z3_srazky():
    od, do = "2024-09-10", "2024-09-21"
    D = nacti()[od:do]
    fig = plt.figure(figsize=(12, 6.75))
    fig.text(0.04, 0.95, "Když se blíží vrchol, už neprší", fontsize=24, weight="semibold", color=INK, va="top")
    osy = [fig.add_axes((0.13, b, 0.84, 0.2)) for b in (0.63, 0.38, 0.13)]
    sra = pd.concat({w: denni(w)["SRA"] for st in STANICE.values() for w in st}, axis=1).mean(axis=1)[od:do]
    osy[0].bar(sra.index + pd.Timedelta(hours=18), sra, width=pd.Timedelta(hours=18), color=MODRA_SVETLA)
    osy[1].plot(D.index, D.melnik_Q, color=MODRA, lw=2.6)
    osy[2].plot(D.index, D.decin_H, color="black", lw=2.6)
    konec, vrchol = pd.Timestamp("2024-09-17 06:00", tz="UTC"), D.decin_H.idxmax()
    for a, popis in zip(osy, ("déšť v povodí\n(mm za den)", "průtok Mělník\n(m³/s)", "hladina Děčín\n(cm)")):
        a.axvspan(konec, vrchol, color="#e9e9e6", zorder=0)
        a.set_xlim(pd.Timestamp(od, tz="UTC"), pd.Timestamp(do, tz="UTC"))
        a.set_ylabel(popis, fontsize=14)
        dny(a)
        osa_cisla(a)
    for a in osy[:2]:
        a.tick_params(labelbottom=False)
    osy[0].text(konec + (vrchol - konec) / 2, osy[0].get_ylim()[1] * 0.7, "neprší", ha="center", fontsize=15, color=INK)
    uloz(fig, "Z3_proc_ne_srazky.png")


def z4_nejistota():
    I = json.loads((ROOT / "models/ridge_intervaly.json").read_text(encoding="utf-8"))
    kombinace = [(c, h) for c in ("decin", "usti") for h in (12, 24, 36)]
    a = [100 * I[f"{c}_{h}"]["pokryti_val"] for c, h in kombinace]
    b = [100 * I[f"{c}_{h}"]["pokryti_povodne"] for c, h in kombinace]
    fig, ax = graf("Jak často je skutečnost v rozmezí od–do")
    x = np.array([0, 1, 2, 3.4, 4.4, 5.4])
    s = 0.36
    ax.bar(x - s / 2 - 0.01, a, s, color=MODRA_SVETLA, label="celá validace")
    ax.bar(x + s / 2 + 0.01, b, s, color=MODRA, label="jen povodně")
    popis_sloupcu(ax, x - s / 2 - 0.01, a, des=0, posun=0.8)
    popis_sloupcu(ax, x + s / 2 + 0.01, b, des=0, posun=0.8)
    ax.axhline(90, color=INK, lw=1.4, ls=(0, (5, 3)))
    ax.text(5.95, 91, "cíl 90 %", ha="right", va="bottom", fontsize=14, color=INK)
    osa_x_kategorie(ax, x, [f"{'Děčín' if c == 'decin' else 'Ústí'}\nza {h} h" for c, h in kombinace])
    ax.set_xlim(-0.6, 6.0)
    ax.set_ylim(0, 125)
    ax.set_ylabel("skutečnost v rozmezí (%)")
    ax.set_yticks([0, 25, 50, 75, 100])
    osa_cisla(ax)
    ax.legend(loc="upper left", ncol=2, frameon=False)
    uloz(fig, "Z4_jak_moc_se_pleteme.png")


def z5_povoden_2011():
    return povoden("Povodeň 2011: varování {h} hodin předem", "ridge", "jako_ted", "2011-01-08", "2011-01-22 23:00",
                   "Z5_povoden_2011.png", 1)


def z6_vahy():
    W = vahy("decin", 24)
    jmena = {"decin": "Děčín", "usti": "Ústí", "louny": "Louny", "melnik": "Mělník", "vranany": "Vraňany",
             "kostelec": "Kostelec", "praha": "Praha", "nymburk": "Nymburk", "jizera": "Jizera", "beroun": "Beroun",
             "sazava": "Sázava", "prelouc": "Přelouč"}
    radky = [f"{jmena[s]} {'hladina' if v == 'H' else 'průtok'}" for s, v in RADKY]
    fig, ax = graf("Váhy modelu pro Děčín za 24 h", (0.2, 0.13, 0.64, 0.74))
    m = np.nanmax(np.abs(W.to_numpy()))
    cmap = LinearSegmentedColormap.from_list("vahy", [ORANZ, "#f7f7f7", MODRA])
    im = ax.imshow(np.ma.masked_invalid(W.to_numpy()), cmap=cmap, vmin=-m, vmax=m, aspect="auto")
    ax.set_facecolor("#ececec")
    ax.grid(False)
    ax.set_xticks(np.arange(W.shape[1] + 1) - 0.5, minor=True)
    ax.set_yticks(np.arange(W.shape[0] + 1) - 0.5, minor=True)
    ax.grid(which="minor", color="white", lw=2)
    ax.tick_params(which="both", length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_xticks(range(len(ZPOZDENI)), ["teď" if z == 0 else f"{z} h" for z in ZPOZDENI])
    ax.set_xlabel("změřeno před")
    ax.set_yticks(range(len(radky)), radky, fontsize=14, color=INK)
    cax = fig.add_axes((0.87, 0.13, 0.018, 0.74))
    cb = fig.colorbar(im, cax=cax)
    cb.outline.set_visible(False)
    cb.ax.tick_params(length=0, labelsize=14)
    cb.ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: cislo(v, 0).replace("-", "−")))
    cb.set_label("změna předpovědi při vyšší hodnotě (cm)", fontsize=14)
    uloz(fig, "Z6_vahy_modelu.png")


def z8_test():
    R, J = posledni("ridge", "test"), posledni("jako_ted", "test")
    po = lambda Z, hz: np.mean([v["mae_povodne"] for v in Z["vysledky"] if v["horizont"] == hz])
    a = [po(J, hz) for hz in (12, 24, 36)] + [prumer(J)]
    b = [po(R, hz) for hz in (12, 24, 36)] + [prumer(R)]
    fig, ax = graf(f"Test 2021–2025: o {cislo(100 * (1 - b[-1] / a[-1]), 0)}{PROC} menší chyba")
    x = np.array([0, 1, 2, 3.35])
    dvojice_sloupcu(ax, x, a, b)
    popis_sloupcu(ax, x - 0.19, a)
    popis_sloupcu(ax, x + 0.19, b)
    osa_x_kategorie(ax, x, ["za 12 h", "za 24 h", "za 36 h", "celkem"])
    ax.get_xticklabels()[-1].set_weight("semibold")
    ax.axvline(2.67, color="#d0d0d0", lw=1)
    ax.set_xlim(-0.6, 3.95)
    ax.set_ylim(0, 80)
    ax.set_xlabel("předpověď dopředu")
    ax.set_ylabel(CHYBA)
    ax.yaxis.set_major_locator(MultipleLocator(20))
    osa_cisla(ax)
    ax.legend(loc="upper left", frameon=False)
    uloz(fig, "Z8_test_2021_2025.png")


def z9_vicenasobna():
    R = pd.read_csv(sorted((RESULTS / "krizova_validace").glob("*.csv"))[-1])
    P = R.groupby(["povoden", "model"]).chyba.mean().unstack()
    P = P.loc[sorted(P.index)]
    a, b = list(P.jako_ted) + [P.jako_ted.mean()], list(P.ridge) + [P.ridge.mean()]
    fig, ax = graf(f"Vícenásobná validace: o {cislo(100 * (1 - b[-1] / a[-1]), 0)}{PROC} menší chyba na 8 povodních")
    x = np.arange(len(a)) * 1.0
    x[-1] += 0.5
    dvojice_sloupcu(ax, x, a, b, 0.38)
    popis_sloupcu(ax, [x[-1] - 0.2], [a[-1]])
    popis_sloupcu(ax, [x[-1] + 0.2], [b[-1]])
    osa_x_kategorie(ax, x, [f"{p[5:].lstrip('0')}/{p[:4]}" for p in P.index] + ["průměr"])
    ax.get_xticklabels()[-1].set_weight("semibold")
    ax.axvline(x[-2] + 0.75, color="#d0d0d0", lw=1)
    ax.set_xlim(-0.6, x[-1] + 0.6)
    ax.set_ylim(0, 80)
    ax.set_xlabel("vynechaná povodeň")
    ax.set_ylabel(CHYBA)
    ax.yaxis.set_major_locator(MultipleLocator(20))
    osa_cisla(ax)
    ax.legend(loc="upper left", ncol=2, frameon=False)
    uloz(fig, "Z9_vicenasobna_validace.png")


def z10_proc_externi_data():
    z = json.loads(sorted((RESULTS / "kolik_dat").glob("*_kolik_dat.json"))[-1].read_text(encoding="utf-8"))
    balicek = next(r for r in z["souhrn"] if r["sada"] == "kraj" and r["let"] == 2)["prumer_povodne"]
    h = [prumer(posledni("jako_ted")), balicek, prumer(posledni("ridge"))]
    fig, ax = graf("Jen s daty z balíčku by model nefungoval")
    x = np.arange(3)
    ax.bar(x, h, 0.56, color=[SEDA, ORANZ, MODRA])
    popis_sloupcu(ax, x, h)
    osa_x_kategorie(ax, x, [JAKO_TED, "data z balíčku\n2 roky, 3 stanice", "naše data\n20 let, 12 stanic"])
    ax.set_ylim(0, 50)
    ax.set_ylabel(CHYBA)
    ax.yaxis.set_major_locator(MultipleLocator(10))
    osa_cisla(ax)
    uloz(fig, "Z10_proc_externi_data.png")


if __name__ == "__main__":
    CIL.mkdir(exist_ok=True)
    shutil.copy(GRAFY / "mapbox2_porovnani.png", CIL / "01_mapa_decin.png")
    shutil.copy(GRAFY / "mapbox_povodi.png", CIL / "02a_mapa_stanic.png")
    s02b_doba_dobehu()
    s03_co_model_bere()
    s04_cesta_k_modelu()
    print("  součet:", s05_soucet_rek())
    s06_jak_overujeme()
    print("  Boris předstih h:", s07_boris())
    z1_srovnani_modelu()
    z2_jako_ted()
    z3_srazky()
    z4_nejistota()
    print("  2011 předstih h:", z5_povoden_2011())
    z6_vahy()
    z8_test()
    z9_vicenasobna()
    z10_proc_externi_data()
