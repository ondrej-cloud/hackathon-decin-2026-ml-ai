"""Video povodně z 3D mapy (app/mapbox_mapa.py) pro úvod prezentace: hodina po hodině, pět záběrů z různých stran.

Rozliv ze změřené hladiny při západu slunce, dole přehrávač s grafem; boční boxy skryté. Každý záběr má vlastní pomalý
pohyb kamery a záběry se do sebe prolínají (PRECHOD hodin, v prolínačce běží oba záběry ve stejné hodině, takže se voda,
datum ani graf nezdvojí). Playwright nafotí KROKU snímků na každou hodinu, mimo prolínačky beze změny, takže je obraz ostrý
(60 fps). Domy jsou ve všech vzdálenostech naše vrstva z OpenStreetMap (budovy Mapboxu by se při pohybu kamery nestihly načíst). Vlevo nahoře je skleněná pilulka s datem a hodinou, boční boxy jsou skryté.
Volba --porovnani zapne režim vlevo předpověď 24 h předem, vpravo skutečnost (v prezentaci se nepoužívá).

Spuštění z kořene repa (Windows: `$env:PYTHONUTF8=1; .venv\\Scripts\\python -u src\\video_povoden.py`, Mac: `.venv/bin/python -u src/video_povoden.py`):
    python -u src/video_povoden.py --diag          # jen snímky začátku a konce každého záběru do dočasné složky
    python -u src/video_povoden.py                 # celé natáčení, asi 5 minut, pak ffmpeg
    python -u src/video_povoden.py --jen-video     # jen prolínačky a ffmpeg z už natočených záběrů
Volby: --povoden "6/2013" --cil decin --model ridge_bez2013 --od 2013-06-01T00:00 --do 2013-06-06T12:00 (český čas)
       --rezim headless|chromium|okno (prohlížeč; výchozí zkouší v tomhle pořadí) --porovnani (vlevo předpověď, vpravo skutečnost)
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
LIMIT = 6000  # ms čekání na idle mapy u jednoho snímku
KROKU = 11  # snímků na hodinu povodně; 133 hodin × 11 = 1 463 snímků, při 60 fps 24 s
FPS = 60

# Záběry pro Děčín 6/2013: hodiny k_od až k_do (od --od), kamera jede z "od" do "do". Slunce svítí od západojihozápadu,
# takže se střídá světlo z boku (1, 3), proti slunci s oblohou (2) a slunce v zádech (4, 5). Sousední záběry se o PRECHOD
# hodin překrývají a v tu dobu se prolínají. Jiná povodeň nebo město: doladit přes --diag.
PRECHOD = 6
ZABERY = [
    {"nazev": "celé město", "k_od": 0, "k_do": 33,
     "od": {"center": [14.2045, 50.7700], "zoom": 13.45, "pitch": 57, "bearing": -18},
     "do": {"center": [14.2050, 50.7720], "zoom": 13.75, "pitch": 61, "bearing": -6}},
    {"nazev": "proti slunci", "k_od": 27, "k_do": 63,
     "od": {"center": [14.2150, 50.7745], "zoom": 13.95, "pitch": 74, "bearing": 222},
     "do": {"center": [14.2120, 50.7728], "zoom": 14.2, "pitch": 77, "bearing": 238}},
    {"nazev": "podél řeky od jihu", "k_od": 57, "k_do": 93,
     "od": {"center": [14.2060, 50.7700], "zoom": 14.35, "pitch": 64, "bearing": 8},
     "do": {"center": [14.2085, 50.7740], "zoom": 14.7, "pitch": 66, "bearing": 28}},
    {"nazev": "Staré Město, slunce v zádech", "k_od": 87, "k_do": 117,
     "od": {"center": [14.2120, 50.7745], "zoom": 15.05, "pitch": 66, "bearing": 58},
     "do": {"center": [14.2140, 50.7755], "zoom": 15.3, "pitch": 67, "bearing": 76}},
    {"nazev": "vrchol mezi domy", "k_od": 111, "k_do": 133,
     "od": {"center": [14.2140, 50.7760], "zoom": 15.45, "pitch": 66, "bearing": -40},
     "do": {"center": [14.2150, 50.7762], "zoom": 15.85, "pitch": 67, "bearing": -28}},
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
  for (const id of ['vlevo', 'vpravo', 'okamzik', 'nastaveni-tlacitko', 'cela']) { const e = document.getElementById(id); if (e) e.style.display = 'none'; }
  document.querySelector('.napoveda')?.remove();
  const n = document.getElementById('najeti'); if (n) n.style.display = 'none';
  if (typeof N !== 'undefined') N.poi = false;
  for (const m of [mapaA, mapaB].filter(Boolean)) {
    try { m.setConfigProperty('basemap', 'showPointOfInterestLabels', false); m.setConfigProperty('basemap', 'showTransitLabels', false); }
    catch (e) { /* styl se teprve načítá, konfigurace() ho nastaví při načtení */ }
    // domy jen z naší vrstvy a ve všech vzdálenostech: budovy Mapboxu by se při pohybu kamery nestihly načíst a mizely by
    m.setConfigProperty('basemap', 'show3dObjects', false);
    m.setLayerZoomRange('budovy', 11, 24);
    m.setPaintProperty('budovy', 'fill-extrusion-opacity', 1);
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


def kamera(z, kf):
    """Kamera záběru z v čase kf (hodiny od začátku videu, i se zlomky). Uvnitř záběru stálá rychlost, na začátku videa
    se kamera rozjede a na konci zastaví."""
    t = max(0.0, min(1.0, (kf - z["k_od"]) / (z["k_do"] - z["k_od"])))
    s0 = 0.0 if z is ZABERY[0] else 1.0
    s1 = 0.0 if z is ZABERY[-1] else 1.0
    t = (t**3 - 2 * t**2 + t) * s0 + (-2 * t**3 + 3 * t**2) + (t**3 - t**2) * s1  # Hermite s danými sklony na krajích
    lin = lambda a, b: a + (b - a) * t  # noqa: E731
    od, do = z["od"], z["do"]
    return {"center": [round(lin(od["center"][0], do["center"][0]), 6), round(lin(od["center"][1], do["center"][1]), 6)],
            "zoom": round(lin(od["zoom"], do["zoom"]), 4), "bearing": round(lin(od["bearing"], do["bearing"]), 3),
            "pitch": round(lin(od["pitch"], do["pitch"]), 3), "zaber": z["nazev"]}


class Natoceni:
    def __init__(self, a):
        self.a = a
        self.tmp = Path(tempfile.gettempdir()) / f"video_povoden_{a.cil}"
        self.snimky = self.tmp / "snimky"
        self.zabery = self.tmp / "zabery"
        self.snimky.mkdir(parents=True, exist_ok=True)
        self.zabery.mkdir(parents=True, exist_ok=True)
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
        """Každý záběr zvlášť do zabery/<z>_<snímek>.png; snímek je číslo ve výsledném videu, takže se prolínačky sejdou."""
        from playwright.sync_api import sync_playwright
        for soubor in self.zabery.glob("*.png"):
            soubor.unlink()
        konec = (i1 - i0 + 1) * KROKU
        with sync_playwright() as pw:
            b, page, chyby, info = self.otevri(pw, rezim)
            if page is None:
                return None
            casy, zaznamy = [], []
            for zi, z in enumerate(ZABERY):
                prvni = z["k_od"] * KROKU
                page.evaluate(KROK, {"i": i0 + z["k_od"], "kamera": kamera(z, z["k_od"]), "limit": 20000})
                page.evaluate("() => cekej(10000)")
                for f in range(prvni, min(z["k_do"] * KROKU, konec)):
                    t = time.time()
                    k, kf = f // KROKU, f / KROKU  # kamera jede plynule i uvnitř hodiny, voda se mění po hodinách
                    kam = kamera(z, kf)
                    vysl = page.evaluate(KROK, {"i": i0 + k, "kamera": kam, "limit": LIMIT})
                    page.screenshot(path=str(self.zabery / f"{zi}_{f:04d}.png"))
                    casy.append(time.time() - t)
                    zaznamy.append({"n": f, "k": k, "i": i0 + k, "zaber": z["nazev"], **vysl, "s": round(casy[-1], 2)})
                    if f % KROKU == 0 and (k % 12 == 0 or f == prvni):
                        tisk(f"  {k:3d} i={i0 + k} {vysl['datum']} {vysl['h']} cm  {z['nazev']}  {vysl['stav']}  {casy[-1]:.1f} s")
                    if rezim != "okno" and len(casy) == 3 * KROKU and sum(casy) / len(casy) > POMALU:
                        tisk(f"{rezim} je pomalý ({sum(casy) / len(casy):.1f} s na snímek), zkusím další režim")
                        b.close()
                        return None
            b.close()
        prumer = sum(casy) / len(casy)
        tisk(f"natočeno {len(casy)} snímků, průměr {prumer:.2f} s na snímek, chyby stránky: {chyby[:5]}")
        return info | {"prumer_s": round(prumer, 2), "max_s": round(max(casy), 2), "snimky": len(casy),
                       "od": zaznamy[0]["datum"], "do": zaznamy[-1]["datum"], "h_od": zaznamy[0]["h"], "h_do": zaznamy[-1]["h"],
                       "limity": sum(z["stav"] == "limit" for z in zaznamy), "chyby": chyby[:5], "lista_od": self.lista_od,
                       "zaznamy": zaznamy}

    def prolni(self, i0, i1):
        """Výsledné snímky: mimo prolínačky kopie záběru, v prolínačce plynulý přechod (smoothstep) z jednoho do druhého."""
        import shutil
        from PIL import Image
        for soubor in self.snimky.glob("*.png"):
            soubor.unlink()
        for f in range((i1 - i0 + 1) * KROKU):
            v = [zi for zi, z in enumerate(ZABERY) if z["k_od"] * KROKU <= f < z["k_do"] * KROKU]
            cil = self.snimky / f"{f:04d}.png"
            if len(v) == 1:
                shutil.copyfile(self.zabery / f"{v[0]}_{f:04d}.png", cil)
                continue
            a, b = v[0], v[1]
            od, do = ZABERY[b]["k_od"] * KROKU, ZABERY[a]["k_do"] * KROKU
            t = (f - od + 0.5) / (do - od)
            t = t * t * (3 - 2 * t)
            Image.blend(Image.open(self.zabery / f"{a}_{f:04d}.png").convert("RGB"),
                        Image.open(self.zabery / f"{b}_{f:04d}.png").convert("RGB"), t).save(cil)
        tisk(f"složeno {(i1 - i0 + 1) * KROKU} snímků, prolínaček {len(ZABERY) - 1} po {PRECHOD} h")

    def diag(self, i0, rezimy):
        """Snímek začátku a konce každého záběru: diag_<záběr>_<od|do>.png v dočasné složce."""
        from playwright.sync_api import sync_playwright
        for rezim in rezimy:
            with sync_playwright() as pw:
                b, page, chyby, info = self.otevri(pw, rezim)
                if page is None:
                    continue
                for zi, z in enumerate(ZABERY):
                    for kraj, k in (("od", z["k_od"]), ("do", z["k_do"] - 1)):
                        t = time.time()
                        vysl = page.evaluate(KROK, {"i": i0 + k, "kamera": kamera(z, k), "limit": 20000})
                        page.evaluate("() => cekej(6000)")
                        page.screenshot(path=str(self.tmp / f"diag_{zi}_{kraj}.png"))
                        tisk(f"  diag {zi} {kraj} k={k} {vysl['datum']} {vysl['h']} cm {z['nazev']} {vysl['stav']} {time.time() - t:.1f} s")
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
    n.prolni(i0, i1)
    n.slozit()
    n.web_verze()
    log = json.loads(n.log.read_text(encoding="utf-8")) if n.log.exists() else {}
    log["video"] = {"master": n.proved(n.video), "web": n.proved(n.web_video)}
    n.log.write_text(json.dumps(log, ensure_ascii=False, indent=1), encoding="utf-8")
    tisk("HOTOVO")


if __name__ == "__main__":
    main()
