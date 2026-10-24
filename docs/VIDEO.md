# Video povodně pro úvod prezentace

Úvodní video decku (`web/prezentace/video/povoden_2013_decin_1080.mp4`, 24 s, 1920 × 1080, bez zvuku) je povodeň v Děčíně od 1. 6. do 6. 6. 2013 po hodinách z 3D mapy aplikace: vlevo rozliv z předpovědi vydané 24 h předem modelem `ridge_bez2013` (učený bez této povodně), vpravo rozliv ze skutečné hladiny, dole přehrávač s grafem. Kamera jde ve čtyřech záběrech od celého města k domům Starého Města, střihy sedí na růst hladiny. Nic není kreslené ručně, každý snímek je stránka mapy v dané hodině.

Natáčí ho `src/video_povoden.py`: vygeneruje stránku mapy, skryje úvod a boční boxy, zapne porovnání, vypne popisky podniků, nafotí 133 hodin Playwrightem a složí ffmpegem (mapa se prolíná na 30 fps, štítky nahoře a lišta dole zůstávají ostré). Master je `docs/grafy/video_povoden_2013_decin.mp4` (není v Gitu), webová verze do 22 MB a poster `web/prezentace/grafy/video_2013_poster.jpg`.

## Na Windows

```
$env:PYTHONUTF8=1
.venv\Scripts\python -u src\video_povoden.py --diag     # snímky konců záběrů do dočasné složky (cesta se vypíše)
.venv\Scripts\python -u src\video_povoden.py            # celé natáčení, asi 5 minut, pak ffmpeg
```

Potřebuje `MAPBOX_TOKEN` v `.env`, Playwright (`pip install playwright`) s Chromem v počítači, ffmpeg v PATH a GPU (bez něj je snímek pomalý, skript to ohlásí).

## Na Macu (písmo San Francisco)

Stránka mapy má písmo `-apple-system, "SF Pro Text", … Inter`. Na Windows se vykreslí Inter, na Macu přímo San Francisco, takže video natočené na Macu má písmo jako zbytek decku na Macu. Postup na Macu z kořene repa:

```
python3 -m venv .venv
.venv/bin/pip install -r app/requirements.txt playwright
.venv/bin/playwright install chromium        # nebo mít nainstalovaný Chrome, skript ho zkusí první
brew install ffmpeg
echo 'MAPBOX_TOKEN=…' > .env                 # veřejný token Mapboxu (soubor .env není v Gitu, dá ho Honza)
.venv/bin/python src/uloz_model.py           # modely, nejsou v Gitu
.venv/bin/python -u src/video_povoden.py --diag
.venv/bin/python -u src/video_povoden.py
```

Výstup se zapíše rovnou do `web/prezentace/video/` a `web/prezentace/grafy/`; po natočení stačí web nasadit (`docs/WEB.md`) a deck má nové video. Když `--diag` ukáže jiný výřez než na Windows (jiný poměr písma), stačí upravit `ZABERY` ve skriptu.

## Pro Tobiase: natočit video na Macu v písmu San Francisco a pushnout

Tenhle postup je napsaný tak, aby ho šlo zadat Claudovi na Tobiasově Macu doslova (`/tobias`, pak: „natoč video podle docs/VIDEO.md a pushni ho do main“). Trvá asi 15 minut, z toho natáčení 5 minut.

1. Repo a větev: `git switch tobias`, `git fetch origin`, `git merge origin/main` (video i skript jsou v `main`).
2. Prostředí (jednou): `python3 -m venv .venv`, `.venv/bin/pip install -r app/requirements.txt playwright`, `.venv/bin/playwright install chromium` (když je v Macu Chrome, skript ho použije první), `brew install ffmpeg`.
3. Token: do kořene repa soubor `.env` s řádkem `MAPBOX_TOKEN=pk.…` (veřejný token Mapboxu dá Honza; `.env` je v `.gitignore`, nikdy ho necommitovat ani nevypisovat).
4. Modely: `.venv/bin/python src/uloz_model.py` (model `ridge_bez2013` si skript dotrénuje sám při prvním běhu, asi 10 s).
5. Zkouška kamery: `.venv/bin/python -u src/video_povoden.py --diag` vypíše dočasnou složku se snímky `diag_0_zacatek.png` … `diag_4_vrchol_mezi_domy.png`; podívat se, že je v záběru celé město a potom voda mezi domy, štítky nahoře a lišta dole celé v obraze, žádné popisky podniků. Když něco nesedí, upravit `ZABERY` ve skriptu a zkoušku zopakovat.
6. Natáčení: `.venv/bin/python -u src/video_povoden.py`. Výstup: `web/prezentace/video/povoden_2013_decin_1080.mp4` (do 22 MB, 1920 × 1080, 30 fps, asi 24 s) a `web/prezentace/grafy/video_2013_poster.jpg`; kontrolní snímky `kontrola_1..4.png` v dočasné složce. Skript na konci vypíše ffprobe obou videí a `HOTOVO`.
7. Kontrola v decku: `.venv/bin/python -m http.server 8000 -d web`, otevřít http://localhost:8000/prezentace/, mezerník spustí video; písmo ve videu má být San Francisco (stejné jako nadpisy decku).
8. Commit a push jen těch dvou souborů: `git add web/prezentace/video/povoden_2013_decin_1080.mp4 web/prezentace/grafy/video_2013_poster.jpg`, `git commit -m "Tobias: úvodní video povodně 2013 natočené na Macu v písmu San Francisco"`, `git push origin tobias`, pak `/sync main` (nebo ručně `git merge origin/main` a `git push origin HEAD:main`). Nikdy `--force`.
9. Nasazení webu udělá Honza z Windows (`npx netlify-cli@latest deploy --prod --no-build --dir web`, viz `docs/WEB.md`), nebo hodinová GitHub Action, pokud má secrets. Napsat Honzovi, že video je v `main`.

Když Playwright na Macu nemá GPU a snímek trvá přes 4 s, skript sám přejde na další režim prohlížeče (`chromium`, nakonec viditelné okno `okno`); kdyby selhaly všechny, pustit `--rezim okno`. Video z Windows (v Interu) zůstává v `main` jako záloha, dokud ho Tobias nepřepíše.

## Jiná povodeň nebo město

`--povoden "9/2024 Boris (test)" --cil decin --model ridge_test --od 2024-09-13T00:00 --do 2024-09-18T12:00`; záběry `ZABERY` jsou dělané pro Děčín, pro Ústí je potřeba doladit středy záběrů přes `--diag`.
