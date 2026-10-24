"""Měření zpoždění dat ČHMÚ v provozu: každých 10 minut přečte výpis hydrology/now/data/ (čas poslední změny souboru
= čas zveřejnění) a stáhne jen ty z 30 stanic, které se od minula změnily. Zpoždění = čas zveřejnění − čas poslední
hodnoty v souboru. Ukládá cache/provoz/now/<čas stažení>/ a zaznamy_now.csv. Šetrně: po jednom, pauza 2 s.

python sleduj_now.py <konec HH:MM místního času>
"""
import csv
import json
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ZDE = Path(__file__).resolve().parent
sys.path.insert(0, str(ZDE.parent))
from stanice import HYDRO  # noqa: E402

URL = "https://opendata.chmi.cz/hydrology/now/data/"
CIL = ZDE.parent / "cache/provoz/now"
LOG = ZDE / "zaznamy_now.csv"
HLAVA = {"User-Agent": "studentsky-projekt-hackathon (pomale stahovani)"}
PAUZA = 2.0


def stahni(url):
    time.sleep(PAUZA)
    with urllib.request.urlopen(urllib.request.Request(url, headers=HLAVA), timeout=60) as r:
        return r.read(), r.headers.get("Last-Modified")


def posledni(data):
    out = {}
    for ts in json.loads(data)["objList"][0]["tsList"]:
        if ts["tsConID"] in ("H", "Q") and ts["tsData"]:
            out[ts["tsConID"]] = ts["tsData"][-1]["dt"]
    return out


if __name__ == "__main__":
    konec = datetime.strptime(sys.argv[1], "%H:%M").time()
    znamy = {}
    nova = not LOG.exists()
    with open(LOG, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if nova:
            w.writerow(["stazeno_utc", "dbc", "stanice", "zverejneno_vypis_utc", "last_modified_http", "posledni_H", "posledni_Q"])
        while datetime.now().time() < konec:
            t0 = time.time()
            vypis, _ = stahni(URL)
            casy = dict(re.findall(r'href="0-203-1-(\w+)\.json">[^<]*</a>\s+(\d\d-\w\w\w-\d{4} \d\d:\d\d)', vypis.decode()))
            ted = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M")
            for dbc, (klic, _) in HYDRO.items():
                if dbc not in casy or znamy.get(dbc) == casy[dbc]:
                    continue
                data, lm = stahni(f"{URL}0-203-1-{dbc}.json")
                (CIL / ted).mkdir(parents=True, exist_ok=True)
                (CIL / ted / f"0-203-1-{dbc}.json").write_bytes(data)
                p = posledni(data)
                w.writerow([datetime.now(timezone.utc).isoformat(timespec="seconds"), dbc, klic, casy[dbc], lm,
                            p.get("H"), p.get("Q")])
                znamy[dbc] = casy[dbc]
            f.flush()
            time.sleep(max(0, 600 - (time.time() - t0)))
