# Grafy do prezentace na 7 minut

Číslo na začátku názvu je číslo slajdu v `docs/PREZENTACE_7MIN.md`, `Z` jsou záložní slajdy po poděkování. Všechny grafy mají stejný formát (16:9), krátký nadpis vlevo nahoře, popisky os s jednotkami a nic navíc. Kreslí je `python src/grafy_prezentace.py`, mapy jsou snímky z aplikace.

| Slajd | Soubor | Nadpis v grafu |
|---|---|---|
| 2 | `02_mapa_decin.png` | (snímek z aplikace) |
| 3 | `03a_mapa_stanic.png` | (snímek z aplikace) |
| 3 | `03b_proc_externi_data.png` | Jen s daty z balíčku by model nefungoval |
| 4 | `04_predpoved_je_soucet.png` | Předpověď je součet: kolik centimetrů přidá každá řeka |
| 5 | `05_co_jsme_zkouseli.png` | Žádná z 11 dalších cest nebyla lepší |
| 6 | `06_jak_overujeme.png` | Tři ověření, pokaždé na povodních, které model neviděl |
| 7 | `07_boris_2024.png` | Boris 2024: varování 27 hodin předem |
| 8 | `08a_test_2021_2025.png` | Test 2021–2025: o 55 % menší chyba |
| 8 | `08b_vicenasobna_validace.png` | Vícenásobná validace: o 55 % menší chyba na 8 povodních |
| záloha | `Z1_srovnani_ctyr_modelu.png` | Čtyři modely na validaci: vyhrál nejjednodušší |
| záloha | `Z2_co_je_jako_ted.png` | „Bude jako teď“ je vždycky o den pozadu |
| záloha | `Z3_proc_ne_srazky.png` | Když se blíží vrchol, už neprší |
| záloha | `Z4_jak_moc_se_pleteme.png` | Jak často je skutečnost v rozmezí od–do |
| záloha | `Z5_povoden_2011.png` | Povodeň 2011: varování 15 hodin předem |
| záloha | `Z6_vahy_modelu.png` | Váhy modelu pro Děčín za 24 h |

Jak číst graf 4: předpověď vydaná 14. 9. 2024 v 11:00 na 15. 9. v 11:00. Začíná průměrnou hladinou v Děčíně (198 cm), ke které model přičte, kolik centimetrů přidává voda, která právě teče v každé větvi povodí: Děčín a Ústí +80, Vltava (Praha, Vraňany, Beroun, Sázava) +89, horní Labe (Kostelec, Nymburk, Jizera, Přelouč) +116, Mělník +95, Ohře −2. Součet 577 cm je nad 3. stupněm (560 cm), proto model varoval. Skutečně bylo 551 cm a 3. stupeň voda překročila o 3 h později.

Jak číst graf Z6: každé políčko je váha jednoho vstupu, tedy o kolik centimetrů se změní předpověď, když je ta hodnota o obvyklý rozkmit (jednu směrodatnou odchylku) vyšší než průměr. Modrá předpověď zvedá, oranžová snižuje. Děčín teď +88 cm, Praha teď +49 cm. Oranžová políčka hned vedle modrých znamenají, že model odečítá starší hodnotu od nové, tedy počítá, jestli voda stoupá.

Čísla v ostatních grafech: chyba = průměrná chyba hladiny během povodní v cm, průměr Děčína a Ústí na 12, 24 a 36 h. Grafy 3, 5 a Z1 jsou z validace (4 povodně 2006–2011), 7 a 8a z testu 2021–2025, 8b z vícenásobné validace (8 povodní 2006–2020).
