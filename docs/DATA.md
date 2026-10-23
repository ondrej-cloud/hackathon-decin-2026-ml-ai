# Data

Co víme o datech. Kdo něco zjistí, doplní nebo opraví příslušnou sekci. U každého tvrzení, jestli je ověřené, nebo jen domněnka.

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
