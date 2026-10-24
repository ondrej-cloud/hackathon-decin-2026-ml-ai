r"""Data a stránky pro web (složka web/, na Netlify jde celá bez build kroku).

python src/export_web.py --jen-data   web/data/*.json a obrázky (web/img, web/prezentace/grafy), bez map
python src/export_web.py --vse        navíc web/mapa/*.html a web/animace/*.html (potřebují MAPBOX_TOKEN v .env)

web/data/dnesek.json (živá data ČHMÚ) dělá src/dnesek_export.py, tenhle skript na něj nesahá.

Povodně z validace počítá model ridge (učený 2006–2018), Boris 9/2024 model ridge_test (učený na všem do 2020,
stejný jako při finálním testu v docs/PREHLED.md, aby web říkal stejná čísla jako prezentace); ten si skript uloží
do models/ridge_test_<cil>_<h>.joblib, když chybí.

Na Windows před spuštěním $env:PYTHONUTF8=1. Modely models/ridge_*.joblib a ridge_vse_*.joblib si při chybění
vyrobí predikce.nacti_model stejně jako src/uloz_model.py.

Časy v JSON jsou český čas bez pásma ("2011-01-15T09:00"), hladiny a předpovědi celé cm.
"""
import json
import shutil
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "app"))

from data import CILE, SPA, nacti  # noqa: E402
from evaluate import PO, PRED, varovani  # noqa: E402
from predikce import HORIZONTY, MODELS, nacti_model, vstupy  # noqa: E402
from animace import POVODNE, okno  # noqa: E402

WEB = ROOT / "web"
DATA = WEB / "data"
GRAFY = ROOT / "docs/grafy"
TZ = "Europe/Prague"
MODEL = "ridge"  # učený 2006–2018, povodně z validace
MODEL_TEST = "ridge_test"  # učený na všem do 2020 jako při finálním testu, povodeň z testu (Boris)
MODEL_2013 = "ridge_bez2013"  # jako ridge_test, jen bez povodně 6/2013 a 20 dní kolem ní (ta je v tréninku)
UCEN = {MODEL: "2006–2018", MODEL_TEST: "2006–2020", MODEL_2013: "2006–2020 bez povodně 2013"}
# slug pro web, klíč v app/app.py a app/animace.py, název
POVODNE_WEB = [("2006-04", "4/2006", "Duben 2006"), ("2009-03", "3/2009", "Březen 2009"),
               ("2010-09", "9/2010", "Září 2010"), ("2011-01", "1/2011", "Leden 2011"),
               ("2013-06", "6/2013", "Červen 2013, model ji neviděl"),
               ("2024-09", "9/2024 Boris (test)", "Září 2024, Boris")]
STANICE = {"decin": "Děčín", "usti": "Ústí nad Labem"}
VSTUPY_GRAF = ("praha_Q", "melnik_Q", "usti_H", "decin_H")
NABEH = pd.Timedelta(days=5)  # před oknem navíc, aby varování vidělo 4 klidné dny před překročením stupně
SOUHRN = {"validace": {"chyba_model": 17.1, "chyba_jako_ted": 44.3, "povodni": 4, "roky": "2006–2011"},
          "test": {"chyba_model": 22.4, "chyba_jako_ted": 50.2, "roky": "2021–2025"}}
SNIMKY = ("mapbox3_decin", "mapbox3_usti", "mapbox3_animace")
PISMA = "../fonts/"  # písma webu pro stránky v web/mapa a web/animace (self-hostovaná, bez Google Fonts)


def cesky(t):
    return t.tz_convert(TZ).strftime("%Y-%m-%dT%H:%M")


def zdroj_povodne(klic):
    """test = Boris (model ridge_test), trenink = 6/2013 (model učený bez ní), jinak validace."""
    return "test" if "test" in klic else "trenink" if klic == "6/2013" else "validace"


def model_povodne(zdroj):
    return {"test": MODEL_TEST, "trenink": MODEL_2013}.get(zdroj, MODEL)


def uloz_model_test():
    """models/ridge_test_<cil>_<h>.joblib: ridge učený na všem do 2020 (casti finalni=True), jako finální test."""
    from evaluate import casti
    from features import tabulka
    from models import ridge

    MODELS.mkdir(exist_ok=True)
    for cil in CILE:
        for h in HORIZONTY:
            soubor = MODELS / f"{MODEL_TEST}_{cil}_{h}.joblib"
            if soubor.exists():
                continue
            X, y = tabulka(cil, h)
            tr = casti(cil, h, finalni=True).reindex(X.index) == "train"
            joblib.dump(ridge.pipeline(ridge.PARAMETRY["alpha"]).fit(X[tr], y[tr]), soubor)


def cela(rada):
    return [None if pd.isna(v) else int(round(float(v))) for v in rada]


def uloz(nazev, obj):
    soubor = DATA / nazev
    soubor.write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return soubor


def hodiny(klic):
    """Hodiny okna povodně v UTC: od půlnoci prvního dne do 23:00 posledního dne českého času."""
    od, do = POVODNE[klic]
    return pd.date_range(pd.Timestamp(od, tz=TZ), pd.Timestamp(f"{do} 23:00", tz=TZ), freq="h").tz_convert("UTC")


def rozmezi(cil, h, ted, pred):
    """Dolní a horní mez jako predikce.interval, pro celé řady najednou."""
    z = json.loads((MODELS / "ridge_intervaly.json").read_text(encoding="utf-8"))[f"{cil}_{h}"]
    i = np.searchsorted(z["pasma"][1:-1], ted.to_numpy(), side="right")
    return pred + np.array(z["dolni"])[i], pred + np.array(z["horni"])[i]


def predpovedi(cil, cas, model=MODEL):
    """{h: Series} předpovědí modelu vydaných v každé hodině `cas` (UTC) na cas + h; NaN, kde chybí vstupy."""
    X = vstupy(cil).reindex(cas)
    ok = X.notna().all(axis=1)
    out = {}
    for h in HORIZONTY:
        p = pd.Series(np.nan, index=cas)
        p[ok] = nacti_model(model, cil, h).predict(X[ok])
        out[h] = p
    return out, X[f"{cil}_H_0"]


def predstih(H, P, prah, h):
    """Hodiny od vydání prvního varování do skutečného překročení prahu (jako Boris 27 h v PREHLED.md).

    H a P jsou v čase platnosti. Varování je souvislý úsek předpovědí nad prahem (mezery do 6 h spojené jako
    u planých poplachů v evaluate.py) těsně před překročením; krátký výkyv o dva dny dřív se nepočítá.
    None, když hladina práh nepřekročila; (None, True), když model před překročením nevaroval.
    """
    nad = H.index[H >= prah]
    if nad.empty:
        return None, False
    vydano = P.index[P >= prah] - pd.Timedelta(hours=h)
    vydano = vydano[vydano < nad[0]]
    if vydano.empty:
        return None, True
    zacatek = vydano[-1]
    for t in vydano[-2::-1]:
        if zacatek - t > pd.Timedelta(hours=6):
            break
        zacatek = t
    return int(round((nad[0] - zacatek) / pd.Timedelta(hours=1))), False


def metriky_povodne(cil, cas, cas_vse, pred, Hvse):
    """Pro každý horizont chyba modelu a „bude jako teď“ v týdnu před vrcholem a 5 dní po něm, předstih a poplachy.

    cas je okno povodně, cas_vse okno s náběhem (varování potřebuje 4 klidné dny před překročením stupně).
    """
    H = Hvse.reindex(cas)
    vrchol = H.idxmax()
    okno_v = cas[(cas >= vrchol - PRED) & (cas <= vrchol + PO)]
    out = {}
    for h in HORIZONTY:
        hod = pd.Timedelta(hours=h)
        P = pred[h].shift(h, freq="h").reindex(cas)  # v čase platnosti
        J = Hvse.shift(h, freq="h").reindex(cas)  # bude jako teď: hladina před h hodinami
        p2, prop2 = predstih(H, P, SPA[cil][1], h)
        p3, prop3 = predstih(H, P, SPA[cil][2], h)
        # propásnuté a plané poplachy 2. stupně stejně jako v src/evaluate.py (index je čas vydání)
        v = varovani(Hvse.shift(-h, freq="h").reindex(cas_vse), pred[h], SPA[cil][1], h)
        out[str(h)] = {
            "chyba_model": round(float((P - H).abs()[okno_v].mean()), 1),
            "chyba_jako_ted": round(float((J - H).abs()[okno_v].mean()), 1),
            "predstih_2_stupen_h": p2, "predstih_3_stupen_h": p3,
            "propasnute": int(v["propasnuto"]), "plane": int(v["plane_poplachy"]),
            "povodni": int(v["povodni"]), "vrchol_cm": int(round(float(H.max()))),
            "vrchol_model_cm": None if pd.isna(P[vrchol]) else int(round(float(P[vrchol]))),
            "nevarovano_2_stupen": prop2, "nevarovano_3_stupen": prop3,
        }
    return out


def data_povodni():
    D = nacti()
    povodne, metriky = [], {}
    for slug, klic, nazev in POVODNE_WEB:
        cas = hodiny(klic)
        cas_vse = pd.date_range(cas[0] - NABEH, cas[-1], freq="h")
        Dw = D.reindex(cas)
        zdroj = zdroj_povodne(klic)
        model = model_povodne(zdroj)
        zaznam = {"slug": slug, "klic": klic, "nazev": nazev, "od": cesky(cas[0]), "do": cesky(cas[-1]),
                  "zdroj": zdroj, "model": model, "ucen": UCEN[model], "vrchol": {}}
        metriky[slug] = {}
        for cil in CILE:
            pred, ted = predpovedi(cil, cas_vse, model)
            H = D[f"{cil}_H"]
            zaznam["vrchol"][cil] = {"cas": cesky(Dw[f"{cil}_H"].idxmax()), "cm": int(round(Dw[f"{cil}_H"].max()))}
            metriky[slug][cil] = metriky_povodne(cil, cas, cas_vse, pred, H)
            rada = {"cas": [cesky(t) for t in cas], "skutecnost": cela(Dw[f"{cil}_H"]),
                    "pred": {}, "dolni": {}, "horni": {},
                    "vstupy": {k: cela(Dw[k]) for k in VSTUPY_GRAF}}
            for h in HORIZONTY:
                p = pred[h].reindex(cas)
                lo, hi = rozmezi(cil, h, ted.reindex(cas), p)
                rada["pred"][str(h)], rada["dolni"][str(h)], rada["horni"][str(h)] = cela(p), cela(lo), cela(hi)
            uloz(f"rada_{slug}_{cil}.json", rada)
        povodne.append(zaznam)
    metriky["souhrn"] = SOUHRN
    uloz("metriky.json", metriky)
    vstupu = vstupy("decin").shape[1]
    uloz("povodne.json", {
        "povodne": povodne,
        "stanice": {c: {"nazev": STANICE[c], "spa": list(SPA[c])} for c in CILE},
        "model": {"nazev": MODEL, "ucen": UCEN[MODEL], "vstupu": vstupu, "nazev_test": MODEL_TEST, "ucen_test": UCEN[MODEL_TEST],
                  "chyba_validace": SOUHRN["validace"]["chyba_model"],
                  "chyba_jako_ted": SOUHRN["validace"]["chyba_jako_ted"],
                  "chyba_test": SOUHRN["test"]["chyba_model"],
                  "chyba_test_jako_ted": SOUHRN["test"]["chyba_jako_ted"]},
    })
    return metriky


def modely_do_json():
    """Pipeline (odmocnina průtoků, StandardScaler, Ridge) jako čísla, aby šla předpověď spočítat v prohlížeči."""
    X = vstupy("decin").tail(1)
    for cil in CILE:
        for h in HORIZONTY:
            m = nacti_model("ridge_vse", cil, h)
            sc, rg = m.named_steps["standardscaler"], m.named_steps["ridge"]
            sloupce = list(m.feature_names_in_)
            z = {"sloupce": sloupce, "mean": [round(float(v), 6) for v in sc.mean_],
                 "scale": [round(float(v), 6) for v in sc.scale_], "coef": [round(float(v), 6) for v in rg.coef_],
                 "intercept": round(float(rg.intercept_), 6), "odmocnina_prutoku": True}
            # kontrola: ruční výpočet z JSON proti pipeline
            x = X[sloupce].iloc[0].to_numpy(dtype=float).copy()
            q = np.array(["_Q_" in s for s in sloupce])
            x[q] = np.sqrt(x[q])
            rucne = ((x - np.array(z["mean"])) / np.array(z["scale"])) @ np.array(z["coef"]) + z["intercept"]
            assert abs(rucne - float(m.predict(X[sloupce])[0])) < 0.01, (cil, h, rucne)
            uloz(f"model_ridge_vse_{cil}_{h}.json", z)


def obrazky():
    from PIL import Image

    (WEB / "img").mkdir(parents=True, exist_ok=True)
    for n in SNIMKY:
        im = Image.open(GRAFY / f"{n}.png").convert("RGB")
        w, h = im.size
        if w > 1600:
            im = im.resize((1600, round(h * 1600 / w)), Image.LANCZOS)
        im.save(WEB / "img" / f"{n}.webp", quality=82, method=6)
        # menší náhled pro telefony (srcset), ať se do 360 px širokého boxu nestahuje 1600 px
        w, h = im.size
        im.resize((800, round(h * 800 / w)), Image.LANCZOS).save(WEB / "img" / f"{n}_800.webp", quality=80, method=6)
    # jen grafy, na které deck odkazuje (mapy a součet má deck jako jpg nebo vlastní SVG), ať se nenahrává nic navíc
    cil = WEB / "prezentace/grafy"
    cil.mkdir(parents=True, exist_ok=True)
    deck = (WEB / "prezentace/index.html").read_text(encoding="utf-8")
    for f in sorted((GRAFY / "prezentace").glob("*.png")):
        if f"grafy/{f.name}" in deck:
            shutil.copy2(f, cil / f.name)


def mapy():
    """Stránky map a animace s tokenem Mapboxu (jsou v .gitignore, na Netlify jdou z lokálního stroje)."""
    import animace
    import mapa
    import mapbox_mapa

    if not mapa.mapbox_token():
        print("MAPBOX_TOKEN v .env chybí, stránky map budou jen s hláškou.")
    (WEB / "mapa").mkdir(parents=True, exist_ok=True)
    (WEB / "animace").mkdir(parents=True, exist_ok=True)
    for slug, klic, _ in POVODNE_WEB:
        od, do = okno(klic)
        model = model_povodne(zdroj_povodne(klic))
        (WEB / "animace" / f"{slug}.html").write_text(animace.html(od, do, model, pisma=PISMA), encoding="utf-8")
        for cil in CILE:
            stranka = mapbox_mapa.html_animace(od, do, cil, model, mapbox_mapa.MESTA[cil], pisma=PISMA)
            (WEB / "mapa" / f"{slug}_{cil}.html").write_text(stranka, encoding="utf-8")
        print(f"  mapy {slug}")


def kontrola():
    """Referenční bod aplikace (app/test_app.py): Děčín 15. 1. 2011 9:00 českého času, 646 cm, za 24 h asi 738 cm."""
    r = json.loads((DATA / "rada_2011-01_decin.json").read_text(encoding="utf-8"))
    i = r["cas"].index("2011-01-15T09:00")
    assert r["skutecnost"][i] == 646, r["skutecnost"][i]
    assert abs(r["pred"]["24"][i] - 738) <= 3, r["pred"]["24"][i]
    for f in sorted(DATA.glob("*.json")):
        json.loads(f.read_text(encoding="utf-8"))
    print(f"kontrola: 15. 1. 2011 9:00 Děčín {r['skutecnost'][i]} cm, za 24 h {r['pred']['24'][i]} cm "
          f"({r['dolni']['24'][i]} až {r['horni']['24'][i]})")


def vypis():
    celkem = 0
    for f in sorted(p for p in WEB.rglob("*") if p.is_file() and p.parts[len(WEB.parts)] in
                    ("data", "img", "mapa", "animace") or p.parent == WEB / "prezentace/grafy"):
        kb = f.stat().st_size / 1e3
        celkem += kb
        print(f"  {f.relative_to(ROOT).as_posix():48s} {kb:9.1f} kB")
    print(f"  celkem {celkem / 1e3:.1f} MB")


if __name__ == "__main__":
    DATA.mkdir(parents=True, exist_ok=True)
    uloz_model_test()
    M = data_povodni()
    modely_do_json()
    obrazky()
    kontrola()
    b = M["2024-09"]["decin"]["24"]
    print(f"Boris Děčín, 24 h ({MODEL_TEST}): 3. stupeň hlášen {b['predstih_3_stupen_h']} h předem, chyba {b['chyba_model']} cm "
          f"proti {b['chyba_jako_ted']} cm, vrchol {b['vrchol_cm']} cm předpovězen na {b['vrchol_model_cm']} cm")
    d = M["2013-06"]["decin"]["24"]
    print(f"Povodeň 2013 Děčín, 24 h ({MODEL_2013}): 3. stupeň hlášen {d['predstih_3_stupen_h']} h předem, chyba {d['chyba_model']} cm "
          f"proti {d['chyba_jako_ted']} cm, vrchol {d['vrchol_cm']} cm předpovězen na {d['vrchol_model_cm']} cm")
    if "--vse" in sys.argv[1:]:
        mapy()
    vypis()
