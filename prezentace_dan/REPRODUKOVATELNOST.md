# Reprodukovatelnost main

Čistý klon `main` (commit 764984a, so 24. 10. 2026 01:49) do dočasné složky mimo repozitář. Codex v něm podle README,
CLAUDE.md, PRIPRAVA.md a app/README.md spustil, co jde bez velkého stahování, bez instalace a bez testu 2021–2025.
Zapisovat směl jen do klonu, v repu nic nezměnil. Plný výstup: `codex/reprodukovatelnost_codex.md` (27 min).

**Prostředí:** Windows 11, Python 3.12.10 (`C:\Users\danie\.venvs\hackathon`), pandas 3.1.0, numpy 2.5.2,
scikit-learn 1.9.1, LightGBM 4.7.0, Streamlit 1.66.1, pyarrow 26.0.0, `PYTHONUTF8=1`. Internet byl při bězích blokovaný,
běhy šly po jednom. Na notebooku zároveň běžely další dvě session, volná RAM kolem 1–2 GB.

## Co prošlo

| Příkaz | Výsledek | Čas | Proti dokumentaci |
|---|---|---|---|
| načtení dat (`src/data.py: nacti`) | prošlo | 24 s | 175 320 hodin, 14 sloupců: sedí |
| `python src/porovnej.py jako_ted --rychle` | prošlo | 6 s | Děčín +24 h 44,4 cm: sedí |
| `python src/porovnej.py jako_ted ridge` | prošlo | 82 s | průměr 44,3 a 17,1 cm, Ridge Děčín +24 h 15,5 cm: sedí |
| `python src/porovnej.py --prehled` | prošlo, ale část výsledků vyřadil jako staré | 9 s | viz problém 2 |
| `python src/uloz_model.py` | uloženo 6 modelů Ridge | 53 s | dokumentace uvádí asi 5 s |
| `python app/test_app.py` | 9 z 9 kontrol | 142 s | výchozí hladina 646 cm, předpověď +24 h 738 cm: sedí |
| `python src/procenta.py ridge mlp lgbm fyzika jako_ted` | prošlo nad uloženými předpověďmi | 26 s | 17,1 / 17,8 / 23,1 / 24,8 / 44,3 cm: sedí |
| `python src/krizova_validace.py ridge` | prošlo | 217 s | 20,1 ± 7,7 cm, „jako teď“ 45,2 ± 13,9 cm: sedí |

**Závěr:** hlavní výsledky týmu (validace, vícenásobná validace, procenta, aplikace) jdou z čistého klonu zopakovat
a na desetinu sedí s `docs/PREHLED.md`.

## Problémy

| Závažnost | Co | Návrh opravy (kdo rozhodne: Ondra) |
|---|---|---|
| vysoká | **Otisk verze výsledků závisí na koncích řádků.** Na Windows (Git `core.autocrlf=true`) vychází 69a6db32, na Macu 9a31181e, i když data a kód jsou stejné. `--prehled` pak výsledky z druhého systému vyřadí jako „staré“ (tady síť a fyziku). Hlášeno už v pá 20:20 (`docs/DENIK.md`). | V `src/porovnej.py: verze()` u `.py` souborů před hashováním nahradit `\r\n` za `\n`, nebo do `.gitattributes` přidat `*.py text eol=lf`. |
| střední | **Nové běhy LightGBM a fyzikálního modelu nedoběhly v limitech, které si kontrola dala** (6 a 2 min). Příčina neurčená. Večer stejný kód na tomhle notebooku doběhl (LightGBM do minuty na model, větev dan), takže nejspíš šlo o vytíženou RAM se dvěma dalšími session, ne o chybu. Uložené výsledky obou modelů sedí (`procenta.py`). | Při nácviku pustit `python src/porovnej.py lgbm fyzika --rychle` na volném počítači a zapsat čas. |
| střední | **Verze knihoven nejsou zapsané.** README instaluje balíky bez verzí. Pro přestavbu mapových podkladů je potřeba `pyproj`, který README nezmiňuje. | Do `app/requirements.txt` a README dopsat ověřené verze (stačí výpis z tohoto běhu) a `pyproj` jako volitelný balík. |
| střední | **Otisk nezahrnuje kód modelu, `data.py` ani verze knihoven.** Předpovědi v `results/predpovedi/` se přepisují pod stejným jménem a aplikace ani `procenta.py` nekontrolují, ke kterému běhu patří. | Do JSON i parquetu ukládat stejné ID běhu, aplikace ať ho ukáže. |
| střední | **Záložka testu v aplikaci píše „trénink do 2018“**, ale uložené testové předpovědi jsou z modelu učeného do 2020 (tak se test dělal). | V `app/app.py` u testu napsat, že model byl učený na 2006–2020. |
| nízká | `docs/PREHLED.md` (Další kroky) píše, že export trénuje jen na train, přitom `uloz_model.py --vse` existuje. Výchozí model aplikace i v režimu Dnešek je `ridge` učený do 2018, `ridge_vse` se musí zvolit v menu (nález fact-checku). | Opravit větu v PREHLED a pro Dnešek předvolit `ridge_vse`. |
| nízká | `src/krizova_validace.py` vypisuje varování při prázdném seznamu vrcholů. | Ošetřit prázdný seznam v `src/evaluate.py` (jen kosmetika). |

## Co se neověřovalo a proč

- Stahování dat ČHMÚ a přestavba tabulky (`src/stahni_chmu_hydro.py`, `src/data.py`): stovky MB, zadání to zakazovalo.
  Tabulka `data/external/labe_hodinove.parquet` je v Gitu, takže stahování pro zopakování výsledků není potřeba.
- Trénink neuronových sítí (`mlp`, `tcn`): trvá minuty až desítky minut, RAM. Uložené výsledky sedí (`procenta.py`).
- Finální test 2021–2025: záměrně ne. Test aplikace jen zobrazil uložené předpovědi Borise.
- Živá data ČHMÚ, Open-Meteo a mapové dlaždice: internet byl blokovaný. Aplikace bez nich jede na historii.
- Mac: kontrolovalo se jen na Windows. Rozdíl v otisku verze je ale známý (problém 1).
