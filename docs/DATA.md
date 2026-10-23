# Data

Co víme o datech. Kdo něco zjistí, doplní nebo opraví příslušnou sekci. U každého tvrzení, jestli je ověřené, nebo jen domněnka.

## Labe (vybraná úloha)

**Společná tabulka:** `data/external/labe_hodinove.parquet` (4,8 MB, v Gitu). Hodinově 2006–2025 (UTC), 175 320 hodin. Postaví ji `python src/data.py` ze surových dat ČHMÚ (`src/stahni_chmu_hydro.py`, asi 280 MB). Ostatní kód čte jen ji.

| Sloupce | Stanice |
|---|---|
| hladina (cm) i průtok (m³/s) | Děčín, Ústí nad Labem (cíle) |
| jen průtok | Louny (Ohře), Mělník, Vraňany (Vltava), Kostelec n. L., Praha-Chuchle, Nymburk, Předměřice (Jizera), Beroun (Berounka), Nespeky (Sázava), Přelouč |

Ověřeno:
- Začínáme rokem 2006, protože průtok v Kostelci, Mělníku a Nymburku za rok 2005 chybí celý.
- Chyba měření: 5.–7. 2. 2006 je v Děčíně hladina až 1 019 cm při průtoku kolem 120 m³/s, skoky o 1–3 m za hodinu. Vyřazeno (66 hodin chybí).
- Díry do 6 hodin doplněné lineárně. Jinak chybí jen tyhle 3 dny.
- Skoky v Ústí o 50–65 cm za hodinu (2007, 2014, 2019, 2023) jsou skutečné, průtok jde s nimi. Nechané.
- Hladina v Nymburce chybí z třetiny, proto u stanic proti proudu bereme jen průtok.
- Mezi lety 2016 a 2020 nepřekročilo Labe v Děčíně ani 1. stupeň povodňové aktivity, byla to suchá léta.
- Stupně povodňové aktivity (metadata ČHMÚ): Děčín 400 / 490 / 560 cm, Ústí 450 / 530 / 600 cm.

**Kontrola správnosti** (pá 19:45, ověřeno):
- Data ČHMÚ jsou za 2024–2025 na hodinu i na centimetr stejná jako balíček od pořadatelů (Děčín, Ústí, Louny, 17 544 hodin, rozdíl 0, bez časového posunu).
- Bilance vody sedí každý rok: Mělník = Vraňany + Kostelec (poměr 1,00), Ústí = 1,01–1,04 × (Mělník + Louny), Děčín = 1,04–1,08 × Ústí. Navíc přitékají menší přítoky (Bílina, Ploučnice). Žádná stanice nemá v některém roce průtok posunutý.
- Měrná křivka se nemění: při průtoku 250–300 m³/s je hladina v Děčíně každý rok 204–214 cm, v Ústí 234–242 cm. V Děčíně za 20 let klesla asi o 5 cm, nejspíš kvůli dnu řeky (domněnka).
- Časy sedí: voda z Ústí do Děčína dorazí každý rok za 4–5 h, z Prahy do Vraňan za 4–5 h. Vrchol povodně šel z Mělníka do Ústí za 17 h v letech 2006, 2009, 2013 i 2024. Při vyšší vodě se zpoždění Mělník → Ústí zkrátilo z 8–11 h (2006–2013) na 6–7 h (2021–2024). Posun času v datech to není, ten by byl skokový. Nejspíš jde o jezy (domněnka). Modely trénované do 2018 se proto na testu můžou o hodinu dvě splést v načasování.
- Odlehlé hodnoty: jednohodinové výkyvy průtoku, které se hned vrátí, má Vraňany 35 hodin za 20 let, Mělník 3, Přelouč 2, Nymburk 1. Nejspíš manipulace na jezech. Vliv na modely je zanedbatelný, nechané.
- Stejná hodnota déle než 3 dny: Sázava v zimě 8krát (nejdéle 18 dní v lednu 2009) a Louny 2krát, vždy při malém průtoku. Jsou to odhady ČHMÚ při ledu. Na povodně to vliv nemá, nechané.
- Žádné nulové ani záporné hodnoty.

**Povodně v Děčíně nad 3. stupněm:** 4/2006 (875 cm), 8/2010 (560), 1/2011 (730), 6/2013 (1 072), 12/2023 (624), 9/2024 (649).

**Doba doběhu do Děčína** (ověřeno, `src/doba_dobehu.py`): posun s největší korelací změn průtoku za 6 h, jen trénovací část. Ústí 4 h (korelace 0,93), Kostelec 10 h, Nymburk 10 h, Mělník 13 h, Vraňany 13 h, Louny 16 h, Praha-Chuchle 17 h, Předměřice a Přelouč 18 h, Beroun 23 h, Nespeky 25 h. Při velké vodě (Děčín nad 300 cm) vychází skoro stejně, jen korelace je silnější (Mělník 0,76 místo 0,51). Do Ústí je to o 3–4 h méně (Mělník 9 h, Praha 13 h). Z Lounů a vzdálených stanic je korelace slabá (0,2–0,3), doba je tam jen přibližná.

**Rozdělení** (`src/evaluate.py`, dělení v čase, ne náhodně):
- train: 2006–2018 bez validačních povodní a 20 dní kolem nich,
- val: povodně 4/2006, 3/2009, 9/2010 a 1/2011 (14 dní před vrcholem až 5 dní po něm) a klidné roky 2019–2020,
- test: 2021–2025, povodně 12/2023 a 9/2024,
- řádek, jehož vstupy (36 h zpět) nebo cíl (t + horizont) zasahují do jiné části, se vynechá.

Proč takhle: mezi 2016 a 2020 povodeň nebyla, validace na pozdějších letech by nic neřekla. V tréninku zůstává největší povodeň 2013, ve validaci jsou dvě velké a dvě menší.

## Ovzduší

Z doby, kdy jsme zvažovali úlohu Ovzduší. Týkají se jí všechny sekce níž.

## Soubory

Balíček úlohy Ovzduší je rozbalený v `data/raw/ovzdusi/uloha_2/` (není v Gitu).

| Soubor | Co obsahuje |
|---|---|
| `Hlavní dataset/ovzdusi_hodinove_wide.csv` | hodinová měření ČHMÚ, 13 stanic, 1. 1. 2024 – 30. 9. 2026 (UTC), 312 369 řádků (ověřeno) |
| `Hlavní dataset/metadata/metadata.json` | 98 stanic ovzduší ČR, poloha v `Localization.Lat/Lon` ve stupních, minutách a vteřinách |
| `Hlavní dataset/metadata/ValueType.csv`, `AirQualityIndex.csv` | kódy kvality a stupně indexu kvality 1A–3B |
| `Doplňkové datasety/meteorologie_hodinove_wide.csv` | hodinová meteorologie, 32 stanic, bez názvů a poloh |
| `Geodata obcí/obce_ustecky_kraj.geojson` | hranice 354 obcí (13 MB) |

Data přidaná z internetu (`data/external/`, v Gitu, protože jsou veřejná):

| Soubor | Co obsahuje | Zdroj |
|---|---|---|
| `chmu_meteo_meta1-20261023.json` | seznam meteostanic ČHMÚ s názvy, polohou a výškou | https://opendata.chmi.cz/meteorology/climate/now/metadata/ |
| `stanice_ovzdusi.csv` | 13 stanic ovzduší s polohou v desetinných stupních | z `metadata.json` |
| `parovani_ovzdusi_meteo.csv` | ke každé stanici ovzduší nejbližší meteostanice s teplotou i větrem | `src/parovani_stanic.py` |

Všech 32 meteostanic z balíčku jsme v seznamu ČHMÚ našli (ověřeno). Nejbližší meteostanice je od stanice ovzduší 0–6 km, jen Chomutov 11,7 km a Štětí 14,5 km. Pozor: nejbližší neznamená stejná výška. Ústí-město (v údolí) dostalo Kočkov (375 m).

## Sloupce a jejich význam

- Ovzduší: `station, dt, PM10, PM2_5, NO2, NOx, O3, SO2, CO` v µg/m³ a ke každé látce `<látka>_quality`.
- Meteorologie: `T` teplota, `H` vlhkost, `P` tlak, `SRA1H` srážky za hodinu, `Fprum` rychlost větru, `Dprum` směr větru. Jednotky dokumentace uvádí jen jako „pravděpodobné“.
- Pozor: u meteostanic ČHMÚ je `GEOGR1` zeměpisná délka a `GEOGR2` šířka, v hydrologických metadatech naopak.

Co která stanice měří (podíl hodin s platnou hodnotou):
- PM10 má 11 stanic, chybí Doksany a Sněžník.
- PM2,5 nemá Chomutov, Rudolice a Ústí-město.
- CO měří jen Ústí-Všebořická.
- Chomutov měří jen PM10.

## Jak data vypadají

- **Sezóna** (z reportu): PM10 je v zimě zhruba dvojnásobné proti létu.
- **Poměr PM2,5/PM10** (ověřeno, medián): zima 0,78, léto 0,54, Silvestr 1. 1. 2025 0–3 h 0,91, 30.–31. 3. 2024 0,39. Domněnka: vysoký poměr znamená spalování, nízký prach. Březen 2024 by tak mohl být saharský prach, ověřit.
- **Inverze** (ověřeno): když je na Milešovce (830 m) tepleji než v Ústí-Vaňově (150 m), je inverze. Nastává ve 14 % hodin, v zimě v 19 %.

  | | PM10 Ústí-město při inverzi | bez inverze |
  |---|---|---|
  | celý rok | 32,6 | 18,3 |
  | zima (XI–II) | 41,9 | 24,1 |

  Korelace rozdílu teplot s PM10 je v zimě 0,5. Sedí to s fyzikou: studený vzduch zůstane v údolí pod teplejší vrstvou a znečištění nemá kam odejít.
- **Stanice jdou spolu:** PM10 jednotlivých stanic jde odhadnout z ostatních s chybou kolem 5 µg/m³. Výjimkou je Lom s chybou 11, ten má zřejmě místní zdroj. Ověřeno lineárním modelem na validaci 7–12/2025.
- **Labe a ovzduší v Děčíně spolu nesouvisejí** (ověřeno na denních průměrech):
  - Teplota vody a NO₂ mají korelaci −0,69, ale po odečtení ročního období jen −0,10. Je to jen léto proti zimě.
  - Při povodni v září 2024 byl během deště vzduch čistý (PM10 kolem 5). Společnou příčinou je počasí.

## Chybějící, chybné a podivné hodnoty

- Platné hodnoty mají kvalitu 9 (ověřená) a 8 (operativní). Kvalita 10 a 11 je hodnota pod detekčním limitem, nejspíš taky platná (ověřit). 6 a 7 jsou chyby.
- Hodnoty −5000 až −5011 jsou technické kódy, ne koncentrace. Převést na chybějící hodnotu.
- Rok 2026 má jen operativní data (kvalita 8 a 6), roky 2024–2025 jsou ověřené.
- V asi 28 tisících hodin je PM2,5 vyšší než PM10 (z reportu, neověřeno). Jsou to různé měřicí metody.
- Odlehlá hodnota SO₂ 1 096 µg/m³ (z reportu).
- Čas je v UTC. Pro denní průběh převést na Europe/Prague.

## Rozdělení na train / val / test

Návrh (ještě neschválený): trénink 1/2024–6/2025, validace 7–12/2025, test 2026. Dělení v čase, nikdy náhodně.

## Úpravy dat

Zatím žádné.
