"""Síť (LOFO předpovědi ze session se sítí, hackathon-2026-sit/sit_dan/lofo/) a směsi se sítí, pevné váhy 0,5.

Řádky sítě se ověří proti oknům lofo.povodne_lofo(24) (stejné časy v každém foldu), jinak skript skončí chybou.
G5 = 0,5·Ridge 30 + 0,5·síť (+18 stanic), G6 = 0,5·Ridge 12 + 0,5·síť (beze změny). Nic se nevybírá.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import lofo as L  # noqa: E402

SIT = Path(r"C:\Users\danie\Documents\hackathon-2026-sit\sit_dan\lofo\sit_lofo_oof.parquet")


def nacti_oof(f):
    d = pd.read_parquet(f)
    return [g.sort_values("cas").pred.to_numpy() for _, g in d.groupby("fold", sort=True)]


if __name__ == "__main__":
    X, y, T = L.zaklad(24)
    pov = L.povodne_lofo(24)
    S = pd.read_parquet(SIT)
    S = S[(S.cil == "decin") & (S.horizont == 24)]
    sit = {}
    for var in ("beze_zmeny", "plus_18_stanic"):
        out = []
        for k, p in enumerate(pov):
            g = S[(S.varianta == var) & (S.fold == k)].sort_values("cas")
            cas = y.index[p["okno"]]
            assert len(g) == len(cas) and (g.cas.to_numpy() == cas.to_numpy()).all(), (var, k, len(g), len(cas))
            assert np.allclose(g.skutecnost.to_numpy(), y[p["okno"]].to_numpy())
            out.append(g.predpoved.to_numpy())
        sit[var] = out
    p12, p30 = nacti_oof("oof/ridge_12.parquet"), nacti_oof("oof/ridge_30.parquet")
    varianty = {"sit_beze_zmeny": sit["beze_zmeny"], "sit_plus_18": sit["plus_18_stanic"],
                "G5_ridge30_plus_sit18": [0.5 * a + 0.5 * b for a, b in zip(p30, sit["plus_18_stanic"])],
                "G6_ridge12_plus_sit12": [0.5 * a + 0.5 * b for a, b in zip(p12, sit["beze_zmeny"])]}
    vysl = []
    for n, pr in varianty.items():
        s = L.skore(pr, 24, p12)
        vysl.append(dict(nazev=n, **s))
        print(n, {k: v for k, v in s.items() if k != "po_povodnich"}, flush=True)
    s = L.skore(sit["plus_18_stanic"], 24, sit["beze_zmeny"])
    vysl.append(dict(nazev="sit_plus_18_proti_sit_beze_zmeny", **s))
    print("síť +18 proti síti beze změny", {k: v for k, v in s.items() if k != "po_povodnich"})
    Path(__file__).with_name("vysledky_G5.json").write_text(json.dumps(vysl, ensure_ascii=False, indent=1), encoding="utf-8")
