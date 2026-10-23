"""Rozliv Labe v Děčíně a Ústí z výškového modelu terénu (statický rozliv) pro hladiny po 10 cm.

Výška hladiny u vodočtu = nula vodočtu + hladina, podél řeky se mění se sklonem hladiny.
Zaplavený je každý bod terénu pod hladinou, který je s korytem spojený (8 sousedů).
Bez dynamiky: žádné proudění, objem vlny ani hráze pod rozlišením terénu.

Terén: ČÚZK DMR 5G (2 m, S-JTSK) z https://ags.cuzk.cz/arcgis2/rest/services/dmr5g/ImageServer,
dlaždice v data/raw/dem/. Osa řeky: OpenStreetMap (data/raw/osm/reky_overpass.json z animace.py,
bez něj si Labe stáhne z Overpass). `python app/rozliv_dem.py --priprav` postaví
data/external/rozliv_dem_<cil>.geojson (asi 3 minuty), `python app/rozliv_dem.py` jen vypíše kontroly
proti záplavovým územím DIBAVOD. V aplikaci: polygon(cil, hladina_cm), plocha_ha(cil, hladina_cm).
"""
import heapq
import json
import sys
from functools import cache
from io import BytesIO
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/dem"
OSM = ROOT / "data/raw/osm/reky_overpass.json"
N_LETE = ROOT / "data/external/n_lete_vody.csv"
UZEMI = ROOT / "data/external/zaplavova_uzemi.geojson"
DMR = "https://ags.cuzk.cz/arcgis2/rest/services/dmr5g/ImageServer/exportImage"
ZDROJ = "ČÚZK DMR 5G"
VODOCET = {"decin": (14.209554, 50.7821845), "usti": (14.042504, 50.6539106)}  # stanice_hydro.csv
NULA = {"decin": 120.07, "usti": 130.94}  # m n. m., n_lete_vody.csv
HLADINY = {"decin": range(300, 1251, 10), "usti": range(350, 1201, 10)}
KROK = 2  # m, nativní rozlišení služby
POLOMER = 3000  # m, čtverec 6 × 6 km kolem vodočtu
DLAZDICE = 1000  # pixelů
# Sklon hladiny z našich hodinových dat 2006–2025: (nula Ústí + H Ústí) − (nula Děčín + H Děčín o 4 h později)
# na 25,4 km řeky, medián 0,438 m/km a v pásmech hladiny 0,43 až 0,44. Oba vodočty jsou pod jezem Střekov.
SKLON = 0.44  # m/km
# Jez Střekov: staničení v m nad vodočtem Ústí a hladina zdrže v m n. m. podle vody v DMR 5G nad jezem
JEZ = {"usti": (1700, 141.55)}
TOLERANCE = 2.5  # m, zjednodušení obrysů; při 2 m má Děčín 3,99 MB
MIN_PLOCHA = 400  # m², menší ostrůvky a díry vynecháme


def soubor(cil):
    return ROOT / f"data/external/rozliv_dem_{cil}.geojson"


def _jtsk():
    from pyproj import Transformer
    return (Transformer.from_crs("EPSG:4326", "EPSG:5514", always_xy=True),
            Transformer.from_crs("EPSG:5514", "EPSG:4326", always_xy=True))


def _okno(cil):
    """Levý horní roh (x0, y0) v S-JTSK a počet pixelů na stranu."""
    x, y = _jtsk()[0].transform(*VODOCET[cil])
    x0, y0 = round((x - POLOMER) / KROK) * KROK, round((y + POLOMER) / KROK) * KROK
    return x0, y0, 2 * POLOMER // KROK


@cache
def teren(cil):
    """Výšky terénu (m n. m.) v mřížce po KROK m, řádky od severu; dlaždice se stáhnou jednou."""
    import requests
    from PIL import Image
    x0, y0, n = _okno(cil)
    z = np.empty((n, n), np.float32)
    for i in range(0, n, DLAZDICE):
        for j in range(0, n, DLAZDICE):
            f = RAW / f"dmr5g_{cil}_{i}_{j}.tif"
            if not f.exists():
                xa, ya = x0 + j * KROK, y0 - (i + DLAZDICE) * KROK
                r = requests.get(DMR, timeout=300, headers={"User-Agent": "Mozilla/5.0"}, params=dict(
                    bbox=f"{xa},{ya},{xa + DLAZDICE * KROK},{ya + DLAZDICE * KROK}", bboxSR=5514, imageSR=5514,
                    size=f"{DLAZDICE},{DLAZDICE}", format="tiff", pixelType="F32", f="image",
                    interpolation="RSP_NearestNeighbor"))
                r.raise_for_status()
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_bytes(r.content)
            z[i:i + DLAZDICE, j:j + DLAZDICE] = np.asarray(Image.open(BytesIO(f.read_bytes())), np.float32)
    return z


@cache
def osa(cil):
    """Osa Labe v okně: pixely (i, j) a staničení s v m po řece od vodočtu, kladné proti proudu.

    Cesty waterway=river v OSM jsou orientované po proudu, takže „proti proudu“ jsou uzly,
    ze kterých se po směru cest dá dojít k vodočtu.
    """
    do_jtsk = _jtsk()[0]
    x0, y0, n = _okno(cil)
    osm = OSM if OSM.exists() else RAW / "labe_osm.json"
    if not osm.exists():
        import requests
        # Overpass odmítá požadavky bez vlastního User-Agent (406)
        r = requests.post(
            "https://overpass-api.de/api/interpreter", timeout=600, headers={"User-Agent": "hackathon-decin-2026"},
            data={"data": '[out:json][timeout:240];way["waterway"="river"]["name"="Labe"](50.55,13.9,50.9,14.4);out geom;'})
        r.raise_for_status()
        osm.parent.mkdir(parents=True, exist_ok=True)
        osm.write_bytes(r.content)
    xy, dolu, sousede = {}, {}, {}
    for cesta in json.loads(osm.read_text(encoding="utf-8"))["elements"]:
        if cesta["tags"].get("name") != "Labe":
            continue
        x, y = do_jtsk.transform([g["lon"] for g in cesta["geometry"]], [g["lat"] for g in cesta["geometry"]])
        if not ((np.abs(np.array(x) - x0 - POLOMER) < 2 * POLOMER) & (np.abs(y0 - np.array(y) - POLOMER) < 2 * POLOMER)).any():
            continue
        for uzel, bod in zip(cesta["nodes"], zip(x, y)):
            xy[uzel] = bod
            sousede.setdefault(uzel, set())
            dolu.setdefault(uzel, set())
        for a, b in zip(cesta["nodes"], cesta["nodes"][1:]):
            sousede[a].add(b)
            sousede[b].add(a)
            dolu[a].add(b)
    uzly = list(xy)
    vx, vy = do_jtsk.transform(*VODOCET[cil])
    start = uzly[int(np.argmin([np.hypot(xy[u][0] - vx, xy[u][1] - vy) for u in uzly]))]
    vzdal, fronta = {start: 0.0}, [(0.0, start)]
    while fronta:
        d, u = heapq.heappop(fronta)
        if d > vzdal[u]:
            continue
        for m in sousede[u]:
            dm = d + np.hypot(xy[m][0] - xy[u][0], xy[m][1] - xy[u][1])
            if dm < vzdal.get(m, np.inf):
                vzdal[m] = dm
                heapq.heappush(fronta, (dm, m))
    nahore, fronta = {start}, [start]
    while fronta:
        u = fronta.pop()
        for m in sousede[u]:
            if u in dolu[m] and m not in nahore:
                nahore.add(m)
                fronta.append(m)
    s = {u: (vzdal[u] if u in nahore else -vzdal[u]) for u in vzdal}
    body = []
    for a in s:
        for b in dolu[a]:
            if b in s:
                k = np.linspace(0, 1, int(np.hypot(xy[b][0] - xy[a][0], xy[b][1] - xy[a][1])) + 2)
                body.append(np.column_stack([xy[a][0] + k * (xy[b][0] - xy[a][0]), xy[a][1] + k * (xy[b][1] - xy[a][1]),
                                             s[a] + k * (s[b] - s[a])]))
    body = np.vstack(body)
    i, j = ((y0 - body[:, 1]) / KROK).astype(int), ((body[:, 0] - x0) / KROK).astype(int)
    ok = (i >= 0) & (i < n) & (j >= 0) & (j < n)
    return i[ok], j[ok], body[ok, 2]


@cache
def prevyseni(cil):
    """O kolik m je hladina v každém pixelu výš než u vodočtu (sklon podle nejbližšího bodu osy)
    a nejnižší hladina v pixelu (zdrž nad jezem Střekov, jinde -inf)."""
    from scipy import ndimage
    z = teren(cil)
    i, j, s = osa(cil)
    reka = np.ones(z.shape, bool)
    reka[i, j] = False
    staniceni = np.zeros(z.shape, np.float32)
    staniceni[i, j] = s
    kde = ndimage.distance_transform_edt(reka, return_distances=False, return_indices=True)
    staniceni = staniceni[kde[0], kde[1]]
    minimum = np.full(z.shape, -np.inf, np.float32)
    if cil in JEZ:
        od, zdrz = JEZ[cil]
        minimum[staniceni > od] = zdrz
    return SKLON * staniceni / 1000, minimum


def maska(cil, hladina_cm):
    """Zaplavené pixely: terén pod hladinou a spojené s osou řeky (8 sousedů)."""
    from scipy import ndimage
    z = teren(cil)
    i, j, _ = osa(cil)
    nad, minimum = prevyseni(cil)
    pod = z < np.maximum(NULA[cil] + hladina_cm / 100 + nad, minimum)
    oblasti, _ = ndimage.label(pod, structure=np.ones((3, 3)))
    spojene = np.unique(oblasti[i, j])
    return np.isin(oblasti, spojene[spojene > 0])


def obrysy(m, cil):
    """Polygony masky [[vnější, díra, ...], ...] v WGS84, zjednodušené po TOLERANCE m."""
    import contourpy
    from rozliv import _plocha, _zjednodus
    x0, y0, n = _okno(cil)
    do_wgs = _jtsk()[1]
    # pixel (i, j) má střed v (x0 + (j + 0,5) KROK, y0 − (i + 0,5) KROK); okraj okna doplníme nulami, ať se polygony uzavřou
    pole = np.pad(m.astype(np.float32), 1)
    xs = x0 + (np.arange(n + 2) - 0.5) * KROK
    ys = y0 - (np.arange(n + 2) - 0.5) * KROK
    body, zacatky = contourpy.contour_generator(xs, ys, pole, fill_type="OuterOffset").filled(0.5, 1.5)
    polygony = []
    for b, z in zip(body, zacatky):
        kruhy = []
        for a, c in zip(z[:-1], z[1:]):
            p = _zjednodus(b[a:c], TOLERANCE)
            if len(p) >= 4 and abs(_plocha(p)) >= MIN_PLOCHA:
                if (_plocha(p) > 0) == bool(kruhy):  # GeoJSON: vnější proti směru hodinových ručiček, díry po
                    p = p[::-1]
                lon, lat = do_wgs.transform(p[:, 0], p[:, 1])
                kruhy.append(np.round(np.column_stack([lon, lat]), 5).tolist())
            elif not kruhy:
                break
        if kruhy:
            polygony.append(kruhy)
    return polygony


def priprav():
    for cil in VODOCET:
        features = []
        for h in HLADINY[cil]:
            m = maska(cil, h)
            features.append({"type": "Feature", "properties": {
                "cil": cil, "hladina_cm": h, "plocha_ha": round(float(m.sum()) * KROK ** 2 / 1e4, 1),
                "vyska_hladiny_m": round(NULA[cil] + h / 100, 2), "zdroj_dem": ZDROJ, "rozliseni_m": KROK,
                "sklon_m_km": SKLON,
            }, "geometry": {"type": "MultiPolygon", "coordinates": obrysy(m, cil)}})
            print(cil, h, features[-1]["properties"]["plocha_ha"], "ha", flush=True)
        soubor(cil).write_text(json.dumps({"type": "FeatureCollection", "features": features},
                                          ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(f"{soubor(cil).relative_to(ROOT)}: {soubor(cil).stat().st_size / 1e6:.2f} MB")


@cache
def _spocitane(cil):
    if not soubor(cil).exists():
        return {}
    return {f["properties"]["hladina_cm"]: f for f in json.loads(soubor(cil).read_text(encoding="utf-8"))["features"]}


def polygon(cil, hladina_cm):
    """GeoJSON Feature rozlivu pro nejbližší spočítanou hladinu (cm na vodočtu), None bez souboru."""
    f = _spocitane(cil)
    return f[min(f, key=lambda h: abs(h - hladina_cm))] if f else None


def plocha_ha(cil, hladina_cm):
    f = polygon(cil, hladina_cm)
    return f["properties"]["plocha_ha"] if f else float("nan")


def dibavod(cil, N):
    """Záplavové území DIBAVOD pro Q_N na úseku cil jako maska v mřížce terénu."""
    from PIL import Image, ImageDraw
    x0, y0, n = _okno(cil)
    do_jtsk = _jtsk()[0]
    vnejsi, diry = Image.new("1", (n, n)), Image.new("1", (n, n))
    for f in json.loads(UZEMI.read_text(encoding="utf-8"))["features"]:
        p = f["properties"]
        if p["usek"] == cil and p["N"] == N and p["typ"] == "záplavové území":
            for polygon_ in f["geometry"]["coordinates"]:
                for k, kruh in enumerate(polygon_):
                    x, y = do_jtsk.transform([c[0] for c in kruh], [c[1] for c in kruh])
                    body = list(zip((np.array(x) - x0) / KROK - 0.5, (y0 - np.array(y)) / KROK - 0.5))
                    ImageDraw.Draw(diry if k else vnejsi).polygon(body, fill=1)
    return np.asarray(vnejsi) & ~np.asarray(diry)


def kontrola():
    import pandas as pd
    q = pd.read_csv(N_LETE)
    for cil in VODOCET:
        print(f"{cil}: {ZDROJ}, {KROK} m, sklon {SKLON} m/km, okno {2 * POLOMER / 1000:.0f} × {2 * POLOMER / 1000:.0f} km")
        for N in (5, 20, 100):
            h = int(q.query("klic == @cil and N == @N").H_cm.iloc[0])
            a, b = maska(cil, h), dibavod(cil, N)
            ha = KROK ** 2 / 1e4
            print(f"  Q{N} ({h} cm): DEM {a.sum() * ha:.0f} ha, DIBAVOD {b.sum() * ha:.0f} ha, "
                  f"průnik {(a & b).sum() * ha:.0f} ha, IoU {(a & b).sum() / (a | b).sum():.2f}, "
                  f"jen DEM {(a & ~b).sum() * ha:.0f} ha, jen DIBAVOD {(b & ~a).sum() * ha:.0f} ha")
        plochy = [f["properties"]["plocha_ha"] for f in _spocitane(cil).values()]
        if plochy:
            print(f"  {min(HLADINY[cil])} cm: {plochy[0]} ha, {max(HLADINY[cil])} cm: {plochy[-1]} ha, "
                  f"plocha neklesá: {bool(np.all(np.diff(plochy) >= 0))}, "
                  f"soubor {soubor(cil).stat().st_size / 1e6:.2f} MB")


if __name__ == "__main__":
    if "--priprav" in sys.argv:
        priprav()
    kontrola()
