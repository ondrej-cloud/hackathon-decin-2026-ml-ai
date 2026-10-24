"""Živá předpověď pro web: web/data/dnesek.json z operativních dat ČHMÚ, modelu ridge_vse a srážek z Open-Meteo.

python src/dnesek_export.py             zapíše web/data/dnesek.json a vypíše souhrn
python src/dnesek_export.py <cesta>     zapíše jinam (kontrola)

Když ČHMÚ neodpoví, zapíše se JSON s ok=false a větou v "chyba" a v "posledni" zůstane poslední úspěšný
stav, skript neskončí chybou. Token Mapboxu ani .env se tu nepoužívají, stačí internet.
"""
import json
import os
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "app"))

import aktualni  # noqa: E402
import pocasi  # noqa: E402
import predikce  # noqa: E402
from data import CILE, PROTI_PROUDU, SPA  # noqa: E402

MODEL = "ridge_vse"
VYSTUP = ROOT / "web/data/dnesek.json"
TZ = "Europe/Prague"
HISTORIE_H = 72
HORIZONTY = [str(h) for h in predikce.HORIZONTY]
POVINNE = ("ok", "chyba", "vytvoreno_utc", "cas_utc", "cas_cesky", "stari_h", "upozorneni", "model", "stanice",
           "tabulka", "historie", "srazky")
POVINNE_STANICE = ("nazev", "spa", "ted", "stupen", "pred", "stupne", "dolni", "horni", "chmu", "veta")


def _utc(cas):
    return pd.Timestamp(cas).tz_convert("UTC").strftime("%Y-%m-%dT%H:%MZ")


def _cesky_iso(cas):
    return pd.Timestamp(cas).tz_convert(TZ).strftime("%Y-%m-%dT%H:%M")


def _cesky(cas):
    c = pd.Timestamp(cas).tz_convert(TZ)
    return f"{c.day}. {c.month}. {c.year} {c.hour}:{c:%M}"


def _cm(x):
    return None if x is None or pd.isna(x) else int(round(float(x)))


def _rozdel_nazev(nazev):
    """"Praha-Chuchle (Vltava)" -> ("Praha-Chuchle", "Vltava")."""
    stanice, tok = nazev.rsplit(" (", 1)
    return stanice, tok.rstrip(")")


def stanice(P, cil):
    p = P[cil]
    ted, pred = p["ted"], p["predpoved"]
    rozmezi = {h: predikce.interval(MODEL, cil, h, ted, pred[h]) or (None, None) for h in pred}
    return dict(
        nazev=_rozdel_nazev(predikce.NAZEV[cil])[0], spa=list(SPA[cil]), ted=_cm(ted), stupen=int(p["stupen_ted"]),
        pred={str(h): _cm(v) for h, v in pred.items()},
        stupne={str(h): int(s) for h, s in p["stupen"].items()},
        dolni={str(h): _cm(r[0]) for h, r in rozmezi.items()},
        horni={str(h): _cm(r[1]) for h, r in rozmezi.items()},
        chmu={str(h): _cm(v) for h, v in p["chmu"].items()},
        veta=predikce.vysvetleni(cil, 24, ted, pred[24], p["radek"]),
    )


def tabulka(P):
    """Průtoky všech stanic v hodině vydání; u Děčína a Ústí i hladina."""
    radek = P["tabulka"].loc[P["cas_utc"]]
    out = []
    for klic in CILE | PROTI_PROUDU:
        nazev, tok = _rozdel_nazev(predikce.NAZEV[klic])
        r = dict(klic=klic, stanice=nazev, tok=tok, Q=_cm(radek[f"{klic}_Q"]),
                 dopocteno=f"{predikce.NAZEV[klic]}, průtok" in P["dopocteno"])
        if klic in CILE:
            r["H"] = _cm(radek[f"{klic}_H"])
        out.append(r)
    return out


def historie(P):
    """Posledních 72 h: hladiny v cílech a průtok v Praze a Mělníku, pro graf 3 dnů. Chybějící hodiny jsou null."""
    D = P["tabulka"].loc[:P["cas_utc"]].tail(HISTORIE_H)
    sloupce = [f"{k}_H" for k in CILE] + ["praha_Q", "melnik_Q"]
    return {"cas": [_cesky_iso(t) for t in D.index]} | {c: [_cm(v) for v in D[c]] for c in sloupce}


def _vycet(polozky):
    """["Mělník (Labe), průtok", "Nymburk (Labe), průtok"] -> "průtok Mělník (Labe) a Nymburk (Labe)"."""
    skupiny = {}
    for p in polozky:
        stanice, _, velicina = p.rpartition(", ")
        skupiny.setdefault(velicina or "hodnota", []).append(stanice or p)
    return "; ".join(f"{v} {' a '.join(s) if len(s) <= 2 else ', '.join(s)}" for v, s in skupiny.items())


def upozorneni(P):
    """Věty nad vodočtem. Dopočtené stanice se nehlásí jako chybějící, ty má web v poznámce pod tabulkou."""
    vety = [P["upozorneni"]] if P["upozorneni"] else []
    chybi = [c for c in P["chybi"] if c not in P["dopocteno"]]
    if chybi:
        vety.append("ČHMÚ zatím nezveřejnil všechny hodiny, chybí " + _vycet(chybi) + ".")
    if P["dopocteno"]:
        vety.append("Dopočteno z bilance vody (ČHMÚ to operativně nezveřejňuje): " + _vycet(P["dopocteno"]) + ".")
    return vety


def srazky():
    S = pocasi.predpoved_srazek()
    return dict(ok=S["ok"], chyba=S["chyba"], cas_utc=_utc(S["cas"]), veta=S["veta"],
                povodi={k: dict(nazev=pocasi.NAZEV[k], **{x: int(v) for x, v in p.items()})
                        for k, p in S["povodi"].items()})


def _posledni(soubor):
    """Poslední úspěšný stav z minulého běhu, aby web při výpadku ČHMÚ měl co ukázat."""
    try:
        stary = json.loads(soubor.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if stary.get("ok"):
        stary.pop("srazky", None)
        return stary
    return stary.get("posledni")


def sestav(soubor):
    P = aktualni.predpoved_dnes(MODEL)
    out = dict(ok=bool(P["ok"]), chyba=P["chyba"], vytvoreno_utc=_utc(pd.Timestamp.now(tz="UTC")),
               model=dict(nazev=MODEL, ucen="2006–2025", vstupu=98, horizonty=list(predikce.HORIZONTY)))
    if P["ok"]:
        out.update(cas_utc=_utc(P["cas_utc"]), cas_cesky=_cesky(P["cas_utc"]), cas=_cesky_iso(P["cas_utc"]),
                   stari_h=float(P["stari_h"]), upozorneni=upozorneni(P), chybi=P["chybi"], dopocteno=P["dopocteno"],
                   stanice={cil: stanice(P, cil) for cil in CILE}, tabulka=tabulka(P), historie=historie(P))
    else:
        out.update(cas_utc=None, cas_cesky=None, cas=None, stari_h=None, upozorneni=[P["chyba"]], chybi=[],
                   dopocteno=[], stanice={}, tabulka=[], historie=None, posledni=_posledni(soubor))
    out["srazky"] = srazky()
    return out


def zkontroluj(out):
    chybi = [k for k in POVINNE if k not in out]
    if out["ok"]:
        for cil in CILE:
            s = out["stanice"][cil]
            chybi += [f"stanice.{cil}.{k}" for k in POVINNE_STANICE if k not in s]
            chybi += [f"stanice.{cil}.{k}.{h}" for k in ("pred", "dolni", "horni", "chmu", "stupne")
                      for h in HORIZONTY if h not in s.get(k, {})]
            chybi += [f"stanice.{cil}.pred.{h} je null" for h in HORIZONTY if s["pred"].get(h) is None]
        if len(out["tabulka"]) != len(CILE | PROTI_PROUDU):
            chybi.append("tabulka nemá všech 12 stanic")
    if chybi:
        raise ValueError("výstup nemá pole: " + ", ".join(chybi))


def uloz(out, soubor):
    soubor.parent.mkdir(parents=True, exist_ok=True)
    docasny = soubor.with_suffix(".json.tmp")
    docasny.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    os.replace(docasny, soubor)


if __name__ == "__main__":
    soubor = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else VYSTUP
    out = sestav(soubor)
    zkontroluj(out)
    uloz(out, soubor)
    print(f"{soubor}: {soubor.stat().st_size / 1e3:.1f} kB, ok={out['ok']}")
    if out["ok"]:
        print(f"vydáno {out['cas_cesky']} (stáří {out['stari_h']} h), upozornění: {out['upozorneni'] or 'žádné'}")
        for cil, s in out["stanice"].items():
            print(f"{s['nazev']}: teď {s['ted']} cm ({predikce.STUPNE[s['stupen']]}); "
                  + ", ".join(f"za {h} h {s['pred'][h]} cm ({s['dolni'][h]} až {s['horni'][h]}, "
                              f"ČHMÚ {s['chmu'][h] if s['chmu'][h] is not None else '?'})" for h in HORIZONTY))
    else:
        print("CHYBA:", out["chyba"], "| poslední stav z", (out.get("posledni") or {}).get("cas_cesky"))
    print("srážky:", out["srazky"]["veta"])
