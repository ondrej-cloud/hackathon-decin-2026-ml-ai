"""Budovy v Děčíně a Ústí z OpenStreetMap pro 3D mapu (mapbox_mapa.py), aby byly vidět i z dálky.

Mapbox Standard kreslí 3D budovy až od zoomu 15 a dlaždice Mapbox Streets v8 mají pod ním jen pár velkých budov
(v pohledu na Děčín 3 na zoomu 13 a 30 na zoomu 14). Obrysy budov ve čtverci kolem vodočtu proto stáhneme jednou
z OpenStreetMap (Overpass API, data/raw/osm/budovy_overpass.json, není v Gitu) a uložíme kompaktně do
data/external/budovy_<cil>.json. Výška: tag height, jinak building:levels × 3 m, jinak 3 m u garáží a kůlen
a 9 m u ostatních. `python app/budovy.py --priprav` (asi minuta), `python app/budovy.py` vypíše přehled.

Formát: {"lon0", "lat0", "b": [[výška, základna, x0, y0, dx1, dy1, ...], ...]}; souřadnice v 1e-5 stupně od
(lon0, lat0), další body jako rozdíl od předchozího. Jen vnější obrys, dvory uvnitř budov jsou vyplněné.
"""
import json
import math
import sys
from functools import cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/osm/budovy_overpass.json"
OKNA = {"decin": (14.150, 50.745, 14.270, 50.820), "usti": (13.975, 50.612, 14.110, 50.697)}  # z, j, v, s
KROK = 1e-5
MALE = {"garage", "garages", "shed", "carport", "roof", "hut", "kiosk", "container"}
MIN_PLOCHA = 15  # m², menší přístřešky vynecháme


def soubor(cil):
    return ROOT / f"data/external/budovy_{cil}.json"


def _cislo(text):
    try:
        return float(str(text).replace(",", ".").split()[0].rstrip("m"))
    except (ValueError, IndexError):
        return None


def _vyska(tagy):
    v = _cislo(tagy.get("height"))
    if v is None and _cislo(tagy.get("building:levels")) is not None:
        v = 3 * _cislo(tagy["building:levels"]) + (2 if tagy.get("roof:shape") not in (None, "flat") else 0)
    if v is None:
        v = 3 if tagy.get("building") in MALE else 9
    zakladna = _cislo(tagy.get("min_height"))
    if zakladna is None and _cislo(tagy.get("building:min_level")) is not None:
        zakladna = 3 * _cislo(tagy["building:min_level"])
    return max(1, round(min(v, 300))), round(zakladna or 0)


def _plocha_m2(kruh):
    lat = math.radians(kruh[0][1])
    xy = [(lon * 111320 * math.cos(lat), la * 110540) for lon, la in kruh]
    return abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(xy, xy[1:] + xy[:1]))) / 2


def _stahni():
    import requests
    okna = "".join(f'way["building"]({s0},{z0},{s1},{z1});relation["building"]({s0},{z0},{s1},{z1});'
                   for z0, s0, z1, s1 in OKNA.values())
    dotaz = f"[out:json][timeout:300];({okna});out geom;"
    odpoved = requests.post("https://overpass-api.de/api/interpreter", data={"data": dotaz}, timeout=600,
                            headers={"User-Agent": "hackathon-decin-2026"})
    odpoved.raise_for_status()
    RAW.parent.mkdir(parents=True, exist_ok=True)
    RAW.write_text(odpoved.text, encoding="utf-8")


def _obrysy(prvek):
    """Vnější obrysy [(lon, lat), ...] cesty nebo relace (u relace uzavřené vnější členy)."""
    if prvek["type"] == "way":
        cesty = [prvek.get("geometry", [])]
    else:
        cesty = [m.get("geometry", []) for m in prvek.get("members", []) if m.get("role") == "outer"]
    for g in cesty:
        kruh = [(b["lon"], b["lat"]) for b in g]
        if len(kruh) >= 4 and kruh[0] == kruh[-1]:
            yield kruh[:-1]


def priprav():
    if not RAW.exists():
        _stahni()
    prvky = json.loads(RAW.read_text(encoding="utf-8"))["elements"]
    for cil, (z0, s0, z1, s1) in OKNA.items():
        budovy = []
        for p in prvky:
            tagy = p.get("tags", {})
            if tagy.get("location") == "underground" or tagy.get("building") in ("no", "construction"):
                continue
            vyska, zakladna = _vyska(tagy)
            for kruh in _obrysy(p):
                lon, lat = sum(b[0] for b in kruh) / len(kruh), sum(b[1] for b in kruh) / len(kruh)
                if not (z0 <= lon <= z1 and s0 <= lat <= s1) or _plocha_m2(kruh) < MIN_PLOCHA:
                    continue
                body = []
                for b in kruh:
                    bod = (round((b[0] - z0) / KROK), round((b[1] - s0) / KROK))
                    if not body or bod != body[-1]:
                        body.append(bod)
                if len(body) < 3:
                    continue
                radek = [vyska, zakladna, *body[0]]
                for (x1, y1), (x2, y2) in zip(body, body[1:]):
                    radek += [x2 - x1, y2 - y1]
                budovy.append(radek)
        soubor(cil).write_text(json.dumps({"lon0": z0, "lat0": s0, "b": budovy}, separators=(",", ":")),
                               encoding="utf-8")
        print(f"{cil}: {len(budovy)} budov, {soubor(cil).stat().st_size / 1e6:.2f} MB")


@cache
def nacti(cil):
    """Kompaktní budovy pro mapu, nebo None, když soubor ještě není."""
    return json.loads(soubor(cil).read_text(encoding="utf-8")) if soubor(cil).exists() else None


if __name__ == "__main__":
    if "--priprav" in sys.argv:
        priprav()
    for cil in OKNA:
        d = nacti(cil)
        if d:
            vysky = sorted(b[0] for b in d["b"])
            print(f"{cil}: {len(vysky)} budov, medián výšky {vysky[len(vysky) // 2]} m, nejvyšší {vysky[-1]} m")
