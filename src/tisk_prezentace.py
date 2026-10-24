"""Tisk decku do docs/prezentace.pdf: deck.tisk() odkryje všechny kroky, @media print dá každý slajd na stránku 1920 × 1080.
Server: .venv\\Scripts\\python -m http.server 8607 -d web (adresa v ZAKLAD). Uloží i snímky slajdů v tiskovém režimu do tisk6/."""
import os
import pathlib
import re
from playwright.sync_api import sync_playwright

ZAKLAD = os.environ.get('ZAKLAD', 'http://127.0.0.1:8607')
ROOT = pathlib.Path(__file__).resolve().parents[1]
PDF = ROOT / 'docs' / 'prezentace.pdf'
VEN = pathlib.Path(tempfile.gettempdir()) / 'tisk_prezentace'
VEN.mkdir(exist_ok=True)

with sync_playwright() as p:
    b = p.chromium.launch(channel='chrome')
    page = b.new_page(viewport={'width': 1920, 'height': 1080})
    chyby = []
    page.on('pageerror', lambda e: chyby.append(str(e)))
    page.on('console', lambda m: chyby.append(m.text) if m.type == 'error' else None)
    page.goto(ZAKLAD + '/prezentace/#1', wait_until='load')
    page.evaluate('document.fonts.ready')
    page.wait_for_timeout(1500)
    page.evaluate('deck.tisk()')
    page.emulate_media(media='print')
    page.wait_for_timeout(800)
    nenactene = page.evaluate('Array.from(document.images).filter(i => !(i.complete && i.naturalWidth)).map(i => i.getAttribute("src"))')
    hud = page.evaluate('!!document.querySelector(".hud")')
    paty = page.evaluate('Array.from(document.querySelectorAll(".pata")).map(p => p.textContent.trim().slice(0, 60))')
    page.pdf(path=str(PDF), width='1920px', height='1080px', print_background=True, prefer_css_page_size=True)
    n = page.locator('.slajd').count()
    for k in (0, 2, 8):
        page.locator('.slajd').nth(k).screenshot(path=str(VEN / f'tisk_{k + 1:02d}.png'))
    b.close()

data = PDF.read_bytes()
stran = len(re.findall(rb'/Type\s*/Page[^s]', data))
print(f'{PDF} {len(data) // 1024} kB, stran {stran}, slajdů {n}, nenačtené obrázky {nenactene}, hud {hud}, patičky {paty}, chyby {chyby}')
