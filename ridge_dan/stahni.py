"""Šetrné stahování otevřených dat ČHMÚ (CC BY 4.0) s cache na disku.

Každý soubor se stáhne nejvýš jednou do ridge_dan/cache/ (není v Gitu), mezi požadavky je pauza,
stahuje se po jednom. Každé stažení se zapíše do ridge_dan/STAZENO.csv (čas, adresa, velikost).
"""
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ZDE = Path(__file__).resolve().parent
CACHE = ZDE / "cache"
LOG = ZDE / "STAZENO.csv"
ZAKLAD = "https://opendata.chmi.cz/"
PAUZA_S = 1.0
_posledni = [0.0]


def ziskej(cesta, povinne=True):
    """cesta relativně k opendata.chmi.cz. Vrátí lokální soubor, nebo None, když na serveru není (404)."""
    soubor = CACHE / cesta / "_index.html" if cesta.endswith("/") else CACHE / cesta
    if soubor.exists():
        return soubor
    if soubor.with_suffix(soubor.suffix + ".404").exists():
        return None
    soubor.parent.mkdir(parents=True, exist_ok=True)
    cekat = PAUZA_S - (time.time() - _posledni[0])
    if cekat > 0:
        time.sleep(cekat)
    req = urllib.request.Request(ZAKLAD + cesta, headers={"User-Agent": "studentsky-projekt-hackathon (pomale stahovani)"})
    try:
        data = urllib.request.urlopen(req, timeout=60).read()
    except urllib.error.HTTPError as e:
        _posledni[0] = time.time()
        if e.code == 404 and not povinne:
            soubor.with_suffix(soubor.suffix + ".404").touch()
            return None
        raise
    _posledni[0] = time.time()
    soubor.with_suffix(".part").write_bytes(data)
    soubor.with_suffix(".part").replace(soubor)
    novy = not LOG.exists()
    with open(LOG, "a", encoding="utf-8") as f:
        if novy:
            f.write("cas_utc,adresa,bajtu\n")
        f.write(f"{datetime.now(timezone.utc):%Y-%m-%dT%H:%M:%S},{ZAKLAD + cesta},{len(data)}\n")
    return soubor
