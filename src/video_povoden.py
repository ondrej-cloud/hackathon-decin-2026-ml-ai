"""Video povodně z 3D mapy (app/mapbox_mapa.py) pro úvod prezentace: hodina po hodině, střihy a přibližování podle hladiny.

Vlevo rozliv z předpovědi vydané 24 h předem, vpravo ze skutečné hladiny (režim porovnání), dole přehrávač s grafem.
Playwright nafotí každou hodinu jako snímek, ffmpeg je složí (mapa se prolíná, štítky a lišta zůstávají ostré).

Spuštění z kořene repa (Windows: `$env:PYTHONUTF8=1; .venv\\Scripts\\python -u src\\video_povoden.py`, Mac: `.venv/bin/python -u src/video_povoden.py`):
    python -u src/video_povoden.py --diag          # jen snímky začátku a konců záběrů do dočasné složky, na doladění kamery
    python -u src/video_povoden.py                 # celé natáčení, asi 5 minut, pak ffmpeg
    python -u src/video_povoden.py --jen-video     # jen ffmpeg z už natočených snímků
Volby: --povoden "6/2013" --cil decin --model ridge_bez2013 --od 2013-06-01T00:00 --do 2013-06-06T12:00 (český čas)
       --rezim headless|chromium|okno (prohlížeč; výchozí zkouší v tomhle pořadí)
Potřebuje MAPBOX_TOKEN v .env, Playwright (`pip install playwright`, Chrome v počítači nebo `playwright install chromium`) a ffmpeg.
Na Macu se stránka vykreslí v písmu San Francisco, na Windows v Interu. HTML s tokenem zůstává jen v dočasné složce.
"""
import argparse
import json
import platform
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd  # noqa: E402

import animace  # noqa: E402
import mapbox_mapa  # noqa: E402

TZ = "Europe/Prague"
POMALU = 4.0  # s na snímek; pomalejší režim prohlížeče vyměníme za další
LIMIT = 6000  # ms čekání na idle obou map u jednoho snímku

# Záběry pro Děčín 6/2013: k je číslo snímku (hodina od --od), kamera se uvnitř záběru plynule posouvá od "od" k "do".
# Střih je mezi záběry. "stred": None = kamera města z mapy (D.kamery). Jiná povodeň nebo město: doladit přes --diag.
ZABERY = [
    {"nazev": "celé město", "k_od": 0, "k_do": 50, "stred": None,
     "zoom": (13.6, 13.9), "bearing": (-10, -4), "pitch": 60},
    {"nazev": "ohyb řeky a centrum", "k_od": 51, "k_do": 90, "stred": [14.2085, 50.7745],
     "zoom": (14.35, 14.65), "bearing": (-28, -20), "pitch": 62},
    {"nazev": "nábřeží zblízka", "k_od": 91, "k_do": 114, "stred": [14.2135, 50.7770],
     "zoom": (15.0, 15.3), "bearing": (22, 30), "pitch": 64},
    {"nazev": "vrchol mezi domy", "k_od": 115, "k_do": 132, "stred": [14.2150, 50.7762],
     "zoom": (15.45, 15.8), "bearing": (-38, -28), "pitch": 66},
]

CEKEJ = """() => {
  window.cekej = limit => new Promise(res => {
    let hotovo = false;
    const konec = v => { if (!hotovo) { hotovo = true; res(v); } };
    const ms = (typeof mapaB !== 'undefined' && mapaB) ? [mapaA, mapaB] : [mapaA];
    requestAnimationFrame(() => {
      if (ms.every(m => m.loaded() && m.areTilesLoaded() && !m.isMoving())) return konec('hotovo');
      let zbyva = ms.length;
      ms.forEach(m => m.once('idle', () => { if (--zbyva === 0) konec('idle'); }));
    });
    setTimeout(() => konec('limit'), limit);
  });
  const c = document.createElement('canvas'), gl = c.getContext('webgl2') || c.getContext('webgl');
  if (!gl) return 'bez WebGL';
  const d = gl.getExtension('WEBGL_debug_renderer_info');
  return d ? gl.getParameter(d.UNMASKED_RENDERER_WEBGL) : 'WebGL (neznámý renderer)';
}"""
# bez úvodu a bočních boxů, bez podniků a dopravních popisků; porovnání zapnuté (vlevo předpověď, vpravo skutečnost)
SKRYJ = """(mesto) => {
  zavriUvod(); pauza(); porovnat(true);
  document.querySelector('.uvod')?.remove();
  for (const id of ['vlevo', 'vpravo']) document.getElementById(id)?.remove();
  document.querySelector('.napoveda')?.remove();
  const n = document.getElementById('najeti'); if (n) n.style.display = 'none';
  if (typeof N !== 'undefined') N.poi = false;
  for (const m of [mapaA, mapaB].filter(Boolean)) {
    try { m.setConfigProperty('basemap', 'showPointOfInterestLabels', false); m.setConfigProperty('basemap', 'showTransitLabels', false); }
    catch (e) { /* styl se teprve načítá, konfigurace() ho nastaví při načtení */ }
  }
  window.STRED = D.kamery[mesto].center;
  const lista = document.getElementById('lista') || document.querySelector('.lista, .prehravac');
  const vyska = lista ? Math.round(lista.getBoundingClientRect().height) + 20 : 190;
  window.PAD = {top: 0, bottom: vyska, left: 0, right: 0};
  const s = stavPrehravace();
  s.lista_od = lista ? Math.floor(lista.getBoundingClientRect().top / 2) * 2 : null;
  s.pismo = getComputedStyle(document.body).fontFamily.split(',')[0];
  s.mapaB = !!mapaB;
  return s;
}"""
KROK = """({i, kamera, limit}) => {
  skoc(i);
  const k = {center: kamera.center || STRED, zoom: kamera.zoom, pitch: kamera.pitch, bearing: kamera.bearing, padding: PAD};
  mapaA.jumpTo(k);
  if (mapaB) mapaB.jumpTo(k);
  return cekej(limit).then(stav => {
    const s = stavPrehravace();
    return {stav, hodina: s.hodina, datum: s.datum, h: s.skutecnost, p: s.predpoved};
  });
}"""


def tisk(*a):
    print(*a, flush=True)


def cisty(text):
    return re.sub(r"(access_token=|pk\.)[A-Za-z0-9._-]+", r"\1***", str(text))


def zaber(k):
    for z in ZABERY:
        if z["k_od"] <= k <= z["k_do"]:
            return z
    return ZABERY[-1]


def kamera(k):
    z = zaber(k)
    t = 0 if z["k_do"] == z["k_od"] else (k - z["k_od"]) / (z["k_do"] - z["k_od"])
    t = max(0.0, min(1.0, t))
    lin = lambda a: a[0] + (a[1] - a[0]) * t  # noqa: E731
    return {"center": z["stred"], "zoom": round(lin(z["zoom"]), 4), "bearing": round(lin(z["bearing"]), 3),
            "pitch": z["pitch"], "zaber": z["nazev"]}


class Natoceni:
    def __init__(self, a):
        self.a = a
        self.tmp = Path(tempfile.gettempdir()) / f"video_povoden_{a.cil}"
        self.snimky = self.tmp / "snimky"
        self.snimky.mkdir(parents=True, exist_ok=True)
        self.html = self.tmp / "povoden.html"
        self.log = self.tmp / "log.json"
        slug = re.sub(r"\W+", "_", a.povoden.split()[0]).strip("_")
        self.video = ROOT / "docs/grafy" / f"video_povoden_{slug}_{a.cil}.mp4"
        self.web_video = ROOT / "web/prezentace/video" / f"povoden_{slug.split('_')[-1]}_{a.cil}_1080.mp4"
        self.poster = ROOT / "web/prezentace/grafy" / f"video_{slug.split('_')[-1]}_poster.jpg"
        self.mesto = mapbox_mapa.MESTA[a.cil]
        self.lista_od = 852
        if platform.system() == "Windows":
            self.gpu = ["--use-gl=angle", "--use-angle=d3d11", "--enable-gpu", "--ignore-gpu-blocklist", "--allow-file-access-from-files"]
        else:
            self.gpu = ["--enable-gpu", "--ignore-gpu-blocklist", "--allow-file-access-from-files"]
        self.rezimy = {"headless": {"headless": True, "channel": "chrome"}, "chromium": {"headless": True},
                       "okno": {"headless": False, "channel": "chrome"}}

    def stranka(self):
        od, do = animace.okno(self.a.povoden)
        pisma = (ROOT / "web/fonts").as_uri() + "/"
        self.html.write_text(mapbox_mapa.html_animace(od, do, self.a.cil, self.a.model, self.mesto, pisma=pisma), encoding="utf-8")
        hodina = pd.Timedelta(hours=1)
        od_videa = pd.Timestamp(self.a.od, tz=TZ)
        do_videa = pd.Timestamp(self.a.do, tz=TZ)
        i0, i1 = int((od_videa - od) / hodina), int((do_videa - od) / hodina)
        K = int((do - od) / hodina)
        i0, i1 = max(0, i0), min(K, i1)
        tisk(f"okno {od} až {do} (UTC), K={K}, snímky {i0}..{i1} ({i1 - i0 + 1} hodin), dočasná složka {self.tmp}")
        return i0, i1

    def otevri(self, pw, rezim):
        try:
            b = pw.chromium.launch(args=self.gpu, **self.rezimy[rezim])
        except Exception as e:  # noqa: BLE001
            tisk(f"{rezim}: prohlížeč nejde spustit ({cisty(e)[:120]})")
            return None, None, [], {"rezim": rezim}
        page = b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
        chyby = []
        page.on("console", lambda m: m.type == "error" and chyby.append(f"console: {cisty(m.text)[:200]}"))
        page.on("pageerror", lambda e: chyby.append(f"pageerror: {cisty(e)[:200]}"))
        page.goto(self.html.as_uri(), timeout=90000)
        page.wait_for_function("() => typeof mapaA !== 'undefined'", timeout=60000)
        renderer = page.evaluate(CEKEJ)
        t = time.time()
        stav = page.evaluate("() => cekej(90000)")
        info = {"rezim": rezim, "renderer": renderer, "nacteni_s": round(time.time() - t, 1), "stav_nacteni": stav}
        if stav == "limit":
            tisk(f"{rezim}: mapa se do 90 s nenačetla, chyby: {chyby[:5]}")
            b.close()
            return None, None, chyby, info
        p = page.evaluate(SKRYJ, self.mesto)
        if p.get("lista_od"):
            self.lista_od = p["lista_od"]
        page.evaluate("() => cekej(30000)")
        tisk(f"{rezim}: {renderer}, první idle za {info['nacteni_s']} s, přehrávač start={p['start']} vrchol={p['vrchol']} "
             f"konec={p['konec']} rezim={p['rezim']} písmo={p.get('pismo')} lišta od {self.lista_od} px, chyby: {chyby[:3]}")
        return b, page, chyby, info

    def natoc(self, i0, i1, rezim):
        from playwright.sync_api import sync_playwright
        for soubor in self.snimky.glob("*.png"):
            soubor.unlink()
        with sync_playwright() as pw:
            b, page, chyby, info = self.otevri(pw, rezim)
            if page is None:
                return None
            strihy = {z["k_od"] for z in ZABERY}
            page.evaluate(KROK, {"i": i0, "kamera": kamera(0), "limit": 20000})
            page.evaluate("() => cekej(10000)")
            casy, zaznamy = [], []
            for k, i in enumerate(range(i0, i1 + 1)):
                t = time.time()
                kam = kamera(k)
                vysl = page.evaluate(KROK, {"i": i, "kamera": kam, "limit": 20000 if k in strihy else LIMIT})
                if k in strihy:
                    page.evaluate("() => cekej(6000)")
                page.screenshot(path=str(self.snimky / f"{k:04d}.png"))
                casy.append(time.time() - t)
                zaznamy.append({"k": k, "i": i, "zaber": kam["zaber"], **vysl, "s": round(casy[-1], 2)})
                if k % 12 == 0 or k < 3 or k in strihy:
                    tisk(f"  {k:3d} i={i} {vysl['datum']} {vysl['h']} cm / předpověď {vysl['p']} cm  {kam['zaber']}  {vysl['stav']}  {casy[-1]:.1f} s")
                if rezim != "okno" and k == 2 and sum(casy) / len(casy) > POMALU:
                    tisk(f"{rezim} je pomalý ({sum(casy) / 3:.1f} s na snímek), zkusím další režim")
                    b.close()
                    return None
            b.close()
        prumer = sum(casy) / len(casy)
        tisk(f"natočeno {len(casy)} snímků, průměr {prumer:.2f} s na snímek, chyby stránky: {chyby[:5]}")
        return info | {"prumer_s": round(prumer, 2), "max_s": round(max(casy), 2), "snimky": len(casy),
                       "od": zaznamy[0]["datum"], "do": zaznamy[-1]["datum"], "h_od": zaznamy[0]["h"], "h_do": zaznamy[-1]["h"],
                       "limity": sum(z["stav"] == "limit" for z in zaznamy), "chyby": chyby[:5], "lista_od": self.lista_od,
                       "zaznamy": zaznamy}

    def diag(self, i0, rezimy):
        """Snímek začátku prvního záběru a konce každého záběru: diag_<n>_<nazev>.png v dočasné složce."""
        from playwright.sync_api import sync_playwright
        body = [(0, "zacatek")] + [(z["k_do"], z["nazev"].replace(" ", "_")) for z in ZABERY]
        for rezim in rezimy:
            with sync_playwright() as pw:
                b, page, chyby, info = self.otevri(pw, rezim)
                if page is None:
                    continue
                for n, (k, nazev) in enumerate(body):
                    t = time.time()
                    vysl = page.evaluate(KROK, {"i": i0 + k, "kamera": kamera(k), "limit": 20000})
                    page.evaluate("() => cekej(6000)")
                    page.screenshot(path=str(self.tmp / f"diag_{n}_{nazev}.png"))
                    tisk(f"  diag {n} k={k} {vysl['datum']} {vysl['h']} cm / {vysl['p']} cm {kamera(k)} {vysl['stav']} {time.time() - t:.1f} s")
                b.close()
                tisk(f"snímky diagnostiky: {self.tmp}")
                return

    def filtr(self):
        """Tři pásy: štítky nahoře (0 až 72 px) a lišta dole ostré, mapa mezi nimi prolínaná na 30 fps."""
        h = 1080
        lista = self.lista_od if 400 < self.lista_od < 1000 else 852
        lista -= lista % 2
        return ("-filter_complex",
                f"[0:v]split=3[a][b][c];[a]crop=1920:72:0:0,fps=30[t];[b]crop=1920:{lista - 72}:0:72,minterpolate=fps=30:mi_mode=blend[m];"
                f"[c]crop=1920:{h - lista}:0:{lista},fps=30[l];[t][m][l]vstack=inputs=3,format=yuv420p")

    def slozit(self, crf=19):
        self.video.parent.mkdir(parents=True, exist_ok=True)
        prikaz = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", "5.5", "-i", str(self.snimky / "%04d.png"), *self.filtr(),
                  "-c:v", "libx264", "-crf", str(crf), "-preset", "slow", "-movflags", "+faststart", str(self.video)]
        tisk("ffmpeg: master, crf", crf)
        v = subprocess.run(prikaz, capture_output=True, text=True)
        if v.returncode:
            tisk(v.stderr[-800:])
            raise SystemExit("ffmpeg selhal")

    def web_verze(self):
        self.web_video.parent.mkdir(parents=True, exist_ok=True)
        crf = 23
        for crf in (23, 25, 27):
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(self.video), "-c:v", "libx264", "-crf", str(crf),
                            "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(self.web_video)], check=True)
            if self.web_video.stat().st_size <= 22e6:
                break
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "22", "-i", str(self.web_video), "-frames:v", "1", "-q:v", "3",
                        str(self.poster)], check=True)
        for n, ss in ((1, 1), (2, 9), (3, 17), (4, 23)):
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(ss), "-i", str(self.web_video), "-frames:v", "1",
                            str(self.tmp / f"kontrola_{n}.png")], check=True)
        tisk(f"web: {self.web_video} ({self.web_video.stat().st_size / 1e6:.1f} MB, crf {crf}), poster {self.poster}, "
             f"kontrolní snímky {self.tmp}")

    @staticmethod
    def proved(soubor):
        p = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                            "stream=width,height,r_frame_rate,nb_frames,codec_name:format=duration,size", "-of", "json", str(soubor)],
                           capture_output=True, text=True)
        j = json.loads(p.stdout)
        s, f = j["streams"][0], j["format"]
        out = {"rozliseni": f"{s['width']}x{s['height']}", "fps": s["r_frame_rate"], "kodek": s["codec_name"],
               "trvani_s": round(float(f["duration"]), 2), "velikost_mb": round(int(f["size"]) / 1e6, 2), "snimku_videa": s.get("nb_frames")}
        tisk("ffprobe", Path(soubor).name, out)
        return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--povoden", default="6/2013")
    ap.add_argument("--cil", default="decin", choices=["decin", "usti"])
    ap.add_argument("--model", default="ridge_bez2013")
    ap.add_argument("--od", default="2013-06-01T00:00", help="začátek videa, český čas")
    ap.add_argument("--do", dest="do", default="2013-06-06T12:00", help="konec videa, český čas")
    ap.add_argument("--rezim", choices=["headless", "chromium", "okno"])
    ap.add_argument("--diag", action="store_true")
    ap.add_argument("--jen-video", action="store_true")
    a = ap.parse_args()
    n = Natoceni(a)
    i0, i1 = n.stranka()
    rezimy = [a.rezim] if a.rezim else list(n.rezimy)
    if a.diag:
        return n.diag(i0, rezimy)
    if not a.jen_video:
        vysledek = None
        for rezim in rezimy:
            vysledek = n.natoc(i0, i1, rezim)
            if vysledek:
                break
        if not vysledek:
            raise SystemExit("žádný režim prohlížeče nefunguje (Chrome nebo `playwright install chromium`, GPU)")
        n.log.write_text(json.dumps(vysledek, ensure_ascii=False, indent=1), encoding="utf-8")
    elif n.log.exists():
        n.lista_od = json.loads(n.log.read_text(encoding="utf-8")).get("lista_od", n.lista_od)
    n.slozit()
    n.web_verze()
    log = json.loads(n.log.read_text(encoding="utf-8")) if n.log.exists() else {}
    log["video"] = {"master": n.proved(n.video), "web": n.proved(n.web_video)}
    n.log.write_text(json.dumps(log, ensure_ascii=False, indent=1), encoding="utf-8")
    tisk("HOTOVO")


if __name__ == "__main__":
    main()
