"""Stáhne z otevřených dat ČHMÚ hodinové vodní stavy a průtoky pro Labe nad Děčínem, přítoky a malé řeky v kraji.

Zdroj: https://opendata.chmi.cz/hydrology/historical/data/hourly/
Soubory jdou do data/raw/chmu_hydro/ (asi 280 MB, není v Gitu). Už stažené soubory přeskočí.
Potřebuje to jen ten, kdo přestavuje data/external/labe_hodinove.parquet (src/data.py).
"""
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

URL = "https://opendata.chmi.cz/hydrology/historical/data/hourly/"
OUT = Path(__file__).resolve().parents[1] / "data/raw/chmu_hydro"
STATIONS = {
    # Vltava a její přítoky
    "167200": "Nespeky (Sázava)",
    "198000": "Beroun (Berounka)",
    "169000": "Zbraslav (Vltava)",
    "200100": "Praha-Chuchle (Vltava)",
    "203000": "Vraňany (Vltava)",
    # horní Labe a Jizera
    "061000": "Přelouč (Labe)",
    "080000": "Nymburk (Labe)",
    "101800": "Předměřice (Jizera)",
    "104400": "Kostelec nad Labem (Labe)",
    # Ohře
    "214000": "Karlovy Vary (Ohře)",
    "216000": "Žatec (Ohře)",
    "219000": "Louny (Ohře)",
    "215100": "Kadaň (Ohře)",
    # malé řeky v kraji
    "241000": "Srbská Kamenice (Kamenice)",
    "244000": "Hřensko (Kamenice)",
    "222900": "Bílina (Bílina)",
    "226000": "Trmice (Bílina)",
    "320800": "Rumburk (Mandava)",
    "321000": "Varnsdorf (Mandava)",
    "218000": "Třetí Mlýn (Chomutovka)",
    "218700": "Postoloprty (Chomutovka)",
    "239000": "Benešov nad Ploučnicí (Ploučnice)",
    # Labe v kraji
    "204000": "Mělník (Labe)",
    "220000": "Litoměřice (Labe)",
    "221000": "Ústí nad Labem (Labe)",
    "240000": "Děčín (Labe)",
}

OUT.mkdir(parents=True, exist_ok=True)
index = urllib.request.urlopen(URL, timeout=60).read().decode()
names = sorted(set(re.findall(r"H_0-203-1-(?:%s)_HQ_\d{4}\.json" % "|".join(STATIONS), index)))


def download(name):
    path = OUT / name
    if not path.exists():
        # přes dočasný soubor, ať po přerušeném stahování nezůstane useknutý soubor
        urllib.request.urlretrieve(URL + name, path.with_suffix(".part"))
        path.with_suffix(".part").rename(path)


with ThreadPoolExecutor(8) as pool:
    list(pool.map(download, names))
print(f"{len(names)} souborů v {OUT}")
