"""Stáhne z otevřených dat ČHMÚ denní klimatická data stanic v povodí Labe nad Děčínem.

Zdroj: https://opendata.chmi.cz/meteorology/climate/historical/data/daily/
Jeden soubor na stanici se všemi veličinami od začátku měření (40–90 MB), do data/raw/chmu_meteo/ (není v Gitu).
Potřebuje to jen ten, kdo přestavuje data/external/labe_meteo.parquet (src/meteo.py).
"""
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

URL = "https://opendata.chmi.cz/meteorology/climate/historical/data/daily/"
OUT = Path(__file__).resolve().parents[1] / "data/raw/chmu_meteo"
# stanice podle toho, do které ze tří větví voda z jejich okolí teče (hory i nížiny)
STANICE = {
    "vltava": {
        "0-20000-0-11457": "Churáňov", "0-20000-0-11546": "České Budějovice", "0-20000-0-11538": "Temelín",
        "0-20000-0-11487": "Kocelovice", "0-20000-0-11450": "Plzeň, Mikulka", "0-20000-0-11423": "Přimda",
        "0-20000-0-11518": "Praha, Ruzyně", "0-20000-0-11628": "Košetice", "0-20000-0-11659": "Přibyslav",
        "0-203-0-11582": "Tábor",
    },
    "labe": {
        "0-20000-0-11643": "Pec pod Sněžkou", "0-203-0-11640": "Labská bouda", "0-20000-0-11609": "Jičín",
        "0-203-0-11559": "Kořenov, Jizerka", "0-20000-0-11669": "Polom", "0-20000-0-11683": "Svratouch",
        "0-20000-0-11652": "Pardubice", "0-203-0-11649": "Hradec Králové", "0-20000-0-11679": "Ústí nad Orlicí",
    },
    "ohre": {
        "0-20000-0-11406": "Cheb", "0-20000-0-11414": "Karlovy Vary", "0-203-0-11420": "Klínovec",
        "0-20000-0-11438": "Tušimice", "0-20000-0-11509": "Doksany", "0-203-0-11468": "Žatec",
    },
}


def download(wsi):
    path = OUT / f"dly-{wsi}.json"
    if not path.exists():
        urllib.request.urlretrieve(f"{URL}dly-{wsi}.json", path.with_suffix(".part"))
        path.with_suffix(".part").rename(path)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    vse = [w for v in STANICE.values() for w in v]
    # server omezuje rychlost každého spojení zvlášť, proto všechny soubory najednou
    with ThreadPoolExecutor(len(vse)) as pool:
        list(pool.map(download, vse))
    print(f"{len(vse)} stanic v {OUT}")
