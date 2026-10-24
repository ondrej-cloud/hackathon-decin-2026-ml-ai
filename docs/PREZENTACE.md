# Prezentace: HTML deck a vizuální jazyk

Hlavní prezentace je HTML deck na https://field-zero.netlify.app/prezentace/ (zdroj `web/prezentace/`: `index.html`, `deck.css`, `deck.js`, `reka.js`, grafy v `grafy/`, video ve `video/`). Pořadí, nadpisy a grafy odpovídají kostře `docs/PREZENTACE_7MIN.md`, texty řečníků jsou doslova z `prezentace/SLAJDY.md` a jsou i v poznámkách decku (klávesa N). Canva deck https://www.canva.com/d/xVAIR8am2CrRslj je jen starší záloha se starou kostrou.

Ovládání: šipky nebo mezerník = další krok (na úvodním slajdu první mezerník nebo klepnutí spustí video, druhý mezerník nebo konec videa ukáže nadpis a 18 h), N poznámky řečníka s časem, kroky a stopkami, F celá obrazovka, B černá, Home/End (End skočí na konec, šipkou zpět na záložní slajd). Stopky běží od prvního posunu jen v panelu poznámek (od 6:30 oranžové, od 7:00 červené); na ploše není počítadlo slajdů ani čas. Snímek mapy na slajdu 8 a snímek aplikace na Z10 jsou odkazy (pilulka „Otevřít živou mapu“ / „Otevřít aplikaci“): klepnutím se v nové kartě otevře živá mapa `mapa.html?povoden=2013-06&cil=decin`, resp. web; deck v původní kartě běží dál. Tisk (Ctrl+P, 1920 × 1080, všechny kroky odkryté, video jako poster) dává zálohu `docs/prezentace.pdf`, 26 stran (9 hlavních + Z1–Z17).

Lokálně: `.venv\Scripts\python -m http.server 8622 -d web` a otevřít http://127.0.0.1:8622/prezentace/ (deck musí běžet přes server kvůli videu a písmům). PDF se tiskne Playwrightem (`deck.tisk()`, `emulate_media('print')`, `page.pdf` 1920 × 1080); po výměně videa nebo posteru `video_2013_poster.jpg` se musí přegenerovat, strana 1 bere poster místo videa.

## Slajdy a grafy

| # | Nadpis | Soubor v `grafy/` | Kroky |
|---|---|---|---|
| 1 | Den předem víme, kam v Děčíně dosáhne voda | video `video/povoden_2013_decin_1080.mp4` (poster `video_2013_poster.jpg`), nadpis nahoře, 18 h dole | 2 (video, nadpis a 18 h) |
| 2 | Jen z balíčku by to nešlo: bereme 20 let a 12 stanic proti proudu | mapa 7 hlavních stanic kreslená v SVG (`reka.js`, doba doběhu do Děčína u každé), `02b_proc_externi_data.png`, pod ním 20 · 12 · 175 320 | 1 (třetí sloupec) |
| 3 | Bereme jen řeku, počasí nepomohlo | mřížka 98 vstupů kreslená v HTML (`deck.js`), karta 98 čísel, `03_co_model_bere.png` | 1 (graf) |
| 4 | Čtyři modely, vyhrál nejjednodušší | `04_cesta_k_modelu.png` | 2 (skupiny sloupců) |
| 5 | Voda v Děčíně je součet řek | součet kreslený v SVG (`deck.js`), vpravo číslo 198 → 577 cm, citát ze zadání | 6 |
| 6 | Ověřeno třikrát na povodních, které model neviděl | `06_jak_overujeme.png` | 0 |
| 7 | Na všech povodních o polovinu menší chyba, Boris 27 hodin předem | `07a_boris_2024.png` a pod ním řádek 2013, vpravo karta 27 h a −55 %, `07b_vicenasobna_validace.png` | 3 (27 h samo po 3 s, −55 % s grafem, řádek 2013) |
| 8 | Z předpovědi mapa: kam až voda dosáhne | `08_mapa_rozlivu.png` (Děčín 6. 6. 2013 při 1 072 cm, rozliv z výšky terénu proti hladině), klikací, QR na web | 0 |
| 9 | Co neumíme a co dál | tři karty, závěrečná věta, QR na repozitář, jediná řádka se zdroji (licence map) | 1 |
| Z1–Z17 | otázky poroty | `Z1`–`Z6`, `mapbox3_decin.jpg` (Z7), `Z8_test_2021_2025.png`, `Z9_doba_dobehu.png`, `Z10_aplikace_dnes.png` (klikací), `Z11_primka_a_krivka.png`, `Z12_jeden_a_98_vstupu.png` | 0 |

V decku není žádné porovnání předpovědi se skutečností: video na slajdu 1 ukazuje rozliv ze změřené hladiny hodinu po hodině, snímek na slajdu 8 jeden rozliv při 1 072 cm. Grafy jsou kopie z `docs/grafy/prezentace/` (kreslí je `python src/grafy_prezentace.py`, snímky mapy a aplikace dělá Playwright ze světlého webu). Horních 7 % každého PNG grafu (jeho nadpis) je v kartě oříznuto, nadpis má slajd.

Slajd 3 ukazuje, odkud je 98 vstupů (`src/features.py`): hladina v Děčíně a Ústí teď a před 1, 2, 3, 6, 12 a 24 h (2 × 7, tmavě modrá) a průtok 12 stanic teď a před 3, 6, 12, 18, 24 a 36 h (12 × 7, světle modrá), stanice seskupené po řekách (dolní Labe: Mělník, Ústí nad Labem, Děčín; Vltava: Vraňany, Praha-Chuchle, Beroun, Nespeky; horní Labe: Kostelec nad Labem, Předměřice, Nymburk, Přelouč; Ohře: Louny). Vpravo karta 14 veličin × 7 časů = 98 čísel a krokem graf; dvě pasti z budoucnosti zazní jen v řeči.

Mapa na slajdu 2 má jen 7 hlavních stanic (Děčín, Ústí nad Labem, Mělník, Praha-Chuchle, Beroun, Nymburk, Louny) s dobou doběhu vody do Děčína z `docs/DATA.md` (Ústí 4 h, Nymburk 10 h, Mělník 13 h, Louny 16 h, Praha 17 h, Beroun 23 h); číslo 12 stanic zůstává v trojčíslí pod grafem.

## Zdroje

Na slajdech nejsou patičky se zdroji. Jediná výjimka kvůli licenci map je malá tlumená řádka na slajdu 9 (Děkujeme): „Mapy © Mapbox, © OpenStreetMap · terén ČÚZK · záplavová území DIBAVOD · data ČHMÚ“. Zdroje ostatních slajdů (validace, test, archiv ČHMÚ, mapové podklady) jsou v poznámkách řečníka (klávesa N, poslední odstavec „Zdroje:“).

## Vizuální jazyk

Jedna paleta pro všechny slajdy: pozadí #f5f5f7, bílé karty s rohem 22 px, jedním jemným stínem a vnitřním odsazením 28 px, text #1d1d1f a tlumený #6e6e73, modrá #167c9c a světle modrá #9fcad8, oranžová #cb6c31 z grafů, stupně povodňové aktivity #f2c437 / #ef6c00 / #c62828. Písmo Inter (na Macu San Francisco). Nadpis 76 px na každém slajdu stejně a má vyhrazený pruh na dva řádky (164 px), takže bílé karty začínají na všech slajdech na stejné rovině 272 px; karty v jednom řádku jsou stejně vysoké (grid `align-items: stretch`). Velká čísla stejným stylem (číslo tučně, jednotka menší a tlumená), popisky 22 až 26 px. Jeden slajd = tvrzení v nadpisu + jedno číslo nebo graf + nejvýš jedna věta, bez odrážkových stěn, ikon a přechodů. Linie řeky Praha–Děčín vpravo nahoře (1754–1840 × 40–260 px, nad rovinou karet) ukazuje na každém slajdu, kde v prezentaci jsme (tečka jde po proudu); nadpis do ní nezasahuje (nejvýš 1620 px, na úvodu 1320 px). Čeština s nezlomitelnými mezerami.

Slajd 1: přechody do barvy stránky jen na 22 % výšky nahoře a dole, mapa zůstává vidět; nadpis a 18 h mají lehký bílý nádech jen pod sebou (rozostřený obdélník), ne přes celou mapu. Slajd 5: SVG součtu vyplní kartu od kraje ke kraji (vnitřek 1108 × 696 px = viewBox 1 : 1), číslo 577 cm sedí na horní hraně karty, citát ze zadání je dole v pravém sloupci.

Plocha je 16:9 (1920 × 1080) a škáluje se na šířku i výšku okna; na MacBooku Air 13" (1470 × 956, 16:10) jsou nad a pod plochou pruhy v barvě pozadí, písmo zůstává čitelné (nejmenší text 17 px na ploše, tedy 13 px na Airu). Ověřeno Playwrightem (Chrome) na 1920 × 1080, 1470 × 956 a 1280 × 832 (DPR 2): všech 26 slajdů ve všech krocích bez chyb konzole, bez prvků mimo plochu a bez překryvu nadpisu s linií řeky; snímky `docs/grafy/deck8_1..9.png`, `deck8_5_karta.png`, `deck8_air_1.png`.

## Animace

V klidu, podle zásad fluidního rozhraní: přechod slajdů prolnutím a posunem 14 px (400 ms, ease-out), prvky slajdu nastupují po 70 ms (nadpis, pak karty; tři karty na slajdu 9 postupně), do 1,2 s od příchodu je všechno vidět. Linie řeky se na slajdu 1 s nadpisem nakreslí tahem od Prahy k Děčínu (stroke-dashoffset, 1,2 s) a na dalších slajdech tečka plynule putuje po linii na pozici slajdu (poloha po délce cesty, 700 ms, ease-out), ne rovně. Čísla se načítají (20, 12, 175 320, 98, 27, −55, součet 198 → 577), mapa řek se kreslí tahem a stanice naskakují po proudu (popisky vidět do 1,2 s), PNG grafy se odkrývají zleva (clip-path), mřížka 98 vstupů se vyplňuje políčko po políčku, součet řek na slajdu 5 roste po krocích, graf Borise se kreslí 3 s a pak samo naskočí 27 h. Při `prefers-reduced-motion` se všechno ukáže hned a bez posunů; v tisku nic animovaného nechybí.

Video na slajdu 1: `web/prezentace/video/povoden_2013_decin_1080.mp4` (24 s, bez zvuku), povodeň v červnu 2013 v Děčíně hodinu po hodině (největší v datech, vrchol 1 072 cm 6. 6. 2013; model ji při učení neviděl a 3. stupeň ohlásil 18 h předem), rozliv ze změřené hladiny, kamera se přibližuje k domům. Video se spustí až mezerníkem nebo klepnutím, do té doby je vidět poster. Věta přes video: „Tohle je Děčín v červnu 2013. Voda stoupá hodinu po hodině, až k domům.“ Po dohrání (nebo dalším mezerníkem) nadpis nahoře a 18 h s řádkem „3. stupeň v Děčíně hlášen 18 hodin předem“ dole, nad spodním pruhem videa. Starší video Borise (`boris_decin_1080.mp4`) a jeho poster už v decku nejsou.

## Otázky poroty

Odpovědi jsou v `prezentace/OTAZKY.md` (otázka, dvě tři věty, kdo odpovídá, který záložní slajd), delší v `docs/POROZUMENI.md` a celá cesta modelu v `docs/CESTA_MODELU.md`. Záložní slajdy Z1 až Z12 odpovídají rovnou grafem: proč lineární regrese, co je „bude jako teď“, proč ne srážky, jak moc se pleteme, jiná povodeň, váhy modelu (předpověď hladiny v Děčíně za 24 h), jestli je rozliv hydraulický model (není, výška terénu proti hladině ověřená proti úřední mapě), jak dopadl test, proč jen 36 hodin, jak vypadá aplikace dnes (snímek je odkaz na web), proč je předpověď křivka a jak je to s přímkou při 98 vstupech. Živé demo neděláme, web je otevřený v druhé kartě.
