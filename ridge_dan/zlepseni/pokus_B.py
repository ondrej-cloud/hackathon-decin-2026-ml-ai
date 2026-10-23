"""Pokus B: Ridge s 30 stanicemi, nové sloupce po standardizaci × f, tj. penalizace alpha/f² jen pro ně.

f se vybírá vnořeně (vnitřní LOFO přes 21 povodní bez povodně k), diagnosticky i LOFO pro každé pevné f.
Násobení před StandardScalerem by škálování zrušilo, proto se násobí až standardizované sloupce (= násobek penalizace).
"""
import json
import sys
import time

sys.path.insert(0, r"C:\Users\danie\Documents\hackathon-2026-ridge\ridge_dan\zlepseni")
import numpy as np  # noqa: E402

import lofo as L  # noqa: E402

MRIZKA = (1.0, 0.75, 0.5, 0.25, 0.1, 0.05, 0.02, 0.01)
VYSTUP = L.ZDE / "vysledky_B.json"


def penalizace(sloupce, f):
    nove = np.array([any(c.startswith(f"{s}_") for s in L.NOVE) for c in sloupce])
    return np.where(nove, 1 / f ** 2, 1.0)


if __name__ == "__main__":
    t0 = time.time()
    L.cekej_na_ram(1500, max_min=2)  # první běh čekal 20 min a pak spadl bez hlášky, termín 00:05
    A12, y = L.matice(24)
    A30, _ = L.matice(24, nove=L.NOVE)
    sl = list(A30.columns)
    assert sl[:98] == list(A12.columns) and sum(penalizace(sl, 0.5) > 1) == 126
    pen = {f: penalizace(sl, f) for f in MRIZKA}

    m12 = L.Motor(A12.to_numpy(), y, 24)
    p12, _ = m12.lofo()
    del m12
    A = A30.to_numpy()
    m = L.Motor(A, y, 24)
    zaznamy = []

    # diagnosticky: pevné f
    for f in MRIZKA:
        p, _ = m.lofo(pen=pen[f])
        s = L.skore(p, 24, zaklad_pred=p12)
        zaznamy.append(dict(nazev=f"B_pevne_f{f}", popis=f"Ridge 30, nové sloupce × {f} po standardizaci (pevně, jen diagnostika)",
                            **s))
        print(f"pevné f={f}: LOFO {s['lofo']}, rozdíl {s['rozdil']}, zlepšeno {s['zlepseno']}/22", flush=True)
        VYSTUP.write_text(json.dumps(zaznamy, ensure_ascii=False, indent=1, default=float), encoding="utf-8")

    # hlavní varianta: f vnořeně
    vybrane = {}

    def vyber(motor, k):
        sk = {f: motor.vnitrni_skore(k, pen=pen[f]) for f in MRIZKA}
        f = min(sk, key=sk.get)
        vybrane[motor.pov[k]["nazev"]] = f
        return dict(pen=pen[f])

    p, _ = m.lofo(vyber=vyber)
    s = L.skore(p, 24, zaklad_pred=p12)
    zaznamy.append(dict(nazev="B", popis="Ridge 30, nové sloupce × f po standardizaci, f vnořeně z vnitřního LOFO",
                        **s, vybrane_f=vybrane))
    VYSTUP.write_text(json.dumps(zaznamy, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    print(f"B vnořené: LOFO {s['lofo']}, rozdíl {s['rozdil']}, zlepšeno {s['zlepseno']}/22, vybrané f {vybrane}", flush=True)

    # validace: výběr f vnořeně jen z tréninku týmového splitu (vnitřní LOFO přes 18 tréninkových povodní)
    vybrane_val = {}

    def vyber_val(A_, y_, tr, h):
        vn = L.vnitrni_val(A_, y_, tr, h)
        sk = {f: L.skore_vnitrni_val(vn, pen=pen[f]) for f in MRIZKA}
        vybrane_val["f"] = min(sk, key=sk.get)
        vybrane_val["vnitrni"] = {str(k): round(v, 3) for k, v in sk.items()}
        return dict(pen=pen[vybrane_val["f"]])

    val, _ = L.validace_ridge(A, y, 24, vyber_val=vyber_val)
    zaznamy[-1] |= dict(val={k: float(v) for k, v in val.items()}, vybrane_f_val=vybrane_val)
    VYSTUP.write_text(json.dumps(zaznamy, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    # validace i pro pevná f (diagnostika)
    for z in zaznamy[:-1]:
        f = float(z["nazev"].split("_f")[1])
        v, _ = L.validace_ridge(A, y, 24, pen=pen[f])
        z["val"] = {k: float(x) for k, x in v.items()}
    VYSTUP.write_text(json.dumps(zaznamy, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    print("val B", zaznamy[-1]["val"], "f_val", vybrane_val["f"], f"({time.time() - t0:.0f} s)")
