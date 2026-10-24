"""Video povodně z 3D mapy (app/mapbox_mapa.py) pro úvod prezentace: hodina po hodině, kamera se plynule přibližuje s hladinou.

Rozliv ze změřené hladiny, dole přehrávač s grafem; boční boxy skryté. Playwright nafotí KROKU snímků na každou hodinu
(voda se mění po hodinách, kamera jede jedním plynulým průletem bez střihů, zpomalí jen na začátku a na konci) a ffmpeg
je složí beze změny, takže je obraz ostrý (60 fps, žádné prolínání). Vlevo nahoře je skleněná pilulka s datem a hodinou, boční boxy jsou skryté.
Volba --porovnani zapne režim vlevo předpověď 24 h předem, vpravo skutečnost (v prezentaci se nepoužívá).

Spuštění z kořene repa (Windows: `$env:PYTHONUTF8=1; .venv\\Scripts\\python -u src\\video_povoden.py`, Mac: `.venv/bin/python -u src/video_povoden.py`):
    python -u src/video_povoden.py --diag          # jen snímky začátku a konců záběrů do dočasné složky, na doladění kamery
    python -u src/video_povoden.py                 # celé natáčení, asi 5 minut, pak ffmpeg
    python -u src/video_povoden.py --jen-video     # jen ffmpeg z už natočených snímků
Volby: --povoden "6/2013" --cil decin --model ridge_bez2013 --od 2013-06-01T00:00 --do 2013-06-06T12:00 (český čas)
       --rezim headless|chromium|okno (prohlížeč; výchozí zkouší v tomhle pořadí) --porovnani (vlevo předpověď, vpravo skutečnost)
Potřebuje MAPBOX_TOKEN v .env, Playwright (`pip install playwright`, Chrome v počítači nebo `playwright install chromium`) a ffmpeg.
Na Macu se stránka vykreslí v písmu San Francisco, na Windows v Interu. HTML s tokenem zůstává jen v dočasné složce.
"""
import argparse
import bisect
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
LIMIT = 6000  # ms čekání na idle mapy u jednoho snímku
KROKU = 11  # snímků na hodinu povodně; 133 hodin × 11 = 1 463 snímků, při 60 fps 24 s
FPS = 60

# Průlet kamery pro Děčín 6/2013: k je hodina od --od, kamera prochází klíčovými pozicemi bez střihů. Zoom roste s hladinou
# (od celého města k domům Starého Města) a kamera se celou dobu pomalu stáčí jedním směrem. Jiná povodeň nebo město:
# doladit pozice přes --diag.
KLICE = [
    {"nazev": "celé město", "k": 0, "stred": [14.2040, 50.7730], "zoom": 13.6, "bearing": -10, "pitch": 58},
    {"nazev": "město, voda stoupá", "k": 42, "stred": [14.2055, 50.7736], "zoom": 13.95, "bearing": -14, "pitch": 60},
    {"nazev": "ohyb řeky a centrum", "k": 78, "stred": [14.2085, 50.7745], "zoom": 14.6, "bearing": -21, "pitch": 62},
    {"nazev": "nábřeží zblízka", "k": 106, "stred": [14.2128, 50.7760], "zoom": 15.25, "bearing": -27, "pitch": 64},
    {"nazev": "vrchol mezi domy", "k": 132, "stred": [14.2150, 50.7762], "zoom": 15.8, "bearing": -32, "pitch": 66},
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
SKRYJ = """({mesto, porovnani}) => {
  zavriUvod(); pauza(); porovnat(!!porovnani);
  document.querySelector('.uvod')?.remove();
  // boxy jen skrýt: panelAnimace() do nich zapisuje (#p-den), po remove() by každý snímek vyhodil chybu a smyčka by umřela
  for (const id of ['vlevo', 'vpravo']) { const e = document.getElementById(id); if (e) e.style.display = 'none'; }
  document.querySelector('.napoveda')?.remove();
  const n = document.getElementById('najeti'); if (n) n.style.display = 'none';
  if (typeof N !== 'undefined') N.poi = false;
  for (const m of [mapaA, mapaB].filter(Boolean)) {
    try { m.setConfigProperty('basemap', 'showPointOfInterestLabels', false); m.setConfigProperty('basemap', 'showTransitLabels', false); }
    catch (e) { /* styl se teprve načítá, konfigurace() ho nastaví při načtení */ }
  }
  const pil = document.createElement('div');
  pil.id = 'video-datum'; pil.className = 'sklo';
  pil.style.cssText = 'position:absolute;top:18px;left:18px;z-index:5;padding:14px 22px;border-radius:999px;font:700 30px/1 -apple-system,BlinkMacSystemFont,"SF Pro Display","SF Pro Text","Helvetica Neue",Inter,Helvetica,sans-serif;color:#1d1d1f;letter-spacing:-0.02em;white-space:nowrap;font-variant-numeric:tabular-nums';
  document.body.append(pil);
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
  const pil = document.getElementById('video-datum');
  if (pil) {
    const d = String(stavPrehravace().datum || '').replace(/ ?SEL?Č$/, '');
    const m = d.match(/^(.*?) ([0-9]{1,2}:[0-9]{2})$/);
    pil.innerHTML = m ? `${m[1]} <span style="color:#6e6e73;font-weight:500;margin-left:6px">${m[2]}</span>` : d;
  }
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


def hladce(xs, ys, x):
    """Monotónní kubická interpolace (Fritsch a Carlson): rychlost bez skoků, bez přestřelení, na krajích zastaví."""
    n = len(xs)
    s = [(ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i]) for i in range(n - 1)]
    d = [0.0] + [0.0 if s[i - 1] * s[i] <= 0 else 2 / (1 / s[i - 1] + 1 / s[i]) for i in range(1, n - 1)] + [0.0]
    i = max(0, min(n - 2, bisect.bisect_right(xs, x) - 1))
    h = xs[i + 1] - xs[i]
    t = max(0.0, min(1.0, (x - xs[i]) / h))
    return ((2 * t**3 - 3 * t**2 + 1) * ys[i] + (t**3 - 2 * t**2 + t) * h * d[i]
            + (-2 * t**3 + 3 * t**2) * ys[i + 1] + (t**3 - t**2) * h * d[i + 1])


def kamera(k):
    xs = [z["k"] for z in KLICE]
    hod = lambda kl: hladce(xs, [kl(z) for z in KLICE], k)  # noqa: E731
    nejbliz = min(KLICE, key=lambda z: abs(z["k"] - k))
    return {"center": [round(hod(lambda z: z["stred"][0]), 6), round(hod(lambda z: z["stred"][1]), 6)],
            "zoom": round(hod(lambda z: z["zoom"]), 4), "bearing": round(hod(lambda z: z["bearing"]), 3),
            "pitch": round(hod(lambda z: z["pitch"]), 3), "zaber": nejbliz["nazev"]}


class Natoceni:
    def __init__(self, a):
        self.a = a
        self.tmp = Path(tempfile.gettempdir()) / f"video_povoden_{a.cil}"
        self.snimky = self.tmp / "snimky"
        self.snimky.mkdir(parents=True, exist_ok=True)
        self.html = self.tmp / "povoden.html"
        self.log = self.tmp / "log.json"
        rok = re.sub(r"\W+", "_", a.povoden.split()[0]).strip("_").split("_")[-1]  # „6/2013“ → 2013
        self.video = ROOT / "docs/grafy" / f"video_povoden_{rok}_{a.cil}.mp4"
        self.web_video = ROOT / "web/prezentace/video" / f"povoden_{rok}_{a.cil}_1080.mp4"
        self.poster = ROOT / "web/prezentace/grafy" / f"video_{rok}_poster.jpg"
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
        p = page.evaluate(SKRYJ, {"mesto": self.mesto, "porovnani": self.a.porovnani})
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
            page.evaluate(KROK, {"i": i0, "kamera": kamera(0), "limit": 20000})
            page.evaluate("() => cekej(10000)")
            casy, zaznamy = [], []
            n = 0
            for k, i in enumerate(range(i0, i1 + 1)):
                for sub in range(KROKU):
                    t = time.time()
                    kf = k + sub / KROKU  # kamera jede plynule i uvnitř hodiny, voda se mění po hodinách
                    kam = kamera(kf)
                    vysl = page.evaluate(KROK, {"i": i, "kamera": kam, "limit": LIMIT})
                    page.screenshot(path=str(self.snimky / f"{n:04d}.png"))
                    n += 1
                    casy.append(time.time() - t)
                    zaznamy.append({"n": n - 1, "k": k, "i": i, "zaber": kam["zaber"], **vysl, "s": round(casy[-1], 2)})
                    if sub == 0 and (k % 12 == 0 or k < 3):
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
        """Snímek v každé klíčové pozici kamery a mezi nimi: diag_<n>_<nazev>.png v dočasné složce."""
        from playwright.sync_api import sync_playwright
        body = []
        for a, b in zip(KLICE, KLICE[1:]):
            body += [(a["k"], a["nazev"].replace(" ", "_").replace(",", "")), ((a["k"] + b["k"]) // 2, "mezi")]
        body.append((KLICE[-1]["k"], KLICE[-1]["nazev"].replace(" ", "_")))
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
        """Snímky beze změny (ostré), jen formát pro H.264."""
        return ("-vf", "format=yuv420p")

    def slozit(self, crf=19):
        self.video.parent.mkdir(parents=True, exist_ok=True)
        prikaz = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(self.snimky / "%04d.png"), *self.filtr(),
                  "-c:v", "libx264", "-crf", str(crf), "-preset", "slow", "-tune", "animation", "-movflags", "+faststart", str(self.video)]
        tisk("ffmpeg: master, crf", crf)
        v = subprocess.run(prikaz, capture_output=True, text=True)
        if v.returncode:
            tisk(v.stderr[-800:])
            raise SystemExit("ffmpeg selhal")

    def web_verze(self):
        self.web_video.parent.mkdir(parents=True, exist_ok=True)
        crf = 23
        for crf in (20, 22, 24, 26):
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(self.video), "-c:v", "libx264", "-crf", str(crf),
                            "-preset", "slow", "-tune", "animation", "-profile:v", "high", "-level", "4.2", "-g", "60",
                            "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(self.web_video)], check=True)
            if self.web_video.stat().st_size <= 40e6:
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
    ap.add_argument("--porovnani", action="store_true", help="vlevo předpověď 24 h předem, vpravo skutečnost")
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
