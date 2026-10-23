"""Souhrnná tabulka všech variant z vysledky_*.json (zlepseni/) a smesi/vysledky_G.json → markdown na stdout.

python tabulka.py
"""
import json
from pathlib import Path

ZDE = Path(__file__).resolve().parent
SOUBORY = sorted(ZDE.glob("vysledky_*.json")) + sorted((ZDE.parent / "smesi").glob("vysledky_*.json"))


def zaznamy(f):
    z = json.loads(f.read_text(encoding="utf-8"))
    if isinstance(z, dict):
        z = z.get("varianty") or z.get("vysledky") or z.get("zaznamy") or [z]
    for r in z:
        if isinstance(r, dict) and ("lofo" in r or "skore" in r):
            yield f.stem.replace("vysledky_", ""), r


def cislo(x, des=1, znam=False):
    if x is None or x == "":
        return ""
    try:
        return (f"{float(x):+.{des}f}" if znam else f"{float(x):.{des}f}").replace(".", ",")
    except (TypeError, ValueError):
        return str(x)


def val_cislo(r):
    v = r.get("val") or r.get("validace") or {}
    if isinstance(v, (list, tuple)):
        v = v[0] if v else {}
    if isinstance(v, dict):
        return v.get("mae_povodne")
    return v


if __name__ == "__main__":
    print("| Pokus | Varianta | LOFO 22 | rozdíl | zlepšeno z 22 | nejhorší zhoršení | znam. test p | splňuje | val Děčín | začátek | 2006 | plané 2. SPA |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for f in SOUBORY:
        for pokus, r in zaznamy(f):
            s = r.get("skore", r)
            print(f"| {pokus} | {r.get('nazev', '')} | {cislo(s.get('lofo'), 2)} | {cislo(s.get('rozdil'), 2, True)} | "
                  f"{s.get('zlepseno', '')} | {cislo(s.get('nejhorsi_zhorseni'), 1, True)} | {cislo(s.get('znamenkovy_p'), 3)} | "
                  f"{'ano' if s.get('splnuje') else 'ne' if 'splnuje' in s else ''} | {cislo(val_cislo(r))} | "
                  f"{cislo(s.get('zacatek'))} | {cislo(s.get('povoden_2006'))} | {s.get('spa2_plane', '')} |")
