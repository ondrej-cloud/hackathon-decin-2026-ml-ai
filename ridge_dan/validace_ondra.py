"""Souhrn Ondrovy vícenásobné validace (src/krizova_validace.py) s ridge30 a g3.

python validace_ondra.py <můj CSV> <Ondrův CSV>
Z mého běhu jako_ted, ridge, lgbm, ridge30, g3; síť (mlp) a fyzika z Ondrova uloženého běhu (netrénují se znovu).
U jako_ted, ridge a lgbm ověří, že oba běhy dávají stejná čísla. Vypíše tabulky v markdownu.
"""
import sys

import pandas as pd

MODELY = ["jako_ted", "ridge", "mlp", "lgbm", "fyzika", "ridge30", "g3"]


def c(x, d=1):
    return f"{round(x + 1e-9, d):.{d}f}".replace(".", ",")  # zaokrouhlení jako pandas v krizova_validace


if __name__ == "__main__":
    moje, ondra = pd.read_csv(sys.argv[1]), pd.read_csv(sys.argv[2])
    klic = ["cil", "h", "povoden", "model"]
    spol = moje.merge(ondra, on=klic, suffixes=("", "_ondra"))
    for m in ("jako_ted", "ridge", "lgbm"):
        s = spol[spol.model == m]
        rozdil = (s.chyba - s.chyba_ondra).abs().max()
        shoda_popl = ((s.propasnuto == s.propasnuto_ondra) & (s.plane == s.plane_ondra)).all()
        print(f"shoda {m}: {len(s)} řádků, největší rozdíl chyby {rozdil:.2f} cm, poplachy stejné: {shoda_popl}")
    R = pd.concat([moje, ondra[ondra.model.isin(["mlp", "fyzika"])]], ignore_index=True)
    P = R.groupby(["povoden", "model"]).chyba.mean().unstack()[MODELY]

    print("\n| Povodeň | " + " | ".join(MODELY) + " | nejlepší |")
    print("|---" * (len(MODELY) + 2) + "|")
    for pov, r in P.iterrows():
        nej = r.drop("jako_ted").idxmin()
        print(f"| {pov} | " + " | ".join(("**" + c(r[m]) + "**") if m == nej else c(r[m]) for m in MODELY) + f" | {nej} |")
    print("| průměr ± sm. odch. | " + " | ".join(f"{c(P[m].mean())} ± {c(P[m].std())}" for m in MODELY) + " | |")

    nej = P.drop(columns="jako_ted").idxmin(axis=1).value_counts()
    print("\nnejlepší (z 8 povodní, bez jako_ted):", {m: int(nej.get(m, 0)) for m in MODELY[1:]})
    ondra_bez = P[["ridge", "mlp", "lgbm", "fyzika"]].drop(columns=[]).idxmin(axis=1).value_counts()
    print("nejlepší jen mezi Ondrovými modely:", ondra_bez.to_dict())
    pp = R.groupby("model")[["propasnuto", "plane"]].sum().reindex(MODELY)
    print("\n| Model | propásnutá varování (2. + 3. SPA) | plané poplachy (2. SPA) |\n|---|---|---|")
    for m, r in pp.iterrows():
        print(f"| {m} | {int(r.propasnuto)} | {int(r.plane)} |")

    nejlepsi_ondra = P[["ridge", "mlp", "lgbm", "fyzika"]].mean().idxmin()
    d = P.g3 - P[nejlepsi_ondra]
    print(f"\nG3 proti nejlepšímu Ondrovu modelu ({nejlepsi_ondra}): průměr {c(d.mean(), 2)} cm, "
          f"G3 lepší v {int((d < 0).sum())} z {len(d)} povodní, nejhorší zhoršení {c(d.max())}, nejlepší {c(d.min())}")
    d30 = P.ridge30 - P[nejlepsi_ondra]
    print(f"ridge30 proti {nejlepsi_ondra}: průměr {c(d30.mean(), 2)} cm, lepší v {int((d30 < 0).sum())} z {len(d30)}")
    K = R[R.model.isin(["ridge", "g3", "ridge30"])].pivot_table(index=["cil", "h"], columns="model", values="chyba", aggfunc="mean")
    print("\npo kombinacích cíl × horizont (průměr přes 8 povodní):\n" + K.round(1).to_string())
