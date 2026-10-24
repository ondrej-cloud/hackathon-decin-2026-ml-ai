r"""3D mapa povodí v Mapbox GL JS ve stylu Mapbox Standard: terén, 3D budovy a stromy, osvětlení, stanice a rozliv.

Proti pydeck mapě v mapa.py (ta zůstává jako záloha) jsou dobře vidět malá území: rozliv leží přímo na terénu,
budovy v Děčíně a Ústí stojí ve vodě a ulice mají ostré popisky. Potřebuje MAPBOX_TOKEN v .env.

Ukázka z kořene repozitáře:
    .venv\Scripts\python -m streamlit run app/mapbox_mapa.py --server.port 8506
V aplikaci (stejné argumenty jako mapa.deck):
    st.iframe(mapbox_mapa.html(cas, predpovedi, pohled), height=700)
Animace povodně s porovnáním předpověď × skutečnost (od a do jako animace.okno):
    st.iframe(mapbox_mapa.html_animace(od, do, "decin", nazev, "Děčín"), height=720)
Stránka animace má pro nahrávání videa globální funkce prehraj(), pauza(), nastavRychlost(h), skoc(i),
skocNaVrchol(), porovnat(true/false), zavriUvod() a stavPrehravace(); na konci vyšle událost povoden-konec.
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
from budovy import nacti as nacti_budovy
from predikce import BARVY, KDE, ROOT, SPA, nacti, nacti_model, nazev_modelu, stupen, vstupy
from rozliv import GENITIV, SOUBOR_UZEMI, n_leta_voda, n_lete

MAPBOX = "https://api.mapbox.com/mapbox-gl-js/v3.8.0"
POROVNANI = "https://api.mapbox.com/mapbox-gl-js/plugins/mapbox-gl-compare/v0.4.2"
REKY = ROOT / "data/external/reky.geojson"
MESTA = {"decin": "Děčín", "usti": "Ústí nad Labem"}
# Klíče jako mapa.POHLEDY. Města jsou natočená po proudu Labe, ať je vidět řeka i svahy nad ní. Zoom 13,6 ukáže
# celé město s rozlivem a už i budovy (vlastní vrstva budov jde od zoomu 13, budovy Standardu až od 15).
KAMERY = {
    "celé povodí": {"center": [14.65, 50.30], "zoom": 8, "pitch": 55, "bearing": 0},
    "Ústí nad Labem": {"center": [14.037, 50.6585], "zoom": 13.6, "pitch": 60, "bearing": -25},
    "Děčín": {"center": [14.204, 50.773], "zoom": 13.6, "pitch": 60, "bearing": -10},
}
POHLEDY = [("celé povodí", "Celé povodí", "12 stanic a řeky"), ("Ústí nad Labem", "Ústí nad Labem", "záplavové území"),
           ("Děčín", "Děčín", "záplavové území")]
MESICE = ["leden", "únor", "březen", "duben", "květen", "červen", "červenec", "srpen", "září", "říjen", "listopad",
          "prosinec"]
JMENA_POVODNI = {(2024, 9): "Boris"}
NABEH = 48  # h; přehrávání začne dva dny před 1. stupněm, ať se nečeká na klidné dny na začátku okna
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


def _stranka(data, porovnani=False, pisma=None):
    data = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    plugin = (f'<link href="{POROVNANI}/mapbox-gl-compare.css" rel="stylesheet">\n'
              f'<script src="{POROVNANI}/mapbox-gl-compare.js"></script>') if porovnani else ""
    return (STRANKA.replace("__MAPBOX__", MAPBOX).replace("__POROVNANI__", plugin).replace("__PISMA__", _pisma(pisma))
            .replace("__DATA__", data))


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


def _spolecne(token, pohled, cile=tuple(MESTA)):
    return {"token": token, "kamery": KAMERY, "pohled": pohled, "pohledy": POHLEDY, "barvy": mapa.BARVY,
            "seda": mapa.SEDA, "spa_barvy": BARVY, "reky": json.loads(REKY.read_text(encoding="utf-8")),
            "budovy": [b for b in map(nacti_budovy, cile) if b]}


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


def html_animace(od, do, cil="decin", model="ridge", pohled="Děčín", nazev=None, pisma=None) -> str:
    """Animace povodně od `od` do `do` (UTC, jako animace.okno) pro st.iframe(..., height=720).

    Úvodní okno nabídne přehrání, dole je přehrávač s časovou osou. `nazev` je nadpis povodně, bez něj se
    sestaví z měsíce vrcholu (Povodeň leden 2011).

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

    mistni = cas.tz_convert(mapa.PASMO)
    vrchol = max(range(len(H)), key=lambda i: -1 if H[i] is None else H[i])
    nad = next((i for i, v in enumerate(H) if v is not None and v >= SPA[cil][0]), 0)
    if nazev is None:
        t = mistni[vrchol]
        jmeno = JMENA_POVODNI.get((t.year, t.month))
        nazev = f"Povodeň {jmeno + ', ' if jmeno else ''}{MESICE[t.month - 1]} {t.year}"
    a, b = mistni[0], mistni[-1]
    rozsah = f"{a.day}. {a.month}. {'' if a.year == b.year else f'{a.year} '}– {b.day}. {b.month}. {b.year}"

    data = _spolecne(token, pohled, [cil]) | {
        "uzemi": _zaplavy([], cil), "anim": {
            "cil": cil, "mesto": MESTA[cil], "model": model, "nazev_modelu": nazev_modelu(model),
            "popisky": [_popisek_casu(t) for t in cas],
            "nazev": nazev, "rozsah": rozsah, "vrchol": vrchol, "start": max(0, nad - NABEH),
            "pulnoci": [[i, f"{t.day}. {t.month}."] for i, t in enumerate(mistni) if t.hour == 0],
            "H": H, "P": Pr, "spa": SPA[cil], "vety": vety, "rozlivy": rozlivy,
            "Q": {s["klic"]: _rada(T[f"{s['klic']}_Q"], 1) for s in stanice},
            "Hs": {k: _rada(T[f"{k}_H"]) for k in SPA}, "stanice": stanice,
        },
    }
    return _stranka(data, porovnani=True, pisma=pisma)


BEZ_TOKENU = """<!doctype html><html lang="cs"><meta charset="utf-8">
<body style="margin:0;padding:24px;background:#0c1720;color:#eef3f6;font:15px sans-serif">
Mapa v Mapbox GL potřebuje MAPBOX_TOKEN v souboru .env. Bez něj použijte mapu z mapa.py.</body></html>"""

STRANKA = r"""<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Labe · mapa povodně</title>
__PISMA__
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
  --text: #e6ebf0;
  --tlumene: #8b98a5;
  --voda: #3aa0c9;
  --voda-svetla: #7cc6e4;
  --plne: #1e78dc;
  --pismo: "Schibsted Grotesk", sans-serif;
  --cisla: "Sofia Sans Extra Condensed", "Schibsted Grotesk", sans-serif;
  --lista: 0px;  /* výška přehrávače, nastaví ji skript */
}
* { box-sizing: border-box; }
html, body { margin: 0; height: 100%; background: var(--pozadi); color: var(--text); overflow: hidden;
  font: 14px/1.4 var(--pismo); }
.datum, .cm, .lista-cas b, .hodnota b, #stitky span b, .srovnani td { font-variant-numeric: tabular-nums; }
#mapy, .mapa { position: absolute; inset: 0; }
#mapa-b { display: none; }
.sklo { position: absolute; background: var(--sklo); border: 1px solid var(--okraj); border-radius: 12px;
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); box-shadow: 0 8px 28px rgba(0, 0, 0, 0.35); }
.sklo { z-index: 2; }
.vlevo { top: 12px; left: 12px; width: 236px; padding: 11px; max-height: calc(100% - 56px - var(--lista)); overflow: auto; }
.vpravo { top: 12px; right: 12px; width: 300px; padding: 11px 12px; max-height: calc(100% - 56px - var(--lista)); overflow: auto; }
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
.datum { font: 700 24px/1.1 var(--cisla); letter-spacing: 0.01em; }
.radek { display: flex; align-items: baseline; gap: 7px; margin-top: 7px; }
.radek .jmeno { flex: 1; color: var(--tlumene); }
.radek .jmeno b { color: var(--text); font-weight: 600; }
.cm { font: 700 22px/1.1 var(--cisla); }
.cm.pred { color: var(--voda); }
.odznak { font-size: 11.5px; font-weight: 700; padding: 2px 7px; border-radius: 6px; white-space: nowrap; }
.mesto + .mesto { margin-top: 6px; padding-top: 6px; border-top: 1px solid var(--okraj); }
.maly { margin-top: 2px; font-size: 12.5px; color: var(--tlumene); }
.veta { margin-top: 9px; padding-top: 8px; border-top: 1px solid var(--okraj); font-size: 12.5px; color: var(--tlumene); }
.veta b { color: var(--text); }
.srovnani { width: 100%; margin-top: 6px; border-collapse: collapse; font-size: 13px; }
.srovnani th { font-size: 11px; font-weight: 600; color: var(--tlumene); text-align: left; padding: 0 0 3px; }
.srovnani td { padding: 3px 4px 3px 0; white-space: nowrap; }
.srovnani td:first-child { color: var(--tlumene); }
.srovnani .cm { font-size: 20px; }
.srovnani .pred { color: var(--voda); }
.srovnani small { color: var(--tlumene); }
.segment { display: flex; gap: 4px; margin-top: 9px; }
.segment .volba { flex: 1; font-size: 12.5px; padding: 5px 4px; }
/* přehrávač povodně: přes celou šířku mapy nad atribucí */
.lista { left: 12px; right: 12px; bottom: 32px; padding: 12px 18px 8px; z-index: 3; }
.lista-horni { display: flex; align-items: center; gap: 24px; }
.hraj { flex: none; width: 54px; height: 54px; border-radius: 50%; border: 0; background: var(--voda); color: #06141b;
  display: grid; place-items: center; box-shadow: 0 0 0 5px rgba(58, 160, 201, 0.18);
  transition: background-color 0.15s ease-out, transform 0.12s ease-out; }
.hraj:hover { background: var(--voda-svetla); }
.hraj:active { transform: scale(0.95); }
.hraj svg { width: 22px; height: 22px; fill: currentColor; }
.lista-cas { flex: none; display: flex; align-items: baseline; gap: 9px; min-width: 196px; }
.lista-cas b { font: 800 34px/1 var(--cisla); letter-spacing: 0.01em; }
.lista-cas b + b { color: var(--voda-svetla); }
.lista-cas small { color: var(--tlumene); font-size: 12px; font-weight: 600; }
.hodnota { flex: none; display: grid; grid-template-columns: auto auto; justify-content: start; align-items: center; column-gap: 9px; }
.hodnota-nazev { grid-column: 1 / -1; display: flex; align-items: center; gap: 6px; font-size: 11px; font-weight: 700;
  letter-spacing: 0.1em; text-transform: uppercase; color: var(--tlumene); }
.hodnota b { font: 800 32px/1.05 var(--cisla); white-space: nowrap; }
.hodnota.pred b { color: var(--voda-svetla); }
.hodnota.rozdil b { font-weight: 700; color: var(--tlumene); }
.vzor { display: inline-block; width: 14px; height: 3px; border-radius: 2px; background: var(--text); }
.pred .vzor { background: var(--voda-svetla); }
.rychlost { margin-left: auto; display: flex; align-items: center; gap: 4px; }
.rychlost > span { margin-right: 6px; font-size: 11px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: var(--tlumene); }
.rychlost button { padding: 7px 11px; font-size: 13px; font-weight: 600; background: var(--karta); border: 1px solid var(--okraj);
  border-radius: 9px; white-space: nowrap; transition: background-color 0.15s ease-out, border-color 0.15s ease-out; }
.rychlost button:hover { background: rgba(255, 255, 255, 0.08); }
.rychlost button[aria-pressed="true"] { background: var(--karta-aktivni); border-color: rgba(255, 255, 255, 0.85); }
.osa { position: relative; height: 74px; margin-top: 12px; cursor: pointer; touch-action: none; border-radius: 6px;
  background: rgba(255, 255, 255, 0.025); }
.osa:focus-visible { outline: 2px solid var(--voda); outline-offset: 3px; }
.graf { position: absolute; inset: 0; pointer-events: none; }
.graf svg, .uvod-graf svg { position: absolute; inset: 0; width: 100%; height: 100%; overflow: visible; }
.prah { position: absolute; left: 0; right: 0; border-top: 1px dashed var(--c); opacity: 0.8; }
.prah span { position: absolute; left: calc(4px + var(--k) * 82px); bottom: 1px; padding: 0 4px; border-radius: 4px; background: #0f1419;
  font-size: 10.5px; font-weight: 700; color: var(--c); white-space: nowrap; }
.prah span { z-index: 1; }  /* nad čarou vrcholu */
.prah i { font-style: normal; }
.vrchol { position: absolute; top: 0; bottom: 0; border-left: 1px solid rgba(230, 235, 240, 0.55); }
.vrchol span { position: absolute; top: 1px; left: 6px; padding: 0 5px; border-radius: 4px; background: rgba(15, 20, 25, 0.85);
  font-size: 11px; font-weight: 700; white-space: nowrap; }
.vrchol.vlevo-od span { left: auto; right: 6px; }
.pasmo { position: absolute; left: 0; right: 0; bottom: -7px; height: 4px; border-radius: 2px; overflow: hidden;
  background: rgba(255, 255, 255, 0.06); pointer-events: none; }
.pasmo i { position: absolute; top: 0; bottom: 0; }
.hlava { position: absolute; top: -5px; bottom: -9px; width: 2px; margin-left: -1px; background: #fff; pointer-events: none;
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.35); }
.hlava i { position: absolute; left: 50%; width: 12px; height: 12px; margin: -6px 0 0 -6px; border-radius: 50%; background: #fff;
  box-shadow: 0 0 0 4px rgba(58, 160, 201, 0.45); }
.najeti { position: absolute; top: 0; bottom: 0; width: 1px; background: rgba(255, 255, 255, 0.4); pointer-events: none; display: none; }
.najeti span { position: absolute; bottom: calc(100% + 4px); transform: translateX(-50%); padding: 2px 7px; border-radius: 6px;
  background: #0b0f13; border: 1px solid var(--okraj); font-size: 11.5px; font-weight: 600; white-space: nowrap; }
.dny { position: relative; height: 15px; margin-top: 11px; font-size: 11px; color: var(--tlumene); }
.dny span { position: absolute; top: 0; transform: translateX(-50%); white-space: nowrap; }
/* úvodní okno animace */
.uvod { position: absolute; inset: 0; z-index: 10; display: grid; place-items: center; padding: 16px;
  background: radial-gradient(ellipse at center, rgba(8, 12, 16, 0.45), rgba(8, 12, 16, 0.82)); transition: opacity 0.3s ease-out; }
.uvod.pryc { opacity: 0; pointer-events: none; }
.uvod-karta { width: min(640px, 100%); max-height: 100%; overflow: auto; padding: 26px 30px 22px; background: var(--sklo);
  border: 1px solid var(--okraj); border-radius: 16px; backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.5); }
.uvod-nadtitul { font-size: 12px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: var(--voda-svetla); }
.uvod h1 { margin: 8px 0 0; font: 800 60px/0.95 var(--cisla); letter-spacing: 0; text-wrap: balance; }
.uvod h1 span { color: var(--tlumene); font-weight: 700; }
.uvod-rozsah { margin: 12px 0 0; color: var(--tlumene); font-size: 14.5px; }
.uvod-rozsah b { color: var(--text); font-weight: 600; }
.uvod-graf { position: relative; height: 124px; margin-top: 38px; }
/* v úvodu je štítek vrcholu nad grafem, ať nezakryje popisky stupňů */
.uvod-graf .vrchol { top: -20px; }
.uvod-legenda { display: flex; gap: 18px; margin-top: 8px; font-size: 12.5px; color: var(--tlumene); }
.uvod-legenda span { display: flex; align-items: center; gap: 7px; }
.uvod-hraj { margin-top: 18px; width: 100%; height: 62px; display: flex; align-items: center; justify-content: center; gap: 12px;
  border: 0; border-radius: 12px; background: var(--voda); color: #06141b; font: 800 28px/1 var(--cisla); letter-spacing: 0.02em;
  transition: background-color 0.15s ease-out, transform 0.12s ease-out; }
.uvod-hraj:hover { background: var(--voda-svetla); }
.uvod-hraj:active { transform: scale(0.98); }
.uvod-hraj svg { width: 22px; height: 22px; fill: currentColor; }
.uvod-napoveda { margin: 14px 0 0; font-size: 12.5px; color: var(--tlumene); }
kbd { font: 600 11.5px var(--pismo); padding: 1px 6px; border-radius: 5px; border: 1px solid rgba(255, 255, 255, 0.18);
  background: rgba(255, 255, 255, 0.06); color: var(--text); }
/* jeden okamžik: štítek, že celá povodeň jde přehrát v jiném režimu */
.napoveda { left: calc(250px + (100% - 565px) / 2); transform: translateX(-50%); bottom: 34px; max-width: calc(100% - 600px);
  display: flex; align-items: center; gap: 8px; padding: 7px 14px 7px 10px; border-radius: 999px; font-size: 13px; color: var(--tlumene); }
.napoveda svg { flex: none; width: 18px; height: 18px; stroke: var(--voda-svetla); fill: none; stroke-width: 1.7; stroke-linejoin: round; }
.napoveda b { color: var(--text); font-weight: 600; }
/* porovnání: popisky stran a výrazné držadlo */
#stitky { position: absolute; top: 16px; left: 50%; display: none; pointer-events: none; z-index: 2; }
#stitky span { position: absolute; top: 0; display: flex; align-items: center; gap: 8px; white-space: nowrap; padding: 7px 12px;
  border-radius: 10px; background: var(--sklo); border: 1px solid var(--okraj); font-size: 13px; font-weight: 700;
  letter-spacing: 0.06em; text-transform: uppercase; box-shadow: 0 6px 18px rgba(0, 0, 0, 0.35); }
#stitky span b { font: 800 24px/1 var(--cisla); letter-spacing: 0; text-transform: none; }
#stitky svg { width: 14px; height: 14px; fill: currentColor; }
#st-pred { right: 14px; color: var(--voda-svetla); }
#st-skut { left: 14px; }
.mapboxgl-compare { width: 3px; background-color: #e6ebf0; box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.35), 0 0 16px rgba(124, 198, 228, 0.6); }
.mapboxgl-compare .compare-swiper-vertical { width: 54px; height: 54px; left: -27px; margin: -27px 0 0 1.5px;
  background-color: #e6ebf0; background-size: 54px 54px; background-position: center;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 54 54'%3E%3Cpath d='M23 18l-9 9 9 9zM31 18l9 9-9 9z' fill='%230f1419'/%3E%3C/svg%3E");
  box-shadow: 0 0 0 4px rgba(15, 20, 25, 0.55), 0 8px 22px rgba(0, 0, 0, 0.55); }
/* tiráž: nezakryje logo Mapboxu a když se nevejde na řádek, zalomí se na dva vyrovnané */
.mapboxgl-ctrl-bottom-right .mapboxgl-ctrl-attrib:not(.mapboxgl-compact) { max-width: calc(100vw - 120px); text-align: right;
  text-wrap: balance; }
.mapboxgl-popup-content { background: #151c22; color: #fff; font: 13.5px/1.4 var(--pismo);
  border-radius: 9px; padding: 10px 28px 10px 12px; border: 1px solid var(--okraj); }
.mapboxgl-popup-close-button { color: #fff; font-size: 18px; padding: 0 7px; }
.mapboxgl-popup-anchor-top .mapboxgl-popup-tip, .mapboxgl-popup-anchor-top-left .mapboxgl-popup-tip,
.mapboxgl-popup-anchor-top-right .mapboxgl-popup-tip { border-bottom-color: #151c22; }
.mapboxgl-popup-anchor-bottom .mapboxgl-popup-tip, .mapboxgl-popup-anchor-bottom-left .mapboxgl-popup-tip,
.mapboxgl-popup-anchor-bottom-right .mapboxgl-popup-tip { border-top-color: #151c22; }
.mapboxgl-popup-anchor-left .mapboxgl-popup-tip { border-right-color: #151c22; }
.mapboxgl-popup-anchor-right .mapboxgl-popup-tip { border-left-color: #151c22; }
@media (max-width: 1180px) {
  .hodnota.rozdil, .rychlost > span { display: none; }
  .lista-horni { gap: 16px; }
}
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
  .anim .vpravo, .napoveda { display: none; }
  .lista { left: 8px; right: 8px; padding: 8px 10px 6px; }
  .lista-horni { flex-wrap: wrap; gap: 6px 14px; }
  .hraj { width: 44px; height: 44px; }
  .lista-cas { min-width: 0; }
  .lista-cas b, .hodnota b { font-size: 24px; }
  .uvod h1 { font-size: 36px; }
  .uvod-karta { padding: 18px 18px 0; }
  .uvod-graf { height: 84px; margin-top: 32px; }
  .lista .prah span { left: calc(4px + var(--k) * 31px); }
  .lista .prah i { display: none; }
  .uvod-hraj { position: sticky; bottom: 0; height: 56px; font-size: 24px; margin-top: 14px; box-shadow: 0 -12px 16px rgba(15, 20, 25, 0.9); }
  .uvod-napoveda { display: none; }
  .uvod-karta::after { content: ""; display: block; height: 14px; }
  .rychlost, .hodnota-nazev i { display: none; }
  .hodnota-nazev { font-size: 10px; }
  .osa { height: 48px; margin-top: 8px; }
  .dny { margin-top: 9px; }
}
@media (max-height: 520px) {
  .uvod h1 { font-size: 28px; }
  .uvod-graf, .uvod-legenda, .uvod-napoveda { display: none; }
}
</style>
</head>
<body>
<div id="mapy"><div class="mapa" id="mapa"></div><div class="mapa" id="mapa-b"></div></div>
<div id="stitky"><span id="st-pred"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-8 7 8 7z"/></svg>Předpověď 24 h předem<b></b></span><span id="st-skut">Skutečnost<b></b><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5l8 7-8 7z"/></svg></span></div>
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
// budovy z OpenStreetMap (app/budovy.py): kompaktní obrysy převedené na GeoJSON; bez nich dlaždice Mapbox Streets v8
const BUDOVY_OSM = D.budovy.length ? {type: 'FeatureCollection', features: D.budovy.flatMap(B => B.b.map(a => {
  let x = a[2], y = a[3];
  const kruh = [[B.lon0 + x * 1e-5, B.lat0 + y * 1e-5]];
  for (let i = 4; i < a.length; i += 2) { x += a[i]; y += a[i + 1]; kruh.push([B.lon0 + x * 1e-5, B.lat0 + y * 1e-5]); }
  kruh.push(kruh[0]);
  return {type: 'Feature', geometry: {type: 'Polygon', coordinates: [kruh]}, properties: {height: a[0], min_height: a[1]}};
}))} : null;
// pevné mezery uvnitř zdrojů a před tečkou: tiráž se láme jen mezi zdroji
const ATRIBUCE = ['Měření a N-leté průtoky © ČHMÚ', 'Záplavová území DIBAVOD (VÚV TGM)', DEM ? 'Terén ČÚZK DMR 5G' : '',
  BUDOVY_OSM ? 'Řeky a budovy © OpenStreetMap' : 'Řeky © OpenStreetMap'].filter(Boolean).map(t => t.replaceAll(' ', '\u00a0')).join('\u00a0· ');
const N = Object.assign({svetlo: 'dusk', tema: 'default', satelit: false, mista: true, poi: true, objekty: true,
                         ulice: false, uredni: false}, STAV.nast);
// vlastní budovy podle světla Standardu: den světle šedé, noc tmavě modrošedé; trocha svitu, ať jsou vidět i za šera
const BUDOVY = {dawn: ['#e2e5ea', 0.45], day: ['#e6e9ed', 0.15], dusk: ['#d2d8e1', 0.7], night: ['#4a5b74', 0.8]};
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
  // střed záběru mezi panely a nad přehrávačem; celé povodí se musí vejít i do užšího okna
  const k = {...D.kamery[pohled], padding: SIROKO ? {top: 0, bottom: A ? 190 : 40, left: 250, right: 315} : {top: 60, bottom: 220, left: 0, right: 0}};
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
    attributionControl: false, keyboard: !A  // v animaci šipky posouvají čas
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
  // Budovy i z dálky: Standard kreslí 3D budovy až od zoomu 15 a dlaždice Streets v8 mají pod 15 jen pár velkých budov,
  // proto u Děčína a Ústí obrysy z OpenStreetMap (od zoomu 11). Vrstva je ve slotu middle za rozlivem, takže domy stojí
  // ve vodě; od zoomu 15 ji vystřídají budovy Standardu.
  m.addSource('budovy', BUDOVY_OSM ? {type: 'geojson', data: BUDOVY_OSM} : {type: 'vector', url: 'mapbox://mapbox.mapbox-streets-v8'});
  m.addLayer({id: 'budovy', type: 'fill-extrusion', source: 'budovy', slot: 'middle',
    minzoom: BUDOVY_OSM ? 11 : 13, maxzoom: m.satelit ? 24 : 15.3,
    ...(BUDOVY_OSM ? {} : {'source-layer': 'building',
      filter: ['all', ['==', ['get', 'extrude'], 'true'], ['==', ['get', 'underground'], 'false']]}),
    layout: {visibility: m.satelit || N.objekty ? 'visible' : 'none'},
    paint: {
      'fill-extrusion-color': BUDOVY[N.svetlo][0], 'fill-extrusion-emissive-strength': BUDOVY[N.svetlo][1],
      'fill-extrusion-height': ['coalesce', ['get', 'height'], 9], 'fill-extrusion-base': ['coalesce', ['get', 'min_height'], 0],
      'fill-extrusion-vertical-gradient': true, 'fill-extrusion-ambient-occlusion-intensity': 0.35,
      // satelit 3D budovy nemá, tam zůstanou naše; ve Standardu se prolnou s jeho budovami (ty najíždějí 15 až 15,3)
      'fill-extrusion-opacity': m.satelit ? 1 : ['interpolate', ['linear'], ['zoom'], 15, 1, 15.3, 0]
    }});
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
let cas = A ? Math.min(STAV.cas ?? A.start, K) : 0, rezim = A ? (STAV.rezim ?? 'animace') : null;
let hraje = false, rychlost = STAV.rychlost ?? 6;  // rychlost v hodinách povodně za sekundu
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
  return {nast: N, pohled, cas, rezim, podle, hraje, rychlost,
          kamera: {center: [c.lng, c.lat], zoom: mapaA.getZoom(), pitch: mapaA.getPitch(), bearing: mapaA.getBearing()}};
}
async function celaObrazovka() {
  if (document.fullscreenElement) return document.exitFullscreen();
  try {
    if (!document.fullscreenEnabled) throw new Error('celá obrazovka je v iframu zakázaná');
    await document.documentElement.requestFullscreen();
  } catch (e) {
    const url = /^https?:/.test(location.href) ? location.href.split('#')[0]
      : URL.createObjectURL(new Blob([KOPIE], {type: 'text/html'}));
    if (!window.open(url + '#' + encodeURIComponent(JSON.stringify(stav())), '_blank')) {
      document.getElementById('cela').textContent = 'Povolte vyskakovací okna';
    }
  }
}
document.getElementById('cela').addEventListener('click', celaObrazovka);
// bez podpory celé obrazovky (Safari na iPhonu) a mimo iframe nemá tlačítko co dělat
if (window === window.top && !document.fullscreenEnabled) document.getElementById('cela').hidden = true;
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
  N.svetlo = b.dataset.id; podklad('lightPreset', N.svetlo); budovy(); nastaveni();
});
function budovy() {
  for (const m of [mapaA, mapaB].filter(Boolean)) if (m.nacteno && m.getLayer('budovy')) {
    m.setPaintProperty('budovy', 'fill-extrusion-color', BUDOVY[N.svetlo][0]);
    m.setPaintProperty('budovy', 'fill-extrusion-emissive-strength', BUDOVY[N.svetlo][1]);
    m.setLayoutProperty('budovy', 'visibility', m.satelit || N.objekty ? 'visible' : 'none');
  }
}
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
    if (id === 'objekty') budovy();
  }
  nastaveni();
});

function odznak(st) {
  const pozadi = st ? D.spa_barvy[st] : 'rgba(255,255,255,0.1)', text = st === 1 ? '#1a1a1a' : st ? '#fff' : 'var(--text)';
  return `<span class="odznak" style="background:${pozadi};color:${text}">${st == null ? 'chybí' : STUPNE[st]}</span>`;
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
    <div class="maly">Předpověď vydaná o 24 h dřív: ${A.nazev_modelu}.</div>
    ${rezim === 'porovnani' ? '' : `<div class="segment" id="podle">
      <button class="volba" data-id="skutecnost" aria-pressed="${podle === 'skutecnost'}">Mapa: skutečnost</button>
      <button class="volba" data-id="predpoved" aria-pressed="${podle === 'predpoved'}">Mapa: předpověď</button></div>`}
    <div class="veta">${veta ?? 'Pro tuhle hodinu chybí měření.'}</div>`;
  document.querySelector('#st-pred b').textContent = p == null ? '–' : cislo(p) + ' cm';
  document.querySelector('#st-skut b').textContent = h == null ? '–' : cislo(h) + ' cm';
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

// ---------- přehrávač povodně ----------
const IKONA = {hraj: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 4.5v15l13-7.5z"/></svg>',
               stuj: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 4h4.5v16H6zM13.5 4H18v16h-4.5z"/></svg>',
               znovu: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5V1.5L7 6l5 4.5V7a6 6 0 1 1-6 6H4a8 8 0 1 0 8-8z"/></svg>'};
if (A) {
  for (const b of document.querySelectorAll('#rezimy .polozka')) b.addEventListener('click', () => nastavRezim(b.dataset.id));
  document.body.classList.add('anim');
  const RYCHLOSTI = [2, 6, 12];
  let minule = null, nakresleno = -1, tahne = false, uvod = null;
  const q = id => document.getElementById(id);
  const procento = i => i / K * 100;
  const casti = i => {
    const c = A.popisky[i].split(' ');  // "17. 1. 2011 05:00 SEČ"
    return {den: c.slice(0, 3).join(' '), hodina: c[3].replace(/^0(?=\d)/, ''), pasmo: c[4]};
  };
  const kratce = i => { const c = casti(i); return `${c.den.replace(/ \d{4}$/, '')} v ${c.hodina}`; };

  // graf hladiny pro časovou osu i úvod: svisle od nejnižší hladiny po vrchol s rezervou na popisek, 1. stupeň vždy
  const hodnoty = A.H.concat(A.P).filter(v => v != null);
  const dno = Math.min(...hodnoty), strop = Math.max(...hodnoty, A.spa[0]);
  const y = v => 100 - (v - (dno - 0.06 * (strop - dno))) / (1.3 * (strop - dno)) * 100;
  function cesta(rada, plocha) {
    let d = '', od = null, posledni = null;
    const x = i => (i / K * 1000).toFixed(1);
    const zavri = () => { if (plocha && od != null) d += `L${x(posledni)},100Z`; };
    rada.forEach((v, i) => {
      if (v == null) { zavri(); od = null; return; }
      const yy = y(v).toFixed(2);
      if (od == null) { od = i; d += plocha ? `M${x(i)},100L${x(i)},${yy}` : `M${x(i)},${yy}`; }
      else d += `L${x(i)},${yy}`;
      posledni = i;
    });
    zavri();
    return d;
  }
  function graf(el, id) {
    const xv = procento(A.vrchol);
    el.innerHTML = `<svg viewBox="0 0 1000 100" preserveAspectRatio="none" aria-hidden="true">
        <defs><linearGradient id="${id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3aa0c9" stop-opacity="0.55"/>
          <stop offset="1" stop-color="#3aa0c9" stop-opacity="0.05"/></linearGradient></defs>
        <path d="${cesta(A.H, true)}" fill="url(#${id})"/>
        <path d="${cesta(A.P)}" fill="none" stroke="#7cc6e4" stroke-width="1.6" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>
        <path d="${cesta(A.H)}" fill="none" stroke="#e6ebf0" stroke-width="1.8" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>
      </svg>` +
      // prahy jsou u sebe blízko, popisky proto vedle sebe
      A.spa.map((v, k) => y(v) < 0 ? '' : `<div class="prah" style="top:${y(v)}%;--c:${D.spa_barvy[k + 1]}">
        <span style="--k:${k}"><i>${k + 1}. stupeň </i>${cislo(v)}</span></div>`).join('') +
      `<div class="vrchol${xv > 70 ? ' vlevo-od' : ''}" style="left:${xv}%"><span>vrchol ${kratce(A.vrchol)} · ${cislo(A.H[A.vrchol])} cm</span></div>`;
  }
  function pasmo() {  // pruh pod osou: kdy byla skutečná hladina v kterém stupni
    let html = '', od = 0, st = stupenH(A.spa, A.H[0]);
    for (let i = 1; i <= K + 1; i++) {
      const s = i <= K ? stupenH(A.spa, A.H[i]) : -1;
      if (s === st) continue;
      if (st) html += `<i style="left:${procento(od)}%;width:${procento(i - od)}%;background:${D.spa_barvy[st]}"></i>`;
      od = i; st = s;
    }
    return html;
  }

  const lista = document.createElement('div');
  lista.className = 'sklo lista';
  lista.innerHTML = `<div class="lista-horni">
      <button class="hraj" id="hraj"></button>
      <div class="lista-cas"><b id="l-den"></b><b id="l-hodina"></b><small id="l-pasmo"></small></div>
      <div class="hodnota"><span class="hodnota-nazev"><i class="vzor"></i>Skutečnost</span><b id="l-skut"></b><span id="l-skut-st"></span></div>
      <div class="hodnota pred"><span class="hodnota-nazev"><i class="vzor"></i>Předpověď 24 h předem</span><b id="l-pred"></b><span id="l-pred-st"></span></div>
      <div class="hodnota rozdil"><span class="hodnota-nazev">Rozdíl</span><b id="l-rozdil"></b></div>
      <div class="rychlost" id="rychlost" role="group" aria-label="Rychlost přehrávání"><span>Rychlost</span>${RYCHLOSTI.map(h =>
        `<button data-h="${h}" title="${h} ${h < 5 ? 'hodiny' : 'hodin'} povodně za sekundu">${h} h/s</button>`).join('')}</div>
    </div>
    <div class="osa" id="osa" role="slider" tabindex="0" aria-label="Čas povodně" aria-valuemin="0" aria-valuemax="${K}">
      <div class="graf" id="graf-osa"></div><div class="pasmo">${pasmo()}</div>
      <div class="najeti" id="najeti"><span></span></div><div class="hlava" id="hlava"><i></i></div>
    </div>
    <div class="dny" id="dny"></div>`;
  document.body.append(lista);
  graf(q('graf-osa'), 'g-osa');
  const osa = q('osa'), hlava = q('hlava'), najeti = q('najeti'), tlacitko = q('hraj'), stitky = q('stitky');
  function dny() {  // půlnoci, ať mezi popisky zbyde aspoň 46 px
    const krok = Math.ceil(46 / (osa.clientWidth / Math.max(1, K) * 24));
    q('dny').innerHTML = A.pulnoci.filter((_, j) => j % krok === 0).map(([i, t]) => `<span style="left:${procento(i)}%">${t}</span>`).join('');
  }
  // přehrávač stojí nad tiráží Mapboxu, i když se tiráž na užší obrazovce zalomí do dvou řádků
  const tiraz = document.querySelector('#mapa .mapboxgl-ctrl-attrib');
  function rozmer() {
    const dole = tiraz && !tiraz.classList.contains('mapboxgl-compact') ? Math.max(32, tiraz.offsetHeight + 12) : 32;
    lista.style.bottom = dole + 'px';
    document.documentElement.style.setProperty('--lista', lista.offsetHeight + dole - 32 + 'px');
    dny();
  }
  rozmer();
  addEventListener('resize', rozmer);
  if (tiraz && window.ResizeObserver) new ResizeObserver(rozmer).observe(tiraz);

  function obnovListu(i) {
    const c = casti(i), h = A.H[i], p = A.P[i];
    q('l-den').textContent = c.den; q('l-hodina').textContent = c.hodina; q('l-pasmo').textContent = c.pasmo;
    q('l-skut').textContent = h == null ? '–' : cislo(h) + ' cm';
    q('l-pred').textContent = p == null ? '–' : cislo(p) + ' cm';
    q('l-skut-st').innerHTML = odznak(stupenH(A.spa, h));
    q('l-pred-st').innerHTML = p == null ? '' : odznak(stupenH(A.spa, p));
    q('l-rozdil').textContent = p == null || h == null ? '–' : znamenko(p - h) + ' cm';
    hlava.firstChild.style.top = `calc(5px + (100% - 14px) * ${(h == null ? 50 : y(h)) / 100})`;
    osa.setAttribute('aria-valuenow', i);
    osa.setAttribute('aria-valuetext', A.popisky[i]);
  }
  function ikona() {
    tlacitko.innerHTML = hraje ? IKONA.stuj : cas >= K ? IKONA.znovu : IKONA.hraj;
    tlacitko.setAttribute('aria-label', hraje ? 'Zastavit' : 'Přehrát povodeň');
  }
  function zavriUvod() {
    if (!uvod) return;
    const u = uvod;
    uvod = null;
    u.classList.add('pryc');
    setTimeout(() => u.remove(), 350);
  }
  function prehraj() { zavriUvod(); if (cas >= K) cas = A.start; hraje = true; minule = null; ikona(); }
  function pauza() { hraje = false; minule = null; ikona(); }
  function nastavRychlost(h) {
    if (+h > 0) rychlost = +h;
    for (const b of document.querySelectorAll('#rychlost button')) b.setAttribute('aria-pressed', +b.dataset.h === rychlost);
  }
  function skoc(i) { cas = Math.max(0, Math.min(K, Math.round(+i))); minule = null; ikona(); }
  const krok = d => { pauza(); skoc(hodina() + d); };

  tlacitko.addEventListener('click', () => hraje ? pauza() : prehraj());
  q('rychlost').addEventListener('click', e => { const b = e.target.closest('button'); if (b) nastavRychlost(b.dataset.h); });
  const zBodu = e => { const o = osa.getBoundingClientRect(); return Math.round(Math.min(1, Math.max(0, (e.clientX - o.left) / o.width)) * K); };
  osa.addEventListener('pointerdown', e => { tahne = true; osa.setPointerCapture(e.pointerId); cas = zBodu(e); });
  osa.addEventListener('pointermove', e => {
    const i = zBodu(e);
    if (tahne) cas = i;
    najeti.style.display = 'block';
    najeti.style.left = procento(i) + '%';
    najeti.firstChild.textContent = kratce(i);
  });
  const pust = () => { tahne = false; minule = null; };
  osa.addEventListener('pointerup', pust);
  osa.addEventListener('pointercancel', pust);
  osa.addEventListener('pointerleave', () => { najeti.style.display = 'none'; });
  document.addEventListener('keydown', e => {
    if (['INPUT', 'SELECT', 'TEXTAREA'].includes(e.target.tagName)) return;
    if (e.code === 'Space') { e.preventDefault(); if (!e.repeat) hraje ? pauza() : prehraj(); }
    else if (e.code === 'ArrowRight' || e.code === 'ArrowLeft') {
      e.preventDefault();
      krok((e.code === 'ArrowRight' ? 1 : -1) * (e.shiftKey ? 24 : 1));
    }
  });
  // mezerník na tlačítku by ho po puštění ještě jednou stiskl
  document.addEventListener('keyup', e => { if (e.code === 'Space' && e.target.tagName === 'BUTTON') e.preventDefault(); });

  // úvod: velké okno s jedním tlačítkem; nová záložka z celé obrazovky (stav v adrese) pokračuje bez něj
  if (!Object.keys(STAV).length) {
    uvod = document.createElement('div');
    uvod.className = 'uvod';
    uvod.innerHTML = `<div class="uvod-karta" role="dialog" aria-labelledby="uvod-nazev">
      <div class="uvod-nadtitul">Celá povodeň po hodinách · předpověď × skutečnost</div>
      <h1 id="uvod-nazev">${A.nazev} <span>· ${A.mesto}</span></h1>
      <p class="uvod-rozsah">Data ${A.rozsah}, ${cislo(K + 1)} hodin. Vrchol <b>${kratce(A.vrchol)}, ${cislo(A.H[A.vrchol])} cm</b>
        ${odznak(stupenH(A.spa, A.H[A.vrchol]))}</p>
      <div class="uvod-graf" id="graf-uvod"></div>
      <div class="uvod-legenda"><span><i class="vzor"></i>skutečnost</span><span class="pred"><i class="vzor"></i>předpověď 24 h předem (${A.nazev_modelu})</span></div>
      <button class="uvod-hraj" id="uvod-hraj">${IKONA.hraj}Přehrát povodeň</button>
      <p class="uvod-napoveda">Mapa ukazuje rozliv podle změřené hladiny, vlevo jde přepnout na porovnání s předpovědí.
        <kbd>mezerník</kbd> spustí a zastaví, <kbd>←</kbd> <kbd>→</kbd> posunou o hodinu, kliknutím na osu skočíte v čase.</p></div>`;
    document.body.append(uvod);
    graf(q('graf-uvod'), 'g-uvod');
    q('uvod-hraj').addEventListener('click', prehraj);
  } else {
    hraje = Boolean(STAV.hraje);
  }

  const snimek = ts => {
    if (hraje && !tahne && minule != null) {
      cas = Math.min(cas + (ts - minule) / 1000 * rychlost, K);
      if (cas >= K) { hraje = false; ikona(); document.dispatchEvent(new CustomEvent('povoden-konec')); }
    }
    minule = hraje && !tahne ? ts : null;
    const i = hodina();
    if (i !== nakresleno) {
      for (const m of mapy()) obnovMapu(m, i);
      panelAnimace(i);
      obnovListu(i);
      nakresleno = i;
    }
    hlava.style.left = procento(cas) + '%';
    if (porovnani) stitky.style.left = porovnani.currentPosition + 'px';
    requestAnimationFrame(snimek);
  };
  // pro nahrávání videa a ovládání z konzole
  Object.assign(window, {prehraj, pauza, nastavRychlost, skoc, zavriUvod,
    skocNaVrchol: () => skoc(A.vrchol),
    porovnat: (ano = true) => nastavRezim(ano ? 'porovnani' : 'animace'),
    stavPrehravace: () => ({hodina: hodina(), konec: K, hraje, rychlost, rezim, datum: A.popisky[hodina()],
                            skutecnost: A.H[hodina()], predpoved: A.P[hodina()], start: A.start, vrchol: A.vrchol})});
  ikona();
  nastavRychlost(rychlost);
  oznac('rezimy', rezim);
  if (rezim === 'porovnani') mapaA.once('load', () => nastavRezim('porovnani'));
  requestAnimationFrame(snimek);
} else {
  const napoveda = document.createElement('div');
  napoveda.className = 'sklo napoveda';
  napoveda.innerHTML = `${svg(IKONY.animace)}<span>Celou povodeň po hodinách přehrajete v režimu <b>Celá povodeň</b> nad mapou</span>`;
  document.body.append(napoveda);
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
