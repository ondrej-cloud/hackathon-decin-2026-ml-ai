"""Kontrola, že srážkové příznaky nevidí do budoucnosti.

python kontrola_casovani.py [USAF]     (výchozí Ústí nad Labem 115020)

Na skutečných zprávách stanice se 300× náhodně změní (nebo smaže) jedna termínová zpráva v čase E a postaví se
hodinové příznaky znovu. Žádný příznak v hodině t < E + 1 h se nesmí změnit (ani NaN na číslo a naopak).
Hodina zpoždění je tu napsaná pevně, ne převzatá ze srazky.py. Navíc pevné případy t = E, E + 1 h, E + 6 h,
E + 7 h a 24h součty proti přímému výpočtu z 12h úhrnů v termínech 06/18 (rozdíl smí být jen tam, kde je
předchozí 6h úhrn větší než 12h, a přesně o ten rozpor).
"""
import sys

import numpy as np
import pandas as pd

import srazky as R


HODINA = pd.Timedelta(hours=1)


def stejne(a, b):
    return np.array_equal(np.isnan(a), np.isnan(b)) and np.allclose(np.nan_to_num(a), np.nan_to_num(b))


if __name__ == "__main__":
    usaf = sys.argv[1] if len(sys.argv) > 1 else "115020"
    z = R.nacti_zpravy(usaf)
    z = z[(z.index >= "2009-01-01") & (z.index < "2011-01-01")]
    zaklad = R.priznaky_stanice(z)
    rng = np.random.default_rng(42)
    terminy = pd.date_range("2009-01-10", "2010-12-20", freq="6h", tz="UTC")
    unik, bez_ucinku = 0, 0
    for E in rng.choice(terminy, 300, replace=False):
        E = pd.Timestamp(E)
        z2 = z.copy()
        if rng.random() < 0.3:
            z2 = z2.drop(index=E, errors="ignore")  # zpráva chybí
        else:
            z2.loc[E, ["u6", "u12"]] = rng.uniform(5, 40, 2)
        z2 = z2.sort_index()
        nove = R.priznaky_stanice(z2)
        pred = zaklad.index < E + HODINA
        if not stejne(zaklad[pred].to_numpy(), nove[pred].to_numpy()):
            unik += 1
            print("ZMĚNA PŘED E + 1 h:", E)
        po = (zaklad.index >= E + HODINA) & (zaklad.index < E + pd.Timedelta(hours=79))
        if stejne(zaklad[po].to_numpy(), nove[po].to_numpy()):
            bez_ucinku += 1
    print(f"{usaf}: 300 změn, změna před E + 1 h: {unik}, bez účinku po E + 1 h: {bez_ucinku} "
          "(beze účinku je v pořádku jen u zpráv, které termínový rozpis nepoužije, např. 6h úhrn v 06/18 "
          "při známém 12h a smazání chybějící zprávy)")
    # přímý výpočet: v hodině 07–12 UTC platí termín 06, součet za 24 h = 12h úhrn v 06 + 12h úhrn v 18 předchozího dne
    s = z.u12
    t = pd.date_range("2009-02-01 07:00", "2010-12-01 07:00", freq="D", tz="UTC")
    primo = s.reindex(t - pd.Timedelta(hours=1)).to_numpy() + s.reindex(t - pd.Timedelta(hours=13)).to_numpy()
    moje = zaklad.loc[t, 24].to_numpy()
    ok = ~np.isnan(primo)
    # rozpor: 6h úhrn v 00 (12) větší než 12h úhrn v 06 (18); druhý díl je pak 0 a součet větší přesně o rozpor
    rozpor = sum(np.clip(z.u6.reindex(t - pd.Timedelta(hours=h + 6)).to_numpy()
                         - s.reindex(t - pd.Timedelta(hours=h)).to_numpy(), 0, None) for h in (1, 13))
    rozdil = moje[ok] - primo[ok]
    ocekavany = np.nan_to_num(rozpor[ok])
    print(f"24h součet v 07 UTC proti přímému výpočtu z 12h úhrnů: {ok.sum()} dní, největší rozdíl "
          f"{np.nanmax(np.abs(rozdil)):.3f} mm, po odečtení rozporů {np.nanmax(np.abs(rozdil - ocekavany)):.3f} mm, "
          f"NaN u mě {np.isnan(moje[ok]).sum()}")
    assert unik == 0
    assert np.isnan(moje[ok]).sum() == 0 and np.abs(rozdil - ocekavany).max() < 0.01
    # pevné případy: 6h úhrn 50 mm v termínu E = 2010-06-01 00:00, 12h v 06 navíc o 50 mm
    E = pd.Timestamp("2010-06-01 00:00", tz="UTC")
    z2 = z.copy()
    z2.loc[E, "u6"] = z.loc[E, "u6"] + 50 if E in z.index else 50.0
    z2.loc[E + pd.Timedelta(hours=6), "u12"] += 50
    z2 = z2.sort_index()
    nove = R.priznaky_stanice(z2)
    d = (nove - zaklad).round(6)
    assert (d.loc[E] == 0).all() and (d.loc[E - HODINA] == 0).all()           # v E ještě nic
    assert (d.loc[E + HODINA] == 50).all()                                     # od E + 1 h všechna okna
    assert (d.loc[E + 6 * HODINA] == 50).all()                                 # E + 6 h: pořád termín E
    assert d.loc[E + 7 * HODINA, 6] == 0 and (d.loc[E + 7 * HODINA, [12, 24, 48, 72]] == 50).all()
    assert (d.loc[E + 72 * HODINA, 72] == 50) and (d.loc[E + 73 * HODINA, 72] == 0)  # 72h okno termínu E + 66 platí do E + 72 h
    print("pevné případy t = E, E + 1 h, E + 6 h, E + 7 h, E + 72 h, E + 73 h: v pořádku")
