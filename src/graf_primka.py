"""Kde je v lineární regresi přímka: vlevo učení (každá hodina 2006–2018 je bod, přímka se proloží jednou), vpravo
stejná přímka použitá hodinu po hodině za Borise, body v čase dají křivku. Zjednodušeně s jedním vstupem
(průtok v Mělníku teď), skutečný model má 98 vstupů a odmocninu průtoků.

python src/graf_primka.py    uloží docs/grafy/prezentace/Z11_primka_a_krivka.png (záložní slajd)
"""
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter, MultipleLocator

from data import nacti
from grafy_slajdy import INK, MODRA, ORANZ, ROOT, SEDA, cislo, osa_cisla

plt.rcParams.update({"font.size": 15, "axes.labelsize": 15, "xtick.labelsize": 14, "ytick.labelsize": 14})

D = nacti()
x = D.melnik_Q
y = D.decin_H.shift(-24)  # hladina v Děčíně o 24 h později
uceni = pd.concat([x, y], axis=1, keys=["x", "y"])[:"2018"].dropna()
b, a = np.polyfit(uceni.x, uceni.y, 1)
print(f"přímka z {len(uceni)} hodin: hladina za 24 h = {a:.0f} + {b:.3f} × průtok v Mělníku teď")

body = pd.to_datetime(["2024-09-13 09:00", "2024-09-13 21:00", "2024-09-14 09:00", "2024-09-14 21:00"], utc=True)
cesky = lambda t: t.tz_convert("Europe/Prague").tz_localize(None)

fig = plt.figure(figsize=(12, 6.75))
fig.text(0.04, 0.95, "Přímka je mezi vstupem a výsledkem, ne v čase", fontsize=24, weight="semibold", color=INK, va="top")
levy, pravy = fig.add_axes((0.09, 0.13, 0.37, 0.64)), fig.add_axes((0.6, 0.13, 0.37, 0.64))

vzorek = uceni.sample(6000, random_state=42)
levy.scatter(vzorek.x, vzorek.y, s=6, color=SEDA, alpha=0.25, lw=0)
xs = np.array([0, 1500])
levy.plot(xs, a + b * xs, color=MODRA, lw=3)
for t in body:
    levy.plot(x[t], a + b * x[t], "o", ms=11, color=ORANZ, mec="white", mew=1.5, zorder=3)
    levy.annotate(f"{cesky(t).day}. {cesky(t).month}. {cesky(t):%H:%M}", (x[t], a + b * x[t]), xytext=(8, -18),
                  textcoords="offset points", fontsize=12, color=INK)
levy.set_title("1. učení: každá hodina 2006–2018 je bod,\npřímka se proloží jednou", fontsize=14, loc="left", color=INK)
levy.set_xlabel("průtok v Mělníku teď (m³/s)")
levy.set_ylabel("hladina v Děčíně za 24 h (cm)")
levy.set_xlim(0, 1500)
levy.set_ylim(0, 1100)
levy.xaxis.set_major_locator(MultipleLocator(500))
osa_cisla(levy)

okno = slice("2024-09-11", "2024-09-17")
pred = (a + b * x[okno]).shift(24, freq="h")[:D.decin_H[okno].index[-1]]
pravy.plot(cesky(D.decin_H[okno].index), D.decin_H[okno], color="black", lw=2.5, label="skutečnost")
pravy.plot(cesky(pred.index), pred, color=MODRA, lw=2.5, label="předpověď z přímky, 24 h předem")
for t in body:
    pravy.plot(cesky(t + pd.Timedelta(hours=24)), a + b * x[t], "o", ms=11, color=ORANZ, mec="white", mew=1.5, zorder=3)
pravy.set_title("2. předpověď: stejná přímka každou hodinu\ns novým průtokem, body v čase dají křivku", fontsize=14,
                loc="left", color=INK)
pravy.xaxis.set_major_locator(mdates.DayLocator(interval=2))
pravy.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{mdates.num2date(v).day}. 9."))
pravy.set_ylabel("hladina v Děčíně (cm)")
pravy.set_ylim(0, 1100)
osa_cisla(pravy)
pravy.legend(loc="upper left", frameon=False, fontsize=12)

cil = ROOT / "docs/grafy/prezentace/Z11_primka_a_krivka.png"
fig.savefig(cil, dpi=150)
print(f"uloženo {cil.relative_to(ROOT)}")
for t in body:
    print(f"{cesky(t).day}. {cesky(t).month}. {cesky(t):%H:%M}: Mělník {cislo(x[t], 0)} m³/s → {cislo(a + b * x[t], 0)} cm")
