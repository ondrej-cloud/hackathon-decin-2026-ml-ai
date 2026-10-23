"""Přehled pokusů z vysledky/pokusy.jsonl: python prehled.py [filtr názvu]"""
import json
import sys
from pathlib import Path

import pandas as pd

LOG = Path(__file__).resolve().parent / "vysledky/pokusy.jsonl"
radky = []
for r in LOG.read_text(encoding="utf-8").splitlines():
    z = json.loads(r)
    v = z.get("val") or {}
    radky.append(dict(cas=z["cas"][11:16], nazev=z["nazev"], sloupcu=z["sloupcu"], alpha=z["alpha"],
                      cv_povodne=z["cv_povodne"], cv_vzestup=z["cv_vzestup"], cv_bias_vz=z["cv_bias_vzestup"],
                      cv_mae=z["cv_mae"], val_povodne=v.get("mae_povodne"), val_n=z.get("poradi_nahlednuti_val")))
df = pd.DataFrame(radky)
if len(sys.argv) > 1:
    df = df[df.nazev.str.contains(sys.argv[1])]
print(df.to_string(index=False))
