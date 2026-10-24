"""Vzhled aplikace: světlý povodňový pult s vodočtem, stejný jazyk jako grafy v prezentaci (bílé pozadí, modrá a
oranžová z grafů, systémové písmo Applu, zaoblené karty). Barvy, písma, šablona grafů, vodočet v SVG a styly prvků
Streamlitu.

Prvky Streamlitu se stylují přes data-testid a klíče kontejnerů (třída st-key-<klíč>). Karta je každý kontejner
s klíčem začínajícím na karta_.
"""
import base64
import math
from pathlib import Path

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

POZADI = "#f5f5f7"
STUDNA = "#ffffff"  # karty a levý panel
OVLADAC = "#e9e9eb"  # dráha přepínačů, lať vodočtu
TEXT = "#1d1d1f"
TEXT2 = "#6e6e73"
TLUMENE = "#86868b"
CARA = "#e5e5ea"
CARA_SILNA = "#d2d2d7"
JAKO_TED = "#666666"  # „bude jako teď“, stejná šedá jako v grafech prezentace
VODA = "#167c9c"  # modrá z grafů prezentace (tmavé sloupce)
VODA_SVETLA = "#9fcad8"  # světlé sloupce
ORANZOVA = "#cb6c31"
SPA = ["#f2c437", "#ef6c00", "#c62828"]
NA_SPA = [TEXT, STUDNA, STUDNA]  # písmo na výplni stupně: na žluté tmavé, na oranžové a červené bílé
PISMO = ('-apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", Inter, "Helvetica Neue", Helvetica, '
         'sans-serif')  # na Macu San Francisco, jinde Inter z app/fonts (Helvetica by se na Windows nahradila Arialem)
FONTY = Path(__file__).resolve().parent / "fonts"
ROZSAHY = {"inter-latin.woff2": "U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, "
                                "U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, "
                                "U+FFFD",
           "inter-latin-ext.woff2": "U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, "
                                    "U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C4, "
                                    "U+2113, U+2C60-2C7F, U+A720-A7FF"}

GRAF = {"displaylogo": False, "modeBarButtons": [["toImage"]],
        "toImageButtonOptions": {"format": "png", "scale": 2, "filename": "labe_graf"}}


def _pisma():
    """Inter (OFL) z app/fonts vložený do CSS jako base64, ať aplikace nic nestahuje z internetu."""
    s = []
    for soubor, rozsah in ROZSAHY.items():
        f = FONTY / soubor
        if f.exists():
            data = base64.b64encode(f.read_bytes()).decode()
            s.append("@font-face { font-family: Inter; font-style: normal; font-weight: 100 900; font-display: swap; "
                     f"src: url(data:font/woff2;base64,{data}) format('woff2'); unicode-range: {rozsah}; }}")
    return "".join(s)


PISMA = _pisma()


def _sablona():
    osa = dict(gridcolor=CARA, linecolor=CARA_SILNA, showline=True, zeroline=False, ticks="outside", ticklen=4,
               tickcolor=CARA_SILNA, tickfont=dict(color=TEXT2, size=13),
               title=dict(font=dict(color=TEXT2, size=13), standoff=10))
    return go.layout.Template(layout=dict(
        paper_bgcolor=STUDNA, plot_bgcolor=STUDNA, colorway=[VODA, ORANZOVA, JAKO_TED, VODA_SVETLA],
        font=dict(family=PISMO, size=13, color=TEXT), xaxis=osa, yaxis=osa,
        hovermode="x unified", margin=dict(l=8, r=8, t=44, b=8),
        hoverlabel=dict(bgcolor=STUDNA, bordercolor=CARA_SILNA, font=dict(family=PISMO, color=TEXT, size=13)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, xanchor="left", bgcolor="rgba(0,0,0,0)",
                    font=dict(color=TEXT2, size=13)),
        modebar=dict(bgcolor="rgba(0,0,0,0)", color=TLUMENE, activecolor=TEXT)))


pio.templates["pult"] = _sablona()


def cary_spa(fig, prahy, ymax=None):
    """Vodorovné tečkované čáry stupňů povodňové aktivity se štítkem; při nízké vodě jen ty v dosahu dat."""
    for n, (prah, barva, pismo) in enumerate(zip(prahy, SPA, NA_SPA), 1):
        if ymax is not None and prah > ymax * 1.6 + 60:
            continue
        fig.add_hline(y=prah, line=dict(color=barva, width=1.5, dash="dot"), layer="below",
                      annotation=dict(text=f"{n}. stupeň · {prah} cm", bgcolor=barva, borderpad=4,
                                      font=dict(family=PISMO, size=12, color=pismo, weight=600)),
                      annotation_position="top left")


def graf(fig, vyska):
    """Vzhled grafů z prezentace; barvy a písma i přímo v layoutu, protože Streamlit jinak vnutí svoje téma."""
    sablona = pio.templates["pult"].layout
    fig.update_layout(template="pult", height=vyska, paper_bgcolor=STUDNA, plot_bgcolor=STUDNA, font=sablona.font,
                      hoverlabel=sablona.hoverlabel, legend=sablona.legend, modebar=sablona.modebar,
                      margin=dict(l=56, r=12, t=44, b=48), hovermode="x unified")
    fig.update_xaxes(sablona.xaxis.to_plotly_json(), tickformat="%-d. %-m.\n%H:%M", automargin=True)
    fig.update_yaxes(sablona.yaxis.to_plotly_json(), automargin=True)
    for tvar in fig.layout.shapes:  # svislá čára okamžiku má na bílé barvu hrany, ať je vidět
        if tvar.type == "line" and tvar.x0 == tvar.x1:
            tvar.line.color = CARA_SILNA


def stitek(text, vpravo=""):
    """Nadpis karty: malý štítek, případně s údajem vpravo."""
    return f'<div class="stitek"><b>{text}</b>{f"<i>{vpravo}</i>" if vpravo else ""}</div>'


def sekce(text):
    st.markdown(f'<div class="sekce">{text}</div>', unsafe_allow_html=True)


def _znak(velikost=44):
    """Malá měrná lať s vodou, znak aplikace."""
    carky = "".join(f'<line x1="14" x2="{22 if i % 5 else 30}" y1="{6 + i * 3}" y2="{6 + i * 3}"/>' for i in range(11))
    return (f'<svg viewBox="0 0 44 44" width="{velikost}" height="{velikost}" aria-hidden="true">'
            f'<rect x="12" y="3" width="20" height="38" rx="5" fill="{OVLADAC}"/>'
            f'<g stroke="{TEXT2}" stroke-width="1.2" stroke-opacity=".8">{carky}</g>'
            f'<path d="M12 25h20v11a5 5 0 0 1 -5 5h-10a5 5 0 0 1 -5 -5z" fill="{VODA}" fill-opacity=".55"/>'
            f'<path d="M4 25.5h36" stroke="{VODA}" stroke-width="2.5" stroke-linecap="round"/></svg>')


def hlavicka(okamzik, model, zdroj, zive):
    """Tiráž: otázka, na kterou aplikace odpovídá, a stav (okamžik, model, zdroj dat)."""
    tecka = f'<i class="tecka{" zive" if zive else ""}"></i>'
    return ('<header class="tiraz">'
            f'<div class="tiraz-znak">{_znak()}</div>'
            '<div class="tiraz-nazev"><h1>Kolik vody přiteče do Děčína a&nbsp;Ústí</h1>'
            '<p>Předpověď hladiny Labe na&nbsp;12, 24 a&nbsp;36 hodin pro povodňovou komisi města a&nbsp;lidi '
            'u&nbsp;řeky.</p></div>'
            '<dl class="tiraz-stav">'
            f'<div><dt>Okamžik</dt><dd>{okamzik}</dd></div>'
            f'<div><dt>Model</dt><dd>{model}</dd></div>'
            f'<div><dt>Data</dt><dd>{tecka}{zdroj}</dd></div>'
            '</dl></header>')


def panel_hlava():
    return (f'<div class="panel-hlava">{_znak(36)}<div><b>Povodňový pult</b>'
            '<small>Labe, Děčín a&nbsp;Ústí nad&nbsp;Labem</small></div></div>')


def vodocet(prahy, ted, pred, rozmezi, chmu=None):
    """Svislá měrná lať: stupně povodňové aktivity, hladina teď a předpověď za 12, 24 a 36 h s rozmezím nejistoty.

    prahy jsou tři stupně v cm, pred {h: cm}, rozmezi {h: (dolní, horní) nebo None}, chmu {h: cm nebo None}.
    """
    chmu = {h: v for h, v in (chmu or {}).items() if v is not None}
    vse = [ted, *pred.values(), *chmu.values()] + [x for r in rozmezi.values() if r for x in r]
    dole = max(0, math.floor(min(min(vse) - 60, prahy[0] - 100) / 50) * 50)
    nahore = math.ceil(max(max(vse) + 50, prahy[2] + 90) / 50) * 50
    W, H, T, B = 480, 600, 14, 40
    dno = H - B
    k = (dno - T) / (nahore - dole)

    def y(cm):
        return round(T + (nahore - cm) * k, 1)

    L0, L1, STITKY, POPIS = 50, 124, 380, 214  # lať, štítky stupňů vpravo, začátek popisků předpovědi
    pruhy = {12: L1 + 12, 24: L1 + 28, 36: L1 + 44}  # pruhy rozmezí vedle latě, šířka 10
    s = []
    hranice = list(prahy) + [nahore]
    for i in range(3):  # zóny stupňů vpravo od latě a barevný pruh na její hraně
        a, b = max(hranice[i], dole), min(hranice[i + 1], nahore)
        if a < b:
            s.append(f'<rect x="{L1}" y="{y(b)}" width="{W - L1}" height="{round(y(a) - y(b), 1)}" fill="{SPA[i]}" '
                     f'fill-opacity="{(0.07, 0.07, 0.07)[i]}"/>')
            s.append(f'<rect x="{L1}" y="{y(b)}" width="5" height="{round(y(a) - y(b), 1)}" fill="{SPA[i]}"/>')
    s.append(f'<rect x="{L0}" y="{T}" width="{L1 - L0}" height="{dno - T}" rx="6" fill="{OVLADAC}"/>')
    for cm in range(dole, nahore, 10):  # střídavé bloky po 10 cm jako na skutečné lati
        if cm // 10 % 2 == 0:
            x = L0 + 8 if cm // 100 % 2 == 0 else L1 - 30
            s.append(f'<rect x="{x}" y="{y(cm + 10)}" width="22" height="{round(y(cm) - y(cm + 10), 1)}" '
                     f'fill="{TEXT}" fill-opacity=".07"/>')
    for cm in range(dole, nahore + 1, 10):
        x2, op = (L1, 0.55) if cm % 100 == 0 else (L0 + 30, 0.35) if cm % 50 == 0 else (L0 + 8, 0.2)
        s.append(f'<line x1="{L0}" x2="{x2}" y1="{y(cm)}" y2="{y(cm)}" stroke="{TEXT}" stroke-opacity="{op}"/>')
        if cm % 100 == 0:
            s.append(f'<text x="{L0 - 8}" y="{y(cm) + 5}" text-anchor="end" class="lat-cislo">{cm}</text>')
    s.append(f'<rect x="{L0}" y="{y(ted)}" width="{L1 + 5 - L0}" height="{round(dno - y(ted), 1)}" fill="{VODA}" '
             f'fill-opacity=".45"/>')
    s.append(f'<line x1="{L0}" x2="{W}" y1="{dno}" y2="{dno}" stroke="{CARA_SILNA}"/>')

    for n, (prah, barva, pismo) in enumerate(zip(prahy, SPA, NA_SPA), 1):
        yp = y(prah)
        s.append(f'<line x1="{L0}" x2="{STITKY}" y1="{yp}" y2="{yp}" stroke="{barva}" stroke-width="1.5" '
                 f'stroke-dasharray="1.5 4" stroke-linecap="round"/>')
        s.append(f'<rect x="{STITKY}" y="{yp - 12}" width="{W - STITKY}" height="24" rx="12" fill="{barva}"/>')
        s.append(f'<text x="{(STITKY + W) / 2}" y="{yp + 4.5}" text-anchor="middle" class="lat-stupen" '
                 f'fill="{pismo}">{n}. stupeň {prah}</text>')

    s.append(f'<line x1="0" x2="{STITKY}" y1="{y(ted)}" y2="{y(ted)}" stroke="{VODA}" stroke-width="2"/>')
    s.append(f'<rect x="0" y="{y(ted) - 13}" width="{L0 - 5}" height="26" rx="13" fill="{VODA}"/>')
    s.append(f'<text x="{(L0 - 5) / 2}" y="{y(ted) + 5.5}" text-anchor="middle" class="lat-ted">{ted:.0f}</text>')

    popisky = sorted(((y(pred[h]), h) for h in pruhy), reverse=False)
    polohy = []
    for yp, h in popisky:  # popisky nad sebou bez překryvu
        polohy.append(max(yp, polohy[-1] + 34) if polohy else yp)
    posun = max(0, polohy[-1] - (dno - 16))
    polohy = [p - posun for p in polohy]
    for (yp, h), ly in zip(popisky, polohy):
        x, p = pruhy[h], pred[h]
        if rozmezi.get(h):
            lo, hi = rozmezi[h]
            s.append(f'<rect x="{x}" y="{y(hi)}" width="10" height="{round(y(lo) - y(hi), 1)}" rx="5" '
                     f'fill="{VODA_SVETLA}" fill-opacity=".75"/>')
        s.append(f'<rect x="{x - 3}" y="{yp - 2}" width="16" height="4" rx="2" fill="{VODA}"/>')
        if h in chmu:
            s.append(f'<path d="M{x + 12} {y(chmu[h])}l8 -5v10z" fill="{TEXT}"/>')
        s.append(f'<path d="M{x + 13} {yp}H{L1 + 66}L{POPIS - 8} {ly}H{POPIS - 2}" fill="none" '
                 f'stroke="{VODA}" stroke-opacity=".5"/>')
        s.append(f'<rect x="{POPIS - 2}" y="{ly - 15}" width="{166 if h in chmu else 122}" height="30" '
                 f'fill="{STUDNA}" fill-opacity=".9" rx="8"/>')
        dalsi = f'<tspan class="lat-chmu"> · ČHMÚ {chmu[h]:.0f}</tspan>' if h in chmu else ""
        s.append(f'<text x="{POPIS + 46}" y="{ly + 9}" text-anchor="end" class="lat-hodnota">{p:.0f}</text>'
                 f'<text x="{POPIS + 52}" y="{ly + 7}" class="lat-osa">cm za {h} h{dalsi}</text>')
    s.append(f'<rect x="{L0}" y="{dno + 16}" width="14" height="10" rx="5" fill="{VODA_SVETLA}" fill-opacity=".75"/>'
             f'<text x="{L0 + 20}" y="{dno + 25}" class="lat-legenda">rozmezí nejistoty (90 % chyb)</text>'
             f'<rect x="{L0 + 196}" y="{dno + 16}" width="14" height="10" rx="2" fill="{VODA}" fill-opacity=".45"/>'
             f'<text x="{L0 + 216}" y="{dno + 25}" class="lat-legenda">voda teď</text>')
    if chmu:
        s.append(f'<path d="M{L0 + 290} {dno + 21}l8 -5v10z" fill="{TEXT}"/>'
                 f'<text x="{L0 + 304}" y="{dno + 25}" class="lat-legenda">ČHMÚ</text>')
    popis = (f"Vodočet: teď {ted:.0f} cm, " + ", ".join(f"za {h} h {pred[h]:.0f} cm" for h in pruhy)
             + f"; stupně povodňové aktivity {prahy[0]}, {prahy[1]} a {prahy[2]} cm.")
    return (f'<div class="lat"><svg viewBox="0 0 {W} {H}" role="img" aria-label="{popis}" '
            f'preserveAspectRatio="xMidYMid meet">{"".join(s)}</svg></div>')


CSS = r"""
:root {
  --pismo: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", Inter, "Helvetica Neue", Helvetica, sans-serif;
  --r: 22px; --r-maly: 14px; --pilulka: 999px;
  --stin: 0 1px 2px rgba(0, 0, 0, 0.04), 0 10px 30px rgba(0, 0, 0, 0.06);
  --stin-segment: 0 1px 2px rgba(0, 0, 0, 0.08), 0 3px 8px rgba(0, 0, 0, 0.06);
  --ven: cubic-bezier(0.16, 1, 0.3, 1);
}
html { font-size: 17px; }
html, body, .stApp { background: var(--pozadi); color: var(--text); font-family: var(--pismo); -webkit-font-smoothing: antialiased; }
.stApp :not(code, pre, kbd, samp, svg, svg *, .material-symbols-rounded, [data-testid="stIconMaterial"]) { font-family: var(--pismo); }
::selection { background: rgba(22, 124, 156, 0.22); color: var(--text); }
* { scrollbar-width: thin; scrollbar-color: rgba(0, 0, 0, 0.18) transparent; }
:focus-visible { outline: 2px solid var(--voda); outline-offset: 2px; }
input, textarea { caret-color: var(--voda); }
div[data-testid="stElementContainer"]:has(style#styl-pultu) { display: none; }

/* chrome Streamlitu: zůstává jen tlačítko levého panelu */
header[data-testid="stHeader"], header[data-testid="stHeader"] * { background: transparent; pointer-events: none; }
header[data-testid="stHeader"] button, header[data-testid="stHeader"] button * { pointer-events: auto; }
header[data-testid="stHeader"] button { background: var(--studna); box-shadow: 0 0 0 1px var(--cara-silna), var(--stin); border-radius: var(--pilulka); color: var(--text); }
[data-testid="stToolbarActions"], [data-testid="stAppDeployButton"], [data-testid="stMainMenu"],
[data-testid="stDecoration"], [data-testid="stHeaderActionElements"], footer { display: none !important; }
[data-testid="stMainBlockContainer"] { max-width: 1280px; padding: 32px 40px 80px; }
[data-testid="stMain"] [data-testid="stVerticalBlock"] { gap: 20px; }

/* tiráž */
[data-testid="stMarkdownContainer"] .tiraz {
  display: grid; grid-template-columns: auto minmax(0, 1fr) auto; align-items: center; gap: 0 20px;
  padding: 4px 0 24px; border-bottom: 1px solid var(--cara);
}
.tiraz .tiraz-znak { line-height: 0; }
[data-testid="stMarkdownContainer"] .tiraz h1 {
  font-size: 38px; font-weight: 700; line-height: 1.1; letter-spacing: -0.02em; margin: 0; padding: 0; color: var(--text); text-wrap: balance;
}
[data-testid="stMarkdownContainer"] .tiraz p { margin: 6px 0 0; color: var(--text2); font-size: 17px; line-height: 1.5; max-width: 62ch; text-wrap: pretty; }
.tiraz dl { display: flex; gap: 10px; margin: 0; }
.tiraz dl > div { padding: 10px 16px 11px; background: var(--studna); border: 1px solid var(--cara); border-radius: var(--r-maly); box-shadow: var(--stin); }
.tiraz dt { font-size: 13px; font-weight: 600; color: var(--text2); line-height: 1.3; }
.tiraz dd { margin: 2px 0 0; font-size: 17px; font-weight: 700; letter-spacing: -0.01em; line-height: 1.3;
  white-space: nowrap; color: var(--text); display: flex; align-items: center; gap: 8px; font-variant-numeric: tabular-nums; }
.tiraz .tecka { width: 9px; height: 9px; border-radius: 50%; box-shadow: inset 0 0 0 1.5px var(--tlumene); flex: none; }
.tiraz .tecka.zive { box-shadow: none; background: var(--voda); animation: puls 2.4s var(--ven) infinite; }
@keyframes puls { 0% { box-shadow: 0 0 0 0 rgba(22, 124, 156, 0.45); } 70%, 100% { box-shadow: 0 0 0 10px rgba(22, 124, 156, 0); } }

/* záložky: segmentovaný přepínač */
[data-testid="stTabs"] [role="tablist"] {
  display: inline-flex; gap: 2px; padding: 3px; margin: 0 0 24px; width: fit-content; max-width: 100%;
  background: var(--ovladac); border: 0; border-radius: var(--pilulka); box-shadow: none; overflow: visible;
}
[data-testid="stTabs"] [role="tablist"]::before, [data-testid="stTabs"] [role="tablist"]::after { display: none; }
[data-testid="stTabsScrollRight"], [data-testid="stTabsScrollLeft"] { display: none; }
[data-testid="stTab"] > div:not([data-testid]) { display: none; }
[data-testid="stTab"] {
  position: relative; height: auto; min-height: 40px; margin: 0; padding: 0 18px; display: flex; align-items: center;
  background: none; border: 0; border-radius: var(--pilulka); color: var(--text2); cursor: pointer;
  transition: color 160ms var(--ven), background-color 160ms var(--ven), box-shadow 160ms var(--ven);
}
[data-testid="stTab"] p { font-size: 15px; font-weight: 600; margin: 0; color: inherit; line-height: 1.2; white-space: nowrap; }
[data-testid="stTab"]:hover { color: var(--text); }
[data-testid="stTab"][aria-selected="true"] { color: var(--text); background: var(--studna); box-shadow: var(--stin-segment); }
[data-testid="stTab"][data-focus-visible] { outline: 2px solid var(--voda); outline-offset: 2px; }

/* texty */
[data-testid="stMain"] [data-testid="stHeading"] h3 {
  font-size: 28px; font-weight: 700; letter-spacing: -0.02em; line-height: 1.2; padding: 0; color: var(--text);
}
[data-testid="stMain"] [data-testid="stMarkdown"] p { color: var(--text); font-size: 17px; line-height: 1.5; max-width: 75ch; }
[data-testid="stMain"] [data-testid="stMarkdown"] p strong { color: var(--text); font-weight: 600; }
[data-testid="stCaptionContainer"] { color: var(--text2); }
[data-testid="stCaptionContainer"] p, [data-testid="stMain"] [data-testid="stMarkdown"] [data-testid="stCaptionContainer"] p { font-size: 13px; line-height: 1.5; max-width: 110ch; color: var(--text2); }
[data-testid="stWidgetLabel"] p, .stitek b, .sekce { font-size: 13px; font-weight: 600; letter-spacing: 0; text-transform: none; color: var(--text2); line-height: 1.4; }
/* kontejner markdownu má záporný spodní okraj 1rem (počítá s odstavcem), vlastní divy ho musí vyrovnat */
.stitek { display: flex; justify-content: space-between; align-items: baseline; gap: 16px; margin-bottom: 0.65rem; }
.sekce, .panel-hlava { margin-bottom: 1rem; }
.stitek i { font-style: normal; font-size: 13px; font-weight: 500; color: var(--tlumene); font-variant-numeric: tabular-nums; }

/* karty: bílé, zaoblené, vlasová hrana, měkký stín */
[class*="st-key-karta"] {
  background: var(--studna); border: 1px solid var(--cara); border-radius: var(--r); padding: 20px 24px 24px; box-shadow: var(--stin);
}
[class*="st-key-karta"] [data-testid="stVerticalBlock"] { gap: 14px; }

/* vodočet */
.lat svg { display: block; width: 100%; height: auto; max-height: 640px; overflow: visible; }
.lat text { font-family: var(--pismo); }
.lat .lat-cislo { font-size: 13px; font-weight: 600; fill: var(--tlumene); font-variant-numeric: tabular-nums; }
.lat .lat-stupen { font-size: 13px; font-weight: 600; }
.lat .lat-hodnota { font-size: 30px; font-weight: 800; letter-spacing: -0.03em; fill: var(--text); font-variant-numeric: tabular-nums; }
.lat .lat-ted { font-size: 15px; font-weight: 700; fill: var(--studna); font-variant-numeric: tabular-nums; }
.lat .lat-osa { font-size: 15px; font-weight: 600; fill: var(--text2); }
.lat .lat-legenda { font-size: 12px; fill: var(--text2); }
.lat .lat-chmu { font-size: 13px; font-weight: 600; fill: var(--tlumene); }

/* odečty u vodočtu */
[class*="st-key-cteni_"] { display: grid; grid-template-columns: minmax(0, 1fr) auto; column-gap: 16px; row-gap: 6px;
  align-content: start; padding: 16px 0 18px; border-top: 1px solid var(--cara); }
.st-key-cteni_ted { border-top: 0; padding-top: 4px; }
[class*="st-key-cteni_"] > [data-testid="stElementContainer"]:nth-child(1) { grid-column: 1; grid-row: 1 / span 2; }
[class*="st-key-cteni_"] > [data-testid="stElementContainer"]:nth-child(2) { grid-column: 2; grid-row: 1; justify-self: end; align-self: start; width: auto; }
[class*="st-key-cteni_"] > [data-testid="stElementContainer"]:nth-child(3) { grid-column: 2; grid-row: 2; justify-self: end; align-self: end; width: auto; text-align: right; }
[class*="st-key-cteni_"] [data-testid="stMetricLabel"] p { font-size: 15px; font-weight: 600; color: var(--text2); display: flex; align-items: center; gap: 8px; }
[class*="st-key-cteni_"] [data-testid="stMetricLabel"] p::before { content: ""; width: 10px; height: 10px; border-radius: 50%; background: var(--voda-svetla); }
.st-key-cteni_ted [data-testid="stMetricLabel"] p::before { background: var(--voda); }
[data-testid="stMetricValue"] { font-size: 48px; font-weight: 800; line-height: 1; letter-spacing: -0.03em; color: var(--text); font-variant-numeric: tabular-nums; }
.st-key-cteni_ted [data-testid="stMetricValue"] { font-size: 64px; }
[data-testid="stMetricValue"] p { color: inherit; font: inherit; }
[data-testid="stMetricDelta"] { color: var(--text2) !important; background: none !important; padding: 0; font-size: 15px; font-weight: 600; font-variant-numeric: tabular-nums; }
[data-testid="stMetricDelta"] svg, [data-testid^="stMetricDeltaIcon"] { display: none; }
[class*="st-key-cteni_"] [data-testid="stCaptionContainer"] p { font-size: 13px; color: var(--text2); font-variant-numeric: tabular-nums; white-space: nowrap; }
.odznak { display: inline-flex; align-items: center; min-height: 28px; padding: 0 12px; border-radius: var(--pilulka); font-size: 13px;
  font-weight: 600; line-height: 1; white-space: nowrap; }
.odznak.spa-0 { background: var(--pozadi); color: var(--text2); box-shadow: inset 0 0 0 1px var(--cara-silna); }
.odznak.spa-1 { background: #f2c437; color: var(--text); }
.odznak.spa-2 { background: #ef6c00; color: #ffffff; }
.odznak.spa-3 { background: #c62828; color: #ffffff; }

/* věta pro laika */
.st-key-karta_citat [data-testid="stAlertContainer"] { background: none; border: 0; padding: 0; box-shadow: none; }
.st-key-karta_citat [data-testid="stAlertContainer"] p { font-size: 21px; line-height: 1.45; letter-spacing: -0.01em; color: var(--text); font-weight: 400; max-width: 70ch; }

/* hlášky */
[data-testid="stAlertContainer"] { border-radius: var(--r-maly); background: var(--pozadi); border: 1px solid var(--cara); color: var(--text); }
[data-testid="stAlertContainer"] p { color: var(--text); }
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentWarning"]) { border-color: rgba(239, 108, 0, 0.45); background: #fff4ea; }

/* souhrnné údaje (Dnešek, kvalita) */
.udaje { display: grid; grid-template-columns: repeat(auto-fit, minmax(8.5rem, 1fr)); gap: 16px 0; margin: 0; }
.udaje > div { padding: 2px 20px 2px; border-left: 1px solid var(--cara); }
.udaje > div:first-child { padding-left: 0; border-left: 0; }
.udaje dt { font-size: 13px; font-weight: 600; color: var(--text2); line-height: 1.4; }
.udaje dd { margin: 4px 0 0; font-size: 36px; font-weight: 800; letter-spacing: -0.03em; line-height: 1; color: var(--text); font-variant-numeric: tabular-nums; }
.udaje dd small { font-size: 15px; font-weight: 600; letter-spacing: 0; color: var(--text2); margin-left: 4px; }
.udaje p { margin: 6px 0 0; font-size: 13px; line-height: 1.4; color: var(--text2); }
.udaje p b { color: var(--text); font-weight: 600; }

/* grafy, tabulky, mapy */
[data-testid="stPlotlyChart"] { background: var(--studna); border-radius: var(--r-maly); }
iframe, [data-testid="stIFrame"], [data-testid="stDeckGlJsonChart"] { border-radius: var(--r); }
[data-testid="stIFrame"] { border: 1px solid var(--cara); background: var(--studna); box-shadow: var(--stin); }
[data-testid="stTable"] { overflow-x: auto; }
[data-testid="stTable"] table { width: 100%; border-collapse: collapse; border: 0; font-variant-numeric: tabular-nums; color: var(--text); }
[data-testid="stTable"] td, [data-testid="stTable"] tbody th { font-size: 15px !important; font-weight: 500; }
[data-testid="stTable"] th, [data-testid="stTable"] td { border: 0; border-bottom: 1px solid var(--cara); padding: 10px 14px; background: none; }
[data-testid="stTable"] thead th { font-size: 13px; font-weight: 600; letter-spacing: 0; text-transform: none;
  color: var(--text2); text-align: right; vertical-align: bottom; line-height: 1.3; border-bottom-color: var(--cara-silna); }
[data-testid="stTable"] tbody th { font-weight: 600; text-align: left; color: var(--text); }
[data-testid="stTable"] td { text-align: right; }

/* volby v hlavní části: segmentovaný přepínač */
[data-testid="stMain"] [data-testid="stRadioGroup"][aria-orientation="horizontal"] {
  display: inline-flex; flex-wrap: wrap; gap: 2px; padding: 3px; width: fit-content; max-width: 100%;
  background: var(--ovladac); border: 0; border-radius: 22px;
}
[data-testid="stRadioGroup"] > div { margin: 0; }
[data-testid="stRadioOption"] > div > div:first-child:not([data-testid]) { display: none; }
[data-testid="stMain"] [data-testid="stRadioOption"] {
  margin: 0; min-height: 38px; display: flex; align-items: center; padding: 0 16px; border-radius: var(--pilulka); cursor: pointer; color: var(--text2);
  transition: background-color 160ms var(--ven), color 160ms var(--ven), box-shadow 160ms var(--ven);
}
[data-testid="stMain"] [data-testid="stRadioOption"] p { font-size: 15px; font-weight: 600; line-height: 1.2; color: inherit; font-variant-numeric: tabular-nums; white-space: nowrap; }
[data-testid="stMain"] [data-testid="stRadioOption"]:hover { color: var(--text); }
[data-testid="stMain"] [data-testid="stRadioOption"][data-selected="true"] { color: var(--text); background: var(--studna); box-shadow: var(--stin-segment); }
[data-testid="stRadioOption"]:has(input:focus-visible) { outline: 2px solid var(--voda); outline-offset: 2px; }

/* režim mapy: dvě velké dlaždice */
.st-key-mapa_rezim [data-testid="stRadioGroup"][aria-orientation="horizontal"] {
  display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); align-items: stretch; width: 100%; gap: 10px; padding: 0; background: none; border: 0; border-radius: 0;
}
.st-key-mapa_rezim [data-testid="stRadio"] { width: 100%; }
.st-key-mapa_rezim [data-testid="stRadioGroup"] > div {
  position: relative; padding: 14px 16px 16px; border-radius: var(--r-maly); background: var(--pozadi); border: 1px solid var(--cara);
  transition: border-color 160ms var(--ven), background-color 160ms var(--ven), box-shadow 160ms var(--ven);
}
.st-key-mapa_rezim [data-testid="stRadioGroup"] > div:hover { border-color: var(--cara-silna); }
.st-key-mapa_rezim [data-testid="stRadioGroup"] > div[data-selected="true"] { background: var(--studna); border-color: var(--voda); box-shadow: 0 0 0 1px var(--voda), var(--stin); }
.st-key-mapa_rezim [data-testid="stRadioOption"] { padding: 0; min-height: 0; background: none !important; box-shadow: none !important; }
.st-key-mapa_rezim [data-testid="stRadioOption"]::after { content: ""; position: absolute; inset: 0; }
.st-key-mapa_rezim [data-testid="stRadioOption"] p { font-size: 17px; font-weight: 700; letter-spacing: -0.01em; white-space: normal; color: var(--text); }
.st-key-mapa_rezim [data-testid="stRadioCaption"] { margin: 4px 0 0; padding: 0; }
.st-key-mapa_rezim [data-testid="stRadioCaption"] p { font-size: 13px; color: var(--text2); }

/* tlačítka */
[data-testid="stBaseButton-primary"] {
  min-height: 44px; padding: 0 22px; border: 0; border-radius: var(--pilulka); background: var(--voda); color: #ffffff;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08); transition: background-color 160ms var(--ven), transform 120ms var(--ven);
}
[data-testid="stBaseButton-primary"]::before { content: ""; width: 11px; height: 13px; margin-right: 10px; background: currentColor; clip-path: polygon(0 0, 100% 50%, 0 100%); }
[data-testid="stBaseButton-primary"] p { font-size: 15px; font-weight: 600; color: inherit; }
[data-testid="stBaseButton-primary"]:hover { background: #136b87; color: #ffffff; }
[data-testid="stBaseButton-primary"]:active { transform: translateY(1px); }
[data-testid="stBaseButton-secondary"] { min-height: 44px; background: var(--studna); border: 1px solid var(--cara-silna); border-radius: var(--pilulka); color: var(--text); }
[data-testid="stBaseButton-secondary"]:hover { border-color: var(--voda); color: var(--text); }

/* levý panel jako řídicí panel */
section[data-testid="stSidebar"] { background: var(--studna); border-right: 1px solid var(--cara); }
section[data-testid="stSidebar"][data-collapsed="false"] { width: 312px !important; min-width: 312px !important; }
[data-testid="stSidebar"] [data-testid="stElementContainer"] { width: 100% !important; }
[data-testid="stSidebarHeader"] { padding: 12px 20px 0; height: 44px; }
[data-testid="stSidebarUserContent"] { padding: 0 20px 40px; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 10px; }
.panel-hlava { display: flex; align-items: center; gap: 12px; }
.panel-hlava b { display: block; font-size: 20px; font-weight: 700; letter-spacing: -0.02em; line-height: 1.1; color: var(--text); }
.panel-hlava small { display: block; margin-top: 3px; font-size: 13px; color: var(--text2); }
.sekce { display: flex; align-items: center; gap: 8px; padding: 0; }
[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.sekce) { margin-top: 14px; padding-top: 16px; border-top: 1px solid var(--cara); }
[data-testid="stSidebar"] [data-testid="stRadio"], [data-testid="stSidebar"] [data-testid="stRadioGroup"] { width: 100%; }
[data-testid="stSidebar"] [data-testid="stRadioGroup"] { gap: 6px; }
[data-testid="stSidebar"] [data-testid="stRadioGroup"] > div {
  position: relative; display: grid; grid-template-columns: 1fr; align-self: stretch; box-sizing: border-box; padding: 11px 14px 12px; border-radius: var(--r-maly);
  border: 1px solid var(--cara); background: var(--pozadi); transition: background-color 160ms var(--ven), border-color 160ms var(--ven), box-shadow 160ms var(--ven);
}
[data-testid="stSidebar"] [data-testid="stRadioGroup"] > div:hover { border-color: var(--cara-silna); }
[data-testid="stSidebar"] [data-testid="stRadioGroup"] > div[data-selected="true"] { background: var(--studna); border-color: var(--voda); box-shadow: 0 0 0 1px var(--voda); }
[data-testid="stSidebar"] [data-testid="stRadioOption"] { margin: 0; cursor: pointer; }
[data-testid="stSidebar"] [data-testid="stRadioOption"]::after { content: ""; position: absolute; inset: 0; }
[data-testid="stSidebar"] [data-testid="stRadioOption"] p { font-size: 17px; font-weight: 600; letter-spacing: -0.01em; line-height: 1.2; color: var(--text); }
[data-testid="stSidebar"] [data-testid="stRadioCaption"] { margin: 2px 0 0; padding: 0; }
[data-testid="stSidebar"] [data-testid="stRadioCaption"] p { font-size: 13px; color: var(--text2); font-variant-numeric: tabular-nums; }
[data-testid="stSidebar"] [data-testid="stCheckbox"] {
  padding: 12px 14px; border-radius: var(--r-maly); border: 1px solid var(--cara); background: var(--pozadi); width: 100%;
  transition: background-color 160ms var(--ven), border-color 160ms var(--ven);
}
[data-testid="stSidebar"] [data-testid="stCheckbox"]:has(input:checked) { border-color: var(--voda); background: var(--studna); box-shadow: 0 0 0 1px var(--voda); }
[data-testid="stSidebar"] [data-testid="stCheckbox"] label { align-items: center; gap: 4px; }
[data-testid="stSidebar"] [data-testid="stCheckbox"] label > div:not([data-testid]) { transform: scale(1.3); transform-origin: left center; margin-right: 10px; }
[data-testid="stSidebar"] [data-testid="stCheckbox"] [data-testid="stWidgetLabel"] p { font-size: 15px; font-weight: 600; letter-spacing: 0; text-transform: none; color: var(--text); }
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { font-size: 13px; }
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { font-size: 13px; }
[data-testid="stSidebar"] [data-testid="stSlider"] { padding: 0 6px; }
[data-testid="stSliderThumbValue"] p { font-size: 13px; font-weight: 600; font-variant-numeric: tabular-nums; }
[data-testid="stSliderTickBar"] p { font-size: 12px; color: var(--text2); font-variant-numeric: tabular-nums; }
[data-testid="stSelectbox"] input, [data-testid="stDateInputField"] { font-size: 15px; font-weight: 500; }

@media (max-width: 900px) {
  [data-testid="stMarkdownContainer"] .tiraz { grid-template-columns: auto minmax(0, 1fr); }
  .tiraz dl { grid-column: 1 / -1; margin-top: 16px; flex-wrap: wrap; }
}
@media (max-width: 640px) {
  [data-testid="stMainBlockContainer"] { padding: 56px 16px 64px; }
  [data-testid="stMarkdownContainer"] .tiraz h1 { font-size: 28px; }
  .tiraz .tiraz-znak { align-self: start; padding-top: 4px; }
  .tiraz .tiraz-znak svg { width: 34px; height: 34px; }
  .tiraz dl { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }
  .tiraz dl > div { padding: 8px 12px 9px; min-width: 0; }
  .tiraz dd { font-size: 15px; white-space: normal; }
  .tiraz dl > div:nth-child(3) { grid-column: 1 / -1; }
  [data-testid="stTabs"] [role="tablist"] { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); width: 100%; border-radius: 20px; }
  [data-testid="stTab"] { padding: 0 10px; justify-content: center; }
  [data-testid="stTab"] p { font-size: 14px; white-space: normal; text-align: center; }
  [data-testid="stMain"] [data-testid="stHeading"] h3 { font-size: 22px; }
  [class*="st-key-karta"] { padding: 16px 16px 18px; border-radius: 18px; }
  [data-testid="stMetricValue"] { font-size: 44px; }
  .st-key-cteni_ted [data-testid="stMetricValue"] { font-size: 56px; }
  [class*="st-key-cteni_"] { row-gap: 10px; }
  [class*="st-key-cteni_"] > [data-testid="stElementContainer"]:nth-child(1) { grid-column: 1 / -1; grid-row: 1; }
  [class*="st-key-cteni_"] > [data-testid="stElementContainer"]:nth-child(2) { grid-column: 1; grid-row: 2; justify-self: start; align-self: center; }
  [class*="st-key-cteni_"] > [data-testid="stElementContainer"]:nth-child(3) { grid-column: 2; grid-row: 2; justify-self: end; align-self: center; }
  [class*="st-key-cteni_"] [data-testid="stCaptionContainer"] p { white-space: normal; }
  .stitek { flex-direction: column; align-items: flex-start; gap: 2px; }
  .st-key-karta_citat [data-testid="stAlertContainer"] p { font-size: 18px; }
  .st-key-mapa_rezim [data-testid="stRadioGroup"][aria-orientation="horizontal"] { grid-template-columns: 1fr; }
  [data-testid="stMain"] [data-testid="stRadioOption"] { padding: 0 12px; min-height: 36px; }
  [data-testid="stMain"] [data-testid="stRadioOption"] p { font-size: 14px; }
  .st-key-mapa_rezim [data-testid="stRadioOption"] { padding: 0; }
  .st-key-mapa_rezim [data-testid="stRadioOption"] p { font-size: 16px; }
  .udaje > div { padding: 2px 12px 2px; }
  .udaje dd { font-size: 30px; }
  iframe, [data-testid="stIFrame"], [data-testid="stDeckGlJsonChart"] { border-radius: 18px; }
  [data-testid="stPlotlyChart"] .modebar-container { display: none; }
}
@media (prefers-reduced-motion: reduce) {
  .tiraz .tecka.zive { animation: none; }
  * { transition-duration: 0s !important; }
}
"""


def pouzij():
    """Vloží písma a styly; volá se hned po st.set_page_config."""
    barvy = {"pozadi": POZADI, "studna": STUDNA, "ovladac": OVLADAC, "text": TEXT, "text2": TEXT2,
             "tlumene": TLUMENE, "cara": CARA, "cara-silna": CARA_SILNA, "voda": VODA, "voda-svetla": VODA_SVETLA}
    koren = ":root { " + " ".join(f"--{k}: {v};" for k, v in barvy.items()) + " }"
    st.markdown(f'<style id="styl-pultu">{PISMA}{koren}{CSS}</style>', unsafe_allow_html=True)
