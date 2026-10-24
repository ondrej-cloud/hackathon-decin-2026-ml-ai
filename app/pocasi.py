"""Předpověď srážek v povodí nad Ústím z Open-Meteo (https://open-meteo.com/, CC BY 4.0, bez klíče).

Je to jen kontext vedle předpovědi hladiny, do modelu srážky nevstupují: na horizontech 12 až 36 h je voda
z deště už v řekách a srážky se v pokusech neprojevily (docs/DATA.md, sekce Labe).

Open-Meteo dává srážky po hodinách a hodnota v čase t je součet za hodinu před t. Okno "příštích 24 h"
jsou proto hodiny s časem v intervalu (teď, teď + 24 h].

python app/pocasi.py stáhne předpověď a vypíše ji.
"""
import math
import time

import pandas as pd
import requests

URL = "https://api.open-meteo.com/v1/forecast"
# reprezentativní body povodí (zeměpisná šířka, délka)
BODY = {
    "vltava": [(50.07, 14.43), (49.96, 14.07), (49.69, 14.01), (49.78, 14.69), (48.97, 14.47)],  # Praha, Beroun, Příbram, Benešov, České Budějovice
    "labe": [(50.21, 15.83), (50.59, 15.16), (50.04, 15.78), (50.63, 15.61)],  # Hradec Králové, Turnov, Pardubice, Vrchlabí
    "ohre": [(50.23, 12.87), (50.36, 13.80), (50.38, 13.27)],  # Karlovy Vary, Louny, Kadaň
}
NAZEV = {"vltava": "Vltavy", "labe": "horního Labe", "ohre": "Ohře"}
HODNE_MM = 20  # průměrný úhrn povodí za 48 h, od kterého varujeme
MALO_MM = 5  # pod tím je to "skoro nic"
PAMET_S = 30 * 60
PAMET_CHYBY_S = 2 * 60  # ať aplikace při výpadku sítě nečeká na každé překreslení

_pamet = {"do": 0.0, "vysledek": None}


def _mm(x):
    return int(math.floor(x + 0.5))  # round() zaokrouhluje 2,5 na 2


def _vyjmenuj(klice):
    jmena = [NAZEV[k] for k in klice]
    return jmena[0] if len(jmena) == 1 else ", ".join(jmena[:-1]) + " a " + jmena[-1]


def _stahni():
    """Hodinové srážky (mm) po bodech: {povodí: [Series s indexem UTC, ...]}."""
    body = [b for bs in BODY.values() for b in bs]
    r = requests.get(URL, params=dict(latitude=",".join(str(b[0]) for b in body),
                                      longitude=",".join(str(b[1]) for b in body),
                                      hourly="precipitation", forecast_days=3, timezone="UTC"), timeout=20)
    r.raise_for_status()
    data = r.json()
    if not isinstance(data, list) or len(data) != len(body):
        raise ValueError("Open-Meteo vrátil jiný počet bodů, než jsme chtěli.")
    rady = [pd.Series(d["hourly"]["precipitation"], index=pd.to_datetime(d["hourly"]["time"], utc=True),
                      dtype=float) for d in data]
    out, i = {}, 0
    for povodi, bs in BODY.items():
        out[povodi] = rady[i:i + len(bs)]
        i += len(bs)
    return out


def _spocti(rady, ted):
    povodi = {}
    for k, body in rady.items():
        uhrn = {}
        for h in (24, 48):
            okna = [s[(s.index > ted) & (s.index <= ted + pd.Timedelta(hours=h))] for s in body]
            if any(len(o) < h or o.isna().any() for o in okna):
                raise ValueError(f"Open-Meteo nemá srážky na celých {h} h dopředu.")
            uhrn[h] = [o.sum() for o in okna]
        povodi[k] = dict(mm_24=_mm(sum(uhrn[24]) / len(body)), mm_48=_mm(sum(uhrn[48]) / len(body)),
                         max_bod_48=_mm(max(uhrn[48])))
    return povodi


def _veta(povodi):
    v, l, o = (povodi[k]["mm_48"] for k in ("vltava", "labe", "ohre"))
    veta = f"Příštích 48 h má v povodí Vltavy spadnout {v} mm, horního Labe {l} mm, Ohře {o} mm"
    hodne = [k for k, p in povodi.items() if p["mm_48"] > HODNE_MM]
    if hodne:
        return (f"{veta}; v povodí {_vyjmenuj(hodne)} to je hodně, za 36 h a dál může být hladina vyšší, "
                f"než model říká, srážky do něj nevstupují.")
    if max(p["mm_48"] for p in povodi.values()) < MALO_MM:
        return f"{veta}, tedy skoro nic; předpověď hladiny tím není ohrožena."
    return f"{veta}, tedy mírný déšť, který předpověď hladiny podstatně nezmění."


def predpoved_srazek() -> dict:
    """Předpověď srážek v povodí Vltavy, horního Labe a Ohře. Nikdy nevyhodí výjimku: při chybě vrátí ok=False.

    Klíče: ok, chyba (věta nebo None), cas (UTC čas stažení), povodi {vltava/labe/ohre: {mm_24, mm_48, max_bod_48}}
    (mm_* je průměr bodů povodí za příštích 24 a 48 h, max_bod_48 nejvíc z jednoho bodu za 48 h, vše v celých mm)
    a veta (jedna věta pro laika, při chybě totéž co chyba). Výsledek se drží v paměti 30 minut.
    """
    if _pamet["vysledek"] is not None and time.time() < _pamet["do"]:
        return _pamet["vysledek"]
    cas = pd.Timestamp.now(tz="UTC")
    try:
        povodi = _spocti(_stahni(), cas)
        vysledek = dict(ok=True, chyba=None, cas=cas, povodi=povodi, veta=_veta(povodi))
        platnost = PAMET_S
    except requests.RequestException as e:
        chyba = (f"Předpověď srážek se nepodařilo stáhnout z Open-Meteo ({type(e).__name__}). "
                 f"Předpověď hladiny to neovlivňuje, srážky do ní nevstupují.")
        vysledek, platnost = dict(ok=False, chyba=chyba, cas=cas, povodi={}, veta=chyba), PAMET_CHYBY_S
    except Exception as e:  # aplikace má ukázat větu, ne spadnout
        chyba = f"Předpověď srážek nejde spočítat: {e}"
        vysledek, platnost = dict(ok=False, chyba=chyba, cas=cas, povodi={}, veta=chyba), PAMET_CHYBY_S
    _pamet.update(do=time.time() + platnost, vysledek=vysledek)
    return vysledek


if __name__ == "__main__":
    P = predpoved_srazek()
    print(f"staženo {P['cas']:%d. %m. %Y %H:%M} UTC, ok={P['ok']}")
    for k, p in P["povodi"].items():
        print(f"{NAZEV[k]}: 24 h {p['mm_24']} mm, 48 h {p['mm_48']} mm, nejvíc z jednoho bodu {p['max_bod_48']} mm")
    print(P["veta"])
