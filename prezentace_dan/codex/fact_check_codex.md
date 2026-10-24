**1. NESOULADY**

Všechny kontrolované soubory jsou v `prezentace_dan/`. Danovy zdroje níže označuji větví; četl jsem je přes `git show origin/<větev>:<soubor>`. Část nepřesností je převzatá už ze zdrojové dokumentace.

| Soubor:řádek | Tvrzení v podkladu | Co říká zdroj — přesné číslo / citace | Zdroj (soubor, sekce) | Návrh opravy |
|---|---|---|---|---|
| PREHLED_POKUSU.md:16; OTAZKY_POROTY.md:98; TAHAK_DAN.md:41 | Síť: trénink **5**, validace **22 cm**, bez vymezení metriky | Dokumentace dvojici vztahuje k **D24**, zatímco **26,0** je průměr šesti kombinací. Novější uložený běh má D24 `mae_povodne: 21.2`, `mae_nad_1spa: 23.5`. | `docs/POKUSY.md`, pá 20:00, MLP; `results/2026-10-23_195410_mlp_v1.json`, D24 | Oddělit průměr šesti kombinací od D24; dvojici 5/22 označit jako starší rozbor, případně vypustit. |
| PREHLED_POKUSU.md:24; OTAZKY_POROTY.md:14 | „12 z 24 propásnutých povodní“ | „**24 znamená 4 povodně × 2 cíle × 3 horizonty, nikoli 24 různých povodní.**“ | `docs/POKUSY.md`, pá 20:44, kolik let dat | „12 z 24 případů varování.“ |
| OTAZKY_POROTY.md:14 | Se skutečným balíčkem by chyba byla **44,6 cm** | „**44,6 cm patří krajským stanicím v letech 2017–2018, ne skutečnému balíčku 2024–2026**.“ | `docs/POKUSY.md`, pá 20:46, sjednocení učicí křivky | Uvést, že jde o napodobení délky a rozsahu balíčku na jiných letech. |
| PREHLED_POKUSU.md:34 | Horní Ohře a Zbraslav: vícenásobná validace **19,7** | „s horní Ohří **19,7 ± 8,2**, i se Zbraslaví **19,9 ± 8,1 cm**“ | `docs/POKUSY.md`, so 0:19, další stanice | Rozlišit obě varianty. |
| PREHLED_POKUSU.md:39 | **18 nových stanic u všech modelů** | Fyzika používá „**+ 8 stanic**“; „**Nejde 10 z 18**“. | `dan-ridge:ridge_dan/STANICE_VSEM.md`, Jak se srovnávalo, Tabulka | Doplnit výjimku: fyzika přidala osm stanic. |
| PREHLED_POKUSU.md:50 | Přísným LOFO prošla **jen G3** | „**Děčín +36 h: pravidlo splní samotný Ridge s 30 stanicemi**“, **26,39 → 23,96**, **−2,43 cm**, **17 z 22**. | `dan-ridge:ridge_dan/ZLEPSENI.md`, Verdikt | „Na D24 prošla G3; na D36 také Ridge 30.“ |
| PREHLED_POKUSU.md:49–50; TAHAK_DAN.md:51–52 | Žádný proveditelný pokus nezlepšil validaci alespoň o centimetr | Fyzika s dalšími stanicemi: **24,75 → 23,40**. LightGBM se srážkami: průměr šesti kombinací **23,03 → 21,85**. | `STANICE_VSEM.md`, Tabulka; `dan-srazky:srazky_dan/ZPRAVA_SRAZKY.md`, Výsledky | Zúžit: žádný uvedený provozně použitelný kandidát nepřekonal **finální Ridge** na hlavní validaci alespoň o centimetr. |
| PREHLED_POKUSU.md:51; TAHAK_DAN.md:55 | Spolehlivě pomáhají **jen stanice** | Srážky u sítě zlepšily začátek vzestupu o **2,90 cm**, „**u všech seedů**“. | `dan-sit:sit_dan/SIT_VARIANTY.md`, §3 | Vypustit „jen“; oddělit začátek vzestupu od hlavní chyby. |
| OTAZKY_POROTY.md:18–19 | Měrná křivka se nemění | Novější popis: „**Mezi roky se křivka trochu posouvá**“; při **300 m³/s** Děčín **218–227 cm**, při **1 000 m³/s 453–478 cm**. | `docs/DATA.md`, Hladina je měřená, průtok dopočtený | „Křivka je přibližně stabilní, mezi roky se mírně posouvá.“ |
| OTAZKY_POROTY.md:50–51 | Danovy pokusy rozhodovala **jen CV a LOFO**, čtyři nahlédnutí | Zdroj přiznává: „**rozbor validace ovlivnil směr hledání**“. Čtyři nahlédnutí eviduje první zpráva o Ridge, nikoli souhrn všech pozdějších experimentů. | `dan-ridge:ridge_dan/ZPRAVA.md`, Vyhodnocení, Nálezy Codexu | Přiznat vliv validace na směr hledání a omezit údaj čtyř nahlédnutí na první úkol. |
| OTAZKY_POROTY.md:55 | „Vše opraveno a přepočítáno“ | „**Přepočet B, D a G2 do 00:30 nedoběhl**.“ Další kontrola ponechává výhradu k týmovým pevným dobám doběhu. | `ZLEPSENI.md`, Kontrola Codexu; `VALIDACE_ONDRA.md`, Kontrola Codexu | Omezit tvrzení na konkrétní dokončené opravy; uvést zbývající výhrady. |
| OTAZKY_POROTY.md:74 | Na klidné řece: chyba **12,8 proti 8,2 cm** | Tabulka označuje obě hodnoty jako „**Chyba celkem**“ přes celou validaci, včetně povodní. | `docs/POKUSY.md`, pá 20:15, srovnání čtyř modelů | „Na celé validaci je celková chyba 12,8 proti 8,2 cm.“ |
| OTAZKY_POROTY.md:92; TAHAK_DAN.md:41 | LightGBM: trénink **4,7**, validace **27,8 cm**, bez horizontu | **4,7 / 27,8** patří staršímu rozboru **Děčín +12 h**. Průměr šesti kombinací starého v2 je **40,9**; po opravě dokumentace uvádí **40,8**. | `docs/POKUSY.md`, pá 19:45, v1/v2; pá 20:15, přepočet; `results/2026-10-23_1940_lgbm_v2.json` | Výslovně napsat „starší běh D12“; nesrovnávat tuto dvojici přímo s průměrem 23,1. |
| TAHAK_DAN.md:41 | Regrese **19,7 proti 15,5**, bez označení metriky | „**Děčín +24 h trénink / validace: … 19,7 / 15,5 cm**.“ | `docs/POKUSY.md`, so 0:48 | Doplnit **D24**. |
| OTAZKY_POROTY.md:121; TAHAK_DAN.md:44 | G3 na „validaci“ **18,2 proti 15,5** | Tabulka má sloupec „**val Děčín +24**“: **18,2 / 15,5**. Nejde o zde definovaný průměr šesti kombinací. | `dan-ridge:ridge_dan/ZLEPSENI.md`, Všechny varianty | Napsat „na validaci **D24**“. U poplachů také výslovně uvést LOFO. |
| OTAZKY_POROTY.md:138; TAHAK_DAN.md:13,61 | Za 36 h už voda neprotekla žádnou stanicí; dál předpovídat nejde | Zdroj uvádí hranici „**za víc než 40 h**“; navíc existují pokusy na **48 a 72 h**. | `docs/POROZUMENI.md`, Proč zpoždění a horizonty; `docs/POKUSY.md`, pá 22:46 | „Na 36 h už část přicházející vody síť stanic nezachytí; delší horizonty mají výrazně větší chybu.“ |
| OTAZKY_POROTY.md:143–144 | Z každé stanice sedm zpoždění **0–36 h** | Průtoky: **0, 3, 6, 12, 18, 24, 36**; hladiny: **0, 1, 2, 3, 6, 12, 24**. | `docs/PREHLED.md`, Vstupy modelů | Rozlišit **84 průtokových a 14 hladinových vstupů**. |
| OTAZKY_POROTY.md:171 | Šestihodinové srážky jsou známé „hned“ | „Do modelu smí od **E + 1 h**“, některé dorovnané díly až od **07/19 UTC**. | `dan-srazky:srazky_dan/ZPRAVA_SRAZKY.md`, Data, Časování | „Jsou dostupné dříve než denní úhrny, s popsaným zpožděním.“ |
| OTAZKY_POROTY.md:191 | Validace **26,0 cm**, **51 %** do ±20 cm | **26,0 cm** je Děčín +36 h; **51 %** je souhrnný podíl přes oba cíle při horizontu 36 h. | `results/2026-10-23_201351_ridge.json`, D36; `docs/POKUSY.md`, pá 20:15 | Označit rozdílné soubory hodnocených předpovědí. |
| OTAZKY_POROTY.md:192 | Vrcholy na testu D24 v průměru o **10,5 cm níž** | **−10,5 cm** je **bias v povodňových hodinách**; „Chyba vrcholu“ je **21,4 cm**. | `docs/PREHLED.md`, Finální model na testu podrobně, D24 | „Na povodňových hodinách má bias −10,5 cm.“ |
| OTAZKY_POROTY.md:191–192; TAHAK_DAN.md:62 | Boris dokládá podhodnocování vrcholů vyšších než trénink | Boris **649 cm** je nižší než tréninková povodeň 2013 s **1 072 cm**. | `docs/DATA.md`, Povodně nad 3. stupněm; `docs/POROZUMENI.md`, Proč vyhrála regrese | Boris dokládá podhodnocení vrcholu, nikoli extrapolaci nad tréninkové maximum. |
| OTAZKY_POROTY.md:213 | DIBAVOD pro **nejbližší** N-letou vodu | Kód vybírá „**největší … kterou průtok dosáhne**“, nikoli nejbližší. | `app/rozliv.py`, `n_leta_voda`; `app/mapbox_mapa.py`, `uroven` | „Pro nejvyšší dosaženou dostupnou N-letou úroveň.“ |
| TAHAK_DAN.md:10 | Všech 98 čísel bylo změřeno **v čase t** | Vstupy zahrnují měření z času **t až t−36 h**. | `docs/PREHLED.md`, Vstupy modelů | „98 čísel dostupných v čase t.“ |
| TAHAK_DAN.md:39 | **198 + 89 + 116 + 95 + 80 − 2 = 577** | Součet uvedených zaokrouhlených členů je **576**. Zdroj prezentace sám uvádí **577**. | `docs/PREZENTACE_7MIN.md`, slajd 4 | Použít **≈ 577 cm** a přiznat zaokrouhlení příspěvků. |
| TAHAK_DAN.md:45 | SHAP při povodni 2011 kolem **18 cm** | „při povodni 2011 v průměru **19 cm vlivu**“ | `docs/POKUSY.md`, pá 20:00, LightGBM a SHAP | „Kolem **19 cm**.“ |
| OTAZKY_POROTY.md:217–218 | Pro Dnešek se používá model učený do 2025 | Takový režim má `ridge_vse`; aplikace však výchozí volbu nastavuje na **`ridge`** a přepínač Dnešek předává zvolený model. | `app/app.py`, výběr modelu a větev `if dnes`; `app/predikce.py`, `nacti_model` | Doplnit podmínku: „Pro Dnešek **zvolíme ridge_vse**.“ |

**2. Tvrzení, která nejde z uvedených zdrojů ověřit**

- **OTAZKY_POROTY.md:3:** délka odpovědí **15–30 s** — chybí měření nebo nácvik.
- **OTAZKY_POROTY.md:224–226:** právní kompetence a odpovědnost podle zákona **254/2001 Sb.** — text sám přiznává, že v repozitáři podklad není.
- **OTAZKY_POROTY.md:226:** „stačí uvést zdroj“ — zdroje uvádějí licenci ČHMÚ, ale nedokládají úplnost tohoto shrnutí licenčních povinností.
- **OTAZKY_POROTY.md:228:** obecná volnost NOAA ISD — zpráva rozlišuje dílo vlády USA a data výměny WMO s uvedeným **nekomerčním použitím**; jednotný neomezený režim nedokládá.
- **TAHAK_DAN.md:32; OTAZKY_POROTY.md:122:** kategorické „není náhoda“ / „náhoda“ — uvedené p-hodnoty podporují statistické hodnocení, nikoli jistotu těchto závěrů.

**3. Počet zkontrolovaných čísel**

Počítám výskyty zapsané číslicemi a zlomky; opakování a meze intervalů zvlášť. Vynechávám číslování položek, odkazy a identifikátory typu G3 či D24. Chybné označení metriky počítám jako nesoulad.

| Soubor | Zkontrolováno | Sedí | Nesedí | Neověřitelné |
|---|---:|---:|---:|---:|
| PREHLED_POKUSU.md | 213 | 207 | 6 | 0 |
| OTAZKY_POROTY.md | 336 | 318 | 14 | 4 |
| TAHAK_DAN.md | 155 | 144 | 11 | 0 |
| **Celkem** | **704** | **669** | **31** | **4** |

Celkově základní výsledky sedí, ale podklady potřebují přesnější označení metrik, oddělení starších běhů a zmírnění několika příliš obecných závěrů.