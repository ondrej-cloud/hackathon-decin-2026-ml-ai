r"""Živá 3D animace povodně na Labi: průtoky stanic a voda, která po řekách teče k Děčínu.

Všechno se kreslí v prohlížeči (deck.gl), čas proto běží plynule bez překreslování přes server.

Ukázka z kořene repozitáře:
    .venv\Scripts\python -m streamlit run app/animace.py
V aplikaci (od a do jsou UTC, okno("1/2011") je vrátí pro známou povodeň):
    st.iframe(animace.html(od, do, nazev), height=720)
    starší Streamlit bez st.iframe: streamlit.components.v1.html(animace.html(od, do, nazev), height=720)

Řeky v data/external/reky.geojson postaví `python app/animace.py reky` z OpenStreetMap (Overpass API).
"""
import heapq
import json
import math
import sys
from functools import cache

import numpy as np
import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components

from mapa import BARVY, MERITKO_PRUTOKU, PREHANI, SEDA, VYSKY, mapbox_token
from predikce import ROOT, SPA, nacti, nacti_model, nazev_modelu, vstupy

PASMO = "Europe/Prague"
DECK = "https://unpkg.com/deck.gl@9.1.14/dist.min.js"
REKY = ROOT / "data/external/reky.geojson"
OSM = ROOT / "data/raw/osm/reky_overpass.json"
STANICE = ROOT / "data/external/stanice_hydro.csv"
POVODNE = {"4/2006": ("2006-03-25", "2006-04-10"), "3/2009": ("2009-02-26", "2009-03-14"),
           "9/2010": ("2010-09-20", "2010-10-06"), "1/2011": ("2011-01-08", "2011-01-24"),
           "9/2024 Boris (test)": ("2024-09-08", "2024-09-24")}
# Doba putování vody v hodinách. Ústí → Děčín, Praha → Vraňany a Mělník → Ústí jsou změřené (docs/DATA.md),
# ostatní jsou odhad z rozdílu dob do Ústí v tabulce stanic a z délky úseku.
USEKY = {
    ("prelouc", "nymburk"): 8, ("nymburk", "kostelec"): 5, ("jizera", "kostelec"): 6,
    ("kostelec", "melnik"): 3, ("beroun", "praha"): 4, ("sazava", "praha"): 5,
    ("praha", "vranany"): 4.5, ("vranany", "melnik"): 2, ("melnik", "usti"): 12,
    ("louny", "usti"): 20, ("usti", "decin"): 4,
}
NABEH = 24  # hodin dat před oknem, aby kapky hned na začátku nesly naměřený průtok
JMENA_REK = ("Labe", "Vltava", "Ohře", "Berounka", "Sázava", "Jizera")
DOTAZ = "[out:json][timeout:240];(" + "".join(
    f'way["waterway"="river"]["name"="{j}"](49.8,13.5,50.9,15.7);' for j in JMENA_REK) + ");out geom;"


def _metry(lon, lat):
    """Rovinné souřadnice v metrech; na pár set kilometrů kolem 50° s. š. stačí."""
    return lon * 111320 * math.cos(math.radians(50.3)), lat * 110540


def _zjednodus(body, tolerance):
    """Douglasův–Peuckerův algoritmus: nechá jen body, které od spojnice sousedů uhnou víc než tolerance (m)."""
    nechat = [False] * len(body)
    nechat[0] = nechat[-1] = True
    zasobnik = [(0, len(body) - 1)]
    while zasobnik:
        i, j = zasobnik.pop()
        if j - i < 2:
            continue
        (x1, y1), (x2, y2) = body[i], body[j]
        delka = math.dist(body[i], body[j]) or 1

        def odchylka(k):
            return abs((x2 - x1) * (y1 - body[k][1]) - (x1 - body[k][0]) * (y2 - y1)) / delka

        k = max(range(i + 1, j), key=odchylka)
        if odchylka(k) > tolerance:
            nechat[k] = True
            zasobnik += [(i, k), (k, j)]
    return [i for i, ok in enumerate(nechat) if ok]


def _nejkratsi(xy, sousede, a, b):
    """Dijkstra: nejkratší cesta po síti řek z uzlu a do uzlu b."""
    vzdal, odkud, fronta = {a: 0.0}, {}, [(0.0, a)]
    while fronta:
        d, n = heapq.heappop(fronta)
        if n == b:
            break
        if d > vzdal[n]:
            continue
        for m in sousede[n]:
            dm = d + math.dist(xy[n], xy[m])
            if dm < vzdal.get(m, math.inf):
                vzdal[m], odkud[m] = dm, n
                heapq.heappush(fronta, (dm, m))
    cesta = [b]
    while cesta[-1] != a:
        cesta.append(odkud[cesta[-1]])
    return cesta[::-1]


def postav_reky(max_bodu=3000):
    """Úseky řek mezi stanicemi z OpenStreetMap, zjednodušené na nejvýš max_bodu bodů."""
    if not OSM.exists():
        OSM.parent.mkdir(parents=True, exist_ok=True)
        odpoved = requests.post("https://overpass-api.de/api/interpreter", data={"data": DOTAZ}, timeout=600)
        odpoved.raise_for_status()
        OSM.write_bytes(odpoved.content)
    lonlat, xy, reka, sousede = {}, {}, {}, {}
    for cesta in json.loads(OSM.read_text(encoding="utf-8"))["elements"]:
        for n, g in zip(cesta["nodes"], cesta["geometry"]):
            lonlat[n] = (g["lon"], g["lat"])
            xy[n] = _metry(g["lon"], g["lat"])
            reka.setdefault(n, set()).add(cesta["tags"]["name"])
            sousede.setdefault(n, set())
        for a, b in zip(cesta["nodes"], cesta["nodes"][1:]):
            sousede[a].add(b)
            sousede[b].add(a)

    # OSM má řeky místy přerušené (jezy, plavební komory). Konec čáry spojíme s nejbližším bodem
    # stejné řeky z jiné souvislé části, když je do 500 m.
    cast = {}
    for start in sousede:
        if start not in cast:
            cast[start], fronta = start, [start]
            while fronta:
                for m in sousede[fronta.pop()]:
                    if m not in cast:
                        cast[m] = start
                        fronta.append(m)
    uzly = list(xy)
    poloha = np.array([xy[n] for n in uzly])
    for n in [n for n in uzly if len(sousede[n]) == 1]:
        jinde = np.array([cast[m] != cast[n] and bool(reka[m] & reka[n]) for m in uzly])
        if jinde.any():
            d = np.where(jinde, np.hypot(*(poloha - xy[n]).T), np.inf)
            if d.min() < 500:
                m = uzly[int(d.argmin())]
                sousede[n].add(m)
                sousede[m].add(n)

    stanice = pd.read_csv(STANICE).set_index("klic")
    uzel = {}
    for klic, s in stanice.iterrows():
        na_rece = [n for n in uzly if s.tok in reka[n]]
        x, y = _metry(s.lon, s.lat)
        uzel[klic] = min(na_rece, key=lambda n: (xy[n][0] - x) ** 2 + (xy[n][1] - y) ** 2)
    cesty = {usek: _nejkratsi(xy, sousede, uzel[usek[0]], uzel[usek[1]]) for usek in USEKY}

    tolerance = 15
    while True:
        vybrane = {usek: [c[i] for i in _zjednodus([xy[n] for n in c], tolerance)] for usek, c in cesty.items()}
        if sum(map(len, vybrane.values())) <= max_bodu:
            break
        tolerance *= 1.25
    prvky = []
    for (od, do), c in cesty.items():
        delka = sum(math.dist(xy[a], xy[b]) for a, b in zip(c, c[1:])) / 1000
        prvky.append({
            "type": "Feature",
            "properties": {"od": od, "do": do, "delka_km": round(delka, 1), "doba_h": USEKY[(od, do)],
                           "reky": sorted({r for n in c for r in reka[n]})},
            "geometry": {"type": "LineString",
                         "coordinates": [[round(v, 5) for v in lonlat[n]] for n in vybrane[(od, do)]]},
        })
    REKY.write_text(json.dumps({"type": "FeatureCollection", "features": prvky}, ensure_ascii=False),
                    encoding="utf-8")
    for p in prvky:
        v = p["properties"]
        print(f"{v['od']:>8} → {v['do']:<8} {v['delka_km']:6.1f} km  {v['doba_h']:>4} h  "
              f"{v['delka_km'] / v['doba_h']:4.1f} km/h  {len(p['geometry']['coordinates'])} bodů")
    print(f"tolerance {tolerance:.0f} m, {REKY.stat().st_size / 1000:.0f} kB")


@cache
def _percentily():
    return nacti().loc["2006":"2018"].filter(regex="_Q$").quantile([0.5, 0.95, 0.99])


@cache
def _vstupy(cil):
    return vstupy(cil)


def _rada(hodnoty, mist=1):
    return [None if pd.isna(v) else round(float(v), mist) for v in hodnoty]


def _popisek(t):
    t = t.tz_convert(PASMO)
    return f"{t.day}. {t.month}. {t.year} {t:%H:%M} {'SELČ' if t.dst() else 'SEČ'}"


def _useky():
    """Úseky z reky.geojson s výškou hladiny podél toku (lineárně mezi stanicemi) a vzdáleností od začátku."""
    useky = []
    for prvek in json.loads(REKY.read_text(encoding="utf-8"))["features"]:
        od, do = prvek["properties"]["od"], prvek["properties"]["do"]
        body = prvek["geometry"]["coordinates"]
        vzdal = [0.0]
        for a, b in zip(body, body[1:]):
            vzdal.append(vzdal[-1] + math.dist(_metry(*a), _metry(*b)))
        z1, z2 = (VYSKY[k] * PREHANI + 30 for k in (od, do))
        useky.append({
            "od": od, "do": do, "doba": USEKY[(od, do)],
            "cesta": [[x, y, round(z1 + (z2 - z1) * d / vzdal[-1])] for (x, y), d in zip(body, vzdal)],
            "vzdal": [round(d) for d in vzdal],
        })
    return useky


def _teren():
    token = mapbox_token()
    if token:
        vysky = f"https://api.mapbox.com/v4/mapbox.terrain-rgb/{{z}}/{{x}}/{{y}}.pngraw?access_token={token}"
        povrch = f"https://api.mapbox.com/v4/mapbox.satellite/{{z}}/{{x}}/{{y}}@2x.png?access_token={token}"
        dekoder = {"rScaler": 6553.6, "gScaler": 25.6, "bScaler": 0.1, "offset": -10000}
        zdroj = "Snímky a výšky © Mapbox, © Maxar"
    else:
        vysky = "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"
        povrch = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        dekoder = {"rScaler": 256, "gScaler": 1, "bScaler": 1 / 256, "offset": -32768}
        zdroj = "Podklad © OpenStreetMap, výšky Mapzen / AWS Terrain Tiles"
    # TerrainLayer nemá elevationScale, převýšení je vynásobený dekodér včetně offsetu (jako v mapa.py).
    return {"vysky": vysky, "povrch": povrch, "dekoder": {k: v * PREHANI for k, v in dekoder.items()},
            "satelit": bool(token), "zdroj": zdroj}


def okno(povoden):
    """Od 14 dní před vrcholem hladiny v Děčíně do 5 dní po něm (UTC)."""
    vrchol = nacti().loc[slice(*POVODNE[povoden]), "decin_H"].idxmax()
    return vrchol - pd.Timedelta(days=14), vrchol + pd.Timedelta(days=5)


def html(od, do, model="ridge", pisma=None) -> str:
    """Stránka s animací od `od` do `do` (pandas Timestamp v UTC) pro st.iframe(..., height=720).

    Předpověď je z models/<model>_<cil>_24.joblib, vydaná v každé hodině okna na 24 h dopředu.
    """
    hodina = pd.Timedelta(hours=1)
    cas = pd.date_range(od - NABEH * hodina, do + 24 * hodina, freq="h")
    D = nacti().reindex(cas)
    percentily = _percentily()
    stanice = []
    for s in pd.read_csv(STANICE).itertuples(index=False):
        q50, p95, p99 = percentily[f"{s.klic}_Q"]
        stanice.append({"klic": s.klic, "nazev": s.stanice, "tok": s.tok, "lon": s.lon, "lat": s.lat,
                        "z": VYSKY[s.klic] * PREHANI + 40, "spa": SPA.get(s.klic),
                        "q50": round(q50, 1), "p95": round(p95, 1), "p99": round(p99, 1)})
    predpovedi = {}
    for cil in SPA:
        X = _vstupy(cil)
        X = X[X.index.isin(cas)]
        p = pd.Series(nacti_model(model, cil, 24).predict(X), index=X.index)
        predpovedi[cil] = _rada(p.reindex(cas))
    data = {
        "nabeh": NABEH, "konec": int((do - od) / hodina), "model": model, "nazev_modelu": nazev_modelu(model),
        "popisky": [_popisek(t) for t in cas],
        "Q": {s["klic"]: _rada(D[f"{s['klic']}_Q"]) for s in stanice},
        "H": {cil: _rada(D[f"{cil}_H"]) for cil in SPA},
        "P": predpovedi,
        "stanice": stanice, "useky": _useky(), "teren": _teren(),
        "barvy": BARVY_PULT, "seda": SEDA_PULT, "meritko": MERITKO_PRUTOKU,
    }
    data = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return STRANKA.replace("__DECK__", DECK).replace("__PISMA__", _pisma(pisma)).replace("__DATA__", data)


# barvy povodňového pultu (app/styl.py, web/css/pult.css): bez stupně voda, stupně žlutá, oranžová, červená
BARVY_PULT = ([58, 160, 201], [242, 196, 55], [239, 108, 0], [198, 40, 40])
SEDA_PULT = [139, 152, 165]


def _pisma(pisma):
    """Písma webu: ze složky `pisma` (na webu ../fonts/), bez ní z Google Fonts (aplikace, iframe bez souborů)."""
    if pisma:
        return PISMA_LOKALNE.replace("__PISMA__", pisma)
    return PISMA_GOOGLE


PISMA_LOKALNE = '''<style>
@font-face { font-family: "Schibsted Grotesk"; font-style: normal; font-weight: 400 800; font-display: swap;
  src: url("__PISMA__schibsted-grotesk-latin.woff2") format("woff2");
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD; }
@font-face { font-family: "Schibsted Grotesk"; font-style: normal; font-weight: 400 800; font-display: swap;
  src: url("__PISMA__schibsted-grotesk-latin-ext.woff2") format("woff2");
  unicode-range: U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C4, U+2113, U+2C60-2C7F, U+A720-A7FF; }
@font-face { font-family: "Sofia Sans Extra Condensed"; font-style: normal; font-weight: 500 800; font-display: swap;
  src: url("__PISMA__sofia-sans-extra-condensed-latin.woff2") format("woff2");
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD; }
@font-face { font-family: "Sofia Sans Extra Condensed"; font-style: normal; font-weight: 500 800; font-display: swap;
  src: url("__PISMA__sofia-sans-extra-condensed-latin-ext.woff2") format("woff2");
  unicode-range: U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C4, U+2113, U+2C60-2C7F, U+A720-A7FF; }
</style>'''
PISMA_GOOGLE = '''<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Schibsted+Grotesk:wght@400..800&family=Sofia+Sans+Extra+Condensed:wght@500..800&display=swap" rel="stylesheet">'''


STRANKA = r"""<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Labe · animace povodně</title>
__PISMA__
<script src="__DECK__"></script>
<style>
:root {
  --pozadi: #111820;
  --panel: rgba(11, 16, 22, 0.92);
  --text: #e6ebf0;
  --text2: #c8d1d9;
  --tlumene: #8b98a5;
  --cara: rgba(255, 255, 255, 0.08);
  --voda: #7cc6e4;
  --pismo: "Schibsted Grotesk", sans-serif;
  --cisla: "Sofia Sans Extra Condensed", "Schibsted Grotesk", sans-serif;
}
* { box-sizing: border-box; }
html, body { margin: 0; height: 100%; background: var(--pozadi); color: var(--text); overflow: hidden;
  font: 14px/1.4 var(--pismo); }
.datum, .cm, .pred b, .cas-text { font-family: var(--cisla); font-variant-numeric: tabular-nums; }
#mapa { position: absolute; inset: 0; }
.box { position: absolute; background: var(--panel); border: 1px solid var(--cara); border-radius: 12px; }
.veta { top: 12px; left: 12px; max-width: min(400px, calc(100% - 24px)); padding: 9px 14px; }
.veta h1 { margin: 0 0 4px; font: 800 24px/1 var(--cisla); letter-spacing: 0; }
.veta p { margin: 0; color: var(--tlumene); font-size: 13.5px; }
.legenda { left: 12px; bottom: 70px; max-width: calc(100% - 24px); padding: 6px 10px; font-size: 12.5px;
  color: var(--tlumene); }
.legenda i { display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin: 0 4px 0 6px; vertical-align: -1px; }
.panel { top: 12px; right: 12px; width: 300px; padding: 12px 14px 10px; }
.datum { font-size: 26px; font-weight: 800; letter-spacing: 0.01em; line-height: 1.1; }
.mesto { margin-top: 10px; padding-top: 8px; border-top: 1px solid var(--cara); }
.radek { display: flex; align-items: baseline; gap: 8px; }
.jmeno { font-weight: 600; flex: 1; color: var(--text2); }
.cm { font-size: 24px; font-weight: 800; }
.odznak { font-size: 11.5px; font-weight: 700; padding: 2px 7px; border-radius: 6px; white-space: nowrap; }
.odznak.bez { background: none !important; color: var(--text2) !important; box-shadow: inset 0 0 0 1px rgba(230, 235, 240, 0.2); }
.pred { margin-top: 3px; font-size: 13px; color: var(--tlumene); display: flex; align-items: baseline; gap: 6px; flex-wrap: wrap; }
.pred b { color: var(--voda); font-size: 18px; font-weight: 800; }
canvas#graf { display: block; width: 100%; height: 104px; margin-top: 10px; cursor: pointer; }
.popis { font-size: 12px; color: var(--tlumene); margin-top: 4px; }
.popis span { white-space: nowrap; }
.ovladani { left: 12px; right: 12px; bottom: 12px; display: flex; align-items: center; gap: 12px; padding: 8px 12px; }
button#hraj { flex: none; width: 44px; height: 44px; border-radius: 50%; border: 0; background: #3aa0c9;
  color: #0b1016; cursor: pointer; display: grid; place-items: center; }
button#hraj:hover { background: var(--voda); }
button#hraj:active { transform: scale(0.96); }
button#hraj svg { width: 18px; height: 18px; fill: currentColor; }
input#cas { flex: 1; min-width: 80px; height: 28px; margin: 0; accent-color: #3aa0c9; }
.cas-text { flex: none; min-width: 150px; font-size: 17px; font-weight: 700; }
select { background: transparent; color: var(--text); border: 1px solid var(--cara); border-radius: 6px; padding: 4px 6px; font: inherit; }
select option { color: #111; }
.zdroj { position: absolute; right: 14px; bottom: 72px; max-width: 40%; text-align: right; font-size: 11px;
  color: rgba(255, 255, 255, 0.75); text-shadow: 0 0 3px #000; text-wrap: balance; }
.zdroj span { display: block; }
@media (max-width: 720px) {
  .panel { top: auto; bottom: 76px; right: 12px; left: 12px; width: auto; padding: 8px 12px 6px; }
  .veta { padding: 7px 12px; }
  .veta h1 { font-size: 20px; }
  .veta p, .legenda, .zdroj, canvas#graf, .popis, .pred, .cas-text { display: none; }
  .datum { font-size: 20px; }
  .mesto { margin-top: 5px; padding-top: 4px; }
  .cm { font-size: 20px; }
  .ovladani { padding: 8px 10px; gap: 8px; }
}
</style>
</head>
<body>
<div id="mapa"></div>
<div class="box veta">
  <h1>Co teče proti proudu, dorazí k nám.</h1>
  <p>Kapka nese průtok ze stanice proti proudu: víc vody, víc a jasnějších kapek.</p>
</div>
<div class="box legenda" id="legenda"></div>
<div class="box panel">
  <div class="datum" id="datum"></div>
  <div class="mesto" id="mesta"></div>
  <canvas id="graf" title="Kliknutím skočíte na ten čas"></canvas>
  <div class="popis"><span>Děčín: <b style="color:#eef3f6">změřeno</b>,</span>
    <span><b style="color:var(--voda)">předpověď na 24 h</b></span> <span>(čárkovaně stupně)</span></div>
</div>
<div class="zdroj" id="zdroj"></div>
<div class="box ovladani">
  <button id="hraj" aria-label="Přehrát nebo zastavit"></button>
  <input id="cas" type="range" min="0" step="0.01" aria-label="Čas">
  <div class="cas-text" id="cas-text"></div>
  <select id="rychlost" aria-label="Rychlost">
    <option value="1">1 h za s</option><option value="2">2 h za s</option>
    <option value="4" selected>4 h za s</option><option value="8">8 h za s</option><option value="16">16 h za s</option>
  </select>
</div>
<script>
const D = __DATA__;
const N = D.nabeh, K = D.konec, S = D.stanice, U = D.useky, SAT = D.teren.satelit;
const PODLE = Object.fromEntries(S.map(s => [s.klic, s]));
const STUPNE = ['bez stupně', '1. stupeň', '2. stupeň', '3. stupeň'];
const IKONA = {
  hraj: '<svg viewBox="0 0 24 24"><path d="M7 4.5v15l13-7.5z"/></svg>',
  stuj: '<svg viewBox="0 0 24 24"><path d="M6 4h4.5v16H6zM13.5 4H18v16h-4.5z"/></svg>'
};
const HUSTOTA = 0.9;  // kapek na kilometr toku při velké vodě
const OCAS = 0.6;     // délka stopy kapky v hodinách cesty

// hodnota řady v čase t (hodiny od začátku okna, i desetinné), mezi hodinami lineárně
function rada(r, t) {
  const x = Math.min(Math.max(t + N, 0), r.length - 1);
  const i = Math.floor(x), j = Math.min(i + 1, r.length - 1), w = x - i;
  if (r[i] == null || r[j] == null) return r[i] ?? r[j];
  return r[i] + (r[j] - r[i]) * w;
}
const omez = (x, a, b) => Math.min(Math.max(x, a), b);
const cislo = v => v == null ? '–' : Math.round(v).toLocaleString('cs-CZ');
// 0 = běžný průtok (medián), 1 = 99. percentil a víc
const uroven = (klic, q) => q == null ? 0 : omez((q - PODLE[klic].q50) / (PODLE[klic].p99 - PODLE[klic].q50), 0, 1);

function stupen(s, t) {
  if (s.spa) {
    const h = rada(D.H[s.klic], t);
    return h == null ? null : s.spa.filter(m => h >= m).length;
  }
  const q = rada(D.Q[s.klic], t);
  return q == null ? null : q >= s.p99 ? 3 : q >= s.p95 ? 1 : 0;
}
const stupenH = (klic, h) => h == null ? null : PODLE[klic].spa.filter(m => h >= m).length;
const barvaStupne = st => st == null ? D.seda : D.barvy[st];
const css = (c, a = 1) => `rgba(${c[0]},${c[1]},${c[2]},${a})`;

// geometrie úseků: kolmice k toku kvůli šířce proudu kapek
for (const u of U) {
  u.delka = u.vzdal[u.vzdal.length - 1];
  u.bok = [];
  for (let i = 0; i < u.cesta.length - 1; i++) {
    const [x1, y1] = u.cesta[i], [x2, y2] = u.cesta[i + 1];
    const kx = 111320 * Math.cos(y1 * Math.PI / 180), ky = 110540;
    const dx = (x2 - x1) * kx, dy = (y2 - y1) * ky, l = Math.hypot(dx, dy) || 1;
    u.bok.push([-dy / l / kx, dx / l / ky]);
  }
}
function bod(u, f, bok) {
  const d = f * u.delka, v = u.vzdal;
  let a = 0, b = v.length - 1;
  while (b - a > 1) { const m = (a + b) >> 1; if (v[m] <= d) a = m; else b = m; }
  const p = u.cesta[a], q = u.cesta[b], w = (d - v[a]) / ((v[b] - v[a]) || 1), n = u.bok[a];
  return [p[0] + (q[0] - p[0]) * w + n[0] * bok, p[1] + (q[1] - p[1]) * w + n[1] * bok, p[2] + (q[2] - p[2]) * w];
}

const kapky = [];
U.forEach((u, iu) => {
  const pocet = Math.ceil(u.delka / 1000 * HUSTOTA);
  for (let k = 0; k < pocet; k++) {
    kapky.push({u: iu, faze: (k + Math.random()) / pocet, prah: Math.random(), bok: Math.random() * 2 - 1});
  }
});

// Kapka na místě f úseku vyjela ze stanice proti proudu před f * doba hodinami a nese průtok z té chvíle.
function kapkyTed(t) {
  const out = [];
  for (const k of kapky) {
    const u = U[k.u];
    const f = (((k.faze + t / u.doba) % 1) + 1) % 1;
    const q = rada(D.Q[u.od], t - f * u.doba);
    if (q == null) continue;
    const l = uroven(u.od, q);
    if (k.prah > 0.3 + 0.7 * l) continue;
    const bok = k.bok * (120 + 520 * l);
    out.push({hlava: bod(u, f, bok), ocas: bod(u, Math.max(0, f - OCAS / u.doba), bok), l});
  }
  return out;
}
const [SVETLA, TMAVA] = SAT ? [[95, 175, 245], [235, 250, 255]] : [[80, 150, 225], [0, 45, 160]];
function barvaKapky(l, a) {
  return [0, 1, 2].map(i => SVETLA[i] + (TMAVA[i] - SVETLA[i]) * l).concat(255 * a * (0.5 + 0.5 * l));
}

// popisky stanic, které jsou u soutoku Vltavy a Labe blízko sebe, odsuneme do stran
const UZKE = innerWidth < 720;  // telefon: jen jména stanic, menším písmem
const KRATCE = UZKE ? {kostelec: 'Kostelec n. L.', praha: 'Praha', usti: 'Ústí n. L.'} : {kostelec: 'Kostelec n. L.', praha: 'Praha-Chuchle'};
const KOTVA = {vranany: 'end', kostelec: 'pod', prelouc: 'pod'};
const POSUN = {end: [-9, 0], start: [9, 0], pod: [0, 9], middle: [0, -10]};
// při malém zoomu by se popisky blízkých stanic překrývaly: ty schováme, Ústí a Děčín rozdělíme do stran
const ZOOM0 = 8.15 + Math.max(-1.3, Math.log2(Math.min(1, innerWidth / 1270)));
const MALY_ZOOM = 8;
const BLIZKE = new Set(['vranany', 'kostelec', 'jizera', 'beroun', 'sazava']);
const STRANOU = {usti: 'end', decin: 'start'};
const S_MALY = S.filter(s => !BLIZKE.has(s.klic));
let maly = ZOOM0 < MALY_ZOOM;
const kotva = s => (maly && STRANOU[s.klic]) || KOTVA[s.klic];
const vrchol = (s, t) => s.z + (KOTVA[s.klic] === 'pod' ? 0 : (rada(D.Q[s.klic], t) ?? 0) * D.meritko);
function popisek(s, t) {
  const jmeno = KRATCE[s.klic] ?? s.nazev;
  if (UZKE) return jmeno;
  if (s.spa) return `${jmeno}\n${cislo(rada(D.H[s.klic], t))} cm`;
  const q = rada(D.Q[s.klic], t);
  return `${jmeno}\n${cislo(q)}${q == null ? '' : ' m³/s'}`;
}

const NAVRCH = {depthCompare: 'always', depthWriteEnabled: false};
const teren = new deck.TerrainLayer({
  id: 'teren',
  elevationData: D.teren.vysky,
  texture: D.teren.povrch,
  elevationDecoder: D.teren.dekoder,
  tileSize: 256, minZoom: 0, maxZoom: 14,
  extent: [12.8, 49.2, 16.5, 51.4],
  meshMaxError: 8,
  material: {ambient: 0.6, diffuse: 0.6, shininess: 12},
  pickable: false
});

function vrstvy(t) {
  const kap = kapkyTed(t);
  return [
    teren,
    new deck.PathLayer({
      id: 'reky', data: U, getPath: u => u.cesta,
      getWidth: u => 2 + 5 * uroven(u.od, rada(D.Q[u.od], t)),
      widthUnits: 'pixels', jointRounded: true, capRounded: true,
      getColor: SAT ? [70, 150, 230, 120] : [40, 110, 200, 130],
      parameters: NAVRCH, updateTriggers: {getWidth: t}
    }),
    new deck.LineLayer({
      id: 'stopy', data: kap, getSourcePosition: k => k.ocas, getTargetPosition: k => k.hlava,
      getColor: k => barvaKapky(k.l, 0.45), getWidth: k => 1.2 + 1.8 * k.l, widthUnits: 'pixels',
      parameters: NAVRCH
    }),
    new deck.ScatterplotLayer({
      id: 'kapky', data: kap, getPosition: k => k.hlava,
      getRadius: k => 1.3 + 1.9 * k.l, radiusUnits: 'pixels',
      getFillColor: k => barvaKapky(k.l, 1), parameters: NAVRCH
    }),
    new deck.ColumnLayer({
      id: 'stanice', data: S, getPosition: s => [s.lon, s.lat, s.z],
      getElevation: s => rada(D.Q[s.klic], t) ?? 0, elevationScale: D.meritko,
      getFillColor: s => barvaStupne(stupen(s, t)),
      radius: 800, diskResolution: 20, extruded: true, pickable: true, autoHighlight: true,
      updateTriggers: {getElevation: t, getFillColor: t}
    }),
    new deck.TextLayer({
      id: 'popisky', data: maly ? S_MALY : S,
      getPosition: s => [s.lon, s.lat, vrchol(s, t)],
      getText: s => popisek(s, t), getSize: UZKE ? 10 : 15, fontWeight: 600,
      fontFamily: '"Schibsted Grotesk", sans-serif', characterSet: 'auto',
      getColor: SAT ? [255, 255, 255] : [25, 35, 45],
      getTextAnchor: s => ({end: 'end', start: 'start'})[kotva(s)] ?? 'middle',
      getPixelOffset: s => POSUN[kotva(s) ?? 'middle'],
      getAlignmentBaseline: s => ({end: 'center', start: 'center', pod: 'top'})[kotva(s)] ?? 'bottom',
      outlineWidth: SAT ? 2 : 1.5, outlineColor: SAT ? [15, 25, 35, 240] : [255, 255, 255, 230],
      fontSettings: {sdf: true}, parameters: NAVRCH,
      updateTriggers: {getPosition: t, getText: t, getTextAnchor: maly, getPixelOffset: maly, getAlignmentBaseline: maly}
    })
  ];
}

function tooltip({object, layer}) {
  if (!object || !layer || layer.id !== 'stanice') return null;
  const s = object, q = rada(D.Q[s.klic], cas);
  let text = `${s.nazev} · ${s.tok}\nPrůtok: ${cislo(q)} m³/s`;
  if (s.spa) {
    const st = stupen(s, cas);
    text += `\nHladina: ${cislo(rada(D.H[s.klic], cas))} cm\n${st == null ? 'stupeň nelze určit' : STUPNE[st]}`;
  } else {
    text += `\n95. / 99. percentil: ${cislo(s.p95)} / ${cislo(s.p99)} m³/s\nBarva není oficiální povodňový stupeň.`;
  }
  return {text, style: {backgroundColor: '#1a232d', color: '#e6ebf0', fontSize: '14px', fontFamily: 'var(--pismo)', borderRadius: '8px'}};
}

// panel s hladinami a předpovědí
const MESTA = [['decin', 'Děčín'], ['usti', 'Ústí nad Labem']];
document.getElementById('mesta').outerHTML = MESTA.map(([k, j]) => `
  <div class="mesto">
    <div class="radek"><span class="jmeno">${j}</span><span class="cm" id="h-${k}"></span><span class="odznak" id="s-${k}"></span></div>
    <div class="pred">model za 24 h <b id="p-${k}"></b><span class="odznak" id="ps-${k}"></span><span id="sk-${k}"></span></div>
  </div>`).join('');
function odznak(el, st) {
  const c = barvaStupne(st);
  el.textContent = st == null ? 'chybí' : STUPNE[st];
  el.classList.toggle('bez', st === 0);
  el.style.background = css(c);
  el.style.color = st === 3 ? '#e6ebf0' : '#0b1016';
}
function panel(t) {
  const i = Math.floor(t) + N;
  document.getElementById('datum').textContent = D.popisky[i];
  document.getElementById('cas-text').textContent = D.popisky[i];
  for (const [k] of MESTA) {
    const h = rada(D.H[k], t), p = D.P[k][i], sk = D.H[k][i + 24];
    document.getElementById(`h-${k}`).textContent = `${cislo(h)} cm`;
    odznak(document.getElementById(`s-${k}`), stupenH(k, h));
    document.getElementById(`p-${k}`).textContent = p == null ? 'chybí vstupy' : `${cislo(p)} cm`;
    odznak(document.getElementById(`ps-${k}`), stupenH(k, p));
    document.getElementById(`sk-${k}`).textContent = sk == null ? '' : `skutečnost ${cislo(sk)} cm (známe až zpětně)`;
  }
}

// graf hladiny v Děčíně: změřená do teď plně, potom slabě; předpověď vydaná do teď o 24 h dopředu
const GRAF = document.getElementById('graf');
const HD = D.H.decin, PD = D.P.decin, SPA_D = PODLE.decin.spa;
const OD = N, DO = N + K + 24;
const hodnoty = HD.slice(OD, DO + 1).concat(PD.slice(OD, DO + 1 - 24)).filter(v => v != null);
const YMIN = Math.min(...hodnoty) - 20, YMAX = Math.max(...hodnoty, SPA_D[2]) + 20;
function graf(t) {
  const W = GRAF.clientWidth, V = GRAF.clientHeight, dpr = window.devicePixelRatio || 1;
  if (!W) return;
  if (GRAF.width !== Math.round(W * dpr)) { GRAF.width = Math.round(W * dpr); GRAF.height = Math.round(V * dpr); }
  const g = GRAF.getContext('2d');
  g.setTransform(dpr, 0, 0, dpr, 0, 0);
  g.clearRect(0, 0, W, V);
  const x = i => (i - OD) / (DO - OD) * W, y = v => V - 3 - (v - YMIN) / (YMAX - YMIN) * (V - 6);
  const ted = OD + t;
  g.lineWidth = 1;
  g.setLineDash([3, 3]);
  SPA_D.forEach((m, k) => { g.strokeStyle = css(D.barvy[k + 1], 0.8); g.beginPath(); g.moveTo(0, y(m)); g.lineTo(W, y(m)); g.stroke(); });
  g.setLineDash([]);
  const cara = (od, doo, hodnota, posun, barva, sirka) => {
    g.strokeStyle = barva; g.lineWidth = sirka; g.beginPath();
    let kresli = false;
    for (let i = od; i <= doo; i++) {
      const v = hodnota[i];
      if (v == null) { kresli = false; continue; }
      kresli ? g.lineTo(x(i + posun), y(v)) : g.moveTo(x(i + posun), y(v));
      kresli = true;
    }
    g.stroke();
  };
  cara(OD, DO, HD, 0, 'rgba(230,235,240,0.25)', 1.5);
  cara(OD, Math.floor(ted), HD, 0, '#e6ebf0', 2);
  cara(OD, Math.floor(ted), PD, 24, '#7cc6e4', 2);
  const p = PD[Math.floor(ted)];
  g.strokeStyle = 'rgba(255,255,255,0.55)'; g.lineWidth = 1;
  g.beginPath(); g.moveTo(x(ted), 0); g.lineTo(x(ted), V); g.stroke();
  if (p != null) {
    g.fillStyle = '#7cc6e4'; g.beginPath(); g.arc(x(Math.floor(ted) + 24), y(p), 4, 0, 2 * Math.PI); g.fill();
  }
}
GRAF.addEventListener('click', e => {
  const r = GRAF.getBoundingClientRect();
  nastav(omez((e.clientX - r.left) / r.width * (K + 24), 0, K));
});

// legenda a zdroje
const B = D.barvy;
const ctverec = c => `<i style="background:${css(c)}"></i>`;
document.getElementById('legenda').innerHTML =
  `<div>Sloupec: výška je průtok, barva stupeň povodňové aktivity.</div>` +
  `<div>Děčín, Ústí: ${ctverec(B[0])}bez stupně ${ctverec(B[1])}1. ${ctverec(B[2])}2. ${ctverec(B[3])}3. stupeň</div>` +
  `<div>Ostatní: ${ctverec(B[0])}běžně ${ctverec(B[1])}nad 95. ${ctverec(B[3])}nad 99. percentilem průtoku</div>`;
// dva řádky: zdroje dat a model; užší okno každý zalomí na vyrovnané půlky
document.getElementById('zdroj').innerHTML =
  `<span>${[D.teren.zdroj, 'Řeky © OpenStreetMap', 'Měření ČHMÚ'].map(t => t.replaceAll(' ', '\u00a0')).join('\u00a0· ')}</span>` +
  `<span>Předpověď: ${D.nazev_modelu}</span>`;

// přehrávání
const posuvnik = document.getElementById('cas'), tlacitko = document.getElementById('hraj');
posuvnik.max = K;
let cas = 0, hraje = true, rychlost = 4, minule = null, nakresleno = -1, tahne = false;
const mapa = new deck.Deck({
  parent: document.getElementById('mapa'),
  initialViewState: {longitude: 14.78, latitude: 50.27, pitch: 50, bearing: 0, minZoom: 6, maxZoom: 14, zoom: ZOOM0},
  controller: true,
  onViewStateChange: ({viewState}) => {
    if ((viewState.zoom < MALY_ZOOM) !== maly) { maly = !maly; nakresleno = -1; }
  },
  getTooltip: tooltip,
  layers: []
});
function ikona() { tlacitko.innerHTML = hraje ? IKONA.stuj : IKONA.hraj; }
function nastav(t) { cas = t; nakresleno = -1; }
function prepni() {
  if (!hraje && cas >= K) cas = 0;
  hraje = !hraje; minule = null; ikona();
}
tlacitko.addEventListener('click', prepni);
posuvnik.addEventListener('input', () => nastav(+posuvnik.value));
posuvnik.addEventListener('pointerdown', () => { tahne = true; });
window.addEventListener('pointerup', () => { tahne = false; });
document.getElementById('rychlost').addEventListener('change', e => { rychlost = +e.target.value; });
document.addEventListener('keydown', e => {
  if (e.code === 'Space' && !['SELECT', 'BUTTON'].includes(e.target.tagName)) { e.preventDefault(); prepni(); }
});
function snimek(ts) {
  if (hraje && minule != null) {
    cas = Math.min(cas + (ts - minule) / 1000 * rychlost, K);
    if (cas >= K) { hraje = false; ikona(); }
  }
  minule = hraje ? ts : null;
  if (cas !== nakresleno) {
    mapa.setProps({layers: vrstvy(cas)});
    if (Math.floor(cas) !== Math.floor(nakresleno) || nakresleno < 0) panel(cas);
    graf(cas);
    if (!tahne) posuvnik.value = cas;
    nakresleno = cas;
  }
  requestAnimationFrame(snimek);
}
ikona();
panel(0);
// popisky stanic kreslí deck.gl do atlasu jednou, proto se čeká, až se písmo načte (nejvýš 1,5 s)
const pismo = document.fonts ? Promise.race([document.fonts.load('600 15px "Schibsted Grotesk"'), new Promise(r => setTimeout(r, 1500))])
  : Promise.resolve();
pismo.catch(() => {}).then(() => requestAnimationFrame(snimek));
</script>
</body>
</html>
"""


def main():
    st.set_page_config(page_title="Povodeň na Labi · animace", layout="wide")
    povoden = st.selectbox("Povodeň", list(POVODNE), index=3)
    od, do = okno(povoden)
    # novější Streamlit má st.iframe a components.html hlásí jako zastaralé, starší st.iframe nemá
    getattr(st, "iframe", components.html)(html(od, do), height=720)
    st.caption("Okno je 14 dní před vrcholem hladiny v Děčíně a 5 dní po něm. Mezerníkem spustíte a zastavíte, "
               "kolečkem přiblížíte, tažením posunete, Shift a tažením natočíte mapu. Terén je zvýšený 2,5×, "
               "1 m³/s průtoku je 5 m výšky sloupce.")


if __name__ == "__main__":
    if sys.argv[1:] == ["reky"]:
        postav_reky()
    else:
        main()
