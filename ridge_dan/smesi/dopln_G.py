import sys; sys.path.insert(0, r"C:\Users\danie\Documents\hackathon-2026-ridge\ridge_dan\zlepseni"); import lofo as L

import argparse
import json
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd
from experiment_G import ZDE, RIDGE, GRID, cti_pred_2021, validace_pevna, zapis_json, vahy_zapis, cekej_ram, log

SIT = Path(r"C:\Users\danie\Documents\hackathon-2026-sit\sit_dan\lofo")
LGBM = RIDGE / "zlepseni" / "oof" / "lgbm_30.parquet"
METODA = "G1 R12+R30; G2 totéž, striktně vnořená váha; G3 R30+LGBM30; G4 totéž, přibližně vnořená váha; G5 R30+síť; pevné směsi 0,5, váhy po foldech v JSON."
POPIS_CHYBI = {
    "G3": "0,5 Ridge30 + 0,5 LightGBM30 (seed 42); LOFO nespočteno, chybí ověřené předpovědi.",
    "G4": "w Ridge30 + (1−w) LightGBM30; POUZE PŘIBLIŽNĚ vnořené váhy dle ostatních 21 LOFO oken; nespočteno, chybí předpovědi.",
    "G5": "0,5 Ridge30 + 0,5 síť; nespočteno, chybí ověřené LOFO předpovědi sítě.",
}


def cti_oof(cesta, zaklad):
    cti_oof.varianta = None
    if cesta.suffix.lower() == ".parquet":
        d = pd.read_parquet(cesta, filters=[("cas", "<", L.KONEC)])
    else:
        d = pd.read_csv(cesta)
    if "cas" not in d and d.index.name == "cas":
        d = d.reset_index()
    d = d.rename(columns={"predpoved": "pred", "skutecnost": "y"})
    assert {"fold", "cas", "y", "pred"} <= set(d.columns), list(d.columns)
    if "horizont" in d:
        d = d[d.horizont == 24]
    if "cil" in d:
        d = d[d.cil == "decin"]
    if "seed" in d:
        d = d[d.seed == 42]
    if "varianta" in d:
        # Volba předem podle identity týmového modelu, nikoli podle výsledku.
        dostupne = set(d.varianta.dropna().unique())
        varianta = "beze_zmeny" if "beze_zmeny" in dostupne else "plus_18_stanic"
        assert varianta in dostupne, dostupne
        d = d[d.varianta == varianta]
        cti_oof.varianta = varianta
    d["cas"] = pd.to_datetime(d.cas, utc=True)
    assert (d.cas < L.KONEC).all()
    assert set(d.fold.unique()) == set(range(22)), d.fold.unique()
    out = []
    for k in range(22):
        zdroj = d[d.fold == k]
        refer = zaklad[zaklad.fold == k]
        assert zdroj.cas.is_monotonic_increasing and zdroj.cas.is_unique
        pd.testing.assert_index_equal(pd.DatetimeIndex(zdroj.cas).as_unit("ns"), pd.DatetimeIndex(refer.cas).as_unit("ns"), check_names=False)
        np.testing.assert_allclose(zdroj.y.to_numpy(), refer.y.to_numpy(), atol=1e-8, rtol=0)
        assert np.isfinite(zdroj.pred.to_numpy()).all()
        out.append(zdroj.pred.to_numpy(dtype=float))
    assert len(d) == len(zaklad)
    return out


def sestav(final=False):
    if cekej_ram() is None:
        raise RuntimeError("Není volných 1500 MB RAM.")
    vysl = json.loads((ZDE / "vysledky_G.json").read_text(encoding="utf-8"))
    # Při opakování zachovat jen základní výsledky, ostatní vždy z aktuálního zdroje.
    vysl = [r for r in vysl if r["nazev"] in ("G1", "G2")]
    refs = json.loads((ZDE / "reference_G.json").read_text(encoding="utf-8"))
    d = pd.read_parquet(ZDE / "predpovedi_G.parquet")
    assert (d.cas + pd.Timedelta(hours=24) < L.KONEC).all()
    p12 = [d[d.fold == k].ridge12.to_numpy() for k in range(22)]
    p30 = [d[d.fold == k].ridge30.to_numpy() for k in range(22)]
    pov = L.povodne_lofo(24)
    for k in range(22):
        expected = L.zaklad(24)[1].index[pov[k]["okno"]]
        pd.testing.assert_index_equal(pd.DatetimeIndex(d[d.fold == k].cas).as_unit("ns"), expected.as_unit("ns"), check_names=False)
    refs["Ridge12"]["validace"] = validace_pevna("predpovedi_ridge_12_None.parquet")
    refs["Ridge30"]["validace"] = validace_pevna("predpovedi_ridge_30_None.parquet")
    zapis_json("reference_G.json", refs)
    vysl[0]["validace"] = validace_pevna("predpovedi_ridge_12_None.parquet", "predpovedi_ridge_30_None.parquet")
    vysl[0]["validace_zdroj"] = "Hotové týmové val předpovědi, shodný časový index a y; evaluate.vyhodnot, Děčín +24 h."
    val_g3 = validace_pevna("predpovedi_ridge_30_None.parquet", "predpovedi_lgbm_30_42.parquet")

    chyby = []
    def pridej(jmeno, popis, pred, vahy, val=None, **navic):
        vysl.append(dict(nazev=jmeno, popis=popis, skore=L.skore(pred, 24, zaklad_pred=p12),
                         validace=val, vybrane_vahy=vahy, **navic))
    if LGBM.is_file():
        try:
            pg = cti_oof(LGBM, d)
            g3 = [(a + b) / 2 for a, b in zip(p30, pg)]
            pridej("G3", "0,5 Ridge30 + 0,5 LightGBM30 (seed 42); pevná váha.", g3, 0.5,
                   val_g3, zdroj=str(LGBM))
            g4, w4 = [], []
            for k in range(22):
                errs = []
                for j in range(22):
                    if j == k:
                        continue
                    yy = d[d.fold == j].y.to_numpy()
                    errs.append(np.abs(GRID[:, None] * p30[j] + (1 - GRID[:, None]) * pg[j] - yy).mean(axis=1))
                w = float(GRID[np.argmin(np.mean(errs, axis=0))])
                w4.append(w)
                g4.append(w * p30[k] + (1 - w) * pg[k])
            pridej("G4", "w Ridge30 + (1−w) LightGBM30; POUZE PŘIBLIŽNĚ vnořené: váha dle průměru MAE ostatních 21 LOFO oken, jejich modely viděly k v tréninku; mřížka 0:0,1:1, shoda → nižší w.",
                   g4, vahy_zapis(w4, pov), vnoreni="priblizne",
                   vyhrada="Pole skore.splnuje je doslovný výstup L.skore; platí pouze s výhradou úniku při volbě vah, nejde o striktně vnořený důkaz.",
                   poznamka_validace="Val pro laděné směsi zadání nevyžaduje; nehodnoceno.")
            for k in range(22):
                ix = d.index[d.fold == k]
                d.loc[ix, "lgbm30"] = pg[k]
                d.loc[ix, "G3"] = g3[k]
                d.loc[ix, "G4"] = g4[k]
        except Exception as exc:
            chyby.append(f"LightGBM soubor existuje, ale neprošel ověřením: {type(exc).__name__}: {exc}")
    else:
        chyby.append("LOFO LightGBM30 zatím nedodáno.")

    sit_nalez = None
    if SIT.is_dir():
        for cesta in sorted(SIT.rglob("*")):
            if not cesta.is_file() or cesta.suffix.lower() not in (".parquet", ".csv"):
                continue
            # G5 smí použít jen soubor dodaný do místního termínu 00:10.
            if datetime.fromtimestamp(cesta.stat().st_mtime) > datetime(2026, 10, 24, 0, 10):
                continue
            try:
                ps = cti_oof(cesta, d)
                sit_nalez = cesta
                g5 = [(a + b) / 2 for a, b in zip(p30, ps)]
                sit_varianta = cti_oof.varianta
                pridej("G5", f"0,5 Ridge30 + 0,5 týmová síť (varianta {sit_varianta or 'dle dodaného souboru'}, seed 42); pevná váha; předem dána přednost beze_zmeny, jinak dostupná plus_18_stanic, bez výběru dle skóre; ověřeno všech 22 foldů, časů a cílů proti týmovému manifestu.", g5, 0.5,
                       zdroj=str(cesta), varianta_site=sit_varianta, poznamka_validace="Hotové validační předpovědi sítě nebyly zadány.")
                for k in range(22):
                    ix = d.index[d.fold == k]
                    d.loc[ix, "sit"] = ps[k]
                    d.loc[ix, "G5"] = g5[k]
                break
            except Exception as exc:
                chyby.append(f"Síť {cesta.name}: nelze ověřit ({type(exc).__name__}: {exc}).")
    if sit_nalez is None:
        chyby.append(f"V {SIT} nebyly nalezeny použitelné LOFO předpovědi sítě ({datetime.now():%Y-%m-%d %H:%M:%S}).")
    hotove = {r["nazev"] for r in vysl}
    for jmeno in ("G3", "G4", "G5"):
        if jmeno not in hotove:
            vysl.append(dict(nazev=jmeno, popis=POPIS_CHYBI[jmeno],
                             skore=None, validace=val_g3 if jmeno == "G3" else None, vybrane_vahy=0.5 if jmeno in ("G3", "G5") else None,
                             duvod="; ".join(chyby), stav="nedostupne" if final else "ceka"))
    zapis_json("vysledky_G.json", vysl)
    d.to_parquet(ZDE / "predpovedi_G.parquet", index=False)
    zapis_json("stav_G.json", dict(cas=datetime.now().isoformat(), finalni=final, chybi=chyby,
        protokol="2006–2020; před tvorbou vstupů filtr v Parquet; 2021–2025 nepoužito; L.skore beze změn.",
        ram="L.cekej_na_ram(1500), původní čekání; CIM dotaz lokálně nahrazen GlobalMemoryStatusEx kvůli sandboxu.",
        casovy_limit="35 minut od zahájení 23:22, konec nejpozději 23:57; dříve než dodací termíny 00:10/00:12."))
    radky = ["Děčín +24 h; 22 LOFO povodní 2006–2020, test 2021–2025 nepoužit; jednotky cm.",
             METODA,
             "", "| Varianta | LOFO | rozdíl | zlepšeno z 22 | nejhorší zhoršení | splňuje | val |", "|---|---:|---:|---:|---:|---|---:|"]
    for name in ("Ridge12", "Ridge30"):
        s = refs[name]
        radky.append(f"| {name} | {s['lofo']:.2f} | {s.get('rozdil', 0):+.2f} | {s.get('zlepseno', '—')} | {s.get('nejhorsi_zhorseni', 0):.1f} | {'ano' if s.get('splnuje') else '—' if name == 'Ridge12' else 'ne'} | {s['validace']['mae_povodne']:.1f} |")
    for r in vysl:
        s = r["skore"]
        if s is None:
            val = r["validace"]["mae_povodne"] if r["validace"] else "—"
            radky.append(f"| {r['nazev']} | nedodáno | — | — | — | nehodnoceno | {val} |")
            continue
        val = r["validace"]["mae_povodne"] if r["validace"] else None
        radky.append(f"| {r['nazev']} | {s['lofo']:.2f} | {s['rozdil']:+.2f} | {s['zlepseno']} | {s['nejhorsi_zhorseni']:.1f} | {'ano' if s['splnuje'] else 'ne'}{'*' if r['nazev'] == 'G4' else ''} | {val if val is not None else '—'} |")
    radky.append("*G4 je pouze přibližně vnořená: modely ostatních foldů viděly vlastní povodeň k; splnění pravidla platí s touto výhradou.")
    nedokoncene = [r["nazev"] for r in vysl if r["skore"] is None]
    if nedokoncene:
        radky.append("Nedokončeno: " + ", ".join(nedokoncene) + f"; ověřené externí LOFO chybí při kontrole {datetime.now():%H:%M:%S}." + (" Limit 35 minut končí před 00:10/00:12." if final else " Čekání pokračuje v limitu 35 minut."))
    else:
        radky.append("Val = mae_povodne z evaluate.vyhodnot nad hotovými týmovými val předpověďmi; u G2/G4 se nepožaduje.")
    dobre = [r["nazev"] for r in vysl if r["skore"] and r["skore"]["splnuje"] and r["nazev"] != "G4"]
    radky.append("Závěr: " + (", ".join(dobre) + " splňuje stanovené pravidlo." if dobre else "Žádná dostupná striktně hodnocená směs nesplňuje celé stanovené pravidlo."))
    assert 5 <= len(radky) <= 15, len(radky)
    (ZDE / "pokus_G.md").write_text("\n".join(radky) + "\n", encoding="utf-8")
    log(f"Doplnění: hotovo {sorted(hotove)}; chybí {chyby}")
    print("\n".join(radky), flush=True)


def uzavri_pouze_vystupy():
    """Pouze uzavření textu/JSON z již spočtených metrik, bez nového výpočtu."""
    vysl = json.loads((ZDE / "vysledky_G.json").read_text(encoding="utf-8"))
    stav = json.loads((ZDE / "stav_G.json").read_text(encoding="utf-8"))
    stav["cas"] = datetime.now().isoformat()
    stav["finalni"] = True
    stav["posledni_kontrola_zdroju"] = datetime.now().isoformat()
    for r in vysl:
        if r["skore"] is None:
            r["stav"] = "nedostupne_v_limitu"
            r["popis"] = POPIS_CHYBI[r["nazev"]]
            if r["nazev"] == "G4":
                r["vnoreni"] = "priblizne"
            r["duvod"] += f" Poslední kontrola {datetime.now():%Y-%m-%d %H:%M:%S}: ověřené podklady pro tuto variantu stále chybí. Celkový limit 35 minut končí před dodacími termíny 00:10/00:12."
            cesta = SIT / "sit_lofo_oof.parquet" if r["nazev"] == "G5" else LGBM
            if cesta.is_file():
                r["stav"] = "dodano_nevyhodnoceno_ram"
                r["zdroj"] = str(cesta)
                r["duvod"] = f"Soubor dodán ({datetime.fromtimestamp(cesta.stat().st_mtime).isoformat()}), ale doplňovací běh od 23:53 čekal v L.cekej_na_ram(1500); v limitu 35 minut se hodnocení nedokončilo. Shoda foldů tohoto zdroje zatím neověřena."
                r["popis"] = r["popis"].split("; nespočteno")[0] + "; soubor dodán, vyhodnocení nedokončeno kvůli čekání na RAM."
    stav["chybi"] = [r["nazev"] + ": " + r.get("duvod", "") for r in vysl if r["skore"] is None]
    zapis_json("vysledky_G.json", vysl)
    zapis_json("stav_G.json", stav)
    md = (ZDE / "pokus_G.md").read_text(encoding="utf-8")
    radky = md.splitlines()
    radky[1] = METODA
    md = "\n".join(radky) + "\n"
    md = md.replace("Čekání pokračuje v limitu 35 minut.", "Limit 35 minut končí před 00:10/00:12; k poslední kontrole nebyly podklady dodány.")
    md = md.replace("Chybí externí LOFO:", f"Poslední kontrola {datetime.now():%H:%M:%S}; chybí externí LOFO:")
    chybi = [r["nazev"] for r in vysl if r["skore"] is None]
    if chybi:
        radky = md.splitlines()
        for i, line in enumerate(radky):
            if line.startswith(("Nedokončeno:", "Poslední kontrola ")):
                nedodano = [r["nazev"] for r in vysl if r["skore"] is None and r["stav"] != "dodano_nevyhodnoceno_ram"]
                ram = [r["nazev"] for r in vysl if r["skore"] is None and r["stav"] == "dodano_nevyhodnoceno_ram"]
                info = (f"{','.join(nedodano)}: LOFO nedodáno. " if nedodano else "") + (f"{','.join(ram)}: soubor dodán, hodnocení nestihlo čekání na RAM. " if ram else "")
                radky[i] = f"Kontrola {datetime.now():%H:%M:%S}: {info}Limit 35 minut končí před 00:10/00:12."
        for i, line in enumerate(radky):
            if line.startswith("| G5 |") and any(r["nazev"] == "G5" and r.get("stav") == "dodano_nevyhodnoceno_ram" for r in vysl):
                radky[i] = line.replace("nedodáno", "čekání na RAM")
        md = "\n".join(radky) + "\n"
    (ZDE / "pokus_G.md").write_text(md, encoding="utf-8")
    log("Výstupy uzavřeny z již spočtených metrik, bez nového výpočtu.")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--final", action="store_true")
    p.add_argument("--uzavri", action="store_true")
    args = p.parse_args()
    if args.uzavri:
        uzavri_pouze_vystupy()
    else:
        sestav(args.final)
