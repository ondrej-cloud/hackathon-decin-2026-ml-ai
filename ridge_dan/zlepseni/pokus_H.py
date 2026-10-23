"""Pokus H (doplňkový, předem zapsaný v PRUBEH 23:37): ukazatel útlumu vlny v nivě z týmových stanic.

Rozdíl průtoku po proudu a součtu přítoků nad ním (m³/s, bez odmocniny): když je záporný, voda se drží v nivě
(rozbor A, 2006). Tři úseky × zpoždění 0/6/12/24 h = 12 sloupců. H12 = týmový Ridge + ukazatel, H30 = Ridge 30 +
ukazatel. Alpha 1, nic se nevybírá. LOFO 22 povodní, skóre proti týmovému Ridge.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import lofo as L  # noqa: E402

USEKY = {"polabi": ("kostelec", ["nymburk", "jizera"]), "melnik": ("melnik", ["vranany", "kostelec"]),
         "usti": ("usti", ["melnik", "louny"])}


def s_utlumem(A):
    _, _, T = L.zaklad(24)
    extra = {f"utlum_{u}_{z}": (T[f"{d}_Q"] - sum(T[f"{n}_Q"] for n in nad)).shift(z)
             for u, (d, nad) in USEKY.items() for z in (0, 6, 12, 24)}
    E = pd.DataFrame(extra).reindex(A.index)
    assert E.notna().all().all()
    return pd.concat([A, E.astype("float32")], axis=1)


if __name__ == "__main__":
    L.cekej_na_ram(1200)
    A12, y = L.matice(24)
    m12 = L.Motor(A12.to_numpy(), y, 24)
    p12, _ = m12.lofo()
    out = []
    for nazev, A in (("H12_tym_plus_utlum", s_utlumem(A12)), ("H30_ridge30_plus_utlum", s_utlumem(L.matice(24, nove=L.NOVE)[0]))):
        m = L.Motor(A.to_numpy(), y, 24)
        p, _ = m.lofo()
        val, _ = L.validace_ridge(A.to_numpy(), y, 24)
        out.append(dict(nazev=nazev, sloupcu=A.shape[1], **L.skore(p, 24, p12), val={k: float(v) for k, v in val.items()}))
        del m
        print(nazev, {k: v for k, v in out[-1].items() if k not in ("po_povodnich",)}, flush=True)
    Path(__file__).with_name("vysledky_H.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
