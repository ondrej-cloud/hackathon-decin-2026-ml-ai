r"""3D mapa povodí v Mapbox GL JS: satelit s popisky ulic, terén, budovy, stanice a záplavová území.

Proti pydeck mapě v mapa.py (ta zůstává jako záloha) jsou dobře vidět malá území: záplavové území leží
přímo na terénu, v Děčíně a Ústí stojí budovy ve 3D a ulice mají ostré popisky. Potřebuje MAPBOX_TOKEN v .env.

Ukázka z kořene repozitáře:
    .venv\Scripts\python -m streamlit run app/mapbox_mapa.py --server.port 8505
V aplikaci (stejné argumenty jako mapa.deck):
    st.iframe(mapbox_mapa.html(cas, predpovedi, pohled), height=700)
"""
import json
import re
from datetime import date, datetime, time
from functools import cache
from html import escape

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

import mapa
from predikce import KDE, ROOT, nacti, nacti_model, stupen, vstupy
from rozliv import GENITIV, SOUBOR_UZEMI, n_leta_voda, n_lete

MAPBOX = "https://api.mapbox.com/mapbox-gl-js/v3.8.0"
STYL = "mapbox://styles/mapbox/satellite-streets-v12"
REKY = ROOT / "data/external/reky.geojson"
MESTA = {"decin": "Děčín", "usti": "Ústí nad Labem"}
# Klíče jako mapa.POHLEDY. Města jsou natočená podél údolí Labe, ať je vidět řeka i svahy nad ní.
# Města na zoomu 15,1: dlaždice Mapbox Streets mají budovy až od úrovně 15, na 14 jen pár velkých.
KAMERY = {
    "celé povodí": {"center": [14.65, 50.30], "zoom": 8, "pitch": 55, "bearing": 0},
    "Ústí nad Labem": {"center": [14.043, 50.6575], "zoom": 15.1, "pitch": 62, "bearing": 10},
    "Děčín": {"center": [14.205, 50.775], "zoom": 15.1, "pitch": 62, "bearing": -20},
}
TLACITKA = [("celé povodí", "Celé povodí"), ("Ústí nad Labem", "Ústí nad Labem"), ("Děčín", "Děčín")]


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
             "stupen": None if pd.isna(h) else int(stupen(cil, h)), "predpoved": None, "N": None,
             "veta": "Pro tuhle hodinu nemáme předpověď, záplavová území jsou jen obrysem."}
        if predpovedi and cil in predpovedi:
            hor, cm = predpovedi[cil]
            voda = n_leta_voda(cil, cm)
            zony = [N for N in (5, 20, 100) if N <= voda["N"]]
            m["N"] = zony[-1] if zony else None
            m["predpoved"] = {"h": hor, "cm": round(cm), "stupen": stupen(cil, cm)}
            m["veta"] = f"Předpověď za {hor} h: {voda['popis']} " + (
                f"Vyplněné je záplavové území {GENITIV[m['N']]} vody (Q{m['N']})." if m["N"] else
                "Záplavová území Q5, Q20 a Q100 jsou jen obrysem.")
            m["veta"] = re.sub(r"(\d) (\d{3})", "\\1\u00a0\\2", m["veta"])  # tisíce se nezalomí
        mesta.append(m)
    return mesta


def _zaplavy(mesta):
    plne = {m["klic"]: m["N"] for m in mesta}
    q = n_lete().set_index(["klic", "N"]).Q_m3s
    prvky = []
    for N, usek, souradnice in _uzemi():
        tooltip = (f"Záplavové území {GENITIV[N]} vody (Q{N} = {mapa._cislo(q[usek, N])} m³/s "
                   f"{'v Děčíně' if usek == 'decin' else 'v Ústí'})<br>DIBAVOD, VÚV TGM; průběh je orientační")
        if N == plne[usek]:
            tooltip += "<br>Odpovídá předpovědi modelu"
        prvky.append({"type": "Feature", "geometry": {"type": "MultiPolygon", "coordinates": souradnice},
                      "properties": {"N": N, "plne": N == plne[usek], "tooltip": tooltip}})
    prvky.sort(key=lambda f: f["properties"]["plne"])  # vyplněné území navrch
    return {"type": "FeatureCollection", "features": prvky}


def _popisek_casu(cas):
    t = cas.tz_convert(mapa.PASMO)
    return f"{t.day}. {t.month}. {t.year} {t:%H:%M} {'SELČ' if t.dst() else 'SEČ'}"


def html(cas, predpovedi=None, pohled="celé povodí") -> str:
    """Stránka s mapou pro st.iframe(..., height=700); argumenty jako mapa.deck (čas bez pásma = český čas)."""
    token = mapa.mapbox_token()
    if not token:
        return BEZ_TOKENU
    cas = mapa._cas_utc(cas)
    mesta = _mesta(cas, predpovedi)
    data = {
        "token": token, "styl": STYL, "kamery": KAMERY, "pohled": pohled, "tlacitka": TLACITKA,
        "datum": _popisek_casu(cas), "mesta": mesta, "barvy": mapa.BARVY, "seda": mapa.SEDA,
        "stanice": _stanice(cas, predpovedi), "uzemi": _zaplavy(mesta),
        "reky": json.loads(REKY.read_text(encoding="utf-8")),
    }
    data = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return STRANKA.replace("__MAPBOX__", MAPBOX).replace("__DATA__", data)


BEZ_TOKENU = """<!doctype html><html lang="cs"><meta charset="utf-8">
<body style="margin:0;padding:24px;background:#0c1720;color:#eef3f6;font:15px sans-serif">
Mapa v Mapbox GL potřebuje MAPBOX_TOKEN v souboru .env. Bez něj použijte mapu z mapa.py.</body></html>"""

STRANKA = r"""<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&display=swap" rel="stylesheet">
<link href="__MAPBOX__/mapbox-gl.css" rel="stylesheet">
<script src="__MAPBOX__/mapbox-gl.js"></script>
<style>
:root {
  --pozadi: #0c1720;
  --panel: rgba(12, 23, 32, 0.86);
  --text: #eef3f6;
  --tlumene: #9db0bd;
  --cara: rgba(255, 255, 255, 0.14);
  --voda: #6cc8f5;
  --plne: #1e78dc;
}
* { box-sizing: border-box; }
html, body { margin: 0; height: 100%; background: var(--pozadi); color: var(--text); overflow: hidden;
  font: 15px/1.35 "Source Sans 3", sans-serif; font-variant-numeric: tabular-nums; }
#mapa { position: absolute; inset: 0; }
.box { position: absolute; background: var(--panel); border: 1px solid var(--cara); border-radius: 10px;
  backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px); }
.pohledy { top: 12px; left: 12px; display: flex; gap: 4px; padding: 4px; }
.pohledy button { font: inherit; font-weight: 600; color: var(--text); background: transparent; border: 0;
  border-radius: 7px; padding: 7px 12px; cursor: pointer; transition: background-color 0.15s ease-out; }
.pohledy button:hover { background: rgba(255, 255, 255, 0.08); }
.pohledy button:active { transform: scale(0.97); }
.pohledy button[aria-pressed="true"] { background: var(--voda); color: #08202e; }
.panel { top: 12px; right: 12px; width: 320px; padding: 12px 14px; }
.datum { font-size: 22px; font-weight: 700; letter-spacing: -0.01em; }
.mesto { margin-top: 9px; padding-top: 8px; border-top: 1px solid var(--cara); }
.radek { display: flex; align-items: baseline; gap: 8px; }
.jmeno { font-weight: 600; flex: 1; }
.cm { font-size: 20px; font-weight: 700; }
.odznak { font-size: 12px; font-weight: 600; padding: 1px 7px; border-radius: 5px; white-space: nowrap; }
.pred { margin-top: 3px; font-size: 13.5px; color: var(--tlumene); display: flex; align-items: baseline; gap: 6px; }
.pred b { color: var(--voda); font-size: 15px; }
.veta { margin-top: 10px; padding-top: 8px; border-top: 1px solid var(--cara); font-size: 13.5px; color: var(--tlumene); }
.veta b { color: var(--text); }
.legenda { left: 12px; bottom: 38px; max-width: calc(100% - 24px); padding: 7px 11px; font-size: 12.5px; color: var(--tlumene); }
.legenda i { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin: 0 4px 0 6px; vertical-align: -1px; }
.legenda i.plocha { border-radius: 2px; }
.mapboxgl-popup-content { background: #172b3a; color: #fff; font: 14px/1.4 "Source Sans 3", sans-serif;
  border-radius: 8px; padding: 10px 28px 10px 12px; }
.mapboxgl-popup-close-button { color: #fff; font-size: 18px; padding: 0 7px; }
.mapboxgl-popup-anchor-top .mapboxgl-popup-tip, .mapboxgl-popup-anchor-top-left .mapboxgl-popup-tip,
.mapboxgl-popup-anchor-top-right .mapboxgl-popup-tip { border-bottom-color: #172b3a; }
.mapboxgl-popup-anchor-bottom .mapboxgl-popup-tip, .mapboxgl-popup-anchor-bottom-left .mapboxgl-popup-tip,
.mapboxgl-popup-anchor-bottom-right .mapboxgl-popup-tip { border-top-color: #172b3a; }
.mapboxgl-popup-anchor-left .mapboxgl-popup-tip { border-right-color: #172b3a; }
.mapboxgl-popup-anchor-right .mapboxgl-popup-tip { border-left-color: #172b3a; }
@media (max-width: 720px) {
  .panel { top: auto; bottom: 12px; left: 12px; right: 12px; width: auto; }
  .legenda, .veta, .mapboxgl-ctrl-group { display: none; }
}
</style>
</head>
<body>
<div id="mapa"></div>
<div class="box pohledy" id="pohledy" role="group" aria-label="Pohled"></div>
<div class="box panel" id="panel"></div>
<div class="box legenda" id="legenda"></div>
<script>
const D = __DATA__;
const STUPNE = ['bez stupně', '1. stupeň', '2. stupeň', '3. stupeň'];
const css = c => `rgb(${c[0]},${c[1]},${c[2]})`;
const cislo = v => v == null ? '–' : Math.round(v).toLocaleString('cs-CZ');

function kamera(pohled) {
  // střed záběru mimo panel (vpravo, na úzké obrazovce dole); celé povodí se musí vejít i do užšího okna
  const siroko = innerWidth > 720;
  const k = {...D.kamery[pohled], padding: {top: 0, left: 0, right: siroko ? 340 : 0, bottom: siroko ? 0 : 200}};
  if (pohled === 'celé povodí') k.zoom += Math.max(-1.3, Math.log2(Math.min(1, innerWidth / 1270)));
  return k;
}

mapboxgl.accessToken = D.token;
const map = new mapboxgl.Map({
  container: 'mapa', style: D.styl, ...kamera(D.pohled), minZoom: 6, maxPitch: 75,
  customAttribution: 'Měření a N-leté průtoky © ČHMÚ · Záplavová území DIBAVOD (VÚV TGM)'
});
map.setPadding(kamera(D.pohled).padding);  // konstruktor odsazení nebere
map.addControl(new mapboxgl.NavigationControl({visualizePitch: true}), 'bottom-right');

map.on('style.load', () => {
  map.addSource('vysky', {type: 'raster-dem', url: 'mapbox://mapbox.mapbox-terrain-dem-v1', tileSize: 512, maxzoom: 14});
  map.setTerrain({source: 'vysky', exaggeration: 1.8});
  map.setFog({range: [1, 10], color: '#dce6ee', 'high-color': '#4a78a8', 'horizon-blend': 0.06,
              'space-color': '#0c1720', 'star-intensity': 0});

  // plochy, řeky a budovy pod popisky podkladu, ať názvy ulic zůstanou čitelné
  const popisky = map.getStyle().layers.find(l => l.type === 'symbol')?.id;
  map.addSource('uzemi', {type: 'geojson', data: D.uzemi});
  map.addLayer({id: 'uzemi', type: 'fill', source: 'uzemi', paint: {
    'fill-color': ['case', ['get', 'plne'], '#1e78dc', '#7cc4ff'],
    'fill-opacity': ['case', ['get', 'plne'], 0.55, 0.12]
  }}, popisky);
  map.addLayer({id: 'uzemi-obrys', type: 'line', source: 'uzemi', paint: {
    'line-color': ['case', ['get', 'plne'], '#cfe9ff', '#8fd0ff'],
    'line-width': ['interpolate', ['linear'], ['zoom'], 10, 0.5, 15, 1.6], 'line-opacity': 0.75
  }}, popisky);
  map.addSource('reky', {type: 'geojson', data: D.reky});
  map.addLayer({id: 'reky', type: 'line', source: 'reky', layout: {'line-join': 'round', 'line-cap': 'round'}, paint: {
    'line-color': '#8fd3ff',
    'line-width': ['interpolate', ['exponential', 1.5], ['zoom'], 7, 1.5, 10, 3, 14, 6],
    // řeky jsou zjednodušené, ve městě je přesnější satelit
    'line-opacity': ['interpolate', ['linear'], ['zoom'], 10, 0.9, 13, 0.3]
  }}, popisky);
  // zdroj composite (Mapbox Streets) je součástí stylu satellite-streets
  map.addLayer({id: 'budovy', type: 'fill-extrusion', source: 'composite', 'source-layer': 'building', minzoom: 14,
    filter: ['==', ['get', 'extrude'], 'true'], paint: {
      'fill-extrusion-color': '#d9dcdf',
      'fill-extrusion-height': ['interpolate', ['linear'], ['zoom'], 14, 0, 14.5, ['get', 'height']],
      'fill-extrusion-base': ['interpolate', ['linear'], ['zoom'], 14, 0, 14.5, ['get', 'min_height']],
      'fill-extrusion-opacity': 0.9
    }}, popisky);

  // čísla silnic jen zahlcují satelit
  for (const l of map.getStyle().layers) if (l.id.includes('shield')) map.setLayoutProperty(l.id, 'visibility', 'none');

  map.addSource('stanice', {type: 'geojson', data: D.stanice});
  const s = ['sqrt', ['get', 'prutok']];
  // ve městě menší kolečka, ať nezakryjí záplavové území
  map.addLayer({id: 'stanice', type: 'circle', source: 'stanice', paint: {
    'circle-radius': ['interpolate', ['linear'], ['zoom'],
      7, ['+', 3, ['*', 0.25, s]], 11, ['+', 5, ['*', 0.5, s]], 15, ['+', 4, ['*', 0.3, s]]],
    'circle-pitch-scale': 'viewport',
    'circle-color': ['get', 'barva'], 'circle-opacity': 0.92,
    'circle-stroke-color': '#ffffff', 'circle-stroke-width': 1.5
  }});
  map.addLayer({id: 'stanice-popisky', type: 'symbol', source: 'stanice', layout: {
    'text-field': ['get', 'popisek'], 'text-font': ['DIN Pro Bold', 'Arial Unicode MS Bold'],
    'text-size': ['interpolate', ['linear'], ['zoom'], 7, 11, 12, 14],
    'text-variable-anchor': ['top', 'bottom', 'right', 'left'],
    // odsazení v em: poloměr kolečka / velikost písma + mezera
    'text-radial-offset': ['interpolate', ['linear'], ['zoom'],
      7, ['+', 0.62, ['*', 0.023, s]], 11, ['+', 0.72, ['*', 0.037, s]], 15, ['+', 0.64, ['*', 0.021, s]]],
    'text-justify': 'auto', 'symbol-sort-key': ['-', 0, ['get', 'prutok']]
  }, paint: {'text-color': '#ffffff', 'text-halo-color': 'rgba(10, 20, 30, 0.95)', 'text-halo-width': 1.6}});
});

const KLIKACI = ['stanice', 'uzemi'];
// území se překrývají: přednost má stanice, pak vyplněné území, pak menší N
const poradi = f => f.layer.id === 'stanice' ? 0 : f.properties.plne ? 1 : 1 + f.properties.N;
map.on('click', e => {
  const f = map.queryRenderedFeatures(e.point, {layers: KLIKACI}).sort((a, b) => poradi(a) - poradi(b))[0];
  if (!f) return;
  new mapboxgl.Popup({maxWidth: '330px'})
    .setLngLat(f.layer.id === 'stanice' ? f.geometry.coordinates : e.lngLat)
    .setHTML(f.properties.tooltip).addTo(map);
});
for (const id of KLIKACI) {
  map.on('mouseenter', id, () => { map.getCanvas().style.cursor = 'pointer'; });
  map.on('mouseleave', id, () => { map.getCanvas().style.cursor = ''; });
}

function odznak(st) {
  const c = st == null ? D.seda : D.barvy[st];
  return `<span class="odznak" style="background:${css(c)};color:${st === 1 ? '#1a1a1a' : '#fff'}">${st == null ? 'chybí' : STUPNE[st]}</span>`;
}
function panel(pohled) {
  // věta o N-leté vodě pro město v záběru, u celého povodí pro Děčín
  const vybrane = D.mesta.find(m => m.nazev === pohled) ?? D.mesta[0];
  document.getElementById('panel').innerHTML = `<div class="datum">${D.datum}</div>` + D.mesta.map(m => `
    <div class="mesto">
      <div class="radek"><span class="jmeno">${m.nazev}</span><span class="cm">${cislo(m.hladina)} cm</span>${odznak(m.stupen)}</div>
      <div class="pred">${m.predpoved ? `model za ${m.predpoved.h} h <b>${cislo(m.predpoved.cm)} cm</b>${odznak(m.predpoved.stupen)}` : 'bez předpovědi'}</div>
    </div>`).join('') + `<div class="veta"><b>${vybrane.nazev}:</b> ${vybrane.veta}</div>`;
}
const tlacitka = D.tlacitka.map(([pohled, popis]) => {
  const b = document.createElement('button');
  b.textContent = popis;
  b.addEventListener('click', () => {
    map.flyTo({...kamera(pohled), duration: 3500, essential: true});
    map.once('moveend', () => dolad(pohled));
    oznac(pohled);
  });
  document.getElementById('pohledy').append(b);
  return [pohled, b];
});
function oznac(pohled) {
  for (const [p, b] of tlacitka) b.setAttribute('aria-pressed', p === pohled);
  panel(pohled);
}
// Mapbox drží výšku kamery, a když se pod středem donačte přesnější terén, zoom ujede (ve městě i pod 15,
// kde dlaždice ještě nemají budovy). Po donačtení proto kameru jednou srovnáme, pokud s ní mezitím nikdo nehnul.
function dolad(pohled) {
  map.once('idle', () => {
    const k = kamera(pohled), c = map.getCenter();
    const stejne = Math.abs(c.lng - k.center[0]) < 1e-4 && Math.abs(c.lat - k.center[1]) < 1e-4;
    if (stejne && Math.abs(map.getZoom() - k.zoom) > 0.05) map.easeTo({...k, duration: 600});
  });
}
oznac(D.pohled);
dolad(D.pohled);

const B = D.barvy, kruh = c => `<i style="background:${css(c)}"></i>`;
document.getElementById('legenda').innerHTML =
  `<div>Stanice: velikost kolečka je průtok, barva stupeň povodňové aktivity.</div>` +
  `<div>Děčín, Ústí: ${kruh(B[0])}bez stupně ${kruh(B[1])}1. ${kruh(B[2])}2. ${kruh(B[3])}3. stupeň</div>` +
  `<div>Ostatní: ${kruh(B[0])}běžně ${kruh(B[1])}nad 95. ${kruh(B[3])}nad 99. percentilem průtoku</div>` +
  `<div>Záplavová území Q5 / Q20 / Q100: <i class="plocha" style="background:var(--plne)"></i>odpovídá předpovědi` +
  `<i class="plocha" style="background:rgba(124,196,255,0.35);outline:1px solid #8fd0ff"></i>ostatní</div>`;
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


def main():
    st.set_page_config(page_title="Labe · 3D mapa Mapbox", layout="wide")
    a, b, c = st.columns([1, 2, 2])
    den = a.date_input("Den (UTC)", date(2011, 1, 15), min_value=date(2006, 1, 2), max_value=date(2025, 12, 30))
    hodina = b.slider("Hodina (UTC)", 0, 23, 8)
    pohled = c.radio("Výchozí pohled", list(mapa.POHLEDY), horizontal=True)
    cas = pd.Timestamp(datetime.combine(den, time(hodina)), tz="UTC")
    getattr(st, "iframe", components.html)(html(cas, predpovedi(cas), pohled), height=700)
    st.caption("Plná modrá: oficiální záplavové území (DIBAVOD) pro N-letou vodu, kterou dosáhne předpověď modelu "
               "na 24 h; ostatní z Q5, Q20 a Q100 jen slabě. Území platí pro ustálený N-letý průtok, ne pro konkrétní "
               "povodeň. Terén je zvýšený 1,8×. Tažením posunete, pravým tlačítkem nebo Ctrl a tažením natočíte.")


if __name__ == "__main__":
    main()
