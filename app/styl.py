"""Vzhled aplikace: tmavý povodňový pult. Písma, barvy a styly prvků Streamlitu (cílené přes data-testid).

Barvy panelů a okrajů jsou stejné jako u mapy a animace, aby vložené komponenty a zbytek aplikace působily jako
jedna věc. Barvy stupňů povodňové aktivity jsou z predikce.BARVY.
"""
from urllib.parse import quote

import streamlit as st

POZADI = "#111820"
PANEL = "rgba(15, 20, 25, 0.92)"
CARA = "rgba(255, 255, 255, 0.08)"
TEXT = "#e8edf1"
TLUMENE = "#93a1ad"
VODA = "#3aa0c9"
VODA_SVETLA = "#7cc6e4"
SEDA = "#7d8995"
PISMO = "Schibsted Grotesk"
DISPLAY = "Sofia Sans Extra Condensed"
# popisky čar stupňů v grafu: světlejší odstíny BARVY[1:], aby se daly přečíst na tmavém pozadí
POPISKY_SPA = ["#f2c437", "#ff9a45", "#ff7a72"]

_IKONY = {
    "vodocet": ('<path d="M8 3v18"/><path d="M8 5.5h4M8 9.5h6M8 13.5h4M8 17.5h6"/>'
                '<path d="M2.5 15.5c1.4 0 1.4-1 2.8-1s1.4 1 2.8 1 1.4-1 2.8-1 1.4 1 2.8 1 1.4-1 2.8-1 1.4 1 2.8 1 '
                '1.4-1 2.8-1"/>'),
    "kvalita": '<path d="M3.5 19.5h17"/><path d="M5 15.5l4.5-5 3.5 3 6-7"/><path d="M15 6.5h4v4"/>',
    "mapa": '<path d="M3 6.5l6-2.5 6 2.5 6-2.5v13.5l-6 2.5-6-2.5-6 2.5z"/><path d="M9 4v13.5M15 6.5V20"/>',
    "animace": '<circle cx="12" cy="12" r="9"/><path d="M10 8.6l5 3.4-5 3.4z"/>',
}


def _svg(nazev, velikost=24, barva="currentColor"):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="{velikost}" height="{velikost}" '
            f'fill="none" stroke="{barva}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" '
            f'aria-hidden="true">{_IKONY[nazev]}</svg>')


def _url(nazev, barva="#000"):
    return f'url("data:image/svg+xml,{quote(_svg(nazev, barva=barva))}")'


def hlavicka(okamzik, model, zdroj, zive):
    """Úzký pruh nahoře: název, pro koho to je a stav (okamžik, model, zdroj dat)."""
    tecka = '<i class="tecka zive"></i>' if zive else '<i class="tecka"></i>'
    return ('<header class="pruh">'
            f'<div class="pruh-znak">{_svg("vodocet", 28)}</div>'
            '<div class="pruh-nazev"><h1>Kolik vody přiteče do Děčína a Ústí</h1>'
            '<p>Předpověď hladiny Labe na 12, 24 a 36 hodin pro povodňovou komisi města a lidi u řeky.</p></div>'
            '<dl class="pruh-stav">'
            f'<div><dt>Okamžik</dt><dd>{okamzik}</dd></div>'
            f'<div><dt>Model</dt><dd>{model}</dd></div>'
            f'<div><dt>Data</dt><dd>{tecka}{zdroj}</dd></div>'
            '</dl></header>')


CSS = """
@import url('https://fonts.googleapis.com/css2?family=Schibsted+Grotesk:wght@400..800&family=Sofia+Sans+Extra+Condensed:wght@500..800&display=swap');
:root {
  --pozadi: %(POZADI)s; --panel: %(PANEL)s; --cara: %(CARA)s; --cara-silna: rgba(255, 255, 255, 0.16);
  --text: %(TEXT)s; --tlumene: %(TLUMENE)s; --voda: %(VODA)s; --voda-svetla: %(VODA_SVETLA)s;
  --aktivni: rgba(255, 255, 255, 0.08); --najeti: rgba(255, 255, 255, 0.045);
  --pismo: '%(PISMO)s', sans-serif; --display: '%(DISPLAY)s', '%(PISMO)s', sans-serif;
  --r: 12px; --ven: cubic-bezier(0.16, 1, 0.3, 1);
}
html, body, .stApp { background: var(--pozadi); }
::selection { background: rgba(58, 160, 201, 0.4); color: #fff; }
* { scrollbar-width: thin; scrollbar-color: rgba(255, 255, 255, 0.18) transparent; }
:focus-visible { outline: 2px solid var(--voda); outline-offset: 2px; }
div[data-testid="stElementContainer"]:has(style#styl-pultu) { display: none; }

/* chrome Streamlitu */
header[data-testid="stHeader"] { background: transparent; }
[data-testid="stAppDeployButton"], [data-testid="stDecoration"] { display: none; }
[data-testid="stMainBlockContainer"] { max-width: 1320px; padding-bottom: 4rem; }

/* pruh nahoře */
[data-testid="stMarkdownContainer"] .pruh {
  display: flex; align-items: center; gap: 1rem 1.25rem; padding: 0.85rem 1.1rem; margin-bottom: 1.1rem;
  background: var(--panel); border: 1px solid var(--cara); border-radius: var(--r);
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
}
.pruh .pruh-znak { flex: none; display: grid; place-items: center; width: 44px; height: 44px; border-radius: 10px;
  color: var(--voda-svetla); background: rgba(58, 160, 201, 0.12); }
.pruh .pruh-nazev { min-width: 0; flex: 1 1 auto; }
[data-testid="stMarkdownContainer"] .pruh h1 {
  font-family: var(--display); font-size: 1.85rem; font-weight: 750; line-height: 1; letter-spacing: -0.005em;
  margin: 0; padding: 0; color: var(--text);
}
[data-testid="stMarkdownContainer"] .pruh p { margin: 0.3rem 0 0; color: var(--tlumene); font-size: 0.9rem;
  line-height: 1.4; max-width: 62ch; }
.pruh .pruh-stav { display: flex; gap: 0.5rem; margin: 0; flex: none; }
.pruh .pruh-stav > div { padding: 0.45rem 0.75rem; border-radius: 10px; background: rgba(255, 255, 255, 0.035);
  border: 1px solid var(--cara); }
.pruh dt { font-size: 11px; font-weight: 700; letter-spacing: 0.09em; text-transform: uppercase; color: var(--tlumene); }
.pruh dd { margin: 0.15rem 0 0; font-weight: 600; font-size: 0.95rem; white-space: nowrap; color: var(--text);
  display: flex; align-items: center; gap: 0.45rem; font-variant-numeric: proportional-nums; }
.pruh .tecka { width: 8px; height: 8px; border-radius: 50%%; border: 1.5px solid var(--tlumene); flex: none; }
.pruh .tecka.zive { border: 0; background: var(--voda); animation: puls 2.4s var(--ven) infinite; }
@keyframes puls { 0%% { box-shadow: 0 0 0 0 rgba(58, 160, 201, 0.55); } 70%%, 100%% { box-shadow: 0 0 0 9px rgba(58, 160, 201, 0); } }

/* záložky jako segmentovaná navigace */
[data-testid="stTabs"] [role="tablist"] {
  gap: 4px; padding: 4px; width: fit-content; max-width: 100%%; margin-bottom: 0.75rem; overflow: visible;
  background: var(--panel); border: 1px solid var(--cara); border-radius: var(--r); box-shadow: none;
}
[data-testid="stTabs"] [role="tablist"]::before, [data-testid="stTabs"] [role="tablist"]::after { display: none; }
[data-testid="stTab"] > div:not([data-testid]) { display: none; }
[data-testid="stTab"] {
  display: inline-flex; align-items: center; gap: 0.55rem; height: auto; margin: 0; padding: 0.55rem 1rem 0.55rem 0.85rem;
  border: 1px solid transparent; border-radius: 9px; background: transparent; color: var(--tlumene); cursor: pointer;
  transition: background-color 160ms var(--ven), color 160ms var(--ven), border-color 160ms var(--ven);
}
[data-testid="stTab"]::before {
  content: ""; width: 18px; height: 18px; flex: none; background: currentColor;
  -webkit-mask: var(--ikona) center / contain no-repeat; mask: var(--ikona) center / contain no-repeat;
}
[data-testid="stTab"]:nth-child(1) { --ikona: %(IKONA_VODOCET)s; }
[data-testid="stTab"]:nth-child(2) { --ikona: %(IKONA_KVALITA)s; }
[data-testid="stTab"]:nth-child(3) { --ikona: %(IKONA_MAPA)s; }
[data-testid="stTab"]:nth-child(4) { --ikona: %(IKONA_ANIMACE)s; }
[data-testid="stTab"]:hover { color: var(--text); background: var(--najeti); }
[data-testid="stTab"][aria-selected="true"] { color: #fff; background: var(--aktivni); border-color: #fff; }
[data-testid="stTab"][data-focus-visible] { outline: 2px solid var(--voda); outline-offset: 2px; }
[data-testid="stTab"] p { font-size: 0.95rem; font-weight: 600; margin: 0; color: inherit; }

/* nadpisy a texty */
[data-testid="stMain"] h3 { font-family: var(--display); font-size: 2.1rem; font-weight: 700; letter-spacing: -0.005em;
  line-height: 1.05; padding: 0.5rem 0 0; }
[data-testid="stMain"] [data-testid="stHeading"] { margin-bottom: 0.4rem; }
[data-testid="stMain"] [data-testid="stMarkdownContainer"] > p { max-width: 78ch; line-height: 1.55; }
.st-key-animace_povoden { max-width: 22rem; }
[data-testid="stCaptionContainer"] { color: var(--tlumene); max-width: 96ch; line-height: 1.5; }
[data-testid="stCaptionContainer"] p { font-size: 0.85rem; }

/* řádek hodnot: teď, 12, 24 a 36 h */
.st-key-pult [data-testid="stHorizontalBlock"] {
  gap: 0; background: var(--panel); border: 1px solid var(--cara); border-radius: var(--r); overflow: hidden;
}
.st-key-pult [data-testid="stColumn"] { position: relative; padding: 1.45rem 1.25rem 1.15rem; border-left: 1px solid var(--cara); }
.st-key-pult [data-testid="stColumn"]:first-child { border-left: 0; background: rgba(255, 255, 255, 0.025); }
.st-key-pult [data-testid="stColumn"]::before { content: ""; position: absolute; inset: 0 0 auto 0; height: 4px; background: var(--spa); }
.st-key-pult [data-testid="stColumn"]:has(.spa-0) { --spa: %(SPA0)s; }
.st-key-pult [data-testid="stColumn"]:has(.spa-1) { --spa: %(SPA1)s; }
.st-key-pult [data-testid="stColumn"]:has(.spa-2) { --spa: %(SPA2)s; }
.st-key-pult [data-testid="stColumn"]:has(.spa-3) { --spa: %(SPA3)s; }
.st-key-pult [data-testid="stColumn"] [data-testid="stVerticalBlock"] { gap: 0.6rem; }
[data-testid="stMetricLabel"] p { font-size: 11px; font-weight: 700; letter-spacing: 0.09em; text-transform: uppercase; color: var(--tlumene); }
[data-testid="stMetricValue"] { font-family: var(--display); font-size: 3.75rem; font-weight: 750; line-height: 1;
  letter-spacing: -0.01em; font-variant-numeric: tabular-nums; padding: 0.15rem 0 0.1rem; }
[data-testid="stMetricDelta"] { font-variant-numeric: tabular-nums; font-weight: 600; }
.odznak { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 6px; font-size: 0.8rem; font-weight: 700;
  line-height: 1.3; white-space: nowrap; }
.st-key-pult [data-testid="stCaptionContainer"] p { font-variant-numeric: tabular-nums; font-size: 0.85rem; }

/* věta pro laika jako citát */
.st-key-citat [data-testid="stAlertContainer"] { background: transparent; border: 0; padding: 0.4rem 0 0.4rem 3.1rem; position: relative; }
.st-key-citat [data-testid="stAlertContainer"]::before {
  content: "\\201E"; position: absolute; left: 0; top: -1.45rem; font-family: var(--pismo); font-size: 4.6rem;
  font-weight: 800; line-height: 1; color: var(--voda);
}
.st-key-citat [data-testid="stAlertContainer"] p { font-size: 1.3rem; line-height: 1.5; color: var(--text); max-width: 70ch; font-weight: 500; }

/* ostatní hlášky */
[data-testid="stAlertContainer"] { border-radius: var(--r); }

/* grafy, tabulky, mapy */
[data-testid="stPlotlyChart"] { background: var(--panel); border: 1px solid var(--cara); border-radius: var(--r); padding: 0; overflow: hidden; }
[data-testid="stDataFrame"] { border-radius: var(--r); }
iframe, [data-testid="stDeckGlJsonChart"] { border-radius: var(--r); }

/* ovládání v hlavní části: vodorovné volby jako segmenty */
[data-testid="stMain"] [data-testid="stRadioGroup"] {
  display: inline-flex; flex-wrap: wrap; gap: 3px; padding: 3px; width: fit-content;
  background: var(--panel); border: 1px solid var(--cara); border-radius: var(--r);
}
[data-testid="stMain"] [data-testid="stRadioGroup"] > div { margin: 0; }
[data-testid="stMain"] [data-testid="stRadioOption"] {
  margin: 0; padding: 0.3rem 0.95rem; border: 1px solid transparent; border-radius: 9px; cursor: pointer;
  transition: background-color 160ms var(--ven), border-color 160ms var(--ven);
}
[data-testid="stRadioOption"] > div > div:first-child:not([data-testid]) { display: none; }
[data-testid="stMain"] [data-testid="stRadioOption"]:hover { background: var(--najeti); }
[data-testid="stMain"] [data-testid="stRadioOption"][data-selected="true"] { background: var(--aktivni); border-color: #fff; }
[data-testid="stRadioOption"]:has(input:focus-visible) { outline: 2px solid var(--voda); outline-offset: 2px; }
[data-testid="stRadioOption"] p { font-weight: 600; font-variant-numeric: tabular-nums; }
[data-testid="stWidgetLabel"] p { font-size: 11px; font-weight: 700; letter-spacing: 0.09em; text-transform: uppercase; color: var(--tlumene); }
[data-testid="stCheckbox"] [data-testid="stWidgetLabel"] p { font-size: 0.95rem; font-weight: 600; letter-spacing: 0; text-transform: none; color: var(--text); }
[data-testid="stBaseButton-secondary"] { background: var(--panel); border: 1px solid var(--cara-silna); border-radius: 10px; font-weight: 600;
  transition: background-color 160ms var(--ven), border-color 160ms var(--ven); }
[data-testid="stBaseButton-secondary"]:hover { background: var(--aktivni); border-color: #fff; color: #fff; }

/* levé menu */
[data-testid="stSidebar"] { background: var(--panel); border-right: 1px solid var(--cara); backdrop-filter: blur(12px); }
[data-testid="stSidebar"] h2 { font-family: var(--display); font-size: 1.6rem; font-weight: 750; letter-spacing: 0; }
[data-testid="stSidebar"] h3 { font-family: var(--pismo); font-size: 0.95rem; font-weight: 700; letter-spacing: 0;
  margin-top: 0.5rem; padding-top: 1.1rem; border-top: 1px solid var(--cara); }
[data-testid="stSidebar"] [data-testid="stRadioGroup"] { gap: 6px; }
[data-testid="stSidebar"] [data-testid="stRadioGroup"] > div {
  position: relative; display: grid; grid-template-columns: 34px 1fr; column-gap: 0.7rem; align-items: center;
  margin: 0; padding: 0.6rem 0.75rem; border-radius: 10px; border: 1px solid var(--cara); background: rgba(255, 255, 255, 0.03);
  transition: background-color 160ms var(--ven), border-color 160ms var(--ven);
}
[data-testid="stSidebar"] [data-testid="stRadioGroup"] > div::before {
  content: ""; grid-row: 1 / span 2; width: 34px; height: 34px; border-radius: 8px;
  background: %(IKONA_STANICE)s center / 20px no-repeat, rgba(255, 255, 255, 0.06);
}
[data-testid="stSidebar"] [data-testid="stRadioGroup"] > div:hover { background: var(--najeti); }
[data-testid="stSidebar"] [data-testid="stRadioGroup"] > div[data-selected="true"] { background: var(--aktivni); border-color: #fff; }
[data-testid="stSidebar"] [data-testid="stRadioGroup"] > div[data-selected="true"]::before {
  background: %(IKONA_STANICE_AKTIVNI)s center / 20px no-repeat, rgba(58, 160, 201, 0.2);
}
[data-testid="stSidebar"] [data-testid="stRadioOption"] { margin: 0; cursor: pointer; }
[data-testid="stSidebar"] [data-testid="stRadioOption"]::after { content: ""; position: absolute; inset: 0; }
[data-testid="stSidebar"] [data-testid="stRadioCaption"] { margin: 0; padding: 0; }
[data-testid="stSidebar"] [data-testid="stRadioCaption"] p { font-size: 0.8rem; font-variant-numeric: tabular-nums; }

@media (max-width: 640px) {
  [data-testid="stMarkdownContainer"] .pruh { flex-wrap: wrap; align-items: flex-start; }
  .pruh .pruh-nazev { flex-basis: calc(100%% - 60px); }
  [data-testid="stMarkdownContainer"] .pruh h1 { font-size: 1.6rem; }
  .pruh .pruh-stav { flex-wrap: wrap; width: 100%%; }
  .pruh .pruh-stav > div { flex: 1 1 auto; }
  [data-testid="stTabs"] [role="tablist"] { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); width: 100%%; }
  [data-testid="stTab"] { justify-content: flex-start; min-width: 0; padding: 0.5rem 0.6rem; }
  [data-testid="stTab"] p { font-size: 0.85rem; white-space: normal; text-align: left; line-height: 1.2; }
  [data-testid="stMain"] h3 { font-size: 1.7rem; }
  .st-key-pult [data-testid="stColumn"] { border-left: 0; border-top: 1px solid var(--cara); padding: 1.2rem 1rem 1rem; }
  .st-key-pult [data-testid="stColumn"]:first-child { border-top: 0; }
  [data-testid="stMetricValue"] { font-size: 3.1rem; }
  [data-testid="stPlotlyChart"] .modebar-container { display: none; }
  .st-key-citat [data-testid="stAlertContainer"] { padding-left: 2.4rem; }
  .st-key-citat [data-testid="stAlertContainer"] p { font-size: 1.12rem; }
  .st-key-citat [data-testid="stAlertContainer"]::before { font-size: 4.2rem; top: -1.1rem; }
}
@media (prefers-reduced-motion: reduce) {
  .pruh .tecka.zive { animation: none; }
  * { transition-duration: 0s !important; }
}
"""


def pouzij():
    """Vloží písma a styly; volá se hned po st.set_page_config."""
    from predikce import BARVY
    hodnoty = dict(POZADI=POZADI, PANEL=PANEL, CARA=CARA, TEXT=TEXT, TLUMENE=TLUMENE, VODA=VODA, VODA_SVETLA=VODA_SVETLA,
                   PISMO=PISMO, DISPLAY=DISPLAY, SPA0=BARVY[0], SPA1=BARVY[1], SPA2=BARVY[2], SPA3=BARVY[3],
                   IKONA_VODOCET=_url("vodocet"), IKONA_KVALITA=_url("kvalita"), IKONA_MAPA=_url("mapa"),
                   IKONA_ANIMACE=_url("animace"), IKONA_STANICE=_url("vodocet", TLUMENE),
                   IKONA_STANICE_AKTIVNI=_url("vodocet", VODA_SVETLA))
    st.markdown(f'<style id="styl-pultu">{CSS % hodnoty}</style>', unsafe_allow_html=True)
