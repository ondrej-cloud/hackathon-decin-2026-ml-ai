r"""Labe: kolik vody přiteče do Děčína a Ústí. Aplikace pro povodňovou komisi města a lidi u řeky.

Spuštění z kořene repozitáře:
    Windows:  .venv\Scripts\python -m streamlit run app\app.py
    Mac:      .venv/bin/python -m streamlit run app/app.py
"""
import json
from datetime import date, datetime, time

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from predikce import (BARVY, HORIZONTY, KDE, NAZEV, ROOT, SPA, STUPNE, modely, nacti, nacti_model, stupen, vstupy,
                      vysvetleni)

POVODNE = {"4/2006": ("2006-03-25", "2006-04-10"), "3/2009": ("2009-02-26", "2009-03-14"),
           "9/2010": ("2010-09-20", "2010-10-06"), "1/2011": ("2011-01-08", "2011-01-24")}
TZ = "Europe/Prague"
MODRA = "#1f77b4"

st.set_page_config(page_title="Labe: předpověď hladiny", layout="wide")


@st.cache_data
def hladiny(cil):
    return nacti()[f"{cil}_H"]


@st.cache_data
def vstupy_c(cil):
    return vstupy(cil)


@st.cache_resource
def model_c(nazev, cil, h):
    return nacti_model(nazev, cil, h)


@st.cache_data
def predpovedi_val(nazev):
    return pd.read_parquet(ROOT / "results/predpovedi" / f"{nazev}.parquet")


@st.cache_data
def metriky(nazev):
    """Poslední plný výsledek modelu na validaci z results/."""
    for f in sorted((ROOT / "results").glob(f"*_{nazev}.json"), reverse=True):
        z = json.loads(f.read_text(encoding="utf-8"))
        if z["cast"] == "val" and not z.get("rychle"):
            return pd.DataFrame(z["vysledky"])
    return pd.DataFrame()


def jmeno(cil):
    return NAZEV[cil].split(" (")[0]


def odznak(cil, hladina):
    s = stupen(cil, hladina)
    return (f'<span style="background:{BARVY[s]};color:{"black" if s == 1 else "white"};padding:3px 10px;'
            f'border-radius:6px;font-weight:600">{STUPNE[s]}</span>')


def cary_spa(fig, cil):
    for n, (prah, barva) in enumerate(zip(SPA[cil], BARVY[1:]), 1):
        fig.add_hline(y=prah, line=dict(color=barva, dash="dot"), annotation_text=f"{n}. stupeň",
                      annotation_position="top left", annotation_font_color=barva)


def cesky(t):
    return t.tz_convert(TZ)


st.title("Kolik vody přiteče do Děčína a Ústí")
st.caption("Předpověď hladiny Labe za 12, 24 a 36 hodin z toho, co teď teče po Vltavě, Labi a Ohři proti proudu. "
           "Pro povodňovou komisi města a lidi u řeky. Data ČHMÚ 2006–2025.")

with st.sidebar:
    st.header("Nastavení")
    seznam = modely()
    nazev = st.selectbox("Model", seznam, index=seznam.index("ridge"))
    cil = st.radio("Stanice", list(KDE), format_func=jmeno)
    st.subheader("Okamžik předpovědi")
    st.caption("Přehrávání historie: vyber den a hodinu a aplikace ukáže, co by model řekl tehdy.")
    den = st.date_input("Den", value=date(2011, 1, 15), min_value=date(2006, 1, 3), max_value=date(2025, 12, 30))
    hodina = st.slider("Hodina (český čas)", 0, 23, 9)

X = vstupy_c(cil)
H = hladiny(cil)
cas = pd.Timestamp(datetime.combine(den, time(hodina))).tz_localize(TZ, ambiguous=False, nonexistent="shift_forward")
cas = cas.tz_convert("UTC")
if cas not in X.index:
    cas = X.index[X.index.get_indexer([cas], method="nearest")[0]]
    st.sidebar.warning(f"Pro zvolenou hodinu chybí data, beru nejbližší: {cesky(cas):%d. %m. %Y %H:%M}.")
radek = X.loc[[cas]]
ted = float(radek[f"{cil}_H_0"].iloc[0])
pred = {h: float(model_c(nazev, cil, h).predict(radek)[0]) for h in HORIZONTY}

tab_ted, tab_kvalita = st.tabs(["Teď", "Jak dobře to funguje"])

with tab_ted:
    st.subheader(f"{jmeno(cil)}, {cesky(cas):%d. %m. %Y %H:%M} českého času")
    sloupce = st.columns(4)
    sloupce[0].metric("Hladina teď", f"{ted:.0f} cm")
    sloupce[0].markdown(odznak(cil, ted), unsafe_allow_html=True)
    for c, h in zip(sloupce[1:], HORIZONTY):
        c.metric(f"Za {h} h", f"{pred[h]:.0f} cm", delta=f"{pred[h] - ted:+.0f} cm", delta_color="inverse")
        c.markdown(odznak(cil, pred[h]), unsafe_allow_html=True)
    st.info(vysvetleni(cil, 24, ted, pred[24], radek))

    okno = H[cas - pd.Timedelta(hours=72): cas]
    fig = go.Figure()
    fig.add_scatter(x=cesky(okno.index), y=okno.values, mode="lines", name="hladina (změřeno)",
                    line=dict(color="black", width=2))
    fig.add_scatter(x=[cesky(cas + pd.Timedelta(hours=h)) for h in (0,) + HORIZONTY],
                    y=[ted] + [pred[h] for h in HORIZONTY], mode="markers+lines", name="předpověď",
                    line=dict(color=MODRA, dash="dash"), marker=dict(size=[6, 11, 11, 11]),
                    text=["teď"] + [f"za {h} h" for h in HORIZONTY])
    cary_spa(fig, cil)
    fig.update_layout(yaxis_title="hladina (cm)", height=420, margin=dict(l=10, r=10, t=30, b=50),
                      legend=dict(orientation="h"), hovermode="x unified")
    fig.update_xaxes(tickformat="%d. %m.\n%H:%M")
    st.plotly_chart(fig, width="stretch")
    st.caption("Černá čára je, co se změřilo do zvoleného okamžiku. Modré body jsou předpověď vydaná v tomhle "
               "okamžiku na 12, 24 a 36 hodin dopředu. Tečkované čáry jsou stupně povodňové aktivity.")

with tab_kvalita:
    st.markdown("Model jsme zkoušeli na čtyřech povodních, které při učení neviděl (učil se na letech 2006–2018 "
                "bez nich a bez 20 dní kolem nich). Srovnáváme s nejjednodušší předpovědí „bude jako teď“.")
    a, b = st.columns(2)
    povoden = a.selectbox("Povodeň", list(POVODNE), index=3)
    h = b.radio("Předpověď vydaná ... hodin předem", HORIZONTY, index=1, horizontal=True)
    od, do = POVODNE[povoden]
    try:
        P = predpovedi_val(nazev)
    except FileNotFoundError:
        P = None
        st.warning(f"Pro model {nazev} zatím nejsou uložené předpovědi na validaci (results/predpovedi/{nazev}.parquet).")
    J = predpovedi_val("jako_ted")
    J = J[(J.cil == cil) & (J.horizont == h)][od:do]
    fig = go.Figure()
    fig.add_scatter(x=cesky(J.index + pd.Timedelta(hours=h)), y=J.skutecnost, name="skutečná hladina",
                    line=dict(color="black", width=2))
    fig.add_scatter(x=cesky(J.index + pd.Timedelta(hours=h)), y=J.predpoved, name="„bude jako teď“",
                    line=dict(color="gray", dash="dash"))
    if P is not None:
        P = P[(P.cil == cil) & (P.horizont == h)][od:do]
        fig.add_scatter(x=cesky(P.index + pd.Timedelta(hours=h)), y=P.predpoved,
                        name=f"model {nazev}, vydáno {h} h předem", line=dict(color=MODRA, width=2))
    cary_spa(fig, cil)
    fig.update_layout(yaxis_title="hladina (cm)", height=450, margin=dict(l=10, r=10, t=30, b=50),
                      legend=dict(orientation="h"), hovermode="x unified")
    fig.update_xaxes(tickformat="%d. %m.\n%H:%M")
    st.plotly_chart(fig, width="stretch")
    st.caption("Každý bod modré čáry je samostatná předpověď vydaná o zvolený počet hodin dřív. "
               "„Bude jako teď“ je stejná křivka posunutá o ten počet hodin, proto je vždycky pozadu.")

    M, MJ = metriky(nazev), metriky("jako_ted")
    if not M.empty:
        tab = pd.concat([M.assign(model=nazev), MJ.assign(model="bude jako teď")])
        tab = tab[tab.cil == cil][["model", "horizont", "mae_povodne", "spa2_predstih_h", "spa2_propasnuto",
                                   "spa2_plane_poplachy"]]
        tab.columns = ["model", "hodin dopředu", "chyba při povodních (cm)", "varování před 2. stupněm (h předem)",
                       "propásnuté povodně", "plané poplachy"]
        st.dataframe(tab.set_index(["hodin dopředu", "model"]).sort_index(), width="stretch")
        st.caption("Chyba při povodních je průměrná odchylka v cm v týdnu před vrcholem a 5 dní po něm, "
                   "průměr přes 4 povodně. Varování počítáme od chvíle, kdy model poprvé předpověděl překročení "
                   "2. stupně, do chvíle, kdy hladina práh opravdu překročila.")
