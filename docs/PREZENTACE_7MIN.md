# Prezentace na 7 minut: kostra

Návrh Ondry (so 1:00). Vizuální jazyk, barvy, písma a stavba v Canvě zůstávají podle Honzova `docs/PREZENTACE.md`, ten plán je ale na 15 minut a 16 slajdů. Tady je zkrácený na 7 minut a 9 slajdů. Nezačínáme problémem, ale tím, co řešení umí: ukážeme rozliv a hned řekneme, komu pomáhá.

Zadání chce, aby v prezentaci zaznělo sedm věcí. U každého slajdu je číslo bodu, který pokrývá: 1 co řešíme, 2 data, 3 příprava dat, 4 vstupy, 5 model, 6 ověření, 7 limity.

| # | Čas | Nadpis (tvrzení) | Co tam je a co se říká | Podklad | Kdo | Bod |
|---|---|---|---|---|---|---|
| 1 | 0:00–0:30 | bez nadpisu | video 25 s: Děčín v září 2024, voda se rozlévá po hodinách. Bez mluvení, na konci jedna věta: „Tohle je Děčín v září 2024. Náš model to hlásil 27 hodin předem.“ | video z aplikace (návod níž) | Tobias | |
| 2 | 0:30–1:10 | Den předem víte, kam až voda dosáhne | Co to dělá: hladina v Děčíně a Ústí za 12, 24 a 36 h, varování před 2. a 3. stupněm a rozliv v mapě. Komu: povodňová komise, hasiči, lidé u řeky. Den navíc znamená odvézt auta, postavit pytle, vyklidit sklepy. | `app_dnes.png` nebo `mapbox2_porovnani.png`, velké číslo 27 h | Tobias | 1 |
| 3 | 1:10–2:00 | Co teče Prahou teď, je zítra v Děčíně | Data: hodinový archiv ČHMÚ, 12 stanic na Vltavě, horním Labi a Ohři, 2006–2025, 175 320 hodin. Je to stejný zdroj jako balíček, jen delší a s víc stanicemi. Jen s balíčkem (2 roky, jen kraj) by byl model stejně špatný jako „bude jako teď“. Vstupy: hladina a průtok teď a za posledních 36 h, 98 čísel, jen to, co je v tu chvíli změřené. | `mapbox_povodi.png`, malé `slajdy/kolik_dat.png` | Ondra | 2, 4 |
| 4 | 2:00–2:40 | Testujeme na povodních, které model neviděl | Příprava: data jsme zkontrolovali (s balíčkem shodná na centimetr, chybu měření z 2/2006 vyřadili). Dělení v čase: učí se na 2006–2018, vybíráme na 4 vynechaných povodních, test 2021–2025 jsme pustili jednou na konci. Dvě pasti, které jsme našli: doplňování děr a denní srážky braly informaci z budoucnosti. | pruh času 2006–2025 (nakreslit v Canvě) | Ondra | 3 |
| 5 | 2:40–3:30 | Čtyři modely, vyhrál nejjednodušší | Zkusili jsme lineární regresi, neuronovou síť, LightGBM a fyzikální model. Chyba na povodních 17,1 / 17,8 / 23,1 / 24,8 cm, „jako teď“ 44,3. Proč přímka: voda v Děčíně je součet Vltavy, Labe a Ohře posunutých o dobu putování, a velkých povodní je na složitý model málo. Graf vah: největší váhu má Praha teď. | `slajdy/srovnani_modelu.png`, `slajdy/vahy_decin_24h.png` | Dan | 5 |
| 6 | 3:30–4:20 | Na povodních, které neviděl, o 55 % menší chyba | Test 2021–2025: 22,4 cm proti 50,2 u „jako teď“. Na 24 h je 7 předpovědí z 10 do ±20 cm. Před 3. stupněm varoval pokaždé, Borise 27 h předem. Vícenásobná validace přes 8 povodní dala stejné zlepšení (56 %), není to náhoda. | `test_chybovost.png` nebo `slajdy/test_2021_2025.png`, `krizova_validace.png` | Ondra | 6 |
| 7 | 4:20–5:40 | Živé demo | Dnešek: živá data ČHMÚ a naše předpověď vedle oficiální. Mapa Děčína: porovnání předpověď × skutečnost u Borise. Nacvičené kliknutí po kliknutí, nejvýš 80 s. Když se zasekne, pustit záložní video a jet dál. | aplikace, záložní video | Honza | |
| 8 | 5:40–6:30 | Co umíme a co ne | Na 36 h je chyba dvakrát větší, voda, která přijde, ještě neteče žádnou stanicí. Srážky jsme zkusili: na 12–36 h nepomáhají, voda už je v řekách; s předpovědí deště by šlo dešťové povodně předpovídat na 2–3 dny. Vrcholy vyšší než kdy v tréninku podhodnotí. V provozu chodí data se zpožděním. S oficiální předpovědí ČHMÚ se srovnat neumíme. | `boris_dest_prutoky_decin.png` | Dan | 7 |
| 9 | 6:30–7:00 | Co dál | Předpověď srážek pro 2–3 dny, dvoustupňové varování (předběžné podle horní meze), víc stanic proti proudu. Závěrečná věta: „Z otevřených dat zdarma: o povodni v Děčíně den předem, s modelem, který se vejde na jeden obrázek.“ | linie řeky končí v Děčíně, QR na repozitář | Tobias | |

Když se nestíhá: slajd 4 se spojí se slajdem 3 (jedna věta o dělení v čase) a demo se zkrátí na mapu.

## Co z Honzova plánu na 15 minut vypadlo

Titulní slajd (místo něj video), slajd o mřížce 98 vstupů (jedna věta na slajdu 3), samostatné slajdy o nejistotě, o tom, co jsme zkoušeli, a o rozlivu (nejistota a rozliv se ukážou v demu, pokusy jednou větou v limitech). Pozor na Honzův nadpis „Dnes vidí Děčín 4 hodiny dopředu“: ČHMÚ pro Děčín oficiální předpověď vydává a aplikace ji ukazuje. Platí jen, že z dat balíčku jde vidět 4 h dopředu.

## Video na začátek

Nahrát z aplikace na Macu: `streamlit run app/app.py`, záložka s mapou, pohled Děčín, Animace povodně, Celá obrazovka, rychlost 4 h za s, povodeň Boris 9/2024 (13.–18. 9.). Nahrávání přes Cmd+Shift+5, výřez mapy, 1920×1080, asi 25 s. Bez zvuku. Stejné video poslouží jako záloha dema.

## Otázky, které po 7 minutách přijdou

Odpovědi jsou v `docs/POROZUMENI.md` (sekce Otázky, které čekáme od poroty) a celá cesta modelu v `docs/CESTA_MODELU.md`. Nejpravděpodobnější: proč jen lineární regrese, proč ne srážky, nepřeučil se model, není výsledek náhoda, co znamená „bude jako teď“, proč jste brali data mimo balíček.
