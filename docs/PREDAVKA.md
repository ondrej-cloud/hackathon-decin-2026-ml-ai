# Předávka: stav prezentace, webu a mapy (so 24. 10., 13:00) a co dodělat

Pro toho, kdo pokračuje v Honzově práci (Honza na jiném účtu nebo kdokoli z týmu): tady je přesný stav a kroky. Pravidla týmu jsou v `CLAUDE.md`, mluvený script v `prezentace/SCRIPT_VITEZNY.md`, texty řečníků v `prezentace/SLAJDY.md`, kostra v `docs/PREZENTACE_7MIN.md`.

## Kde co je

| Co | Kde | Stav |
|---|---|---|
| Web (Teď, Jak dobře to funguje, Mapa, Animace) | https://field-zero.netlify.app, zdroj `web/` | nasazeno 12:08 (verze 3), v `main` |
| Hlavní prezentace (HTML deck, 9 slajdů + Z1–Z12) | https://field-zero.netlify.app/prezentace/, zdroj `web/prezentace/` | nasazena verze bez porovnání; poslední úpravy (slajd 1 bez mlhy, tlačítko na 8, slajd 2 ve dvou krocích, zalamování) jsou rozpracované, viz níž |
| Varianta prezentace ve stylu Liquid Glass (námět) | `web/prezentace-sklo/` (po nasazení https://field-zero.netlify.app/prezentace-sklo/) | commit e2d4f2e, obsah = kopie hlavního decku z 12:20 |
| Úvodní video (2013, 60 fps, ostré, bez porovnání, s datem) | `web/prezentace/video/povoden_2013_decin_1080.mp4` (36 MB), poster `web/prezentace/grafy/video_2013_poster.jpg` | commit 0ea3fb3 na větvi `honza`; natáčí `src/video_povoden.py`, návod `docs/VIDEO.md` (i pro Mac, písmo San Francisco) |
| PDF prezentace | `docs/prezentace.pdf` | přegenerovat po dokončení decku: `src/tisk_prezentace.py` (21 stran) |
| Mapa povodí (Liquid Glass, soumrak, bez porovnání v UI) | `app/mapbox_mapa.py`, generuje `src/export_web.py --vse` | v `main` (bf7bbd5) |
| Snímek aplikace pro Z10 a snímek mapy pro slajd 8 | `web/prezentace/grafy/Z10_aplikace_dnes.png`, `08_mapa_rozlivu.png` (+ kopie v `docs/grafy/prezentace/`, `prezentace/grafy/`) | hotové, v Gitu |

Větve: `honza` má vše, `main` je o několik commitů pozadu (video, varianta ve skle, texty). Sloučit a pushnout až s čistým pracovním stromem (viz krok 3). Nikdy `git merge`, dokud jsou v pracovní kopii rozpracované změny: dnes při tom git vrátil deck na starší verzi.

## Stav ve 13:00 (aktualizace)

1. **Deck je hotový a commitnutý** na větvi `honza` (slajd 1 bez mlhy: po dohrání se video zmenší do karty vpravo, vlevo nadpis a 18 h; slajd 2 ve dvou krocích; tlačítko „Otevřít živou mapu“ na slajdu 8; linie řeky a zalamování; bez citátu na slajdu 5; PDF 21 stran). Varianta ve skle `web/prezentace-sklo/` má stejný obsah.
2. **Opravy webu** (pilulky prahů v grafech mimo křivky, kompaktní vodočet na telefonu, dlaždice na 768–1024 px, kontrast 2. stupně, typografie) dělal agent; první část je v commitu (graf.js, vodocet.js, web funguje bez chyb), zbytek mohl zůstat nedodělaný. Když `git status` ukáže změny ve `web/js` nebo `web/css`, ověřit v prohlížeči (0 chyb konzole, čísla 646 / 738 cm na `/?povoden=2011-01&cil=decin&cas=2011-01-15T09:00`) a commitnout; když je něco rozbité, `git checkout -- web/js web/css` vrátí ověřený stav.
3. Kontrola faktů proběhla bez věcné chyby; kontroly layoutu webu a grafů jsou zapracované, kromě velikosti písma v PNG grafech (jde jen na Macu, `src/grafy_prezentace.py`, popisky ≥ 24 pt).

## Kroky k dokončení (v tomhle pořadí)

```
git switch honza
git status                                  # když jsou změny v web/prezentace, je to rozpracovaný bod 1
$env:PYTHONUTF8=1
.venv\Scripts\python -m http.server 8622 -d web      # v druhém okně nechat běžet
.venv\Scripts\python src\kontrola_prezentace.py      # 0 chyb, 0 přetečení, snímky docs/grafy/deck8_*.png, podívat se
.venv\Scripts\python src\tisk_prezentace.py          # ZAKLAD=http://127.0.0.1:8622 ; docs/prezentace.pdf 21 stran
```

4. Varianta ve skle: po dokončení hlavního decku zkopírovat `web/prezentace/index.html`, `deck.js`, `reka.js` do `web/prezentace-sklo/` a v `index.html` přepsat cesty `src="grafy/` → `src="../prezentace/grafy/`, `src="video/` → `src="../prezentace/video/`, `poster="grafy/` → `poster="../prezentace/grafy/` (pozor, `type="video/mp4"` nechat). `deck.css` ve variantě nechat.
5. Commit pod Honzou (česky, bez Co-Authored-By): `git add web/prezentace web/prezentace-sklo docs/prezentace.pdf docs/grafy/deck8_*.png` a commit; pak `git fetch origin`, `git merge origin/main` (jen s čistým stromem), `git push origin honza`, `git push origin honza:main` (velké soubory: `git -c http.postBuffer=524288000 push …`).
6. Nasazení: `npx netlify-cli@latest deploy --prod --no-build --dir web` (Netlify CLI je na Honzově počítači přihlášené; jinde `NETLIFY_AUTH_TOKEN` a `--site f8d8a20b-180f-43c4-a142-fdaa47996c00`). Ověřit https://field-zero.netlify.app/prezentace/ (mezerník spustí video) a `/prezentace-sklo/`.
7. Tobias: na Macu pustit `src/video_povoden.py` podle `docs/VIDEO.md` (video v písmu San Francisco), pushnout; pak nasadit znovu.
8. Zbývá na Honzovi: GitHub secrets pro hodinovou Action (`docs/WEB.md`), omezení tokenu Mapboxu na doménu, nácvik podle `prezentace/SCRIPT_VITEZNY.md` (dvakrát s časomírou, 6:45).

## Co nedělat

- Neměnit grafy PNG v `docs/grafy/prezentace/` na Windows (jsou z Macu v Helvetice).
- Nespouštět `src/porovnej.py --test`.
- Žádné zmínky o AI nebo nástrojích v commitech ani textech.
