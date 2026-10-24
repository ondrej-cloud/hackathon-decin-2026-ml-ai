"""Výsledky jako CSV do results/csv/: souhrn metrik všech modelů a hodinové předpovědi na validaci a testu.

python src/export_csv.py
Čte jen results/ (JSON běhů a results/predpovedi/*.parquet), nic netrénuje.
"""
import json

import pandas as pd

from grafy_slajdy import RESULTS

CIL = RESULTS / "csv"
MODELY = ["jako_ted", "ridge", "mlp", "lgbm", "fyzika"]
SLOUPCE = ["mae_povodne", "mae", "chyba_vrcholu", "spa2_predstih_h", "spa2_propasnuto", "spa2_plane_poplachy",
           "spa3_predstih_h", "spa3_propasnuto", "spa3_plane_poplachy"]


def nacti_json(f):
    b = f.read_bytes()
    try:
        return json.loads(b.decode("utf-8"))
    except UnicodeDecodeError:  # starší výsledky z Windows bez UTF-8
        return json.loads(b.decode("cp1250"))


def souhrn():
    """Poslední plný běh každého modelu a varianty (6 kombinací cíle a horizontu) na validaci i testu."""
    radky, videno = [], set()
    for f in sorted(RESULTS.glob("*.json"), reverse=True):
        z = nacti_json(f)
        klic = (z["model"], z["cast"])
        if z.get("rychle") or len(z["vysledky"]) != 6 or klic in videno:
            continue
        videno.add(klic)
        for v in z["vysledky"]:
            radky.append(dict(model=z["model"], cast=z["cast"], cil=v["cil"], horizont=v["horizont"],
                              **{c: v.get(c) for c in SLOUPCE}, autor=z.get("autor"), cas_behu=z.get("cas"),
                              popis=z.get("popis")))
    S = pd.DataFrame(radky).sort_values(["cast", "model", "cil", "horizont"])
    S.to_csv(CIL / "souhrn_modelu.csv", index=False)
    return S


def predpovedi(cast):
    pripona = "_test" if cast == "test" else ""
    P = None
    for m in MODELY:
        d = pd.read_parquet(RESULTS / "predpovedi" / f"{m}{pripona}.parquet").set_index(["cil", "horizont"], append=True)
        P = d.rename(columns={"predpoved": m}) if P is None else P.join(d[["predpoved"]].rename(columns={"predpoved": m}))
    cisla = {c: 1 for c in ["skutecnost", *MODELY]}
    P = P.reset_index()[["cas_vydani", "cil", "horizont", "skutecnost", *MODELY]].round(cisla)
    P.to_csv(CIL / f"predpovedi_{'test' if cast == 'test' else 'validace'}.csv", index=False)
    return P


if __name__ == "__main__":
    CIL.mkdir(exist_ok=True)
    S = souhrn()
    print(f"souhrn_modelu.csv: {S.model.nunique()} modelů a variant, {len(S)} řádků")
    for cast in ("val", "test"):
        P = predpovedi(cast)
        print(f"predpovedi {cast}: {len(P)} řádků, chybí {P[MODELY].isna().mean().round(3).to_dict()}")
        for m in MODELY:
            chyba = (P[m] - P.skutecnost).abs().mean()
            print(f"  {m}: průměrná chyba všech hodin {chyba:.1f} cm")
