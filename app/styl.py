"""Vzhled aplikace: povodňový pult s vodočtem. Barvy, písma, šablona grafů, vodočet v SVG a styly prvků Streamlitu.

Prvky Streamlitu se stylují přes data-testid a klíče kontejnerů (třída st-key-<klíč>). Karta je každý kontejner
s klíčem začínajícím na karta_.
"""
import math

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

POZADI = "#111820"
STUDNA = "#0b1016"  # karty a levý panel
OVLADAC = "#1a232d"  # ovládací prvky, vybraná volba
TEXT = "#e6ebf0"
TEXT2 = "#c8d1d9"
TLUMENE = "#8b98a5"
JAKO_TED = "#666666"
VODA = "#3aa0c9"
VODA_SVETLA = "#7cc6e4"
SPA = ["#f2c437", "#ef6c00", "#c62828"]
NA_SPA = [STUDNA, STUDNA, TEXT]  # písmo na výplni stupně, kontrast aspoň 4,5 : 1
PISMO = "Schibsted Grotesk"
DISPLAY = "Sofia Sans Extra Condensed"

GRAF = {"displaylogo": False, "modeBarButtons": [["toImage"]],
        "toImageButtonOptions": {"format": "png", "scale": 2, "filename": "labe_graf"}}


def _sablona():
    osa = dict(gridcolor="rgba(230, 235, 240, 0.055)", linecolor="rgba(230, 235, 240, 0.16)", showline=True,
               zeroline=False, ticks="outside", ticklen=4, tickcolor="rgba(230, 235, 240, 0.16)",
               tickfont=dict(color=TLUMENE, size=12), title=dict(font=dict(color=TLUMENE, size=12), standoff=10))
    return go.layout.Template(layout=dict(
        paper_bgcolor=STUDNA, plot_bgcolor=STUDNA, colorway=[VODA, TEXT, JAKO_TED, VODA_SVETLA],
        font=dict(family=f"{PISMO}, sans-serif", size=13, color=TEXT2), xaxis=osa, yaxis=osa,
        hovermode="x unified", margin=dict(l=8, r=8, t=44, b=8),
        hoverlabel=dict(bgcolor=OVLADAC, bordercolor="rgba(230, 235, 240, 0.2)",
                        font=dict(family=f"{PISMO}, sans-serif", color=TEXT, size=13)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, xanchor="left", bgcolor="rgba(0,0,0,0)",
                    font=dict(color=TEXT2, size=13)),
        modebar=dict(bgcolor="rgba(0,0,0,0)", color=TLUMENE, activecolor=TEXT)))


pio.templates["pult"] = _sablona()


def cary_spa(fig, prahy, ymax=None):
    """Vodorovné čáry stupňů povodňové aktivity se štítkem; při nízké vodě jen ty v dosahu dat."""
    for n, (prah, barva, pismo) in enumerate(zip(prahy, SPA, NA_SPA), 1):
        if ymax is not None and prah > ymax * 1.6 + 60:
            continue
        fig.add_hline(y=prah, line=dict(color=barva, width=1.2, dash="dot"), layer="below",
                      annotation=dict(text=f"{n}. stupeň · {prah} cm", bgcolor=barva, borderpad=3,
                                      font=dict(family=f"{DISPLAY}, sans-serif", size=14, color=pismo)),
                      annotation_position="top left")


def graf(fig, vyska):
    """Vzhled pultu; barvy a písma i přímo v layoutu, protože Streamlit jinak vnutí svoje téma."""
    sablona = pio.templates["pult"].layout
    fig.update_layout(template="pult", height=vyska, paper_bgcolor=STUDNA, plot_bgcolor=STUDNA, font=sablona.font,
                      hoverlabel=sablona.hoverlabel, legend=sablona.legend, modebar=sablona.modebar,
                      margin=dict(l=56, r=12, t=44, b=48), hovermode="x unified")
    fig.update_xaxes(sablona.xaxis.to_plotly_json(), tickformat="%-d. %-m.\n%H:%M", automargin=True)
    fig.update_yaxes(sablona.yaxis.to_plotly_json(), automargin=True)


def stitek(text, vpravo=""):
    """Nadpis karty: malý kondenzovaný štítek, případně s údajem vpravo."""
    return f'<div class="stitek"><b>{text}</b>{f"<i>{vpravo}</i>" if vpravo else ""}</div>'


def sekce(text):
    st.markdown(f'<div class="sekce">{text}</div>', unsafe_allow_html=True)


def _znak(velikost=44):
    """Malá měrná lať s vodou, znak aplikace."""
    carky = "".join(f'<line x1="14" x2="{22 if i % 5 else 30}" y1="{6 + i * 3}" y2="{6 + i * 3}"/>' for i in range(11))
    return (f'<svg viewBox="0 0 44 44" width="{velikost}" height="{velikost}" aria-hidden="true">'
            f'<rect x="12" y="3" width="20" height="38" rx="2" fill="{OVLADAC}"/>'
            f'<g stroke="{TEXT2}" stroke-width="1.2" stroke-opacity=".7">{carky}</g>'
            f'<rect x="12" y="25" width="20" height="16" fill="{VODA}" fill-opacity=".55"/>'
            f'<path d="M4 25.5h36" stroke="{VODA_SVETLA}" stroke-width="2"/></svg>')


def hlavicka(okamzik, model, zdroj, zive):
    """Tiráž: otázka, na kterou aplikace odpovídá, a stav (okamžik, model, zdroj dat)."""
    tecka = f'<i class="tecka{" zive" if zive else ""}"></i>'
    return ('<header class="tiraz">'
            f'<div class="tiraz-znak">{_znak()}</div>'
            '<div class="tiraz-nazev"><h1>Kolik vody přiteče do Děčína a Ústí</h1>'
            '<p>Předpověď hladiny Labe na 12, 24 a 36 hodin pro povodňovou komisi města a lidi u řeky.</p></div>'
            '<dl class="tiraz-stav">'
            f'<div><dt>Okamžik</dt><dd>{okamzik}</dd></div>'
            f'<div><dt>Model</dt><dd>{model}</dd></div>'
            f'<div><dt>Data</dt><dd>{tecka}{zdroj}</dd></div>'
            '</dl></header>')


def panel_hlava():
    return (f'<div class="panel-hlava">{_znak(36)}<div><b>Povodňový pult</b>'
            '<small>Labe, Děčín a Ústí nad Labem</small></div></div>')


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

    L0, L1, STITKY, POPIS = 50, 124, 394, 214  # lať, štítky stupňů vpravo, začátek popisků předpovědi
    pruhy = {12: L1 + 12, 24: L1 + 28, 36: L1 + 44}  # pruhy rozmezí vedle latě, šířka 10
    s = []
    hranice = list(prahy) + [nahore]
    for i in range(3):  # zóny stupňů vpravo od latě a barevný pruh na její hraně
        a, b = max(hranice[i], dole), min(hranice[i + 1], nahore)
        if a < b:
            s.append(f'<rect x="{L1}" y="{y(b)}" width="{W - L1}" height="{round(y(a) - y(b), 1)}" fill="{SPA[i]}" '
                     f'fill-opacity="{(0.035, 0.045, 0.06)[i]}"/>')
            s.append(f'<rect x="{L1}" y="{y(b)}" width="5" height="{round(y(a) - y(b), 1)}" fill="{SPA[i]}"/>')
    s.append(f'<rect x="{L0}" y="{T}" width="{L1 - L0}" height="{dno - T}" fill="{OVLADAC}"/>')
    for cm in range(dole, nahore, 10):  # střídavé bloky po 10 cm jako na skutečné lati
        if cm // 10 % 2 == 0:
            x = L0 + 8 if cm // 100 % 2 == 0 else L1 - 30
            s.append(f'<rect x="{x}" y="{y(cm + 10)}" width="22" height="{round(y(cm) - y(cm + 10), 1)}" '
                     f'fill="{TEXT2}" fill-opacity=".13"/>')
    for cm in range(dole, nahore + 1, 10):
        x2, op = (L1, 0.75) if cm % 100 == 0 else (L0 + 30, 0.5) if cm % 50 == 0 else (L0 + 8, 0.3)
        s.append(f'<line x1="{L0}" x2="{x2}" y1="{y(cm)}" y2="{y(cm)}" stroke="{TEXT2}" stroke-opacity="{op}"/>')
        if cm % 100 == 0:
            s.append(f'<text x="{L0 - 8}" y="{y(cm) + 5}" text-anchor="end" class="lat-cislo">{cm}</text>')
    s.append(f'<rect x="{L0}" y="{y(ted)}" width="{L1 + 5 - L0}" height="{round(dno - y(ted), 1)}" fill="{VODA}" '
             f'fill-opacity=".5"/>')
    s.append(f'<line x1="{L0}" x2="{W}" y1="{dno}" y2="{dno}" stroke="{TEXT2}" stroke-opacity=".25"/>')

    for n, (prah, barva, pismo) in enumerate(zip(prahy, SPA, NA_SPA), 1):
        yp = y(prah)
        s.append(f'<line x1="{L0}" x2="{STITKY}" y1="{yp}" y2="{yp}" stroke="{barva}" stroke-width="1.2" '
                 f'stroke-opacity=".9"/>')
        s.append(f'<rect x="{STITKY}" y="{yp - 11}" width="{W - STITKY}" height="22" rx="4" fill="{barva}"/>')
        s.append(f'<text x="{(STITKY + W) / 2}" y="{yp + 5}" text-anchor="middle" class="lat-stupen" '
                 f'fill="{pismo}">{n}. stupeň {prah}</text>')

    s.append(f'<line x1="0" x2="{STITKY}" y1="{y(ted)}" y2="{y(ted)}" stroke="{VODA_SVETLA}" stroke-width="2"/>')
    s.append(f'<rect x="0" y="{y(ted) - 12}" width="{L0 - 5}" height="24" rx="4" fill="{VODA_SVETLA}"/>')
    s.append(f'<text x="{(L0 - 5) / 2}" y="{y(ted) + 6}" text-anchor="middle" class="lat-ted">{ted:.0f}</text>')

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
            s.append(f'<rect x="{x}" y="{y(hi)}" width="10" height="{round(y(lo) - y(hi), 1)}" rx="2" '
                     f'fill="{VODA_SVETLA}" fill-opacity=".32"/>')
        s.append(f'<rect x="{x - 3}" y="{yp - 2}" width="16" height="4" rx="1" fill="{VODA_SVETLA}"/>')
        if h in chmu:
            s.append(f'<path d="M{x + 12} {y(chmu[h])}l8 -5v10z" fill="{TEXT}"/>')
        s.append(f'<path d="M{x + 13} {yp}H{L1 + 66}L{POPIS - 8} {ly}H{POPIS - 2}" fill="none" '
                 f'stroke="{VODA_SVETLA}" stroke-opacity=".6"/>')
        s.append(f'<rect x="{POPIS - 2}" y="{ly - 15}" width="{176 if h in chmu else 124}" height="30" '
                 f'fill="{STUDNA}" fill-opacity=".85" rx="3"/>')
        dalsi = f'<tspan class="lat-chmu"> · ČHMÚ {chmu[h]:.0f}</tspan>' if h in chmu else ""
        s.append(f'<text x="{POPIS + 46}" y="{ly + 9}" text-anchor="end" class="lat-hodnota">{p:.0f}</text>'
                 f'<text x="{POPIS + 52}" y="{ly + 7}" class="lat-osa">cm za {h} h{dalsi}</text>')
    s.append(f'<rect x="{L0}" y="{dno + 16}" width="14" height="10" rx="2" fill="{VODA_SVETLA}" fill-opacity=".32"/>'
             f'<text x="{L0 + 20}" y="{dno + 25}" class="lat-legenda">rozmezí nejistoty (90 % chyb)</text>'
             f'<rect x="{L0 + 196}" y="{dno + 16}" width="14" height="10" fill="{VODA}" fill-opacity=".5"/>'
             f'<text x="{L0 + 216}" y="{dno + 25}" class="lat-legenda">voda teď</text>')
    if chmu:
        s.append(f'<path d="M{L0 + 290} {dno + 21}l8 -5v10z" fill="{TEXT}"/>'
                 f'<text x="{L0 + 304}" y="{dno + 25}" class="lat-legenda">ČHMÚ</text>')
    popis = (f"Vodočet: teď {ted:.0f} cm, " + ", ".join(f"za {h} h {pred[h]:.0f} cm" for h in pruhy)
             + f"; stupně povodňové aktivity {prahy[0]}, {prahy[1]} a {prahy[2]} cm.")
    return (f'<div class="lat"><svg viewBox="0 0 {W} {H}" role="img" aria-label="{popis}" '
            f'preserveAspectRatio="xMidYMid meet">{"".join(s)}</svg></div>')


CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Schibsted+Grotesk:wght@400..800&family=Sofia+Sans+Extra+Condensed:wght@500..800&display=swap');
:root {
  --cara: rgba(230, 235, 240, 0.09); --cara-silna: rgba(230, 235, 240, 0.2);
  --pismo: 'Schibsted Grotesk', sans-serif; --display: 'Sofia Sans Extra Condensed', 'Schibsted Grotesk', sans-serif;
  --r: 14px; --r-maly: 9px; --ven: cubic-bezier(0.16, 1, 0.3, 1);
}
html, body, .stApp { background: var(--pozadi); color: var(--text); font-family: var(--pismo); }
::selection { background: rgba(58, 160, 201, 0.45); color: var(--text); }
* { scrollbar-width: thin; scrollbar-color: rgba(230, 235, 240, 0.18) transparent; }
:focus-visible { outline: 2px solid var(--voda-svetla); outline-offset: 2px; }
input, textarea { caret-color: var(--voda-svetla); }
div[data-testid="stElementContainer"]:has(style#styl-pultu) { display: none; }

/* chrome Streamlitu: zůstává jen tlačítko levého panelu */
header[data-testid="stHeader"], header[data-testid="stHeader"] * { background: transparent; pointer-events: none; }
header[data-testid="stHeader"] button, header[data-testid="stHeader"] button * { pointer-events: auto; }
header[data-testid="stHeader"] button { background: var(--studna); box-shadow: inset 0 0 0 1px var(--cara-silna); border-radius: 9px; color: var(--text2); }
[data-testid="stToolbarActions"], [data-testid="stAppDeployButton"], [data-testid="stMainMenu"],
[data-testid="stDecoration"], [data-testid="stHeaderActionElements"], footer { display: none !important; }
[data-testid="stMainBlockContainer"] { max-width: 1280px; padding: 2rem 2.5rem 5rem; }
[data-testid="stMain"] [data-testid="stVerticalBlock"] { gap: 1.1rem; }

/* tiráž */
[data-testid="stMarkdownContainer"] .tiraz {
  display: grid; grid-template-columns: auto minmax(0, 1fr) auto; align-items: end; gap: 0 1.25rem;
  padding: 0.25rem 0 1.4rem; border-bottom: 1px solid var(--cara);
}
.tiraz .tiraz-znak { align-self: center; line-height: 0; }
[data-testid="stMarkdownContainer"] .tiraz h1 {
  font-family: var(--display); font-size: 3.1rem; font-weight: 800; line-height: 0.92; letter-spacing: -0.01em;
  margin: 0; padding: 0; color: var(--text); text-wrap: balance;
}
[data-testid="stMarkdownContainer"] .tiraz p { margin: 0.5rem 0 0; color: var(--text2); font-size: 0.98rem; line-height: 1.45; max-width: 62ch; text-wrap: pretty; }
.tiraz dl { display: flex; margin: 0; }
.tiraz dl > div { padding: 0 0 0 1.1rem; margin-left: 1.1rem; border-left: 1px solid var(--cara); }
.tiraz dt { font-family: var(--display); font-size: 0.9rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: var(--tlumene); }
.tiraz dd { margin: 0.1rem 0 0; font-family: var(--display); font-size: 1.55rem; font-weight: 700; line-height: 1.1;
  white-space: nowrap; color: var(--text); display: flex; align-items: center; gap: 0.5rem; font-variant-numeric: tabular-nums; }
.tiraz .tecka { width: 9px; height: 9px; border-radius: 50%; box-shadow: inset 0 0 0 1.5px var(--tlumene); flex: none; }
.tiraz .tecka.zive { box-shadow: none; background: var(--voda-svetla); animation: puls 2.4s var(--ven) infinite; }
@keyframes puls { 0% { box-shadow: 0 0 0 0 rgba(124, 198, 228, 0.55); } 70%, 100% { box-shadow: 0 0 0 10px rgba(124, 198, 228, 0); } }

/* záložky: lišta s podtržením barvou vody */
[data-testid="stTabs"] [role="tablist"] {
  gap: 2.4rem; padding: 0; margin: 0 0 1.6rem; border-bottom: 1px solid var(--cara); background: none; box-shadow: none; overflow: visible;
}
[data-testid="stTabs"] [role="tablist"]::before, [data-testid="stTabs"] [role="tablist"]::after { display: none; }
[data-testid="stTab"] > div:not([data-testid]) { display: none; }
[data-testid="stTab"] {
  position: relative; height: auto; margin: 0; padding: 0.5rem 0 0.75rem; background: none; border: 0;
  color: var(--tlumene); cursor: pointer; transition: color 160ms var(--ven);
}
[data-testid="stTab"]::after {
  content: ""; position: absolute; left: 0; right: 0; bottom: -1px; height: 3px; border-radius: 2px 2px 0 0;
  background: var(--voda); transform: scaleX(0); transform-origin: left; transition: transform 260ms var(--ven);
}
[data-testid="stTab"] p { font-family: var(--display); font-size: 1.6rem; font-weight: 700; letter-spacing: 0.005em; margin: 0; color: inherit; line-height: 1; }
[data-testid="stTab"]:hover { color: var(--text2); }
[data-testid="stTab"][aria-selected="true"] { color: var(--text); }
[data-testid="stTab"][aria-selected="true"]::after { transform: scaleX(1); }
[data-testid="stTab"][data-focus-visible] { outline: 2px solid var(--voda-svetla); outline-offset: 4px; border-radius: 4px; }

/* texty */
[data-testid="stMain"] [data-testid="stHeading"] h3 {
  font-family: var(--display); font-size: 2.5rem; font-weight: 750; letter-spacing: -0.005em; line-height: 1; padding: 0.15rem 0 0; color: var(--text);
}
[data-testid="stMain"] [data-testid="stMarkdown"] p { color: var(--text2); line-height: 1.55; max-width: 75ch; }
[data-testid="stMain"] [data-testid="stMarkdown"] p strong { color: var(--text); font-weight: 650; }
[data-testid="stCaptionContainer"] { color: var(--tlumene); }
[data-testid="stCaptionContainer"] p, [data-testid="stMain"] [data-testid="stMarkdown"] [data-testid="stCaptionContainer"] p { font-size: 0.85rem; line-height: 1.5; max-width: 110ch; color: var(--tlumene); }
[data-testid="stWidgetLabel"] p, .stitek b, .sekce {
  font-family: var(--display); font-size: 1rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: var(--tlumene);
}
.stitek { display: flex; justify-content: space-between; align-items: baseline; gap: 1rem; }
.stitek i { font-style: normal; font-family: var(--display); font-size: 1rem; font-weight: 600; color: var(--text2); font-variant-numeric: tabular-nums; }

/* karty: jedna studna, jeden rádius, jedna vlasová hrana */
[class*="st-key-karta"] {
  background: var(--studna); border: 1px solid var(--cara); border-radius: var(--r); padding: 1.2rem 1.35rem 1.3rem;
}
[class*="st-key-karta"] [data-testid="stVerticalBlock"] { gap: 0.85rem; }

/* vodočet */
.lat svg { display: block; width: 100%; height: auto; max-height: 640px; overflow: visible; }
.lat text { font-family: var(--display); }
.lat .lat-cislo { font-size: 15px; font-weight: 600; fill: var(--tlumene); font-variant-numeric: tabular-nums; }
.lat .lat-stupen { font-size: 14px; font-weight: 750; letter-spacing: 0.02em; }
.lat .lat-hodnota { font-size: 30px; font-weight: 800; fill: var(--text); font-variant-numeric: tabular-nums; }
.lat .lat-ted { font-size: 17px; font-weight: 800; fill: var(--studna); font-variant-numeric: tabular-nums; }
.lat .lat-osa { font-size: 16px; font-weight: 700; fill: var(--text2); letter-spacing: 0.02em; }
.lat .lat-legenda { font-family: var(--pismo); font-size: 12px; fill: var(--tlumene); }
.lat .lat-chmu { font-size: 14px; font-weight: 600; fill: var(--tlumene); }

/* odečty u vodočtu */
[class*="st-key-cteni_"] { display: grid; grid-template-columns: minmax(0, 1fr) auto; column-gap: 1rem; row-gap: 0.4rem;
  align-content: start; padding: 0.95rem 0 1rem; border-top: 1px solid var(--cara); }
.st-key-cteni_ted { border-top: 0; padding-top: 0.2rem; }
[class*="st-key-cteni_"] > [data-testid="stElementContainer"]:nth-child(1) { grid-column: 1; grid-row: 1 / span 2; }
[class*="st-key-cteni_"] > [data-testid="stElementContainer"]:nth-child(2) { grid-column: 2; grid-row: 1; justify-self: end; align-self: start; width: auto; }
[class*="st-key-cteni_"] > [data-testid="stElementContainer"]:nth-child(3) { grid-column: 2; grid-row: 2; justify-self: end; align-self: end; width: auto; text-align: right; }
[class*="st-key-cteni_"] [data-testid="stMetricLabel"] p { font-family: var(--display); font-size: 1.3rem; font-weight: 700; letter-spacing: 0.01em; color: var(--text2); display: flex; align-items: center; gap: 0.5rem; }
[class*="st-key-cteni_"] [data-testid="stMetricLabel"] p::before { content: ""; width: 0.7rem; height: 0.7rem; border-radius: 2px; background: var(--voda-svetla); opacity: 0.55; }
.st-key-cteni_ted [data-testid="stMetricLabel"] p::before { background: var(--voda); opacity: 1; }
[data-testid="stMetricValue"] { font-family: var(--display); font-size: 3.6rem; font-weight: 800; line-height: 0.95; letter-spacing: -0.01em; color: var(--text); font-variant-numeric: tabular-nums; }
.st-key-cteni_ted [data-testid="stMetricValue"] { font-size: 4.6rem; }
[data-testid="stMetricValue"] p { color: inherit; font: inherit; }
[data-testid="stMetricDelta"] { color: var(--text2) !important; background: none !important; padding: 0; font-family: var(--display); font-size: 1.15rem; font-weight: 700; font-variant-numeric: tabular-nums; }
[data-testid="stMetricDelta"] svg, [data-testid^="stMetricDeltaIcon"] { display: none; }
[class*="st-key-cteni_"] [data-testid="stCaptionContainer"] p { font-size: 0.88rem; color: var(--text2); font-variant-numeric: tabular-nums; white-space: nowrap; }
.odznak { display: inline-block; padding: 0.2rem 0.6rem 0.22rem; border-radius: 6px; font-family: var(--display); font-size: 1.05rem;
  font-weight: 750; letter-spacing: 0.02em; line-height: 1.15; white-space: nowrap; }
.odznak.spa-0 { color: var(--text2); box-shadow: inset 0 0 0 1px var(--cara-silna); }
.odznak.spa-1 { background: #f2c437; color: var(--studna); }
.odznak.spa-2 { background: #ef6c00; color: var(--studna); }
.odznak.spa-3 { background: #c62828; color: var(--text); }

/* věta pro laika */
.st-key-karta_citat [data-testid="stAlertContainer"] { background: none; border: 0; padding: 0; }
.st-key-karta_citat [data-testid="stAlertContainer"] p { font-size: 1.3rem; line-height: 1.5; color: var(--text); font-weight: 450; max-width: 70ch; }

/* hlášky */
[data-testid="stAlertContainer"] { border-radius: var(--r-maly); background: var(--ovladac); border: 1px solid var(--cara); color: var(--text2); }
[data-testid="stAlertContentWarning"] { color: var(--text); }
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentWarning"]) { border-color: rgba(239, 108, 0, 0.55); background: rgba(239, 108, 0, 0.1); }

/* souhrnné údaje (Dnešek, kvalita) */
.udaje { display: grid; grid-template-columns: repeat(auto-fit, minmax(9.5rem, 1fr)); gap: 0.9rem 0; margin: 0; }
.udaje > div { padding: 0.15rem 1.1rem 0.1rem; border-left: 1px solid var(--cara); }
.udaje > div:first-child { padding-left: 0; border-left: 0; }
.udaje dt { font-family: var(--display); font-size: 0.95rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: var(--tlumene); }
.udaje dd { margin: 0.2rem 0 0; font-family: var(--display); font-size: 2.6rem; font-weight: 800; line-height: 1; color: var(--text); font-variant-numeric: tabular-nums; }
.udaje dd small { font-size: 1.2rem; font-weight: 700; color: var(--text2); margin-left: 0.2rem; }
.udaje p { margin: 0.4rem 0 0; font-size: 0.85rem; line-height: 1.4; color: var(--tlumene); }
.udaje p b { color: var(--text2); font-weight: 600; }

/* grafy, tabulky, mapy */
[data-testid="stPlotlyChart"] { background: var(--studna); border-radius: var(--r); }
iframe, [data-testid="stIFrame"], [data-testid="stDeckGlJsonChart"] { border-radius: var(--r); }
[data-testid="stIFrame"] { border: 1px solid var(--cara); background: var(--studna); }
[data-testid="stTable"] { overflow-x: auto; }
[data-testid="stTable"] table { width: 100%; border-collapse: collapse; border: 0; font-variant-numeric: tabular-nums; color: var(--text); }
[data-testid="stTable"] td, [data-testid="stTable"] tbody th { font-family: var(--display) !important; font-size: 1.2rem !important; font-weight: 650; letter-spacing: 0.01em; }
[data-testid="stTable"] th, [data-testid="stTable"] td { border: 0; border-bottom: 1px solid var(--cara); padding: 0.6rem 0.8rem; background: none; }
[data-testid="stTable"] thead th { font-family: var(--display); font-size: 0.95rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase;
  color: var(--tlumene); text-align: right; vertical-align: bottom; line-height: 1.15; border-bottom-color: var(--cara-silna); }
[data-testid="stTable"] tbody th { font-weight: 600; text-align: left; color: var(--text2); }
[data-testid="stTable"] td { text-align: right; font-size: 1rem; }

/* volby v hlavní části: segmenty */
[data-testid="stMain"] [data-testid="stRadioGroup"][aria-orientation="horizontal"] {
  display: inline-flex; flex-wrap: wrap; gap: 4px; padding: 4px; width: fit-content; max-width: 100%;
  background: var(--pozadi); border: 1px solid var(--cara); border-radius: 11px;
}
[data-testid="stRadioGroup"] > div { margin: 0; }
[data-testid="stRadioOption"] > div > div:first-child:not([data-testid]) { display: none; }
[data-testid="stMain"] [data-testid="stRadioOption"] {
  margin: 0; padding: 0.4rem 0.95rem 0.45rem; border-radius: 8px; cursor: pointer; color: var(--tlumene);
  transition: background-color 160ms var(--ven), color 160ms var(--ven), box-shadow 160ms var(--ven);
}
[data-testid="stMain"] [data-testid="stRadioOption"] p { font-family: var(--display); font-size: 1.3rem; font-weight: 700; line-height: 1.1; color: inherit; font-variant-numeric: tabular-nums; white-space: nowrap; }
[data-testid="stMain"] [data-testid="stRadioOption"]:hover { color: var(--text2); background: rgba(230, 235, 240, 0.04); }
[data-testid="stMain"] [data-testid="stRadioOption"][data-selected="true"] { color: var(--text); background: var(--ovladac); box-shadow: inset 0 0 0 1px var(--voda); }
[data-testid="stRadioOption"]:has(input:focus-visible) { outline: 2px solid var(--voda-svetla); outline-offset: 2px; }

/* režim mapy: dvě velké dlaždice */
.st-key-mapa_rezim [data-testid="stRadioGroup"][aria-orientation="horizontal"] {
  display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); align-items: stretch; width: 100%; gap: 0.6rem; padding: 0; background: none; border: 0;
}
.st-key-mapa_rezim [data-testid="stRadio"] { width: 100%; }
.st-key-mapa_rezim [data-testid="stRadioGroup"] > div {
  position: relative; padding: 0.85rem 1rem 0.9rem; border-radius: 11px; background: var(--pozadi); border: 1px solid var(--cara);
  transition: border-color 160ms var(--ven), background-color 160ms var(--ven);
}
.st-key-mapa_rezim [data-testid="stRadioGroup"] > div:hover { border-color: var(--cara-silna); }
.st-key-mapa_rezim [data-testid="stRadioGroup"] > div[data-selected="true"] { background: var(--ovladac); border-color: var(--voda); }
.st-key-mapa_rezim [data-testid="stRadioOption"] { padding: 0; background: none !important; box-shadow: none !important; }
.st-key-mapa_rezim [data-testid="stRadioOption"]::after { content: ""; position: absolute; inset: 0; }
.st-key-mapa_rezim [data-testid="stRadioOption"] p { font-size: 1.55rem; white-space: normal; }
.st-key-mapa_rezim [data-testid="stRadioCaption"] { margin: 0.25rem 0 0; padding: 0; }
.st-key-mapa_rezim [data-testid="stRadioCaption"] p { font-size: 0.88rem; color: var(--tlumene); }
.st-key-mapa_rezim [data-testid="stRadioGroup"] > div[data-selected="true"] [data-testid="stRadioCaption"] p { color: var(--text2); }

/* tlačítka */
[data-testid="stBaseButton-primary"] {
  min-height: 3.1rem; padding: 0 1.5rem; border: 0; border-radius: 11px; background: var(--voda); color: var(--studna);
  transition: background-color 160ms var(--ven), transform 120ms var(--ven);
}
[data-testid="stBaseButton-primary"]::before { content: ""; width: 0.8rem; height: 0.95rem; margin-right: 0.65rem; background: currentColor; clip-path: polygon(0 0, 100% 50%, 0 100%); }
[data-testid="stBaseButton-primary"] p { font-family: var(--display); font-size: 1.45rem; font-weight: 800; letter-spacing: 0.01em; color: inherit; }
[data-testid="stBaseButton-primary"]:hover { background: var(--voda-svetla); color: var(--studna); }
[data-testid="stBaseButton-primary"]:active { transform: translateY(1px); }
[data-testid="stBaseButton-secondary"] { background: var(--ovladac); border: 1px solid var(--cara-silna); border-radius: 10px; color: var(--text); }
[data-testid="stBaseButton-secondary"]:hover { border-color: var(--voda-svetla); color: var(--text); }

/* levý panel jako řídicí panel */
section[data-testid="stSidebar"] { background: var(--studna); border-right: 1px solid var(--cara); }
section[data-testid="stSidebar"][data-collapsed="false"] { width: 300px !important; min-width: 300px !important; }
[data-testid="stSidebar"] [data-testid="stElementContainer"] { width: 100% !important; }
[data-testid="stSidebarHeader"] { padding: 0.75rem 1.25rem 0; height: 2.75rem; }
[data-testid="stSidebarUserContent"] { padding: 0 1.25rem 2.5rem; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 0.65rem; }
.panel-hlava { display: flex; align-items: center; gap: 0.75rem; padding-bottom: 0.4rem; }
.panel-hlava b { display: block; font-family: var(--display); font-size: 1.65rem; font-weight: 800; line-height: 1; color: var(--text); }
.panel-hlava small { display: block; margin-top: 0.2rem; font-size: 0.8rem; color: var(--tlumene); }
.sekce { display: flex; align-items: center; gap: 0.6rem; margin-top: 0.85rem; padding-top: 1rem; border-top: 1px solid var(--cara); }
[data-testid="stSidebar"] [data-testid="stRadio"], [data-testid="stSidebar"] [data-testid="stRadioGroup"] { width: 100%; }
[data-testid="stSidebar"] [data-testid="stRadioGroup"] { gap: 6px; }
[data-testid="stSidebar"] [data-testid="stRadioGroup"] > div {
  position: relative; display: grid; grid-template-columns: 1fr; align-self: stretch; box-sizing: border-box; padding: 0.65rem 0.85rem 0.7rem; border-radius: 10px;
  border: 1px solid var(--cara); background: var(--pozadi); transition: background-color 160ms var(--ven), border-color 160ms var(--ven);
}
[data-testid="stSidebar"] [data-testid="stRadioGroup"] > div:hover { border-color: var(--cara-silna); }
[data-testid="stSidebar"] [data-testid="stRadioGroup"] > div[data-selected="true"] { background: var(--ovladac); border-color: var(--voda); }
[data-testid="stSidebar"] [data-testid="stRadioOption"] { margin: 0; cursor: pointer; }
[data-testid="stSidebar"] [data-testid="stRadioOption"]::after { content: ""; position: absolute; inset: 0; }
[data-testid="stSidebar"] [data-testid="stRadioOption"] p { font-family: var(--display); font-size: 1.5rem; font-weight: 750; line-height: 1.05; color: var(--text2); }
[data-testid="stSidebar"] [data-testid="stRadioGroup"] > div[data-selected="true"] [data-testid="stRadioOption"] p { color: var(--text); }
[data-testid="stSidebar"] [data-testid="stRadioCaption"] { margin: 0.15rem 0 0; padding: 0; }
[data-testid="stSidebar"] [data-testid="stRadioCaption"] p { font-size: 0.8rem; color: var(--tlumene); font-variant-numeric: tabular-nums; }
[data-testid="stSidebar"] [data-testid="stCheckbox"] {
  padding: 0.7rem 0.85rem; border-radius: 10px; border: 1px solid var(--cara); background: var(--pozadi); width: 100%;
}
[data-testid="stSidebar"] [data-testid="stCheckbox"]:has(input:checked) { border-color: var(--voda); background: var(--ovladac); }
[data-testid="stSidebar"] [data-testid="stCheckbox"] [data-testid="stWidgetLabel"] p { font-family: var(--pismo); font-size: 0.95rem; font-weight: 600; letter-spacing: 0; text-transform: none; color: var(--text); }
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { font-size: 0.8rem; }
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { font-size: 0.9rem; }
[data-testid="stSidebar"] [data-testid="stSlider"] { padding: 0 0.4rem; }
[data-testid="stSliderThumbValue"] { font-family: var(--display); font-size: 1.1rem; font-weight: 700; }
[data-baseweb="select"] > div, [data-testid="stDateInputField"] { border-radius: 9px; }

@media (max-width: 900px) {
  [data-testid="stMarkdownContainer"] .tiraz { grid-template-columns: auto minmax(0, 1fr); }
  .tiraz dl { grid-column: 1 / -1; margin-top: 1rem; flex-wrap: wrap; row-gap: 0.6rem; }
  .tiraz dl > div:first-child { margin-left: 0; padding-left: 0; border-left: 0; }
}
@media (max-width: 640px) {
  [data-testid="stMainBlockContainer"] { padding: 3.4rem 1rem 4rem; }
  [data-testid="stMarkdownContainer"] .tiraz h1 { font-size: 2.15rem; }
  .tiraz .tiraz-znak { align-self: start; padding-top: 0.2rem; }
  .tiraz .tiraz-znak svg { width: 34px; height: 34px; }
  .tiraz dd { font-size: 1.3rem; }
  .tiraz dl { display: grid; grid-template-columns: auto auto; justify-content: start; }
  .tiraz dl > div { margin-left: 0.8rem; padding-left: 0.8rem; }
  .tiraz dl > div:nth-child(3) { grid-column: 1 / -1; margin-left: 0; padding-left: 0; border-left: 0; }
  [data-testid="stTabs"] [role="tablist"] { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0 1rem; }
  [data-testid="stTabsScrollRight"], [data-testid="stTabsScrollLeft"] { display: none; }
  [data-testid="stTab"] { padding: 0.55rem 0 0.6rem; }
  [data-testid="stTab"] p { font-size: 1.3rem; }
  [data-testid="stMain"] [data-testid="stHeading"] h3 { font-size: 1.95rem; }
  [class*="st-key-karta"] { padding: 1rem 1rem 1.1rem; }
  [data-testid="stMetricValue"] { font-size: 3rem; }
  .st-key-cteni_ted [data-testid="stMetricValue"] { font-size: 3.6rem; }
  .st-key-karta_citat [data-testid="stAlertContainer"] p { font-size: 1.12rem; }
  .st-key-mapa_rezim [data-testid="stRadioGroup"][aria-orientation="horizontal"] { grid-template-columns: 1fr; }
  [data-testid="stMain"] [data-testid="stRadioOption"] { padding: 0.35rem 0.7rem 0.4rem; }
  [data-testid="stMain"] [data-testid="stRadioOption"] p { font-size: 1.15rem; }
  .st-key-mapa_rezim [data-testid="stRadioOption"] { padding: 0; }
  .st-key-mapa_rezim [data-testid="stRadioOption"] p { font-size: 1.4rem; }
  .udaje > div { padding: 0.15rem 0.7rem 0.1rem; }
  .udaje dd { font-size: 2.1rem; }
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
             "tlumene": TLUMENE, "voda": VODA, "voda-svetla": VODA_SVETLA}
    koren = ":root { " + " ".join(f"--{k}: {v};" for k, v in barvy.items()) + " }"
    st.markdown(f'<style id="styl-pultu">{koren}{CSS}</style>', unsafe_allow_html=True)
