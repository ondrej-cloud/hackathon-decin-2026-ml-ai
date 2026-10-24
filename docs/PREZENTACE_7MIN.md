# Prezentace na 7 minut: kostra

Hotová prezentace na jednom místě (texty řečníků doslova, otázky poroty a grafy) je ve složce `prezentace/`, tady zůstává kostra a proč je takhle postavená.

Návrh Ondry (so 1:00, předěláno so 8:50). Vizuální jazyk, barvy, písma a stavba v Canvě zůstávají podle Honzova `docs/PREZENTACE.md`. Nezačínáme problémem, ale tím, co řešení umí: ukážeme rozliv a hned řekneme, komu pomáhá. Za postup a odbornost je 30 bodů z 50, proto mají vlastní slajd vstupy (co model bere a co ne a proč, i když by to člověku dávalo smysl) a cesta k modelu (od „bude jako teď“ přes čtyři modely k přímce). Živé demo neděláme: v 7 minutách by zabralo přes minutu a záviselo by na Wi-Fi a na tom, jestli ČHMÚ zrovna zveřejnil data. Aplikace je na slajdu 9 jako snímek z dnešního rána a web je otevřený v druhé kartě na otázky.

Zadání chce, aby v prezentaci zaznělo sedm věcí. U každého slajdu je číslo bodu, který pokrývá: 1 co řešíme, 2 data, 3 příprava dat, 4 vstupy, 5 model, 6 ověření, 7 limity.

| # | Čas | Nadpis (tvrzení) | Co se říká | Graf | Kdo | Bod |
|---|---|---|---|---|---|---|
| 1 | 0:00–0:25 | bez nadpisu | video: Děčín v září 2024, voda se rozlévá po hodinách. Bez mluvení, na konci jedna věta: „Tohle je Děčín v září 2024. Náš model to hlásil 27 hodin předem.“ | video z aplikace (návod níž) | Tobias | 1 |
| 2 | 0:25–0:50 | Den předem víte, kam až voda dosáhne | Hladina v Děčíně a Ústí za 12, 24 a 36 h, varování před 2. a 3. stupněm a rozliv v mapě. Pro povodňovou komisi, hasiče a lidi u řeky. Den navíc znamená odvézt auta, postavit pytle, vyklidit sklepy. | `02_mapa_decin.png`, velké číslo 27 h | Tobias | 1 |
| 3 | 0:50–1:30 | Co teče Prahou teď, je zítra v Děčíně | Hodinový archiv ČHMÚ, 12 stanic na Vltavě, horním Labi a Ohři, 2006–2025, stejný zdroj jako balíček, jen delší a s víc stanicemi. Voda doteče do Děčína z Ústí za 4 h, z Prahy za 17 h, ze Sázavy za 25 h, proto předpověď jde den dopředu; vodu, která ještě neteče žádnou stanicí, z měření nevidí nikdo. | `03a_mapa_stanic.png`, `03b_doba_dobehu.png` | Ondra | 2 |
| 4 | 1:30–2:20 | Co model bere a co ne | Bereme hladinu Děčína a Ústí a průtok na 12 stanicích, teď a až 36 h zpátky, 98 čísel, průtok pod odmocninou. Nebereme srážky, sníh, teplotu vzduchu, vlhkost, tlak ani vítr: všechno vyzkoušené, nic chybu nezmenšilo, co přijde do 36 h, už teče řekou. I dokonale známý déšť na 3 dny ubere jen 1 cm. | `04_co_model_bere.png` | Dan | 3, 4 |
| 5 | 2:20–3:10 | Od 44 cm k 17: jak jsme došli k přímce | Laťka „bude jako teď“ 44 cm, s daty jako v balíčku totéž, výsledek až se stanicemi proti proudu a 20 lety. Čtyři modely od jednoduchého po složitý se stejným pravidlem (zlepšení aspoň o 1 cm): fyzikální 25, LightGBM 23, síť 18, lineární regrese 17, vybraná před testem. Úpravy přímky nic nezlepšily o víc než 1 cm. Citát ze zadání: „Cílem není vytvořit co nejsložitější model.“ | `05_cesta_k_modelu.png` | Honza | 5 |
| 6 | 3:10–3:45 | Předpověď je součet: kolik centimetrů přidá každá řeka | Na Borisovi den předem: z průměrné hladiny 198 cm model přičetl Děčín a Ústí +80, Vltavu +89, horní Labe +116, Mělník +96, Ohři −2, vyšlo 577 cm, nad 3. stupněm, a varoval. Skutečně 551 cm, 3. stupeň o 3 h později. | `06_predpoved_je_soucet.png` | Honza | 5 |
| 7 | 3:45–4:20 | Ověřujeme třikrát, na povodních, které model neviděl | Dělení v čase, nikdy náhodně. Výběr na 4 vynechaných povodních, vícenásobná validace přes 8 povodní 2006–2020, test 2021–2025 jednou na konci. Dvě pasti z budoucnosti (doplňování děr, denní srážky) vyřazené. | `07_jak_overujeme.png` | Ondra | 3, 6 |
| 8 | 4:20–5:10 | Boris: 3. stupeň hlášen 27 h předem, chyba o 55 % menší | Předpověď vydaná den předem jde se skutečností, „bude jako teď“ je o den pozadu, vrchol 649 cm předpověděl na 611 cm. Test 22,4 cm proti 50,2, vícenásobná validace 20,1 proti 45,2, dvakrát o 55 % méně. | `08_boris_2024.png`, velká čísla 27 h a −55 % | Ondra | 6 |
| 9 | 5:10–5:40 | Aplikace: Děčín dnes a za 24 hodin | Snímek webu na Dnešku z dnešního rána: Děčín v 6:00 84 cm, za 24 h 94 cm, ČHMÚ 90 cm, rozmezí, data živě od ČHMÚ. Živé demo ne. | `09_aplikace_dnes.png`, adresa a QR | Honza | 1 |
| 10 | 5:40–6:40 | Co umíme, co ne a co dál | Na 36 h skoro dvakrát větší chyba, voda, která přijde, ještě neteče žádnou stanicí. Vyšší vrchol než v tréninku podhodnotí, data v provozu o 1 až 3 h zpožděná, s ČHMÚ se na starých povodních srovnat neumíme. Dál: předpověď srážek na 2–3 dny, dvoustupňové varování. Závěr: „Z otevřených dat zdarma: o povodni v Děčíně víte den předem, s modelem, který se vejde na jeden obrázek.“ | linie řeky končí v Děčíně, QR na repozitář | Dan, závěr Tobias | 7 |

Rezerva 20 s. Když se nestíhá: na slajdu 8 jen věta „na testu i ve vícenásobné validaci je chyba o 55 procent menší“.

## Záložní slajdy

Za poděkováním, ukážou se jen na otázku poroty. Odpovědět rovnou grafem působí odborně.

| # | Otázka | Graf |
|---|---|---|
| Z1 | Proč jen lineární regrese? | `Z1_srovnani_ctyr_modelu.png` |
| Z2 | Co znamená „bude jako teď“? | `Z2_co_je_jako_ted.png` |
| Z3 | Proč ne srážky? | `Z3_proc_ne_srazky.png` |
| Z4 | Jak moc se pletete? | `Z4_jak_moc_se_pleteme.png` |
| Z5 | Funguje to i na jiné povodni? | `Z5_povoden_2011.png` |
| Z6 | Podle čeho model rozhoduje? | `Z6_vahy_modelu.png` |
| Z7 | Je rozliv hydraulický model? | `mapbox3_decin.jpg` |
| Z8 | Jak dopadl test? | `Z8_test_2021_2025.png` |
| Z9 | Není výsledek jen náhoda výběru validace? | `Z9_vicenasobna_validace.png` |
| Z10 | Proč jste brali data mimo balíček? | `Z10_proc_externi_data.png` |

## Grafy

Všechny grafy pro prezentaci jsou ve složce `docs/grafy/prezentace/` (kopie v `prezentace/grafy/`), pojmenované číslem slajdu (`08_boris_2024.png` patří na slajd 8). Všechny mají stejný formát, krátký nadpis, popisky os s jednotkami a nic navíc, takže slajd v Canvě může být jen graf přes celou plochu. Přehled je v `docs/grafy/prezentace/README.md`, kreslí je `python src/grafy_prezentace.py`. Na Macu chybí písmo Segoe UI, které mají Honzovy grafy, takže jsou v Helvetice; na Windows je stačí pustit znovu.

## Video na začátek

Nahrát z aplikace: `streamlit run app/app.py`, záložka s mapou, pohled Děčín, Animace povodně, Celá obrazovka, rychlost 4 h za s, povodeň Boris 9/2024 (13.–18. 9.). Na Macu Cmd+Shift+5, výřez mapy, 1920×1080, asi 25 s, bez zvuku. Hotová videa jsou `web/prezentace/video/boris_decin_720.mp4` a u Honzy `docs/grafy/video_povoden_*.mp4`.

## Co se změnilo proti první kostře

Slajd na vstupy a slajd na cestu k modelu jsou nové (Ondra so 8:50), místo grafu „všech 12 cest“ jsou dva grafy, které cestu rozdělují na vstupy a modely. Test a vícenásobná validace jsou spojené s Borisem do slajdu 8, jejich grafy a „proč data mimo balíček“ přešly do záložních Z8 až Z10. Živé demo je nahrazené snímkem. Oprava obsahu: neříkat „žádná cesta nebyla lepší“, některé byly lepší o desetiny (průměr regrese a sítě 16,9, tlak 17,0), správně je „nic nebylo lepší o víc než 1 cm“. Pozor i na starý nadpis „Dnes vidí Děčín 4 hodiny dopředu“: ČHMÚ pro Děčín oficiální předpověď vydává, 4 h platí jen pro data z balíčku.

## Otázky, které po 7 minutách přijdou

Odpovědi jsou v `prezentace/OTAZKY.md`, delší v `docs/POROZUMENI.md` a celá cesta modelu v `docs/CESTA_MODELU.md`. Nejpravděpodobnější: proč jen lineární regrese, proč ne srážky, nepřeučil se model, není výsledek náhoda, co znamená „bude jako teď“, proč jste brali data mimo balíček, proč neukazujete živé demo.
