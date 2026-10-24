"""Markdown tabulka zpoždění a úplnosti po stanicích pro PROVOZ.md a vložení na místo značky <!-- ZPOZDENI -->.

python tabulka_zpozdeni.py    (po zpozdeni.py a výpočtu úplnosti uplnost_stanice.csv)
"""
import sys
from pathlib import Path

import pandas as pd

ZDE = Path(__file__).resolve().parent
sys.path.insert(0, str(ZDE.parent))
from stanice import HYDRO  # noqa: E402

if __name__ == "__main__":
    Z = pd.read_csv(ZDE / "zpozdeni_stanice.csv", index_col=0)
    U = pd.read_csv(ZDE / "uplnost_stanice.csv", index_col=0)
    d = pd.read_csv(ZDE / "zaznamy_now.csv")
    t = pd.to_datetime(d.last_modified_http, format="%a, %d %b %Y %H:%M:%S GMT", utc=True)
    nazvy = {k: n for k, n in HYDRO.values()}
    radky = ["| Stanice | vzorků | zpoždění H medián / max (min) | zpoždění Q medián / max (min) | úplnost H / Q 30 dní (%) |",
             "|---|---|---|---|---|"]
    for k in [k for k, _ in HYDRO.values()]:
        z, u = Z.loc[k], U.loc[k]
        q = "chybí" if pd.isna(z.Q_median_min) else f"{z.Q_median_min:.0f} / {z.Q_max_min:.0f}" if "Q_max_min" in z else f"{z.Q_median_min:.0f}"
        radky.append(f"| {nazvy[k]} | {int(z.vzorku)} | {z.H_median_min:.0f} / {z.H_max_min:.0f} | {q} | "
                     f"{u.H_uplnost_pct:.1f} / {u.Q_uplnost_pct:.1f} |".replace(".", ","))
    uvod = (f"Měřeno {t.min():%d. %m. %H:%M}–{t.max():%H:%M} UTC ({t.dt.floor('20min').nunique()} dávek zveřejnění), "
            "zpoždění = čas zveřejnění souboru (HTTP Last-Modified) − čas poslední hodnoty v něm; úplnost = podíl hodin "
            "25. 9.–23. 10., kdy existuje hodnota v celou hodinu.\n\n")
    tab = uvod + "\n".join(radky) + "\n"
    p = ZDE.parent / "PROVOZ.md"
    s = p.read_text(encoding="utf-8")
    if "<!-- ZPOZDENI -->" in s:
        p.write_text(s.replace("<!-- ZPOZDENI -->", tab.rstrip("\n")), encoding="utf-8")
    print(tab)
