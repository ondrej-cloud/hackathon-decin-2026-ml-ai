"""Pokus C: místo 126 sloupců jednotlivých nových stanic jen součty po 8 dílčích povodích (56 sloupců).

C1: součet odmocnin průtoků stanic skupiny; C2: odmocnina součtu průtoků skupiny. Alpha 1, nic se nevybírá.
"""
import json
import sys

sys.path.insert(0, r"C:\Users\danie\Documents\hackathon-2026-ridge\ridge_dan\zlepseni")
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import lofo as L  # noqa: E402

H = 24


def matice_c2():
    A12, y = L.matice(H)
    _, _, T = L.zaklad(H)
    extra = {}
    for g, st in L.SKUPINY.items():
        q = sum(T[f"{s}_Q"].clip(lower=0) for s in st)
        for z in L.ZPOZDENI_Q:
            extra[f"sqrtsum_{g}_Q_{z}"] = np.sqrt(q).shift(z)
    E = pd.DataFrame(extra).reindex(A12.index)
    assert E.notna().all().all(), "díra ve vstupech"
    return pd.concat([A12, E.astype("float32")], axis=1), y


def zaznam(nazev, popis, A, y, p12):
    m = L.Motor(A.to_numpy(), y, H)
    pred, _ = m.lofo()
    s = L.skore(pred, H, zaklad_pred=p12)
    v, _ = L.validace_ridge(A.to_numpy(), y, H)
    print(nazev, A.shape[1], s["lofo"], s.get("rozdil"), s.get("zlepseno"), s.get("nejhorsi_zhorseni"),
          s.get("splnuje"), "val", v["mae_povodne"], flush=True)
    return dict(nazev=nazev, popis=popis, sloupcu=A.shape[1], **s, val={k: float(x) for k, x in v.items()})


if __name__ == "__main__":
    L.cekej_na_ram(1500)
    A12, y = L.matice(H)
    m12 = L.Motor(A12.to_numpy(), y, H)
    p12, _ = m12.lofo()
    out = [zaznam("ridge_12", "týmový Ridge (základ)", A12, y, None)]
    del m12
    A, _ = L.matice(H, nove=L.NOVE)
    out.append(zaznam("ridge_30", "Ridge + 18 nových stanic jednotlivě (126 sloupců)", A, y, p12))
    del A
    A, _ = L.matice(H, soucty=L.SKUPINY)
    out.append(zaznam("C1_soucet_odmocnin", "tým + součet odmocnin průtoků 8 skupin (56 sloupců)", A, y, p12))
    del A
    A, _ = matice_c2()
    out.append(zaznam("C2_odmocnina_souctu", "tým + odmocnina součtu průtoků 8 skupin (56 sloupců)", A, y, p12))
    (L.ZDE / "vysledky_C.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
