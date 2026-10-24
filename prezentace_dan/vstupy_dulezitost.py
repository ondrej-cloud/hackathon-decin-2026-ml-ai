"""Co jde do finálního modelu (týmový Ridge) a jak důležité jsou jednotlivé stanice, Děčín +12 / +24 / +36 h.

    set PYTHONUTF8=1
    python prezentace_dan/vstupy_dulezitost.py

Důležitost po stanicích (všechna zpoždění stanice dohromady), protože sousední zpoždění jsou skoro stejná a jednotlivé
váhy by klamaly:
- vyřazení: stanici z modelu vyřadit, model znovu natrénovat (src/models/ridge.py, sloupce bez stanice) a změřit,
  o kolik vzroste chyba na povodních ve validaci (okna jako evaluate.vyhodnot);
- kontrola, skupinová permutace: plný model, na validaci se sloupce stanice zamíchají společně (5 opakování).
Navíc vyřazení celé větve (Vltava, horní Labe, všech 10 stanic proti proudu), protože sousedé se zastoupí.
Jen trénovací a validační část, test 2021–2025 se nepoužije. Výsledek: vysledky/vstupy_dulezitost.csv a .json,
vysledky/vstupy_dulezitost_vetve.csv,
grafy grafy/V1_co_jde_do_modelu.png, V2_dulezitost_stanic.png, V3_dulezitost_permutace.png,
V4_dulezitost_vetvi.png.
"""
import json
import sys
from pathlib import Path

ZDE = Path(__file__).resolve().parent
sys.path[:0] = [str(ZDE.parent / "src"), str(ZDE)]

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

import grafy_dan as G  # noqa: E402  (styl, barvy, doby doběhu, schéma stanic)
from data import CILE, PROTI_PROUDU, SPA  # noqa: E402
from evaluate import PO, PRED, casti, povodne, vyhodnot  # noqa: E402
from features import ZPOZDENI_H, ZPOZDENI_Q, tabulka  # noqa: E402
from models import ridge  # noqa: E402

CIL = "decin"
HORIZONTY = (12, 24, 36)
STANICE = list(CILE) + list(PROTI_PROUDU)
OPAKOVANI = 5
VYSLEDKY = ZDE / "vysledky"


def mae_povodne(y, pred, cil=CIL):
    """Stejně jako evaluate.vyhodnot (mae_povodne), jen nezaokrouhleně."""
    pred = pd.Series(np.asarray(pred, dtype=float), index=y.index)
    okno = pd.Series(False, index=y.index)
    for v in povodne(y, SPA[cil][1]):
        okno[v - PRED: v + PO] = True
    return float((pred - y).abs()[okno].mean())


def spocitej():
    radky = []
    for h in HORIZONTY:
        X, y = tabulka(CIL, h)
        c = casti(CIL, h).reindex(X.index)
        tr, ev = c == "train", c == "val"
        plny = ridge.fit(X[tr], y[tr], CIL, h)
        zaklad = mae_povodne(y[ev], plny(X[ev]))
        kontrola = vyhodnot(y[ev], np.asarray(plny(X[ev])), CIL, h)["mae_povodne"]
        print(f"+{h} h: plný model {zaklad:.2f} cm (vyhodnot {kontrola}), {int(tr.sum())} train / {int(ev.sum())} val")
        for s in STANICE:
            sl = [k for k in X.columns if k.startswith(f"{s}_")]
            bez = ridge.fit(X[tr], y[tr], CIL, h, sloupce=[k for k in X.columns if k not in sl])
            vyr = mae_povodne(y[ev], bez(X[ev])) - zaklad
            perm = []
            for i in range(OPAKOVANI):
                rng = np.random.default_rng(42 + i)
                Xp = X[ev].copy()
                Xp[sl] = Xp[sl].to_numpy()[rng.permutation(len(Xp))]
                perm.append(mae_povodne(y[ev], plny(Xp)) - zaklad)
            radky.append(dict(horizont=h, stanice=s, sloupcu=len(sl), zaklad=round(zaklad, 3), vyrazeni=round(vyr, 3),
                              permutace=round(float(np.mean(perm)), 3), permutace_sd=round(float(np.std(perm)), 3)))
            print(f"   {s:9s} vyřazení {vyr:+6.2f} cm, permutace {np.mean(perm):+6.2f} ± {np.std(perm):.2f}")
    return pd.DataFrame(radky)


def spocitej_skupiny():
    """Vyřazení celé větve najednou: sousední stanice na stejné řece se navzájem zastoupí, po jedné to podceňuje."""
    skupiny = {"vltava": G.VETVE["vltava"][2], "labe_horni": G.VETVE["labe_horni"][2],
               "vse_proti_proudu": list(PROTI_PROUDU)}
    radky = []
    for h in HORIZONTY:
        X, y = tabulka(CIL, h)
        c = casti(CIL, h).reindex(X.index)
        tr, ev = c == "train", c == "val"
        zaklad = mae_povodne(y[ev], ridge.fit(X[tr], y[tr], CIL, h)(X[ev]))
        for nazev, st in skupiny.items():
            sl = [k for k in X.columns if k.split("_")[0] in st]
            bez = ridge.fit(X[tr], y[tr], CIL, h, sloupce=[k for k in X.columns if k not in sl])
            vyr = mae_povodne(y[ev], bez(X[ev])) - zaklad
            radky.append(dict(horizont=h, skupina=nazev, stanice=" ".join(st), sloupcu=len(sl),
                              zaklad=round(zaklad, 3), vyrazeni=round(vyr, 3)))
            print(f"+{h} h: bez {nazev:16s} ({len(sl)} sloupců) {vyr:+6.2f} cm")
    return pd.DataFrame(radky)


# --- grafy -----------------------------------------------------------------------------------------------------------

def v1_co_jde_do_modelu():
    """Schéma povodí s dobou doběhu (jako G1) a vpravo, co přesně model dostane."""
    S = pd.read_csv(G.PREZ / "data/external/stanice_hydro.csv", dtype={"cislo": str}).set_index("klic")
    barva = {s: b for b, _, st in G.VETVE.values() for s in st}
    fig, _ = G.graf("Co jde do modelu: 98 čísel změřených do okamžiku předpovědi", rect=None)
    ax = fig.add_axes((0.0, 0.02, 0.58, 0.83))
    ax.set_aspect(1 / np.cos(np.radians(50.3)))
    ax.axis("off")
    for a, b in G.SPOJNICE:
        ax.plot([S.lon[a], S.lon[b]], [S.lat[a], S.lat[b]], color=barva[a], lw=3, solid_capstyle="round", zorder=3)
    for k, r in S.iterrows():
        cil = k == "decin"
        ax.scatter(r.lon, r.lat, s=420 if cil else 150, color=barva[k], edgecolor="white", linewidth=2.5, zorder=5)
        if cil:
            ax.scatter(r.lon, r.lat, s=900, facecolor="none", edgecolor=G.INK, linewidth=2, zorder=5)
        dx, dy, ha, *vod = G.STITKY[k]
        if k in CILE:
            text = ("Děčín · cíl" if cil else f"{G.JMENA[k]} · {G.DOBEH[k]}{G.NB}h") + "\nhladina + průtok"
        else:
            text = f"{G.JMENA[k]} · {G.DOBEH[k]}{G.NB}h"
        ax.annotate(text, (r.lon, r.lat), xytext=(dx + (8 if cil else 0), dy), textcoords="offset points", ha=ha,
                    va="center", fontsize=16 if cil else 13.5, weight="bold" if cil else "normal", color=G.INK,
                    zorder=6, linespacing=1.1,
                    arrowprops=dict(arrowstyle="-", color=G.INK2, lw=1, shrinkA=0, shrinkB=7) if vod else None)
    ax.set_xlim(S.lon.min() - 0.55, S.lon.max() + 0.35)  # vlevo místo na popisky Ústí, Louny, Beroun
    ax.set_ylim(S.lat.min() - 0.30, S.lat.max() + 0.06)  # dole místo na legendu pod stanicemi
    znacky = [Line2D([], [], color=b, lw=3, marker="o", ms=9, mec="white", mew=2, label=n) for b, n, _ in G.VETVE.values()]
    ax.legend(handles=znacky, loc="lower left", fontsize=13, handlelength=2, labelspacing=0.35)
    zh = ", ".join(str(z) for z in ZPOZDENI_H[1:])
    zq = ", ".join(str(z) for z in ZPOZDENI_Q[1:])
    x0, y = 0.60, 0.80
    bloky = [
        ("Hladina v Děčíně a Ústí", f"teď a před {zh} h", f"2 × 7 = {2 * len(ZPOZDENI_H)}"),
        ("Průtok na 12 stanicích", f"teď a před {zq} h", f"12 × 7 = {12 * len(ZPOZDENI_Q)}"),
    ]
    for nadpis, kdy, kolik in bloky:
        fig.text(x0, y, nadpis, fontsize=18, weight="semibold", color=G.INK)
        fig.text(0.965, y, kolik, fontsize=18, weight="semibold", color=G.MODRA, ha="right")
        fig.text(x0, y - 0.05, kdy, fontsize=15, color=G.INK2)
        y -= 0.15
    fig.text(x0, y + 0.02, "celkem 98 čísel", fontsize=18, weight="semibold", color=G.INK)
    y -= 0.07
    for t in ("jen co je v okamžiku předpovědi už změřené",
              "průtoky pod odmocninou (měrná křivka)",
              "všechna čísla škálovaná na stejné měřítko"):
        fig.text(x0, y, "•  " + t, fontsize=15, color=G.INK)
        y -= 0.055
    y -= 0.03
    fig.text(x0, y, "Není v něm: srážky, sníh, teplota.", fontsize=15, weight="semibold", color=G.ORANZ)
    fig.text(x0, y - 0.05, "Na 24 h rozhoduje voda, která už teče řekou;", fontsize=15, color=G.INK2)
    fig.text(x0, y - 0.095, "srážky jsme zkoušeli a nepomohly.", fontsize=15, color=G.INK2)
    fig.text(0.04, 0.035, "U stanice doba doběhu vody do Děčína.", fontsize=12, color=G.INK2)
    G.uloz(fig, "V1_co_jde_do_modelu.png")


def heatmapa(D, sloupec, titulek, nazev, popis_barvy, pozn):
    poradi = sorted(STANICE, key=lambda s: -G.DOBEH.get(s, 0))  # nahoře nejdál proti proudu, dole Děčín
    T = D.pivot(index="stanice", columns="horizont", values=sloupec).loc[poradi, list(HORIZONTY)]
    fig, ax = G.graf(titulek, rect=(0.27, 0.10, 0.50, 0.75))
    ax.grid(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_visible(False)
    cmap = LinearSegmentedColormap.from_list("vliv", [G.ORANZ, "#f7f7f7", G.MODRA])
    vmax = np.nanpercentile(T.drop(index=[k for k in T.index if T.loc[k].max() > 40]).abs().to_numpy(), 100)
    vmax = max(vmax, 1.0)
    norm = TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)
    im = ax.imshow(np.clip(T.to_numpy(), -vmax, vmax), cmap=cmap, norm=norm, aspect="auto")
    for i, s in enumerate(T.index):
        for j, h in enumerate(T.columns):
            v = T.loc[s, h] if abs(T.loc[s, h]) >= 0.05 else 0.0  # bez „-0,0“
            silna = abs(v) > 0.6 * vmax
            ax.text(j, i, ("+" if v > 0.05 else "") + G.cislo(v), ha="center", va="center", fontsize=14,
                    color="white" if silna else G.INK, weight="semibold" if abs(v) >= 1 else "normal")
    ax.set_xticks(range(len(T.columns)), [f"za {h}{G.NB}h" for h in T.columns], fontsize=15)
    ax.xaxis.tick_top()
    ax.set_yticks(range(len(T.index)),
                  [f"{G.JMENA[s]} ({G.DOBEH[s]}{G.NB}h)" if s in G.DOBEH else f"{G.JMENA[s]} (cíl)" for s in T.index],
                  fontsize=14)
    ax.tick_params(length=0)
    cb = fig.colorbar(im, ax=ax, fraction=0.05, pad=0.03)
    cb.set_label(popis_barvy, fontsize=13)
    cb.ax.tick_params(labelsize=12)
    fig.text(0.04, 0.02, "Děčín, validace (4 povodně 2006–2011), chyba na povodních jako evaluate.py; "
             "v závorce doba doběhu do Děčína\n" + pozn, fontsize=12, color=G.INK2, va="bottom", linespacing=1.4)
    G.uloz(fig, nazev)
    return T


def v4_vetve(D, Dv):
    """Vlastní hladina Děčína proti celým větvím proti proudu, po horizontech."""
    rady = [  # popisek, barva, hodnoty po horizontech
        ("vlastní hladina a průtok Děčína", G.SEDA, [D.query("stanice == 'decin' and horizont == @h").vyrazeni.item()
                                                  for h in HORIZONTY]),
        ("Vltava (Praha, Beroun, Sázava, Vraňany)", G.MODRA,
         [Dv.query("skupina == 'vltava' and horizont == @h").vyrazeni.item() for h in HORIZONTY]),
        ("horní Labe (Přelouč, Nymburk, Jizera, Kostelec)", G.ORANZ,
         [Dv.query("skupina == 'labe_horni' and horizont == @h").vyrazeni.item() for h in HORIZONTY]),
        ("všech 10 stanic proti proudu", G.INK,
         [Dv.query("skupina == 'vse_proti_proudu' and horizont == @h").vyrazeni.item() for h in HORIZONTY]),
    ]
    fig, ax = G.graf("Čím dál dopředu, tím víc rozhoduje voda proti proudu", rect=(0.09, 0.12, 0.88, 0.62))
    sirka = 0.2
    for i, (popis, barva, hodnoty) in enumerate(rady):
        x = np.arange(len(HORIZONTY)) + (i - 1.5) * sirka
        ax.bar(x, hodnoty, sirka * 0.92, color=barva, label=popis, zorder=3)
        for xi, v in zip(x, hodnoty):
            ax.text(xi, v + (0.4 if v >= 0 else -0.4), ("+" if v > 0.05 else "") + G.cislo(v), ha="center",
                    va="bottom" if v >= 0 else "top", fontsize=13, color=G.INK)
    ax.axhline(0, color=G.INK2, lw=1, zorder=4)
    ax.set_xticks(range(len(HORIZONTY)), [f"předpověď za {h}{G.NB}h" for h in HORIZONTY], fontsize=16)
    ax.tick_params(axis="x", length=0)
    ax.set_ylim(-2, 24)
    G.osa_cisla(ax)
    ax.set_ylabel("o kolik cm vzroste chyba bez nich")
    fig.legend(loc="upper left", bbox_to_anchor=(0.085, 0.87), ncol=2, fontsize=14, columnspacing=1.5,
               handlelength=1.2)
    fig.text(0.04, 0.035, "Děčín, validace (4 povodně 2006–2011), chyba na povodních jako evaluate.py; model vždy "
             "znovu natrénovaný bez daných stanic", fontsize=12, color=G.INK2)
    G.uloz(fig, "V4_dulezitost_vetvi.png")


if __name__ == "__main__":
    VYSLEDKY.mkdir(exist_ok=True)
    G.CIL.mkdir(exist_ok=True)
    if "--jen-grafy" in sys.argv:  # grafy z uložených výsledků, bez přepočtu
        D = pd.read_csv(VYSLEDKY / "vstupy_dulezitost.csv")
    else:
        D = spocitej()
        D.to_csv(VYSLEDKY / "vstupy_dulezitost.csv", index=False)
        (VYSLEDKY / "vstupy_dulezitost.json").write_text(json.dumps(D.to_dict("records"), ensure_ascii=False, indent=1),
                                                        encoding="utf-8")
        spocitej_skupiny().to_csv(VYSLEDKY / "vstupy_dulezitost_vetve.csv", index=False)
    Dv = pd.read_csv(VYSLEDKY / "vstupy_dulezitost_vetve.csv")
    v1_co_jde_do_modelu()
    heatmapa(D, "vyrazeni", "Bez které stanice se model nejvíc zhorší", "V2_dulezitost_stanic.png",
             "o kolik cm vzroste chyba bez stanice", "pod 1 cm nebrat jako přesvědčivé; sousední stanice na stejné řece se mohou zastoupit")
    heatmapa(D, "permutace", "Kontrola zamícháním: na 12 h Mělník, na 36 h Vltava a horní Labe",
             "V3_dulezitost_permutace.png", "o kolik cm vzroste chyba po zamíchání",
             "plný model, sloupce stanice zamíchané ve validaci, průměr z 5 opakování; barva oříznutá, čísla platí")
    v4_vetve(D, Dv)
