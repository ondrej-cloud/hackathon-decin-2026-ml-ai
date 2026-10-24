# Aplikace: předpověď hladiny Labe v Děčíně a Ústí

Streamlit aplikace pro povodňovou komisi města Děčín a lidi u řeky. Ukáže hladinu Labe teď a předpověď na 12, 24 a 36 hodin se stupněm povodňové aktivity. Zadání je v [docs/UKOL_APLIKACE.md](../docs/UKOL_APLIKACE.md).

## Spuštění (z kořene repozitáře, Python 3.10 a novější)

Windows (PowerShell):
```
git pull
python -m venv .venv
.venv\Scripts\python -m pip install -r app/requirements.txt
$env:PYTHONUTF8=1
.venv\Scripts\python -m streamlit run app/app.py
```
Mac (Terminál):
```
git pull
python3 -m venv .venv
.venv/bin/python -m pip install -r app/requirements.txt
.venv/bin/python -m streamlit run app/app.py
```
Aplikace se otevře na http://localhost:8501. Pro satelitní mapu vytvoř v kořeni repa soubor `.env` s řádkem `MAPBOX_TOKEN=...`, token dá Honza (do Gitu nepatří). Bez něj mapa i animace běží s OpenStreetMap.

Modely v `models/` nejsou v Gitu. Když chybí, aplikace si ridge a ridge_vse natrénuje sama (asi 5 s). Předem je uloží `python src/uloz_model.py` (ridge, učený do 2018, pro přehrávání historie) a `python src/uloz_model.py --vse` (ridge_vse, učený na všem do 2025, pro dnešek).

## Co aplikace ukazuje

Levý panel má sekce Stanice (Děčín, Ústí), Zdroj dat (přepínač Dnešek, po startu zapnutý), Okamžik předpovědi (den a hodina pro přehrávání historie, výchozí 15. 1. 2011 9:00; v Dnešku zamčené) a Model.

- Teď: vodočet (měrná lať se stupni povodňové aktivity, voda teď, značky předpovědi za 12, 24 a 36 h a pruhy rozmezí nejistoty), vedle něj odečty se stupněm, věta pro laika a graf 3 dnů.
- Přepínač Dnešek: stáhne živá data ČHMÚ a vydá předpověď na teď, vedle ní oficiální předpověď ČHMÚ (i na vodočtu) a srážky v povodí z Open-Meteo. Je zapnutý hned po startu; když data nejdou stáhnout, aplikace ukáže varování v panelu a přehrává historii.
- Jak dobře to funguje: povodeň (4 z validace a Boris 9/2024 z testu) a horizont, souhrn (chyba, předstih varování, propásnuté povodně, plané poplachy proti „bude jako teď“), graf a tabulka všech horizontů.
- Mapa povodí: nahoře přehrávač. Režim „Celá povodeň: předpověď × skutečnost“ nebo „Zvolený okamžik“, výběr povodně a tlačítko Přehrát povodeň, které přepne do celé povodně. Ve zvoleném okamžiku je 3D mapa 12 stanic (výška sloupce je průtok, barva stupeň) a pohled Děčín nebo Ústí vyplní záplavové území podle předpovědi. Bez tokenu Mapboxu tlačítko projde vybranou povodeň po 6 hodinách na jednodušší mapě.
- Animace povodně: výběr povodně, kapky tečou po řekách k Děčínu, tlačítko spustí čas, posuvník ho posune.

## Internet

Potřebují ho dlaždice mapy a výšek (Mapbox nebo OpenStreetMap), animace (knihovna deck.gl a písmo) a živá data ČHMÚ pro Dnešek. Bez internetu funguje Teď a Jak dobře to funguje včetně přehrávání historie, data jsou v repu. Mapa a animace bez něj použitelné nejsou.

## Časté potíže

- Port 8501 je obsazený: přidej `--server.port 8502`.
- Windows, chyba kódování: před spuštěním `$env:PYTHONUTF8=1`.
- Mapa je bez satelitu: v kořeni repa chybí `.env` s `MAPBOX_TOKEN=...`; po doplnění aplikaci restartuj.
- První načtení trvá asi 10 s (data, případně trénink modelů), další jsou rychlé.
- V Dnešku jsou Mělník a Nymburk dopočtené z bilance vody, ČHMÚ je operativně nezveřejňuje.
- Dnešek hlásí, že data nejdou stáhnout: zkontroluj internet a zkus to za chvíli.

## Kontrola

`.venv\Scripts\python app/test_app.py` (Mac: `.venv/bin/python app/test_app.py`) projde aplikaci bez prohlížeče a ke každému kroku vypíše OK nebo CHYBA. S `--dnesek` ověří i živá data (potřebuje internet).
