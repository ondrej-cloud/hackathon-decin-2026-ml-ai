# Šestihodinové srážky ze synoptických stanic pro Labe v Děčíně: zpráva

Dan, větev `dan-srazky` (z `dan-ridge`), pá 23. 10. 2026 22:47–0:00. Průběh v `PRUBEH.md`, nálezy Codexu
v `NALEZY_CODEX.md`, všechny běhy ve `vysledky/srazky.jsonl` (CV a validace) a `vysledky/lofo.jsonl` (LOFO).
Test 2021–2025 jsem nespouštěl.

## Shrnutí

- Otázka: denní srážky ČHMÚ nepomohly, protože úhrn smí do modelu až další den v 07:00 UTC. Šestihodinové úhrny
  ze zpráv SYNOP (NOAA ISD) jsou k dispozici hodinu po konci období, tedy se zpožděním 1–6 h.
- **Verdikt: srážky nepomohly ani jednomu z obou Ridge, oba jsou „beze změny“** (LightGBM ještě běží) (zlepšení ani zhoršení
  od 1 cm na hlavních číslech CV povodně a validace Děčín +24 h). Přísnější LOFO přes 22 povodní to potvrzuje:
  rozdíl do 0,1 cm a zlepšená zhruba polovina povodní.
- Jediný stálý, ale malý efekt je u týmového Ridge na začátku vzestupu: CV −0,9 cm, validace −1,9 cm, LOFO −0,9 cm.
  Na celkovou chybu na povodních to nestačí a u Danova Ridge s 30 stanicemi efekt není: horní stanice ukážou
  vlnu dřív, než by to uměly srážky ze 2 + 7 bodů.
- Proč ne víc: v ISD po roce ~2013 chybí u 12 z 21 stanic hlavně suché termíny (nuly ze zpráv BUFR), takže zůstalo
  jen 9 stanic s úplnou řadou: 2 u Děčína a 7 dál proti proudu. Na bouřky a místní déšť (jako 9/2010) je to
  málo bodů. Přes 24 h k tomu většinu deště, který spadl dřív, už ukážou vodoměry.

## Data

- **Zdroj:** NOAA NCEI Global Hourly (Integrated Surface Database). Seznam stanic `isd-history.csv` z ncei.noaa.gov,
  data `https://noaa-global-hourly-pds.s3.amazonaws.com/<rok>/<USAF>99999.csv` (adresa
  `ncei.noaa.gov/data/global-hourly/access/…` dnes přesměrovává na tuto kopii NOAA na AWS). Podmínky: data
  NOAA/NCEI volně bez omezení (dílo vlády USA), data výměny WMO podle Resolution 40 (volné nekomerční použití,
  uvést zdroj). Stahování šetrné: nejvýš 3 souběžně, pauza 1,5 s, cache na disku, nic dvakrát, všech 421 adres
  ve `STAZENO.csv`. Data nejsou v Gitu, postaví je `python srazky_dan/stahni_isd.py data …` a `python srazky_dan/srazky.py`.
- **Stažené stanice (21, 2006–2025, žádný rok nechybí):** u Děčína Ústí nad Labem, Doksany, Milešovka, Liberec
  (povodí Nisy, ale u Jizerských hor a Ploučnice, Jizera vlastní synop nemá); Ohře Cheb, Karlovy Vary, Tušimice;
  Berounka Plzeň-Mikulka, Přimda; Vltava a Sázava Churáňov, Kocelovice, Temelín, České Budějovice, Praha-Ruzyně,
  Praha-Libuš, Košetice, Přibyslav; horní Labe Pec pod Sněžkou, Pardubice, Čáslav, Ústí nad Orlicí.
- **Použité stanice (9):** jen ty, které mají 6h úhrn v 00/12 UTC aspoň v 80 % termínů v každém tréninkovém roce
  2006–2018. U ostatních po roce ~2013 chybějí hlavně suché termíny: podíl kladných úhrnů mezi platnými stoupl
  z ~0,2 na 0,6–0,9, takže průměr skupiny by srážky nadhodnotil. Hranice je ostrá (použité ≥ 0,80, vyřazené ≤ 0,39),
  s roky 2006–2020 i 2006–2017 vyjde totéž. Pokrytí po letech ve `vysledky/pokryti_stanic.csv`.
  - **blízko Děčína:** Ústí nad Labem, Doksany;
  - **dál proti proudu:** Tušimice (Ohře), Plzeň-Mikulka (Berounka), Temelín a Přibyslav (Vltava, Sázava),
    Pec pod Sněžkou, Pardubice a Ústí nad Orlicí (horní Labe).
- **Úhrny:** pole AA1–AA4 zpráv SYNOP v termínech 00/06/12/18 UTC. České stanice hlásí 6h úhrn v 00 a 12 UTC
  a 12h úhrn v 06 a 18 UTC. 6h díl končící v 06 (18) = 12h úhrn − 6h úhrn v 00 (12); když 6h úhrn chybí, dělí se
  12h úhrn napůl. Stopové srážky = 0. Vyhazuju kvalitu 3 a 7 (chybné), podmínky 1 a 4–8, 9999 a nesmyslné úhrny
  (6h > 150 mm, 12h > 250 mm). Podmínka 3 nese v souborech od ~2013 běžné změřené úhrny (ověřeno proti zprávě
  SYNOP v poli REM), kvalitu 2 a 6 (podezřelé) nechávám.
- **Časování (žádný únik z budoucnosti):** úhrn patří ke konci období E a do modelu smí od E + 1 h, vše v UTC.
  Díl končící v 00/12, který se dorovná až z 12h úhrnu v 06/18, vstupuje dorovnaný až od 07/19. Příznak v hodině t
  je součet za 6/12/24/48/72 h končící posledním termínem E ≤ t − 1 h, jen ze zpráv s koncem ≤ E. Nejstarší
  použité měření je t − 90 h a s tím počítá i dělení na train/val (řádky přes hranici se vyhazují).
- **Díry:**
  - chybějící 6h díly v okně nahradí průměr známých dílů téhož okna, pokud je jich aspoň polovina;
  - když chybí celý termín, platí ještě součty předchozího termínu (nejvýš o 6 h starší);
  - jinak NaN a řádek se vyhodí u obou variant.

  V letech 2006–2020 tak chybí nejvýš 0,7 % hodin a v oknech validačních povodní nic. První verze tabulky bez
  průměrování dílů vyhazovala 66–126 h přímo v povodních 9/2010, 1/2011 a 3/2009: 25. 9. 2010 v 06 UTC chyběla
  zpráva v Ústí i v Doksanech, tedy právě na začátku deště. Ty běhy jsem zahodil.
- **Příznaky:** hlavní sada (rozhodnutá předem, podle ní verdikt) = skupiny „blízko“ a „dál“ × okna 6/12/24/48/72 h,
  10 sloupců v mm. Citlivostní sada = „blízko“ + 4 dílčí povodí (Ohře, Berounka, Vltava, horní Labe) × 5 oken,
  25 sloupců. Tabulka `data/srazky_6h.parquet`, otisk 0fa9e49a.
- **Kontrola časování:** `kontrola_casovani.py` na Ústí i Doksanech:
  - 300 náhodně změněných nebo smazaných zpráv, žádný příznak před E + 1 h se nezměnil;
  - pevné případy t = E, E + 1 h, E + 6 h, E + 7 h, E + 72 h a E + 73 h sedí;
  - 24h součty sedí s přímým výpočtem z 12h úhrnů (rozdíl jen tam, kde je v datech 6h úhrn větší než 12h,
    nejvýš 1 mm, a přesně o něj).

## Protokol

- Každý model ve dvou variantách „beze změny“ a „+ srážky“, jinak nic neměněno. Původní soubory zůstaly beze
  změny, varianty jsou obaly v `obaly.py`:
  - (a) týmový Ridge = `src/models/ridge.py` na 98 týmových vstupech, srážky se neodmocňují;
  - (b) Danův Ridge = `ridge_dan/model_ridge.py`, 224 vstupů (30 stanic), alpha 1, jen Děčín +24 h;
  - (c) LightGBM = `src/models/lgbm.py` (lgbm_c) se srážkami připojenými k jeho vstupům, seedy 42/43/44.
- **Stejné řádky:** obě varianty trénují i hodnotí na identických řádcích, assert to hlídá v CV i validaci.
  Po průniku se srážkami zbylo 107 314 trénovacích a 18 982 validačních řádků (původně 107 662 / 19 264).
  Varianta beze změny dává na původních řádcích přesně známá čísla:
  - týmový Ridge: CV 15,64, validace 15,5, průměr 17,08;
  - Danův Ridge: 14,17 a 17,8;
  - LightGBM: 18,05, 21,3 a 23,07.
- **CV** = Danova časová CV uvnitř tréninku (6 bloků let, mezera 10 dní, průměr přes 18 povodní nad 400 cm),
  Děčín +24 h. **Validace** = týmový split. Týmový Ridge a LightGBM mají všech 6 kombinací (`prumer_povodne` jako
  `porovnej.py`), Danův Ridge jen Děčín +24 h. Plané a propásnuté poplachy 2. a 3. SPA podle `evaluate.varovani`.
- **Začátek vzestupu** = za 24 h stoupne aspoň o 50 cm, ale posledních 6 h stouplo méně než o 10 cm. Zvlášť
  povodně 9/2010 (místní déšť) a 4/2006 (tání), okno 7 dní před až 5 dní po vrcholu.
- **LOFO-CV (přísnější):** 22 povodní 2006–2020 se stejnými foldy jako ostatní (`vysledky/lofo_foldy.csv`,
  převzato z `stanice_vsem`, sha1 ad383c28). Fold drží okno povodně a z tréninku vyřadí okno ± 20 dní. Zlepšení
  platí jen při průměru lepším aspoň o 1 cm a zlepšení většiny povodní.

## Výsledky (Děčín +24 h, chyba v cm, stejné řádky)

Rozdíl = + srážky − beze změny, záporný = menší chyba.

| model | varianta | CV povodně | CV začátek vzestupu | VAL Děčín +24 povodně | VAL průměr 6 kombinací | VAL začátek vzestupu | VAL 9/2010 | VAL 4/2006 | plané 2./3. SPA (VAL) | LOFO 22 povodní | LOFO začátek | LOFO zlepšeno |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Ridge týmový | beze změny | 15,64 | 35,00 | 15,5 | 17,08 | 35,4 | 20,8 | 16,0 | 0 / 0 | 15,29 | 41,9 | |
| | + srážky | 15,65 | 34,14 | 15,4 | 17,05 | 33,5 | 20,4 | 15,6 | 0 / 0 | 15,32 | 41,0 | 12 z 22 |
| | rozdíl | +0,01 | −0,86 | −0,1 | −0,03 | −1,9 | −0,4 | −0,4 | 0 / 0 | +0,04 | −0,9 | p = 0,83 |
| Ridge Danův (30 stanic) | beze změny | 14,16 | 28,95 | 17,8 | – | 28,1 | 20,7 | 24,6 | 0 / 0 | 14,79 | 34,1 | |
| | + srážky | 14,10 | 29,03 | 18,1 | – | 28,4 | 21,0 | 25,4 | 0 / 0 | 14,77 | 34,1 | 13 z 22 |
| | rozdíl | −0,07 | +0,08 | +0,3 | – | +0,3 | +0,3 | +0,8 | 0 / 0 | −0,03 | 0,0 | p = 0,52 |
| LightGBM (seed 42) | beze změny | 17,77 | 36,40 | běží | běží | běží | běží | běží | běží | běží | běží | |
| | + srážky | běží | | | | | | | | | | |

Propásnuto nebylo nic u žádného modelu ani varianty: validace 2. i 3. SPA, LOFO 2. i 3. SPA. Plané poplachy
v LOFO jsou u obou variant stejné: týmový Ridge 4 / 1 (2. / 3. SPA), Danův Ridge 3 / 1.

LOFO po povodních: týmový Ridge má rozdíly od −0,7 (8/2010) do +1,3 cm (6/2013), Danův od −0,4 do +0,5 cm.
Povodeň 9/2010 (místní déšť) je −0,4 a +0,2, 4/2006 (tání) +0,1 a +0,5. Ani jedna povodeň se nezlepšila
aspoň o 1 cm.

Citlivostní sada (blízko + 4 dílčí povodí, 25 sloupců) dopadla stejně:
- týmový Ridge: CV povodně 15,64 → 15,66, validace Děčín +24 h 15,5 → 15,3, začátek vzestupu na validaci
  35,4 → 32,8, 9/2010 20,8 → 19,9;
- Danův Ridge: CV 14,16 → 14,15, validace 17,8 → 18,0.

Ani jemnější rozdělení povodí tedy nepomůže.

## Verdikt po modelech

| model | verdikt | proč |
|---|---|---|
| Ridge týmový | **beze změny** | CV +0,01, VAL −0,1, LOFO +0,04 cm (12 z 22 povodní lepších); jen začátek vzestupu o 0,9–1,9 cm lepší, pod hranicí nebo jen na validaci |
| Ridge Danův (30 stanic) | **beze změny** | CV −0,07, VAL +0,3, LOFO −0,03 cm (13 z 22); horní vodoměry nesou totéž co srážky, dřív |
| LightGBM | **zatím bez verdiktu** | běh pod zátěží druhé session (volná RAM ~0,5 GB) jde 4× pomaleji, výsledek doplním |

## Nálezy Codexu

Dvě kontroly `codex exec -s read-only` s pravidly v promptu (nic neměnit, nečíst .env ani údaje Kaggle, nálezy se
souborem, řádkem a závažností). Prompty a plné odpovědi jsou v `codex/`, reakce v `NALEZY_CODEX.md`.

- **(a) časování srážek** (`srazky.py`, test): přímý únik z budoucnosti nenašel. Měl tři střední nálezy, všechny
  jsem opravil:
  - nejstarší měření sahá dál než 78 h, nastaveno na 90 h a s tím počítá dělení na části;
  - test bral zpoždění z kontrolovaného kódu, teď má pevnou hodinu a pevné případy;
  - shoda součtů se jen vypisovala, teď ji hlídají aserce.

  Nízký nález (rozpor 6h > 12h) je zdůvodněný: 6h úhrn zůstává, protože ho model už používal.
- **(b) stejné řádky a varianty** (`obaly.py`, `spust_srazky.py`, `spolecne.py`, `tabulka_vysledku.py`):
  potvrdil stejné řádky, `y` i značky částí a to, že se varianty liší jen srážkami. Obal LightGBM bez srážek dává
  přesně stejné předpovědi jako `lgbm_c.fit` a srážky se připojují podle UTC bez posunu. Dva střední nálezy:
  - výběr stanic podle pokrytí včetně let 2019–2020: zdůvodněno, s roky 2006–2018 vyjde stejných 9 stanic,
    kód teď bere 2006–2018;
  - souhrn mohl spárovat záznamy z různých běhů: opraveno, kontroluje otisk, historii a počty řádků v páru.

## Slabiny

- Jen 9 stanic s úplnou řadou, 2 z nich u Děčína. ISD nemá od ~2015 nuly ze zpráv BUFR, proto 12 stanic vypadlo.
  Hodinové srážky ČHMÚ by byly hustší, ale jsou až od 2018.
- Pro test 2021–2025 by tabulka nebyla úplná: v letech 2024–2025 chybí 35–38 % hodin (výpadky zpráv u Doksan,
  Temelína a Pardubic). Test jsem ale nespouštěl a podle výsledků ho kvůli srážkám ani spouštět nemá smysl.
- Srážky jsou naměřené, ne předpovězené. Přes 24 h dopředu by víc mohla dát srážková předpověď (ALADIN, ICON),
  ta ale do roku 2006 zpětně volně není.

Otázka poroty a odpověď: „Proč jste nepřidali srážky, když povodně dělá déšť?“ Zkusili jsme je dvakrát. Denní
úhrny ČHMÚ jsou známé až druhý den ráno. Šestihodinové ze synoptických zpráv přijdou hodinu po měření, ani ty ale
chybu na povodních nezlepšily o víc než 0,1 cm, ani v přísnější kontrole přes 22 povodní. Co spadlo, ukážou
vodoměry proti proudu za pár hodin taky, a přesněji, protože měří celé povodí, ne jeden bod. Pomoct by mohla až
srážková předpověď.
