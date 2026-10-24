# Prezentace na 7 minut: kostra

Hotová prezentace na jednom místě (texty řečníků doslova, otázky poroty a grafy) je ve složce `prezentace/`, tady zůstává kostra a proč je takhle postavená.

Návrh Ondry (so 1:00, předěláno so 8:50 a 9:05). Vizuální jazyk, barvy, písma a stavba v Canvě zůstávají podle Honzova `docs/PREZENTACE.md`. Každý slajd odpovídá na jednu otázku, kterou by porota položila, nadpis je odpověď. Za postup a odbornost je 30 bodů z 50, proto nese prezentaci cesta vstupů (co model bere a co ne) a cesta modelů (čtyři modely a u každého, proč prohrál), hned za ní pointa, proč vyhrála přímka: voda v Děčíně je součet řek. Podrobnosti jsou v záložních slajdech na otázky. Živé demo neděláme: v 7 minutách by zabralo přes minutu a záviselo by na Wi-Fi a na tom, jestli ČHMÚ zrovna zveřejnil data. Aplikace je na slajdu 8 jako snímek z dnešního rána a web je otevřený v druhé kartě na otázky.

Zadání chce, aby v prezentaci zaznělo sedm věcí: 1 co řešíme, 2 data, 3 příprava dat, 4 vstupy, 5 model, 6 ověření, 7 limity.

| # | Čas | Otázka poroty | Nadpis (odpověď) | Co musí zaznít | Graf | Kdo | Bod |
|---|---|---|---|---|---|---|---|
| 1 | 0:00–0:45 | Co řešíte a pro koho? | Den předem víme, kam v Děčíně dosáhne voda | video Borise; hladina Děčín a Ústí za 12/24/36 h a varování před 2. a 3. stupněm; komise, hasiči, lidi u řeky | video, `01_mapa_decin.png`, velké 27 h | Tobias | 1 |
| 2 | 0:45–1:25 | Odkud se to dá poznat? | Z Prahy teče voda do Děčína 17 hodin, ze Sázavy 25 | tři větve a doba doběhu; archiv ČHMÚ, 12 stanic, 20 let; samotný balíček 44,6 cm jako „jako teď“; proto den dopředu, dál z řeky nevidí nikdo | `02a_mapa_stanic.png`, `02b_doba_dobehu.png` | Ondra | 2 |
| 3 | 1:25–2:15 | Co model bere? | Bereme jen řeku, počasí nepomohlo | 98 čísel z 12 stanic; srážky, sníh, teplota, vlhkost, tlak, vítr ani o 1 cm, co přijde do 36 h, už teče řekou; dvě pasti z budoucnosti (doplňování děr, čas denních srážek) | `03_co_model_bere.png` | Dan | 3, 4 |
| 4 | 2:15–3:25 | Jak jste vybrali model? | Čtyři modely, vyhrál nejjednodušší | laťka 44 cm; fyzikální 25 (pevná doba putování), LightGBM 23 (neumí výš, než viděl), síť 18 (přeučí se), regrese 17; vybráno před testem; úpravy nic přes 1 cm | `04_cesta_k_modelu.png` | Honza | 5 |
| 5 | 3:25–4:05 | Proč zrovna přímka? | Voda v Děčíně je součet řek | součet Vltavy, horního Labe a Ohře = vážený součet; Boris 198 + 80 + 89 + 116 + 96 − 2 = 577 cm, varoval; citát ze zadání | `05_soucet_rek.png` | Honza | 5 |
| 6 | 4:05–4:40 | Jak víte, že to funguje? | Ověřeno třikrát na povodních, které model neviděl | dělení v čase; výběr na 4 povodních; vícenásobná validace na 8; test jednou na konci | `06_jak_overujeme.png` | Ondra | 3, 6 |
| 7 | 4:40–5:25 | Funguje to na skutečné povodni? | Boris: 3. stupeň 27 hodin předem, chyba o 55 % menší | Boris z testu; 27 h; test 22,4 proti 50,2, vícenásobná validace 20,1 proti 45,2 | `07_boris_2024.png`, velká čísla | Ondra | 6 |
| 8 | 5:25–5:50 | Dá se to použít? | Každou hodinu nová předpověď z živých dat | Děčín dnes 84 cm, za 24 h 94, ČHMÚ 90 | `08_aplikace_dnes.png`, adresa a QR | Honza | 1 |
| 9 | 5:50–6:45 | Kde to selže? | Co umíme, co ne a co dál | 36 h skoro 2× horší; vyšší vrchol podhodnotí; zpoždění živých dat; dál srážky na 2–3 dny, dvoustupňové varování; závěrečná věta | karty, QR na repozitář | Dan, závěr Tobias | 7 |

Rezerva 15 s. Když se nestíhá: na slajdu 7 vynechat druhý odstavec a říct jen „na testu i ve vícenásobné validaci je chyba o 55 procent menší“.

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

Všechny grafy pro prezentaci jsou ve složce `docs/grafy/prezentace/` (kopie v `prezentace/grafy/`), pojmenované číslem slajdu (`07_boris_2024.png` patří na slajd 7). Všechny mají stejný formát, krátký nadpis, popisky os s jednotkami a nic navíc, takže slajd v Canvě může být jen graf přes celou plochu. Přehled je v `docs/grafy/prezentace/README.md`, kreslí je `python src/grafy_prezentace.py`. Na Macu chybí písmo Segoe UI, které mají Honzovy grafy, takže jsou v Helvetice; na Windows je stačí pustit znovu.

## Video na začátek

Nahrát z aplikace: `streamlit run app/app.py`, záložka s mapou, pohled Děčín, Animace povodně, Celá obrazovka, rychlost 4 h za s, povodeň Boris 9/2024 (13.–18. 9.). Na Macu Cmd+Shift+5, výřez mapy, 1920×1080, asi 25 s, bez zvuku. Hotová videa jsou `web/prezentace/video/boris_decin_720.mp4` a u Honzy `docs/grafy/video_povoden_*.mp4`.

## Co se změnilo proti první kostře

Slajd na vstupy a slajd na cestu k modelu jsou nové (Ondra so 8:50), místo grafu „všech 12 cest“ jsou dva grafy, které cestu rozdělují na vstupy a modely. V so 9:05 každý slajd dostal otázku poroty a nadpis jako odpověď, úvod a „pro koho“ jsou spojené do slajdu 1, pasti z budoucnosti jsou u vstupů (příprava dat), cesta modelů má u každého modelu větu, proč prohrál, a „předpověď je součet“ je hned za ní jako odpověď na „proč přímka“. Test a vícenásobná validace jsou spojené s Borisem do slajdu 7, jejich grafy a „proč data mimo balíček“ přešly do záložních Z8 až Z10. Živé demo je nahrazené snímkem. Oprava obsahu: neříkat „žádná cesta nebyla lepší“, některé byly lepší o desetiny (průměr regrese a sítě 16,9, tlak 17,0), správně je „nic nebylo lepší o víc než 1 cm“. Pozor i na starý nadpis „Dnes vidí Děčín 4 hodiny dopředu“: ČHMÚ pro Děčín oficiální předpověď vydává, 4 h platí jen pro data z balíčku.

## Otázky, které po 7 minutách přijdou

Odpovědi jsou v `prezentace/OTAZKY.md`, delší v `docs/POROZUMENI.md` a celá cesta modelu v `docs/CESTA_MODELU.md`. Nejpravděpodobnější: proč jen lineární regrese, proč ne srážky, nepřeučil se model, není výsledek náhoda, co znamená „bude jako teď“, proč jste brali data mimo balíček, proč neukazujete živé demo.
