# Revize aplikace (app/, Honza) před demem

Dan, so 24. 10. 2026 02:00–04:00, stav `origin/main` 59956c9. Aplikaci v main jsem neměnil. Opravy jsou jako návrhy
v `patche/01.patch` … `09.patch`: každý jde aplikovat samostatně i všechny po sobě (`git apply nejistota_dan/patche/NN.patch`
z kořene repa) a se všemi prošel `python app/test_app.py --dnesek` (10 z 10). Zdroje nálezů: nezávislá statická revize
kódu, nezávislá revize Codexem (`codex/kontrola_b_aplikace.md`) a vlastní spuštění. Každý nález níž jsem ověřil v kódu.

## Co jsem spustil

- `python app/test_app.py`: na čistém stavu (modely nejsou v Gitu, aplikace si je natrénuje) **9 z 9 OK**,
  první načtení **23,5 s** (README slibuje asi 10 s; počítač byl vytížený), druhé 7 s. S `--dnesek` **10 z 10**,
  Dnešek s internetem 16–21 s (stahuje 48 souborů ČHMÚ).
- Simulovaná „visící“ Wi-Fi (proxy na nedosažitelnou adresu): Dnešek čekal **42 s**, než ukázal srozumitelnou chybu,
  a to už měl uložené soubory recent/; na čistém klonu by stahoval 4× víc souborů (řádově 2–3 minuty).
- Výchozí obrazovka Děčín 15. 1. 2011 9:00: teď 646 cm, za 12 / 24 / 36 h 705 / 738 / 756 cm, skutečnost pak byla
  685 / 703 / 724 cm. Dnešní pásmo „nejspíš“ 712–794 cm na 24 h skutečnost **mine** (703), nové 80% pásmo 708–794 taky
  (těsně). Prezentující by to měl vědět (viz V4).
- Čísla v aplikaci proti `docs/PREHLED.md`: validace 17,1 cm (průměr 6 kombinací), Děčín +24 h 15,5 cm, test 22,4 cm,
  Děčín +24 h na testu 17,5 cm, 2. stupeň 3 z 4, 12 h, 1 planý: **sedí**. Nesedí texty o tom, z jakého modelu jsou
  předpovědi Borise (V1), a popisek tabulky testu (V2).

## Kritické (může shodit nebo zkazit demo)

**K1. Bez internetu jsou Mapa a Animace prázdný tmavý obdélník bez vysvětlení.** `animace.py:29, 271` (deck.gl
z unpkg.com), `mapbox_mapa.py:28, 251` (mapbox-gl z api.mapbox.com); i bez tokenu potřebuje mapa dlaždice
OpenStreetMap a výšky z AWS (`mapa.py`). Slajd 9 a video Borise přitom stojí právě na mapě. README to říká
(„Mapa a animace bez něj použitelné nejsou“), na obrazovce ale porota uvidí jen prázdno.
- Patch `02.patch`: když se knihovna nenačte, iframe ukáže větu „Animace / Mapa potřebuje internet… pusťte záložní video“.
- Mimo kód: **záložní video** a hotspot z mobilu; před porotou projít všechny záložky (načtou se dlaždice).

**K2. Dnešek na špatné Wi-Fi zamrzne na minuty, chybu si pamatuje 10 minut a rozbitý soubor uloží natrvalo.**
- `aktualni.py:39`: 48 požadavků, každý s timeoutem 30 s, stránka mezitím jen „Running…“.
- `app.py:76`: `@st.cache_data(ttl=600)` si pamatuje i neúspěch (`ok=False`); když se síť vrátí, Dnešek dál 10 minut hlásí
  chybu a přepnutí tlačítka nepomůže (potvrdil i Codex).
- `aktualni.py:43–45`: soubor se zapíše na disk dřív, než se ověří, že je to JSON. Na Wi-Fi s přihlašovací stránkou se
  do `data/raw/chmu_aktualni/recent_*.json` uloží HTML a Dnešek je rozbitý, dokud někdo složku nesmaže.
- Patch `03.patch`: timeout (5, 15) s, na disk jen platný JSON, rozbitý soubor se smaže a stáhne znovu, spinner
  „Stahuji živá data ČHMÚ…“, po chybě `dnes_c.clear()`, Open-Meteo timeout (5, 10).
- Mimo kód: Dnešek před porotou jednou zapnout (soubory recent/ se uloží, další načtení je rychlé).

## Vysoké (špatné číslo nebo matoucí text)

**V1. U Borise aplikace píše „Předpovědi jsou z modelu učeného do roku 2018“, ale jsou z modelu učeného do 2020**
(`app.py:243`; `results/predpovedi/ridge_test.parquet` vyrobil `porovnej.py --test` s `finalni=True`, PREHLED:
„natrénovaný na všem do 2020“). Mapa „Celá povodeň“ a Animace u Borise ale opravdu počítají model `ridge` do 2018,
takže dávají trochu jiná čísla než slajd (vrchol 611 cm, 27 h). **Video Borise se nahrává z mapy, ne z testu.**
- Patch `04.patch` opraví text. Video: před nahráním porovnat hodnotu u vrcholu v mapě s 611 cm, případně říct,
  že video je z modelu do 2018.

**V2. U Borise tabulka ukazuje celý test 2021–2025, ne Borise, a popisek tvrdí „průměr přes 4 povodně“**
(`app.py:266–280`). Propásnutý 2. stupeň v tabulce je únor 2024, ne Boris. Patch `04.patch`: popisek rozliší validaci
a test a řekne, že předstih je nejvýš horizont a propásnutá povodeň = 0.

**V3. Text pod Mapbox mapou popisuje úřední záplavová území (DIBAVOD), mapa ale ukazuje rozliv z výškového modelu
(ČÚZK DMR 5G)** (`app.py:293–296, 339–342`; `mapbox_mapa.py:403` výchozí `uredni: false`). Patch `04.patch`.

**V4. Pásmo „nejspíš“ slibuje víc, než platí, a na výchozí obrazovce ho skutečnost mine.** Popisek (`app.py:228`)
„90 % chyb na tréninku; na povodních… asi 8 z 10“: vnořená kontrola na 22 povodních (`ZPRAVA_NEJISTOTA.md`) dává
dnešnímu pásmu na povodních 59–72 % a na začátku vzestupu 15 %.
- Patch `01.patch` napojí nové pásmo (`nejistota_dan.pasmo`, 80 %, ověřené 79–80 % na povodních, při rychlém vzestupu
  ~2 ze 3) a opraví popisky. Potřebuje sloučit `nejistota_dan/` z větve `dan-nejistota` (modul + `kvantily.json`);
  bez něj aplikace zůstane u starého pásma, nic nespadne.
- Patch `09.patch` (volitelný): při přehrávání historie tečkovaně dokreslí, co pak opravdu nastalo, takže porota vidí,
  jak předpověď dopadla. Na výchozí obrazovce bude vidět, že model o 20–35 cm přestřelil, to je poctivé a dá se na
  tom vysvětlit pásmo.
- Prezentující: „za 24 h model říkal 738 cm, skutečnost byla 703 cm, pásmo to skoro zachytí“.

**V5. Dnešek počítá s modelem `ridge` učeným do 2018, ne s `ridge_vse` (do 2025), a `ridge_vse` při přehrávání
historie předpovídá povodně, na kterých se učil** (`app.py:135–151`; potvrdil i Codex). Patch `05.patch`: Dnešek
použije `ridge_vse`, výběr `ridge_vse` v historii ukáže varování.

**V6. Animace a mapa „Celá povodeň“ se spustí v záložce, kterou nikdo nevidí** (`animace.py:596`, `mapbox_mapa.py:836`:
`hraje = true`; Streamlit vykreslí všechny záložky hned) a rozvržení počítané z `innerWidth` může v neviditelném iframu
vyjít z nuly (záběr oddálený). Patch `06.patch`: start po kliknutí na Přehrát, `innerWidth || 1270`. Ověřit ručně
v prohlížeči (AppTest JavaScript nespouští).

## Střední

- **S1. `.env` v jiném kódování shodí celou aplikaci** (`mapa.py:37`: `read_text(encoding="utf-8")`; PowerShell 5.1
  `echo … > .env` dělá UTF-16). Patch `07.patch` (`utf-8-sig`, `errors="replace"`, mezery, uvozovky). Na Macu `.env`
  dělat v Terminálu, ne v TextEditu (RTF).
- **S2. Pomalý start a kopírování 133 MB tabulky při každé akci** (`app.py:42`: `@st.cache_data` vrací kopii; volá se
  3× při každém kliknutí). Patch `08.patch` (`@st.cache_resource`, tabulku nikdo nemění). Před demem
  `python src/uloz_model.py` a `--vse`, aplikaci jednou otevřít a server nerestartovat.
- **S3. Instalace na Macu:** `requirements.txt` má jen dolní meze (`streamlit>=1.60`), `styl.py` cílí CSS přes
  `data-testid`, nová verze Streamlitu může vzhled rozbít; vyzkoušeno se Streamlit 1.66.1, plotly 7.1.0, pydeck 0.9.3.
  Prostředí na Tobiasově Macu připravit a vyzkoušet předem (instalace potřebuje internet). Python z Xcode je 3.9,
  README chce 3.10+. První `streamlit run` se ptá na e-mail: `--server.headless true` nebo Enter.
- **S4. Hranice starého pásma nesedí s kalibrací** (`predikce.py:74` bere `hladina >= hranice`, `src/nejistota.py`
  `pd.cut` uzavřené zprava): při hladině přesně 300, 450 nebo 600 cm aplikace vezme sousední pásmo (Děčín +24 h
  při 450 cm −37/+9 místo −19/+19 cm). Patch `01.patch` to obchází (nové pásmo), jinak opravit na `>`.
- **S5. Rozliv z výškového modelu se ukáže i pod spočteným rozsahem** (`mapbox_mapa.py:73`: na začátku Borise kolem
  150 cm se vezme polygon pro 300 cm a „pod vodou X ha“). Oprava: `if (h < U[0].h - 10) return -1;` (bez patche,
  potřebuje vyzkoušet v prohlížeči).
- **S6. Tlačítko „Přehrát povodeň 1/2011“** (`app.py:329`) blokuje stránku 40–60 s, s tokenem přepne z Mapboxu na
  pydeck a mapa bliká; totéž lépe dělá „Celá povodeň“. Doporučení: na demu nemačkat (nebo ukázat jen bez tokenu).
- **S7. Projektor:** iframy 700–720 px (lišta animace pod okrajem na 1280×720), drobné popisky 11–13,6 px na tmavém
  pozadí, písma z Google Fonts (bez sítě se vezme systémové). Zkusit zoom prohlížeče 125 % a „Celá obrazovka“ v mapě.

## Nízké

- Den v menu ve formátu 2011/01/15, jinde 15. 1. 2011; „1.3 h“ s tečkou; „1000 m³/s“ bez mezery (`app.py:178`).
- Den a hodina v menu aktivní i v Dnešku, kde se nepoužijí; názvy modelů `ridge` / `ridge_vse` laik nepochopí
  (`format_func`).
- `app.py:366`: popisek „© Mapbox, © Maxar“ i bez tokenu, kdy jde o OSM a AWS.
- `app.py:85`: hledání `*_ridge.json` by chytilo i `*_lgbm_c_ridge.json` (teď náhodou ne); přidat `z["model"] == nazev`.
- Změna času: 31. 10. 2010 2:00 jde vybrat jen jednou, jarní neexistující 2:00 se tiše posune.
- Věta „srážky do modelu nevstupují“ se v Dnešku může zobrazit dvakrát.

## Co vyzkoušet ručně na Tobiasově Macu (AppTest to nepokryje)

1. Čistý klon podle README: verze Pythonu, instalace, `uloz_model.py` i s `--vse`, první načtení.
2. `.env` z Terminálu, satelitní mapa; pak `.env` přejmenovat, restartovat: mapa na OpenStreetMap, nic nespadne.
3. Vypnout Wi-Fi a projít všechny záložky: co je v Mapě a Animaci (s patchem 02 věta, bez něj prázdno). Dnešek bez sítě:
   jak dlouho čeká; zapnout Wi-Fi a Dnešek znovu: nedrží se chyba (bez patche 03 drží 10 minut).
4. Mapa → Celá povodeň → 9/2024 → Děčín: hodnota u vrcholu proti slajdu (611 cm), až potom nahrát video.
5. Animaci otevřít až po chvíli na jiné záložce: neběží už? Je záběr správně přiblížený?
6. Projektor 1280×720 a 1920×1080: lišta animace, čitelnost, kolečko myši nad mapou zoomuje místo posunu stránky.
7. Safari i Chrome (WebGL, celá obrazovka).

## Co má tým ráno rozhodnout

- Které patche vzít do main (doporučuji 02, 03, 04, 05, 07, 08 jako bezpečné; 01 + `nejistota_dan/` jen když chce
  tým nové pásmo; 06 a 09 po ručním vyzkoušení v prohlížeči).
- Odkud je video Borise (mapa = model do 2018) a co přesně říct ke „27 h předem“.
