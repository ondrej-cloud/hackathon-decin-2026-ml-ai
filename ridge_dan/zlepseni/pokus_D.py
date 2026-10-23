"""Pokus D: vnořený dopředný výběr nových stanic pro Ridge Děčín +24 h v leave-one-flood-out CV (22 povodní).

Pro každý vnější fold k zvlášť: začne s týmovými 98 sloupci a po jedné přidává novou stanici (všech 7 jejích
zpoždění), vždy tu, která nejvíc sníží vnitřní LOFO skóre (21 povodní j ≠ k, model bez mezer k i j); přidá ji jen
při striktním zlepšení. Výběr tedy nikdy nevidí povodeň k. Validace: tentýž výběr jen z tréninku týmového splitu.
python pokus_D.py    → vysledky_D.json (průběžně po každém foldu)
"""
import json
import sys
import time

sys.path.insert(0, r"C:\Users\danie\Documents\hackathon-2026-ridge\ridge_dan\zlepseni")
import lofo as L  # noqa: E402
import numpy as np  # noqa: E402

VYSTUP = L.ZDE / "vysledky_D.json"


def dopredny(skore_fn, zaklad, kandidati):
    """Hladový dopředný výběr: skore_fn(seznam indexů sloupců) → vnitřní chyba. Vrací (pořadí stanic, skóre)."""
    vybrane, sloupce = [], list(zaklad)
    nejlepsi = skore_fn(sloupce)
    prubeh = [round(nejlepsi, 3)]
    while True:
        zbyva = [s for s in kandidati if s not in vybrane]
        if not zbyva:
            break
        sk = {s: skore_fn(sloupce + kandidati[s]) for s in zbyva}
        s = min(sk, key=sk.get)
        if sk[s] >= nejlepsi:
            break
        vybrane.append(s)
        sloupce += kandidati[s]
        nejlepsi = sk[s]
        prubeh.append(round(nejlepsi, 3))
    return vybrane, sloupce, prubeh


def zapis(z):
    VYSTUP.write_text(json.dumps(z, ensure_ascii=False, indent=1, default=float), encoding="utf-8")


if __name__ == "__main__":
    t0 = time.time()
    L.cekej_na_ram(1500)
    A30, y = L.matice(24, nove=L.NOVE)
    sl = list(A30.columns)
    zaklad = list(range(98))
    assert all("_Q_" in c or "_H_" in c for c in sl[:98]) and sl[98].split("_Q_")[0] in L.NOVE
    kandidati = {s: [i for i, c in enumerate(sl) if c.startswith(f"{s}_Q_")] for s in L.NOVE}
    assert all(len(v) == 7 for v in kandidati.values())
    A = A30.to_numpy()
    del A30
    m = L.Motor(A, y, 24)
    print(f"motor hotový ({time.time() - t0:.0f} s)", flush=True)

    p12, _ = m.lofo(sloupce=zaklad)  # = týmový Ridge (standardizace sloupců na podmnožině nezávisí)
    p30, _ = m.lofo()
    pred, vyber = [], {}
    for k, p in enumerate(m.pov):
        t = time.time()
        vybrane, sloupce, prubeh = dopredny(lambda s: m.vnitrni_skore(k, sloupce=s), zaklad, kandidati)
        pred.append(L.predikuj(L.ridge_z_souctu(m.trenink(k), sloupce=sloupce), m.okno(k)[0]))
        vyber[p["nazev"]] = dict(stanice=vybrane, vnitrni_skore=prubeh)
        # vnitřní součty pro fold k už nebudou potřeba, ať drží paměť nízko
        for kk in [x for x in m._vnitrni if x[0] == k]:
            del m._vnitrni[kk]
        print(f"fold {k} {p['nazev']}: {vybrane} vnitřní {prubeh[0]} → {prubeh[-1]} ({time.time() - t:.0f} s)", flush=True)
        zapis(dict(nazev="D_dopredny_vyber", hotovo_foldu=k + 1, vyber_po_foldech=vyber))

    s = L.skore(pred, 24, zaklad_pred=p12)
    cetnost = {st: sum(st in v["stanice"] for v in vyber.values()) for st in L.NOVE}

    # validace: tentýž výběr jen z tréninku týmového splitu (vnitřní LOFO přes jeho 18 povodní)
    X, yf, T = L.zaklad(24)
    c = L.casti("decin", 24).reindex(X.index)
    tr = (c == "train").to_numpy()
    vn = L.vnitrni_val(A, y, tr)
    val_vybrane, val_sloupce, val_prubeh = dopredny(lambda s: L.skore_vnitrni_val(vn, sloupce=s), zaklad, kandidati)
    del vn
    val, _ = L.validace_ridge(A, y, 24, sloupce=val_sloupce)
    val12, _ = L.validace_ridge(A, y, 24, sloupce=zaklad)
    val30, _ = L.validace_ridge(A, y, 24)

    z = dict(nazev="D_dopredny_vyber",
             popis="Ridge Děčín +24 h, týmových 98 vstupů + nové stanice vybrané vnořeným dopředným výběrem (alpha 1)",
             **s, val=val, val_vybrane=val_vybrane, val_vnitrni_prubeh=val_prubeh,
             vyber_po_foldech=vyber, cetnost_vyberu_z_22=dict(sorted(cetnost.items(), key=lambda x: -x[1])),
             reference=dict(ridge_12=L.skore(p12, 24), ridge_30=L.skore(p30, 24, zaklad_pred=p12),
                            val_ridge_12=val12, val_ridge_30=val30),
             sekund=round(time.time() - t0))
    zapis(z)
    print({k: v for k, v in z.items() if k not in ("po_povodnich", "vyber_po_foldech", "reference")}, flush=True)
    print("hotovo", round(time.time() - t0), "s", flush=True)
