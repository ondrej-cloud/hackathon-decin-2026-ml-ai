"""Myšlenkový pokus: lineární regrese zná skutečný déšť na 1, 2 a 3 dny dopředu, jako by předpověď srážek byla dokonalá.

Je to horní mez pro nápad „předpovíme déšť a dáme ho do modelu“: žádná skutečná předpověď nebude lepší než skutečný déšť.
Do modelu se nesmí, je to únik z budoucnosti. Jen validace.

python src/pokus_dest_dopredu.py
"""
import pandas as pd

from evaluate import casti, vyhodnot
from features import tabulka
from meteo import STANICE, denni
from models import ridge


def dest_dopredu():
    hodiny = pd.date_range("2006-01-01", "2025-12-31 23:00", freq="h", tz="UTC")
    # srážkový den D je od D 06:00 do D+1 06:00 UTC, v čase t běží den (t − 6 h).normalize()
    den = (hodiny - pd.Timedelta(hours=6)).normalize()
    M = {}
    for vetev, stanice in STANICE.items():
        sra = pd.concat({w: denni(w)["SRA"] for w in stanice}, axis=1).mean(axis=1)
        for dny in (1, 2, 3):
            # dnešní srážkový den a dny−1 dalších, i ta část dnešního dne, která už spadla
            M[f"dest_{vetev}_{dny}d"] = sum(sra.reindex(den + pd.Timedelta(days=k)).to_numpy() for k in range(dny))
    return pd.DataFrame(M, index=hodiny)


if __name__ == "__main__":
    M = dest_dopredu()
    rows = []
    for cil in ("decin", "usti"):
        for h in (12, 24, 36):
            X, y = tabulka(cil, h)
            X = X.join(M).dropna()
            y = y[X.index]
            c = casti(cil, h).reindex(X.index)
            tr, ev = c == "train", c == "val"
            for nazev, cols in {"bez": [x for x in X if x not in M], "s_destem": list(X.columns)}.items():
                m = vyhodnot(y[ev], ridge.fit(X[tr][cols], y[tr], cil, h)(X[ev][cols]), cil, h)
                rows.append(dict(cil=cil, h=h, varianta=nazev) | {k: m[k] for k in (
                    "mae_povodne", "chyba_vrcholu", "spa2_predstih_h", "spa2_propasnuto", "spa2_plane_poplachy",
                    "spa3_predstih_h", "spa3_propasnuto")})
    R = pd.DataFrame(rows).set_index(["cil", "h", "varianta"])
    print(R.to_string())
    print("\nprumer_povodne:", R.groupby("varianta").mae_povodne.mean().round(1).to_dict())
