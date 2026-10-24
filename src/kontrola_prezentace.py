"""Ověření HTML decku: 3 viewporty (1920×1080, 1470×956 MacBook Air, 1280×832), všech slajdů ve všech krocích: chyby konzole,
prvky mimo plochu, překryv nadpisu s linií řeky, obrázky načtené, video na mezerník, opacita nastupujících prvků po 1,2 s.
Snímky docs/grafy/deck8_*.png. Spuštění: server `.venv/Scripts/python -m http.server 8622 -d web` a
`$env:PYTHONUTF8=1; .venv/Scripts/python src/kontrola_prezentace.py` (jiný port přes ZAKLAD)."""
import json
import os
import pathlib
import sys
from playwright.sync_api import sync_playwright

ZAKLAD = os.environ.get('ZAKLAD', 'http://127.0.0.1:8622')
GRAFY = pathlib.Path(__file__).resolve().parents[1] / 'docs' / 'grafy'
VIEWPORTY = [(1920, 1080, 1), (1470, 956, 2), (1280, 832, 2)]

KONTROLA = r"""
() => {
  const s = document.querySelector('.slajd.aktivni');
  const sr = s.getBoundingClientRect();
  const ven = [], pruhledne = [];
  const skryte = e => {
    for (let x = e; x && x !== s; x = x.parentElement) {
      const cs = getComputedStyle(x);
      if (cs.visibility === 'hidden' || cs.display === 'none') return true;
      if (x.matches('[data-krok]:not(.je), .kryt, .jen-tisk, .tisk-popis, .poznamky, .cerna')) return true;
    }
    return false;
  };
  for (const e of s.querySelectorAll('*')) {
    if (skryte(e)) continue;
    const r = e.getBoundingClientRect();
    if (!r.width || !r.height) continue;
    const cs = getComputedStyle(e);
    if (+cs.opacity === 0) continue;
    const tol = 1.5;
    if (r.left < sr.left - tol || r.top < sr.top - tol || r.right > sr.right + tol || r.bottom > sr.bottom + tol) {
      ven.push(`${e.tagName.toLowerCase()}${e.id ? '#' + e.id : ''}${e.className && typeof e.className === 'string' ? '.' + e.className.split(' ').join('.') : ''} ${Math.round(r.left - sr.left)},${Math.round(r.top - sr.top)} ${Math.round(r.width)}x${Math.round(r.height)}`);
    }
    if (+cs.opacity < 0.999 && !e.matches('.reka-mini path, .reka-mini, .reka-mini *, .stin-video, .stin-veta, .veta, video') && !e.closest('.reka-mini')) {
      if (!(s.classList.contains('video') && e.closest('.uvod, .stin-veta'))) pruhledne.push(`${e.tagName.toLowerCase()}${e.id ? '#' + e.id : ''}.${(typeof e.className === 'string' ? e.className : e.className.baseVal || '').split(' ').join('.')} op=${cs.opacity}`);
    }
  }
  const h1 = s.querySelector('h1'), mini = s.querySelector('.reka-mini');
  let prekryv = null;
  if (h1 && mini) {
    const a = h1.getBoundingClientRect(), b = mini.getBoundingClientRect();
    const hs = getComputedStyle(h1), ms = getComputedStyle(mini);
    if (+hs.opacity > 0 && +ms.opacity > 0 && a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top) prekryv = `h1 ${Math.round(a.right - sr.left)} vs reka ${Math.round(b.left - sr.left)}`;
  }
  const obrazky = Array.from(s.querySelectorAll('img')).filter(i => !skryte(i) && !(i.complete && i.naturalWidth > 0)).map(i => i.getAttribute('src'));
  const orez = Array.from(s.querySelectorAll('.skupina .nazev, .soucet-sloupec .stitek')).filter(e => e.scrollWidth > e.clientWidth + 1).map(e => e.textContent);
  const popisky = Array.from(s.querySelectorAll('.dve-cisla .pod-cislo')).map(e => Math.round(e.getBoundingClientRect().height / (sr.height / 1080)));
  const karty = Array.from(s.querySelectorAll('.karta, .graf, .snimek-mapy, .snimek, .ctyri > div')).filter(e => !skryte(e)).map(e => { const r = e.getBoundingClientRect(); const k = 1080 / sr.height; return [Math.round((r.top - sr.top) * k), Math.round((r.bottom - sr.top) * k), Math.round((r.left - sr.left) * k), Math.round((r.right - sr.left) * k)]; });
  return { ven, pruhledne, prekryv, obrazky, orez, popisky, karty, krok: deck.krok, slajd: deck.slajd };
}
"""

souhrn = {}
with sync_playwright() as p:
    b = p.chromium.launch(channel='chrome')
    for (w, hgt, dpr) in VIEWPORTY:
        ctx = b.new_context(viewport={'width': w, 'height': hgt}, device_scale_factor=dpr)
        page = ctx.new_page()
        chyby = []
        page.on('pageerror', lambda e: chyby.append('pageerror: ' + str(e)))
        page.on('console', lambda m: chyby.append('console: ' + m.text) if m.type == 'error' else None)
        page.goto(ZAKLAD + '/prezentace/#1', wait_until='load')
        page.evaluate('document.fonts.ready')
        page.wait_for_timeout(600)
        N = page.evaluate('document.querySelectorAll(".slajd").length')
        nalezy = []
        karty_vse = {}
        popisky_vse = {}
        # video: mezerník spustí, konec videa ukáže nadpis a 18 h
        page.keyboard.press('Space')
        page.wait_for_timeout(900)
        hraje = page.evaluate('!document.getElementById("video").paused')
        page.evaluate('(() => { const v = document.getElementById("video"); v.currentTime = Math.max(0, v.duration - 0.4); })()')
        page.wait_for_timeout(1800)
        if page.evaluate('deck.krok') != 2:
            page.keyboard.press('Space')
            page.wait_for_timeout(300)
        page.wait_for_timeout(1400)
        video = page.evaluate("""() => { const h = document.querySelector('#s-video .uvod h1'), o = document.querySelector('#s-video .obri'), m = document.querySelector('#s-video .reka-mini'), p = m.querySelector('path');
          return { krok: deck.krok, h1: getComputedStyle(h).opacity, uvod: getComputedStyle(document.querySelector('#s-video .uvod')).opacity, obri: o.textContent.trim(), mini: getComputedStyle(m).opacity, dashoffset: p.style.strokeDashoffset }; }""")
        k = page.evaluate(KONTROLA)
        if k['ven'] or k['prekryv'] or k['obrazky'] or k['pruhledne']: nalezy.append((1, 2, k))
        karty_vse[1] = k['karty']
        if w == 1920:
            page.screenshot(path=str(GRAFY / 'deck8_1.png'))
        if w == 1470:
            page.screenshot(path=str(GRAFY / 'deck8_air_1.png'))
        for n in range(1, N):
            page.evaluate(f'deck.prejdi({n})')
            page.wait_for_timeout(1200)
            k = page.evaluate(KONTROLA)
            if k['ven'] or k['prekryv'] or k['obrazky'] or k['pruhledne'] or k['orez']: nalezy.append((n + 1, 0, k))
            kroku = page.evaluate('+document.querySelector(".slajd.aktivni").dataset.kroky')
            for kk in range(1, kroku + 1):
                page.evaluate('deck.dalsi()')
                page.wait_for_timeout(700)
                k = page.evaluate(KONTROLA)
                if k['ven'] or k['prekryv'] or k['obrazky'] or k['orez']: nalezy.append((n + 1, kk, k))
            karty_vse[n + 1] = k['karty']
            if k['popisky']: popisky_vse[n + 1] = k['popisky']
            if w == 1920 and n < 9:
                page.wait_for_timeout(500)
                page.screenshot(path=str(GRAFY / f'deck8_{n + 1}.png'))
                if n == 4:
                    page.screenshot(path=str(GRAFY / 'deck8_5_karta.png'), clip={'x': 60, 'y': 250, 'width': 1800, 'height': 790})
        souhrn[f'{w}x{hgt}@{dpr}'] = { 'slajdu': N, 'chyby': chyby, 'video': {'hraje': hraje, **video}, 'nalezy': [(s, kr, {kk: v for kk, v in k.items() if kk in ('ven', 'pruhledne', 'prekryv', 'obrazky', 'orez')}) for s, kr, k in nalezy], 'karty': karty_vse if w == 1920 else None, 'popisky': popisky_vse }
        ctx.close()
    b.close()
print(json.dumps(souhrn, ensure_ascii=False, indent=1))
