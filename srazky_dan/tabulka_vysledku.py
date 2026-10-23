"""Markdown tabulka z vysledky/srazky.jsonl: model × (beze změny / + srážky / rozdíl) a verdikt.

python tabulka_vysledku.py [JSONL] [-o soubor.md]

Bere vždy nejnovější záznam pro model × sada × varianta × seed × část a jen záznamy se stejným otiskem srážkové
tabulky jako ten nejnovější. U LightGBM průměr přes seedy ± směrodatná odchylka (u rozdílu odchylka rozdílů po seedech).
Verdikt: zlepšení i zhoršení se počítá až od 1 cm, zvlášť na CV povodně a na VAL Děčín +24 h (mae_povodne).
"""
import argparse
import json
import statistics
from pathlib import Path

ZDE = Path(__file__).resolve().parent
PRAH = 1.0
MODELY = {"ridge_tym": "Ridge týmový", "ridge_dan": "Ridge Danův", "lgbm": "LightGBM"}
# (název sloupce, klíč, desetinná místa)
SLOUPCE = [("CV povodně", "cv_povodne", 2), ("CV začátek vzestupu", "cv_zacatek", 2), ("CV 8/2010", "cv_2010_08", 1),
           ("VAL Děčín +24 povodně", "val_d24", 1), ("VAL průměr 6 kombinací", "val_prumer", 2),
           ("VAL začátek vzestupu", "val_zacatek", 1), ("VAL 9/2010", "val_2010", 1), ("VAL 4/2006", "val_2006", 1),
           ("plané 2. SPA", "spa2_plane", 0), ("plané 3. SPA", "spa3_plane", 0),
           ("propásnuto 2. SPA", "spa2_propasnuto", 0), ("propásnuto 3. SPA", "spa3_propasnuto", 0)]


def nejnovejsi(zaznamy):
    posledni = {}
    for z in zaznamy:
        posledni[(z["model"], z["sada"], z["varianta"], z["seed"], z["cast"])] = z
    out = {}
    for (model, sada, *_), z in posledni.items():
        out.setdefault((model, sada), []).append(z)
    # jen záznamy se stejnou srážkovou tabulkou jako ten nejnovější
    for k, zz in out.items():
        otisk = max(zz, key=lambda z: z["cas"])["srazky"]
        out[k] = [z for z in zz if z["srazky"] == otisk]
    return out


def cisla(cv, val):
    """Čísla do tabulky z CV a validačního záznamu jedné varianty a seedu."""
    d = val["decin24"]
    c2010 = [v for k, v in cv["cv_udalosti"].items() if k.startswith("2010-08")]
    return dict(cv_povodne=cv["cv_povodne"], cv_zacatek=cv["cv_zacatek"], cv_2010_08=c2010[0] if c2010 else None,
                val_d24=d["mae_povodne"], val_prumer=val["prumer_povodne"] if val["kombinaci"] == 6 else None,
                val_zacatek=d["mae_zacatek"], val_2010=d["mae_2010_09"], val_2006=d["mae_2006"],
                spa2_plane=val["spa2_plane"], spa3_plane=val["spa3_plane"],
                spa2_propasnuto=val["spa2_propasnuto"], spa3_propasnuto=val["spa3_propasnuto"])


def cislo(x, mista, znamenko=False):
    if x is None:
        return "–"
    s = f"{x:+.{mista}f}" if znamenko else f"{x:.{mista}f}"
    return s.replace("-", "−").replace(".", ",")


def bunka(hodnoty, mista, znamenko=False):
    """Jedna hodnota, nebo průměr ± směrodatná odchylka přes seedy (počty poplachů pak na desetiny)."""
    if any(h is None for h in hodnoty):
        return "–"
    if len(hodnoty) > 1:
        mista = max(mista, 1)
    s = cislo(statistics.mean(hodnoty), mista, znamenko)
    return s if len(hodnoty) == 1 else f"{s} ± {cislo(statistics.stdev(hodnoty), mista)}"


def soud(rozdil):
    return "lepší" if rozdil <= -PRAH else "horší" if rozdil >= PRAH else "beze změny"


def verdikt(d_cv, d_val):
    a, b = soud(d_cv), soud(d_val)
    return a if a == b else f"CV {a}, VAL {b}"


def tabulka(zaznamy, sada):
    radky = [f"| model | varianta | {' | '.join(n for n, _, _ in SLOUPCE)} | verdikt |",
             "|" + "---|" * (len(SLOUPCE) + 3)]
    info = []
    for model, nazev in MODELY.items():
        zz = zaznamy.get((model, sada))
        if not zz:
            continue
        z = {(x["varianta"], x["seed"], x["cast"]): x for x in zz}
        seedy = sorted({s for v, s, _ in z if v == "bez" and (v, s, "cv") in z and (v, s, "val") in z
                        and ("srazky", s, "cv") in z and ("srazky", s, "val") in z}, key=str)
        if not seedy:
            continue
        bez = [cisla(z[("bez", s, "cv")], z[("bez", s, "val")]) for s in seedy]
        se = [cisla(z[("srazky", s, "cv")], z[("srazky", s, "val")]) for s in seedy]
        rozdil = [{k: None if b[k] is None else a[k] - b[k] for k in b} for a, b in zip(se, bez)]
        d_cv = statistics.mean(r["cv_povodne"] for r in rozdil)
        d_val = statistics.mean(r["val_d24"] for r in rozdil)
        for jmeno, hodnoty, zn in (("beze změny", bez, False), ("+ srážky", se, False), ("rozdíl", rozdil, True)):
            bunky = [bunka([h[k] for h in hodnoty], m, zn) for _, k, m in SLOUPCE]
            konec = f"**{verdikt(d_cv, d_val)}**" if jmeno == "rozdíl" else ""
            radky.append(f"| {nazev if jmeno == 'beze změny' else ''} | {jmeno} | {' | '.join(bunky)} | {konec} |")
        v = z[("srazky", seedy[0], "val")]
        info.append(f"{nazev}: seedy {', '.join(str(s or '–') for s in seedy)}, srážky {v['srazky']}, řádky train/val Děčín +24 "
                    f"{v['n_train']}/{v['n_val']}, CV train {z[('srazky', seedy[0], 'cv')]['n_train']}, "
                    f"validace {v['kombinaci']} kombinací, nejnovější {max(x['cas'] for x in zz)}")
    return radky, info


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("jsonl", nargs="?", type=Path, default=ZDE / "vysledky/srazky.jsonl")
    p.add_argument("-o", type=Path)
    a = p.parse_args()
    with open(a.jsonl, encoding="utf-8") as f:
        zaznamy = nejnovejsi(json.loads(r) for r in f if r.strip())
    out = []
    for sada, popis in (("hlavni", "hlavní sada (blizko + dal, 10 sloupců), podle ní verdikt"),
                        ("povodi", "citlivostní sada (blizko + dílčí povodí)")):
        radky, info = tabulka(zaznamy, sada)
        if len(radky) > 2:
            out += [f"### Srážky: {popis}", "", *radky, "", *[f"- {i}" for i in info], ""]
    out += [f"Rozdíl = + srážky − beze změny (záporný = menší chyba). Verdikt: lepší / horší od {cislo(PRAH, 0)} cm, "
            "zvlášť CV povodně a VAL Děčín +24 povodně; když se liší, vypíšou se oba. Plané a propásnuté poplachy "
            "jsou součty přes kombinace z validace (u Danova Ridge jen Děčín +24 h)."]
    text = "\n".join(out)
    print(text)
    if a.o:
        a.o.write_text(text + "\n", encoding="utf-8")
