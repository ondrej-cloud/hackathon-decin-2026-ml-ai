r"""Labe: kolik vody přiteče do Děčína a Ústí. Aplikace pro povodňovou komisi města a lidi u řeky.

Spuštění z kořene repozitáře:
    Windows:  .venv\Scripts\python -m streamlit run app\app.py
    Mac:      .venv/bin/python -m streamlit run app/app.py
"""
import json
import time as cas_modul
from datetime import date, datetime, time

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

import aktualni
import animace
import mapbox_mapa
import pocasi
import styl
from mapa import POHLEDY, deck as mapa_deck, mapbox_token
from rozliv import n_leta_voda
from predikce import (BARVY, HORIZONTY, KDE, NAZEV, ROOT, SPA, STUPNE, interval, modely, nacti, nacti_model, stupen,
                      vstupy, vysvetleni)

POVODNE = {"4/2006": ("2006-03-25", "2006-04-10"), "3/2009": ("2009-02-26", "2009-03-14"),
           "9/2010": ("2010-09-20", "2010-10-06"), "1/2011": ("2011-01-08", "2011-01-24"),
           "9/2024 Boris (test)": ("2024-09-08", "2024-09-24")}
TZ = "Europe/Prague"
MODRA = styl.VODA

st.set_page_config(page_title="Labe: předpověď hladiny", layout="wide")
styl.pouzij()
hlavicka = st.container()


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
def predpovedi_val(nazev, cast="val"):
    return pd.read_parquet(ROOT / "results/predpovedi" / f"{nazev}{'_test' if cast == 'test' else ''}.parquet")


@st.cache_data
def animace_html(povoden, nazev):
    od, do = animace.okno(povoden)
    return animace.html(od, do, nazev)


@st.cache_data
def mapbox_animace_html(povoden, cil, nazev):
    """Celá povodeň v mapě: čas po hodinách, vlevo rozliv z předpovědi 24 h předem, vpravo ze skutečné hladiny."""
    od, do = animace.okno(povoden)
    return mapbox_mapa.html_animace(od, do, cil, nazev, mapbox_mapa.MESTA[cil])


@st.cache_data
def mapbox_html(cas, predpovedi, pohled):
    """Mapa v Mapbox GL (satelit, 3D budovy, záplavová území na terénu); stavba stránky trvá asi sekundu."""
    return mapbox_mapa.html(cas, predpovedi, pohled)


@st.cache_data(ttl=600)
def dnes_c(nazev):
    """Předpověď z aktuálních dat ČHMÚ, nejvýš 10 minut stará."""
    return aktualni.predpoved_dnes(nazev)


@st.cache_data
def metriky(nazev, cast="val"):
    """Poslední plný výsledek modelu na validaci (nebo testu) z results/."""
    for f in sorted((ROOT / "results").glob(f"*_{nazev}{'_test' if cast == 'test' else ''}.json"), reverse=True):
        z = json.loads(f.read_text(encoding="utf-8"))
        if z["cast"] == cast and not z.get("rychle"):
            return pd.DataFrame(z["vysledky"])
    return pd.DataFrame()


def jmeno(cil):
    return NAZEV[cil].split(" (")[0]


def odznak(cil, hladina):
    s = stupen(cil, hladina)
    return (f'<span class="odznak spa-{s}" style="background:{BARVY[s]};color:{"#141414" if s == 1 else "#fff"}">'
            f'{STUPNE[s]}</span>')


def cary_spa(fig, cil, ymax=None):
    """Čáry stupňů povodňové aktivity; při nízké vodě jen ty, které jsou v dosahu dat, jinak by graf roztáhly."""
    for n, (prah, barva, popisek) in enumerate(zip(SPA[cil], BARVY[1:], styl.POPISKY_SPA), 1):
        if ymax is not None and prah > ymax * 1.6 + 60:
            continue
        fig.add_hline(y=prah, line=dict(color=barva, dash="dot", width=1.5), annotation_text=f"{n}. stupeň",
                      annotation_position="top left", annotation_font_color=popisek)


def vzhled_grafu(fig, vyska):
    """Společný vzhled grafů: průhledné pozadí, písmo a barvy aplikace."""
    fig.update_layout(template="plotly_dark", height=vyska, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(family=f"{styl.PISMO}, sans-serif", size=13, color=styl.TLUMENE),
                      yaxis_title="hladina (cm)", margin=dict(l=16, r=20, t=52, b=36), hovermode="x unified",
                      legend=dict(orientation="h", yanchor="bottom", y=1.03, x=0, font=dict(color=styl.TEXT)),
                      hoverlabel=dict(bgcolor="#0f1419", bordercolor="rgba(255,255,255,0.2)",
                                      font=dict(family=f"{styl.PISMO}, sans-serif", color=styl.TEXT)))
    osa = dict(gridcolor="rgba(255,255,255,0.06)", linecolor="rgba(255,255,255,0.14)", zeroline=False)
    fig.update_xaxes(tickformat="%d. %m.\n%H:%M", **osa)
    fig.update_yaxes(**osa)


def cesky(t):
    return t.tz_convert(TZ)


def okamzik(t):
    t = cesky(t)
    return f"{t.day}. {t.month}. {t.year} {t:%H:%M}"


with st.sidebar:
    st.header("Nastavení")
    seznam = modely()
    nazev = st.selectbox("Model", seznam, index=seznam.index("ridge"),
                         help="ridge se učil do roku 2018 (pro přehrávání historie), ridge_vse na všem do 2025 (pro dnešek).")
    cil = st.radio("Stanice", list(KDE), format_func=jmeno,
                   captions=[f"stupně {' / '.join(map(str, SPA[c]))} cm" for c in KDE])
    dnes = st.toggle("Dnešek: živá data ČHMÚ", value=False,
                     help="Stáhne poslední měření z opendata.chmi.cz a vydá předpověď na teď. Vypnuté = přehrávání historie.")
    st.subheader("Okamžik předpovědi")
    st.caption("Přehrávání historie: vyber den a hodinu a aplikace ukáže, co by model řekl tehdy.")
    den = st.date_input("Den", value=date(2011, 1, 15), min_value=date(2006, 1, 3), max_value=date(2025, 12, 30))
    hodina = st.slider("Hodina (český čas)", 0, 23, 9)

X = vstupy_c(cil)
H = hladiny(cil)
DNES = None
if dnes:
    DNES = dnes_c(nazev)
    if not DNES["ok"]:
        st.sidebar.warning(DNES["chyba"])
        DNES = None
if DNES:
    cas, radek, ted, pred = DNES["cas_utc"], DNES[cil]["radek"], DNES[cil]["ted"], DNES[cil]["predpoved"]
    H = DNES["hladiny"][f"{cil}_H"]
else:
    cas = pd.Timestamp(datetime.combine(den, time(hodina))).tz_localize(TZ, ambiguous=False, nonexistent="shift_forward")
    cas = cas.tz_convert("UTC")
    if cas not in X.index:
        cas = X.index[X.index.get_indexer([cas], method="nearest")[0]]
        st.sidebar.warning(f"Pro zvolenou hodinu chybí data, beru nejbližší: {cesky(cas):%d. %m. %Y %H:%M}.")
    radek = X.loc[[cas]]
    ted = float(radek[f"{cil}_H_0"].iloc[0])
    pred = {h: float(model_c(nazev, cil, h).predict(radek)[0]) for h in HORIZONTY}

with hlavicka:
    zdroj = f"živá data ČHMÚ, {str(DNES['stari_h']).replace('.', ',')} h stará" if DNES else "archiv ČHMÚ 2006–2025"
    st.markdown(styl.hlavicka(okamzik(cas), nazev, zdroj, bool(DNES)), unsafe_allow_html=True)

tab_ted, tab_kvalita, tab_mapa, tab_animace = st.tabs(["Teď", "Jak dobře to funguje", "Mapa povodí",
                                                        "Animace povodně"])

with tab_ted:
    if DNES:
        st.subheader(f"{jmeno(cil)} dnes, předpověď vydaná {cesky(cas):%d. %m. %Y %H:%M} českého času")
        st.caption(f"Živá data ČHMÚ (opendata.chmi.cz), {DNES['stari_h']} h stará. "
                   + (f"Dopočteno z bilance vody: {', '.join(DNES['dopocteno'])}. " if DNES["dopocteno"] else "")
                   + (DNES["upozorneni"] or ""))
    else:
        st.subheader(f"{jmeno(cil)}, {cesky(cas):%d. %m. %Y %H:%M} českého času")
    with st.container(key="pult"):
        sloupce = st.columns(4)
    sloupce[0].metric("Hladina teď", f"{ted:.0f} cm")
    sloupce[0].markdown(odznak(cil, ted), unsafe_allow_html=True)
    sloupce[0].caption("změřeno na stanici ČHMÚ")
    rozmezi = {h: interval(nazev, cil, h, ted, pred[h]) for h in HORIZONTY}
    for c, h in zip(sloupce[1:], HORIZONTY):
        c.metric(f"Za {h} h", f"{pred[h]:.0f} cm", delta=f"{pred[h] - ted:+.0f} cm", delta_color="inverse")
        c.markdown(odznak(cil, pred[h]), unsafe_allow_html=True)
        if rozmezi[h]:
            c.caption(f"nejspíš {rozmezi[h][0]:.0f} až {rozmezi[h][1]:.0f} cm")
    with st.container(key="citat"):
        st.info(vysvetleni(cil, 24, ted, pred[24], radek))
    if DNES and any(v is not None for v in DNES[cil]["chmu"].values()):
        st.caption("Pro srovnání oficiální předpověď ČHMÚ na stejné hodiny: "
                   + ", ".join(f"za {h} h {v:.0f} cm" for h, v in DNES[cil]["chmu"].items() if v is not None)
                   + ". Náš model je jednodušší a nemá počasí, ČHMÚ má srážkovou předpověď.")
    if DNES:
        st.caption(pocasi.predpoved_srazek()["veta"] + " Srážky do modelu nevstupují, na 12 až 36 h nepomohly "
                   "(voda z deště je už v řekách). Zdroj Open-Meteo (CC BY 4.0).")

    okno = H[cas - pd.Timedelta(hours=72): cas]
    fig = go.Figure()
    fig.add_scatter(x=cesky(okno.index), y=okno.values, mode="lines", name="hladina (změřeno)",
                    line=dict(color=styl.TEXT, width=2.2))
    casy = [cesky(cas + pd.Timedelta(hours=h)) for h in (0,) + HORIZONTY]
    if all(rozmezi.values()):
        fig.add_scatter(x=casy, y=[ted] + [rozmezi[h][1] for h in HORIZONTY], mode="lines", line=dict(width=0),
                        showlegend=False, hoverinfo="skip")
        fig.add_scatter(x=casy, y=[ted] + [rozmezi[h][0] for h in HORIZONTY], mode="lines", fill="tonexty",
                        fillcolor="rgba(58,160,201,0.2)", line=dict(width=0), name="rozmezí (90 % chyb)",
                        hoverinfo="skip")
    fig.add_scatter(x=casy,
                    y=[ted] + [pred[h] for h in HORIZONTY], mode="markers+lines", name="předpověď",
                    line=dict(color=MODRA, dash="dash", width=2.2),
                    marker=dict(size=[7, 12, 12, 12], color=MODRA, line=dict(color="#0f1419", width=2)),
                    text=["teď"] + [f"za {h} h" for h in HORIZONTY])
    ymax = max([float(okno.max())] + [pred[h] for h in HORIZONTY] + [r[1] for r in rozmezi.values() if r])
    cary_spa(fig, cil, ymax)
    if ymax * 1.6 + 60 < SPA[cil][0]:
        st.caption(f"Hladina je hluboko pod 1. stupněm povodňové aktivity ({SPA[cil][0]} cm), čáry stupňů se do "
                   "grafu nevešly.")
    fig.add_vline(x=casy[0], line=dict(color="rgba(255,255,255,0.25)", width=1))
    vzhled_grafu(fig, 420)
    st.plotly_chart(fig, width="stretch")
    st.caption("Bílá čára je, co se změřilo do zvoleného okamžiku (svislá čára). Modré body jsou předpověď vydaná v tomhle "
               "okamžiku na 12, 24 a 36 hodin dopředu. Modrý pás je rozmezí, do kterého se vešlo 90 % chyb modelu "
               "na tréninku; na povodních, které model neviděl, to bylo asi 8 z 10 případů. Tečkované čáry jsou "
               "stupně povodňové aktivity.")

with tab_kvalita:
    st.markdown("Model jsme zkoušeli na čtyřech povodních, které při učení neviděl (učil se na letech 2006–2018 "
                "bez nich a bez 20 dní kolem nich). Srovnáváme s nejjednodušší předpovědí „bude jako teď“.")
    a, b, _ = st.columns([1.1, 1.3, 1.6], vertical_alignment="bottom")
    povoden = a.selectbox("Povodeň", list(POVODNE), index=3)
    h = b.radio("Předpověď vydaná ... hodin předem", HORIZONTY, index=1, horizontal=True)
    od, do = POVODNE[povoden]
    cast = "test" if "test" in povoden else "val"
    if cast == "test":
        st.info("Povodeň Boris 9/2024 je z testovací části (2021–2025), kterou model nikdy neviděl a která se pustila "
                "jednou na konci na finální model. Předpovědi jsou z modelu učeného do roku 2018.")
    try:
        P = predpovedi_val(nazev, cast)
    except FileNotFoundError:
        P = None
        st.warning(f"Pro model {nazev} zatím nejsou uložené předpovědi ({cast}) v results/predpovedi/.")
    J = predpovedi_val("jako_ted", cast)
    J = J[(J.cil == cil) & (J.horizont == h)][od:do]
    fig = go.Figure()
    fig.add_scatter(x=cesky(J.index + pd.Timedelta(hours=h)), y=J.skutecnost, name="skutečná hladina",
                    line=dict(color=styl.TEXT, width=2.2))
    fig.add_scatter(x=cesky(J.index + pd.Timedelta(hours=h)), y=J.predpoved, name="„bude jako teď“",
                    line=dict(color=styl.SEDA, dash="dash", width=1.6))
    if P is not None:
        P = P[(P.cil == cil) & (P.horizont == h)][od:do]
        fig.add_scatter(x=cesky(P.index + pd.Timedelta(hours=h)), y=P.predpoved,
                        name=f"model {nazev}, vydáno {h} h předem", line=dict(color=MODRA, width=2.4))
    cary_spa(fig, cil)
    vzhled_grafu(fig, 450)
    st.plotly_chart(fig, width="stretch")
    st.caption("Každý bod modré čáry je samostatná předpověď vydaná o zvolený počet hodin dřív. "
               "„Bude jako teď“ je stejná křivka posunutá o ten počet hodin, proto je vždycky pozadu.")

    M, MJ = metriky(nazev, cast), metriky("jako_ted", cast)
    if not M.empty:
        tab = pd.concat([M.assign(model=nazev), MJ.assign(model="bude jako teď")])
        tab = tab[tab.cil == cil][["model", "horizont", "mae_povodne", "spa2_predstih_h", "spa2_propasnuto",
                                   "spa2_plane_poplachy"]]
        tab.columns = ["model", "hodin dopředu", "chyba při povodních (cm)", "varování před 2. stupněm (h předem)",
                       "propásnuté povodně", "plané poplachy"]
        tab = tab.set_index(["hodin dopředu", "model"]).sort_index()
        # řádky „bude jako teď“ ztlumené, ať je vidět náš model
        st.dataframe(tab.style.format(precision=1).apply(
            lambda r: [f"color: {styl.TLUMENE}" if r.name[1] == "bude jako teď" else "" for _ in r], axis=1),
            width="stretch")
        st.caption("Chyba při povodních je průměrná odchylka v cm v týdnu před vrcholem a 5 dní po něm, "
                   "průměr přes 4 povodně. Varování počítáme od chvíle, kdy model poprvé předpověděl překročení "
                   "2. stupně, do chvíle, kdy hladina práh opravdu překročila.")

def predpovedi_pro_mapu(t):
    """Předpověď modelu za 24 h pro Děčín i Ústí v čase t (UTC), pro popisky na mapě."""
    out = {}
    for c in KDE:
        Xc = vstupy_c(c)
        if t in Xc.index:
            out[c] = (24, float(model_c(nazev, c, 24).predict(Xc.loc[[t]])[0]))
    return out


with tab_mapa:
    st.markdown(f"**Co teče proti proudu, dorazí k nám.** Stanice {cesky(cas):%d. %m. %Y %H:%M}: velikost podle "
                "průtoku, barva podle stupně povodňové aktivity, u Děčína a Ústí předpověď modelu za 24 h. Pohled "
                "Děčín nebo Ústí přiblíží město s 3D budovami a oficiálním záplavovým územím, které předpovědi "
                "odpovídá. Okamžik se mění v levém menu.")
    rezim = st.radio("Režim", ["Zvolený okamžik", "Celá povodeň: předpověď × skutečnost"], horizontal=True,
                     key="mapa_rezim", help="Celá povodeň přehraje čas po hodinách a porovná rozliv z předpovědi "
                                            "s rozlivem ze skutečné hladiny.")
    if rezim != "Zvolený okamžik" and mapbox_token():
        a, b = st.columns(2)
        povoden_m = a.selectbox("Povodeň", list(POVODNE), index=3, key="mapa_povoden")
        cil_m = b.radio("Město", list(KDE), format_func=jmeno, horizontal=True, key="mapa_cil")
        getattr(st, "iframe", components.html)(mapbox_animace_html(povoden_m, cil_m, nazev), height=720)
        st.caption("Vlevo rozliv z hladiny, kterou model předpověděl 24 h předem, vpravo rozliv ze skutečně naměřené "
                   "hladiny v tutéž hodinu; posuvník uprostřed obě strany porovná, tlačítko spustí čas. Rozliv je "
                   "z výškového modelu terénu ČÚZK DMR 5G (2 m): zaplaví se vše, co je níž než hladina a spojené "
                   "s řekou; proti úředním územím Q5/Q20/Q100 se shoduje z 82 až 90 %. Je to statický odhad bez "
                   "proudění; zdi a hráze pod rozlišením terénu nevidí.")
        pohled = "celé povodí"
    elif rezim != "Zvolený okamžik":
        st.warning("Celá povodeň s porovnáním potřebuje token Mapboxu v .env.")
        pohled = "celé povodí"
    else:
        pohled = st.radio("Pohled", list(POHLEDY), horizontal=True, key="mapa_pohled",
                          help="Přiblížení na město ukáže záplavové území podle předpovědi.")
    misto = st.empty()
    if rezim != "Zvolený okamžik":
        pass
    elif DNES:
        st.caption("Dnešek: sloupce jsou z živých dat ČHMÚ. Průtoky v Mělníku a Nymburce ČHMÚ operativně nezveřejňuje, "
                   "jsou dopočtené z bilance vody.")
        tabulka_mapy = DNES["tabulka"]
        pred_mapy = {c: (24, DNES[c]["predpoved"][24]) for c in KDE}
    else:
        tabulka_mapy, pred_mapy = None, predpovedi_pro_mapu(cas)
    if rezim != "Zvolený okamžik":
        pass
    elif st.button("Přehrát povodeň 1/2011 (8. až 24. 1., po 6 hodinách, asi 40 s)", icon=":material/play_arrow:"):
        for t in pd.date_range("2011-01-08", "2011-01-24 18:00", freq="6h", tz=TZ):
            t = t.tz_convert("UTC")
            misto.pydeck_chart(mapa_deck(t, predpovedi_pro_mapu(t), pohled), height=650)
            cas_modul.sleep(0.6)
    elif mapbox_token() and not DNES:
        # Mapbox GL: záplavové území přilepené na terén a 3D budovy; v Dnešku a bez tokenu jednodušší mapa níž
        with misto:
            getattr(st, "iframe", components.html)(mapbox_html(cas, pred_mapy, pohled), height=700)
        voda = n_leta_voda(cil, pred[24])
        st.markdown(f"**Co předpověď znamená pro {jmeno(cil)}:** {voda['popis']} "
                    + (f"Na mapě je vyplněné oficiální záplavové území pro {voda['N']}letou vodu (DIBAVOD), ostatní "
                       "jen obrysem." if voda["N"] >= 5 else
                       "Rozliv mimo koryto se čeká až od pětileté vody, záplavová území jsou na mapě jen obrysem."))
    else:
        misto.pydeck_chart(mapa_deck(cas, pred_mapy, pohled, tabulka=tabulka_mapy), height=650)
        voda = n_leta_voda(cil, pred[24])
        st.markdown(f"**Co předpověď znamená pro {jmeno(cil)}:** {voda['popis']} "
                    + (f"Na mapě je vyplněné oficiální záplavové území pro {voda['N']}letou vodu (DIBAVOD), ostatní "
                       "jen obrysem." if voda["N"] >= 5 else
                       "Rozliv mimo koryto se čeká až od pětileté vody, záplavová území jsou na mapě jen obrysem."))
    st.caption("Záplavová území Q5 / Q20 / Q100 jsou oficiální polygony pro ustálený N-letý průtok (VÚV TGM, DIBAVOD), "
               "ne výpočet pro naši konkrétní povodeň; N-leté průtoky a měrná křivka jsou z ČHMÚ. "
               "Děčín a Ústí: barva podle hladiny a stupňů povodňové aktivity. Ostatní stanice: zelená pod 95. "
               "percentilem průtoku z let 2006–2018, žlutá do 99., červená nad ním; nejde o oficiální stupně. "
               "Kolečkem přiblížíte, tažením posunete, Shift a tažením natočíte. "
               + ("Snímky a výšky © Mapbox, © Maxar. " if mapbox_token() else
                  "Podklad © OpenStreetMap, výšky Mapzen / AWS Terrain Tiles. ")
               + "Měření ČHMÚ. Dlaždice se stahují z internetu.")

with tab_animace:
    povoden_a = st.selectbox("Povodeň", list(POVODNE), index=3, key="animace_povoden")
    st.markdown("**Co teče proti proudu, dorazí k nám.** Kapky tečou po skutečných řekách rychlostí podle změřené "
                "doby putování a nesou průtok ze stanice proti proudu: víc vody, víc a jasnějších kapek. Tlačítko "
                "spustí čas, posuvník ho posune. V panelu vpravo je předpověď modelu za 24 h a stupeň; skutečnou "
                "hladinu o 24 h později známe jen zpětně, v provozu by tam nebyla.")
    getattr(st, "iframe", components.html)(animace_html(povoden_a, nazev), height=720)
    st.caption("Řeky © OpenStreetMap (ODbL), snímky a výšky © Mapbox, © Maxar, měření ČHMÚ. Doby putování mezi "
               "stanicemi jsou odhad z našich dat (např. Praha → Vraňany 4,5 h, Mělník → Ústí 12 h, Ústí → Děčín 4 h).")
