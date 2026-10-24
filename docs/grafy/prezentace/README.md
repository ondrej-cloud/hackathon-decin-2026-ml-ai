# Grafy do prezentace na 7 minut

Číslo na začátku názvu je číslo slajdu v `docs/PREZENTACE_7MIN.md` (a v `prezentace/SLAJDY.md`), `Z` jsou záložní slajdy po poděkování. Všechny grafy mají stejný formát (16:9), krátký nadpis vlevo nahoře, popisky os s jednotkami a nic navíc. Kreslí je `python src/grafy_prezentace.py`, mapy a aplikace jsou snímky. Kopie všech grafů je v `prezentace/grafy/`.

| Slajd | Soubor | Nadpis v grafu |
|---|---|---|
| 2 | `02a_mapa_stanic.png` | (snímek z aplikace) |
| 2 | `02b_proc_externi_data.png` | Jen s daty z balíčku by model nefungoval |
| 3 | `03_co_model_bere.png` | Co se stane s chybou, když přidáme další vstup |
| 4 | `04_cesta_k_modelu.png` | Od 44 cm k 17 cm: cesta k finálnímu modelu |
| 5 | `05_soucet_rek.png` | Voda v Děčíně je součet řek |
| 6 | `06_jak_overujeme.png` | Tři ověření, pokaždé na povodních, které model neviděl |
| 7 | `07a_boris_2024.png` | Boris 2024: varování 27 hodin předem |
| 7 | `07b_vicenasobna_validace.png` | Vícenásobná validace: o 55 % menší chyba na 8 povodních |
| 8 | `08_mapa_rozlivu.png` | (snímek mapy z webu: povodeň 6/2013 na vrcholu, vlevo předpověď 24 h předem 952 cm, vpravo skutečnost 1 072 cm) |
| záloha | `Z1_srovnani_ctyr_modelu.png` | Čtyři modely na validaci: vyhrál nejjednodušší |
| záloha | `Z2_co_je_jako_ted.png` | „Bude jako teď“ je vždycky o den pozadu |
| záloha | `Z3_proc_ne_srazky.png` | Když se blíží vrchol, už neprší |
| záloha | `Z4_jak_moc_se_pleteme.png` | Jak často je skutečnost v rozmezí od–do |
| záloha | `Z5_povoden_2011.png` | Povodeň 2011: varování 15 hodin předem |
| záloha | `Z6_vahy_modelu.png` | Váhy modelu pro Děčín za 24 h |
| záloha | `Z8_test_2021_2025.png` | Test 2021–2025: o 55 % menší chyba |
| záloha | `Z9_doba_dobehu.png` | Za kolik hodin doteče voda do Děčína |
| záloha | `Z10_aplikace_dnes.png` | (snímek webu na Dnešku, bez nadpisu) |
| záloha | `Z11_primka_a_krivka.png` | Přímka je mezi vstupem a výsledkem, ne v čase (kreslí `src/graf_primka.py`) |
| záloha | `Z12_jeden_a_98_vstupu.png` | S 98 vstupy leží body těsně u přímky (kreslí `src/graf_primka.py`) |

Záložní slajd Z7 (rozliv) je snímek mapy `mapbox3_decin.jpg` z HTML decku, ne graf.

Jak číst graf Z9: posun s největší korelací změn průtoku za 6 h mezi stanicí a Děčínem, na trénovací části (`src/doba_dobehu.py`, `docs/DATA.md`). Ústí 4 h, Praha-Chuchle 17 h, Beroun 23 h, Nespeky na Sázavě 25 h. Ze vzdálených stanic je korelace slabá, doba je tam přibližná.

Jak číst graf 3: chyba na validaci, když k finálnímu modelu (17,1 cm) přidáme další vstup. Naměřené srážky 17,1, teplota vzduchu a sníh 17,3, voda ve sněhu 17,8, vlhkost 17,2, tlak 17,0, vítr 17,0, víc stanic proti proudu (horní Ohře) 17,4. Myšlenkový pokus „déšť na 3 dny dopředu přesně“ 16,1 se do modelu dát nesmí, je to horní mez. Naše pravidlo je zlepšení aspoň o 1 cm.

Jak číst graf 5: předpověď vydaná 14. 9. 2024 v 11:00 na 15. 9. v 11:00. Začíná průměrnou hladinou v Děčíně (198 cm), ke které model přičte, kolik centimetrů přidává voda, která právě teče v každé větvi povodí: Děčín a Ústí +80, Vltava (Praha, Vraňany, Beroun, Sázava) +89, horní Labe (Kostelec, Nymburk, Jizera, Přelouč) +116, Mělník +96, Ohře −2. Součet 577 cm je nad 3. stupněm (560 cm), proto model varoval. Skutečně bylo 551 cm a 3. stupeň voda překročila o 3 h později.

Jak číst graf Z6: každé políčko je váha jednoho vstupu, tedy o kolik centimetrů se změní předpověď, když je ta hodnota o obvyklý rozkmit (jednu směrodatnou odchylku) vyšší než průměr. Modrá předpověď zvedá, oranžová snižuje. Děčín teď +88 cm, Praha teď +49 cm. Oranžová políčka hned vedle modrých znamenají, že model odečítá starší hodnotu od nové, tedy počítá, jestli voda stoupá.

Čísla v ostatních grafech: chyba = průměrná chyba hladiny během povodní v cm, průměr Děčína a Ústí na 12, 24 a 36 h. Grafy 2b, 3, 4 a Z1 jsou z validace (4 povodně 2006–2011), 7a a Z8 z testu 2021–2025, 7b z vícenásobné validace (8 povodní 2006–2020).
