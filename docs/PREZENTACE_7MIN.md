# Prezentace na 7 minut: kostra

Návrh Ondry (so 1:00, upraveno so 1:15). Vizuální jazyk, barvy, písma a stavba v Canvě zůstávají podle Honzova `docs/PREZENTACE.md`, ten plán je ale na 15 minut a 16 slajdů. Tady je zkrácený na 7 minut a 10 slajdů. Nezačínáme problémem, ale tím, co řešení umí: ukážeme rozliv a hned řekneme, komu pomáhá. Metody (dělení v čase, vícenásobná validace, test jednou, co všechno jsme zkoušeli) mají vlastní slajdy, protože za postup a odbornost je 30 bodů z 50.

Zadání chce, aby v prezentaci zaznělo sedm věcí. U každého slajdu je číslo bodu, který pokrývá: 1 co řešíme, 2 data, 3 příprava dat, 4 vstupy, 5 model, 6 ověření, 7 limity.

| # | Čas | Nadpis (tvrzení) | Co se říká | Graf | Kdo | Bod |
|---|---|---|---|---|---|---|
| 1 | 0:00–0:25 | bez nadpisu | video: Děčín v září 2024, voda se rozlévá po hodinách. Bez mluvení, na konci jedna věta: „Tohle je Děčín v září 2024. Náš model to hlásil 27 hodin předem.“ | video z aplikace (návod níž) | Tobias | |
| 2 | 0:25–0:55 | Den předem víte, kam až voda dosáhne | Hladina v Děčíně a Ústí za 12, 24 a 36 h, varování před 2. a 3. stupněm a rozliv v mapě. Pro povodňovou komisi, hasiče a lidi u řeky. Den navíc znamená odvézt auta, postavit pytle, vyklidit sklepy. | `mapbox2_porovnani.png` přes celý slajd, velké číslo 27 h | Tobias | 1 |
| 3 | 0:55–1:40 | Co teče Prahou teď, je zítra v Děčíně | Hodinový archiv ČHMÚ, 12 stanic na Vltavě, horním Labi a Ohři, 2006–2025. Stejný zdroj jako balíček, jen delší a s víc stanicemi. S daty jen z balíčku (2 roky, stanice v kraji) by model byl stejně špatný jako „bude jako teď“ a propásl by polovinu povodní. | `mapbox_povodi.png`, `slajdy/kolik_dat.png` | Ondra | 2 |
| 4 | 1:40–2:15 | Model vidí jen to, co je v tu chvíli změřené | 98 čísel: hladina a průtok teď a za posledních 36 h. Lineární regrese je vážený součet. Hned po Děčíně má největší váhu Praha teď, její voda je v Děčíně za den. Záporné váhy počítají, jestli voda stoupá. | `slajdy/vahy_decin_24h.png` | Honza | 4, 5 |
| 5 | 2:15–2:55 | Zkusili jsme 12 cest, vyhrál nejjednodušší | Čtyři modely (lineární regrese, neuronová síť, LightGBM, fyzikální) a k tomu srážky, sníh, víc stanic, polynom, váhy na povodně, spojení všech malých zlepšení. Nic nebylo lepší. Proč přímka: voda v Děčíně je součet Vltavy, Labe a Ohře posunutých o dobu putování, a velké povodně jsou v datech jen dvě, na složitý model málo. | `slajdy/vse_co_jsme_zkouseli.png` | Dan | 5 |
| 6 | 2:55–3:30 | Ověřujeme třikrát, pokaždé na povodních, které model neviděl | Dělení v čase, nikdy náhodně. Model jsme vybrali na 4 vynechaných povodních, pak každou z 8 povodní 2006–2020 jednou vynechali (vícenásobná validace) a test 2021–2025 pustili jednou na konci. Data jsme zkontrolovali a našli dvě pasti, které braly informaci z budoucnosti (doplňování děr, denní srážky). | `slajdy/jak_overujeme.png` | Ondra | 3, 6 |
| 7 | 3:30–4:10 | Boris: 3. stupeň hlášen 27 hodin předem | Předpověď vydaná den předem jde se skutečností, „bude jako teď“ je vždycky o den pozadu. Vrchol 649 cm předpověděl na 611 cm. Model tuhle povodeň nikdy neviděl. | `slajdy/boris_2024.png` | Ondra | 6 |
| 8 | 4:10–4:40 | O 55 % menší chyba na testu i na všech 8 povodních | Test: 22,4 cm místo 50,2. Vícenásobná validace: 20,1 místo 45,2, na každé povodni o 34 až 66 % méně. Dvakrát stejné číslo, není to náhoda. | `slajdy/test_2021_2025.png`, `slajdy/vicenasobna_validace.png` | Ondra | 6 |
| 9 | 4:40–5:50 | Živé demo | Dnešek: živá data ČHMÚ a naše předpověď vedle oficiální. Mapa Děčína: předpověď × skutečnost u Borise. Nacvičené kliknutí po kliknutí, nejvýš 70 s. Když se zasekne, pustit video a jet dál. | aplikace, záložní video | Honza | |
| 10 | 5:50–7:00 | Co umíme, co ne a co dál | Na 36 h je chyba dvakrát větší, voda, která přijde, ještě neteče žádnou stanicí. Srážky na 12–36 h nepomáhají, voda už je v řekách. Vrcholy vyšší než kdy v tréninku podhodnotí, s oficiální předpovědí ČHMÚ se srovnat neumíme. Dál: předpověď srážek pro 2–3 dny, dvoustupňové varování. Závěr: „Z otevřených dat zdarma: o povodni v Děčíně den předem, s modelem, který se vejde na jeden obrázek.“ | linie řeky končí v Děčíně, QR na repozitář | Dan, závěr Tobias | 7 |

Když se nestíhá: slajd 8 jen jednou větou na slajdu 7 a demo zkrátit na mapu.

## Záložní slajdy za poděkováním

Jen když se porota zeptá. Odpovědět rovnou grafem působí odborně.

| Otázka | Graf |
|---|---|
| Jak dopadly jednotlivé modely? | `slajdy/srovnani_modelu.png` |
| Co přesně je „bude jako teď“? | `jako_ted_vysvetleni.png` |
| Proč nepoužíváte srážky? | `boris_dest_prutoky_decin.png` |
| Jak moc se pletete? | `slajdy/nejistota.png` |
| Jak dobré je to po stanicích a horizontech? | `test_chybovost.png` |
| A na 2011? | `slajdy/povoden_2011.png` |

`jako_ted_vysvetleni.png`, `boris_dest_prutoky_decin.png` a `test_chybovost.png` nejsou ve stylu slajdů, před použitím je překreslit.

## Grafy ve stylu slajdů

Všechny v `docs/grafy/slajdy/`. Honzových osm kreslí `python src/grafy_slajdy.py`, nové tři (`jak_overujeme.png`, `vicenasobna_validace.png`, `vse_co_jsme_zkouseli.png`) kreslí `python src/grafy_slajdy_overeni.py` se stejným stylem. Na Macu chybí písmo Segoe UI, takže jsou nakreslené v Helvetice. Pro stejné písmo jako ostatní je stačí pustit znovu na Windows.

## Video na začátek

Nahrát z aplikace: `streamlit run app/app.py`, záložka s mapou, pohled Děčín, Animace povodně, Celá obrazovka, rychlost 4 h za s, povodeň Boris 9/2024 (13.–18. 9.). Na Macu Cmd+Shift+5, výřez mapy, 1920×1080, asi 25 s, bez zvuku. Stejné video poslouží jako záloha dema.

## Co z Honzova plánu na 15 minut vypadlo

Titulní slajd (místo něj video), mřížka 98 vstupů (jedna věta na slajdu 4), samostatné slajdy o nejistotě a o rozlivu (ukážou se v demu) a slajd o srovnání čtyř modelů (je v grafu všech 12 cest). Pozor na Honzův nadpis „Dnes vidí Děčín 4 hodiny dopředu“: ČHMÚ pro Děčín oficiální předpověď vydává a aplikace ji ukazuje. Platí jen, že z dat balíčku jde vidět 4 h dopředu.

## Otázky, které po 7 minutách přijdou

Odpovědi jsou v `docs/POROZUMENI.md` (sekce Otázky, které čekáme od poroty) a celá cesta modelu v `docs/CESTA_MODELU.md`. Nejpravděpodobnější: proč jen lineární regrese, proč ne srážky, nepřeučil se model, není výsledek náhoda, co znamená „bude jako teď“, proč jste brali data mimo balíček.
