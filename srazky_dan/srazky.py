"""Šestihodinové srážky ze synoptických zpráv (NOAA ISD) → hodinové příznaky bez informace z budoucnosti.

python srazky.py      postaví data/srazky_6h.parquet (není v Gitu) z cache/ (stahni_isd.py) a vypíše pokrytí

Z pole AA1–AA4 (délka období v h, úhrn v 0,1 mm, podmínka, kvalita) se berou 6h a 12h úhrny zpráv SYNOP v termínech
00, 06, 12, 18 UTC. České stanice hlásí 6h úhrn v 00 a 12 UTC a 12h úhrn v 06 a 18 UTC, proto:
- 6h díl končící v 06 (18) = 12h úhrn v 06 (18) − 6h úhrn v 00 (12); když 6h úhrn chybí, dělí se 12h úhrn napůl.
  Tím se díl končící v 00 (12) „dozví“ až v 06 (18) – do příznaků v 01–06 (13–18) proto vstupuje jen to, co se
  vědělo v 00 (12), tedy chybějící = NaN (predbezne), a dorovnaná hodnota až od 07 (19) (konecne).
- stopové srážky (podmínka 2) = 0, kvalita 3, 7 (chybné) a podmínky 1, 4–8 (neměřeno, konec akumulace,
  smazané, chybějící období) = chybí, nesmyslně velké úhrny (6h > 150 mm, 12h > 250 mm) = chybí.
Úhrn patří ke konci měřeného období E a do modelu smí od E + 1 h. Příznak v hodině t: součet za W hodin
(W = 6, 12, 24, 48, 72) končící posledním termínem E ≤ t − 1 h, jen ze zpráv s koncem ≤ E. Nejstarší měření,
které příznak použije, je tedy t − 1 − 5 − 72 = t − 78 h (NEJSTARSI_SR).
Po stanicích se počítá součet, ve skupině průměr stanic, které ho mají (NaN, když žádná). Do skupin jdou jen
stanice s úplnými zprávami (vyber()).
"""
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

ZDE = Path(__file__).resolve().parent
CACHE = ZDE / "cache/global-hourly"
SOUBOR = ZDE / "data/srazky_6h.parquet"
OD, DO = "2006-01-01", "2025-12-31"
OKNA = (6, 12, 24, 48, 72)
NEJSTARSI_SR = 78
ZPOZDENI = pd.Timedelta(hours=1)

# USAF: (název, dílčí povodí); „blizko“ = okolí Děčína, ostatní = dál proti proudu
STANICE = {
    "115020": ("Ústí nad Labem", "blizko"),
    "115090": ("Doksany", "blizko"),
    "114640": ("Milešovka", "blizko"),
    "116030": ("Liberec", "blizko"),  # povodí Nisy, ale hned u Jizerských hor a Ploučnice; Jizera synop nemá
    "114060": ("Cheb", "ohre"),
    "114140": ("Karlovy Vary", "ohre"),
    "114380": ("Tušimice", "ohre"),
    "114500": ("Plzeň-Mikulka", "berounka"),
    "114230": ("Přimda", "berounka"),
    "114570": ("Churáňov", "vltava"),
    "114870": ("Kocelovice", "vltava"),
    "115380": ("Temelín", "vltava"),
    "115460": ("České Budějovice", "vltava"),
    "115180": ("Praha-Ruzyně", "vltava"),
    "115200": ("Praha-Libuš", "vltava"),
    "116280": ("Košetice", "vltava"),  # Sázava (Želivka)
    "116590": ("Přibyslav", "vltava"),  # Sázava
    "116430": ("Pec pod Sněžkou", "horni_labe"),
    "116520": ("Pardubice", "horni_labe"),
    "116240": ("Čáslav", "horni_labe"),
    "116790": ("Ústí nad Orlicí", "horni_labe"),
}
SPATNA_KVALITA = set("37")  # chybné; podezřelé (2, 6) vznikají hlavně z nesouladu 12h a 24h úhrnu o 0,1 mm
PLATNE_PODMINKY = set("239E")  # 3 = v novějších souborech běžně změřený nenulový úhrn (ověřeno na zprávách SYNOP v REM)
MAX_MM = {6: 150, 12: 250}
MIN_POKRYTI = 0.8


def nacti_zpravy(usaf):
    """Termínové zprávy 00/06/12/18 UTC jedné stanice: DataFrame (index čas UTC) se sloupci u6, u12 v mm."""
    casti = []
    for rok in range(int(OD[:4]), int(DO[:4]) + 1):
        f = CACHE / str(rok) / f"{usaf}99999.csv"
        if not f.exists():
            continue
        hlava = pd.read_csv(f, nrows=0).columns
        aa = [c for c in ("AA1", "AA2", "AA3", "AA4") if c in hlava]
        d = pd.read_csv(f, usecols=["DATE", "REPORT_TYPE", *aa], dtype=str)
        t = pd.to_datetime(d.DATE, utc=True)
        d = d[(t.dt.minute == 0) & t.dt.hour.isin([0, 6, 12, 18]).to_numpy()
              & d.REPORT_TYPE.str.strip().isin(["FM-12", "SY-MT", "SY-SA", "SY-AE"])]
        for c in aa:
            p = d[c].dropna().str.split(",", expand=True)
            if p.empty:
                continue
            p.columns = ["obdobi", "uhrn", "podminka", "kvalita"]
            obdobi = p.obdobi.astype(int)
            mm = p.uhrn.astype(float).where(p.uhrn != "9999") / 10
            mm = mm.where(p.podminka != "2", 0.0)  # stopové srážky
            ok = p.podminka.isin(PLATNE_PODMINKY) & ~p.kvalita.isin(SPATNA_KVALITA)
            for h in (6, 12):
                v = mm.where(ok & (obdobi == h) & (mm <= MAX_MM[h]))
                v = v[obdobi == h]
                casti.append(pd.DataFrame({"t": pd.to_datetime(d.loc[v.index, "DATE"], utc=True), f"u{h}": v}))
    if not casti:
        return pd.DataFrame(columns=["u6", "u12"], dtype=float)
    z = pd.concat(casti)
    # víc záznamů téhož termínu: platná hodnota má přednost před chybějící
    return z.groupby("t")[["u6", "u12"]].first().reindex(columns=["u6", "u12"])


def sestihodinove(z):
    """Šestihodinové díly končící v termínu E. predbezne = co se vědělo v čase E, konecne = po dorovnání
    z 12h úhrnu (díl končící v 00/12 se dorovná v 06/18, tedy o 6 h později)."""
    sit = pd.date_range(OD, f"{DO} 18:00", freq="6h", tz="UTC")
    u6, u12 = z.u6.reindex(sit), z.u12.reindex(sit)
    pred6 = u6.shift(1)  # 6h úhrn v termínu o 6 h dřív (00 nebo 12)
    # v termínu 06/18 s 12h úhrnem se rozdělí 12 h na dva díly: díl končící teď a díl končící o 6 h dřív
    ted = u6.where(u6.notna(), (u12 - pred6).clip(lower=0).where(pred6.notna(), u12 / 2))
    driv = pred6.where(pred6.notna(), (u12 - u6).clip(lower=0).where(u6.notna(), u12 / 2))
    k = np.isin(sit.hour, (6, 18)) & u12.notna().to_numpy()
    predbezne = u6.copy()
    konecne = u6.copy()
    konecne[k] = ted[k]
    konecne.iloc[np.flatnonzero(k) - 1] = driv[k].to_numpy()
    return pd.DataFrame({"predbezne": predbezne, "konecne": konecne})


def soucty_v_terminech(s):
    """S_W(E) = srážky za W hodin končících v termínu E, jen ze zpráv s koncem ≤ E (index = E)."""
    out = {}
    hod = s.index.hour
    for w in OKNA:
        k = w // 6
        # starší díly (E − 6 a dál) jsou v termínu E vždy dorovnané: dorovnání přijde nejpozději v příštím 06/18
        starsi = s.konecne.shift(1).rolling(k - 1, min_periods=k - 1).sum() if k > 1 else 0.0
        posledni = np.where(np.isin(hod, (6, 18)), s.konecne, s.predbezne)
        out[w] = posledni + starsi
    return pd.DataFrame(out, index=s.index)


def hodinove(S):
    """Termínové součty → hodiny: v hodině t platí poslední termín E s E + 1 h ≤ t."""
    hodiny = pd.date_range(OD, f"{DO} 23:00", freq="h", tz="UTC")
    termin = (hodiny - ZPOZDENI).floor("6h")
    return pd.DataFrame(S.reindex(termin).to_numpy(), index=hodiny, columns=S.columns)


def priznaky_stanice(z):
    """Hodinové součty jedné stanice. Chybí-li v termínu zpráva, platí ještě součty z předchozího termínu
    (jen dopředu, nejvýš o 6 h starší), jinak NaN."""
    return hodinove(soucty_v_terminech(sestihodinove(z)).ffill(limit=1))


def vyber(pokryti):
    """Stanice s 6h úhrnem v 00/12 UTC aspoň v 80 % termínů v každém roce 2006–2020 (výběr bez testovacích let).

    U ostatních po roce ~2013 chybějí hlavně suché termíny (nuly ze zpráv BUFR se do ISD nedostaly): podíl kladných
    úhrnů mezi platnými stoupl z ~0,2 na 0,6–0,9, průměr skupiny by srážky nadhodnotil.
    """
    return [u for u in pokryti if pokryti.loc[2006:2020, u].min() >= MIN_POKRYTI]


def postav():
    po_stanicich, pokryti, kladne = {}, {}, {}
    for usaf in STANICE:
        z = nacti_zpravy(usaf)
        s = sestihodinove(z)
        po_stanicich[usaf] = priznaky_stanice(z)
        u6 = s.predbezne[np.isin(s.index.hour, (0, 12))]
        pokryti[usaf] = u6.notna().groupby(u6.index.year).mean()
        kladne[usaf] = (u6 > 0).groupby(u6.index.year).sum() / u6.notna().groupby(u6.index.year).sum()
    pokryti, kladne = pd.DataFrame(pokryti), pd.DataFrame(kladne)
    vybrane = vyber(pokryti)
    skupiny = pd.Series({u: STANICE[u][1] for u in vybrane})
    skupiny_vse = {g: list(skupiny.index[skupiny == g]) for g in skupiny.unique()}
    skupiny_vse["dal"] = list(skupiny.index[skupiny != "blizko"])
    sl = {}
    for g, cleny in skupiny_vse.items():
        for w in OKNA:
            sl[f"sr_{g}_{w}h"] = pd.concat([po_stanicich[u][w] for u in cleny], axis=1).mean(axis=1)
    P = pd.DataFrame(sl).astype("float32").rename_axis("cas")
    SOUBOR.parent.mkdir(exist_ok=True)
    P.to_parquet(SOUBOR)
    nazvy = {u: STANICE[u][0] for u in STANICE}
    pd.concat({"pokryti": pokryti, "podil_kladnych": kladne}, axis=1).rename(columns=nazvy).round(3).to_csv(
        ZDE / "vysledky/pokryti_stanic.csv", encoding="utf-8")
    return P, pokryti.rename(columns=nazvy), [nazvy[u] for u in vybrane], skupiny_vse


def otisk():
    return hashlib.sha1(SOUBOR.read_bytes()).hexdigest()[:8]


if __name__ == "__main__":
    P, pokryti, vybrane, skupiny = postav()
    pd.set_option("display.width", 250)
    print("podíl termínů 00/12 UTC s platným 6h úhrnem, nejmenší za 2006–2020:")
    print(pokryti.loc[2006:2020].min().round(2).to_string())
    print("vybrané:", vybrane)
    print("skupiny:", {g: [STANICE[u][0] for u in c] for g, c in skupiny.items()})
    print(f"{SOUBOR.relative_to(ZDE)}: {P.shape}, otisk {otisk()}")
    print("chybí (hodin):", P.isna().sum().to_dict())
