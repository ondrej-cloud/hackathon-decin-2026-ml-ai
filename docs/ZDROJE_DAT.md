# Zdroje dat: co máme, co z toho používáme a proč

Stav pá 21:00. Kdo přidá nebo vyřadí data, upraví tabulku a zapíše důvod do `docs/DENIK.md`.

## Jednoduše: co model používá

Data z balíčku nezahazujeme. Děčín, Ústí a Louny v balíčku jsou stejné vodočty se stejnými čísly jako v archivu ČHMÚ (ověřeno hodinu po hodině za 2024–2025). Archiv jen sahá o 18 let dál a má i stanice proti proudu.

| Co | Kde se měří | Období | Odkud | K čemu |
|---|---|---|---|---|
| hladina (cm) | Děčín, Ústí | 2006–2025, každou hodinu | archiv ČHMÚ (stejné jako balíček, jen delší) | jak vysoko je voda teď a jestli stoupá |
| průtok (m³/s) | Děčín, Ústí, Louny | 2006–2025 | archiv ČHMÚ (stejné jako balíček, jen delší) | kolik vody teče teď v kraji |
| průtok (m³/s) | Mělník, Vraňany, Kostelec, Praha, Nymburk, Jizera, Beroun, Sázava, Přelouč | 2006–2025 | archiv ČHMÚ (v balíčku nejsou) | voda, která teprve přiteče, bez nich vidíme jen 4 h dopředu |
| prahy povodňových stupňů | Děčín, Ústí | | balíček (metadata) | kdy vyhlásit varování |
| polohy stanic | 12 stanic | | balíček (metadata) | mapa v aplikaci |
| srážky, sníh, teplota (pokus) | 25 meteostanic v povodí | 2006–2025, denně | archiv ČHMÚ | déšť, který v řece ještě není |

| Z balíčku nepoužíváme | Proč |
|---|---|
| 25 menších stanic na potocích v kraji | voda z nich doteče za pár hodin a je jí málo (2–13 %); Bílinu a Ploučnici jsme zkusili a model se zhoršil |
| teplota vody | na výšku hladiny nemá vliv |
| počasí z balíčku | jen 2,75 roku, model se učí na 20 letech; stejné druhy dat bereme z ČHMÚ za 20 let |
| rok 2026 | chybí za něj stanice proti proudu, bez nich model nefunguje |
| geodata obcí | pro výpočet nejsou potřeba, jen do mapy |

## Shrnutí

- **Z balíčku od pořadatelů** používáme přímo metadata stanic: stupně povodňové aktivity a polohy stanic pro mapu. Hladiny a průtoky Děčína, Ústí a Loun z balíčku slouží jako kontrola. Za 2024–2025 jsou na hodinu i na centimetr stejné jako archiv ČHMÚ, ze kterého trénujeme.
- **Trénujeme na archivu ČHMÚ** (stejný zdroj jako balíček): 12 stanic, 2006–2025, 175 320 hodin. Balíček má jen 2024–2026, jedinou povodeň a žádné stanice proti proudu. Na tom by nešlo ani předpovídat dál než pár hodin, ani nic ověřit.
- **Přidáváme meteorologii ČHMÚ** (denní srážky, sníh, teplota z 25 stanic v povodí). Zatím jako pokus, do modelu půjde jen tehdy, když pomůže.

## 1. Balíček od pořadatelů (`data/raw/labe/uloha_3/`, není v Gitu)

| Soubor | Co obsahuje | Rozsah | Používáme | Proč |
|---|---|---|---|---|
| `Hlavní dataset/hydrologie_komplet_ml.csv` (172 MB) | hladina, průtok, teplota vody; 28 stanic na 16 tocích v kraji | 1. 1. 2024 – 30. 9. 2026, do 2025 po hodinách, 2026 po 10 min; 2 355 985 řádků. Vyplněno: hladina 65 %, průtok 54 %, teplota vody 42 % | **jako kontrola**: Děčín, Ústí, Louny (3 z 28 stanic, 12,7 % řádků) | stejná data máme z archivu ČHMÚ za 20 let. Ověřeno shodné za 2024–2025 |
| ″ ostatních 25 stanic | přítoky a potoky v kraji (Bílina, Ploučnice, Kamenice, Ohře nad Louny, …) | ″ | **ne** | Bílinu a Ploučnici jsme zkusili (z archivu ČHMÚ), na validaci nepomohly. Doteče z nich za pár hodin a přidají 2–13 % vody. Malé řeky odložené na druhou zkoušku modelů |
| ″ teplota vody | | ″ | **ne** | s povodní nesouvisí |
| ″ rok 2026 (po 10 min) | | 1–9/2026 | **ne** | stanice proti proudu za 2026 nemáme. Možné využití v aplikaci jako „aktuální stav“ |
| `Hlavní dataset/metadata/meta1-20260930.json` | metadata hydrologických stanic: poloha, stupně povodňové aktivity | | **ano** | prahy 1.–3. stupně pro Děčín a Ústí (`src/data.py`), souřadnice 12 stanic pro mapu (`src/stanice_hydro.py` → `data/external/stanice_hydro.csv`) |
| `Hlavní dataset/dokumentace_hydrologie_CHMU.docx` | popis dat | | přečteno | |
| `Doplňkové datasety/meteorologie_hodinove_wide.csv` (84 MB) | hodinově teplota, vlhkost, tlak, srážky, vítr; 32 stanic | 1. 1. 2024 – 30. 9. 2026, 735 984 řádků | **ne** | jen 2,75 roku, na trénink na 20 letech nestačí. Místo toho denní archiv ČHMÚ od 1946 (níž) |
| `Geodata obcí/` (číselník 354 obcí, hranice geojson) | | | **zatím ne** | pro model nepotřebujeme, případně do mapy v aplikaci |

## 2. Data, která jsme přidali

| Zdroj | Co | Staženo | Používáme | Soubor |
|---|---|---|---|---|
| ČHMÚ, archiv hodinové hydrologie, https://opendata.chmi.cz/hydrology/historical/data/hourly/ | hladina a průtok | 26 stanic, 2002–2025, 276 MB (`src/stahni_chmu_hydro.py`) | **12 stanic, 2006–2025** (hladina Děčín a Ústí, průtok všech 12), 175 320 hodin. Bílina a Ploučnice jen v pokusu. Malé řeky na druhou zkoušku | `data/external/labe_hodinove.parquet` (4,8 MB, v Gitu), `src/data.py` |
| ČHMÚ, archiv denní meteorologie, https://opendata.chmi.cz/meteorology/climate/historical/data/daily/ | srážky, výška sněhu, teplota, index předchozích srážek (API30) | 25 stanic v povodí Vltavy, horního Labe a Ohře, 1,5 GB (`src/stahni_chmu_meteo.py`) | **pokus** (pá 21:00) | zatím ve scratchpadu, do Gitu po výsledku |
| ČHMÚ, metadata meteostanic | polohy a nadmořské výšky | `data/external/chmu_meteo_meta1-20261023.json` | výběr stanic v povodí | |
| ČHMÚ, hodinová meteorologie Praha-Ruzyně 5–7/2020 | hodinové srážky | 3 měsíce | jen kontrola, ke kterým 24 hodinám patří denní úhrn | |

**Pozor na čas u denních srážek** (ověřeno na Praze 5–7/2020): denní úhrn s časem „den D 06:00 UTC“ je déšť za **následujících** 24 h (do D+1 06:00), rozdíl proti hodinovým srážkám 0,02 mm. Kdo by ho použil od jeho časové značky, dal by modelu celý den deště z budoucnosti. Proto ho bereme až od D+1 07:00 UTC, průměrnou teplotu dne D taky.

## 3. Parametry, které modely dostávají

**Společné vstupy** (`src/features.py`), řádek = okamžik předpovědi t, jen hodnoty změřené do t:

| Parametr | Jednotka | Stanice | Kolik hodin zpátky | Sloupců |
|---|---|---|---|---|
| hladina | cm | Děčín, Ústí | 0, 1, 2, 3, 6, 12, 24 | 14 |
| průtok | m³/s | Děčín, Ústí, Louny, Mělník, Vraňany, Kostelec, Praha-Chuchle, Nymburk, Předměřice (Jizera), Beroun, Nespeky (Sázava), Přelouč | 0, 3, 6, 12, 18, 24, 36 | 84 |
| **celkem** | | | | **98** |

**Cíl:** hladina v cm v čase t + 12, 24 nebo 36 h, zvlášť Děčín a Ústí (6 modelů na každý přístup).

**Co si modely dopočítávají samy:**

| Model | Odvozené parametry |
|---|---|
| lineární regrese | odmocnina průtoků |
| neuronová síť | odmocnina průtoků, cíl jako změna hladiny |
| LightGBM | průtok, který dorazí za h hodin (posunutý o dobu doběhu každé stanice), jeho změna, roční období (sin a cos dne v roce), trend hladiny za 6 h, cíl jako změna hladiny |
| fyzikální | doby putování ze tří bran, měrná křivka průtok → hladina |

**V pokusu** (zatím ne ve společných vstupech): pro každou větev (Vltava, horní Labe, Ohře) srážky za poslední den a 3 dny, index předchozích srážek API30, výška sněhu, změna sněhu za 3 dny a průměrná teplota. Celkem 18 sloupců. Dan zkouší dobu doběhu podle průtoku.

## 4. Kolik dat je v které části (Děčín +24 h)

| Část | Období | Řádků (hodin) | Povodně nad 3. stupněm |
|---|---|---|---|
| train | 2006–2018 bez validačních povodní a 20 dní kolem nich | 107 662 | 8/2010, 6/2013 |
| val | povodně 4/2006, 3/2009, 9/2010, 1/2011 (16 dní před vrcholem až 5 po) a 2019–2020 | 19 264 | 4/2006, 1/2011 |
| test | 2021–2025, spustí se jednou na konci | 43 764 | 12/2023, 9/2024 |
| vynecháno | ochranné pásmo kolem hranic částí | 4 440 | |

Zbylých 190 hodin z 175 320 chybí kvůli vyřazené chybě v Děčíně (2/2006) a okrajům tabulky (prvních 36 h, posledních 24 h).
