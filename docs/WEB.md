# Web: field-zero.netlify.app

Statický web ve složce `web/`. Na Netlify se publikuje celá složka tak, jak je, bez build kroku; nastavení je v `netlify.toml` v kořeni repa (`publish = "web"` a hlavičky cache). Streamlit aplikace (`app/`) zůstává pro demo, web je to samé bez serveru: předpočítaná data v JSON, grafy vlastním SVG, mapy a animace jako samostatné stránky v iframu.

## Co kde je

| Cesta | Co to je | Odkud se bere |
|---|---|---|
| `web/index.html` | Dnes: hladina teď a za 12, 24 a 36 h v jedné kartě, graf posledních 72 hodin a vodočet, průtoky a srážky sbalené v Podrobnostech, dole odkaz na povodeň 2013; staré odkazy s `?povoden=…`, `?cas=…` nebo `?dnesek=0` přesměruje na Povodně | ručně |
| `web/povodne.html` | Povodně: jeden výběr povodně a města pro celou stránku; mapa (rozliv nebo voda v řekách v iframe, načte se až na klik), jak přesná byla předpověď (čtyři čísla, graf celé povodně, tabulka po dnech sbalená, přepínač 12/24/36 h) a co model hlásil hodinu po hodině (posuvník času, karta, graf s tím, co pak přišlo, vodočet); stav v adrese (`povoden`, `cil`, `h`, `cas`, `vrstva`) | ručně |
| `web/kvalita.html`, `web/mapa.html`, `web/animace.html` | jen přesměrování na `povodne.html` se stejnými parametry (odkaz z decku na `mapa.html?povoden=2013-06&cil=decin` dál funguje) | ručně |
| `web/prezentace/index.html` | HTML deck; otvírá se vždy jako `/prezentace/` (bez `index.html`, jinak server přesměruje a deck se nenačte); odkazy z decku do aplikace vedou na `../index.html?povoden=…` (na Netlify funguje bez přesměrování, ověřeno); lokální `npx serve` dotaz u `index.html` zahazuje, proto lokálně testovat přes `/?povoden=…` | ručně |
| `web/css/`, `web/js/`, `web/fonts/`, `web/img/` | vzhled, skripty, písma (OFL), obrázky | ručně |
| `web/data/povodne.json`, `rada_*.json`, `metriky.json`, `model_ridge_vse_*.json` | předpočítaná data; povodně z validace modelem `ridge` (učený 2006–2018), Boris 9/2024 modelem `ridge_test` (učený na všem do 2020 jako při finálním testu, stejná čísla jako v `docs/PREHLED.md` a v prezentaci: 14. 9. 2024 11:00 předpověď 577 cm, vrchol 649 předpovězen na 611 cm, 3. stupeň 27 h předem); povodeň 6/2013 (`zdroj` „trenink“) modelem `ridge_bez2013` (učený do 2020 bez této povodně a 20 dní kolem ní, protože 2013 je v tréninku; předtrénuje se sám při prvním běhu) | `python src/export_web.py --vse` |
| `web/data/dnesek.json` | živá předpověď na dnešek | `python src/dnesek_export.py` |
| `web/mapa/*.html`, `web/animace/*.html` | mapy a animace povodní | `python src/export_web.py --vse`; obsahují token Mapboxu, proto nejsou v Gitu |

`web/data/dnesek.json` v Gitu je jen snímek z posledního lokálního běhu. Na webu ho každou hodinu přepíše GitHub Action (viz níž), do Gitu se nezapisuje. Když ho spustíš lokálně, ukáže se v `git status` jako změněný; commitnout ho můžeš, nemusíš.

## Dnešek (`src/dnesek_export.py`)

Stáhne operativní data ČHMÚ (`app/aktualni.py`), spočítá předpověď modelem `ridge_vse` (učený na všem do 2025) s rozmezím nejistoty (`app/predikce.py`) a přidá předpověď srážek z Open-Meteo (`app/pocasi.py`). Zapíše `web/data/dnesek.json`, běží asi 15 s, nepotřebuje `.env` ani token.

- `ok=true`: `cas_cesky`, `stari_h`, `upozorneni` (věty, co chybí a co je dopočtené), `stanice.decin` a `stanice.usti` (`ted`, `stupen`, `pred`, `dolni`, `horni`, `chmu` po horizontech 12/24/36, `veta` pro laika), `tabulka` (průtoky 12 stanic, `dopocteno` u Mělníka a Nymburka), `historie` (posledních 72 h pro graf), `srazky`.
- `ok=false`: `chyba` (věta), v `posledni` zůstane poslední úspěšný stav, aby web měl co ukázat a napsal k tomu, že je starý. Skript přitom neskončí chybou, aby nasazení proběhlo. Když `posledni` chybí nebo se `dnesek.json` nenačte, web přepne na přehrávání historie a napíše to nahoře.

## Lokálně

Z kořene repa (Mac: `.venv/bin/python` a bez `$env:`):

```
$env:PYTHONUTF8=1
.venv\Scripts\python src/uloz_model.py
.venv\Scripts\python src/uloz_model.py --vse
.venv\Scripts\python src/export_web.py --vse
.venv\Scripts\python src/dnesek_export.py
npx serve web
```

Web běží na http://localhost:3000. Mapy a animace potřebují `MAPBOX_TOKEN` v `.env` (čte ho `app/mapa.py`, z prostředí nebo z `.env`); bez něj se stránky v `web/mapa/` a `web/animace/` nevygenerují a iframy na ně budou prázdné. Hlavičky cache z `netlify.toml` lokální server neumí, ty se ověří až na Netlify.

## Ruční nasazení z počítače

Jednou: přihlášení a propojení složky se sitem (vytvoří `.netlify/`, je v `.gitignore`):

```
npx netlify-cli@latest login
npx netlify-cli@latest link --name field-zero
```

Když site `field-zero` ještě neexistuje, založí ho `npx netlify-cli@latest sites:create --name field-zero` (jméno musí být volné, jinak dá Netlify jiné). Pak pokaždé:

```
npx netlify-cli@latest deploy --prod --no-build --dir web
```

Bez propojení složky jde totéž s `--site <ID sitů>` a tokenem v proměnné `NETLIFY_AUTH_TOKEN`. Hotový deploy ověř: `curl -I https://field-zero.netlify.app/data/dnesek.json` má vrátit `cache-control: public, max-age=300`, `/fonts/...` `max-age=31536000, immutable`.

Netlify nepropojuj s GitHubem přes „Import from Git“: build by vzal jen to, co je v Gitu, tedy bez map a animací. Nasazuje se z počítače nebo z GitHub Action.

## Druhý web field-one.netlify.app

Pro zkoušení nové verze prezentace vedle stabilní: site `field-one` (ID `8fd3da20-6ddb-49b6-a2e2-b59ab08602af`), stejná složka `web/`. Nasazení bez přepojení lokálního linku: `npx netlify-cli@latest deploy --prod --no-build --dir web --site 8fd3da20-6ddb-49b6-a2e2-b59ab08602af`. Hodinová Action nasazuje jen na field-zero.

## Každou hodinu automaticky (GitHub Action)

`.github/workflows/dnesek.yml` běží každou hodinu v :05, po každém pushi do `main`, který mění `web/`, `app/`, `src/` nebo `data/external/`, a ručně (Actions > Dnešek na webu > Run workflow). Kroky: Python 3.12 a `app/requirements.txt`, `uloz_model.py` a `--vse`, `export_web.py --vse`, `dnesek_export.py`, `netlify deploy --prod --no-build --dir web`. Nic se necommituje, repo zůstává beze změny.

Secrets (GitHub: repo > Settings > Secrets and variables > Actions > New repository secret):

| Secret | Kde ho vzít |
|---|---|
| `MAPBOX_TOKEN` | veřejný token z `.env` (account.mapbox.com > Tokens) |
| `NETLIFY_AUTH_TOKEN` | app.netlify.com > User settings > OAuth > Personal access tokens > New access token |
| `NETLIFY_SITE_ID` | app.netlify.com > site field-zero > Project configuration > General > Project ID (dřív Site ID); po `netlify link` je i v `.netlify/state.json` |

Bez `NETLIFY_AUTH_TOKEN` nebo `NETLIFY_SITE_ID` Action hned skončí chybou s názvem chybějícího secretu, bez `MAPBOX_TOKEN` jen varuje.

Plánované spuštění (cron) GitHub pouští jen z výchozí větve (`main`), takže workflow musí být sloučený do `main`. Ruční spuštění jde z každé větve, kde soubor je. Když ČHMÚ zrovna neodpoví, `dnesek.json` má `ok=false` a web ukáže poslední známý stav; další hodinu se to spraví samo.

## Hlavičky cache (`netlify.toml`)

| Cesta | Cache |
|---|---|
| `/fonts/*`, `/img/*` | 1 rok, immutable |
| `/data/dnesek.json` | 5 minut |
| `/data/*` ostatní | 1 hodina |
| `/mapa/*`, `/animace/*` | 1 den |
| HTML, CSS, JS | výchozí Netlify (vždy se ověří u serveru, přenese se jen změna) |

`X-Frame-Options` se nenastavuje, iframy map a animací jsou na stejné doméně.

## Co je v `.gitignore`

`web/mapa/*.html` a `web/animace/*.html` (mají v sobě token Mapboxu), `.netlify/` (lokální propojení se sitem), `models/*.joblib` (modely si každý uloží sám), `data/raw/` a `.env`.

## Časté potíže

- Deck je prázdný a v konzoli jsou 404 na `deck.css` a `deck.js`: byl otevřený jako `/prezentace/index.html` a server ho přesměroval na `/prezentace/index`. Otvírat jako `/prezentace/`.
- Mapy na webu dávají 404: při nasazení chyběl `MAPBOX_TOKEN` nebo neproběhl `export_web.py --vse`; v Action se podívej na krok „Data, mapy a animace pro web“.
- Dnešek ukazuje starý čas: ČHMÚ zveřejňuje hodinu až po jejím konci a `stari_h` kolem 1 až 2 h je normální; nad 3 h přidá skript větu do `upozorneni`.
- Action je červená hned na začátku: chybí secret, název je v chybě.
- `netlify deploy` chce přihlášení: `npx netlify-cli@latest login`, nebo nastav `NETLIFY_AUTH_TOKEN`.
