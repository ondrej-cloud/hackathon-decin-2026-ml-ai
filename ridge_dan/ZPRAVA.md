# Vlastní Ridge pro Labe v Děčíně za 24 h: zpráva

Dan, větev `dan-ridge`, pá 23. 10. 2026 20:28–21:55. Průběh po krocích v `PRUBEH.md`, všechny pokusy v
`POKUSY_RIDGE.md` a `vysledky/pokusy.jsonl`, nálezy Codexu v `NALEZY_CODEX.md`.

## Shrnutí

- Nejlepší model je Ridge na odmocninách průtoků **30 stanic** ČHMÚ (týmových 12 + 18 dalších) a stavech Děčína
  a Ústí, se stejnými zpožděními jako týmový model, alpha 1. Data jsou z vlastní tabulky postavené přímo z otevřených
  dat ČHMÚ, ne z Ondrovy.
- Na **jednorázovém testu 2021–2025** je lepší než týmový Ridge: chyba na povodních **16,1 cm proti 17,5**
  („jako teď“ 44,8), na začátku vzestupu 27,0 proti 32,0, předstih varování před 2. stupněm 14,5 h proti 12,5 h,
  stejný počet planých a propásnutých poplachů.
- Na **validaci** je na povodních horší: **17,8 cm proti 15,5** („jako teď“ 44,4). Celý rozdíl dělá jarní povodeň
  2006 (tání, 875 cm), kde model na stoupání přestřelí až o 65 cm a na vrcholu podstřelí. Ve všem ostatním
  (klid, rychlé stoupání, začátek vzestupu, předstih všech tří stupňů, plané poplachy) je lepší i na validaci.
- Model se vybíral časovou křížovou validací uvnitř tréninku (18 povodní), tam je lepší o 1,5 cm (14,2 proti 15,6),
  ve 4 z 5 bloků let. Denní srážky, sníh, teplota, váhy, dva režimy, cíl v průtoku, aktualizace podle chyby ani
  silnější regularizace nepomohly.
- Slabina zůstává stejná jako u týmového modelu: **vrcholy velkých povodní** (na testu chyba vrcholu 29 cm proti 21).

## Laťka: pozor na 17,1

Týmový Ridge má na validaci 17,1 cm jako **průměr přes 6 kombinací** (Děčín a Ústí × 12, 24, 36 h). Pro Děčín +24 h
je to **15,5 cm** a s tím se tady srovnává. „Jako teď“ pro Děčín +24 h je 44,4 cm, to sedí.

## Data (vlastní tabulka)

`data_ridge.py` → `tabulka/labe_ridge.parquet` (není v Gitu), 175 320 hodin 2006–2025 v UTC, 65 sloupců.
Stahování šetrné (`stahni.py`): po jednom souboru, pauza 1–1,5 s, cache na disku, nic dvakrát, seznam všech
stažených adres v `STAZENO.csv` (787 souborů včetně metadat a seznamů, licence ČHMÚ CC BY 4.0).

- **Hodinové stavy a průtoky** (`opendata.chmi.cz/hydrology/historical/data/hourly/`), 31 stanic × 20 let.
  Kontrola: 12 týmových sloupců je přesně stejných jako v `data/external/labe_hodinove.parquet` (rozdíl 0, stejné
  díry). Ondrovu tabulku jsem jen přečetl na tuto kontrolu, na trénink ne. Stejná oprava ledu v Děčíně 2/2006.
  Děčín (číslo hydrologického pořadí 1-14-04-0010, 50 974 km²) leží **pod** soutokem s Ploučnicí i Bílinou.
  Němčice vyřazené (díra 170 h v 10/2020 ve validaci), Terezín (dolní Ohře) a Litoměřice mají data až od 2013/2017.
- **Srážky**: hodinové řady ČHMÚ začínají až 2018, na trénink 2006–2018 nestačí. Proto denní úhrny 84 srážkoměrů
  v 11 dílčích povodích (povodí podle čísla hydrologického pořadí zakódovaného v čísle stanice). Ověřeno na
  hodinových datech 2019, že denní hodnota s razítkem D 06:00Z je součet D 07:00Z … D+1 06:00Z (rozdíl 0,02 mm),
  takže do tabulky vstupuje až od D+1 07:00 UTC.
- **Sníh a teplota**: výška sněhu 38 stanic (pozorování 06:00Z, bráno až od dalšího dne 07:00Z), teplota 31 stanic
  z termínů 06/13/20 UTC (průměr posledních tří, hodinu po posledním).

## Vyhodnocení, srovnatelné s týmem

- Split a metriky převzaté z `src/evaluate.py` (git blob `5fde7d8d`, commit 418debf): `evaluate.casti()` čte Ondrovu
  tabulku, proto je v `hodnoceni.py` převzaté řádek po řádku a ověřené, že dává pro +12/24/36 h stejné značky
  (0 rozdílů z 175 320 hodin). `vyhodnot()` a `varovani()` se importují přímo.
- Týmový Ridge na mé tabulce dává na validaci přesně 15,5 cm na stejných 19 264 řádcích, předpovědi shodné
  s týmovým kódem na Ondrově tabulce na 1e-5.
- Srovnání vždy na **stejných řádcích** (průnik). Na validaci i testu mají všechny tři modely stejné řádky
  (19 264 / 43 764).
- Navíc proti týmové metrice: chyba v klidu (val 2019–2020, test stav pod 300 cm), rychlé stoupání (za 24 h
  stoupne aspoň o 50 cm), začátek vzestupu (totéž, ale posledních 6 h ještě skoro nestoupalo), varování pro
  všechny tři stupně 400 / 490 / 560 cm.
- Proti přeladění validace: o všem rozhodovala časová CV v tréninku (6 bloků let, mezera 10 dní, průměr přes
  18 povodní nad 400 cm, každá se stejnou váhou), pravidlo „přidat jen při zlepšení aspoň o 0,3 cm“. Do validace
  jsem nahlédl 4× (reprodukce laťky, milník, rozbor po povodních, popis finálního modelu), všechna nahlédnutí
  jsou vypsaná v `POKUSY_RIDGE.md`. Rozbor povodně 2006 mě poslal hledat robustnější model; o tom rozhodovala
  zase jen CV a žádný takový model nakonec nezůstal. **Test jsem pustil jednou**, pá 21:49, s modelem a kódem
  commitnutými v 97c2f6e (obsahové otisky souborů jsou ve `vysledky/TEST_HOTOVO.json`; příznak `zmeny: true`
  v otisku je od té značky samotné, založila se těsně před ním).
- Úniky: příznaky jen z času ≤ t, denní data posunutá na dobu, kdy jsou známá, StandardScaler se fituje jen na
  tréninku, řádky, jejichž vstupy (až k nejstaršímu použitému měření) nebo cíl leží v jiné části, se vyhazují.

## Nejlepší model

`model_ridge.py`, konfigurace `FINALNI = dict(stanice="vse")`, `ALPHA = 1`:

- vstupy (224): stav Děčína a Ústí před 0, 1, 2, 3, 6, 12, 24 h; odmocnina průtoku před 0, 3, 6, 12, 18, 24, 36 h
  pro 30 stanic: týmových 12 (Děčín, Ústí, Louny, Mělník, Vraňany, Kostelec, Praha-Chuchle, Nymburk, Jizera
  Předměřice, Beroun, Sázava Nespeky, Přelouč) a 18 nových: Ploučnice (Benešov, Stružnice, Česká Lípa), Bílina
  Trmice, Ohře Žatec a Karlovy Vary, Berounka Zbečno, Liblín, Plzeň-Bílá Hora, Střela Plasy, Litavka Beroun,
  Vltava Zbraslav, Sázava Kácov a Zruč, Chrudimka Nemošice, Orlice Týniště, Cidlina Sány, Jizera Bakov;
- StandardScaler + Ridge(alpha = 1), cíl = stav v cm za 24 h. Alpha z CV: 0,01 / 0,1 / 1 vycházejí stejně
  (14,17), bere se největší.
- Největší váhy (cm na jednu směrodatnou odchylku vstupu): stav Děčína teď +57, Vltava Zbraslav teď +26 a před 3 h
  −19 (rozdíl = jak rychle stoupá), průtok Děčína teď −22 (stav a průtok téže stanice nesou skoro totéž a model si je
  dorovnává), Ústí teď +17, Praha teď +17, Mělník teď +14. Jako u týmového modelu se váhy čtou po skupinách, ne jednotlivě.
- Odkud je zisk (ablace v CV): nejvíc horní Ohře (Žatec, Karlovy Vary) a horní Labe (Orlice, Chrudimka, Cidlina),
  pak Berounka a Jizera, tedy stanice, které vidí vlnu dřív. Přítoky mezi Ústím a Děčínem jsou při povodních malé
  (na vrcholech Ploučnice 1–14 % průtoku Děčína, Bílina 1–3 %), vlna „z ničeho“ u Děčína z nich nevzniká.

## Srovnání (Děčín +24 h, stejné řádky)

| | můj Ridge, 30 stanic | týmový Ridge | „jako teď“ |
|---|---|---|---|
| CV v tréninku: povodně (18 povodní) | **14,2** | 15,6 | |
| CV: rychlé stoupání | **28,8** | 33,8 | |
| **VAL: chyba na povodních** (`mae_povodne`) | 17,8 | **15,5** | 44,4 |
| VAL: chyba celkem | **6,9** | 7,5 | 12,7 |
| VAL: klid 2019–2020 | **6,1** | 6,9 | 10,4 |
| VAL: rychlé stoupání (598 h), bias | **28,5** (−12) | 31,5 (−21) | 77,4 |
| VAL: začátek vzestupu (269 h), bias | **28,1** (−21) | 35,4 (−31) | 72,3 |
| VAL: chyba vrcholu | 16,8 | **14,4** | 38,5 |
| **TEST 2021–2025: chyba na povodních** | **16,1** | 17,5 | 44,8 |
| TEST: chyba celkem | **7,0** | 7,3 | 12,0 |
| TEST: pod 300 cm | **6,6** | 6,8 | 10,2 |
| TEST: rychlé stoupání (859 h), bias | **24,3** (−19) | 28,8 (−24) | 75,2 |
| TEST: začátek vzestupu (532 h), bias | **27,0** (−25) | 32,0 (−31) | 70,0 |
| TEST: chyba vrcholu | 29,0 | **21,4** | 18,3 |

Validace a test trénované jako v týmu: na validaci model z 2006–2018 bez validačních povodní, na test model ze
všeho do konce 2020.

Po povodních:

| Povodeň (vrchol) | můj | tým | „jako teď“ |
|---|---|---|---|
| val 4/2006 (875 cm, tání) | 24,6 | **16,0** | |
| val 3/2009 (514) | **9,1** | 10,1 | |
| val 9/2010 (526) | **20,7** | 20,8 | |
| val 1/2011 (730, tání) | 16,7 | **14,9** | |
| test 12/2023 (624) | **11,9** | 15,0 | 44,5 |
| test 2/2024 (496) | **9,7** | 12,6 | 24,2 |
| test 9/2024 (649) | 26,8 | **25,0** | 65,8 |

Na validaci rozhodují 4 povodně a rozdíl +2,3 cm má směrodatnou chybu asi 2,2 cm, je tedy v rámci náhody; v CV
(18 povodní) je zlepšení −1,5 ± 0,4 cm. Test to potvrdil směrem CV.

## Začátek vzestupu

Tady je největší a nejstálejší zisk. Hodiny, kdy hladina za 24 h stoupne aspoň o 50 cm, ale posledních 6 h ještě
skoro nestoupala: chyba 28,1 místo 35,4 cm (val) a 27,0 místo 32,0 cm (test), podhodnocení se zmenšilo o 6–10 cm.
Důvod: stanice dál proti proudu (horní Ohře, horní Labe, Berounka) ukážou vlnu dřív, než dorazí do Prahy a Mělníka.
Pořád ale model na začátku vzestupu podhodnocuje o 21–25 cm: co teprve naprší, bez srážkové předpovědi nevidí.

## Poplachy (stupně povodňové aktivity 400 / 490 / 560 cm)

Předstih je nejvýš 24 h, propásnutá povodeň se do průměru počítá jako 0 (stejně jako `evaluate.varovani`).

| | povodní | můj: předstih / propásnuto / plané | tým | „jako teď“ |
|---|---|---|---|---|
| VAL 1. SPA (400) | 4 | **16,5 h** / 0 / **0** | 13,8 h / 0 / 2 | 0 h / 4 / 0 |
| VAL 2. SPA (490) | 4 | **16,8 h** / 0 / 0 | 15,5 h / 0 / 0 | 0 h / 4 / 0 |
| VAL 3. SPA (560) | 2 | **21,5 h** / 0 / 0 | 19,0 h / 0 / 0 | 0 h / 2 / 0 |
| TEST 1. SPA | 7 | **19,9 h** / 0 / 2 | 16,9 h / 0 / 2 | 0 h / 7 / 0 |
| TEST 2. SPA | 4 | **14,5 h** / 1 / 1 | 12,5 h / 1 / 1 | 0 h / 4 / 0 |
| TEST 3. SPA | 3 | **22,7 h** / 0 / 0 | 21,3 h / 0 / 0 | 0 h / 3 / 0 |

Na testu oba modely propásly 2. stupeň 13. 2. 2024 (vrchol 496 cm, práh přešel jen o 6 cm) a oba ohlásily planý
2. stupeň 5. 2. 2021 (skutečně 477 cm). Plané 1. stupně oba 9. 2. 2021 a v červenci 2021. Nový model tedy hlásí
dřív, ale ne častěji naplano.

## Co pomohlo a co ne (CV povodně, laťka v závorce)

| Změna | CV povodně | Výsledek |
|---|---|---|
| 18 nových stanic (`b_vse`) | 14,17 (15,64) | **ano**, hlavní zisk, −1,5 cm, vzestup −5 cm |
| odmocnina průtoku proti log / bez transformace | 14,17 / 16,82 / 24,22 | odmocnina zůstává |
| alpha z CV místo 1 | 15,63 (15,64) | nic, model je skoro bez regularizace |
| cíl „změna hladiny“ | 15,63 (15,64) | nic |
| změny za 1/3/6/12 h a zrychlení | 13,90 (14,17) | ne, −0,27 pod hranicí |
| husté zpoždění 0/1/2/3/6/9/12/18/24/36 h | 13,90 (14,17) | ne, −0,27 pod hranicí, ale stálé (5 z 5 bloků) |
| denní srážky po 11 povodích (1/2/3/5 dní) | 14,17 (14,17) | ne, denní úhrn je známý pozdě a co spadlo dřív, ukážou vodoměry |
| sníh, teplota, tání = sníh × kladná teplota | 14,45 (14,17) | ne |
| sezónnost sin/cos | 14,07 (14,17) | ne |
| interakce stav × změna | 14,32 (14,17) | ne |
| součty průtoků přes měrnou křivku Děčína | 14,95 (14,17) | ne |
| váhy 2 / 5 na stoupání | 14,21 / 14,91 (14,17) | ne, menší podhodnocení na stoupání, ale horší zbytek |
| dva režimy (klid / velká voda, stoupá / nestoupá) | 14,26–15,16 (14,17) | ne, přeučené |
| cíl průtok + měrná křivka | 29,4–40,0 | ne, chyby v průtoku dané velkou vodou jsou při malém průtoku ±15 cm |
| silnější regularizace, brzda jen na nové stanice | 14,17–15,72 | ne, CV vždy chce nejmenší alphu |
| aktualizace podle chyby předpovědi před 24 h | 14,08 (14,17) | ne, chyby se za den rozpadnou |
| kompaktní sada (tým + horní Ohře + horní Labe, 133 vstupů) | 14,41 (14,17) | ne, horší i na vzestupu (30,3) |

## Nálezy Codexu

Tři kontroly `codex exec -s read-only` s pravidly v promptu (nic neměnit, nečíst .env ani údaje Kaggle, nálezy se
souborem, řádkem a závažností), plné odpovědi v `codex/`, reakce v `NALEZY_CODEX.md`.

- **(a) po sestavení dat**: přímý únik z budoucnosti nenašel, posun denních srážek potvrdil. Dva střední nálezy:
  nejstarší zpoždění nezahrnovalo stáří denních dat a ffill, takže hraniční řádky splitu se nevyhazovaly. Opraveno.
- **(b) v polovině, protokol**: dva vysoké nálezy, oba oprávněné. Evidence validace nebyla úplná a rozbor validace
  ovlivnil směr hledání (doplněno a přiznáno). Kompaktní kandidát byl v CV horší než ponechaný model, proti
  vlastnímu pravidlu (vráceno k 30 stanicím). Dál alpha ze zaokrouhlených čísel, nejistota jen přes povodně
  místo bloků, chybějící otisky, neatomická značka testu. Vše opraveno.
- **(c) před testem**: kód připravený na test, čísla sedí, únik nenašel. Opraveno: kontrolní předpověď při ukládání
  modelu sahala na roky 2021–2025 (jedno číslo bez srovnání se skutečností), obsahové otisky souborů v testu.

## Napojení do aplikace (aplikaci jsem neměnil)

Model je objekt s `predict(X)` jako u `uloz_model.py`, jen má vlastních 224 vstupů a jen Děčín +24 h:

```
python ridge_dan/stahni_hydro.py && python ridge_dan/stahni_srazky.py && python ridge_dan/stahni_snih.py
python ridge_dan/data_ridge.py      # tabulka/labe_ridge.parquet
python ridge_dan/model_ridge.py     # modely/ridge_dan_decin_24.joblib (14 kB, trénink jako uloz_model.py)
```

V `app/predikce.py` by stačil malý adaptér (dnešní kód předává 98 týmových vstupů, to tomuto modelu nestačí):

```python
sys.path.insert(0, str(ROOT / "ridge_dan"))
import data_ridge  # noqa: E402

def predpoved_ridge_dan(cas):
    """Stav v Děčíně v čase cas + 24 h (cm)."""
    m = joblib.load(ROOT / "ridge_dan/modely/ridge_dan_decin_24.joblib")
    return float(m.predikuj(data_ridge.nacti().loc[:cas].tail(48)).iloc[-1])
```

`predikuj(T)` sám postaví vstupy z hodinové tabulky (stačí posledních 37 h) a vrací i předpovědi pro posledních
24 h, kde skutečnost ještě neznáme. Pro 12 a 36 h a pro Ústí by se musel natrénovat zvlášť (stejný kód,
`priznaky(T, cil, horizont, ...)`), to jsem nedělal.

## Slabiny a co dál

- Vrcholy velkých povodní: na validaci 2006 a 2011 i na testu 9/2024 je vrchol horší než u týmového modelu. Model je
  skoro bez regularizace a má velké protichůdné váhy podobných stanic, které se v neobvyklé povodni přestanou
  vyrušovat. Regularizace to v CV nespravila, protože v tréninku je jediná opravdu velká povodeň (6/2013).
- Bez srážkové předpovědi se začátek vzestupu dál nepozná dřív, než ho ukážou vodoměry. Hodinové srážky ČHMÚ jsou
  až od 2018, na tomto splitu se na nich učit nedá.
- Malé konzistentní zlepšení dávají husté zpoždění a změny za 1 h (−0,27 cm, 5 z 5 bloků); pod předem danou
  hranicí, proto nejsou ve finálním modelu.
- Výběr stanic s úplnou řadou 2006–2025 použil znalost dostupnosti i v testu; ověřil jsem, že žádná vodoměrná stanice
  kvůli dírám v testu nevypadla.

Otázka poroty a odpověď: „Proč máte na validaci horší číslo než týmový model, a přesto ho považujete za lepší?“ –
Protože validace má jen 4 povodně a rozdíl dělá jediná (tání 2006). Model jsme vybírali na 18 povodních
v tréninku, kde je lepší ve 4 z 5 bloků let, a jednorázový test 2021–2025 to potvrdil (16,1 proti 17,5 cm).
Lepší je hlavně na začátku vzestupu a varování hlásí o 1–3 h dřív bez víc planých poplachů.
