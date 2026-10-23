"""Šetrné stahování NOAA NCEI Global Hourly (Integrated Surface Database, ISD) s cache na disku.

python stahni_isd.py seznam                   isd-history.csv (seznam stanic)
python stahni_isd.py data <USAF> ...          roky 2006–2025 vybraných stanic (WBAN 99999)

Zdroj: seznam https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv. Data po stanicích a letech
https://www.ncei.noaa.gov/data/global-hourly/access/<rok>/<stanice>.csv dnes NCEI přesměrovává (301) na svou kopii
v NOAA Open Data Dissemination na AWS, jen ztratí cestu; stahuje se proto přímo odtamtud,
https://noaa-global-hourly-pds.s3.amazonaws.com/<rok>/<stanice>.csv (stejné soubory).
Podmínky: data NOAA/NCEI jsou volně dostupná bez omezení použití (dílo vlády USA); ISD obsahuje data výměny WMO,
pro která platí WMO Resolution 40 (volné nekomerční použití, zdroj se uvádí: NOAA NCEI, Integrated Surface Database).
Každý soubor se stáhne nejvýš jednou do srazky_dan/cache/ (není v Gitu), nejvýš 3 souběžně, každé vlákno s pauzou
1,5 s mezi požadavky; každé stažení je zapsané v STAZENO.csv.
"""
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ZDE = Path(__file__).resolve().parent
CACHE = ZDE / "cache"
LOG = ZDE / "STAZENO.csv"
NCEI = "https://www.ncei.noaa.gov/"
AWS = "https://noaa-global-hourly-pds.s3.amazonaws.com/"
PAUZA_S = 1.5
SOUBEZNE = 3
ROKY = range(2006, 2026)
_zamek = threading.Lock()
_posledni = threading.local()


def ziskej(url, soubor):
    """Vrátí lokální soubor, nebo None, když na serveru není (404). Stažené se už nikdy nestahuje znovu."""
    if soubor.exists():
        return soubor
    if soubor.with_suffix(soubor.suffix + ".404").exists():
        return None
    soubor.parent.mkdir(parents=True, exist_ok=True)
    cekat = PAUZA_S - (time.time() - getattr(_posledni, "t", 0.0))
    if cekat > 0:
        time.sleep(cekat)
    req = urllib.request.Request(url, headers={"User-Agent": "studentsky-projekt-hackathon (pomale stahovani)"})
    try:
        data = urllib.request.urlopen(req, timeout=180).read()
    except urllib.error.HTTPError as e:
        _posledni.t = time.time()
        if e.code in (403, 404):  # S3 vrací na neexistující klíč 403 nebo 404
            soubor.with_suffix(soubor.suffix + ".404").touch()
            return None
        raise
    _posledni.t = time.time()
    if data[:15].lstrip().lower().startswith(b"<!doctype html"):
        raise RuntimeError(f"místo dat přišla HTML stránka: {url}")
    soubor.with_suffix(".part").write_bytes(data)
    soubor.with_suffix(".part").replace(soubor)
    with _zamek:
        novy = not LOG.exists()
        with open(LOG, "a", encoding="utf-8") as f:
            if novy:
                f.write("cas_utc,adresa,bajtu\n")
            f.write(f"{datetime.now(timezone.utc):%Y-%m-%dT%H:%M:%S},{url},{len(data)}\n")
    return soubor


def soubor_stanice(usaf, rok):
    nazev = f"{usaf}99999.csv"
    return ziskej(f"{AWS}{rok}/{nazev}", CACHE / "global-hourly" / str(rok) / nazev)


def seznam():
    return ziskej(NCEI + "pub/data/noaa/isd-history.csv", CACHE / "pub/data/noaa/isd-history.csv")


def stanice(usaf):
    chybi = [r for r in ROKY if soubor_stanice(usaf, r) is None]
    print(usaf, "chybí roky:", chybi or "žádné", flush=True)
    return usaf, chybi


if __name__ == "__main__":
    if sys.argv[1] == "seznam":
        print(seznam())
    else:
        with ThreadPoolExecutor(SOUBEZNE) as ex:
            list(ex.map(stanice, sys.argv[2:]))
