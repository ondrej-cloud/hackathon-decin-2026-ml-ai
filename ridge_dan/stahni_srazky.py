"""Stáhne denní úhrny srážek vybraných stanic (srazkove_stanice.csv), jeden soubor na stanici za celou historii.

Hodinové srážky (data/1hour/precipitation/) začínají až 2018, na trénink 2006–2018 nestačí. Denní ano.
Navíc stáhne hodinové srážky 05–08/2019 pro Ústí-Kočkov, na nich se ověřuje, kdy denní úhrn končí.
"""
import pandas as pd

import stahni

stahni.PAUZA_S = 1.5
if __name__ == "__main__":
    S = pd.read_csv("srazkove_stanice.csv")
    for wsi in S.wsi:
        stahni.ziskej(f"meteorology/climate/historical_csv/data/daily/precipitation/dly-{wsi}-SRA.csv")
    for m in range(5, 9):
        stahni.ziskej(f"meteorology/climate/historical_csv/data/1hour/precipitation/2019/1h-0-20000-0-11502-SRA1H-2019{m:02d}.csv")
    print(len(S), "stanic")
