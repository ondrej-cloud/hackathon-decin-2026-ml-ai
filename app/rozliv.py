"""Předpovězená hladina Labe jako N-letá voda a oficiální záplavové území, které k ní patří.

Bez vlastní hydrauliky: hladinu převedeme na průtok měrnou křivkou z našich hodinových dat,
průtok porovnáme s N-letými průtoky ČHMÚ a na mapě ukážeme záplavové území DIBAVOD (VÚV TGM)
pro tu N-letou vodu. Polygony platí pro ustálený N-letý průtok, ne pro konkrétní povodeň.

Data: data/external/n_lete_vody.csv a data/external/zaplavova_uzemi.geojson, oboje postaví
`python app/rozliv.py --priprav` z data/raw/zaplavy/ (chybějící soubory stáhne, asi 750 MB).
Ukázka: `streamlit run app/rozliv.py`.
"""
import json
import re
import struct
import sys
import zipfile
from functools import cache
from io import BytesIO
from pathlib import Path

import numpy as np
import pandas as pd
import pydeck as pdk

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from data import CILE, nacti  # noqa: E402

RAW = ROOT / "data/raw/zaplavy"
SOUBOR_N = ROOT / "data/external/n_lete_vody.csv"
SOUBOR_UZEMI = ROOT / "data/external/zaplavova_uzemi.geojson"
PREHANI = 2.5  # stejné převýšení terénu jako v mapa.py
NAD_TERENEM = 4  # m; síť terénu v mapě je hrubší než výšky, ze kterých bereme výšku polygonů

CHMU = "https://opendata.chmi.cz/hydrology/characteristic/data"
EVLIST = {"decin": 2497644, "usti": 307228}  # číslo profilu v https://hydro.chmi.cz/hpps/
DIBAVOD = "https://www.dibavod.cz/data/download"
VRSTVY = {  # sada DIBAVOD: (N, typ)
    "dib_D01_ZaplUzemi5Vody": (5, "záplavové území"),
    "dib_D02_ZaplUzemi20Vody": (20, "záplavové území"),
    "dib_D03_ZaplUzemi100Vody": (100, "záplavové území"),
    "dib_D05_AktivniZony100Vody": (100, "aktivní zóna"),
}
# Labe od Ústí po státní hranici; úseky se dělí v půli cesty mezi vodočty Ústí a Děčín.
USEKY = {"usti": (13.95, 50.60, 14.35, 50.72), "decin": (13.95, 50.72, 14.35, 50.90)}
TOLERANCE_M = 4
MIN_PLOCHA_M2 = 1500
TERRARIUM = "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"
ZOOM_VYSKY = 14  # stejné jako max_zoom terénu v mapě

SLOVY = {1: "jednoletá", 2: "dvouletá", 5: "pětiletá", 10: "desetiletá", 20: "dvacetiletá",
         50: "padesátiletá", 100: "stoletá"}
GENITIV = {5: "pětileté", 20: "dvacetileté", 100: "stoleté"}
MODRA = [30, 120, 220]


def _cislo(x):
    return f"{x:,.0f}".replace(",", " ")


@cache
def n_lete():
    return pd.read_csv(SOUBOR_N)


@cache
def merna_krivka(cil):
    """Hladina (cm) → průtok (m³/s): medián průtoku v pásmech hladiny po 10 cm, 2006–2025, neklesající."""
    x = nacti()[[f"{cil}_H", f"{cil}_Q"]].dropna()
    pasmo = x[f"{cil}_H"] // 10 * 10 + 5
    q = x.groupby(pasmo)[f"{cil}_Q"].median()
    return q.index.to_numpy(), np.maximum.accumulate(q.to_numpy())


def prutok(cil, hladina_cm):
    h, q = merna_krivka(cil)
    return float(np.interp(hladina_cm, h, q))


def n_leta_voda(cil, hladina_cm):
    """{prutok_m3s, N, popis}; N je největší N-letá voda ČHMÚ, kterou průtok dosáhne (0 = pod Q1)."""
    q = prutok(cil, hladina_cm)
    t = n_lete().query("klic == @cil").sort_values("N")
    dosazeno = t[t.Q_m3s <= q]
    zacatek = f"{hladina_cm:.0f} cm odpovídá asi {_cislo(round(q, -1))} m³/s"
    if dosazeno.empty:
        q1 = t.iloc[0].Q_m3s
        popis = f"{zacatek}, to je pod jednoletou vodou (Q1 = {_cislo(q1)} m³/s podle ČHMÚ), bez rozlivu mimo koryto."
        N = 0
    else:
        r = dosazeno.iloc[-1]
        N = int(r.N)
        dalsi = t[t.N > N]
        if dalsi.empty:
            popis = f"{zacatek}, to je víc než stoletá voda (Q100 = {_cislo(r.Q_m3s)} m³/s podle ČHMÚ)."
        else:
            d = dalsi.iloc[0]
            popis = (f"{zacatek}, to je zhruba {SLOVY[N]} voda (Q{N} = {_cislo(r.Q_m3s)} m³/s, "
                     f"Q{int(d.N)} = {_cislo(d.Q_m3s)} m³/s podle ČHMÚ).")
    if hladina_cm > nacti()[f"{cil}_H"].max():
        popis += " Tak vysoko jsme hladinu nikdy nezměřili, průtok může být i vyšší."
    return {"prutok_m3s": q, "N": N, "popis": popis}


@cache
def _uzemi():
    """Polygony z geojsonu s výškou převedenou na výšku v mapě (terén zvýšený PREHANI×)."""
    features = json.loads(SOUBOR_UZEMI.read_text(encoding="utf-8"))["features"]
    for f in features:
        f["geometry"]["coordinates"] = [
            [[[x, y, round((z + NAD_TERENEM) * PREHANI)] for x, y, z in kruh] for kruh in polygon]
            for polygon in f["geometry"]["coordinates"]
        ]
    return features


def vrstvy(cil, hladina_cm):
    """GeoJsonLayer záplavových území Q5, Q20, Q100 na úseku Labe u stanice cil.

    Vyplněné je největší území, jehož N-letou vodu předpověď dosáhne; ostatní jen obrysem.
    Souřadnice jsou [lon, lat, výška v mapě], pasují na pdk.Deck z mapa.py.
    """
    voda = n_leta_voda(cil, hladina_cm)
    zony = [N for N in (5, 20, 100) if N <= voda["N"]]
    vyplnit = zony[-1] if zony else None
    q = n_lete().query("klic == @cil").set_index("N").Q_m3s
    plne, obrysy = [], []
    for f in _uzemi():
        p = f["properties"]
        if p["usek"] != cil or p["typ"] != "záplavové území":
            continue
        tooltip = (f"Záplavové území {GENITIV[p['N']]} vody (Q{p['N']} = {_cislo(q[p['N']])} m³/s "
                   f"{'v Děčíně' if cil == 'decin' else 'v Ústí'})\nDIBAVOD, VÚV TGM; průběh je orientační")
        if p["N"] == vyplnit:
            tooltip += f"\nOdpovídá předpovědi: {voda['popis']}"
        (plne if p["N"] == vyplnit else obrysy).append(f | {"tooltip": tooltip})
    vysledek = []
    if obrysy:
        vysledek.append(pdk.Layer(
            "GeoJsonLayer", id=f"rozliv-{cil}-obrysy", data=obrysy,
            filled=False, stroked=True, extruded=False,
            get_line_color=MODRA + [170], line_width_min_pixels=1, line_width_units="pixels",
            pickable=True,
        ))
    if plne:
        vysledek.append(pdk.Layer(
            "GeoJsonLayer", id=f"rozliv-{cil}-Q{vyplnit}", data=plne,
            filled=True, stroked=True, extruded=False,
            get_fill_color=MODRA + [110], get_line_color=[15, 80, 170, 230],
            line_width_min_pixels=2, line_width_units="pixels",
            pickable=True, auto_highlight=True,
        ))
    return vysledek


def _stahni(url, soubor):
    if not soubor.exists():
        import requests
        soubor.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, timeout=1800, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        soubor.write_bytes(r.content)
    return soubor


def _priprav_n_lete():
    radky = []
    for klic, (cislo, _) in CILE.items():
        ny = f"{CHMU}/hydrological_characteristic/NY_0-203-1-{cislo}.json"
        rc = f"{CHMU}/discharge_rating_curve/RC_0-203-1-{cislo}.json"
        ev = f"https://hydro.chmi.cz/hppsevlist/download?seq={EVLIST[klic]}"
        qn = json.loads(_stahni(ny, RAW / "chmu" / ny.rsplit("/", 1)[1]).read_text(encoding="utf-8"))
        krivka = np.array(json.loads(_stahni(rc, RAW / "chmu" / rc.rsplit("/", 1)[1]).read_text(
            encoding="utf-8"))["curveData"]["data"]["values"])
        html = _stahni(ev, RAW / "chmu" / f"evlist_{klic}.html").read_text(encoding="utf-8")
        nula = float(re.search(r"Nula vodočtu:</th><td >([\d.]+)", html).group(1))
        for N, q in qn["charList"][0]["charData"]["data"]["values"]:
            # oficiální měrná křivka ČHMÚ je po 1 cm, bereme nejnižší hladinu s průtokem aspoň Q_N
            H = int(krivka[np.searchsorted(krivka[:, 1], q), 0]) if q <= krivka[-1, 1] else None
            radky.append({"klic": klic, "N": N, "Q_m3s": q, "H_cm": H, "nula_vodoctu_m": nula,
                          "zdroj": ny, "zdroj_H": rc, "zdroj_nula": ev})
    pd.DataFrame(radky).astype({"H_cm": "Int64"}).to_csv(SOUBOR_N, index=False)


def _dbf_labe(dbf):
    """Indexy záznamů s NAZ_TOK == Labe."""
    b = dbf.read_bytes()
    n, hlavicka, delka = struct.unpack("<IHH", b[4:12])
    pole, i = {}, 32
    zacatek = 1
    while b[i] != 0x0D:
        pole[b[i:i + 11].split(b"\0")[0].decode()] = (zacatek, b[i + 16])
        zacatek += b[i + 16]
        i += 32
    od, dl = pole["NAZ_TOK"]
    return [k for k in range(n)
            if b[hlavicka + k * delka + od:hlavicka + k * delka + od + dl].decode("utf-8").strip() == "Labe"]


def _shp_kruhy(shp, zaznam):
    """Prstence polygonu (souřadnice S-JTSK v m) jednoho záznamu SHP."""
    offset = struct.unpack(">i", shp.with_suffix(".shx").read_bytes()[100 + 8 * zaznam:104 + 8 * zaznam])[0] * 2
    with open(shp, "rb") as f:
        f.seek(offset + 8)
        typ, = struct.unpack("<i", f.read(4))
        assert typ in (5, 15), typ  # Polygon nebo PolygonZ, výšku Z nepotřebujeme
        f.read(32)
        casti, bodu = struct.unpack("<2i", f.read(8))
        zacatky = list(struct.unpack(f"<{casti}i", f.read(4 * casti))) + [bodu]
        body = np.frombuffer(f.read(16 * bodu), dtype="<f8").reshape(-1, 2)
    return [body[a:b] for a, b in zip(zacatky[:-1], zacatky[1:])]


def _zjednodus(p, tol):
    """Douglas-Peucker pro jeden prstenec."""
    nechat = np.zeros(len(p), bool)
    nechat[[0, -1]] = True
    zasobnik = [(0, len(p) - 1)]
    while zasobnik:
        a, b = zasobnik.pop()
        if b - a < 2:
            continue
        d = p[b] - p[a]
        v = p[a + 1:b] - p[a]
        delka = np.hypot(*d)
        vzdal = np.abs(d[0] * v[:, 1] - d[1] * v[:, 0]) / delka if delka else np.hypot(v[:, 0], v[:, 1])
        i = int(np.argmax(vzdal))
        if vzdal[i] > tol:
            nechat[a + 1 + i] = True
            zasobnik += [(a, a + 1 + i), (a + 1 + i, b)]
    return p[nechat]


def _plocha(p):
    return 0.5 * float(np.dot(p[:-1, 0], p[1:, 1]) - np.dot(p[1:, 0], p[:-1, 1]))


def _orez(p, obdelnik):
    """Sutherland-Hodgman: prstenec oříznutý obdélníkem (x0, y0, x1, y1)."""
    for osa, mez, vetsi in ((0, obdelnik[0], True), (0, obdelnik[2], False), (1, obdelnik[1], True), (1, obdelnik[3], False)):
        if not len(p):
            return p
        uvnitr = p[:, osa] >= mez if vetsi else p[:, osa] <= mez
        if uvnitr.all():
            continue
        q = np.roll(p, 1, axis=0)
        with np.errstate(divide="ignore", invalid="ignore"):
            t = (mez - q[:, osa]) / (p[:, osa] - q[:, osa])
            prusecik = q + t[:, None] * (p - q)
        prusecik[:, osa] = mez
        maska = np.stack([uvnitr != np.roll(uvnitr, 1), uvnitr], axis=1)
        p = np.stack([prusecik, p], axis=1)[maska]
    return p


def _uvnitr(bod, p):
    x, y = bod
    a, b = p, np.roll(p, 1, axis=0)
    krizi = (a[:, 1] > y) != (b[:, 1] > y)
    with np.errstate(divide="ignore", invalid="ignore"):
        xs = a[:, 0] + (y - a[:, 1]) * (b[:, 0] - a[:, 0]) / (b[:, 1] - a[:, 1])
    return bool(np.count_nonzero(krizi & (x < xs)) % 2)


def _vysky(body):
    """Nadmořská výška terénu (m) z dlaždic Terrarium, stejný zdroj jako terén v mapě bez Mapboxu.

    Bereme nejnižší bod z okolí 3 × 3 pixely (asi 18 m): hranice území leží u paty svahu
    a vyšší bod ze svahu by polygon zvedl nad vodu.
    """
    from PIL import Image
    n = 2 ** ZOOM_VYSKY
    lat = np.radians(body[:, 1])
    x = (body[:, 0] + 180) / 360 * n * 256
    y = (1 - np.log(np.tan(lat) + 1 / np.cos(lat)) / np.pi) / 2 * n * 256
    tx, ty = (x // 256).astype(int), (y // 256).astype(int)
    z = np.empty(len(body))
    for dx, dy in set(zip(tx, ty)):
        soubor = _stahni(TERRARIUM.format(z=ZOOM_VYSKY, x=dx, y=dy), RAW / f"terrarium/{ZOOM_VYSKY}/{dx}/{dy}.png")
        rgb = np.asarray(Image.open(BytesIO(soubor.read_bytes())).convert("RGB"), dtype=float)
        vyska = np.pad(rgb[..., 0] * 256 + rgb[..., 1] + rgb[..., 2] / 256 - 32768, 1, mode="edge")
        vyska = np.min([vyska[i:i + 256, j:j + 256] for i in range(3) for j in range(3)], axis=0)
        m = (tx == dx) & (ty == dy)
        z[m] = vyska[(y[m] % 256).astype(int), (x[m] % 256).astype(int)]
    return z


def _priprav_uzemi():
    from pyproj import Transformer
    do_wgs = Transformer.from_crs("EPSG:5514", "EPSG:4326", always_xy=True)
    do_jtsk = Transformer.from_crs("EPSG:4326", "EPSG:5514", always_xy=True)
    cely = (min(u[0] for u in USEKY.values()), min(u[1] for u in USEKY.values()),
            max(u[2] for u in USEKY.values()), max(u[3] for u in USEKY.values()))
    rohy = np.array(do_jtsk.transform([cely[0], cely[2], cely[0], cely[2]], [cely[1], cely[1], cely[3], cely[3]])).T
    features = []
    for sada, (N, typ) in VRSTVY.items():
        slozka = RAW / sada
        if not any(slozka.glob("*.shp")):
            with zipfile.ZipFile(_stahni(f"{DIBAVOD}/{sada}.zip", slozka / f"{sada}.zip")) as z:
                z.extractall(slozka)
        shp = next(slozka.glob("*.shp"))
        kruhy = []
        for zaznam in _dbf_labe(shp.with_suffix(".dbf")):
            for p in _shp_kruhy(shp, zaznam):
                if (p[:, 0].max() < rohy[:, 0].min() or p[:, 0].min() > rohy[:, 0].max()
                        or p[:, 1].max() < rohy[:, 1].min() or p[:, 1].min() > rohy[:, 1].max()):
                    continue
                p = _zjednodus(p, TOLERANCE_M)
                if len(p) >= 4 and abs(_plocha(p)) >= MIN_PLOCHA_M2:
                    # v SHP jsou vnější prstence po směru hodinových ručiček, díry proti
                    kruhy.append((np.array(do_wgs.transform(p[:, 0], p[:, 1])).T, _plocha(p) < 0))
        for usek, obdelnik in USEKY.items():
            vnejsi, diry = [], []
            for p, je_vnejsi in kruhy:
                p = _orez(p, obdelnik)
                if len(p) < 3:
                    continue
                p = np.vstack([p, p[:1]])
                (vnejsi if je_vnejsi else diry).append(p)
            polygony = [[p] for p in vnejsi]
            for d in diry:
                for poly in polygony:
                    if _uvnitr(d[0], poly[0]):
                        poly.append(d)
                        break
            if not polygony:
                continue
            for poly in polygony:
                for i, p in enumerate(poly):
                    poly[i] = [[round(x, 5), round(y, 5), round(float(z))] for (x, y), z in zip(p, _vysky(p))]
            features.append({"type": "Feature", "properties": {
                "N": N, "typ": typ, "usek": usek, "zdroj": f"{DIBAVOD}/{sada}.zip",
                "popis": f"{typ} Q{N}, Labe, DIBAVOD (VÚV TGM), průběh je orientační",
            }, "geometry": {"type": "MultiPolygon", "coordinates": polygony}})
            print(sada, usek, len(polygony), "polygonů,", sum(len(k) for p in polygony for k in p), "bodů")
    SOUBOR_UZEMI.write_text(json.dumps({"type": "FeatureCollection", "features": features},
                                       ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{SOUBOR_UZEMI.relative_to(ROOT)}: {SOUBOR_UZEMI.stat().st_size / 1e6:.2f} MB")


def priprav():
    _priprav_n_lete()
    _priprav_uzemi()


def _teren(token):
    """TerrainLayer se stejným nastavením jako v mapa.py."""
    if token:
        vysky = f"https://api.mapbox.com/v4/mapbox.terrain-rgb/{{z}}/{{x}}/{{y}}.pngraw?access_token={token}"
        povrch = f"https://api.mapbox.com/v4/mapbox.satellite/{{z}}/{{x}}/{{y}}@2x.png?access_token={token}"
        dekoder = {"rScaler": 6553.6, "gScaler": 25.6, "bScaler": 0.1, "offset": -10000}
    else:
        vysky = TERRARIUM
        povrch = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        dekoder = {"rScaler": 256, "gScaler": 1, "bScaler": 1 / 256, "offset": -32768}
    return pdk.Layer(
        "TerrainLayer", id="teren", elevation_data=vysky, texture=povrch,
        elevation_decoder={k: v * PREHANI for k, v in dekoder.items()},
        tile_size=256, min_zoom=0, max_zoom=14, extent=[13.4, 49.6, 15.9, 51.05], mesh_max_error=8,
        material={"ambient": 0.6, "diffuse": 0.6, "shininess": 12}, pickable=False,
    )


def ukazka():
    import streamlit as st
    sys.path.insert(0, str(ROOT / "app"))
    from mapa import mapbox_token

    st.set_page_config(page_title="Rozliv Labe v Děčíně", layout="wide")
    st.title("Jaké záplavové území odpovídá hladině v Děčíně")
    hladina = st.slider("Hladina Labe v Děčíně (cm)", 200, 1100, 739, step=10)
    voda = n_leta_voda("decin", hladina)
    st.write(voda["popis"])
    st.pydeck_chart(pdk.Deck(
        layers=[_teren(mapbox_token())] + vrstvy("decin", hladina),
        initial_view_state=pdk.ViewState(latitude=50.775, longitude=14.205, zoom=12.3, pitch=55, bearing=-20,
                                         min_zoom=8, max_zoom=15),
        map_style=None, map_provider=None, height=650,
        tooltip={"text": "{tooltip}", "style": {"backgroundColor": "#172b3a", "color": "white", "fontSize": "14px"}},
    ), height=650, key="mapa-rozliv")
    st.caption(
        "Plná modrá: oficiální záplavové území pro N-letou vodu, kterou průtok dosáhne; obrysy: ostatní z Q5, Q20 a Q100. "
        "Území platí pro ustálený N-letý průtok, ne pro tuhle konkrétní povodeň, a v Děčíně rozliv ovlivňuje i Ploučnice. "
        "Průtok je z měrné křivky našich dat 2006–2025, N-leté průtoky z ČHMÚ (2024). Terén je zvýšený 2,5×."
    )
    st.caption(
        "Záplavová území: [DIBAVOD, VÚV TGM](https://www.dibavod.cz/) (stav 30. 10. 2025, průběh je jen orientační) · "
        "N-leté průtoky: [ČHMÚ](https://opendata.chmi.cz/hydrology/characteristic/) · "
        "Mapový podklad: [© OpenStreetMap contributors](https://www.openstreetmap.org/copyright) · "
        "Výšky: [Mapzen / AWS Terrain Tiles](https://github.com/tilezen/joerd/blob/master/docs/attribution.md)"
    )


if __name__ == "__main__":
    priprav() if "--priprav" in sys.argv else ukazka()
