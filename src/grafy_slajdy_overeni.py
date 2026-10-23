"""Tři grafy do prezentace ve stylu src/grafy_slajdy.py: jak ověřujeme, vícenásobná validace a všechno, co jsme zkoušeli.

python src/grafy_slajdy_overeni.py    uloží docs/grafy/slajdy/jak_overujeme.png, vicenasobna_validace.png, vse_co_jsme_zkouseli.png
Nic netrénuje, čte jen results/ a čísla z docs/POKUSY.md.
"""
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from matplotlib.ticker import MultipleLocator

from data import nacti
from grafy_slajdy import (INK, INK2, INK3, JAKO_TED, MODRA, MODRA_SVETLA, ORANZ, PROC, RESULTS, SEDA, cislo, mene,
                          osa_cisla, posledni, prumer, slajd, uloz)
from krizova_validace import BLOKY


def jak_overujeme():
    # rozdělení ze src/evaluate.py, povodně pro vícenásobnou validaci ze src/krizova_validace.py
    fig, ax = slajd("Ověřujeme třikrát, pokaždé na povodních, které model při učení neviděl",
                    "Hodinová data 2006–2025. Model se učí jen z minulosti a z toho, co bylo v okamžiku předpovědi změřené",
                    "Validace: 16 dní před vrcholem až 5 po, 20 dní kolem vynecháno z učení · test spuštěn jednou, pá 21:00,"
                    " model vybraný předem · vícenásobná validace bez testu",
                    rect=(0.16, 0.12, 0.8, 0.62))
    t = lambda d: mdates.date2num(pd.Timestamp(d))
    radky = {"1. validace": 2, "2. vícenásobná\nvalidace": 1, "3. test": 0}
    vys = 0.5
    # 1. validace: učení 2006–2018, 4 povodně a 2019–2020 stranou
    ax.barh(2, t("2019-01-01") - t("2006-01-01"), vys, left=t("2006-01-01"), color=MODRA_SVETLA)
    for d in ("2006-04-03", "2009-03-07", "2010-09-29", "2011-01-17"):
        ax.barh(2, 40, vys, left=t(d) - 20, color=ORANZ)
    ax.barh(2, t("2021-01-01") - t("2019-01-01"), vys, left=t("2019-01-01"), color=ORANZ)
    # 2. vícenásobná: 8 povodní, každá jednou vynechaná
    ax.barh(1, t("2021-01-01") - t("2006-01-01"), vys, left=t("2006-01-01"), color=MODRA_SVETLA)
    for dny in BLOKY.values():
        ax.barh(1, 40, vys, left=t(dny[0]) - 20, color=ORANZ)
    # 3. test
    ax.barh(0, t("2021-01-01") - t("2006-01-01"), vys, left=t("2006-01-01"), color=MODRA_SVETLA)
    ax.barh(0, t("2026-01-01") - t("2021-01-01"), vys, left=t("2021-01-01"), color=MODRA)
    texty = {2: "učení 2006–2018, výběr modelu na 4 povodních a 2019–2020",
             1: "každá z 8 povodní jednou vynechaná, model učený na ostatních",
             0: "jednou na konci: 2021–2025, 4 povodně včetně Borise"}
    for y, text in texty.items():
        ax.text(t("2006-01-01"), y + vys / 2 + 0.06, text, ha="left", va="bottom", fontsize=13, color=INK)
    ax.set_yticks(list(radky.values()), list(radky), fontsize=14, color=INK)
    ax.get_yticklabels()[0].set_weight("semibold")
    ax.tick_params(axis="y", length=0)
    ax.xaxis_date()
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_xlim(t("2005-07-01"), t("2026-03-01"))
    ax.set_ylim(-0.6, 2.75)
    ax.grid(False)
    ax.spines["left"].set_visible(False)
    for barva, nazev in ((MODRA_SVETLA, "učení"), (ORANZ, "ověření"), (MODRA, "test")):
        ax.barh(np.nan, 0, color=barva, label=nazev)
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=3, handlelength=1.2)
    uloz(fig, "jak_overujeme.png")


def vicenasobna_validace():
    # results/krizova_validace/*.csv (src/krizova_validace.py, pá 23:27), průměr 6 kombinací cíle a horizontu
    R = pd.read_csv(sorted((RESULTS / "krizova_validace").glob("*.csv"))[-1])
    P = R.groupby(["povoden", "model"]).chyba.mean().unstack()
    P = P.loc[sorted(P.index)]
    H = nacti().decin_H
    zlepseni = 100 * (1 - P.ridge / P.jako_ted)
    fig, ax = slajd(f"Na každé z 8 povodní menší chyba o {cislo(zlepseni.min(), 0)} až {cislo(zlepseni.max(), 0)}{PROC},"
                    " výsledek není náhoda výběru",
                    "Průměrná chyba hladiny během povodně (cm). Každá povodeň jednou vynechaná, model naučený na ostatních",
                    "Data ČHMÚ 2006–2020, test nepoužitý · průměr Děčín a Ústí, 12 / 24 / 36 h · v závorce vrchol v Děčíně"
                    f" · průměr ostatních modelů: síť {cislo(P.mlp.mean())}, LightGBM {cislo(P.lgbm.mean())},"
                    f" fyzikální {cislo(P.fyzika.mean())} cm",
                    rect=(0.085, 0.2, 0.89, 0.6))
    x = np.arange(len(P) + 1) * 1.0
    x[-1] += 0.45
    j = list(P.jako_ted) + [P.jako_ted.mean()]
    r = list(P.ridge) + [P.ridge.mean()]
    s = 0.36
    ax.bar(x - s / 2 - 0.01, j, s, color=SEDA, label=JAKO_TED)
    ax.bar(x + s / 2 + 0.01, r, s, color=MODRA, label="lineární regrese (finální)")
    for xi, a, b in zip(x, j, r):
        ax.text(xi + s / 2 + 0.01, b + 1, cislo(b), ha="center", va="bottom", fontsize=12, weight="semibold")
        ax.annotate(mene(b, a).replace("o ", "−").replace(" méně", ""), (xi, 0), xycoords=("data", "axes fraction"),
                    xytext=(0, -42), textcoords="offset points", ha="center", va="top", fontsize=12, color=MODRA)
    popisky = [f"{p[5:].lstrip('0')}/{p[2:4]}\n({cislo(H[p].max(), 0)} cm)" for p in P.index] + ["průměr"]
    ax.set_xticks(x, popisky, fontsize=12, color=INK)
    ax.get_xticklabels()[-1].set_weight("semibold")
    ax.tick_params(axis="x", length=0)
    ax.axvline(x[-2] + 0.72, color="#d0d0d0", lw=1)
    ax.set_xlim(-0.6, x[-1] + 0.6)
    ax.set_ylim(0, 80)
    ax.set_ylabel("cm")
    ax.yaxis.set_major_locator(MultipleLocator(20))
    osa_cisla(ax)
    ax.legend(loc="upper left", ncol=2)
    uloz(fig, "vicenasobna_validace.png")
    return zlepseni


def vse_co_jsme_zkouseli():
    # validace, prumer_povodne; z results/, kde běh je uložený, jinak z docs/POKUSY.md (čas záznamu v komentáři)
    finalni = prumer(posledni("ridge"))
    polozky = [
        ("jen balíček: 2 roky, 3 stanice v kraji", 44.6, ORANZ),  # pá 20:55 Honza, results/kolik_dat
        ("fyzikální model", prumer(posledni("fyzika")), ORANZ),
        ("LightGBM (rozhodovací stromy)", prumer(posledni("lgbm")), ORANZ),
        ("polynom 2. stupně", prumer(posledni("ridge_polynom")), ORANZ),
        ("doba putování podle průtoku", 21.8, ORANZ),  # pá 20:45 Dan, ridge_doba
        ("polynom se součiny", prumer(posledni("ridge_polynom_soucin")), ORANZ),
        ("povodňové hodiny s váhou 20×", prumer(posledni("ridge_vahy20")), ORANZ),
        ("neuronová síť", prumer(posledni("mlp")), ORANZ),
        ("+ voda ve sněhu", 17.8, ORANZ),  # so 23:14
        ("+ srážky, sníh a teplota", 17.4, ORANZ),  # pá 20:44
        ("+ horní Ohře (víc stanic)", 17.4, ORANZ),  # so 0:19
        ("všechna malá zlepšení dohromady", 17.2, ORANZ),  # so 0:43
        ("lineární regrese (finální)", finalni, MODRA),
    ]
    fig, ax = slajd("Zkusili jsme 12 jiných cest, žádná nebyla lepší než lineární regrese",
                    "Průměrná chyba hladiny během povodní (cm) na validaci. Modře finální model, „bude jako teď“ má 44,3 cm",
                    "Data ČHMÚ 2006–2020 · validace: 4 povodně (2006, 2009, 2010, 2011) · průměr Děčín a Ústí, 12 / 24 / 36 h"
                    " · podrobnosti v docs/CESTA_MODELU.md",
                    rect=(0.33, 0.1, 0.63, 0.74))
    y = np.arange(len(polozky))[::-1]
    ax.barh(y, [h for _, h, _ in polozky], 0.66, color=[b for _, _, b in polozky])
    for yi, (_, h, _) in zip(y, polozky):
        rozdil = round(h, 1) - round(finalni, 1)
        ax.text(h + 0.5, yi, f"{cislo(h)} cm" + (f"   +{cislo(rozdil)}" if rozdil > 0 else ""), va="center",
                fontsize=12.5, weight="semibold" if h == finalni else "normal", color=INK)
    ax.axvline(finalni, color=MODRA, lw=1.5, ls=(0, (4, 3)), zorder=0)
    ax.set_yticks(y, [n for n, _, _ in polozky], fontsize=13, color=INK)
    ax.get_yticklabels()[-1].set_weight("semibold")
    ax.tick_params(axis="y", length=0)
    ax.grid(False)
    ax.spines["left"].set_visible(False)
    ax.set_xlim(0, 56)
    ax.xaxis.set_major_locator(MultipleLocator(10))
    osa_cisla(ax, "x")
    uloz(fig, "vse_co_jsme_zkouseli.png")
    return polozky


if __name__ == "__main__":
    jak_overujeme()
    print("  zlepšení po povodních:", vicenasobna_validace().round(0).to_dict())
    print("  zkoušeli:", [(n, cislo(h)) for n, h, _ in vse_co_jsme_zkouseli()])
