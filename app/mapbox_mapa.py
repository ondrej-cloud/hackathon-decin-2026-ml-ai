r"""3D mapa povodí v Mapbox GL JS ve stylu Mapbox Standard: terén, 3D budovy a stromy, osvětlení, stanice a rozliv.

Proti pydeck mapě v mapa.py (ta zůstává jako záloha) jsou dobře vidět malá území: rozliv leží přímo na terénu,
budovy v Děčíně a Ústí stojí ve vodě a ulice mají ostré popisky. Potřebuje MAPBOX_TOKEN v .env.

Ukázka z kořene repozitáře:
    .venv\Scripts\python -m streamlit run app/mapbox_mapa.py --server.port 8506
V aplikaci (stejné argumenty jako mapa.deck):
    st.iframe(mapbox_mapa.html(cas, predpovedi, pohled), height=700)
Animace povodně s porovnáním předpověď × skutečnost (od a do jako animace.okno):
    st.iframe(mapbox_mapa.html_animace(od, do, "decin", nazev, "Děčín"), height=720)
"""
import json
import math
import re
from datetime import timedelta
from functools import cache
from html import escape

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

import mapa
from predikce import KDE, ROOT, SPA, nacti, nacti_model, stupen, vstupy
from rozliv import GENITIV, SOUBOR_UZEMI, n_leta_voda, n_lete

MAPBOX = "https://api.mapbox.com/mapbox-gl-js/v3.8.0"
POROVNANI = "https://api.mapbox.com/mapbox-gl-js/plugins/mapbox-gl-compare/v0.4.2"
REKY = ROOT / "data/external/reky.geojson"
MESTA = {"decin": "Děčín", "usti": "Ústí nad Labem"}
# Klíče jako mapa.POHLEDY. Města jsou natočená podél údolí Labe, ať je vidět řeka i svahy nad ní.
KAMERY = {
    "celé povodí": {"center": [14.65, 50.30], "zoom": 8, "pitch": 55, "bearing": 0},
    "Ústí nad Labem": {"center": [14.043, 50.6575], "zoom": 15.6, "pitch": 60, "bearing": 10},
    "Děčín": {"center": [14.205, 50.775], "zoom": 15.6, "pitch": 60, "bearing": -20},
}
POHLEDY = [("celé povodí", "Celé povodí", "12 stanic a řeky"), ("Ústí nad Labem", "Ústí nad Labem", "záplavové území"),
           ("Děčín", "Děčín", "záplavové území")]
OKOLI_DEM = 50  # cm; do animace jdou jen polygony hladin, které okno povodně potřebuje
MAX_DEM = 4_000_000  # bajtů; když je jich víc, vložíme jen hladiny po 20 cm


def _soubor_dem(cil):
    return ROOT / f"data/external/rozliv_dem_{cil}.geojson"


@cache
def _uzemi():
    """Záplavová území Q5, Q20, Q100 ve 2D, na terén je položí Mapbox sám. Aktivní zóny vynecháváme jako rozliv.vrstvy."""
    uzemi = []
    for f in json.loads(SOUBOR_UZEMI.read_text(encoding="utf-8"))["features"]:
        p = f["properties"]
        if p["typ"] == "záplavové území":
            souradnice = [[[c[:2] for c in kruh] for kruh in poly] for poly in f["geometry"]["coordinates"]]
            uzemi.append((p["N"], p["usek"], souradnice))
    return uzemi


@cache
def _dem(cil):
    """Rozliv z výškového modelu (app/rozliv_dem.py) po 10 cm seřazený podle hladiny, nebo None, když soubor ještě není."""
    soubor = _soubor_dem(cil)
    if not soubor.exists():
        return None
    prvky = json.loads(soubor.read_text(encoding="utf-8"))["features"]
    return sorted(({"h": f["properties"]["hladina_cm"], "ha": round(f["properties"]["plocha_ha"]), "g": f["geometry"]}
                   for f in prvky), key=lambda u: u["h"])


def _dem_pro(cil, cm):
    """Rozliv z výškového modelu s nejbližší hladinou (nový slovník, cache se nemění)."""
    return dict(min(_dem(cil), key=lambda u: abs(u["h"] - cm)))


def _plocha_ha(multipolygon):
    """Plocha v ha; na pár kilometrech stačí rovinné souřadnice (jako animace._metry)."""
    plocha = 0.0
    for poly in multipolygon:
        for i, kruh in enumerate(poly):
            xy = [(lon * 111320 * math.cos(math.radians(lat)), lat * 110540) for lon, lat in kruh]
            s = abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(xy, xy[1:] + xy[:1]))) / 2
            plocha += -s if i else s
    return plocha / 10_000


def _veta(cil, cm):
    return re.sub(r"(\d) (\d{3})", "\\1\u00a0\\2", n_leta_voda(cil, cm)["popis"])  # tisíce se nezalomí


def _stanice(cas, predpovedi):
    prvky = []
    for b in mapa._stanice(cas, predpovedi):
        lon, lat, _ = b["pozice"]
        prvky.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [lon, lat]}, "properties": {
            "prutok": round(b["prutok"], 1), "barva": "rgb({},{},{})".format(*b["barva"]), "popisek": b["popisek"],
            "tooltip": escape(b["tooltip"]).replace("\n", "<br>"),
        }})
    return {"type": "FeatureCollection", "features": prvky}


def _mesta(cas, predpovedi):
    """Hladina teď a předpověď pro panel; N je záplavové území, které se vyplní (největší dosažené z Q5, Q20, Q100)."""
    radek = nacti().loc[cas]
    mesta = []
    for cil, nazev in MESTA.items():
        h = radek[f"{cil}_H"]
        m = {"klic": cil, "nazev": nazev, "hladina": None if pd.isna(h) else round(float(h)),
             "stupen": None if pd.isna(h) else int(stupen(cil, h)), "predpoved": None, "N": None, "dem": None, "skut": None,
             "veta": "Pro tuhle hodinu nemáme předpověď.", "uzemi": "Záplavová území jsou jen obrysem."}
        if predpovedi and cil in predpovedi:
            hor, cm = predpovedi[cil]
            zony = [N for N in (5, 20, 100) if N <= n_leta_voda(cil, cm)["N"]]
            m["N"] = zony[-1] if zony else None
            m["predpoved"] = {"h": hor, "cm": round(cm), "stupen": stupen(cil, cm)}
            m["veta"] = f"Předpověď za {hor} h: {_veta(cil, cm)}"
            m["uzemi"] = (f"Vyplněné je záplavové území {GENITIV[m['N']]} vody (Q{m['N']})." if m["N"] else
                          "Záplavová území Q5, Q20 a Q100 jsou jen obrysem.")
            if _dem(cil):
                m["dem"] = _dem_pro(cil, cm)
                skut = nacti()[f"{cil}_H"].get(cas + pd.Timedelta(hours=hor))  # v archivu víme, co pak nastalo
                if skut is not None and pd.notna(skut):
                    m["skut"] = {"cm": round(float(skut))} | _dem_pro(cil, skut)
        mesta.append(m)
    return mesta


def _zaplavy(mesta, usek=None):
    plne = {m["klic"]: m["N"] for m in mesta}
    q = n_lete().set_index(["klic", "N"]).Q_m3s
    prvky = []
    for N, u, souradnice in _uzemi():
        if usek and u != usek:
            continue
        tooltip = (f"Záplavové území {GENITIV[N]} vody (Q{N} = {mapa._cislo(q[u, N])} m³/s "
                   f"{'v Děčíně' if u == 'decin' else 'v Ústí'})<br>DIBAVOD, VÚV TGM; průběh je orientační")
        if N == plne.get(u):
            tooltip += "<br>Odpovídá předpovědi modelu"
        prvky.append({"type": "Feature", "geometry": {"type": "MultiPolygon", "coordinates": souradnice},
                      "properties": {"N": N, "plne": N == plne.get(u), "tooltip": tooltip}})
    prvky.sort(key=lambda f: f["properties"]["plne"])  # vyplněné území navrch
    return {"type": "FeatureCollection", "features": prvky}


def _popisek_casu(cas):
    t = cas.tz_convert(mapa.PASMO)
    return f"{t.day}. {t.month}. {t.year} {t:%H:%M} {'SELČ' if t.dst() else 'SEČ'}"


def _rada(hodnoty, mist=0):
    return [None if pd.isna(v) else round(float(v), mist) for v in hodnoty]


def _stranka(data, porovnani=False):
    data = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    plugin = (f'<link href="{POROVNANI}/mapbox-gl-compare.css" rel="stylesheet">\n'
              f'<script src="{POROVNANI}/mapbox-gl-compare.js"></script>') if porovnani else ""
    return STRANKA.replace("__MAPBOX__", MAPBOX).replace("__POROVNANI__", plugin).replace("__DATA__", data)


def _spolecne(token, pohled):
    return {"token": token, "kamery": KAMERY, "pohled": pohled, "pohledy": POHLEDY, "barvy": mapa.BARVY,
            "seda": mapa.SEDA, "reky": json.loads(REKY.read_text(encoding="utf-8"))}


def html(cas, predpovedi=None, pohled="celé povodí") -> str:
    """Stránka s mapou pro st.iframe(..., height=700); argumenty jako mapa.deck (čas bez pásma = český čas)."""
    token = mapa.mapbox_token()
    if not token:
        return BEZ_TOKENU
    cas = mapa._cas_utc(cas)
    mesta = _mesta(cas, predpovedi)
    # rozliv z terénu jen pro předpovězenou hladinu a pro tu, která pak opravdu nastala
    dem, skut = [], []
    for m in mesta:
        if m["dem"]:
            dem.append({"type": "Feature", "geometry": m["dem"].pop("g"), "properties": {
                "tooltip": f"Rozliv z výškového modelu (ČÚZK DMR 5G) pro předpověď {m['predpoved']['cm']} cm "
                           f"{KDE[m['klic']]}: {m['dem']['ha']} ha<br>Statický rozliv, bez proudění a hrází"}})
        if m["skut"]:
            skut.append({"type": "Feature", "geometry": m["skut"].pop("g"), "properties": {}})
    data = _spolecne(token, pohled) | {
        "datum": _popisek_casu(cas), "mesta": mesta, "stanice": _stanice(cas, predpovedi), "uzemi": _zaplavy(mesta),
        "dem": {"type": "FeatureCollection", "features": dem} if dem else None,
        "skut": {"type": "FeatureCollection", "features": skut},
    }
    return _stranka(data)


def html_animace(od, do, cil="decin", model="ridge", pohled="Děčín") -> str:
    """Animace povodně od `od` do `do` (UTC, jako animace.okno) pro st.iframe(..., height=720).

    V každé hodině: naměřená hladina v cíli, předpověď modelu models/<model>_<cil>_24.joblib vydaná o 24 h dřív
    pro tutéž hodinu a průtoky stanic. Rozliv z výškového modelu (rozliv_dem_<cil>.geojson), když existuje,
    přepínačem (a bez něj vždy) záplavová území DIBAVOD Q5, Q20, Q100 podle N-letých hladin ČHMÚ.
    Porovnání ukáže vlevo rozliv z předpovědi a vpravo ze skutečnosti.
    """
    token = mapa.mapbox_token()
    if not token:
        return BEZ_TOKENU
    hodina = pd.Timedelta(hours=1)
    cas = pd.date_range(mapa._cas_utc(od), mapa._cas_utc(do), freq="h")
    T = nacti().reindex(cas)
    X = _vstupy(cil)
    X = X[X.index.isin(cas - 24 * hodina)]
    P = pd.Series(nacti_model(model, cil, 24).predict(X), index=X.index + 24 * hodina).reindex(cas)

    metadata, percentily = mapa._podklady()
    stanice = [{"klic": s.klic, "nazev": s.stanice, "tok": s.tok, "lon": s.lon, "lat": s.lat, "spa": SPA.get(s.klic),
                "p95": round(percentily[f"{s.klic}_Q"].iloc[0], 1), "p99": round(percentily[f"{s.klic}_Q"].iloc[1], 1)}
               for s in metadata.itertuples(index=False)]
    H, Pr = _rada(T[f"{cil}_H"]), _rada(P)

    hladiny = n_lete().query("klic == @cil").set_index("N").H_cm
    rozlivy = {"dibavod": sorted(({"h": int(hladiny[N]), "N": N, "ha": round(_plocha_ha(s)),
                                   "g": {"type": "MultiPolygon", "coordinates": s}}
                                  for N, usek, s in _uzemi() if usek == cil), key=lambda u: u["h"])}
    if _dem(cil):
        hodnoty = [v for v in H + Pr if v is not None]
        od_cm, do_cm = min(hodnoty) - OKOLI_DEM, max(hodnoty) + OKOLI_DEM
        urovne = [u for u in _dem(cil) if od_cm <= u["h"] <= do_cm] or [_dem_pro(cil, min(hodnoty))]
        if len(json.dumps(urovne)) > MAX_DEM:
            urovne = [u for u in urovne if u["h"] % 20 == 0]
        rozlivy["dem"] = urovne
    vety = {int(v): _veta(cil, v) for v in {v for v in H + Pr if v is not None}}

    data = _spolecne(token, pohled) | {
        "uzemi": _zaplavy([], cil), "anim": {
            "cil": cil, "mesto": MESTA[cil], "model": model, "popisky": [_popisek_casu(t) for t in cas],
            "H": H, "P": Pr, "spa": SPA[cil], "vety": vety, "rozlivy": rozlivy,
            "Q": {s["klic"]: _rada(T[f"{s['klic']}_Q"], 1) for s in stanice},
            "Hs": {k: _rada(T[f"{k}_H"]) for k in SPA}, "stanice": stanice,
        },
    }
    return _stranka(data, porovnani=True)


BEZ_TOKENU = """<!doctype html><html lang="cs"><meta charset="utf-8">
<body style="margin:0;padding:24px;background:#0c1720;color:#eef3f6;font:15px sans-serif">
Mapa v Mapbox GL potřebuje MAPBOX_TOKEN v souboru .env. Bez něj použijte mapu z mapa.py.</body></html>"""

STRANKA = r"""<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Labe · mapa povodně</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&display=swap" rel="stylesheet">
<link href="__MAPBOX__/mapbox-gl.css" rel="stylesheet">
<script src="__MAPBOX__/mapbox-gl.js"></script>
__POROVNANI__
<style>
:root {
  --pozadi: #0b0f13;
  --sklo: rgba(15, 20, 25, 0.92);
  --okraj: rgba(255, 255, 255, 0.08);
  --karta: rgba(255, 255, 255, 0.04);
  --karta-aktivni: rgba(255, 255, 255, 0.12);
  --text: #f3f5f7;
  --tlumene: #9aa4ad;
  --voda: #5cc2f2;
  --plne: #1e78dc;
}
* { box-sizing: border-box; }
html, body { margin: 0; height: 100%; background: var(--pozadi); color: var(--text); overflow: hidden;
  font: 14px/1.35 "Source Sans 3", sans-serif; font-variant-numeric: tabular-nums; }
#mapy, .mapa { position: absolute; inset: 0; }
#mapa-b { display: none; }
.sklo { position: absolute; background: var(--sklo); border: 1px solid var(--okraj); border-radius: 12px;
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); box-shadow: 0 8px 28px rgba(0, 0, 0, 0.35); }
.vlevo { top: 12px; left: 12px; width: 236px; padding: 11px; max-height: calc(100% - 52px); overflow: auto; }
.vpravo { top: 12px; right: 12px; width: 300px; padding: 11px 12px; max-height: calc(100% - 52px); overflow: auto; }
.vlevo::-webkit-scrollbar, .vpravo::-webkit-scrollbar { width: 6px; }
.vlevo::-webkit-scrollbar-thumb, .vpravo::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.15); border-radius: 3px; }
h2 { margin: 0 0 6px; font-size: 11px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: var(--tlumene); }
section + section { margin-top: 12px; }
button { font: inherit; color: inherit; cursor: pointer; }
button:focus-visible { outline: 2px solid var(--voda); outline-offset: 1px; }
.polozka { display: flex; align-items: center; gap: 10px; width: 100%; text-align: left; padding: 7px 9px; margin-top: 4px;
  background: var(--karta); border: 1px solid var(--okraj); border-radius: 9px;
  transition: background-color 0.15s ease-out, border-color 0.15s ease-out; }
.polozka:hover { background: rgba(255, 255, 255, 0.08); }
.polozka:active, .volba:active, .akce:active { transform: scale(0.98); }
.polozka[aria-pressed="true"] { background: var(--karta-aktivni); border-color: rgba(255, 255, 255, 0.85); }
.polozka svg { flex: none; width: 20px; height: 20px; stroke: currentColor; fill: none; stroke-width: 1.6;
  stroke-linecap: round; stroke-linejoin: round; color: var(--voda); }
.polozka b { display: block; font-weight: 600; }
.polozka small { display: block; color: var(--tlumene); font-size: 12px; }
.akce-radek { display: flex; gap: 6px; margin-top: 12px; }
.akce { flex: 1; padding: 7px 6px; font-weight: 600; font-size: 13px; background: var(--karta); border: 1px solid var(--okraj);
  border-radius: 9px; transition: background-color 0.15s ease-out; }
.akce:hover { background: rgba(255, 255, 255, 0.08); }
.akce[aria-pressed="true"] { background: var(--karta-aktivni); border-color: rgba(255, 255, 255, 0.85); }
.popis { margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--okraj); color: var(--tlumene); font-size: 12.5px; }
.popis i { display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin: 0 3px 0 5px; vertical-align: -1px; }
.popis i.plocha { border-radius: 2px; }
.mrizka { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
.mrizka.tri { grid-template-columns: 1fr 1fr 1fr; }
.volba { display: flex; align-items: center; justify-content: center; gap: 7px; padding: 6px; font-weight: 600; font-size: 13px;
  background: var(--karta); border: 1px solid var(--okraj); border-radius: 9px;
  transition: background-color 0.15s ease-out, border-color 0.15s ease-out; }
.volba:hover { background: rgba(255, 255, 255, 0.08); }
.volba[aria-pressed="true"] { background: var(--karta-aktivni); border-color: rgba(255, 255, 255, 0.85); }
.volba:disabled { opacity: 0.35; cursor: default; }
.volba svg { width: 16px; height: 16px; stroke: currentColor; fill: none; stroke-width: 1.7; stroke-linecap: round; }
.tema { flex-direction: column; gap: 5px; }
.tecky { display: flex; gap: 3px; }
.tecky span { width: 9px; height: 9px; border-radius: 50%; }
.prepinac { display: flex; align-items: center; justify-content: space-between; gap: 6px; width: 100%; padding: 3px 0;
  background: none; border: 0; font-size: 13px; white-space: nowrap; text-align: left; }
.prepinac:disabled { opacity: 0.35; cursor: default; }
.prepinac span:last-child { flex: none; width: 30px; height: 17px; border-radius: 9px; background: rgba(255, 255, 255, 0.16);
  position: relative; transition: background-color 0.15s ease-out; }
.prepinac span:last-child::after { content: ""; position: absolute; top: 2px; left: 2px; width: 13px; height: 13px;
  border-radius: 50%; background: #fff; transition: transform 0.18s cubic-bezier(0.2, 0, 0, 1); }
.prepinac[aria-checked="true"] span:last-child { background: var(--voda); }
.prepinac[aria-checked="true"] span:last-child::after { transform: translateX(13px); }
.prepinace { display: grid; grid-template-columns: 1fr 1fr; column-gap: 12px; }
.datum { font-size: 19px; font-weight: 700; letter-spacing: -0.01em; }
.radek { display: flex; align-items: baseline; gap: 7px; margin-top: 7px; }
.radek .jmeno { flex: 1; color: var(--tlumene); }
.radek .jmeno b { color: var(--text); font-weight: 600; }
.cm { font-size: 18px; font-weight: 700; }
.cm.pred { color: var(--voda); }
.odznak { font-size: 11.5px; font-weight: 600; padding: 1px 6px; border-radius: 5px; white-space: nowrap; }
.mesto + .mesto { margin-top: 6px; padding-top: 6px; border-top: 1px solid var(--okraj); }
.maly { margin-top: 2px; font-size: 12.5px; color: var(--tlumene); }
.veta { margin-top: 9px; padding-top: 8px; border-top: 1px solid var(--okraj); font-size: 12.5px; color: var(--tlumene); }
.veta b { color: var(--text); }
.srovnani { width: 100%; margin-top: 6px; border-collapse: collapse; font-size: 13px; }
.srovnani th { font-size: 11px; font-weight: 600; color: var(--tlumene); text-align: left; padding: 0 0 3px; }
.srovnani td { padding: 3px 4px 3px 0; white-space: nowrap; }
.srovnani td:first-child { color: var(--tlumene); }
.srovnani .cm { font-size: 16px; }
.srovnani .pred { color: var(--voda); }
.srovnani small { color: var(--tlumene); }
.segment { display: flex; gap: 4px; margin-top: 9px; }
.segment .volba { flex: 1; font-size: 12.5px; padding: 5px 4px; }
.ovladani { left: 260px; right: 324px; bottom: 34px; display: flex; align-items: center; gap: 10px; padding: 7px 10px; }
#hraj { flex: none; width: 36px; height: 36px; border-radius: 50%; border: 0; background: #fff; color: #0b0f13;
  display: grid; place-items: center; }
#hraj:active { transform: scale(0.95); }
#hraj svg { width: 16px; height: 16px; fill: currentColor; }
#cas { flex: 1; min-width: 60px; accent-color: var(--voda); }
#cas-text { flex: none; min-width: 150px; font-weight: 600; }
select { background: var(--karta); color: var(--text); border: 1px solid var(--okraj); border-radius: 7px; padding: 4px 5px; font: inherit; font-size: 13px; }
select option { color: #111; }
#stitky { position: absolute; top: 14px; left: 50%; display: none; pointer-events: none; z-index: 2; }
#stitky span { position: absolute; top: 0; white-space: nowrap; font-weight: 700; font-size: 13px; letter-spacing: 0.08em;
  text-transform: uppercase; padding: 4px 9px; border-radius: 7px; background: var(--sklo); border: 1px solid var(--okraj); }
#stitky span:first-child { right: 12px; color: var(--voda); }
#stitky span:last-child { left: 12px; }
.mapboxgl-compare .compare-swiper-vertical { background-color: #0f1419; box-shadow: inset 0 0 0 2px #fff, 0 4px 14px rgba(0, 0, 0, 0.4); }
.mapboxgl-popup-content { background: #151c22; color: #fff; font: 13.5px/1.4 "Source Sans 3", sans-serif;
  border-radius: 9px; padding: 10px 28px 10px 12px; border: 1px solid var(--okraj); }
.mapboxgl-popup-close-button { color: #fff; font-size: 18px; padding: 0 7px; }
.mapboxgl-popup-anchor-top .mapboxgl-popup-tip, .mapboxgl-popup-anchor-top-left .mapboxgl-popup-tip,
.mapboxgl-popup-anchor-top-right .mapboxgl-popup-tip { border-bottom-color: #151c22; }
.mapboxgl-popup-anchor-bottom .mapboxgl-popup-tip, .mapboxgl-popup-anchor-bottom-left .mapboxgl-popup-tip,
.mapboxgl-popup-anchor-bottom-right .mapboxgl-popup-tip { border-top-color: #151c22; }
.mapboxgl-popup-anchor-left .mapboxgl-popup-tip { border-right-color: #151c22; }
.mapboxgl-popup-anchor-right .mapboxgl-popup-tip { border-left-color: #151c22; }
@media (max-width: 760px) {
  .vlevo { right: 12px; width: auto; max-height: none; padding: 6px; overflow-x: auto; overflow-y: hidden; }
  .vlevo h2, .vlevo .popis, .polozka small, .nastaveni { display: none; }
  .vlevo .seznam { display: flex; gap: 4px; }
  .vlevo .seznam .polozka { width: auto; flex: none; margin: 0; }
  .vlevo section + section { margin: 0 0 0 4px; }
  .vlevo { display: flex; align-items: center; scrollbar-width: none; }
  .vlevo > * { flex: none; }
  .akce-radek { margin: 0 0 0 4px; }
  .akce { flex: none; white-space: nowrap; }
  .vpravo { top: auto; bottom: 34px; left: 12px; right: 12px; width: auto; max-height: 42%; }
  .ovladani { left: 12px; right: 12px; bottom: calc(34px + 42% + 8px); }
  #cas-text { min-width: 0; font-size: 12px; }
}
</style>
</head>
<body>
<div id="mapy"><div class="mapa" id="mapa"></div><div class="mapa" id="mapa-b"></div></div>
<div id="stitky"><span>Předpověď</span><span>Skutečnost</span></div>
<aside class="sklo vlevo" id="vlevo"></aside>
<aside class="sklo vpravo" id="vpravo"></aside>
<script type="application/json" id="data">__DATA__</script>
<script>
// Vlastní HTML stránky, dokud ji skript nezměnil: když iframe nepovolí celou obrazovku, otevře se v nové záložce.
const KOPIE = '<!doctype html>\n' + document.documentElement.outerHTML;
const D = JSON.parse(document.getElementById('data').textContent);
const A = D.anim;  // jen v animaci: hodinové řady
mapboxgl.accessToken = D.token;
const STAV = (() => { try { return JSON.parse(decodeURIComponent(location.hash.slice(1))); } catch (e) { return {}; } })();
const STUPNE = ['bez stupně', '1. stupeň', '2. stupeň', '3. stupeň'];
const css = c => `rgb(${c[0]},${c[1]},${c[2]})`;
const cislo = v => v == null ? '–' : Math.round(v).toLocaleString('cs-CZ');
const znamenko = v => v == null ? '–' : (v > 0 ? '+' : v < 0 ? '−' : '±') + Math.abs(Math.round(v)).toLocaleString('cs-CZ');
const PRAZDNE = {type: 'FeatureCollection', features: []};
const STYL = {standard: 'mapbox://styles/mapbox/standard', satelit: 'mapbox://styles/mapbox/standard-satellite'};
const DEM = Boolean(A ? A.rozlivy.dem : D.dem);  // máme rozliv z výškového modelu
const ATRIBUCE = 'Měření a N-leté průtoky © ČHMÚ · Záplavová území DIBAVOD (VÚV TGM)' +
  (DEM ? ' · Terén ČÚZK DMR 5G' : '') + ' · Řeky © OpenStreetMap';
const N = Object.assign({svetlo: 'dusk', tema: 'default', satelit: false, mista: true, poi: true, objekty: true,
                         ulice: false, uredni: false}, STAV.nast);
const uredni = () => N.uredni || !DEM;  // úřední N-letá území místo rozlivu z terénu
function nastavZdroj() {
  if (!A) return;
  A.zdroj = uredni() ? 'dibavod' : 'dem';
  A.urovne = A.rozlivy[A.zdroj];
}
nastavZdroj();
const SIROKO = innerWidth > 760;

const IKONY = {
  'celé povodí': '<path d="M4 19c3-1 3-5 6-6s4-4 3-8"/><path d="M13 5c2 2 4 2 6 1"/><circle cx="6" cy="17" r="1.6"/><circle cx="12" cy="11" r="1.6"/><circle cx="14" cy="5" r="1.6"/>',
  'mesto': '<path d="M3 20h18"/><path d="M5 20V9l5-3v14"/><path d="M10 20V4l6 3v13"/><path d="M16 20v-9l4 2v7"/>',
  'animace': '<circle cx="12" cy="12" r="9"/><path d="M10 8.5v7l5.5-3.5z"/>',
  'porovnani': '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M12 2v20"/><path d="M7 10l-2 2 2 2M17 10l2 2-2 2"/>',
  'dawn': '<path d="M4 18h16"/><path d="M7 18a5 5 0 0 1 10 0"/><path d="M12 6v3M5.6 10.6l1.5 1.5M18.4 10.6l-1.5 1.5"/>',
  'day': '<circle cx="12" cy="12" r="4"/><path d="M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6l1.4 1.4M17 17l1.4 1.4M5.6 18.4L7 17M17 7l1.4-1.4"/>',
  'dusk': '<path d="M4 18h16"/><path d="M7 18a5 5 0 0 1 10 0"/><path d="M12 11V6M10 8l2-2 2 2"/>',
  'night': '<path d="M19 14.5A7.5 7.5 0 0 1 9.5 5a7.5 7.5 0 1 0 9.5 9.5z"/>'
};
const svg = (d, vb = 24) => `<svg viewBox="0 0 ${vb} ${vb}" aria-hidden="true">${d}</svg>`;

function kamera(pohled) {
  // střed záběru mezi panely; celé povodí se musí vejít i do užšího okna
  const k = {...D.kamery[pohled], padding: SIROKO ? {top: 0, bottom: 40, left: 250, right: 315} : {top: 60, bottom: 220, left: 0, right: 0}};
  if (pohled === 'celé povodí') k.zoom += Math.max(-1.3, Math.log2(Math.min(1, innerWidth / 1350)));
  return k;
}
function konfigurace(satelit) {
  const c = {lightPreset: N.svetlo, showPlaceLabels: N.mista, showPointOfInterestLabels: N.poi, showTransitLabels: N.poi,
             showRoadLabels: N.ulice};
  if (!satelit) Object.assign(c, {theme: N.tema, show3dObjects: N.objekty});
  return c;
}

// ---------- mapy a naše vrstvy ----------
function vytvorMapu(kontejner, k) {
  const m = new mapboxgl.Map({
    container: kontejner, style: STYL[N.satelit ? 'satelit' : 'standard'], config: {basemap: konfigurace(N.satelit)},
    center: k.center, zoom: k.zoom, pitch: k.pitch, bearing: k.bearing, minZoom: 6, maxPitch: 80,
    attributionControl: false
  });
  m.setPadding(k.padding);
  m.addControl(new mapboxgl.AttributionControl({customAttribution: ATRIBUCE}), 'bottom-right');
  m.on('style.load', () => pridejVrstvy(m));
  klikani(m);
  for (const udalost of ['mousedown', 'touchstart', 'wheel']) m.getCanvasContainer().addEventListener(udalost, zastavOblet, {passive: true});
  return m;
}

function pridejVrstvy(m) {
  m.nacteno = true;
  for (const [klic, hodnota] of Object.entries(konfigurace(m.satelit))) m.setConfigProperty('basemap', klic, hodnota);
  m.addSource('vysky', {type: 'raster-dem', url: 'mapbox://mapbox.mapbox-terrain-dem-v1', tileSize: 512, maxzoom: 14});
  m.setTerrain({source: 'vysky', exaggeration: 1.6});

  // voda ve slotu middle: nad terénem a silnicemi, pod budovami a popisky, takže domy stojí ve vodě
  if (D.uzemi) {
    m.addSource('uzemi', {type: 'geojson', data: D.uzemi});
    m.addLayer({id: 'uzemi', type: 'fill', source: 'uzemi', slot: 'middle', paint: {
      'fill-color': ['case', ['get', 'plne'], '#1e78dc', '#7cc4ff'],
      'fill-opacity': ['case', ['get', 'plne'], 0.6, A ? 0.08 : 0.14], 'fill-emissive-strength': 0.8
    }});
    m.addLayer({id: 'uzemi-obrys', type: 'line', source: 'uzemi', slot: 'middle', paint: {
      'line-color': ['case', ['get', 'plne'], '#cfe9ff', '#8fd0ff'], 'line-emissive-strength': 1,
      'line-width': ['interpolate', ['linear'], ['zoom'], 10, 0.5, 15, 1.6], 'line-opacity': 0.7
    }});
  }
  m.addSource('rozliv', {type: 'geojson', data: A ? PRAZDNE : (D.dem ?? PRAZDNE)});
  m.addLayer({id: 'rozliv', type: 'fill', source: 'rozliv', slot: 'middle', paint: {
    'fill-color': '#1e78dc', 'fill-opacity': 0.62, 'fill-emissive-strength': 0.8}});
  m.addLayer({id: 'rozliv-obrys', type: 'line', source: 'rozliv', slot: 'middle', paint: {
    'line-color': '#d4ecff', 'line-width': ['interpolate', ['linear'], ['zoom'], 10, 0.6, 15, 1.8],
    'line-opacity': 0.85, 'line-emissive-strength': 1}});
  if (D.skut) {
    // skutečný rozliv o 24 h později čárkovaně přes předpověď (jen v archivu, kde ho známe)
    m.addSource('skutecnost', {type: 'geojson', data: D.skut});
    m.addLayer({id: 'skutecnost', type: 'line', source: 'skutecnost', slot: 'middle', paint: {
      'line-color': '#ffffff', 'line-width': 2, 'line-dasharray': [2, 1.5], 'line-opacity': 0.9, 'line-emissive-strength': 1}});
  }
  m.addSource('reky', {type: 'geojson', data: D.reky});
  m.addLayer({id: 'reky', type: 'line', source: 'reky', slot: 'middle', layout: {'line-join': 'round', 'line-cap': 'round'}, paint: {
    'line-color': '#8fd3ff', 'line-emissive-strength': 1,
    'line-width': ['interpolate', ['exponential', 1.5], ['zoom'], 7, 1.5, 10, 3, 14, 6],
    // řeky jsou zjednodušené, ve městě je přesnější podklad
    'line-opacity': ['interpolate', ['linear'], ['zoom'], 10, 0.9, 13, 0.25]
  }});
  m.addSource('stanice', {type: 'geojson', data: A ? staniceV(hodina()) : D.stanice});
  const s = ['sqrt', ['get', 'prutok']];
  // ve městě menší kolečka, ať nezakryjí rozliv
  m.addLayer({id: 'stanice', type: 'circle', source: 'stanice', slot: 'top', paint: {
    'circle-radius': ['interpolate', ['linear'], ['zoom'],
      7, ['+', 3, ['*', 0.25, s]], 11, ['+', 5, ['*', 0.5, s]], 15, ['+', 4, ['*', 0.3, s]]],
    'circle-pitch-scale': 'viewport', 'circle-emissive-strength': 1,
    'circle-color': ['get', 'barva'], 'circle-opacity': 0.92,
    'circle-stroke-color': '#ffffff', 'circle-stroke-width': 1.5
  }});
  m.addLayer({id: 'stanice-popisky', type: 'symbol', source: 'stanice', slot: 'top', layout: {
    'text-field': ['get', 'popisek'], 'text-font': ['DIN Pro Bold', 'Arial Unicode MS Bold'],
    'text-size': ['interpolate', ['linear'], ['zoom'], 7, 11, 12, 14],
    'text-variable-anchor': ['top', 'bottom', 'right', 'left'],
    // odsazení v em: poloměr kolečka / velikost písma + mezera
    'text-radial-offset': ['interpolate', ['linear'], ['zoom'],
      7, ['+', 0.62, ['*', 0.023, s]], 11, ['+', 0.72, ['*', 0.037, s]], 15, ['+', 0.64, ['*', 0.021, s]]],
    'text-justify': 'auto', 'symbol-sort-key': ['-', 0, ['get', 'prutok']]
  }, paint: {'text-color': '#ffffff', 'text-halo-color': 'rgba(10, 15, 20, 0.95)', 'text-halo-width': 1.6,
             'text-emissive-strength': 1}});
  m.klic = undefined;
  viditelnostRozlivu(m);
  if (A) obnovMapu(m, hodina());
}

function viditelnostRozlivu(m) {
  if (!m.getLayer('uzemi')) return;
  const u = uredni();
  for (const id of ['uzemi', 'uzemi-obrys']) m.setLayoutProperty(id, 'visibility', u ? 'visible' : 'none');
  if (!A) for (const id of ['rozliv', 'rozliv-obrys', 'skutecnost']) {
    if (m.getLayer(id)) m.setLayoutProperty(id, 'visibility', u ? 'none' : 'visible');
  }
}

const KLIKACI = ['stanice', 'rozliv', 'uzemi'];
// území se překrývají: přednost má stanice, pak rozliv, pak vyplněné území, pak menší N
const poradi = f => f.layer.id === 'stanice' ? 0 : f.layer.id === 'rozliv' ? 1 : f.properties.plne ? 2 : 2 + f.properties.N;
function klikani(m) {
  m.on('click', e => {
    const vrstvy = KLIKACI.filter(id => m.getLayer(id) && m.getLayoutProperty(id, 'visibility') !== 'none');
    const f = m.queryRenderedFeatures(e.point, {layers: vrstvy}).sort((a, b) => poradi(a) - poradi(b))[0];
    if (!f?.properties.tooltip) return;
    new mapboxgl.Popup({maxWidth: '330px'})
      .setLngLat(f.layer.id === 'stanice' ? f.geometry.coordinates : e.lngLat)
      .setHTML(f.properties.tooltip).addTo(m);
  });
  for (const id of KLIKACI) {
    m.on('mouseenter', id, () => { m.getCanvas().style.cursor = 'pointer'; });
    m.on('mouseleave', id, () => { m.getCanvas().style.cursor = ''; });
  }
}

const k0 = STAV.kamera ? {...kamera(STAV.pohled ?? D.pohled), ...STAV.kamera} : kamera(D.pohled);
const mapaA = vytvorMapu('mapa', k0);
mapaA.satelit = N.satelit;
let mapaB = null, porovnani = null;
const mapy = () => mapaB && rezim === 'porovnani' ? [mapaA, mapaB] : [mapaA];

// ---------- animace: hodinové řady ----------
const K = A ? A.H.length - 1 : 0;
let cas = A ? Math.min(STAV.cas ?? 0, K) : 0, rezim = A ? (STAV.rezim ?? 'animace') : null;
let podle = STAV.podle ?? 'skutecnost';  // čí hladina plní jednu mapu
const hodina = () => Math.round(cas);
const stupenH = (spa, h) => h == null ? null : spa.filter(m => h >= m).length;
const barvaStupne = st => st == null ? D.seda : D.barvy[st];

function staniceV(i) {
  return {type: 'FeatureCollection', features: A.stanice.map(s => {
    const q = A.Q[s.klic][i];
    let st, text = `${s.nazev} · ${s.tok}<br>Průtok: ${q == null ? 'chybí měření' : cislo(q) + ' m³/s'}`;
    if (s.spa) {
      const h = A.Hs[s.klic][i];
      st = stupenH(s.spa, h);
      text += `<br>Hladina: ${h == null ? 'chybí měření' : cislo(h) + ' cm'}<br>${st == null ? 'stupeň nelze určit' :
        st ? st + '. stupeň povodňové aktivity' : 'bez stupně povodňové aktivity'}`;
    } else {
      st = q == null ? null : q >= s.p99 ? 3 : q >= s.p95 ? 1 : 0;
      text += `<br>95. / 99. percentil: ${cislo(s.p95)} / ${cislo(s.p99)} m³/s<br>Barva není oficiální povodňový stupeň.`;
    }
    return {type: 'Feature', geometry: {type: 'Point', coordinates: [s.lon, s.lat]}, properties: {
      prutok: q ?? 0, barva: css(barvaStupne(st)), popisek: `${s.nazev}\n${q == null ? 'chybí' : cislo(q) + ' m³/s'}`, tooltip: text}};
  })};
}

// index úrovně rozlivu pro hladinu h: z terénu nejbližší hladina, z DIBAVOD největší dosažené území (-1 = nic)
function uroven(h) {
  if (h == null) return -1;
  const U = A.urovne;
  if (A.zdroj === 'dem') {
    let a = 0, b = U.length - 1;
    while (b - a > 1) { const c = (a + b) >> 1; if (U[c].h <= h) a = c; else b = c; }
    return Math.abs(U[a].h - h) <= Math.abs(U[b].h - h) ? a : b;
  }
  let k = -1;
  U.forEach((u, i) => { if (h >= u.h) k = i; });
  return k;
}
const hladinaMapy = (m, i) => (m === mapaB || (rezim !== 'porovnani' && podle === 'skutecnost')) ? A.H[i] : A.P[i];

function obnovMapu(m, i) {
  if (!m.getSource('stanice')) return;
  if (m.hodina !== i) { m.getSource('stanice').setData(staniceV(i)); m.hodina = i; }
  const k = uroven(hladinaMapy(m, i));
  if (k === m.klic) return;  // polygon se mění jen při změně úrovně, ne každou hodinu
  m.klic = k;
  const u = A.urovne[k];
  m.getSource('rozliv').setData(k < 0 ? PRAZDNE : {type: 'Feature', geometry: u.g, properties: {tooltip: A.zdroj === 'dem' ?
    `Rozliv z výškového modelu (ČÚZK DMR 5G) pro hladinu ${u.h} cm: ${cislo(u.ha)} ha<br>Statický rozliv, bez proudění a hrází` :
    `Záplavové území Q${u.N} (DIBAVOD, VÚV TGM): ${cislo(u.ha)} ha<br>Vyplní se od hladiny ${u.h} cm podle ČHMÚ`}});
}

// ---------- levý panel ----------
let pohled = STAV.pohled ?? D.pohled;
function polozka(id, nazev, podtitul, ikona) {
  return `<button class="polozka" data-id="${id}">${svg(ikona)}<span><b>${nazev}</b><small>${podtitul}</small></span></button>`;
}
document.getElementById('vlevo').innerHTML = `
  <section><h2>Pohledy</h2><div class="seznam" id="pohledy">${D.pohledy.map(([id, nazev, podtitul]) =>
    polozka(id, nazev, podtitul, id === 'celé povodí' ? IKONY[id] : IKONY.mesto)).join('')}</div></section>
  ${A ? `<section><h2>Povodeň</h2><div class="seznam" id="rezimy">
    ${polozka('animace', 'Animace povodně', 'čas běží po hodinách', IKONY.animace)}
    ${polozka('porovnani', 'Porovnání', 'předpověď × skutečnost', IKONY.porovnani)}</div></section>` : ''}
  <div class="akce-radek"><button class="akce" id="oblet" aria-pressed="false">Obletět</button>
    <button class="akce" id="cela">Celá obrazovka</button></div>
  <div class="popis" id="popis"></div>`;
const B = D.barvy, kruh = c => `<i style="background:${css(c)}"></i>`;
function popis() {
  document.getElementById('popis').innerHTML = (A ?
    `Voda v ${A.mesto === 'Děčín' ? 'Děčíně' : 'Ústí'}: ${uredni() ? 'úřední záplavové území Q5, Q20 nebo Q100 (DIBAVOD), které hladina dosáhla' :
     'rozliv z výškového modelu terénu pro hladinu v té hodině'}. Porovnání: vlevo z předpovědi vydané o 24 h dřív, vpravo ze změřené hladiny.` :
    uredni() ? 'Modře úřední záplavové území (DIBAVOD) pro N-letou vodu, kterou dosáhne předpověď na 24 h.' :
    'Modře rozliv z výškového modelu terénu pro předpověď na 24 h, čárkovaně pro hladinu, která pak opravdu nastala.') +
    `<br>Stanice: velikost je průtok, barva stupeň: ${kruh(B[0])}bez ${kruh(B[1])}1. ${kruh(B[2])}2. ${kruh(B[3])}3.`;
}
popis();

function oznac(id, hodnota) {
  for (const b of document.querySelectorAll(`#${id} .polozka`)) b.setAttribute('aria-pressed', b.dataset.id === hodnota);
}
for (const b of document.querySelectorAll('#pohledy .polozka')) b.addEventListener('click', () => prelet(b.dataset.id));
function prelet(p) {
  zastavOblet();
  pohled = p;
  oznac('pohledy', p);
  mapaA.flyTo({...kamera(p), duration: 3500, essential: true});
  mapaA.once('moveend', () => dolad(p));
  if (!A) panel();
}
// Mapbox drží výšku kamery, a když se pod středem donačte přesnější terén, zoom ujede.
// Po donačtení proto kameru jednou srovnáme, pokud s ní mezitím nikdo nehnul.
function dolad(p) {
  mapaA.once('idle', () => {
    const k = kamera(p), c = mapaA.getCenter();
    const stejne = Math.abs(c.lng - k.center[0]) < 1e-4 && Math.abs(c.lat - k.center[1]) < 1e-4;
    if (stejne && Math.abs(mapaA.getZoom() - k.zoom) > 0.05) mapaA.easeTo({...k, duration: 600});
  });
}

// obletění: pomalé otáčení kamery kolem středu, zastaví ho tah myší nebo kolečko
let oblet = null;
function zastavOblet() {
  if (oblet) cancelAnimationFrame(oblet);
  oblet = null;
  document.getElementById('oblet').setAttribute('aria-pressed', false);
}
document.getElementById('oblet').addEventListener('click', () => {
  if (oblet) return zastavOblet();
  document.getElementById('oblet').setAttribute('aria-pressed', true);
  let minule = null;
  const krok = ts => {
    if (minule != null) mapaA.setBearing(mapaA.getBearing() + (ts - minule) / 1000 * 5);
    minule = ts;
    oblet = requestAnimationFrame(krok);
  };
  oblet = requestAnimationFrame(krok);
});

// celá obrazovka: v iframu Streamlitu bývá zakázaná, pak stejná stránka v nové záložce, kde funguje
function stav() {
  const c = mapaA.getCenter();
  return {nast: N, pohled, cas, rezim, podle,
          kamera: {center: [c.lng, c.lat], zoom: mapaA.getZoom(), pitch: mapaA.getPitch(), bearing: mapaA.getBearing()}};
}
async function celaObrazovka() {
  if (document.fullscreenElement) return document.exitFullscreen();
  try {
    if (!document.fullscreenEnabled) throw new Error('celá obrazovka je v iframu zakázaná');
    await document.documentElement.requestFullscreen();
  } catch (e) {
    const url = URL.createObjectURL(new Blob([KOPIE], {type: 'text/html'}));
    if (!window.open(url + '#' + encodeURIComponent(JSON.stringify(stav())), '_blank')) {
      document.getElementById('cela').textContent = 'Povolte vyskakovací okna';
    }
  }
}
document.getElementById('cela').addEventListener('click', celaObrazovka);
document.addEventListener('fullscreenchange', () => {
  document.getElementById('cela').textContent = document.fullscreenElement ? 'Zavřít' : 'Celá obrazovka';
});

// ---------- pravý panel: osvětlení, téma, zobrazení, předpověď ----------
const SVETLA = [['dawn', 'Svítání'], ['day', 'Den'], ['dusk', 'Soumrak'], ['night', 'Noc']];
const TEMATA = [['default', 'Výchozí', ['#f2efe9', '#a8d4f0', '#c9e4b4']], ['faded', 'Vybledlé', ['#e9e6e1', '#bfd3df', '#d3dccb']],
                ['monochrome', 'Mono', ['#f0f0f0', '#b9b9b9', '#6d6d6d']]];
const PREPINACE = [['satelit', 'Satelit'], ['mista', 'Popisky míst'], ['poi', 'Zajímavá místa'], ['objekty', '3D objekty'],
                   ['ulice', 'Názvy ulic'], ...(DEM ? [['uredni', 'Úřední území']] : [])];
document.getElementById('vpravo').innerHTML = `
  <section class="nastaveni"><h2>Osvětlení</h2><div class="mrizka" id="svetla">${SVETLA.map(([id, nazev]) =>
    `<button class="volba" data-id="${id}">${svg(IKONY[id])}${nazev}</button>`).join('')}</div></section>
  <section class="nastaveni"><h2>Barevné téma</h2><div class="mrizka tri" id="temata">${TEMATA.map(([id, nazev, barvy]) =>
    `<button class="volba tema" data-id="${id}"><span class="tecky">${barvy.map(b => `<span style="background:${b}"></span>`).join('')}</span>${nazev}</button>`).join('')}</div></section>
  <section class="nastaveni"><h2>Zobrazení</h2><div class="prepinace">${PREPINACE.map(([id, nazev]) =>
    `<button class="prepinac" role="switch" data-id="${id}"><span>${nazev}</span><span></span></button>`).join('')}</div></section>
  <section><h2 id="nadpis-panelu">${A ? `Povodeň · ${A.mesto}` : 'Předpověď'}</h2><div id="panel"></div></section>`;

function nastaveni() {
  for (const b of document.querySelectorAll('#svetla .volba')) b.setAttribute('aria-pressed', b.dataset.id === N.svetlo);
  for (const b of document.querySelectorAll('#temata .volba')) {
    b.setAttribute('aria-pressed', b.dataset.id === N.tema);
    b.disabled = N.satelit;  // satelitní Standard témata nemá
  }
  for (const b of document.querySelectorAll('.prepinac')) {
    b.setAttribute('aria-checked', N[b.dataset.id]);
    if (b.dataset.id === 'objekty') b.disabled = N.satelit;
  }
}
function podklad(klic, hodnota) {
  for (const m of [mapaA, mapaB].filter(Boolean)) if (m.nacteno) m.setConfigProperty('basemap', klic, hodnota);
}
document.getElementById('svetla').addEventListener('click', e => {
  const b = e.target.closest('.volba'); if (!b) return;
  N.svetlo = b.dataset.id; podklad('lightPreset', N.svetlo); nastaveni();
});
document.getElementById('temata').addEventListener('click', e => {
  const b = e.target.closest('.volba'); if (!b || b.disabled) return;
  N.tema = b.dataset.id; podklad('theme', N.tema); nastaveni();
});
const KONFIG = {mista: ['showPlaceLabels'], poi: ['showPointOfInterestLabels', 'showTransitLabels'], objekty: ['show3dObjects'],
                ulice: ['showRoadLabels']};
for (const b of document.querySelectorAll('.prepinac')) b.addEventListener('click', () => {
  if (b.disabled) return;
  const id = b.dataset.id;
  N[id] = !N[id];
  if (id === 'satelit') {
    // jiný styl: naše zdroje a vrstvy přidá znovu pridejVrstvy po style.load
    for (const m of [mapaA, mapaB].filter(Boolean)) { m.satelit = N.satelit; m.nacteno = false; m.setStyle(STYL[N.satelit ? 'satelit' : 'standard']); }
  } else if (id === 'uredni') {
    nastavZdroj();
    for (const m of [mapaA, mapaB].filter(Boolean)) {
      viditelnostRozlivu(m);
      m.klic = undefined;
      if (A) obnovMapu(m, hodina());
    }
    popis();
    panel();
  } else {
    for (const klic of KONFIG[id]) podklad(klic, N[id]);
  }
  nastaveni();
});

function odznak(st) {
  const c = barvaStupne(st);
  return `<span class="odznak" style="background:${css(c)};color:${st === 1 ? '#1a1a1a' : '#fff'}">${st == null ? 'chybí' : STUPNE[st]}</span>`;
}
function panel() {
  if (A) return panelAnimace(hodina());
  const vybrane = D.mesta.find(m => m.nazev === pohled) ?? D.mesta[0];
  const dem = !uredni();
  document.getElementById('panel').innerHTML = `<div class="datum">${D.datum}</div>` + D.mesta.map(m => `
    <div class="mesto">
      <div class="radek"><span class="jmeno"><b>${m.nazev}</b></span><span class="cm">${cislo(m.hladina)} cm</span>${odznak(m.stupen)}</div>
      <div class="radek"><span class="jmeno">${m.predpoved ? `model za ${m.predpoved.h} h` : 'bez předpovědi'}</span>${m.predpoved ?
        `<span class="cm pred">${cislo(m.predpoved.cm)} cm</span>${odznak(m.predpoved.stupen)}` : ''}</div>
      ${dem && m.dem ? `<div class="maly">Pod vodou ${cislo(m.dem.ha)} ha` +
        (m.skut ? ` · pak naměřeno ${cislo(m.skut.cm)} cm, ${cislo(m.skut.ha)} ha` : '') + '</div>' : ''}
    </div>`).join('') +
    `<div class="veta"><b>${vybrane.nazev}:</b> ${vybrane.veta}${dem ? '' : ' ' + vybrane.uzemi}</div>`;
}

function panelAnimace(i) {
  const h = A.H[i], p = A.P[i], ks = uroven(h), kp = p == null ? -1 : uroven(p);
  const ha = k => k < 0 ? 0 : A.urovne[k].ha;
  const plocha = k => k < 0 ? '–' : `${cislo(A.urovne[k].ha)} ha` + (A.zdroj === 'dibavod' ? ` <small>Q${A.urovne[k].N}</small>` : '');
  const veta = A.vety[Math.round(rezim !== 'porovnani' && podle === 'predpoved' ? p : h)];
  document.getElementById('panel').innerHTML = `<div class="datum">${A.popisky[i]}</div>
    <table class="srovnani">
      <tr><th></th><th>Skutečnost</th><th class="pred">Předpověď</th><th>Rozdíl</th></tr>
      <tr><td>Hladina</td><td class="cm">${cislo(h)} cm</td><td class="cm pred">${p == null ? '–' : cislo(p) + ' cm'}</td>
        <td>${p == null || h == null ? '–' : znamenko(p - h) + ' cm'}</td></tr>
      <tr><td>Stupeň</td><td>${odznak(stupenH(A.spa, h))}</td><td>${p == null ? '' : odznak(stupenH(A.spa, p))}</td><td></td></tr>
      <tr><td>${A.zdroj === 'dem' ? 'Pod vodou' : 'Území'}</td><td>${plocha(ks)}</td><td class="pred">${p == null ? '–' : plocha(kp)}</td>
        <td>${p == null ? '–' : znamenko(ha(kp) - ha(ks)) + ' ha'}</td></tr>
    </table>
    <div class="maly">Předpověď modelu ${A.model} vydaná o 24 h dřív pro tutéž hodinu.</div>
    ${rezim === 'porovnani' ? '' : `<div class="segment" id="podle">
      <button class="volba" data-id="skutecnost" aria-pressed="${podle === 'skutecnost'}">Mapa: skutečnost</button>
      <button class="volba" data-id="predpoved" aria-pressed="${podle === 'predpoved'}">Mapa: předpověď</button></div>`}
    <div class="veta">${veta ?? 'Pro tuhle hodinu chybí měření.'}</div>`;
  document.getElementById('podle')?.addEventListener('click', e => {
    const b = e.target.closest('.volba'); if (!b) return;
    podle = b.dataset.id; obnovMapu(mapaA, hodina()); panelAnimace(hodina());
  });
}

// ---------- porovnání předpověď × skutečnost ----------
function nastavRezim(r) {
  rezim = r;
  oznac('rezimy', r);
  const kontejner = document.getElementById('mapa-b');
  if (r === 'porovnani') {
    kontejner.style.display = 'block';
    const c = mapaA.getCenter();
    const k = {center: [c.lng, c.lat], zoom: mapaA.getZoom(), pitch: mapaA.getPitch(), bearing: mapaA.getBearing(), padding: mapaA.getPadding()};
    if (!mapaB) { mapaB = vytvorMapu('mapa-b', k); mapaB.satelit = N.satelit; }
    else { mapaB.resize(); mapaB.jumpTo(k); }
    porovnani = new mapboxgl.Compare(mapaA, mapaB, '#mapy');
    porovnani.setSlider(SIROKO ? 250 + (innerWidth - 250 - 315) / 2 : innerWidth / 2);
    document.getElementById('stitky').style.display = 'block';
  } else if (porovnani) {
    porovnani.remove();
    porovnani = null;
    kontejner.style.display = 'none';
    document.getElementById('stitky').style.display = 'none';
  }
  mapaA.klic = undefined;
  for (const m of mapy()) obnovMapu(m, hodina());
  panelAnimace(hodina());
}

// ---------- přehrávání ----------
if (A) {
  for (const b of document.querySelectorAll('#rezimy .polozka')) b.addEventListener('click', () => nastavRezim(b.dataset.id));
  const ovladani = document.createElement('div');
  ovladani.className = 'sklo ovladani';
  ovladani.innerHTML = `<button id="hraj" aria-label="Přehrát nebo zastavit"></button>
    <input id="cas" type="range" min="0" max="${K}" step="0.01" aria-label="Čas">
    <div id="cas-text"></div>
    <select id="rychlost" aria-label="Rychlost">
      <option value="1">1 h za s</option><option value="2">2 h za s</option><option value="4" selected>4 h za s</option>
      <option value="8">8 h za s</option><option value="16">16 h za s</option></select>`;
  document.body.append(ovladani);
  const IKONA = {hraj: '<svg viewBox="0 0 24 24"><path d="M7 4.5v15l13-7.5z"/></svg>',
                 stuj: '<svg viewBox="0 0 24 24"><path d="M6 4h4.5v16H6zM13.5 4H18v16h-4.5z"/></svg>'};
  const posuvnik = document.getElementById('cas'), tlacitko = document.getElementById('hraj');
  const stitky = document.getElementById('stitky');
  let hraje = true, rychlost = 4, minule = null, nakresleno = -1, tahne = false;
  const ikona = () => { tlacitko.innerHTML = hraje ? IKONA.stuj : IKONA.hraj; };
  const prepni = () => { if (!hraje && cas >= K) cas = 0; hraje = !hraje; minule = null; ikona(); };
  tlacitko.addEventListener('click', prepni);
  posuvnik.addEventListener('input', () => { cas = +posuvnik.value; });
  posuvnik.addEventListener('pointerdown', () => { tahne = true; });
  addEventListener('pointerup', () => { tahne = false; });
  document.getElementById('rychlost').addEventListener('change', e => { rychlost = +e.target.value; });
  document.addEventListener('keydown', e => {
    if (e.code === 'Space' && !['SELECT', 'BUTTON', 'INPUT'].includes(e.target.tagName)) { e.preventDefault(); prepni(); }
  });
  const snimek = ts => {
    if (hraje && minule != null) {
      cas = Math.min(cas + (ts - minule) / 1000 * rychlost, K);
      if (cas >= K) { hraje = false; ikona(); }
    }
    minule = hraje ? ts : null;
    const i = hodina();
    if (i !== nakresleno) {
      for (const m of mapy()) obnovMapu(m, i);
      panelAnimace(i);
      document.getElementById('cas-text').textContent = A.popisky[i];
      nakresleno = i;
    }
    if (!tahne) posuvnik.value = cas;
    if (porovnani) stitky.style.left = porovnani.currentPosition + 'px';
    requestAnimationFrame(snimek);
  };
  ikona();
  oznac('rezimy', rezim);
  if (rezim === 'porovnani') mapaA.once('load', () => nastavRezim('porovnani'));
  requestAnimationFrame(snimek);
}

oznac('pohledy', pohled);
nastaveni();
panel();
if (!STAV.kamera) dolad(pohled);
</script>
</body>
</html>
"""


@st.cache_resource
def _vstupy(cil):
    return vstupy(cil)


@st.cache_data
def predpovedi(cas, model="ridge"):
    """{cil: (24, hladina_cm)} z models/<model>_<cil>_24.joblib jako predpovedi_pro_mapu v app.py."""
    out = {}
    for cil in KDE:
        X = _vstupy(cil)
        if cas in X.index:
            out[cil] = (24, float(nacti_model(model, cil, 24).predict(X.loc[[cas]])[0]))
    return out


@st.cache_data
def _animace_c(povoden, cil):
    from animace import okno
    od, do = okno(povoden)
    return html_animace(od, do, cil, "ridge", MESTA[cil])


def main():
    from animace import POVODNE, okno
    st.set_page_config(page_title="Labe · 3D mapa Mapbox", layout="wide")
    a, b = st.columns([2, 1])
    povoden = a.radio("Povodeň", list(POVODNE), index=3, horizontal=True)
    cil = b.radio("Cíl", list(MESTA), format_func=MESTA.get, horizontal=True)
    vyrobit = getattr(st, "iframe", components.html)
    vyrobit(_animace_c(povoden, cil), height=720)
    st.caption("Okno je 14 dní před vrcholem hladiny v Děčíně a 5 dní po něm. Porovnání: vlevo rozliv z hladiny, kterou "
               "model předpověděl o 24 h dřív, vpravo ze změřené hladiny ve stejné hodině. Terén je zvýšený 1,6×.")
    od, do = okno(povoden)
    od, do = od.tz_convert(mapa.PASMO).tz_localize(None), do.tz_convert(mapa.PASMO).tz_localize(None)
    vrchol = nacti().loc[slice(*POVODNE[povoden]), f"{cil}_H"].idxmax().tz_convert(mapa.PASMO).tz_localize(None)
    okamzik = st.slider("Okamžik (český čas)", od.to_pydatetime(), do.to_pydatetime(), vrchol.to_pydatetime(),
                        step=timedelta(hours=1), format="D. M. YYYY HH:mm")
    cas = mapa._cas_utc(pd.Timestamp(okamzik))
    vyrobit(html(cas, predpovedi(cas), MESTA[cil]), height=700)


if __name__ == "__main__":
    main()
