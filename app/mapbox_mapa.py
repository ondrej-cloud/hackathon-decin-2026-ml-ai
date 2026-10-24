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
skocNaVrchol(), porovnat(true/false), zavriUvod(), stavPrehravace() a prelet(pohled); na konci vyšle událost
povoden-konec. Na stránce je vlevo nahoře přepínač pohledů (celé povodí, Ústí, Děčín; stránka nese řady a rozliv
obou měst, graf přehrávače ukazuje město pohledu), vpravo nahoře pilulka s datem a kulaté tlačítko, které rozbalí
přepínače zobrazení (satelit, popisky, zajímavá místa, 3D objekty, názvy ulic, úřední území). Dole je přehrávač bez
karty, jen nad tmavým přechodem: křivka hladiny se kreslí do přehrávané hodiny, předpověď 24 h před ní, vpravo tlačítko
Celá obrazovka. Boxy jsou průsvitné sklo (Liquid Glass), mapa pod nimi prosvítá. Porovnání předpověď × skutečnost
není v ovládání, zapne ho jen porovnat(true) z JS (video a kontroly). Podklad je pevně soumrak a výchozí téma.
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
# barvy stanic jako v grafech a na webu: bez stupně modrá grafů, stupně žlutá, oranžová, červená (mapa.BARVY má zelenou)
BARVY_PULT = ([22, 124, 156], [242, 196, 55], [239, 108, 0], [198, 40, 40])
SEDA_PULT = [142, 142, 147]
PREBARVI = {tuple(a): b for a, b in zip(mapa.BARVY, BARVY_PULT)} | {tuple(mapa.SEDA): SEDA_PULT}
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
            "prutok": round(b["prutok"], 1), "barva": "rgb({},{},{})".format(*PREBARVI.get(tuple(b["barva"]), b["barva"])),
            "popisek": b["popisek"],
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


# ikona záložky jako na webu (vodočet), vložená přímo, ať nic nehledá /favicon.ico ani v iframu
IKONA = """<link rel="icon" href="data:image/svg+xml,%3Csvg%20viewBox='0%200%2044%2044'%20width='44'%20height='44'%20aria-hidden='true'%20xmlns='http://www.w3.org/2000/svg'%3E%3Crect%20width='44'%20height='44'%20rx='12'%20fill='%23167c9c'/%3E%3Crect%20x='15'%20y='4'%20width='14'%20height='36'%20rx='2'%20fill='%23ffffff'/%3E%3Cg%20stroke='%23167c9c'%20stroke-width='1.2'%20stroke-opacity='.8'%3E%3Cline%20x1='15'%20x2='29'%20y1='8'%20y2='8'/%3E%3Cline%20x1='15'%20x2='22'%20y1='11'%20y2='11'/%3E%3Cline%20x1='15'%20x2='22'%20y1='14'%20y2='14'/%3E%3Cline%20x1='15'%20x2='22'%20y1='17'%20y2='17'/%3E%3Cline%20x1='15'%20x2='29'%20y1='20'%20y2='20'/%3E%3Cline%20x1='15'%20x2='22'%20y1='23'%20y2='23'/%3E%3Cline%20x1='15'%20x2='22'%20y1='26'%20y2='26'/%3E%3Cline%20x1='15'%20x2='22'%20y1='29'%20y2='29'/%3E%3Cline%20x1='15'%20x2='29'%20y1='32'%20y2='32'/%3E%3Cline%20x1='15'%20x2='22'%20y1='35'%20y2='35'/%3E%3Cline%20x1='15'%20x2='22'%20y1='38'%20y2='38'/%3E%3C/g%3E%3Cpath%20d='M15%2027h14v11a2%202%200%200%201-2%202H17a2%202%200%200%201-2-2z'%20fill='%239fcad8'/%3E%3Cpath%20d='M8%2027h28'%20stroke='%23ffffff'%20stroke-width='2.2'%20stroke-linecap='round'/%3E%3C/svg%3E">"""


def _stranka(data, porovnani=False, pisma=None):
    data = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    plugin = (f'<link href="{POROVNANI}/mapbox-gl-compare.css" rel="stylesheet">\n'
              f'<script src="{POROVNANI}/mapbox-gl-compare.js"></script>') if porovnani else ""
    return (STRANKA.replace("__MAPBOX__", MAPBOX).replace("__POROVNANI__", plugin).replace("__PISMA__", _pisma(pisma))
            .replace("__IKONA__", IKONA).replace("__DATA__", data))


def _pisma(pisma):
    """Písmo jako v grafech: systémové (na Macu San Francisco), záloha Inter ze složky `pisma` (na webu ../fonts/).
    Bez složky (iframe v aplikaci) jen systémové písmo, žádné stahování z Google Fonts."""
    if pisma:
        return PISMA_LOKALNE.replace("__PISMA__", pisma)
    return ""


PISMA_LOKALNE = '''<style>
@font-face { font-family: "Inter"; font-style: normal; font-weight: 100 900; font-display: swap;
  src: url("__PISMA__inter-latin.woff2") format("woff2");
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD; }
@font-face { font-family: "Inter"; font-style: normal; font-weight: 100 900; font-display: swap;
  src: url("__PISMA__inter-latin-ext.woff2") format("woff2");
  unicode-range: U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C4, U+2113, U+2C60-2C7F, U+A720-A7FF; }
</style>'''


def _spolecne(token, pohled, cile=tuple(MESTA)):
    return {"token": token, "kamery": KAMERY, "pohled": pohled, "pohledy": POHLEDY, "barvy": BARVY_PULT,
            "seda": SEDA_PULT, "spa_barvy": BARVY, "reky": json.loads(REKY.read_text(encoding="utf-8")),
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
    cas = pd.date_range(mapa._cas_utc(od), mapa._cas_utc(do), freq="h")
    T = nacti().reindex(cas)
    metadata, percentily = mapa._podklady()
    stanice = [{"klic": s.klic, "nazev": s.stanice, "tok": s.tok, "lon": s.lon, "lat": s.lat, "spa": SPA.get(s.klic),
                "p95": round(percentily[f"{s.klic}_Q"].iloc[0], 1), "p99": round(percentily[f"{s.klic}_Q"].iloc[1], 1)}
               for s in metadata.itertuples(index=False)]
    # řady a rozliv pro obě města: po přepnutí pohledu na druhé město je vidět i jeho voda a graf jeho hladiny;
    # druhé město má rozliv po 20 cm, ať stránka nenaroste dvakrát
    rady = {c: _rada_mesta(c, cas, T, model, hrube=c != cil) for c in MESTA}
    H = rady[cil]["H"]

    mistni = cas.tz_convert(mapa.PASMO)
    vrchol = rady[cil]["vrchol"]
    nad = next((i for i, v in enumerate(H) if v is not None and v >= SPA[cil][0]), 0)
    if nazev is None:
        t = mistni[vrchol]
        jmeno = JMENA_POVODNI.get((t.year, t.month))
        nazev = f"Povodeň {jmeno + ', ' if jmeno else ''}{MESICE[t.month - 1]} {t.year}"
    a, b = mistni[0], mistni[-1]
    rozsah = f"{a.day}. {a.month}. {'' if a.year == b.year else f'{a.year} '}– {b.day}. {b.month}. {b.year}"

    data = _spolecne(token, pohled) | {
        "uzemi": _zaplavy([]), "anim": {
            "cil": cil, "model": model, "nazev_modelu": nazev_modelu(model),
            "popisky": [_popisek_casu(t) for t in cas],
            "nazev": nazev, "rozsah": rozsah, "start": max(0, nad - NABEH),
            "pulnoci": [[i, f"{t.day}. {t.month}."] for i, t in enumerate(mistni) if t.hour == 0],
            "rady": rady, "Q": {s["klic"]: _rada(T[f"{s['klic']}_Q"], 1) for s in stanice},
            "Hs": {k: _rada(T[f"{k}_H"]) for k in SPA}, "stanice": stanice,
        },
    }
    return _stranka(data, porovnani=True, pisma=pisma)


def _rada_mesta(cil, cas, T, model, hrube=False):
    """Hladina, předpověď 24 h předem a úrovně rozlivu jednoho města pro animaci."""
    hodina = pd.Timedelta(hours=1)
    X = _vstupy(cil)
    X = X[X.index.isin(cas - 24 * hodina)]
    P = pd.Series(nacti_model(model, cil, 24).predict(X), index=X.index + 24 * hodina).reindex(cas)
    H, Pr = _rada(T[f"{cil}_H"]), _rada(P)
    hladiny = n_lete().query("klic == @cil").set_index("N").H_cm
    rozlivy = {"dibavod": sorted(({"h": int(hladiny[N]), "N": N, "ha": round(_plocha_ha(s)),
                                   "g": {"type": "MultiPolygon", "coordinates": s}}
                                  for N, usek, s in _uzemi() if usek == cil), key=lambda u: u["h"])}
    if _dem(cil):
        hodnoty = [v for v in H + Pr if v is not None]
        od_cm, do_cm = min(hodnoty) - OKOLI_DEM, max(hodnoty) + OKOLI_DEM
        urovne = [u for u in _dem(cil) if od_cm <= u["h"] <= do_cm] or [_dem_pro(cil, min(hodnoty))]
        if hrube or len(json.dumps(urovne)) > MAX_DEM:
            urovne = [u for u in urovne if u["h"] % 20 == 0]
        rozlivy["dem"] = urovne
    return {"mesto": MESTA[cil], "H": H, "P": Pr, "spa": SPA[cil], "rozlivy": rozlivy,
            "vrchol": max(range(len(H)), key=lambda i: -1 if H[i] is None else H[i])}


BEZ_TOKENU = """<!doctype html><html lang="cs"><meta charset="utf-8">
<body style="margin:0;padding:24px;background:#f5f5f7;color:#1d1d1f;font:17px/1.5 -apple-system,BlinkMacSystemFont,'SF Pro Text','Helvetica Neue',Inter,Helvetica,sans-serif">
Mapa v Mapbox GL potřebuje MAPBOX_TOKEN v souboru .env. Bez něj použijte mapu z mapa.py.</body></html>"""

STRANKA = r"""<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Labe · mapa povodně</title>
__IKONA__
__PISMA__
<link href="__MAPBOX__/mapbox-gl.css" rel="stylesheet">
<script src="__MAPBOX__/mapbox-gl.js"></script>
__POROVNANI__
<style>
:root {
  --pozadi: #f5f5f7;
  --sklo: rgba(255, 255, 255, 0.58);
  --sklo-hrana: inset 0 1px 0 rgba(255, 255, 255, 0.75), 0 0 0 1px rgba(255, 255, 255, 0.35), 0 12px 40px rgba(0, 0, 0, 0.18);
  --linka: rgba(29, 29, 31, 0.12);
  --karta: #ffffff;
  --okraj: #e5e5ea;
  --okraj-silny: #d2d2d7;
  --draha: #e9e9eb;
  --text: #1d1d1f;
  --tlumene: #6e6e73;
  --terciarni: #86868b;
  --modra: #167c9c;
  --modra-tmava: #136b88;
  --modra-svetla: #9fcad8;
  --oranzova: #cb6c31;
  --stin: 0 1px 2px rgba(0, 0, 0, 0.04), 0 10px 30px rgba(0, 0, 0, 0.06);
  --stin-segment: 0 1px 2px rgba(0, 0, 0, 0.1), 0 3px 8px rgba(0, 0, 0, 0.08);
  --r: 24px;
  --ven: cubic-bezier(0.16, 1, 0.3, 1);
  --pismo: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Helvetica Neue", "Inter", Helvetica, sans-serif;
  --lista: 0px;  /* výška přehrávače nad tiráží, nastaví ji skript */
  color-scheme: light;
}
* { box-sizing: border-box; }
html, body { margin: 0; height: 100%; background: var(--pozadi); color: var(--text); overflow: hidden;
  font: 14px/1.45 var(--pismo); -webkit-font-smoothing: antialiased; }
.datum, .cas, .cm, .hlava span, .najeti span, .prah span, .vrchol span, .dny, #stitky span { font-variant-numeric: tabular-nums; }
#mapy, .mapa { position: absolute; inset: 0; }
#mapa-b { display: none; }
button { font: inherit; color: inherit; cursor: pointer; -webkit-tap-highlight-color: transparent; }
button:focus-visible { outline: 2px solid var(--modra); outline-offset: 2px; }
/* Liquid Glass: průsvitné sklo, mapa pod ním prosvítá; světelná hrana nahoře, vlasová linka kolem a měkký stín.
   Lehký bílý nádech shora drží text čitelný i nad tmavou mapou za soumraku. */
.sklo { position: absolute; z-index: 2; border: 0; border-radius: var(--r); color: var(--text);
  background: linear-gradient(rgba(255, 255, 255, 0.24), rgba(255, 255, 255, 0) 60%), var(--sklo);
  backdrop-filter: blur(28px) saturate(1.7); -webkit-backdrop-filter: blur(28px) saturate(1.7); box-shadow: var(--sklo-hrana); }
/* vlevo nahoře: jen tři pohledy jako segmentovaný přepínač */
.vlevo { top: 12px; left: 12px; padding: 4px; }
.segment { display: flex; gap: 2px; }
.segment button { flex: 1 1 auto; min-height: 36px; padding: 6px 14px; font-size: 13px; font-weight: 600; white-space: nowrap;
  color: var(--tlumene); background: transparent; border: 0; border-radius: 18px;
  transition: background-color 0.2s ease-out, color 0.2s ease-out, box-shadow 0.2s ease-out, transform 0.1s ease-out; }
.segment button:hover { color: var(--text); }
.segment button:active { transform: scale(0.97); }
.segment button[aria-pressed="true"] { color: var(--text); background: rgba(255, 255, 255, 0.92); box-shadow: var(--stin-segment); }
/* vpravo nahoře: datum a hodina přehrávaného okamžiku, pod tím přepínače zobrazení */
.vpravo { top: 12px; right: 12px; width: 272px; padding: 14px 16px 8px; max-height: calc(100% - 56px - var(--lista)); overflow: auto; }
.vpravo::-webkit-scrollbar { width: 6px; }
.vpravo::-webkit-scrollbar-thumb { background: var(--okraj-silny); border-radius: 3px; }
.prepinace { padding: 2px 0; }
/* animace: vpravo nahoře pilulka s okamžikem a kulaté tlačítko, přepínače zobrazení až na rozbalení */
.okamzik { top: 12px; right: 64px; height: 44px; display: flex; align-items: center; gap: 6px; padding: 0 18px; border-radius: 22px;
  font-size: 17px; font-weight: 700; letter-spacing: -0.02em; white-space: nowrap; font-variant-numeric: tabular-nums; }
.okamzik span { color: var(--tlumene); font-weight: 600; }
.animace .nastaveni-tlacitko { display: grid; }
.animace .vpravo { top: 64px; right: 12px; width: min(272px, calc(100vw - 24px)); padding: 6px 16px; max-height: calc(100% - 108px - var(--lista));
  transform-origin: top right; opacity: 0; visibility: hidden; transform: translateY(-6px) scale(0.96);
  transition: opacity 0.2s ease-out, transform 0.24s var(--ven), visibility 0s linear 0.24s; }
.animace .vpravo.otevrene { opacity: 1; visibility: visible; transform: none;
  transition: opacity 0.2s ease-out, transform 0.24s var(--ven), visibility 0s; }
.prepinac { display: flex; align-items: center; justify-content: space-between; gap: 12px; width: 100%; min-height: 34px; padding: 0;
  font-size: 14px; font-weight: 500; text-align: left; background: transparent; border: 0; border-radius: 8px; }
.prepinac:disabled { opacity: 0.4; cursor: default; }
.prepinac span:last-child { position: relative; flex: none; width: 34px; height: 20px; border-radius: 10px; background: rgba(29, 29, 31, 0.2);
  box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.08); transition: background-color 0.2s ease-out; }
.prepinac span:last-child::after { content: ""; position: absolute; top: 2px; left: 2px; width: 16px; height: 16px; border-radius: 50%;
  background: #fff; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.25); transition: transform 0.22s var(--ven); }
.prepinac[aria-checked="true"] span:last-child { background: var(--modra); }
.prepinac[aria-checked="true"] span:last-child::after { transform: translateX(14px); }
.nastaveni-tlacitko { display: none; top: 12px; right: 12px; width: 44px; height: 44px; padding: 0; border-radius: 50%; z-index: 3;
  place-items: center; transition: transform 0.1s ease-out; }
.nastaveni-tlacitko:active { transform: scale(0.94); }
.nastaveni-tlacitko svg { width: 20px; height: 20px; fill: none; stroke: currentColor; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
/* karta předpovědi statické mapy (bez animace) */
h2 { margin: 0 0 8px; font-size: 13px; font-weight: 600; color: var(--tlumene); }
.datum { font-size: 19px; font-weight: 700; letter-spacing: -0.02em; line-height: 1.15; }
.radek { display: flex; align-items: baseline; gap: 8px; margin-top: 8px; }
.radek .jmeno { flex: 1; color: var(--tlumene); }
.radek .jmeno b { color: var(--text); font-weight: 600; }
.cm { font-size: 22px; font-weight: 800; letter-spacing: -0.03em; line-height: 1.1; }
.cm.pred { color: var(--modra); }
.odznak { font-size: 13px; font-weight: 700; padding: 3px 10px; border-radius: 999px; white-space: nowrap; line-height: 1.2; }
.mesto + .mesto { margin-top: 8px; padding-top: 8px; border-top: 1px solid var(--linka); }
.maly { margin-top: 3px; font-size: 12.5px; color: var(--tlumene); }
/* přehrávač dole bez karty: pod ním jen tmavý přechod kvůli čitelnosti; křivka se kreslí, jak povodeň běží */
.stin-dole { position: absolute; left: 0; right: 0; bottom: 0; height: calc(var(--lista) + 170px); z-index: 1; pointer-events: none;
  background: linear-gradient(to top, rgba(8, 12, 20, 0.66), rgba(8, 12, 20, 0.3) 55%, rgba(8, 12, 20, 0)); }
.lista { position: absolute; left: 20px; right: 20px; bottom: 32px; z-index: 3; padding: 30px 0 6px; display: grid;
  grid-template-columns: auto 1fr auto; column-gap: 18px; align-items: center; color: #fff; }
.hraj { width: 54px; height: 54px; border-radius: 50%; border: 0; background: var(--modra); color: #fff; display: grid; place-items: center;
  box-shadow: 0 4px 16px rgba(22, 124, 156, 0.45); transition: background-color 0.2s ease-out, transform 0.1s ease-out; }
.hraj:hover { background: var(--modra-tmava); }
.hraj:active { transform: scale(0.95); }
.hraj svg { width: 22px; height: 22px; fill: currentColor; }
.kulate { width: 44px; height: 44px; padding: 0; border-radius: 50%; border: 0; display: grid; place-items: center; color: #fff;
  background: rgba(255, 255, 255, 0.14); box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.22);
  backdrop-filter: blur(16px) saturate(1.6); -webkit-backdrop-filter: blur(16px) saturate(1.6);
  transition: background-color 0.2s ease-out, transform 0.1s ease-out; }
.kulate:hover { background: rgba(255, 255, 255, 0.24); }
.kulate:active { transform: scale(0.94); }
.kulate svg { width: 20px; height: 20px; fill: none; stroke: currentColor; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
.osa { position: relative; height: 74px; cursor: pointer; touch-action: none; border-radius: 4px;
  background: linear-gradient(rgba(255, 255, 255, 0.32), rgba(255, 255, 255, 0.32)) 0 100% / 100% 1px no-repeat,
    repeating-linear-gradient(to top, transparent 0 calc(25% - 1px), rgba(255, 255, 255, 0.06) calc(25% - 1px) 25%); }
.osa:focus-visible { outline: 2px solid #fff; outline-offset: 4px; }
.graf { position: absolute; inset: 0; pointer-events: none; }
.graf svg, .uvod-graf svg { position: absolute; inset: 0; width: 100%; height: 100%; overflow: visible; }
.graf .h { filter: drop-shadow(0 0 3px rgba(255, 255, 255, 0.6)); }
.prah { position: absolute; left: 0; right: 0; border-top: 1px dashed var(--c); opacity: 0.9; }
.prah span { position: absolute; left: calc(6px + var(--k) * 88px); bottom: 2px; padding: 1px 7px; border-radius: 999px;
  background: var(--c); color: var(--t, #fff); font-size: 10.5px; font-weight: 700; white-space: nowrap; z-index: 1; }
.prah i { font-style: normal; }
.lista .prah { border-top-color: color-mix(in srgb, var(--c) 65%, transparent); opacity: 1; }
.lista .prah span { left: calc(4px + var(--k) * 80px); padding: 0 6px; font-size: 10px; line-height: 15px; opacity: 0.85; }
.vrchol { position: absolute; top: 0; bottom: 0; border-left: 1px solid rgba(29, 29, 31, 0.35); }
.vrchol span { position: absolute; top: 3px; left: 6px; padding: 1px 8px; border-radius: 999px; background: rgba(255, 255, 255, 0.72);
  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.5), 0 1px 4px rgba(0, 0, 0, 0.12); font-size: 11px; font-weight: 600; white-space: nowrap; }
.vrchol.vlevo-od span { left: auto; right: 6px; }
.lista .vrchol { border-left-color: rgba(255, 255, 255, 0.4); opacity: 0; transition: opacity 0.5s ease-out; }
.lista .vrchol span { color: var(--text); }
.lista .vrchol.videt { opacity: 1; }
.pasmo { position: absolute; left: 0; right: 0; bottom: -8px; height: 3px; border-radius: 2px; overflow: hidden;
  background: rgba(255, 255, 255, 0.14); pointer-events: none; }
.pasmo > div { position: absolute; inset: 0; }
.pasmo i { position: absolute; top: 0; bottom: 0; }
.hlava { position: absolute; top: -5px; bottom: -9px; width: 1px; margin-left: -0.5px; background: rgba(255, 255, 255, 0.45); pointer-events: none; }
.hlava i { position: absolute; left: 50%; width: 12px; height: 12px; margin: -6px 0 0 -6px; border-radius: 50%; background: #fff;
  box-shadow: 0 0 0 3px var(--modra), 0 0 14px 5px rgba(159, 202, 216, 0.7); }
.hlava i::after { content: ""; position: absolute; inset: -3px; border-radius: 50%; border: 2px solid rgba(159, 202, 216, 0.9); opacity: 0; }
.hraje .hlava i::after { animation: puls 1.6s var(--ven) infinite; }
@keyframes puls { 0% { transform: scale(1); opacity: 0.9; } 100% { transform: scale(2.6); opacity: 0; } }
.hlava span, .najeti span { position: absolute; bottom: calc(100% + 8px); left: 50%; transform: translateX(-50%); padding: 3px 10px;
  border-radius: 999px; background: rgba(255, 255, 255, 0.82); color: var(--text); font-size: 12.5px; font-weight: 600; line-height: 1.3;
  white-space: nowrap; backdrop-filter: blur(16px) saturate(1.6); -webkit-backdrop-filter: blur(16px) saturate(1.6);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.85), 0 0 0 1px rgba(255, 255, 255, 0.45), 0 4px 14px rgba(0, 0, 0, 0.16); }
.hlava span { transition: opacity 0.2s ease-out; }
.kraj-l span { left: -1px; transform: none; }
.kraj-p span { left: auto; right: -1px; transform: none; }
.osa.najizdi .hlava span { opacity: 0; }
.najeti { position: absolute; top: 0; bottom: 0; width: 1px; background: rgba(255, 255, 255, 0.4); pointer-events: none; display: none; }
.dny { grid-column: 2; position: relative; height: 15px; margin-top: 10px; font-size: 11.5px; color: rgba(255, 255, 255, 0.78); }
.dny span { position: absolute; top: 0; transform: translateX(-50%); white-space: nowrap; }
/* úvodní okno animace */
.uvod { position: absolute; inset: 0; z-index: 10; display: grid; place-items: center; padding: 16px;
  background: rgba(245, 245, 247, 0.6); backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px); transition: opacity 0.3s ease-out; }
.uvod.pryc { opacity: 0; pointer-events: none; }
.uvod-karta { width: min(640px, 100%); max-height: 100%; overflow: auto; padding: 28px 32px 24px; background: var(--karta);
  border: 1px solid var(--okraj); border-radius: var(--r); box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04), 0 24px 60px rgba(0, 0, 0, 0.12); }
.uvod h1 { margin: 0; font-size: 44px; font-weight: 700; letter-spacing: -0.02em; line-height: 1.05; text-wrap: balance; }
.uvod h1 span { color: var(--tlumene); font-weight: 600; }
.uvod-rozsah { margin: 12px 0 0; color: var(--tlumene); font-size: 15px; }
.uvod-rozsah b { color: var(--text); font-weight: 600; }
.uvod-graf { position: relative; height: 124px; margin-top: 36px; background: var(--karta); border: 1px solid var(--okraj); border-radius: 12px; }
/* v úvodu je štítek vrcholu nad grafem, ať nezakryje popisky stupňů */
.uvod-graf .vrchol { top: -22px; }
.uvod-graf .vrchol span { top: 0; }
.uvod-hraj { margin-top: 20px; width: 100%; height: 56px; display: flex; align-items: center; justify-content: center; gap: 10px;
  border: 0; border-radius: 999px; background: var(--modra); color: #fff; font-size: 18px; font-weight: 600; letter-spacing: -0.01em;
  transition: background-color 0.2s ease-out, transform 0.1s ease-out; }
.uvod-hraj:hover { background: var(--modra-tmava); }
.uvod-hraj:active { transform: scale(0.98); }
.uvod-hraj svg { width: 20px; height: 20px; fill: currentColor; }
/* porovnání: popisky stran u dělicí čáry (hodnoty má štítek na ose) a výrazné držadlo */
#stitky { position: absolute; top: 16px; left: 0; right: 0; height: 40px; display: none; overflow: hidden; pointer-events: none; z-index: 2; }
#stitky span { position: absolute; top: 0; display: flex; align-items: center; gap: 8px; white-space: nowrap; padding: 8px 14px;
  border-radius: 999px; background: var(--sklo); border: 0; font-size: 13px; font-weight: 600;
  box-shadow: var(--sklo-hrana); backdrop-filter: blur(28px) saturate(1.7); -webkit-backdrop-filter: blur(28px) saturate(1.7); }
#stitky i { font-style: normal; }
#stitky svg { width: 14px; height: 14px; fill: currentColor; }
#st-pred { right: calc(100% - var(--x, 50%) + 14px); color: var(--modra); }
#st-skut { left: calc(var(--x, 50%) + 14px); }
/* dělicí čára porovnání je neviditelná, zůstává jen kulatý úchyt a štítky nahoře */
.mapboxgl-compare { width: 0; background: transparent; box-shadow: none; }
.mapboxgl-compare .compare-swiper-vertical { width: 54px; height: 54px; left: -27px; margin: -27px 0 0 1.5px;
  background-color: #fff; background-size: 54px 54px; background-position: center;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 54 54'%3E%3Cpath d='M23 18l-9 9 9 9zM31 18l9 9-9 9z' fill='%231d1d1f'/%3E%3C/svg%3E");
  box-shadow: 0 0 0 1px var(--okraj-silny), 0 8px 22px rgba(0, 0, 0, 0.22); }
/* tiráž: nezakryje logo Mapboxu a když se nevejde na řádek, zalomí se na dva vyrovnané */
.mapboxgl-ctrl-bottom-right .mapboxgl-ctrl-attrib:not(.mapboxgl-compact) { max-width: calc(100vw - 120px); text-align: right;
  text-wrap: balance; }
.mapboxgl-map, .mapboxgl-ctrl-attrib { font-family: var(--pismo); }
.mapboxgl-popup-content { background: var(--karta); color: var(--text); font: 13.5px/1.45 var(--pismo);
  border-radius: 14px; padding: 10px 30px 10px 14px; border: 1px solid var(--okraj); box-shadow: var(--stin); }
.mapboxgl-popup-close-button { color: var(--tlumene); font-size: 18px; padding: 0 8px; border-radius: 0 14px 0 10px; }
.mapboxgl-popup-close-button:hover { background: var(--draha); }
.mapboxgl-popup-anchor-top .mapboxgl-popup-tip, .mapboxgl-popup-anchor-top-left .mapboxgl-popup-tip,
.mapboxgl-popup-anchor-top-right .mapboxgl-popup-tip { border-bottom-color: #fff; }
.mapboxgl-popup-anchor-bottom .mapboxgl-popup-tip, .mapboxgl-popup-anchor-bottom-left .mapboxgl-popup-tip,
.mapboxgl-popup-anchor-bottom-right .mapboxgl-popup-tip { border-top-color: #fff; }
.mapboxgl-popup-anchor-left .mapboxgl-popup-tip { border-right-color: #fff; }
.mapboxgl-popup-anchor-right .mapboxgl-popup-tip { border-left-color: #fff; }
/* užší okno: štítky porovnání pod řádkem boxů, pak nad přehrávačem */
@media (max-width: 1100px) {
  #stitky { top: 68px; }
}
@media (max-width: 900px) {
  #stitky { top: auto; bottom: calc(var(--lista) + 44px); }
  body:not(.animace) .vpravo { top: auto; bottom: 34px; left: 12px; right: 12px; width: auto; max-height: 42%; }
  .lista { left: 12px; right: 12px; padding: 28px 0 6px; column-gap: 12px; }
  .hraj { width: 46px; height: 46px; }
  .kulate { width: 40px; height: 40px; }
}
/* telefon: pohledy jako pás nahoře vedle ikony, přehrávač nižší */
@media (max-width: 740px) {
  .vlevo { right: 64px; padding: 3px; overflow-x: auto; scrollbar-width: none; }
  .vlevo::-webkit-scrollbar { display: none; }
  .segment button { min-height: 34px; padding: 6px 10px; font-size: 12.5px; border-radius: 17px; }
  .uvod h1 { font-size: 32px; }
  .uvod-karta { padding: 18px 18px 0; border-radius: 18px; }
  .uvod-graf { height: 84px; margin-top: 32px; }
  .uvod-hraj { position: sticky; bottom: 0; height: 52px; font-size: 17px; margin-top: 14px; box-shadow: 0 -12px 16px rgba(255, 255, 255, 0.95); }
  .uvod-karta::after { content: ""; display: block; height: 14px; }
  .okamzik { top: 58px; right: auto; left: 12px; height: 36px; padding: 0 14px; font-size: 15px; }
  .animace .vpravo { top: 102px; }
  .lista .prah span { left: calc(4px + var(--k) * 34px); }
  .lista .prah i { display: none; }
  .lista .vrchol span { display: none; }  /* na telefonu by překryl pilulky stupňů, čára stačí */
  .osa { height: 54px; }
  .dny { margin-top: 9px; }
  #st-pred i { display: none; }
}
@media (max-height: 520px) {
  .uvod h1 { font-size: 28px; }
  .uvod-graf { display: none; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { transition-duration: 0.01ms !important; }
  .hraje .hlava i::after { animation: none; }
}
@media (prefers-reduced-transparency: reduce) {
  .sklo, .hlava span, .najeti span, #stitky span { background: rgba(255, 255, 255, 0.96); backdrop-filter: none; -webkit-backdrop-filter: none; }
  .kulate { background: rgba(29, 29, 31, 0.8); backdrop-filter: none; -webkit-backdrop-filter: none; }
}
</style>
</head>
<body>
<div id="mapy"><div class="mapa" id="mapa"></div><div class="mapa" id="mapa-b"></div></div>
<div id="stitky"><span id="st-pred"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-8 7 8 7z"/></svg>Předpověď<i>&nbsp;24&nbsp;h předem</i></span><span id="st-skut">Skutečnost<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5l8 7-8 7z"/></svg></span></div>
<nav class="sklo vlevo" id="vlevo" aria-label="Pohled"></nav>
<div class="sklo okamzik" id="okamzik" hidden><b id="p-den"></b><span id="p-hodina"></span></div>
<aside class="sklo vpravo" id="vpravo"></aside>
<button class="sklo nastaveni-tlacitko" id="nastaveni-tlacitko" aria-controls="vpravo" aria-expanded="false" aria-label="Zobrazení"></button>
<script type="application/json" id="data">__DATA__</script>
<script>
const D = JSON.parse(document.getElementById('data').textContent);
const A = D.anim;  // jen v animaci: hodinové řady
mapboxgl.accessToken = D.token;
const STUPNE = ['bez stupně', '1. stupeň', '2. stupeň', '3. stupeň'];
const css = c => `rgb(${c[0]},${c[1]},${c[2]})`;
const cislo = v => v == null ? '–' : Math.round(v).toLocaleString('cs-CZ');
const znamenko = v => v == null ? '–' : (v > 0 ? '+' : v < 0 ? '−' : '±') + Math.abs(Math.round(v)).toLocaleString('cs-CZ');
const PRAZDNE = {type: 'FeatureCollection', features: []};
const STYL = {standard: 'mapbox://styles/mapbox/standard', satelit: 'mapbox://styles/mapbox/standard-satellite'};
const DEM = Boolean(A ? Object.values(A.rady).some(r => r.rozlivy.dem) : D.dem);  // máme rozliv z výškového modelu
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
// podklad: pevně soumrak a výchozí téma (nepřepínají se); zobrazení přepíná pravý box, výchozí jsou popisky míst a 3D objekty
const N = {svetlo: 'dusk', tema: 'default', satelit: false, mista: true, poi: false, objekty: true, ulice: false, uredni: false};
// vlastní budovy podle světla Standardu: den světle šedé jako Apple Maps, noc tmavě modrošedé. Za šera bez vlastního svitu,
// takže je nasvítí stejné slunce jako budovy Standardu (hnědé se stíny) a při přiblížení přes zoom 15 není vidět přechod.
const BUDOVY = {dawn: ['#e2e5ea', 0.45], day: ['#e6e6eb', 0.15], dusk: ['#e6e1da', 0], night: ['#4a5b74', 0.8]};
// západ slunce místo předvolby soumraku (ta byla tmavá jako noc): nízké teplé slunce od západojihozápadu s dlouhými stíny,
// fialové okolní světlo ve stínech a oranžový opar u obzoru; na satelitu zůstává jeho vlastní světlo
const ZAPAD = {
  svetla: [{id: 'okoli', type: 'ambient', properties: {color: 'hsl(255, 20%, 62%)', intensity: 0.42}},
           {id: 'slunce', type: 'directional', properties: {color: 'hsl(28, 98%, 67%)', intensity: 0.92, direction: [250, 78],
             'cast-shadows': true, 'shadow-intensity': 1}}],
  mlha: {color: 'hsl(26, 65%, 74%)', 'high-color': 'hsl(18, 85%, 60%)', 'horizon-blend': 0.15, 'space-color': 'hsl(240, 40%, 20%)',
         'star-intensity': 0, range: [1, 12]}};
// popisky stanic: na světlé mapě tmavé s bílým lemem, za šera, v noci a na satelitu bílé s tmavým lemem
const popisky = m => m.satelit || N.svetlo === 'dusk' || N.svetlo === 'night'
  ? ['#ffffff', 'rgba(29, 29, 31, 0.9)'] : ['#1d1d1f', 'rgba(255, 255, 255, 0.95)'];
const uredni = () => N.uredni || !DEM;  // úřední N-letá území místo rozlivu z terénu
function nastavZdroj() {
  if (A) for (const r of Object.values(A.rady)) { r.zdroj = uredni() || !r.rozlivy.dem ? 'dibavod' : 'dem'; r.urovne = r.rozlivy[r.zdroj]; }
}
nastavZdroj();
const SIROKO = innerWidth > 900;  // stejná hranice jako v CSS: od 900 px dolů je karta předpovědi dole

const IKONY = {nastaveni: '<path d="M4 7h8M17 7h3M4 17h3M12 17h8"/><circle cx="14" cy="7" r="2.5"/><circle cx="9" cy="17" r="2.5"/>',
               zavrit: '<path d="M6 6l12 12M18 6L6 18"/>',
               cela: '<path d="M4 9V4h5M15 4h5v5M20 15v5h-5M9 20H4v-5"/>',
               zmensit: '<path d="M9 4v5H4M20 9h-5V4M15 20v-5h5M4 15h5v5"/>'};
const svg = (d, vb = 24) => `<svg viewBox="0 0 ${vb} ${vb}" aria-hidden="true">${d}</svg>`;

function kamera(pohled) {
  // střed záběru nad přehrávačem (a vedle karty předpovědi); celé povodí se musí vejít i do užšího okna
  const k = {...D.kamery[pohled], padding: SIROKO ? {top: 0, bottom: A ? 180 : 40, left: 0, right: A ? 0 : 315} : {top: 0, bottom: A ? 170 : 220, left: 0, right: 0}};
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
  return m;
}

function pridejVrstvy(m) {
  m.nacteno = true;
  for (const [klic, hodnota] of Object.entries(konfigurace(m.satelit))) m.setConfigProperty('basemap', klic, hodnota);
  if (!m.satelit) { m.setLights(ZAPAD.svetla); m.setFog(ZAPAD.mlha); }
  m.addSource('vysky', {type: 'raster-dem', url: 'mapbox://mapbox.mapbox-terrain-dem-v1', tileSize: 512, maxzoom: 14});
  m.setTerrain({source: 'vysky', exaggeration: 1.6});

  // voda ve slotu middle: nad terénem a silnicemi, pod budovami a popisky, takže domy stojí ve vodě
  if (D.uzemi) {
    m.addSource('uzemi', {type: 'geojson', data: D.uzemi});
    m.addLayer({id: 'uzemi', type: 'fill', source: 'uzemi', slot: 'middle', paint: {
      'fill-color': ['case', ['get', 'plne'], '#167c9c', '#9fcad8'],
      'fill-opacity': ['case', ['get', 'plne'], 0.58, A ? 0.12 : 0.2], 'fill-emissive-strength': 0.8
    }});
    m.addLayer({id: 'uzemi-obrys', type: 'line', source: 'uzemi', slot: 'middle', paint: {
      'line-color': ['case', ['get', 'plne'], '#0e5d77', '#167c9c'], 'line-emissive-strength': 1,
      'line-width': ['interpolate', ['linear'], ['zoom'], 10, 0.5, 15, 1.6], 'line-opacity': 0.8
    }});
  }
  m.addSource('rozliv', {type: 'geojson', data: A ? PRAZDNE : (D.dem ?? PRAZDNE)});
  m.addLayer({id: 'rozliv', type: 'fill', source: 'rozliv', slot: 'middle', paint: {
    'fill-color': '#167c9c', 'fill-opacity': 0.62, 'fill-emissive-strength': 0.8}});
  m.addLayer({id: 'rozliv-obrys', type: 'line', source: 'rozliv', slot: 'middle', paint: {
    'line-color': '#0e5d77', 'line-width': ['interpolate', ['linear'], ['zoom'], 10, 0.6, 15, 1.8],
    'line-opacity': 0.85, 'line-emissive-strength': 1}});
  if (D.skut) {
    // skutečný rozliv o 24 h později čárkovaně přes předpověď (jen v archivu, kde ho známe)
    m.addSource('skutecnost', {type: 'geojson', data: D.skut});
    m.addLayer({id: 'skutecnost', type: 'line', source: 'skutecnost', slot: 'middle', paint: {
      'line-color': '#1d1d1f', 'line-width': 2, 'line-dasharray': [2, 1.5], 'line-opacity': 0.9, 'line-emissive-strength': 1}});
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
      'fill-extrusion-vertical-gradient': N.svetlo !== 'dusk', 'fill-extrusion-ambient-occlusion-intensity': 0.35,
      // satelit 3D budovy nemá, tam zůstanou naše; ve Standardu se prolnou s jeho budovami (ty najíždějí 15 až 15,3)
      'fill-extrusion-opacity': m.satelit ? 1 : ['interpolate', ['linear'], ['zoom'], 15, 1, 15.3, 0]
    }});
  m.addSource('reky', {type: 'geojson', data: D.reky});
  m.addLayer({id: 'reky', type: 'line', source: 'reky', slot: 'middle', layout: {'line-join': 'round', 'line-cap': 'round'}, paint: {
    'line-color': '#167c9c', 'line-emissive-strength': 1,
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
  }, paint: {'text-color': popisky(m)[0], 'text-halo-color': popisky(m)[1], 'text-halo-width': 1.6,
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

const k0 = kamera(D.pohled);
const mapaA = vytvorMapu('mapa', k0);
mapaA.satelit = N.satelit;
let mapaB = null, porovnani = null;
const mapy = () => mapaB && rezim === 'porovnani' ? [mapaA, mapaB] : [mapaA];

// ---------- animace: hodinové řady ----------
const K = A ? A.popisky.length - 1 : 0;
let cas = A ? A.start : 0, rezim = A ? 'animace' : null;
let R = A ? A.rady[A.cil] : null;  // řada v grafu přehrávače: město pohledu, na celém povodí město stránky
let priZmeneMesta = () => {};
let hraje = false, rychlost = 6;  // rychlost v hodinách povodně za sekundu
const podle = 'skutecnost';  // jednu mapu plní změřená hladina, předpověď je v porovnání vlevo
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

// index úrovně rozlivu města r pro hladinu h: z terénu nejbližší hladina, z DIBAVOD největší dosažené území (-1 = nic)
function uroven(r, h) {
  if (h == null) return -1;
  const U = r.urovne;
  if (r.zdroj === 'dem') {
    let a = 0, b = U.length - 1;
    while (b - a > 1) { const c = (a + b) >> 1; if (U[c].h <= h) a = c; else b = c; }
    return Math.abs(U[a].h - h) <= Math.abs(U[b].h - h) ? a : b;
  }
  let k = -1;
  U.forEach((u, i) => { if (h >= u.h) k = i; });
  return k;
}
const hladinaMapy = (m, r, i) => (m === mapaB || (rezim !== 'porovnani' && podle === 'skutecnost')) ? r.H[i] : r.P[i];

function obnovMapu(m, i) {
  if (!m.getSource('stanice')) return;
  if (m.hodina !== i) { m.getSource('stanice').setData(staniceV(i)); m.hodina = i; }
  const rady = Object.values(A.rady), k = rady.map(r => uroven(r, hladinaMapy(m, r, i)));
  if (k.join() === m.klic) return;  // polygony se mění jen při změně úrovně, ne každou hodinu
  m.klic = k.join();
  m.getSource('rozliv').setData({type: 'FeatureCollection', features: rady.flatMap((r, j) => {
    const u = r.urovne[k[j]];
    return u ? [{type: 'Feature', geometry: u.g, properties: {tooltip: `${r.mesto}: ` + (r.zdroj === 'dem' ?
      `rozliv z výškového modelu (ČÚZK DMR 5G) pro hladinu ${u.h} cm, ${cislo(u.ha)} ha<br>Statický rozliv, bez proudění a hrází` :
      `záplavové území Q${u.N} (DIBAVOD, VÚV TGM), ${cislo(u.ha)} ha<br>Vyplní se od hladiny ${u.h} cm podle ČHMÚ`)}}] : [];
  })});
}

// ---------- pohledy: prelet(pohled) pro nahrávání videa a deck, bez tlačítek ----------
let pohled = D.pohled;
function prelet(p) {
  pohled = p;
  oznacPohled(p);
  if (A) priZmeneMesta(p);
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

// ---------- levý box: tři pohledy jako segmentovaný přepínač ----------
const vlevo = document.getElementById('vlevo'), vpravo = document.getElementById('vpravo');
vlevo.innerHTML = `<div class="segment" role="group">${D.pohledy.map(([id, nazev]) =>
  `<button data-id="${id}" aria-pressed="false">${nazev.replaceAll(' ', '\u00a0')}</button>`).join('')}</div>`;
function oznacPohled(p) { for (const b of vlevo.querySelectorAll('button')) b.setAttribute('aria-pressed', b.dataset.id === p); }
vlevo.addEventListener('click', e => { const b = e.target.closest('button'); if (b && b.dataset.id !== pohled) prelet(b.dataset.id); });
oznacPohled(pohled);

// ---------- pravý box: v animaci datum a přepínače zobrazení, na statické mapě karta předpovědi ----------
const PREPINACE = [['satelit', 'Satelit'], ['mista', 'Popisky míst'], ['poi', 'Zajímavá místa'], ['objekty', '3D objekty'],
                   ['ulice', 'Názvy ulic'], ['uredni', 'Úřední území']];
const prepinac = (id, nazev) => `<button class="prepinac" role="switch" aria-checked="false" data-id="${id}">` +
  `<span>${nazev.replaceAll(' ', '\u00a0')}</span><span></span></button>`;
const tlacitkoBoxu = document.getElementById('nastaveni-tlacitko');
if (A) {
  document.body.classList.add('animace');
  document.getElementById('okamzik').hidden = false;
  vpravo.innerHTML = `<div class="prepinace">${PREPINACE.map(([id, nazev]) => prepinac(id, nazev)).join('')}</div>`;
  // přepínače zobrazení jsou sbalené za kulatou ikonou; zavře je i klik mimo nebo Esc
  const otevriBox = ano => {
    vpravo.classList.toggle('otevrene', ano);
    tlacitkoBoxu.setAttribute('aria-expanded', ano);
    tlacitkoBoxu.innerHTML = svg(ano ? IKONY.zavrit : IKONY.nastaveni);
  };
  otevriBox(false);
  tlacitkoBoxu.addEventListener('click', () => otevriBox(!vpravo.classList.contains('otevrene')));
  document.addEventListener('pointerdown', e => {
    if (vpravo.classList.contains('otevrene') && !vpravo.contains(e.target) && !tlacitkoBoxu.contains(e.target)) otevriBox(false);
  });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && vpravo.classList.contains('otevrene')) { otevriBox(false); tlacitkoBoxu.focus(); }
  });
} else {
  vpravo.innerHTML = '<section><h2>Předpověď</h2><div id="panel"></div></section>';
  tlacitkoBoxu.remove();
  document.getElementById('okamzik').remove();
}

function nastaveni() {
  for (const b of vpravo.querySelectorAll('.prepinac[role="switch"]')) {
    const id = b.dataset.id;
    b.setAttribute('aria-checked', id === 'uredni' ? uredni() : N[id]);
    b.disabled = (id === 'objekty' && N.satelit) || (id === 'uredni' && !DEM);  // satelit 3D objekty nemá; bez terénu jsou území vždy
  }
}
function podklad(klic, hodnota) {
  for (const m of [mapaA, mapaB].filter(Boolean)) if (m.nacteno) m.setConfigProperty('basemap', klic, hodnota);
}
function budovy() {
  for (const m of [mapaA, mapaB].filter(Boolean)) if (m.nacteno && m.getLayer('budovy')) {
    m.setLayoutProperty('budovy', 'visibility', m.satelit || N.objekty ? 'visible' : 'none');
  }
}
const KONFIG = {mista: ['showPlaceLabels'], poi: ['showPointOfInterestLabels', 'showTransitLabels'], objekty: ['show3dObjects'],
                ulice: ['showRoadLabels']};
vpravo.addEventListener('click', e => {
  const b = e.target.closest('.prepinac');
  if (!b || b.disabled) return;
  const id = b.dataset.id;
  N[id] = !N[id];
  if (id === 'satelit') {
    // jiný styl: naše zdroje a vrstvy přidá znovu pridejVrstvy po style.load
    for (const m of [mapaA, mapaB].filter(Boolean)) { m.satelit = N.satelit; m.nacteno = false; m.setStyle(STYL[N.satelit ? 'satelit' : 'standard']); }
  } else if (id === 'uredni') {
    nastavZdroj();
    for (const m of [mapaA, mapaB].filter(Boolean)) { viditelnostRozlivu(m); m.klic = undefined; obnovMapu(m, hodina()); }
  } else {
    for (const klic of KONFIG[id]) podklad(klic, N[id]);
    if (id === 'objekty') budovy();
  }
  nastaveni();
});
nastaveni();

function odznak(st) {
  const pozadi = st ? D.spa_barvy[st] : 'var(--draha)', text = st === 1 ? '#1d1d1f' : st ? '#fff' : 'var(--tlumene)';
  return `<span class="odznak" style="background:${pozadi};color:${text}">${st == null ? 'chybí' : STUPNE[st]}</span>`;
}
function panel() {
  if (A) return panelAnimace(hodina());
  const dem = !uredni();
  document.getElementById('panel').innerHTML = `<div class="datum">${D.datum}</div>` + D.mesta.map(m => `
    <div class="mesto">
      <div class="radek"><span class="jmeno"><b>${m.nazev}</b></span><span class="cm">${cislo(m.hladina)} cm</span>${odznak(m.stupen)}</div>
      <div class="radek"><span class="jmeno">${m.predpoved ? `model za ${m.predpoved.h} h` : 'bez předpovědi'}</span>${m.predpoved ?
        `<span class="cm pred">${cislo(m.predpoved.cm)} cm</span>${odznak(m.predpoved.stupen)}` : ''}</div>
      ${dem && m.dem ? `<div class="maly">Pod vodou ${cislo(m.dem.ha)} ha` +
        (m.skut ? ` · pak naměřeno ${cislo(m.skut.cm)} cm, ${cislo(m.skut.ha)} ha` : '') + '</div>' : ''}
    </div>`).join('');
}

function panelAnimace(i) {  // datum a hodina v pravém boxu, hodnota na štítku hlavy osy
  const h = R.H[i], p = R.P[i], c = A.popisky[i].split(' ');  // "17. 1. 2011 05:00 SEČ"
  document.getElementById('p-den').textContent = c.slice(0, 3).join('\u00a0');
  document.getElementById('p-hodina').textContent = '\u00a0· ' + c[3].replace(/^0(?=\d)/, '');
  const stitek = document.getElementById('hlava-stitek');
  if (stitek) stitek.textContent = h == null ? '–' :
    cislo(h) + (rezim === 'porovnani' && p != null ? `\u00a0· předpověď\u00a0${cislo(p)}` : '') + '\u00a0cm';
}

// ---------- porovnání předpověď × skutečnost ----------
function nastavRezim(r) {
  rezim = r;
  const kontejner = document.getElementById('mapa-b');
  if (r === 'porovnani') {
    kontejner.style.display = 'block';
    const c = mapaA.getCenter();
    const k = {center: [c.lng, c.lat], zoom: mapaA.getZoom(), pitch: mapaA.getPitch(), bearing: mapaA.getBearing(), padding: mapaA.getPadding()};
    if (!mapaB) { mapaB = vytvorMapu('mapa-b', k); mapaB.satelit = N.satelit; }
    else { mapaB.resize(); mapaB.jumpTo(k); }
    porovnani = new mapboxgl.Compare(mapaA, mapaB, '#mapy');
    porovnani.setSlider(innerWidth / 2);
    document.getElementById('stitky').style.setProperty('--x', innerWidth / 2 + 'px');
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
  nastaveni();
}

// ---------- přehrávač povodně ----------
const IKONA = {hraj: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 4.5v15l13-7.5z"/></svg>',
               stuj: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 4h4.5v16H6zM13.5 4H18v16h-4.5z"/></svg>',
               znovu: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5V1.5L7 6l5 4.5V7a6 6 0 1 1-6 6H4a8 8 0 1 0 8-8z"/></svg>'};
if (A) {
  let minule = null, nakresleno = -1, tahne = false, uvod = null, yL = null;
  const q = id => document.getElementById(id);
  const procento = i => i / K * 100;
  const casti = i => {
    const c = A.popisky[i].split(' ');  // "17. 1. 2011 05:00 SEČ"
    return {den: c.slice(0, 3).join(' '), hodina: c[3].replace(/^0(?=\d)/, ''), pasmo: c[4]};
  };
  const kratce = i => { const c = casti(i); return `${c.den.replace(/ \d{4}$/, '')} v ${c.hodina}`.replaceAll(' ', ' '); };

  // svislé měřítko grafu města r: od nejnižší hladiny po vrchol s rezervou na popisek, 1. stupeň vždy
  function meritko(r) {
    const hodnoty = r.H.concat(r.P).filter(v => v != null);
    const dno = Math.min(...hodnoty), strop = Math.max(...hodnoty, r.spa[0]);
    return v => 100 - (v - (dno - 0.06 * (strop - dno))) / (1.3 * (strop - dno)) * 100;
  }
  function cesta(rada, y, plocha) {
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
  // prahy jsou u sebe blízko, popisky proto vedle sebe
  const prahy = (r, y) => r.spa.map((v, k) => y(v) < 0 ? '' : `<div class="prah" style="top:${y(v)}%;--c:${D.spa_barvy[k + 1]}">
    <span style="--k:${k};--t:${k ? '#fff' : '#1d1d1f'}"><i>${k + 1}. stupeň </i>${cislo(v)}</span></div>`).join('');
  const vrchol = (r, id = '') => {
    const xv = procento(r.vrchol);
    return `<div class="vrchol${xv > 70 ? ' vlevo-od' : ''}"${id ? ` id="${id}"` : ''} style="left:${xv}%"><span>vrchol ${kratce(r.vrchol)} · ${cislo(r.H[r.vrchol])} cm</span></div>`;
  };
  function grafUvodu(el, r) {  // celá povodeň najednou, tmavě na bílé kartě
    const y = meritko(r);
    el.innerHTML = `<svg viewBox="0 0 1000 100" preserveAspectRatio="none" aria-hidden="true">
        <path d="${cesta(r.H, y, true)}" fill="#167c9c" fill-opacity="0.12"/>
        <path d="${cesta(r.P, y)}" fill="none" stroke="#167c9c" stroke-width="2" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>
        <path d="${cesta(r.H, y)}" fill="none" stroke="#1d1d1f" stroke-width="2" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>
      </svg>` + prahy(r, y) + vrchol(r);
  }
  // přehrávač: skutečná hladina se kreslí do aktuální hodiny, předpověď o 24 h dál (tolik dopředu už model v tu chvíli řekl)
  function grafListy(el, r) {
    yL = meritko(r);
    el.innerHTML = `<svg viewBox="0 0 1000 100" preserveAspectRatio="none" aria-hidden="true">
        <defs><clipPath id="klip-h"><rect id="klip-h-r" x="0" y="-20" width="0" height="140"/></clipPath>
          <clipPath id="klip-p"><rect id="klip-p-r" x="0" y="-20" width="0" height="140"/></clipPath>
          <linearGradient id="vypln" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0.22"/>
            <stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>
        <path clip-path="url(#klip-p)" d="${cesta(r.P, yL)}" fill="none" stroke="#9fcad8" stroke-opacity="0.9" stroke-width="2" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>
        <path clip-path="url(#klip-h)" d="${cesta(r.H, yL, true)}" fill="url(#vypln)"/>
        <path class="h" clip-path="url(#klip-h)" d="${cesta(r.H, yL)}" fill="none" stroke="#fff" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round" vector-effect="non-scaling-stroke"/>
      </svg>` + prahy(r, yL) + vrchol(r, 'vrchol-lista');
  }
  function pasmo(r) {  // pruh pod osou: kdy byla skutečná hladina v kterém stupni
    let html = '', od = 0, st = stupenH(r.spa, r.H[0]);
    for (let i = 1; i <= K + 1; i++) {
      const s = i <= K ? stupenH(r.spa, r.H[i]) : -1;
      if (s === st) continue;
      if (st) html += `<i style="left:${procento(od)}%;width:${procento(i - od)}%;background:${D.spa_barvy[st]}"></i>`;
      od = i; st = s;
    }
    return html;
  }

  const stin = document.createElement('div');
  stin.className = 'stin-dole';
  const lista = document.createElement('div');
  lista.className = 'lista';
  lista.id = 'lista';
  lista.innerHTML = `<button class="hraj" id="hraj"></button>
    <div class="osa" id="osa" role="slider" tabindex="0" aria-label="Čas povodně" aria-valuemin="0" aria-valuemax="${K}">
      <div class="graf" id="graf-osa"></div><div class="pasmo"><div id="pasmo"></div></div>
      <div class="najeti" id="najeti"><span></span></div><div class="hlava" id="hlava"><i></i><span id="hlava-stitek"></span></div>
    </div>
    <button class="kulate" id="cela" type="button"></button>
    <div class="dny" id="dny"></div>`;
  document.body.append(stin, lista);
  const osa = q('osa'), hlava = q('hlava'), najeti = q('najeti'), tlacitko = q('hraj'), stitky = q('stitky');
  function zobrazMesto(r) {
    R = r;
    grafListy(q('graf-osa'), r);
    q('pasmo').innerHTML = pasmo(r);
    nakresleno = -1;
    prubeh();
  }
  priZmeneMesta = p => zobrazMesto(Object.values(A.rady).find(r => r.mesto === p) || A.rady[A.cil]);
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

  // štítek u kraje osy se zarovná dovnitř, ať nevyčnívá z přehrávače
  const kraj = (el, px) => {
    const w = el.lastChild.offsetWidth / 2 + 6;
    el.classList.toggle('kraj-l', px < w);
    el.classList.toggle('kraj-p', osa.clientWidth - px < w);
  };
  function obnovListu(i) {
    kraj(hlava, procento(i) / 100 * osa.clientWidth);
    osa.setAttribute('aria-valuenow', i);
    osa.setAttribute('aria-valuetext', A.popisky[i]);
  }
  // každý snímek: křivka dorůstá k hlavě, tečka jede po ní plynule i uvnitř hodiny
  function prubeh() {
    q('klip-h-r').setAttribute('width', (cas / K * 1000).toFixed(1));
    q('klip-p-r').setAttribute('width', (Math.min(K, cas + 24) / K * 1000).toFixed(1));
    q('pasmo').style.clipPath = `inset(0 ${(100 - procento(cas)).toFixed(2)}% 0 0)`;
    q('vrchol-lista').classList.toggle('videt', cas >= R.vrchol);
    const a = Math.floor(cas), b = Math.min(K, a + 1), ha = R.H[a], hb = R.H[b];
    const h = ha == null ? hb : hb == null ? ha : ha + (hb - ha) * (cas - a);
    hlava.firstChild.style.top = `calc(5px + (100% - 14px) * ${(h == null ? 50 : yL(h)) / 100})`;
    hlava.style.left = procento(cas) + '%';
  }
  function ikona() {
    tlacitko.innerHTML = hraje ? IKONA.stuj : cas >= K ? IKONA.znovu : IKONA.hraj;
    tlacitko.setAttribute('aria-label', hraje ? 'Zastavit' : 'Přehrát povodeň');
    lista.classList.toggle('hraje', hraje);
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
  function nastavRychlost(h) { if (+h > 0) rychlost = +h; }  // bez ovládání na stránce; pro video a deck
  function skoc(i) { cas = Math.max(0, Math.min(K, Math.round(+i))); minule = null; ikona(); }
  const krok = d => { pauza(); skoc(hodina() + d); };

  // celá obrazovka: celý dokument (Safari přes webkit); v rámu, kde je zakázaná, se stejná stránka otevře v nové kartě
  const cela = q('cela');
  const vRamu = (() => { try { return window.self !== window.top; } catch (e) { return true; } })();
  const fsLze = Boolean(document.fullscreenEnabled || document.webkitFullscreenEnabled);
  const fsPrvek = () => document.fullscreenElement || document.webkitFullscreenElement;
  const novaKarta = () => { if (vRamu && location.protocol !== 'about:') open(location.href, '_blank', 'noopener'); };
  function celaObrazovka() {
    if (fsPrvek()) return (document.exitFullscreen || document.webkitExitFullscreen).call(document);
    const el = document.documentElement;
    if (fsLze && el.requestFullscreen) return el.requestFullscreen({navigationUI: 'hide'}).catch(novaKarta);
    if (fsLze && el.webkitRequestFullscreen) return el.webkitRequestFullscreen();
    novaKarta();
  }
  function popisekCele() {
    const v = Boolean(fsPrvek());
    cela.innerHTML = svg(v ? IKONY.zmensit : IKONY.cela);
    cela.setAttribute('aria-label', v ? 'Zavřít celou obrazovku' : 'Celá obrazovka');
    cela.title = cela.getAttribute('aria-label');
  }
  popisekCele();
  if (!fsLze && (!vRamu || location.protocol === 'about:')) cela.hidden = true;
  cela.addEventListener('click', celaObrazovka);
  for (const udalost of ['fullscreenchange', 'webkitfullscreenchange']) document.addEventListener(udalost, () => {
    popisekCele();
    for (const m of [mapaA, mapaB].filter(Boolean)) m.resize();
    rozmer();
  });

  tlacitko.addEventListener('click', () => hraje ? pauza() : prehraj());
  const zBodu = e => { const o = osa.getBoundingClientRect(); return Math.round(Math.min(1, Math.max(0, (e.clientX - o.left) / o.width)) * K); };
  osa.addEventListener('pointerdown', e => { tahne = true; osa.setPointerCapture(e.pointerId); cas = zBodu(e); });
  // při najetí ukáže čas a hladinu pod kurzorem místo štítku hlavy, ať se nepřekrývají
  const schovejNajeti = () => { najeti.style.display = 'none'; osa.classList.remove('najizdi'); };
  osa.addEventListener('pointermove', e => {
    const i = zBodu(e), h = R.H[i];
    if (tahne) cas = i;
    osa.classList.add('najizdi');
    najeti.style.display = 'block';
    najeti.style.left = procento(i) + '%';
    najeti.firstChild.textContent = `${kratce(i)} · ${h == null ? '–' : cislo(h) + ' cm'}`;
    kraj(najeti, procento(i) / 100 * osa.clientWidth);
  });
  const pust = e => { tahne = false; minule = null; if (e.pointerType !== 'mouse') schovejNajeti(); };
  osa.addEventListener('pointerup', pust);
  osa.addEventListener('pointercancel', pust);
  osa.addEventListener('pointerleave', schovejNajeti);
  document.addEventListener('keydown', e => {
    if (['INPUT', 'SELECT', 'TEXTAREA'].includes(e.target.tagName)) return;
    if (e.code === 'Space') { e.preventDefault(); if (!e.repeat) hraje ? pauza() : prehraj(); }
    else if (e.code === 'ArrowRight' || e.code === 'ArrowLeft') {
      e.preventDefault();
      krok((e.code === 'ArrowRight' ? 1 : -1) * (e.shiftKey ? 24 : 1));
    } else if (e.code === 'Home' || e.code === 'End') { e.preventDefault(); pauza(); skoc(e.code === 'Home' ? 0 : K); }
    else if (e.key === 'f' && !e.metaKey && !e.ctrlKey && !cela.hidden) celaObrazovka();
  });
  // mezerník na tlačítku by ho po puštění ještě jednou stiskl
  document.addEventListener('keyup', e => { if (e.code === 'Space' && e.target.tagName === 'BUTTON') e.preventDefault(); });

  // úvod: nadpis, jedna řádka s rozsahem a vrcholem, graf a jedno tlačítko
  const H0 = A.rady[A.cil];
  uvod = document.createElement('div');
  uvod.className = 'uvod';
  uvod.innerHTML = `<div class="uvod-karta" role="dialog" aria-labelledby="uvod-nazev">
    <h1 id="uvod-nazev">${A.nazev} <span>· ${H0.mesto}</span></h1>
    <p class="uvod-rozsah">${A.rozsah}, ${cislo(K + 1)} hodin. Vrchol <b>${kratce(H0.vrchol)}, ${cislo(H0.H[H0.vrchol])} cm</b>
      ${odznak(stupenH(H0.spa, H0.H[H0.vrchol]))}</p>
    <div class="uvod-graf" id="graf-uvod"></div>
    <button class="uvod-hraj" id="uvod-hraj">${IKONA.hraj}Přehrát povodeň</button></div>`;
  document.body.append(uvod);
  grafUvodu(q('graf-uvod'), H0);
  q('uvod-hraj').addEventListener('click', prehraj);
  zobrazMesto(R);

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
    prubeh();
    if (porovnani) stitky.style.setProperty('--x', porovnani.currentPosition + 'px');
    requestAnimationFrame(snimek);
  };
  // pro nahrávání videa a ovládání z konzole (prelet je globální funkce)
  Object.assign(window, {prehraj, pauza, nastavRychlost, skoc, zavriUvod, prelet,
    skocNaVrchol: () => skoc(R.vrchol),
    porovnat: (ano = true) => nastavRezim(ano ? 'porovnani' : 'animace'),
    stavPrehravace: () => ({hodina: hodina(), konec: K, hraje, rychlost, rezim, datum: A.popisky[hodina()],
                            skutecnost: R.H[hodina()], predpoved: R.P[hodina()], start: A.start, vrchol: R.vrchol})});
  ikona();
  requestAnimationFrame(snimek);
}

panel();
dolad(pohled);
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
    st.caption("Okno je 14 dní před vrcholem hladiny v Děčíně a 5 dní po něm. Rozliv jde ze změřené hladiny, v grafu je "
               "modře předpověď modelu vydaná o 24 h dřív. Terén je zvýšený 1,6×.")
    od, do = okno(povoden)
    od, do = od.tz_convert(mapa.PASMO).tz_localize(None), do.tz_convert(mapa.PASMO).tz_localize(None)
    vrchol = nacti().loc[slice(*POVODNE[povoden]), f"{cil}_H"].idxmax().tz_convert(mapa.PASMO).tz_localize(None)
    okamzik = st.slider("Okamžik (český čas)", od.to_pydatetime(), do.to_pydatetime(), vrchol.to_pydatetime(),
                        step=timedelta(hours=1), format="D. M. YYYY HH:mm")
    cas = mapa._cas_utc(pd.Timestamp(okamzik))
    vyrobit(html(cas, predpovedi(cas), MESTA[cil]), height=700)


if __name__ == "__main__":
    main()
