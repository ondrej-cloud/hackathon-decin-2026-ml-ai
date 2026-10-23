"""Kontrola, že srážkové příznaky nevidí do budoucnosti.

python kontrola_casovani.py [USAF]     (výchozí Ústí nad Labem 115020)

Na skutečných zprávách stanice se 300× náhodně změní (nebo smaže) jedna termínová zpráva v čase E a postaví se
hodinové příznaky znovu. Žádný příznak v hodině t < E + 1 h se nesmí změnit (ani NaN na číslo a naopak).
Navíc se ověří, že se změna od E + 1 h opravdu projeví (příznak zprávu používá) a že součty sedí s přímým
výpočtem z 12h úhrnů v termínech 06/18.
"""
import sys

import numpy as np
import pandas as pd

import srazky as R


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
        pred = zaklad.index < E + R.ZPOZDENI
        if not stejne(zaklad[pred].to_numpy(), nove[pred].to_numpy()):
            unik += 1
            print("ZMĚNA PŘED E + 1 h:", E)
        po = (zaklad.index >= E + R.ZPOZDENI) & (zaklad.index < E + pd.Timedelta(hours=79))
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
    print(f"24h součet v 07 UTC proti přímému výpočtu z 12h úhrnů: {ok.sum()} dní, "
          f"největší rozdíl {np.nanmax(np.abs(moje[ok] - primo[ok])):.3f} mm, NaN u mě {np.isnan(moje[ok]).sum()}")
    assert unik == 0
