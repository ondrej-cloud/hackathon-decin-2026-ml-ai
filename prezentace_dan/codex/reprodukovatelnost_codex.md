# Reprodukovatelnost main

**Klon:** větev `main`, commit `764984a259cd68dbe6949c970c61815fa1e9c150`, kontrola 24. 10. 2026.

**Prostředí:** Windows 11, Python 3.12.10 z předepsaného prostředí `C:\Users\danie\.venvs\hackathon\Scripts\python.exe`. pandas 3.1.0, numpy 2.5.2, scikit-learn 1.9.1, LightGBM 4.7.0, Streamlit 1.66.1, pyarrow 26.0.0, matplotlib 3.11.2. Nastaveno `PYTHONUTF8=1`; těžké běhy probíhaly postupně.

**Co slibuje dokumentace**

- **README.md a PRIPRAVA.md:** Python 3.11+, virtuální prostředí, instalaci knihoven a kontrolu importů; na Macu navíc `libomp`. GitHub a Kaggle vyžadují přihlášení.
- **CLAUDE.md, Stav:** hotový datový Parquet v Gitu, společnou validaci, rychlé spuštění modelů, přehled výsledků a export Ridge pro aplikaci.
- **app/README.md:** instalaci přes `app/requirements.txt`, spuštění Streamlitu, automatické dotrénování chybějících modelů a neinteraktivní kontrolu. Historická data fungují lokálně; živá data a mapové zdroje potřebují internet. Mapbox token je volitelný.

**Provedené kroky**

Níže jsou cílové příkazy. Spouštěly se auditním obalem s blokovaným internetem, čtením přihlašovacích souborů a zápisy mimo klon.

| Příkaz | Výsledek | Čas | Číslo proti dokumentaci |
|---|---|---:|---|
| `python .repro_audit/import_check.py` | Základní importy a data prošly | 23,6 s | 175 320 hodin, 14 sloupců, 82 chybějících hodnot: souhlasí |
| `python src/porovnej.py jako_ted --rychle` | Prošel | 5,9 s | Děčín +24 h **44,4 cm**, souhlasí |
| `python src/porovnej.py jako_ted ridge` | Celá validace prošla | 81,8 s | Průměry **44,3 a 17,1 cm**; Ridge Děčín +24 h **15,5 cm**: souhlasí |
| `python src/porovnej.py --prehled` | Prošel, část výsledků vyřadil jako staré | 9,4 s | Problém otisku popsaný níže |
| `python src/uloz_model.py` | Uloženo všech 6 modelů Ridge | 52,8 s | Dokumentace uvádí přibližně 5 s; zde pomalejší |
| `python app/test_app.py` | Opakovaný běh: **9/9**, návratový kód 0 | 141,5 s | Výchozí hladina **646 cm**, předpověď +24 h **738 cm**: souhlasí |
| `python src/procenta.py ridge mlp lgbm fyzika jako_ted` | Prošel nad uloženými validačními předpověďmi | 26,0 s | **17,1 / 17,8 / 23,1 / 24,8 / 44,3 cm**: vše souhlasí |
| `python src/krizova_validace.py ridge` | Prošel | 217,4 s | Ridge **20,1 ± 7,7 cm**, baseline **45,2 ± 13,9 cm**: souhlasí |
| `python src/porovnej.py lgbm fyzika` | Časový limit před prvním výsledkem | 360,9 s | Nový trénink LightGBM neověřen; fyzika v tomto běhu nezačala |
| `python src/porovnej.py fyzika --rychle` | Časový limit bez výsledku | 130,6 s | Nový trénink neověřen; nastavený limit 120 s, zbytek ukončení procesu |

První AppTest selhal za 53,5 s kvůli příliš přísnému auditnímu zákazu localhostu. Po povolení interního loopbacku prošel; při ukončení ještě vypsal `WinError 5` při úklidu dočasné složky. Kontrola používala variantu bez Mapbox tokenu, neověřovala vykreslení JavaScriptu v prohlížeči.

**Problémy a návrhy oprav**

| Závažnost | Zjištění | Navržená změna |
|---|---|---|
| **Vysoká** | Nové běhy LightGBM a fyzikálního modelu nedoběhly v uvedených limitech. Příčina nebyla určena. | `src/porovnej.py`: přidat průběžný výpis před a po načtení, tvorbě vstupů, tréninku a predikci; doložit dokončený běh na Windows. |
| **Vysoká** | Otisk závisí na koncích řádků. Stejné zdroje dávají s CRLF `69a6db32`, s LF `9a31181e`. Přehled proto vyřadil například MLP a fyziku. | `src/porovnej.py:verze()` normalizovat text na LF; sjednotit konce řádků přes `.gitattributes`. |
| **Střední** | Otisk nezahrnuje kód modelu, `data.py` ani verze knihoven. Předpovědi se přepisují pod stejným názvem; aplikace a procenta jejich verzi nekontrolují. | `src/porovnej.py`, `src/procenta.py`, `app/app.py`: společné ID běhu, metadata prostředí a kontrola shody JSON–Parquet. |
| **Střední** | Chybí pevně zaznamenané verze závislostí. Pro obnovu mapových podkladů navíc chybí nedokumentovaný `pyproj`, který zde není instalovaný. | README, PRIPRAVA a requirements: přidat ověřený seznam verzí a samostatné závislosti pro přípravu map. |
| **Střední** | Testová záložka aplikace tvrdí trénink do 2018, ale generátor finálního testu používá trénink do 2020. | `app/app.py`: odlišit původ archivovaných testových předpovědí od historického modelu `.joblib`. |
| **Nízká** | `docs/PREHLED.md` stále tvrdí, že export trénuje pouze na train, přestože existuje `--vse`. Křížová validace vypisuje varování při prázdném seznamu vrcholů. | Aktualizovat přehled; v `src/evaluate.py` ošetřit prázdné vrcholy bez výpočtu průměru. |

Surová data v `data/raw/` a modely `.joblib` v čistém klonu chybějí očekávaně. Zpracovaná data i mapové podklady přítomné jsou a Ridge se podařilo vytvořit. V kontrolovaném `src/` a `app/` nebyly nalezeny pevné cesty na konkrétní počítač.

Finální test ani metriky let 2021–2025 nebyly počítány; AppTest pouze zobrazoval uložené výsledky Borise. Neběhly instalace, internetové dotazy, server ani trénink neuronových sítí. Zdrojový kód a dokumentace zůstaly beze změn; běhy zapsaly výsledky, modely a [auditní protokoly](C:/Users/danie/AppData/Local/Temp/claude/c--hackathon/d470497f-9d22-4ebe-bdb9-82aae6ecf070/scratchpad/klon_main/.repro_audit/runs.jsonl).

Jádro řešení s Ridge je z čistého klonu reprodukovatelné a všechna požadovaná hlavní čísla souhlasí. Aplikace prošla neinteraktivní kontrolou. Úplná reprodukovatelnost všech modelů zatím potvrzena není; hlavní slabiny jsou nedokončené běhy a přenositelnost evidence výsledků mezi Windows a Macem.