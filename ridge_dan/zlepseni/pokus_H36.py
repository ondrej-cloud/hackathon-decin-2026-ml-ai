"""Průzkumné doplnění (noc 24. 10.): pevné H12 a H30 (pokus_H.py) v LOFO-CV 22 povodní pro Děčín +36 h, bez ladění.

Podnět: v Ondrově vícenásobné validaci vyšel H30 na 36 h o ~2 cm lépe než Ridge. Tady jen druhý pohled na stejný,
předem zapsaný model; 8 povodní Ondrovy validace je podmnožinou těchto 22, nejde o nezávislé potvrzení.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import psutil  # noqa: E402

import lofo as L  # noqa: E402
from pokus_H import s_utlumem  # noqa: E402

psutil.Process().nice(psutil.ABOVE_NORMAL_PRIORITY_CLASS)  # jinak Windows běh v pozadí odsouvá (PRUBEH 02:56)

if __name__ == "__main__":
    A12, y = L.matice(36)
    p12, _ = L.Motor(A12.to_numpy(), y, 36).lofo()
    out = []
    for nazev, A in (("ridge30_36", L.matice(36, nove=L.NOVE)[0]), ("H12_36", s_utlumem(A12)),
                     ("H30_36", s_utlumem(L.matice(36, nove=L.NOVE)[0]))):
        p, _ = L.Motor(A.to_numpy(), y, 36).lofo()
        val, _ = L.validace_ridge(A.to_numpy(), y, 36)
        out.append(dict(nazev=nazev, sloupcu=A.shape[1], **L.skore(p, 36, p12), val={k: float(v) for k, v in val.items()}))
        print(nazev, {k: v for k, v in out[-1].items() if k not in ("po_povodnich", "val")}, "val", val["mae_povodne"], flush=True)
    Path(__file__).with_name("vysledky_H36.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
