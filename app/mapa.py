"""Povodeň v lednu 2011 na 3D mapě Labe a přítoků."""

import os
import sys
from datetime import datetime, timedelta
from functools import cache
from pathlib import Path

import pandas as pd
import pydeck as pdk
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from data import SPA, nacti


PASMO = "Europe/Prague"
PREHANI = 2.5
MERITKO_PRUTOKU = 5
BARVY = ([40, 165, 92], [250, 204, 21], [249, 115, 22], [220, 38, 38])
SEDA = [130, 140, 150]
# Zaokrouhlené výšky z Terrarium; backend při posunu času nepotřebuje síť.
VYSKY = {
    "decin": 126, "usti": 145, "louny": 179, "melnik": 161,
    "vranany": 163, "kostelec": 165, "praha": 191, "nymburk": 182,
    "jizera": 180, "beroun": 219, "sazava": 279, "prelouc": 208,
}


def mapbox_token():
    """Veřejný token Mapboxu z proměnné MAPBOX_TOKEN nebo z .env v kořeni repa; bez něj OpenStreetMap."""
    token = os.environ.get("MAPBOX_TOKEN")
    env = ROOT / ".env"
    if not token and env.exists():
        for radek in env.read_text(encoding="utf-8").splitlines():
            if radek.startswith("MAPBOX_TOKEN="):
                token = radek.split("=", 1)[1].strip().strip('"')
    return token or None


@cache
def _podklady():
    stanice = pd.read_csv(ROOT / "data/external/stanice_hydro.csv")
    percentily = nacti().loc["2006":"2018"].filter(regex="_Q$").quantile([0.95, 0.99])
    return stanice, percentily


def _cas_utc(cas):
    cas = pd.Timestamp(cas)
    if cas.tzinfo is None:
        cas = cas.tz_localize(PASMO)
    return cas.tz_convert("UTC")


def _cislo(hodnota):
    return "chybí měření" if pd.isna(hodnota) else f"{hodnota:,.0f}".replace(",", " ")


def _stanice(cas, predpovedi=None):
    """predpovedi: {klic: (horizont, hladina_cm)} z modelu, přidá se k popisku Děčína a Ústí."""
    metadata, percentily = _podklady()
    radek = nacti().loc[_cas_utc(cas)]
    body = []
    for stanice in metadata.itertuples(index=False):
        klic = stanice.klic
        q = radek[f"{klic}_Q"]
        barva = SEDA
        tooltip = f"{stanice.stanice} · {stanice.tok}\nPrůtok: {_cislo(q)}"
        predpoved = ""
        if pd.notna(q):
            tooltip += " m³/s"
        if klic in SPA:
            h = radek[f"{klic}_H"]
            stupen = sum(h >= mez for mez in SPA[klic]) if pd.notna(h) else None
            stav = "stupeň nelze určit" if stupen is None else (
                "bez stupně povodňové aktivity" if stupen == 0 else f"{stupen}. stupeň povodňové aktivity"
            )
            barva = SEDA if stupen is None else BARVY[stupen]
            tooltip += f"\nHladina: {_cislo(h)}" + (" cm" if pd.notna(h) else "")
            tooltip += f"\n{stav}"
            if predpovedi and klic in predpovedi:
                hor, cm = predpovedi[klic]
                s = sum(cm >= mez for mez in SPA[klic])
                predpoved = f"\nza {hor} h: {cm:.0f} cm" + (f", {s}. stupeň" if s else "")
                tooltip += f"\nPředpověď modelu{predpoved}"
        else:
            p95, p99 = percentily[f"{klic}_Q"]
            if pd.notna(q):
                kategorie = 3 if q >= p99 else (1 if q >= p95 else 0)
                barva = BARVY[kategorie]
                stav = {0: "pod 95. percentilem", 1: "od 95. do 99. percentilu", 3: "od 99. percentilu"}[kategorie]
                tooltip += f"\nPrůtok {stav} (2006–2018)"
            tooltip += f"\n95. / 99. percentil: {_cislo(p95)} / {_cislo(p99)} m³/s"
            tooltip += "\nHladinu nemáme; barva není oficiální povodňový stupeň."
        # Odhad výšky paty s malou rezervou kvůli hrubší síti terénu.
        z = VYSKY[klic] * PREHANI + 40
        vyska = float(q) if pd.notna(q) else 0.0
        body.append({
            "klic": klic,
            "pozice": [stanice.lon, stanice.lat, z],
            "vrchol": [stanice.lon, stanice.lat, z + vyska * MERITKO_PRUTOKU],
            "prutok": vyska,
            "barva": barva,
            "popisek": f"{stanice.stanice}\n{_cislo(q)}" + (" m³/s" if pd.notna(q) else "") + predpoved,
            "tooltip": tooltip,
        })
    return body


def deck(cas: pd.Timestamp, predpovedi=None) -> pdk.Deck:
    """Mapa měření v dané hodině; čas bez pásma se bere jako český čas. predpovedi viz _stanice."""
    body = _stanice(cas, predpovedi)
    token = mapbox_token()
    if token:
        vysky = f"https://api.mapbox.com/v4/mapbox.terrain-rgb/{{z}}/{{x}}/{{y}}.pngraw?access_token={token}"
        povrch = f"https://api.mapbox.com/v4/mapbox.satellite/{{z}}/{{x}}/{{y}}@2x.png?access_token={token}"
        dekoder = {"rScaler": 6553.6, "gScaler": 25.6, "bScaler": 0.1, "offset": -10000}
    else:
        vysky = "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"
        povrch = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        dekoder = {"rScaler": 256, "gScaler": 1, "bScaler": 1 / 256, "offset": -32768}
    teren = pdk.Layer(
        "TerrainLayer",
        id="teren",
        elevation_data=vysky,
        texture=povrch,
        # TerrainLayer nemá elevationScale, násobíme celý dekodér včetně offsetu.
        elevation_decoder={k: v * PREHANI for k, v in dekoder.items()},
        tile_size=256,
        min_zoom=0,
        max_zoom=14,
        extent=[13.4, 49.6, 15.9, 51.05],
        mesh_max_error=8,
        material={"ambient": 0.6, "diffuse": 0.6, "shininess": 12},
        pickable=False,
    )
    sloupce = pdk.Layer(
        "ColumnLayer",
        id="stanice",
        data=body,
        get_position="pozice",
        get_elevation="prutok",
        get_fill_color="barva",
        elevation_scale=MERITKO_PRUTOKU,
        radius=800,
        disk_resolution=20,
        extruded=True,
        pickable=True,
        auto_highlight=True,
    )
    popisky = pdk.Layer(
        "TextLayer",
        id="popisky",
        data=body,
        get_position="vrchol",
        get_text="popisek",
        get_size=14,
        font_weight=600,
        # na satelitním snímku bílý text s tmavým obrysem, na mapě naopak
        get_color=[255, 255, 255] if token else [25, 35, 45],
        get_pixel_offset=[0, -12],
        get_text_anchor="'middle'",
        get_alignment_baseline="'bottom'",
        outline_width=2 if token else 1.5,
        outline_color=[15, 25, 35, 240] if token else [255, 255, 255, 230],
        font_settings={"sdf": True},
        character_set="'auto'",
        pickable=True,
    )
    from rozliv import vrstvy  # oficiální záplavová území podle předpovědi (DIBAVOD), viz rozliv.py
    rozliv = [v for k, (h, cm) in (predpovedi or {}).items() for v in vrstvy(k, cm)]
    return pdk.Deck(
        layers=[teren, *rozliv, sloupce, popisky],
        initial_view_state=pdk.ViewState(
            latitude=50.30, longitude=14.65, zoom=8.15, pitch=55, bearing=0,
            min_zoom=6, max_zoom=14,
        ),
        map_style=None,
        map_provider=None,
        height=650,
        tooltip={
            "text": "{tooltip}",
            "style": {"backgroundColor": "#172b3a", "color": "white", "fontSize": "14px"},
        },
    )


def main():
    st.set_page_config(page_title="Povodeň na Labi · 3D mapa", layout="wide")
    st.title("Co teče proti proudu, dorazí k nám")
    st.caption("Naměřené průtoky 12 stanic při povodni v lednu 2011; čas je v českém pásmu (SEČ).")
    cas = st.slider(
        "Čas měření (SEČ)",
        min_value=datetime(2011, 1, 8),
        max_value=datetime(2011, 1, 24, 18),
        value=datetime(2011, 1, 15, 6),
        step=timedelta(hours=6),
        format="DD. MM. YYYY HH:mm",
    )
    st.pydeck_chart(deck(pd.Timestamp(cas)), height=650, key="mapa-povodi")
    radek = nacti().loc[_cas_utc(cas)]
    st.write(
        f"Dne {cas:%d. %m. %Y} v {cas:%H:%M} SEČ teče Prahou {_cislo(radek['praha_Q'])} m³/s, "
        f"Mělníkem {_cislo(radek['melnik_Q'])} m³/s a Děčínem {_cislo(radek['decin_Q'])} m³/s; "
        "posunem času sledujete vývoj povodně od přítoků k dolnímu Labi."
    )
    st.caption(
        "Děčín a Ústí: zelená = bez stupně, žlutá = 1., oranžová = 2., červená = 3. stupeň podle hladiny. "
        "Ostatní stanice: zelená = pod 95., žlutá = od 95. do 99., červená = od 99. percentilu průtoku "
        "z let 2006–2018; nejde o oficiální povodňové stupně. Šedá = chybí měření."
    )
    st.caption(
        "Terén je zvýšený 2,5×, výška sloupců odpovídá průtoku (1 m³/s = 5 m na mapě); "
        "nejde o výšku vody ani rozsah záplavy. Kolečkem přiblížíte, tažením posunete, "
        "Shift + tažením natočíte mapu."
    )
    st.caption(
        "Mapový podklad: [© OpenStreetMap contributors](https://www.openstreetmap.org/copyright) · "
        "Výšky: [Mapzen / AWS Terrain Tiles](https://github.com/tilezen/joerd/blob/master/docs/attribution.md) · "
        "Měření: ČHMÚ · Dlaždice vyžadují připojení k internetu."
    )


if __name__ == "__main__":
    main()
