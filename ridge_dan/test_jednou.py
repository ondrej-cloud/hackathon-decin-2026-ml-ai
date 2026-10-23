"""Jednorázový test 2021–2025 finálního modelu (model_ridge.FINALNI) proti týmovému Ridge a „jako teď“.

python test_jednou.py    podruhé se nespustí (značka vysledky/TEST_HOTOVO.json)

Stejně jako `porovnej.py --test`: všechny modely se trénují na všem do konce 2020 (evaluate.casti(finalni=True)),
test jsou roky 2021–2025, srovnání na stejných řádcích (průnik).
"""
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

import data_ridge
import hodnoceni as Hd
import model_ridge
import pokus
from priznaky import tym_priznaky

ZDE = Path(__file__).resolve().parent
ZNACKA = ZDE / "vysledky/TEST_HOTOVO.json"

if __name__ == "__main__":
    # značka se zakládá výhradně (mód "x") ještě před výpočtem: druhé ani souběžné spuštění neprojde,
    # a když výpočet spadne, test se znovu nepustí bez ručního zásahu (a záznamu proč)
    try:
        with open(ZNACKA, "x", encoding="utf-8") as f:
            f.write(json.dumps(dict(start=datetime.now().isoformat(timespec="seconds"), model=model_ridge.FINALNI,
                                    alpha=model_ridge.ALPHA, otisk=pokus.otisk()), ensure_ascii=False, default=str))
    except FileExistsError:
        sys.exit(f"Test už proběhl nebo běží ({ZNACKA.read_text(encoding='utf-8')[:300]}), podruhé ne.")
    T = data_ridge.nacti()
    H = T["decin_H"]

    m, X, y, c = model_ridge.trenink(T, finalni=True)
    te = c == "test"
    p_moje = pd.Series(m.predict(X[te]), index=X.index[te])

    Xt, yt, Lt = tym_priznaky(T, "decin", 24)
    ct = Hd.casti(H, 24, max(Lt, 36), finalni=True).reindex(Xt.index)
    mt = pokus.Predpoved(1.0, False, None).fit(Xt[ct == "train"], yt[ct == "train"])
    p_tym = pd.Series(mt.predict(Xt[ct == "test"]), index=Xt.index[ct == "test"])

    spol = p_moje.index.intersection(p_tym.index)
    assert np.isfinite(p_moje[spol]).all() and np.isfinite(p_tym[spol]).all()
    yy = y[spol]
    out = dict(cas=datetime.now().isoformat(timespec="seconds"), model=model_ridge.FINALNI, alpha=model_ridge.ALPHA,
               otisk_evaluate=Hd.OTISK_EVALUATE, radku=len(spol), radku_moje=len(p_moje), radku_tym=len(p_tym),
               moje=Hd.metriky(yy, p_moje[spol], H, "decin", 24),
               tym=Hd.metriky(yy, p_tym[spol], H, "decin", 24),
               jako_ted=Hd.metriky(yy, Xt.loc[spol, "decin_H_0"], H, "decin", 24))
    f = ZDE / f"vysledky/test_{datetime.now():%Y-%m-%d_%H%M%S}.json"
    f.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    with open(ZNACKA, "a", encoding="utf-8") as z:
        z.write("\n" + json.dumps(dict(hotovo=out["cas"], soubor=f.name), ensure_ascii=False))
    pd.DataFrame({"skutecnost": yy, "moje": p_moje[spol], "tym": p_tym[spol],
                  "jako_ted": Xt.loc[spol, "decin_H_0"]}).to_parquet(ZDE / "vysledky/test_predpovedi.parquet")
    for k in ("moje", "tym", "jako_ted"):
        r = out[k]
        print(f"{k:9s} povodně {r['mae_povodne']:5.1f}  celkem {r['mae']:4.1f}  vzestup {r['mae_vzestup']:5.1f}  "
              f"začátek {r['mae_zacatek']:5.1f}  2. SPA předstih {r['spa2_predstih_h']} h, propásnuto "
              f"{r['spa2_propasnuto']}, plané {r['spa2_plane_poplachy']}")
    print("uloženo", f.relative_to(ZDE))
