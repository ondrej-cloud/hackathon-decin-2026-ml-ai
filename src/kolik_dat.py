"""Kolik let historie a které stanice potřebuje Ridge na společné validaci.

python src/kolik_dat.py
python src/kolik_dat.py --graf-ze results/kolik_dat/<soubor>.json
"""
import argparse
import hashlib
import json
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import matplotlib
import numpy as np
import pandas as pd
import sklearn

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from data import SPA
from evaluate import casti, povodne, vyhodnot
from features import NEJSTARSI, tabulka
from models import ridge
from porovnej import VSE, verze

ROOT = Path(__file__).resolve().parents[1]
LET = (1, 2, 3, 5, 8, 13)
SADY = {"kraj": "Jen kraj (3 stanice)", "vsechny": "Všechny stanice (12)"}
KONEC = pd.Timestamp("2019-01-01", tz="UTC")


def trenink(index, cast, let, horizont):
    zacatek = pd.Timestamp(f"{2019 - let}-01-01", tz="UTC")
    # Do okna musí vejít i nejstarší vstup a cílová hladina, nejen čas vydání.
    return ((cast == "train")
            & (index - pd.Timedelta(hours=NEJSTARSI) >= zacatek)
            & (index + pd.Timedelta(hours=horizont) < KONEC))


def souhrn(radky):
    df = pd.DataFrame(radky)
    return (df.groupby(["sada", "let"], sort=False)
            .agg(prumer_povodne=("mae_povodne", "mean"),
                 spa2_propasnuto=("spa2_propasnuto", "sum"),
                 spa2_povodni=("spa2_povodni", "sum"),
                 spa2_plane_poplachy=("spa2_plane_poplachy", "sum"),
                 trenink_s=("trenink_s", "sum"))
            .reset_index())


def spust():
    start = time.perf_counter()
    radky, zaklad = [], []
    for cil, horizont in VSE:
        X, y = tabulka(cil, horizont)
        cast = casti(cil, horizont).reindex(X.index)
        val = cast == "val"
        Xval, yval = X.loc[val], y.loc[val]
        assert not (cast.loc[val] == "test").any()
        assert Xval.index.max() < pd.Timestamp("2021-01-01", tz="UTC")
        zaklad.append(dict(cil=cil, horizont=horizont,
                           **vyhodnot(yval, Xval[f"{cil}_H_0"], cil, horizont)))
        for let in LET:
            tr = trenink(X.index, cast, let, horizont)
            assert tr.any() and not (tr & val).any()
            Xtr, ytr = X.loc[tr], y.loc[tr]
            for sada in SADY:
                sloupce = list(X.columns) if sada == "vsechny" else [
                    s for s in X.columns if s.startswith(("decin_", "usti_", "louny_"))
                ]
                assert len(sloupce) == (98 if sada == "vsechny" else 35)
                t0 = time.perf_counter()
                predict = ridge.fit(Xtr[sloupce], ytr, cil=cil, horizont=horizont)
                doba = time.perf_counter() - t0
                pred = np.asarray(predict(Xval[sloupce]), dtype=float)
                pred_tr = np.asarray(predict(Xtr[sloupce]), dtype=float)
                assert np.isfinite(pred).all() and np.isfinite(pred_tr).all()
                metriky = vyhodnot(yval, pred, cil, horizont)
                vysoka = ytr >= SPA[cil][1]
                zaznam = dict(
                    sada=sada, let=let, cil=cil, horizont=horizont,
                    **metriky, sloupcu=len(sloupce), trenink_radku=len(ytr),
                    trenink_s=round(doba, 3),
                    trenink_mae=round(float(np.abs(pred_tr - ytr).mean()), 1),
                    trenink_spa2_hodin=int(vysoka.sum()),
                    trenink_spa2_povodni=len(povodne(ytr, SPA[cil][1])),
                    trenink_max_cm=float(ytr.max()),
                    trenink_vydani_od=Xtr.index.min().isoformat(),
                    trenink_vydani_do=Xtr.index.max().isoformat(),
                    trenink_vstup_od=(Xtr.index.min() - pd.Timedelta(hours=NEJSTARSI)).isoformat(),
                    trenink_cil_do=(Xtr.index.max() + pd.Timedelta(hours=horizont)).isoformat(),
                    val_index_sha256=hashlib.sha256(yval.index.asi8.tobytes()).hexdigest(),
                )
                radky.append(zaznam)
                print(f"{cil} +{horizont} h, {let:2} let, {sada:7}: "
                      f"povodně {metriky['mae_povodne']:5.1f} cm, "
                      f"propásnuto {metriky['spa2_propasnuto']}/{metriky['spa2_povodni']}", flush=True)
    prehled = souhrn(radky)
    baseline = float(np.mean([r["mae_povodne"] for r in zaklad]))
    assert len(radky) == 72 and len(prehled) == 12
    assert round(baseline, 1) == 44.3, "Změnila se společná validace, ověř základ."
    cas = datetime.now(ZoneInfo("Europe/Prague"))
    return dict(
        autor="Honza", cas=cas.isoformat(timespec="seconds"), cast="val",
        experiment="kolik_dat", model="ridge", verze=verze(),
        kod_sha256={jmeno: hashlib.sha256((ROOT / jmeno).read_text(encoding="utf-8")
                                         .encode("utf-8")).hexdigest()
                    for jmeno in ("src/features.py", "src/evaluate.py", "src/models/ridge.py", "src/kolik_dat.py")},
        knihovny=dict(numpy=np.__version__, pandas=pd.__version__, sklearn=sklearn.__version__),
        parametry=dict(ridge=ridge.PARAMETRY, let=list(LET), sady=SADY, seed=42,
                       konec_treninku="2018-12-31", ochrana_okraje_h=NEJSTARSI,
                       validace="Společná část val, stejná pro všech 12 variant; test 2021–2025 nepoužit."),
        poznamka="Retrospektivní srovnání na vynechaných povodních 2006–2011 a klidu 2019–2020; "
                 "nejde o dopředný test ani určení univerzálního minima let.",
        doba_s=round(time.perf_counter() - start, 1),
        zaklad_prumer_povodne=baseline, zaklad=zaklad,
        souhrn=prehled.to_dict("records"), vysledky=radky,
    )


def graf(zaznam):
    df = pd.DataFrame(zaznam["souhrn"])
    fig, ax = plt.subplots(figsize=(11, 6.5))
    for sada, barva in (("kraj", "#cb6c31"), ("vsechny", "#167c9c")):
        body = df[df.sada == sada].sort_values("let")
        ax.plot(body["let"], body.prumer_povodne, "o-", color=barva,
                linewidth=2.5, markersize=7, label=SADY[sada])
        for bod in body.itertuples(index=False):
            ax.annotate(f"{bod.prumer_povodne:.1f}".replace(".", ","),
                        (bod.let, bod.prumer_povodne), xytext=(0, 9),
                        textcoords="offset points", ha="center", color=barva, fontsize=10)
    baseline = zaznam["zaklad_prumer_povodne"]
    ax.axhline(baseline, color="#666666", linestyle="--", linewidth=1.5,
               label=f"Bude jako teď ({baseline:.1f} cm)".replace(".", ","))
    ax.axvspan(0.7, 5.3, color="#e9eef1", alpha=0.6, zorder=0)
    ax.set(xlabel="Počet let trénovací historie (všechna okna končí rokem 2018)",
           ylabel="Průměrná chyba na povodních (cm)", xticks=LET, xlim=(0.7, 13.6),
           ylim=(0, max(baseline, df.prumer_povodne.max()) * 1.2))
    ax.set_title("Kolik historie a které stanice potřebuje model?", loc="left", fontsize=17, pad=18)
    ax.grid(axis="y", alpha=0.2)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="upper right", frameon=False)
    fig.text(0.10, 0.075,
             "Šedé pásmo: 1–5 let bez dosažení 2. povodňového stupně v tréninku; 8 a 13 let zahrnuje povodeň 2013.",
             fontsize=9, color="#444444")
    fig.text(0.10, 0.04,
             "Ridge beze změn · 4 stejné validační povodně · průměr přes Děčín a Ústí, +12 / +24 / +36 h · test nepoužit",
             fontsize=9, color="#444444")
    fig.tight_layout(rect=(0, 0.12, 1, 1))
    cesta = ROOT / "docs/grafy/kolik_dat.png"
    cesta.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(cesta, dpi=180)
    plt.close(fig)
    return cesta


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graf-ze", type=Path, help="Překreslí graf z uloženého JSON bez nového tréninku.")
    args = parser.parse_args()
    if args.graf_ze:
        zaznam = json.loads(args.graf_ze.read_text(encoding="utf-8"))
    else:
        zaznam = spust()
        slozka = ROOT / "results/kolik_dat"
        slozka.mkdir(parents=True, exist_ok=True)
        cas = datetime.fromisoformat(zaznam["cas"])
        cesta = slozka / f"{cas:%Y-%m-%d_%H%M%S}_kolik_dat.json"
        cesta.write_text(json.dumps(zaznam, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
        pd.DataFrame(zaznam["souhrn"]).to_csv(cesta.with_suffix(".csv"), index=False)
        print(f"\nUloženo: {cesta.relative_to(ROOT)}")
    print(pd.DataFrame(zaznam["souhrn"]).round(1).to_string(index=False))
    print(f"Bude jako teď: {zaznam['zaklad_prumer_povodne']:.1f} cm")
    print(f"Graf: {graf(zaznam).relative_to(ROOT)}")


if __name__ == "__main__":
    main()
