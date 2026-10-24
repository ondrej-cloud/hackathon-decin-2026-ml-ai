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
from predikce import HORIZONTY, KDE, NAZEV, ROOT, SPA, STUPNE, interval, modely, nacti, nacti_model, stupen, vstupy, vysvetleni

POVODNE = {"4/2006": ("2006-03-25", "2006-04-10"), "3/2009": ("2009-02-26", "2009-03-14"),
           "9/2010": ("2010-09-20", "2010-10-06"), "1/2011": ("2011-01-08", "2011-01-24"),
           "9/2024 Boris (test)": ("2024-09-08", "2024-09-24")}
REZIMY = ["Celá povodeň: předpověď × skutečnost", "Zvolený okamžik"]
POVODI = {"vltava": "Vltava", "labe": "Horní Labe", "ohre": "Ohře"}
TZ = "Europe/Prague"

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
    return f'<span class="odznak spa-{s}">{STUPNE[s]}</span>'


def cesky(t):
    return t.tz_convert(TZ)


def okamzik(t):
    t = cesky(t)
    return f"{t.day}. {t.month}. {t.year} {t:%H:%M}"


def cislo(x, mist=1):
    return f"{x:.{mist}f}".replace(".", ",")


def html(text):
    st.markdown(text, unsafe_allow_html=True)


def iframe(obsah, vyska):
    getattr(st, "iframe", components.html)(obsah, height=vyska)


with st.sidebar:
    html(styl.panel_hlava())
    styl.sekce("Stanice")
    cil = st.radio("Stanice", list(KDE), format_func=jmeno, label_visibility="collapsed",
                   captions=[f"stupně {' / '.join(map(str, SPA[c]))} cm" for c in KDE])
    styl.sekce("Zdroj dat")
    dnes = st.toggle("Dnešek: živá data ČHMÚ", value=False)
    stav_dat = st.empty()
    styl.sekce("Okamžik předpovědi")
    st.caption("Přehrávání historie: den a hodina, kdy předpověď vydat. Aplikace ukáže, co by model řekl tehdy.")
    den = st.date_input("Den", value=date(2011, 1, 15), min_value=date(2006, 1, 3), max_value=date(2025, 12, 30),
                        format="DD.MM.YYYY", disabled=dnes)
    hodina = st.slider("Hodina (český čas)", 0, 23, 9, format="%d:00", disabled=dnes)
    styl.sekce("Model")
    seznam = modely()
    nazev = st.selectbox("Model", seznam, index=seznam.index("ridge"), label_visibility="collapsed")
    st.caption("ridge se učil do roku 2018, hodí se na přehrávání historie. ridge_vse se učil na všem do 2025, "
               "hodí se na dnešek.")

X = vstupy_c(cil)
H = hladiny(cil)
DNES = None
if dnes:
    DNES = dnes_c(nazev)
    if not DNES["ok"]:
        stav_dat.warning(DNES["chyba"])
        DNES = None
    else:
        stav_dat.caption(f"Živá data ČHMÚ z opendata.chmi.cz, {cislo(DNES['stari_h'])} h stará.")
else:
    stav_dat.caption("Vypnuto: přehrává se historie z archivu ČHMÚ 2006–2025.")
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
    zdroj = f"živě ČHMÚ, {cislo(DNES['stari_h'])} h" if DNES else "archiv ČHMÚ 2006–2025"
    html(styl.hlavicka(okamzik(cas), nazev, zdroj, bool(DNES)))

tab_ted, tab_kvalita, tab_mapa, tab_animace = st.tabs(["Teď", "Jak dobře to funguje", "Mapa povodí",
                                                        "Animace povodně"])

with tab_ted:
    if DNES:
        st.subheader(f"{jmeno(cil)} dnes, předpověď vydaná {okamzik(cas)} českého času")
    else:
        st.subheader(f"{jmeno(cil)}, {okamzik(cas)} českého času")
    rozmezi = {h: interval(nazev, cil, h, ted, pred[h]) for h in HORIZONTY}
    chmu = DNES[cil]["chmu"] if DNES else {}
    lat, cteni = st.columns([5, 6], gap="medium")
    with lat, st.container(key="karta_lat"):
        html(styl.stitek(f"Vodočet {jmeno(cil)}", "hladina v cm"))
        html(styl.vodocet(SPA[cil], ted, pred, rozmezi, chmu))
    with cteni, st.container(key="karta_cteni"):
        html(styl.stitek("Odečet a předpověď", "stupeň povodňové aktivity"))
        with st.container(key="cteni_ted"):
            st.metric("Hladina teď", f"{ted:.0f} cm")
            html(odznak(cil, ted))
            st.caption("změřeno na stanici ČHMÚ")
        for h in HORIZONTY:
            with st.container(key=f"cteni_{h}"):
                st.metric(f"Za {h} h", f"{pred[h]:.0f} cm", delta=f"{pred[h] - ted:+.0f} cm proti teď",
                          delta_color="off")
                html(odznak(cil, pred[h]))
                pozn = [f"nejspíš {rozmezi[h][0]:.0f} až {rozmezi[h][1]:.0f} cm"] if rozmezi[h] else []
                if chmu.get(h) is not None:
                    pozn.append(f"ČHMÚ {chmu[h]:.0f} cm")
                st.caption(" · ".join(pozn) if pozn else "rozmezí jen pro ridge")
    with st.container(key="karta_citat"):
        html(styl.stitek("Proč to tak vyšlo"))
        st.info(vysvetleni(cil, 24, ted, pred[24], radek))

    if DNES:
        a, b = st.columns(2, gap="medium")
        with a, st.container(key="karta_chmu"):
            html(styl.stitek("Náš model vedle oficiální předpovědi ČHMÚ"))
            udaje = "".join(
                f'<div><dt>Za {h} h</dt><dd>{pred[h]:.0f}<small>cm</small></dd><p>ČHMÚ <b>'
                + (f"{chmu[h]:.0f} cm" if chmu.get(h) is not None else "nezveřejnil") + "</b></p></div>"
                for h in HORIZONTY)
            html(f'<dl class="udaje">{udaje}</dl>')
            st.caption("Náš model je jednodušší a nemá počasí, ČHMÚ má srážkovou předpověď.")
        with b, st.container(key="karta_srazky"):
            srazky = pocasi.predpoved_srazek()
            html(styl.stitek("Srážky v povodí, příštích 48 h", "Open-Meteo"))
            if srazky["ok"]:
                udaje = "".join(f'<div><dt>{POVODI[k]}</dt><dd>{p["mm_48"]}<small>mm</small></dd>'
                                f'<p>za 24 h <b>{p["mm_24"]} mm</b></p></div>' for k, p in srazky["povodi"].items())
                html(f'<dl class="udaje">{udaje}</dl>')
            st.caption(srazky["veta"] + " Srážky do modelu nevstupují, na 12 až 36 h nepomohly (voda z deště je už "
                       "v řekách). Zdroj Open-Meteo (CC BY 4.0).")
        st.caption(f"Živá data ČHMÚ (opendata.chmi.cz), {cislo(DNES['stari_h'])} h stará. "
                   + (f"Dopočteno z bilance vody: {', '.join(DNES['dopocteno'])}. " if DNES["dopocteno"] else "")
                   + (DNES["upozorneni"] or ""))

    okno = H[cas - pd.Timedelta(hours=72): cas]
    fig = go.Figure()
    casy = [cesky(cas + pd.Timedelta(hours=h)) for h in (0,) + HORIZONTY]
    if all(rozmezi.values()):
        fig.add_scatter(x=casy, y=[ted] + [rozmezi[h][1] for h in HORIZONTY], mode="lines", line=dict(width=0),
                        showlegend=False, hoverinfo="skip")
        fig.add_scatter(x=casy, y=[ted] + [rozmezi[h][0] for h in HORIZONTY], mode="lines", fill="tonexty",
                        fillcolor="rgba(124, 198, 228, 0.16)", line=dict(width=0), name="rozmezí (90 % chyb)",
                        hoverinfo="skip")
    fig.add_scatter(x=cesky(okno.index), y=okno.values, mode="lines", name="hladina změřená",
                    line=dict(color=styl.TEXT, width=2.2), hovertemplate="%{y:.0f} cm<extra>změřeno</extra>")
    fig.add_scatter(x=casy, y=[ted] + [pred[h] for h in HORIZONTY], mode="markers+lines", name="předpověď",
                    line=dict(color=styl.VODA_SVETLA, dash="dash", width=2.2),
                    marker=dict(size=[7, 12, 12, 12], color=styl.VODA_SVETLA, line=dict(color=styl.STUDNA, width=2)),
                    hovertemplate="%{y:.0f} cm<extra>předpověď</extra>")
    if DNES and chmu and any(v is not None for v in chmu.values()):
        hc = [h for h in HORIZONTY if chmu.get(h) is not None]
        fig.add_scatter(x=[cesky(cas + pd.Timedelta(hours=h)) for h in hc], y=[chmu[h] for h in hc],
                        mode="markers", name="ČHMÚ", marker=dict(symbol="triangle-left", size=12, color=styl.TEXT),
                        hovertemplate="%{y:.0f} cm<extra>ČHMÚ</extra>")
    ymax = max([float(okno.max())] + [pred[h] for h in HORIZONTY] + [r[1] for r in rozmezi.values() if r])
    styl.cary_spa(fig, SPA[cil], ymax)
    fig.add_vline(x=casy[0], line=dict(color="rgba(230, 235, 240, 0.3)", width=1))
    styl.graf(fig, 400)
    fig.update_yaxes(title_text="hladina (cm)")
    with st.container(key="karta_graf"):
        html(styl.stitek("Posledních 72 hodin a předpověď", f"{jmeno(cil)}, hodinová data"))
        st.plotly_chart(fig, width="stretch", theme=None, config=styl.GRAF)
    st.caption("Černá čára je, co se změřilo do zvoleného okamžiku (svislá čára). Modré body jsou předpověď vydaná "
               "v tomhle okamžiku na 12, 24 a 36 hodin dopředu. Modrý pás je rozmezí, do kterého se vešlo 90 % chyb "
               "modelu na tréninku; na povodních, které model neviděl, to bylo asi 8 z 10 případů. Tečkované čáry "
               "jsou stupně povodňové aktivity."
               + (f" Hladina je hluboko pod 1. stupněm ({SPA[cil][0]} cm), čáry stupňů se do grafu nevešly."
                  if ymax * 1.6 + 60 < SPA[cil][0] else ""))

with tab_kvalita:
    html("<p>Model jsme zkoušeli na čtyřech povodních, které při učení neviděl (učil se na letech 2006–2018 bez "
         "nich a bez 20 dní kolem nich). Srovnáváme ho s nejjednodušší předpovědí <strong>„bude jako teď“</strong>, "
         "tedy že za 24 h bude stejná hladina jako teď.</p>")
    with st.container(key="karta_volby_kvalita"):
        a, b = st.columns([3, 1.2], gap="medium")
        povoden = a.radio("Povodeň", list(POVODNE), index=3, horizontal=True)
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

    M, MJ = metriky(nazev, cast), metriky("jako_ted", cast)
    if not M.empty:
        m = M[(M.cil == cil) & (M.horizont == h)].iloc[0]
        j = MJ[(MJ.cil == cil) & (MJ.horizont == h)].iloc[0]
        kde = "průměr 4 povodní z validace" if cast == "val" else f"průměr {m.spa2_povodni} povodní z testu 2021–2025"
        with st.container(key="karta_souhrn"):
            html(styl.stitek(f"{jmeno(cil)}, předpověď vydaná {h} h předem", kde))
            mene = (1 - m.mae_povodne / j.mae_povodne) * 100
            html('<dl class="udaje">'
                 f'<div><dt>Chyba při povodních</dt><dd>{cislo(m.mae_povodne)}<small>cm</small></dd>'
                 f'<p>bude jako teď <b>{cislo(j.mae_povodne)} cm</b>, o {mene:.0f} % méně</p></div>'
                 f'<div><dt>Varování před 2. stupněm</dt><dd>{cislo(m.spa2_predstih_h)}<small>h předem</small></dd>'
                 f'<p>bude jako teď <b>{cislo(j.spa2_predstih_h)} h</b></p></div>'
                 f'<div><dt>Propásnuté povodně</dt><dd>{m.spa2_propasnuto:.0f}<small>z {m.spa2_povodni:.0f}</small></dd>'
                 f'<p>bude jako teď <b>{j.spa2_propasnuto:.0f}</b></p></div>'
                 f'<div><dt>Plané poplachy</dt><dd>{m.spa2_plane_poplachy:.0f}</dd>'
                 f'<p>bude jako teď <b>{j.spa2_plane_poplachy:.0f}</b></p></div></dl>')

    J = predpovedi_val("jako_ted", cast)
    J = J[(J.cil == cil) & (J.horizont == h)][od:do]
    fig = go.Figure()
    fig.add_scatter(x=cesky(J.index + pd.Timedelta(hours=h)), y=J.skutecnost, name="skutečná hladina",
                    line=dict(color=styl.TEXT, width=2.2), hovertemplate="%{y:.0f} cm")
    fig.add_scatter(x=cesky(J.index + pd.Timedelta(hours=h)), y=J.predpoved, name="„bude jako teď“",
                    line=dict(color=styl.JAKO_TED, dash="dash", width=1.8), hovertemplate="%{y:.0f} cm")
    if P is not None:
        P = P[(P.cil == cil) & (P.horizont == h)][od:do]
        fig.add_scatter(x=cesky(P.index + pd.Timedelta(hours=h)), y=P.predpoved,
                        name=f"model {nazev}, vydáno {h} h předem", line=dict(color=styl.VODA, width=2.4),
                        hovertemplate="%{y:.0f} cm")
    styl.cary_spa(fig, SPA[cil])
    styl.graf(fig, 440)
    fig.update_yaxes(title_text="hladina (cm)")
    with st.container(key="karta_graf_kvalita"):
        html(styl.stitek(f"Povodeň {povoden}: skutečnost, model a „bude jako teď“", jmeno(cil)))
        st.plotly_chart(fig, width="stretch", theme=None, config=styl.GRAF)
    st.caption("Každý bod modré čáry je samostatná předpověď vydaná o zvolený počet hodin dřív. „Bude jako teď“ je "
               "stejná křivka posunutá o ten počet hodin, proto je vždycky pozadu.")

    if not M.empty:
        tab = pd.concat([M.assign(model=nazev), MJ.assign(model="bude jako teď")])
        tab = tab[tab.cil == cil][["horizont", "model", "mae_povodne", "spa2_predstih_h", "spa2_propasnuto",
                                   "spa2_plane_poplachy"]]
        tab.columns = ["hodin dopředu", "model", "chyba při povodních (cm)", "varování před 2. stupněm (h)",
                       "propásnuté povodně", "plané poplachy"]
        tab = tab.set_index(["hodin dopředu", "model"]).sort_index()
        with st.container(key="karta_tabulka"):
            html(styl.stitek("Všechny horizonty", kde))
            st.table(tab.style.format(precision=1, decimal=",").apply(
                lambda r: [f"color: {styl.TLUMENE}" if r.name[1] == "bude jako teď" else "" for _ in r], axis=1))
        st.caption("Chyba při povodních je průměrná odchylka v cm v týdnu před vrcholem a 5 dní po něm. Varování "
                   "počítáme od chvíle, kdy model poprvé předpověděl překročení 2. stupně, do chvíle, kdy hladina "
                   "práh opravdu překročila.")


def predpovedi_pro_mapu(t):
    """Předpověď modelu za 24 h pro Děčín i Ústí v čase t (UTC), pro popisky na mapě."""
    out = {}
    for c in KDE:
        Xc = vstupy_c(c)
        if t in Xc.index:
            out[c] = (24, float(model_c(nazev, c, 24).predict(Xc.loc[[t]])[0]))
    return out


def prehrat():
    st.session_state.mapa_rezim = REZIMY[0]


def co_znamena():
    voda = n_leta_voda(cil, pred[24])
    html(f"<p><strong>Co předpověď znamená pro {jmeno(cil)}:</strong> {voda['popis']} "
         + (f"Na mapě je vyplněné oficiální záplavové území pro {voda['N']}letou vodu (DIBAVOD), ostatní jen obrysem."
            if voda["N"] >= 5 else
            "Rozliv mimo koryto se čeká až od pětileté vody, záplavová území jsou na mapě jen obrysem.") + "</p>")


with tab_mapa:
    st.session_state.setdefault("mapa_rezim", REZIMY[1])
    token = mapbox_token()
    with st.container(key="karta_prehravac"):
        html(styl.stitek("Povodeň v mapě", "co teče proti proudu, dorazí k nám"))
        rezim = st.radio("Režim", REZIMY, horizontal=True, key="mapa_rezim", label_visibility="collapsed",
                         captions=["Čas po hodinách, rozliv z předpovědi 24 h předem vedle rozlivu ze skutečné hladiny.",
                                   f"Stanice a rozliv v okamžiku z levého panelu ({okamzik(cas)})."])
        a, b = st.columns([3, 1.25], gap="medium", vertical_alignment="bottom")
        povoden_m = a.radio("Povodeň", list(POVODNE), index=3, horizontal=True, key="mapa_povoden")
        if rezim == REZIMY[0]:
            cil_m = b.radio("Město", list(KDE), format_func=jmeno, horizontal=True, key="mapa_cil")
            prehraj = False
        else:
            prehraj = b.button("Přehrát povodeň", type="primary", width="stretch", on_click=prehrat if token else None)

    if rezim == REZIMY[0] and token:
        iframe(mapbox_animace_html(povoden_m, cil_m, nazev), 720)
        st.caption("Rozliv z terénu ČÚZK DMR 5G proti hladině, shoda s úředními územími 82 až 90 %.")
    elif rezim == REZIMY[0]:
        st.warning("Celá povodeň s porovnáním potřebuje token Mapboxu v .env. Bez něj přepněte na Zvolený okamžik "
                   "a tlačítko Přehrát povodeň projde povodeň po 6 hodinách na jednodušší mapě.")
    else:
        pohled = st.radio("Pohled", list(POHLEDY), horizontal=True, key="mapa_pohled",
                          help="Přiblížení na město ukáže záplavové území podle předpovědi.")
        misto = st.empty()
        if DNES:
            tabulka_mapy = DNES["tabulka"]
            pred_mapy = {c: (24, DNES[c]["predpoved"][24]) for c in KDE}
        else:
            tabulka_mapy, pred_mapy = None, predpovedi_pro_mapu(cas)
        if prehraj and not token:
            od_m, do_m = POVODNE[povoden_m]
            for t in pd.date_range(od_m, f"{do_m} 18:00", freq="6h", tz=TZ):
                t = t.tz_convert("UTC")
                misto.pydeck_chart(mapa_deck(t, predpovedi_pro_mapu(t), pohled), height=650)
                cas_modul.sleep(0.6)
        elif token and not DNES:
            # Mapbox GL: záplavové území přilepené na terén a 3D budovy; v Dnešku a bez tokenu jednodušší mapa níž
            with misto:
                iframe(mapbox_html(cas, pred_mapy, pohled), 700)
        else:
            misto.pydeck_chart(mapa_deck(cas, pred_mapy, pohled, tabulka=tabulka_mapy), height=650)
        if DNES:
            st.caption("Dnešek: sloupce jsou z živých dat ČHMÚ. Průtoky v Mělníku a Nymburce ČHMÚ operativně "
                       "nezveřejňuje, jsou dopočtené z bilance vody.")
        co_znamena()
    st.caption("Záplavová území Q5 / Q20 / Q100 jsou oficiální polygony pro ustálený N-letý průtok (VÚV TGM, DIBAVOD), "
               "ne výpočet pro naši konkrétní povodeň; N-leté průtoky a měrná křivka jsou z ČHMÚ. "
               "Děčín a Ústí: barva podle hladiny a stupňů povodňové aktivity. Ostatní stanice: zelená pod 95. "
               "percentilem průtoku z let 2006–2018, žlutá do 99., červená nad ním; nejde o oficiální stupně. "
               "Kolečkem přiblížíte, tažením posunete, Shift a tažením natočíte. "
               + ("Snímky a výšky © Mapbox, © Maxar. " if token else
                  "Podklad © OpenStreetMap, výšky Mapzen / AWS Terrain Tiles. ")
               + "Měření ČHMÚ. Dlaždice se stahují z internetu.")

with tab_animace:
    with st.container(key="karta_animace"):
        html(styl.stitek("Povodeň v animaci", "kapky po skutečných řekách"))
        povoden_a = st.radio("Povodeň", list(POVODNE), index=3, horizontal=True, key="animace_povoden",
                             label_visibility="collapsed")
        html("<p>Víc vody, víc a jasnějších kapek.</p>")
    iframe(animace_html(povoden_a, nazev), 720)
    st.caption("Řeky © OpenStreetMap, snímky a výšky © Mapbox, © Maxar, měření ČHMÚ.")
