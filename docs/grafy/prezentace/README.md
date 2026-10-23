# Grafy do prezentace na 7 minut

Číslo na začátku názvu je číslo slajdu v `docs/PREZENTACE_7MIN.md`, `Z` jsou záložní slajdy po poděkování. Grafy nemají nadpis, ten je na slajdu. Kreslí je `python src/grafy_prezentace.py`, mapy jsou snímky z aplikace.

| Slajd | Soubor | Nadpis na slajdu |
|---|---|---|
| 2 | `02_mapa_decin.png` | Den předem víte, kam až voda dosáhne |
| 3 | `03a_mapa_stanic.png`, `03b_proc_externi_data.png` | Co teče Prahou teď, je zítra v Děčíně |
| 4 | `04_vahy_modelu.png` | Model vidí jen to, co je v tu chvíli změřené |
| 5 | `05_co_jsme_zkouseli.png` | Zkusili jsme 12 cest, vyhrál nejjednodušší |
| 6 | `06_jak_overujeme.png` | Ověřujeme třikrát, pokaždé na povodních, které model neviděl |
| 7 | `07_boris_2024.png` | Boris: 3. stupeň hlášen 27 hodin předem |
| 8 | `08a_test_2021_2025.png`, `08b_vicenasobna_validace.png` | O 55 % menší chyba na testu i na všech 8 povodních |
| záloha | `Z1_srovnani_ctyr_modelu.png` | Jak dopadly jednotlivé modely |
| záloha | `Z2_co_je_jako_ted.png` | „Bude jako teď“ je vždycky o den pozadu |
| záloha | `Z3_proc_ne_srazky.png` | Když se blíží vrchol, už neprší |
| záloha | `Z4_jak_moc_se_pleteme.png` | Do rozmezí od–do se vejde 8 až 9 z 10 hodnot |
| záloha | `Z5_povoden_2011.png` | Povodeň 2011: 3. stupeň hlášen 15 hodin předem |

Čísla v grafech: chyba = průměrná chyba hladiny během povodní v cm, průměr Děčína a Ústí na 12, 24 a 36 h. Slajdy 3, 5 a Z1 jsou z validace (4 povodně 2006–2011), 7 a 8a z testu 2021–2025, 8b z vícenásobné validace (8 povodní 2006–2020).
