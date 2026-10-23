"""Stáhne hodinové stavy a průtoky vybraných stanic (stanice.py) za 2006–2025, po jednom souboru s pauzou.

python stahni_hydro.py    už stažené přeskočí, každý soubor jde do cache/ jen jednou
"""
import stahni
from stanice import HYDRO, ROKY

stahni.PAUZA_S = 1.5
if __name__ == "__main__":
    n = 0
    for dbc in HYDRO:
        for rok in ROKY:
            f = stahni.ziskej(f"hydrology/historical/data/hourly/H_0-203-1-{dbc}_HQ_{rok}.json", povinne=False)
            n += f is not None
        print(dbc, HYDRO[dbc][0], "hotovo", flush=True)
    print(f"{n} souborů")
