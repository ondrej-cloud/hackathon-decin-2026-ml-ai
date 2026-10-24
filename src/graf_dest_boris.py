"""Graf povodně Boris 9/2024: denní srážky po větvích, průtoky proti proudu a hladina v Děčíně pod sebou.

Ukazuje, proč srážky modelu na 12–36 h nepomáhají: když se v Děčíně blíží vrchol, už neprší a voda teče v řekách.
python src/graf_dest_boris.py
"""
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from data import SPA, nacti
from meteo import STANICE, denni
from porovnej import ROOT

OD, DO = "2024-09-10", "2024-09-21"
BARVY = {"vltava": "#2a78d6", "labe": "#eb6834", "ohre": "#1baf7a"}
NAZVY = {"vltava": "Vltava", "labe": "horní Labe", "ohre": "Ohře"}
SEDA, TEXT = "#52514e", "#0b0b0b"

D = nacti()[OD:DO]
konec_deste = pd.Timestamp("2024-09-17 06:00", tz="UTC")  # srážkový den 16. 9. končí 17. 9. v 6:00 UTC
vrchol = D.decin_H.idxmax()
fig, (a1, a2, a3) = plt.subplots(3, 1, figsize=(10, 8), sharex=True, gridspec_kw=dict(height_ratios=[1, 1.2, 1.2]))

for i, (vetev, stanice) in enumerate(STANICE.items()):
    sra = pd.concat({w: denni(w)["SRA"] for w in stanice}, axis=1).mean(axis=1)[OD:DO]
    # denní úhrn platí od D 06:00 do D+1 06:00, sloupec kreslíme doprostřed
    x = sra.index + pd.Timedelta(hours=18) + pd.Timedelta(hours=7 * (i - 1))
    a1.bar(x, sra, width=pd.Timedelta(hours=6.5), color=BARVY[vetev], label=NAZVY[vetev], zorder=2)
a1.set_ylabel("srážky (mm za den)\nprůměr stanic")
a1.legend(fontsize=8, loc="upper right", frameon=False)

for c, nazev, barva in (("praha_Q", "Praha (Vltava)", BARVY["vltava"]), ("prelouc_Q", "Přelouč (horní Labe)", BARVY["labe"]),
                        ("louny_Q", "Louny (Ohře)", BARVY["ohre"]), ("melnik_Q", "Mělník (pod soutokem)", SEDA)):
    a2.plot(D.index, D[c], color=barva, lw=1.8, label=nazev)
    a2.annotate(f"{nazev}, max {D[c].max():.0f}", (D[c].idxmax(), D[c].max()), xytext=(0, 4),
                textcoords="offset points", ha="center", fontsize=8, color=TEXT)
a2.set_ylabel("průtok (m³/s)")
a2.set_ylim(0, D.melnik_Q.max() * 1.15)

a3.plot(D.index, D.decin_H, color=TEXT, lw=2)
for n, prah in enumerate(SPA["decin"], 1):
    a3.axhline(prah, color=SEDA, lw=0.8, ls=":")
    a3.text(pd.Timestamp(OD, tz="UTC"), prah + 6, f"{n}. stupeň", color=SEDA, fontsize=8)
a3.annotate(f"vrchol {D.decin_H.max():.0f} cm\n{vrchol:%d. %m. %H:%M} UTC", (vrchol, D.decin_H.max()), xytext=(-40, 18),
            textcoords="offset points", ha="right", fontsize=8, color=TEXT, arrowprops=dict(arrowstyle="-", color=SEDA, lw=0.8))
a3.set_ylabel("hladina v Děčíně (cm)")
a3.set_ylim(0, D.decin_H.max() * 1.18)

for a in (a1, a2, a3):
    a.axvspan(konec_deste, vrchol, color="#eeeeec", zorder=0)
    a.grid(axis="y", color="#e4e4e1", lw=0.6, zorder=0)
    a.spines[["top", "right"]].set_visible(False)
a1.text(konec_deste + (vrchol - konec_deste) / 2, a1.get_ylim()[1] * 0.85, "už neprší", ha="center", fontsize=9, color=TEXT)
a3.text(konec_deste + (vrchol - konec_deste) / 2, 60, f"{(vrchol - konec_deste) / pd.Timedelta(hours=1):.0f} h bez deště,\nvoda v Děčíně pořád stoupá",
        ha="center", fontsize=9, color=TEXT)
a3.xaxis.set_major_locator(mdates.DayLocator())
a3.xaxis.set_major_formatter(mdates.DateFormatter("%d. %m."))
a1.set_title("Povodeň Boris 9/2024: déšť, průtoky proti proudu a hladina v Děčíně", fontsize=11, loc="left")
fig.tight_layout()
soubor = ROOT / "docs/grafy/boris_dest_prutoky_decin.png"
fig.savefig(soubor, dpi=150)
print(f"uloženo {soubor.relative_to(ROOT)}")
t = vrchol - pd.Timedelta(hours=24)
print(f"předpověď na vrchol vydaná 24 h předem: {t}, déšť skončil {konec_deste}")
for c in ("prelouc_Q", "praha_Q", "melnik_Q", "decin_H"):
    print(c, "10. 9.:", round(float(D[c][:"2024-09-10"].mean())), "14. 9. 12:00:", D[c]["2024-09-14 12:00"])
