"""Simulace zpoždění vstupů v provozu na LOFO-CV 22 povodní (Děčín), bez ladění.

Model je natrénovaný normálně (čerstvá data). V provozu ale stanice s se zpožděním d_s hodin nemá hodnoty za
posledních d_s hodin a aplikace místo nich dosadí poslední známou: vstup „před z hodinami“ = hodnota v čase
t − max(z, d_s). Nic z budoucnosti: vždy jen hodnoty z času ≤ t − d_s ≤ t. Náprava („model ví o zpoždění“):
natrénovat na vstupech, které jsou celé starší o d (vstup v čase t = vstup v čase t − d), a hodnotit stejně.

python zpozdeni_simulace.py                     rovnoměrná zpoždění 1/2/3/6 h, náprava, citlivost na jednu stanici
python zpozdeni_simulace.py zpozdeni.json       jen naměřená zpoždění {stanice: hodiny} (provoz/zpozdeni.py)
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import psutil

ZDE = Path(__file__).resolve().parent
sys.path.insert(0, str(ZDE.parent / "zlepseni"))
import lofo as L  # noqa: E402

psutil.Process().nice(psutil.ABOVE_NORMAL_PRIORITY_CLASS)  # jinak Windows běh při souběhu odsouvá (PRUBEH 02:56)

MODELY = {"tym_ridge_24": (24, ()), "ridge30_24": (24, L.NOVE), "tym_ridge_36": (36, ()), "ridge30_36": (36, L.NOVE)}


def rozloz(sloupec):
    s, v, z = sloupec.rsplit("_", 2)
    return s, v, int(z)


def matice_se_zpozdenim(A0, zpozdeni, posun_vse=0):
    """Stejné sloupce a řádky jako A0 (lofo.matice), ale stanice s má poslední hodnotu z t − zpozdeni[s].
    posun_vse: celá matice starší o tolik hodin (model, který o zpoždění ví)."""
    _, _, T = L.zaklad(24)
    out = {}
    for c in A0.columns:
        s, v, z = rozloz(c)
        rada = T[f"{s}_{v}"] if v == "H" else np.sqrt(T[f"{s}_Q"].clip(lower=0))
        # díra (led v Děčíně 2/2006) se posunem může dostat do platných řádků: vyplní se starší známou hodnotou
        out[c] = rada.shift(max(z, zpozdeni.get(s, 0)) + posun_vse).ffill()
    M = pd.DataFrame(out).reindex(A0.index)
    assert M.notna().all().all()
    return M.astype("float32")


def predikce(m, A_eval):
    """Model natrénovaný na čerstvých vstupech (Motor nad A0), předpovědi oken z jiné matice vstupů."""
    A_eval = A_eval.to_numpy()
    return [L.predikuj(L.ridge_z_souctu(m.trenink(k)), A_eval[p["okno"]]) for k, p in enumerate(m.pov)]


if __name__ == "__main__":
    namereno = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")) if len(sys.argv) > 1 else {}
    vysl = []
    for nazev, (h, nove) in MODELY.items():
        A0, y = L.matice(h, nove=nove)
        assert np.array_equal(matice_se_zpozdenim(A0, {}).to_numpy(), A0.to_numpy()), "bez zpoždění musí přesně sedět s lofo.matice"
        m = L.Motor(A0.to_numpy(), y, h)
        p0, _ = m.lofo()
        z0 = L.skore(p0, h)
        stanice = sorted({rozloz(c)[0] for c in A0.columns})
        scenare = {f"vse_{d}h": {s: d for s in stanice} for d in (1, 2, 3, 6)}
        if namereno:
            scenare = {"namerene": {s: namereno.get(s, 0) for s in stanice}}
        for sc, zp in scenare.items():
            p = predikce(m, matice_se_zpozdenim(A0, zp))
            s = L.skore(p, h, p0)
            vysl.append(dict(model=nazev, scenar=sc, lofo=s["lofo"], rozdil_proti_cerstvym=s["rozdil"],
                             zhorseno=s["zhorseno"], nejhorsi=s["nejhorsi_zhorseni"], zacatek=s["zacatek"],
                             zacatek_cerstve=z0["zacatek"], lofo_cerstve=z0["lofo"]))
            print(vysl[-1], flush=True)
            if sc.startswith("vse_"):  # náprava: model natrénovaný na stejně starých vstupech
                d = int(sc[4:-1])
                An = matice_se_zpozdenim(A0, {}, posun_vse=d)
                pn, _ = L.Motor(An.to_numpy(), y, h).lofo()
                sn = L.skore(pn, h, p0)
                vysl.append(dict(model=nazev, scenar=f"{sc}_model_vi", lofo=sn["lofo"], rozdil_proti_cerstvym=sn["rozdil"],
                                 zhorseno=sn["zhorseno"], nejhorsi=sn["nejhorsi_zhorseni"], zacatek=sn["zacatek"],
                                 zacatek_cerstve=z0["zacatek"], lofo_cerstve=z0["lofo"]))
                print(vysl[-1], flush=True)
        if nazev == "ridge30_24" and not namereno:  # citlivost: jediná stanice o 6 h starší, ostatní čerstvé
            for s in stanice:
                p = predikce(m, matice_se_zpozdenim(A0, {s: 6}))
                sc = L.skore(p, h, p0)
                vysl.append(dict(model=nazev, scenar=f"jen_{s}_6h", lofo=sc["lofo"], rozdil_proti_cerstvym=sc["rozdil"],
                                 zhorseno=sc["zhorseno"], nejhorsi=sc["nejhorsi_zhorseni"], zacatek=sc["zacatek"],
                                 zacatek_cerstve=z0["zacatek"], lofo_cerstve=z0["lofo"]))
        del m
    pd.DataFrame(vysl).to_csv(ZDE / ("zpozdeni_namerene.csv" if namereno else "zpozdeni_vysledky.csv"), index=False,
                              encoding="utf-8")
