"""Graf, který vysvětluje „bude jako teď“: každou hodinu se vydá nová předpověď, že za 24 h bude stejně jako teď.
Nakreslené v čase, pro který platí, dají skutečnou křivku posunutou o den doprava. Boris 9/2024, Děčín, test.

python src/graf_jako_ted.py
"""
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from data import SPA, nacti
from porovnej import ROOT

OD, DO, H = "2024-09-12", "2024-09-21", 24
CERNA, SEDA, MODRA = "#0b0b0b", "#8a8986", "#2a78d6"
skutecnost = nacti().decin_H[OD:DO]
jako_ted = skutecnost.shift(H, freq="h")[OD:DO]  # hladina z času vydání, nakreslená v čase, pro který platí
P = pd.read_parquet(ROOT / "results/predpovedi/ridge_test.parquet")
P = P[(P.cil == "decin") & (P.horizont == H)]
ridge = P.predpoved.set_axis(P.index + pd.Timedelta(hours=H))[OD:DO]

fig, ax = plt.subplots(figsize=(10, 5.5))
for n, prah in enumerate(SPA["decin"], 1):
    ax.axhline(prah, color="#c9c8c4", lw=0.8, ls=":")
    ax.text(pd.Timestamp(OD, tz="UTC"), prah + 6, f"{n}. stupeň", color=SEDA, fontsize=8)
ax.plot(skutecnost.index, skutecnost, color=CERNA, lw=2.2, label="skutečná hladina")
ax.plot(jako_ted.index, jako_ted, color=SEDA, lw=1.8, ls="--", label="„bude jako teď“ na 24 h: hladina z doby vydání")
ax.plot(ridge.index, ridge, color=MODRA, lw=1.8, label="lineární regrese na 24 h (test)")

# tři předpovědi „jako teď“ jako šipky: z času vydání o 24 h doprava se stejnou hladinou, popis vpravo dole
radky = []
for i, t in enumerate(pd.to_datetime(["2024-09-13 12:00", "2024-09-14 06:00", "2024-09-15 00:00"], utc=True), 1):
    h, pak = skutecnost[t], skutecnost[t + pd.Timedelta(hours=H)]
    ax.annotate("", xy=(t + pd.Timedelta(hours=H), h), xytext=(t, h), arrowprops=dict(arrowstyle="->", color=SEDA, lw=1.2))
    ax.plot([t, t + pd.Timedelta(hours=H)], [h, pak], "o", color=CERNA, ms=5, zorder=4)
    ax.text(t, h + 12, str(i), ha="right", fontsize=9, fontweight="bold", color=CERNA)
    radky.append(f"{i}  {t:%d. %m. %H:%M} je {h:.0f} cm, „jako teď“ předpoví na {t + pd.Timedelta(hours=H):%d. %m. %H:%M} "
                 f"taky {h:.0f} cm, skutečně bylo {pak:.0f} cm (chyba {pak - h:.0f} cm)")
ax.text(0.99, 0.04, "\n".join(radky), transform=ax.transAxes, ha="right", va="bottom", fontsize=8, color=CERNA, linespacing=1.6)

ax.set_ylabel("hladina v Děčíně (cm)")
ax.set_ylim(0, skutecnost.max() * 1.15)
ax.xaxis.set_major_locator(mdates.DayLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d. %m."))
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="y", color="#e4e4e1", lw=0.6)
ax.legend(fontsize=8, loc="upper left", frameon=False, bbox_to_anchor=(0, 0.93))
ax.set_title("„Bude jako teď“ je skutečná hladina posunutá o den: každou hodinu nová předpověď, vždy o den pozadu",
             fontsize=10.5, loc="left")
fig.tight_layout()
soubor = ROOT / "docs/grafy/jako_ted_vysvetleni.png"
fig.savefig(soubor, dpi=150)
print(f"uloženo {soubor.relative_to(ROOT)}")
