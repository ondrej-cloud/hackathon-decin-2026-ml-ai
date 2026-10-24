"""Čtyři grafy do prezentace (Dan), styl jako src/grafy_prezentace.py: 16:9, krátký nadpis vlevo nahoře, bez podtitulků.

Nic netrénuje, jen čte uložené výsledky a předpovědi (cesty níž). Ostatní worktree jen čte, nic v nich nespouští.

    set PYTHONUTF8=1
    python prezentace_dan/grafy_dan.py    uloží prezentace_dan/grafy/G1–G4_*.png

Zdroje a výhrady ke každému grafu jsou v prezentace_dan/grafy/README.md.
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.ticker import FuncFormatter, MultipleLocator  # noqa: E402

ZDE = Path(__file__).resolve().parent
PREZ = ZDE.parent  # worktree dan-prezentace
CIL = ZDE / "grafy"
RIDGE = Path(r"C:\Users\danie\Documents\hackathon-2026-ridge\ridge_dan")
SIT = Path(r"C:\Users\danie\Documents\hackathon-2026-sit\sit_dan")

# barvy týmu (src/grafy_slajdy.py)
INK, INK2 = "#1f1f1f", "#4d4d4d"
MODRA, ORANZ, SEDA, MODRA_SVETLA = "#167c9c", "#cb6c31", "#666666", "#9fcad8"
FIALOVA, TYRKYS = "#6250d6", "#1baf7a"
STUPNE = ("#f2c437", "#ef6c00", "#c62828")
NB = "\u00a0"
JAKO_TED = "„bude jako teď“"
CHYBA = "průměrná chyba během povodní (cm)"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Segoe UI", "Helvetica Neue", "Arial", "DejaVu Sans"],
    "font.size": 16, "text.color": INK,
    "axes.labelsize": 16, "axes.labelcolor": INK2, "axes.labelpad": 8,
    "axes.edgecolor": "#9a9a9a", "axes.linewidth": 1,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "axes.grid.axis": "y", "axes.axisbelow": True,
    "grid.color": "#e6e6e6", "grid.linewidth": 0.9,
    "xtick.labelsize": 15, "ytick.labelsize": 15, "xtick.color": INK2, "ytick.color": INK2,
    "legend.fontsize": 15, "legend.frameon": False,
    "figure.facecolor": "white", "savefig.facecolor": "white",
})
PLOCHA = (0.09, 0.13, 0.88, 0.72)
NESEDI = []  # rozdíly proti kontrolním číslům ze zadání, vypíšou se na konci


def cislo(x, des=1):
    """Česky: desetinná čárka, nezlomitelná mezera u tisíců."""
    return f"{float(x):,.{des}f}".replace(",", NB).replace(".", ",")


def osa_cisla(ax, osa="y"):
    (ax.yaxis if osa == "y" else ax.xaxis).set_major_formatter(FuncFormatter(lambda v, _: cislo(v, 0)))


def graf(titulek, rect=PLOCHA):
    fig = plt.figure(figsize=(12, 6.75))
    fig.text(0.04, 0.95, titulek, fontsize=24, weight="semibold", color=INK, va="top")
    return fig, (fig.add_axes(rect) if rect else None)


def uloz(fig, nazev):
    fig.savefig(CIL / nazev, dpi=150)
    plt.close(fig)
    print(f"uloženo {(CIL / nazev).relative_to(PREZ)}")


def kontrola(co, hodnota, cekano, tolerance=0.05):
    if abs(round(hodnota, 1) - cekano) > tolerance:
        NESEDI.append(f"{co}: ze zdroje {cislo(hodnota)}, v zadání {cislo(cekano)}")


def nacti_json(cesta):
    b = Path(cesta).read_bytes()
    try:
        return json.loads(b.decode("utf-8"))
    except UnicodeDecodeError:  # starší výsledky z Windows bez UTF-8
        return json.loads(b.decode("cp1250"))


# G1 ---------------------------------------------------------------------------------------------------------------
# doba doběhu do Děčína (h): docs/DATA.md „Doba doběhu do Děčína“, src/doba_dobehu.py (train 2006–2018)
DOBEH = {"usti": 4, "kostelec": 10, "nymburk": 10, "melnik": 13, "vranany": 13, "louny": 16, "praha": 17, "jizera": 18,
         "prelouc": 18, "beroun": 23, "sazava": 25}
VETVE = {  # barva, název do legendy, stanice
    "vltava": (MODRA, "Vltava s Berounkou a Sázavou", ["praha", "beroun", "sazava", "vranany"]),
    "labe_horni": (ORANZ, "horní Labe s Jizerou", ["prelouc", "nymburk", "jizera", "kostelec"]),
    "ohre": (FIALOVA, "Ohře", ["louny"]),
    "labe_dolni": (INK, "Labe pod Mělníkem", ["melnik", "usti", "decin"]),
}
SPOJNICE = [("sazava", "praha"), ("beroun", "praha"), ("praha", "vranany"), ("vranany", "melnik"),
            ("prelouc", "nymburk"), ("nymburk", "kostelec"), ("jizera", "kostelec"), ("kostelec", "melnik"),
            ("melnik", "usti"), ("louny", "usti"), ("usti", "decin")]
JMENA = {"decin": "Děčín", "usti": "Ústí n. L.", "louny": "Louny", "melnik": "Mělník", "vranany": "Vraňany",
         "kostelec": "Kostelec n. L.", "praha": "Praha-Chuchle", "nymburk": "Nymburk", "jizera": "Předměřice (Jizera)",
         "beroun": "Beroun", "sazava": "Nespeky (Sázava)", "prelouc": "Přelouč"}
# kam dát štítek: posun v bodech (dx, dy), zarovnání; „vodítko“ = tenká čára od bodu ke štítku
STITKY = {"decin": (14, 0, "left"), "usti": (-12, 16, "right"), "louny": (-10, 14, "right"),
          "melnik": (8, 14, "left"), "vranany": (-14, 0, "right"), "kostelec": (8, -40, "left", "vodítko"),
          "praha": (14, 0, "left"), "nymburk": (12, 16, "left"), "jizera": (10, 22, "left"),
          "beroun": (-14, 0, "right"), "sazava": (14, 0, "left"), "prelouc": (0, -24, "center")}
# 18 nových stanic z ridge_dan/stanice.py (číslo DBC); souřadnice z metadat ČHMÚ v ridge_dan/cache
NOVE_DBC = ["239000", "238000", "235000", "226000", "216000", "214000", "194500", "191000", "186000", "190000",
            "197300", "169000", "165000", "161000", "059000", "037000", "075000", "098000"]


def nove_stanice(S):
    """Souřadnice 18 nových stanic z meta1.json; kontrola, že 12 týmových sedí na stanice_hydro.csv do 0,01°."""
    cesta = RIDGE / "cache/hydrology/historical/metadata/meta1.json"
    if not cesta.exists():
        return None
    m = nacti_json(cesta)["data"]["data"]
    M = pd.DataFrame(m["values"], columns=m["header"].split(",")).set_index("DBC")
    tym = M.loc[S.cislo, ["GEOGR1", "GEOGR2"]].astype(float).to_numpy()
    if np.abs(tym - S[["lat", "lon"]].to_numpy()).max() > 0.01:
        print("G1: souřadnice v meta1.json nesedí na stanice_hydro.csv, nové stanice vynechány")
        return None
    return M.loc[NOVE_DBC, ["STATION_NAME", "STREAM_NAME", "GEOGR1", "GEOGR2"]].astype({"GEOGR1": float, "GEOGR2": float})


def g1_stanice():
    S = pd.read_csv(PREZ / "data/external/stanice_hydro.csv", dtype={"cislo": str}).set_index("klic")
    N = nove_stanice(S)
    barva = {s: b for b, _, st in VETVE.values() for s in st}
    fig, _ = graf("Za kolik hodin doteče voda do Děčína", rect=None)
    ax = fig.add_axes((0.01, 0.02, 0.98, 0.83))
    ax.set_aspect(1 / np.cos(np.radians(50.3)))  # stupeň délky je na 50° š. kratší než stupeň šířky
    ax.axis("off")
    if N is not None:
        ax.scatter(N.GEOGR2, N.GEOGR1, s=55, color="#c4c4c4", edgecolor="white", linewidth=1, zorder=2)
    for a, b in SPOJNICE:
        x0, y0, x1, y1 = S.lon[a], S.lat[a], S.lon[b], S.lat[b]
        ax.plot([x0, x1], [y0, y1], color=barva[a], lw=3, solid_capstyle="round", zorder=3)
        if np.hypot((x1 - x0) * np.cos(np.radians(50.3)), y1 - y0) < 0.125:
            continue  # na krátkých spojnicích (Vraňany → Mělník, Jizera → Kostelec) by šipka splynula s body
        xm, ym, dx, dy = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) * 0.04, (y1 - y0) * 0.04
        ax.annotate("", xy=(xm + dx, ym + dy), xytext=(xm - dx, ym - dy), zorder=3,
                    arrowprops=dict(arrowstyle="-|>,head_length=0.7,head_width=0.4", color=barva[a], lw=0,
                                    shrinkA=0, shrinkB=0))
    for k, r in S.iterrows():
        cil = k == "decin"
        ax.scatter(r.lon, r.lat, s=420 if cil else 150, color=barva[k], edgecolor="white", linewidth=2.5, zorder=5)
        if cil:
            ax.scatter(r.lon, r.lat, s=900, facecolor="none", edgecolor=INK, linewidth=2, zorder=5)
        dx, dy, ha, *vod = STITKY[k]
        text = "Děčín · cíl" if cil else f"{JMENA[k]} · {DOBEH[k]}{NB}h"
        ax.annotate(text, (r.lon, r.lat), xytext=(dx + (8 if cil else 0), dy), textcoords="offset points", ha=ha,
                    va="center", fontsize=19 if cil else 15, weight="bold" if cil else "normal", color=INK, zorder=6,
                    arrowprops=dict(arrowstyle="-", color=INK2, lw=1, shrinkA=0, shrinkB=7) if vod else None)
    lon = list(S.lon) + (list(N.GEOGR2) if N is not None else [])
    lat = list(S.lat) + (list(N.GEOGR1) if N is not None else [])
    ax.set_xlim(min(lon) - 0.15, max(lon) + 0.15)
    ax.set_ylim(min(lat) - 0.06, max(lat) + 0.06)
    znacky = [Line2D([], [], color=b, lw=3, marker="o", ms=10, mec="white", mew=2, label=n) for b, n, _ in VETVE.values()]
    if N is not None:
        znacky.append(Line2D([], [], ls="none", marker="o", ms=9, color="#c4c4c4", mec="white",
                             label="18 nových stanic (doba neměřena)"))
    fig.legend(handles=znacky, loc="upper right", bbox_to_anchor=(0.985, 0.935), handlelength=2.2, fontsize=15,
               labelspacing=0.5)
    uloz(fig, "G1_stanice_doby_dobehu.png")
    return dict(nove_stanice=0 if N is None else len(N))


# G2 ---------------------------------------------------------------------------------------------------------------
VERZE = "9a31181e"
G2_MODELY = [  # klíč v results/, popisek, barva, tloušťka, styl čáry
    ("ridge", "lineární regrese (finální)", MODRA, 3.4, "-"),
    ("mlp", "neuronová síť", ORANZ, 2.4, "-"),
    ("lgbm", "LightGBM", FIALOVA, 2.4, "-"),
    ("fyzika", "fyzikální model", TYRKYS, 2.4, "-"),
    ("jako_ted", JAKO_TED, SEDA, 2.4, (0, (5, 3))),
]
G2_KONTROLA = {("ridge", "decin"): [9.0, 15.5, 26.0], ("mlp", "decin"): [9.3, 18.4, 25.7],
               ("jako_ted", "decin"): [23.0, 44.4, 65.6]}
G2_PRUMERY = {"ridge": 17.1, "mlp": 17.8, "lgbm": 23.1, "fyzika": 24.8, "jako_ted": 44.3}


def nejnovejsi(model):
    """Nejnovější plný běh na validaci s verzí dat a vyhodnocení VERZE (results/*.json, pole „cas“)."""
    kandidati = []
    for f in (PREZ / "results").glob("*.json"):
        z = nacti_json(f)
        if (z.get("model") == model and z.get("verze") == VERZE and z.get("cast") == "val" and not z.get("rychle")
                and len(z.get("vysledky", [])) == 6):
            kandidati.append((z["cas"], f.name, z))
    if not kandidati:
        return None
    return max(kandidati, key=lambda t: t[0])


def g2_horizonty():
    H = (12, 24, 36)
    data, soubory = {}, {}
    for m, *_ in G2_MODELY:
        nalez = nejnovejsi(m) or (nejnovejsi("lgbm_c") if m == "lgbm" else None)
        if nalez is None:
            raise FileNotFoundError(f"results/: chybí běh {m} s verzí {VERZE}")
        soubory[m] = nalez[1]
        v = {(r["cil"], r["horizont"]): r["mae_povodne"] for r in nalez[2]["vysledky"]}
        data[m] = {c: [v[(c, h)] for h in H] for c in ("decin", "usti")}
        kontrola(f"G2 průměr {m}", np.mean([v[k] for k in v]), G2_PRUMERY[m])
    for (m, c), cekano in G2_KONTROLA.items():
        for h, a, b in zip(H, data[m][c], cekano):
            kontrola(f"G2 {m} {c} {h} h", a, b)
    pomer = [j / r for c in ("decin", "usti") for j, r in zip(data["jako_ted"][c], data["ridge"][c])]
    if 2 <= min(pomer) and max(pomer) <= 3:
        titulek = f"Lineární regrese chybuje 2–3× méně než {JAKO_TED}"
    else:
        titulek = "Chyba modelů podle toho, jak daleko dopředu předpovídáme"
    fig, _ = graf(titulek, rect=None)
    osy = [fig.add_axes((0.09, 0.13, 0.415, 0.61)), fig.add_axes((0.565, 0.13, 0.415, 0.61))]
    for ax, c, nazev in zip(osy, ("decin", "usti"), ("Děčín", "Ústí nad Labem")):
        for m, popis, barva, lw, ls in G2_MODELY:
            hl = m in ("ridge", "jako_ted")
            ax.plot(H, data[m][c], color=barva, lw=lw, ls=ls, marker="o", ms=10 if hl else 8, mec="white", mew=2,
                    label=popis, zorder=4 if m == "ridge" else 3)
        for h, v in zip(H, data["ridge"][c]):
            ax.annotate(cislo(v), (h, v), xytext=(0, -13), textcoords="offset points", ha="center", va="top",
                        fontsize=15, weight="bold", color=INK, zorder=6,
                        bbox=dict(boxstyle="round,pad=0.12", facecolor="white", edgecolor="none", alpha=0.9))
        for h, v in zip(H, data["jako_ted"][c]):
            ax.annotate(cislo(v), (h, v), xytext=(0, 11), textcoords="offset points", ha="center", va="bottom",
                        fontsize=15, weight="bold", color=INK, zorder=6)
        ax.text(0.03, 0.97, nazev, transform=ax.transAxes, fontsize=19, weight="semibold", color=INK, va="top")
        ax.set_xticks(H, [f"{h} h" for h in H])
        ax.tick_params(axis="x", length=0)
        ax.set_xlim(7, 41)
        ax.set_ylim(0, 75)
        ax.yaxis.set_major_locator(MultipleLocator(10))
        osa_cisla(ax)
        ax.set_xlabel("předpověď dopředu")
    osy[0].set_ylabel(CHYBA)
    osy[1].tick_params(labelleft=False)
    h, lab = osy[0].get_legend_handles_labels()
    fig.legend(h, lab, loc="lower left", bbox_to_anchor=(0.085, 0.765), ncol=3, handlelength=2.6, columnspacing=1.6,
               fontsize=15)
    uloz(fig, "G2_chyba_podle_horizontu.png")
    return dict(soubory=soubory, data=data, pomer=(round(min(pomer), 2), round(max(pomer), 2)), titulek=titulek)


# G3 ---------------------------------------------------------------------------------------------------------------
G3_KONTROLA = {"ridge": (35.4, 28.1), "lgbm": (36.3, 28.1), "fyzika": (37.1, 32.3), "sit": (32.4, 26.7)}


def g3_zacatek_vzestupu():
    radky = [json.loads(r) for r in (RIDGE / "stanice_vsem/vysledky.jsonl").read_text(encoding="utf-8").splitlines()
             if r.strip()]

    def posledni(varianta):
        r = [z for z in radky if z["varianta"] == varianta and z["cast"] == "val"
             and (z["model"] != "lgbm" or z["seed"] == 42)]
        return r[-1]["decin24"]["mae_zacatek"], r[-1]["decin24"]["n_zacatek"]

    hodnoty, n = {}, set()
    for m in ("ridge", "lgbm", "fyzika"):
        (a, na), (b, nb) = posledni(f"{m}_12"), posledni(f"{m}_30")
        hodnoty[m] = (a, b)
        n |= {na, nb}
    S = nacti_json(SIT / "vysledky/beh1_a_b.json")
    sit = {v: [z["val"]["decin24"]["mae_zacatek"] for z in S if z["varianta"] == v] for v in "ab"}
    n |= {z["val"]["decin24"]["n_zacatek"] for z in S}
    hodnoty["sit"] = (float(np.mean(sit["a"])), float(np.mean(sit["b"])))
    for m, (a, b) in G3_KONTROLA.items():
        kontrola(f"G3 {m} 12 stanic", hodnoty[m][0], a)
        kontrola(f"G3 {m} 30 stanic", hodnoty[m][1], b)
    vsechny_lepsi = all(b < a for a, b in hodnoty.values())
    titulek = "Nové stanice vidí vlnu dřív" if vsechny_lepsi else "Chyba na začátku vzestupu před a po přidání stanic"
    fig, ax = graf(titulek, (0.09, 0.15, 0.88, 0.64))
    poradi = [("ridge", "lineární regrese"), ("lgbm", "LightGBM"), ("fyzika", "fyzikální model\n(zapojeno 8 z 18)"),
              ("sit", "neuronová síť\n(průměr 3 běhů)")]
    x = np.arange(len(poradi))
    s = 0.36
    a = [hodnoty[m][0] for m, _ in poradi]
    b = [hodnoty[m][1] for m, _ in poradi]
    ax.bar(x - s / 2 - 0.01, a, s, color=MODRA_SVETLA, label="12 týmových stanic")
    ax.bar(x + s / 2 + 0.01, b, s, color=MODRA, label="+ 18 nových stanic (30 celkem)")
    for xi, v in zip(x - s / 2 - 0.01, a):
        ax.text(xi, v + 0.6, cislo(v), ha="center", va="bottom", fontsize=16, weight="semibold", color=INK)
    for xi, v in zip(x + s / 2 + 0.01, b):
        ax.text(xi, v + 0.6, cislo(v), ha="center", va="bottom", fontsize=16, weight="semibold", color=INK)
    ax.set_xticks(x, [p for _, p in poradi], color=INK)
    ax.tick_params(axis="x", length=0)
    ax.set_xlim(-0.6, len(poradi) - 0.4)
    ax.set_ylim(0, 42)
    ax.yaxis.set_major_locator(MultipleLocator(10))
    osa_cisla(ax)
    ax.set_ylabel("chyba na začátku vzestupu (cm)")
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, handlelength=1.2)
    uloz(fig, "G3_zacatek_vzestupu_stanice.png")
    return dict(hodnoty={m: (round(a, 2), round(b, 2)) for m, (a, b) in hodnoty.items()}, sit=sit, n_zacatek=n,
                titulek=titulek)


# G4 ---------------------------------------------------------------------------------------------------------------
H4 = 24


def g4_cerven_2013():
    F = pd.read_csv(RIDGE / "stanice_vsem/lofo_foldy.csv")
    F = F[(F.horizont == H4) & F.povoden.str.startswith("2013-06")]
    f = F.loc[F.vrchol_cm.idxmax()]  # 2013-06-05, vrchol 1072 cm (druhá červnová vlna 2013-06-26 má 548 cm)
    oof = {n: pd.read_parquet(RIDGE / f"zlepseni/oof/{n}.parquet") for n in ("ridge_12", "ridge_30", "lgbm_30")}
    a, b, c = oof["ridge_12"], oof["ridge_30"], oof["lgbm_30"]
    for d in (b, c):
        assert len(d) == len(a) and (d.fold.to_numpy() == a.fold.to_numpy()).all() \
            and (d.cas.to_numpy() == a.cas.to_numpy()).all() and (d.y.to_numpy() == a.y.to_numpy()).all()
    m = (a.fold == f.fold).to_numpy()
    cas, y, tym = a.cas[m], a.y.to_numpy()[m], a.pred.to_numpy()[m]
    g3 = 0.5 * b.pred.to_numpy()[m] + 0.5 * c.pred.to_numpy()[m]
    assert cas.min() == pd.Timestamp(f.okno_od) and cas.max() == pd.Timestamp(f.okno_do) and len(cas) == f.radku_okno
    e_tym, e_g3 = float(np.abs(tym - y).mean()), float(np.abs(g3 - y).mean())
    tym_json = next(r for r in nacti_json(RIDGE / "zlepseni/vysledky_C.json") if r["nazev"] == "ridge_12")
    g3_json = next(r for r in nacti_json(RIDGE / "zlepseni/vysledky_G34.json") if r["nazev"].startswith("G3"))
    for co, e, z in (("týmový Ridge", e_tym, tym_json), ("G3", e_g3, g3_json)):
        if abs(e - z["po_povodnich"][f.povoden]) > 0.1:
            NESEDI.append(f"G4 {co}: spočítáno {cislo(e, 2)}, ve vysledky_*.json {z['po_povodnich'][f.povoden]}")
    # kontrola y: skutečná hladina v Děčíně v čase vydání + 24 h (data/external/labe_hodinove.parquet)
    L = pd.read_parquet(PREZ / "data/external/labe_hodinove.parquet", columns=["decin_H"]).decin_H
    assert np.allclose(L.reindex(cas + pd.Timedelta(hours=H4)).to_numpy(), y)
    e_jako_ted = float(np.abs(L.reindex(cas).to_numpy() - y).mean())

    t = (cas + pd.Timedelta(hours=H4)).dt.tz_convert("Europe/Prague").dt.tz_localize(None)
    if e_g3 < e_tym:
        titulek = "Červen 2013: G3 blíž skutečnosti než týmový model"
    else:
        titulek = "Červen 2013: G3 a týmový model proti skutečnosti"
    fig, ax = graf(titulek, (0.09, 0.13, 0.80, 0.72))
    for n, (spa, barva) in enumerate(zip((400, 490, 560), STUPNE), 1):
        ax.axhline(spa, color=barva, lw=2, zorder=1)
        ax.text(1.01, spa, f"{n}. stupeň", transform=ax.get_yaxis_transform(), ha="left", va="center", fontsize=14,
                color=INK2)
    ax.plot(t, y, color=INK, lw=3.2, label="skutečnost", zorder=4)
    ax.plot(t, tym, color=SEDA, lw=2.6, label=f"týmový model (12 stanic): chyba {cislo(e_tym)} cm", zorder=3)
    ax.plot(t, g3, color=MODRA, lw=3.2, label=f"G3 = ½ regrese + ½ LightGBM (30 stanic): chyba {cislo(e_g3)} cm", zorder=5)
    i = int(np.argmax(y))
    ax.annotate(f"vrchol {cislo(y[i], 0)} cm", (t.iloc[i], y[i]), xytext=(14, 4), textcoords="offset points",
                ha="left", va="bottom", fontsize=15, color=INK)
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{mdates.num2date(v).day}. {mdates.num2date(v).month}."))
    ax.set_xlim(t.iloc[0], t.iloc[-1])
    dole = min(y.min(), tym.min(), g3.min())
    ax.set_ylim(np.floor(dole / 100) * 100 - 150, 1200)  # místo pro legendu pod 1. stupněm
    ax.yaxis.set_major_locator(MultipleLocator(200))
    osa_cisla(ax)
    ax.set_ylabel("hladina v Děčíně (cm)")
    ax.set_xlabel("datum (český čas), předpověď vydaná 24 h předem")
    ax.legend(loc="lower right", handlelength=2.4, framealpha=0.95, edgecolor="none")
    uloz(fig, "G4_cerven_2013_g3_vs_tym.png")
    return dict(fold=int(f.fold), povoden=f.povoden, okno=(str(t.iloc[0]), str(t.iloc[-1])), radku=int(m.sum()),
                mae_tym=round(e_tym, 2), mae_g3=round(e_g3, 2), mae_jako_ted=round(e_jako_ted, 2),
                json_tym=tym_json["po_povodnich"][f.povoden], json_g3=g3_json["po_povodnich"][f.povoden],
                vrchol=(str(t.iloc[i]), y[i]), pred_vrchol_tym=round(tym[i], 1), pred_vrchol_g3=round(g3[i], 1),
                max_tym=round(tym.max(), 1), max_g3=round(g3.max(), 1), titulek=titulek)


if __name__ == "__main__":
    CIL.mkdir(exist_ok=True)
    print("G1:", g1_stanice())
    print("G2:", g2_horizonty())
    print("G3:", g3_zacatek_vzestupu())
    print("G4:", g4_cerven_2013())
    print("nesedí s kontrolními čísly:", NESEDI or "nic")
