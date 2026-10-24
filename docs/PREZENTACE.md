# Prezentace: HTML deck a vizuální jazyk

Hlavní prezentace je HTML deck na https://field-zero.netlify.app/prezentace/ (zdroj `web/prezentace/`: `index.html`, `deck.css`, `deck.js`, `reka.js`, grafy v `grafy/`, video ve `video/`). Pořadí, nadpisy a grafy odpovídají kostře `docs/PREZENTACE_7MIN.md`, texty řečníků jsou doslova z `prezentace/SLAJDY.md` a jsou i v poznámkách decku (klávesa N). Canva deck https://www.canva.com/d/xVAIR8am2CrRslj je jen starší záloha se starou kostrou.

Ovládání: šipky nebo mezerník = další krok (na úvodním slajdu první mezerník nebo klepnutí spustí video, druhý mezerník nebo konec videa ukáže nadpis a 27 h), N poznámky řečníka s časem, kroky a stopkami, F celá obrazovka, B černá, Home/End (End skočí na konec, šipkou zpět na záložní slajd). Stopky běží od prvního posunu jen v panelu poznámek (od 6:30 oranžové, od 7:00 červené); na ploše není počítadlo slajdů ani čas. Tisk (Ctrl+P, 1920 × 1080, všechny kroky odkryté, video jako poster) dává zálohu `docs/prezentace.pdf`, 19 stran.

Lokálně: `.venv\Scripts\python -m http.server 8607 -d web` a otevřít http://127.0.0.1:8607/prezentace/ (deck musí běžet přes server kvůli videu a písmům). PDF se tiskne Playwrightem (`deck.tisk()`, `emulate_media('print')`, `page.pdf` 1920 × 1080); po výměně videa nebo posteru `video_2013_poster.jpg` se musí přegenerovat, strana 1 bere poster místo videa.

## Slajdy a grafy

| # | Nadpis | Soubor v `grafy/` | Kroky |
|---|---|---|---|
| 1 | Den předem víme, kam v Děčíně dosáhne voda | video `video/povoden_2013_decin_1080.mp4` (poster `video_2013_poster.jpg`), nadpis nahoře, 27 h dole | 2 (video, nadpis a 27 h) |
| 2 | Jen z balíčku by to nešlo: bereme 20 let a 12 stanic proti proudu | mapa 7 hlavních stanic kreslená v SVG (`reka.js`, doba doběhu do Děčína u každé), `02b_proc_externi_data.png` | 1 (třetí sloupec) |
| 3 | Bereme jen řeku, počasí nepomohlo | mřížka 98 vstupů kreslená v HTML (`deck.js`), `03_co_model_bere.png` | 2 (graf, pasti) |
| 4 | Čtyři modely, vyhrál nejjednodušší | `04_cesta_k_modelu.png` | 2 (skupiny sloupců) |
| 5 | Voda v Děčíně je součet řek | součet kreslený v SVG (`deck.js`), citát ze zadání | 6 |
| 6 | Ověřeno třikrát na povodních, které model neviděl | `06_jak_overujeme.png` | 0 |
| 7 | Na všech povodních o polovinu menší chyba, Boris 27 hodin předem | `07a_boris_2024.png`, `07b_vicenasobna_validace.png` | 3 (27 h samo po 3 s, −55 % s grafem, řádek 2013) |
| 8 | Z předpovědi mapa: kam až voda dosáhne | `08_mapa_rozlivu.png` (povodeň 6/2013, vlevo předpověď 24 h předem 952 cm, vpravo skutečnost 1 072 cm), QR na web | 0 |
| 9 | Co neumíme a co dál | tři karty, závěrečná věta, QR na repozitář, jediná řádka se zdroji (licence map) | 1 |
| Z1–Z10 | otázky poroty | `Z1`–`Z6`, `mapbox3_decin.jpg` (Z7), `Z8_test_2021_2025.png`, `Z9_doba_dobehu.png`, `Z10_aplikace_dnes.png` | 0 |

Grafy jsou kopie z `docs/grafy/prezentace/` (kreslí je `python src/grafy_prezentace.py`, snímky mapy a aplikace dělá Playwright ze světlého webu). Horních 7 % každého PNG grafu (jeho nadpis) je v kartě oříznuto, nadpis má slajd.

Slajd 3 ukazuje, odkud je 98 vstupů (`src/features.py`): hladina v Děčíně a Ústí teď a před 1, 2, 3, 6, 12 a 24 h (2 × 7, tmavě modrá) a průtok 12 stanic teď a před 3, 6, 12, 18, 24 a 36 h (12 × 7, světle modrá), stanice seskupené po řekách (dolní Labe: Mělník, Ústí nad Labem, Děčín; Vltava: Vraňany, Praha-Chuchle, Beroun, Nespeky; horní Labe: Kostelec nad Labem, Předměřice, Nymburk, Přelouč; Ohře: Louny). Vpravo 14 veličin × 7 časů = 98 čísel, krokem graf a rámeček s pastmi.

Mapa na slajdu 2 má jen 7 hlavních stanic (Děčín, Ústí nad Labem, Mělník, Praha-Chuchle, Beroun, Nymburk, Louny) s dobou doběhu vody do Děčína z `docs/DATA.md` (Ústí 4 h, Nymburk 10 h, Mělník 13 h, Louny 16 h, Praha 17 h, Beroun 23 h); číslo 12 stanic zůstává v trojčíslí vedle.

## Zdroje

Na slajdech nejsou patičky se zdroji. Jediná výjimka kvůli licenci map je malá tlumená řádka na slajdu 9 (Děkujeme): „Mapy © Mapbox, © OpenStreetMap · terén ČÚZK · záplavová území DIBAVOD · data ČHMÚ“. Zdroje ostatních slajdů (validace, test, archiv ČHMÚ, mapové podklady) jsou v poznámkách řečníka (klávesa N, poslední odstavec „Zdroje:“).

## Vizuální jazyk

Jedna paleta pro všechny slajdy: pozadí #f5f5f7, bílé karty s rohem 22 px a jemným stínem, text #1d1d1f a tlumený #6e6e73, modrá #167c9c a světle modrá #9fcad8, oranžová #cb6c31 z grafů, stupně povodňové aktivity #f2c437 / #ef6c00 / #c62828. Písmo Inter (na Macu San Francisco). Nadpis 76 px na každém slajdu stejně, obsah začíná 44 px pod ním, velká čísla stejným stylem (číslo tučně, jednotka menší a tlumená). Jeden slajd = tvrzení v nadpisu + jedno číslo nebo graf + nejvýš jedna věta, bez odrážkových stěn, ikon a přechodů. Linie řeky Praha–Děčín vpravo nahoře (1748–1840 × 48–284 px) ukazuje na každém slajdu, kde v prezentaci jsme (tečka jde po proudu, na úvodu se objeví s nadpisem); nadpis do ní nezasahuje (nejvýš 1620 px, na úvodu 1320 px). Čeština s nezlomitelnými mezerami.

Plocha je 16:9 (1920 × 1080) a škáluje se na šířku i výšku okna; na MacBooku Air 13" (1470 × 956, 16:10) jsou nad a pod plochou pruhy v barvě pozadí, písmo zůstává čitelné (nejmenší text 17 px na ploše, tedy 13 px na Airu). Ověřeno Playwrightem na 1920 × 1080, 1470 × 956 a 1280 × 832 (DPR 2).

## Animace

V klidu, podle zásad fluidního rozhraní: přechod slajdů prolnutím a posunem 14 px (400 ms, ease-out), prvky slajdu nastupují po 70 ms (nadpis, pak bloky, karty na slajdu 9 postupně), čísla se načítají (20, 12, 175 320, 98, 27, −55, součet 198 → 577), mapa řek se kreslí tahem (stroke-dashoffset) a stanice naskakují po proudu, PNG grafy se odkrývají zleva (clip-path), mřížka 98 vstupů se vyplňuje políčko po políčku, součet řek na slajdu 5 roste po krocích, graf Borise se kreslí 3 s a pak samo naskočí 27 h. Při `prefers-reduced-motion` se všechno ukáže hned a bez posunů; v tisku nic animovaného nechybí.

Video na slajdu 1: `web/prezentace/video/povoden_2013_decin_1080.mp4` (24 s, bez zvuku), povodeň v červnu 2013 v Děčíně (největší v datech, vrchol 1 072 cm 6. 6. 2013; model `ridge_bez2013` ji při učení neviděl, na 24 h předpověděl vrchol 952 cm) v režimu porovnání: vlevo rozliv z předpovědi 24 h předem, vpravo skutečnost. Video se spustí až mezerníkem nebo klepnutím, do té doby je vidět poster. Věta přes video: „Tohle je Děčín v červnu 2013. Vlevo, co model předpověděl den předem, vpravo skutečnost.“ Po dohrání (nebo dalším mezerníkem) nadpis nahoře a 27 h s řádkem „3. stupeň v Děčíně hlášen 27 hodin předem“ dole. Starší video Borise (`boris_decin_1080.mp4`) a jeho poster už v decku nejsou.

## Otázky poroty

Odpovědi jsou v `prezentace/OTAZKY.md` (otázka, dvě tři věty, kdo odpovídá, který záložní slajd), delší v `docs/POROZUMENI.md` a celá cesta modelu v `docs/CESTA_MODELU.md`. Záložní slajdy Z1 až Z10 odpovídají rovnou grafem: proč lineární regrese, co je „bude jako teď“, proč ne srážky, jak moc se pleteme, jiná povodeň, váhy modelu, jestli je rozliv hydraulický model (není, výška terénu proti hladině ověřená proti úřední mapě), jak dopadl test, proč jen 36 hodin a jak vypadá aplikace dnes. Živé demo neděláme, web je otevřený v druhé kartě.
