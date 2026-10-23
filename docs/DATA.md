# Data

Co víme o datech. Kdo něco zjistí, doplní nebo opraví příslušnou sekci. U každého tvrzení, jestli je ověřené, nebo jen domněnka.

## Labe (vybraná úloha)

**Společná tabulka:** `data/external/labe_hodinove.parquet` (4,8 MB, v Gitu). Hodinově 2006–2025 (UTC), 175 320 hodin. Postaví ji `python src/data.py` ze surových dat ČHMÚ (`src/stahni_chmu_hydro.py`, asi 280 MB). Ostatní kód čte jen ji.

| Sloupce | Stanice |
|---|---|
| hladina (cm) i průtok (m³/s) | Děčín, Ústí nad Labem (cíle) |
| jen průtok | Louny (Ohře), Mělník, Vraňany (Vltava), Kostelec n. L., Praha-Chuchle, Nymburk, Předměřice (Jizera), Beroun (Berounka), Nespeky (Sázava), Přelouč |

**Souřadnice stanic:** `data/external/stanice_hydro.csv` (v Gitu, 12 řádků): klíč jako v `data.py`, číslo ČHMÚ, název, tok, zeměpisná šířka a délka (`lat`, `lon`) a stupně povodňové aktivity v cm. Vytaženo z metadat ČHMÚ v balíčku pořadatelů (`meta1-20260930.json`, 545 profilů) skriptem `src/stanice_hydro.py`. Ověřeno: stupně pro Děčín a Ústí souhlasí s `data.SPA`. Předměřice (Jizera) stupně v metadatech nemají. Pro mapu v aplikaci.

**Hladina je měřená, průtok dopočtený** (ověřeno pá 22:48). Hladinu ČHMÚ měří čidlem na vodočtu, průtok z ní počítá měrnou křivkou, kterou sestaví z občasných měření rychlosti vody a průřezu koryta. Šířku ani tvar koryta v datech nemáme, v metadatech stanic (`meta1-20260930.json`) jsou jen poloha a stupně povodňové aktivity. Že je průtok dopočtený, je vidět na datech: v jednom roce se hladina v Děčíně i Ústí při stejném průtoku liší o 1 cm (medián), u 99 % hodin nejvýš o 5–10 cm. Mezi roky se křivka trochu posouvá, jak se mění koryto a jak ČHMÚ křivku upravuje: při 300 m³/s je Děčín 218–227 cm a Ústí 248–257 cm, při 1 000 m³/s Děčín 453–478 cm a Ústí 486–513 cm. Graf křivky Děčína je `docs/grafy/fyzika_merna_krivka.png`. Oficiální měrnou křivku ČHMÚ zveřejňuje v otevřených datech (`hydrology/characteristic/data/discharge_rating_curve/RC_0-203-1-240000.json`), Honza z ní bral hladiny N-letých vod (`data/external/n_lete_vody.csv`).

**Starší povodně a jiná místa** (ověřeno pá 23:52). Hodinová data ČHMÚ jsme stáhli od 2002, ale celá sada stanic je až od 2006: Děčín má hodinová data od 2003, Louny od 2004, Kostelec a Nymburk od 2006. Povodeň 8/2002 (největší v historii měření) v hodinových datech nemá hladinu v Děčíně ani v Ústí, takže se na ní nedá učit ani ověřovat. Starší data má ČHMÚ jen po dnech: denní průměrný průtok v Děčíně od 1887. Denní průměr ale rozmaže vlnu, která do Děčína putuje 4–40 h, pro předpověď na 12–36 h po hodinách se nehodí. Data z jiných řek (Morava, Odra) nepomůžou: model se učí váhy konkrétních stanic na Labi a jejich doby putování, jiná řeka má jiné stanice, vzdálenosti i koryto.

### Přidaná data ČHMÚ: co, odkud a proč

**Odkud:** otevřená data ČHMÚ, https://opendata.chmi.cz/hydrology/historical/data/hourly/. Soubory jsou `H_0-203-1-<číslo stanice>_HQ_<rok>.json` s hodinovou hladinou (H) a průtokem (Q). Zdarma a bez registrace, v prezentaci uvést zdroj ČHMÚ. Stáhli jsme 26 stanic (`src/stahni_chmu_hydro.py`), do společné tabulky bereme 12.

**Proč přidávat data:** balíček má na Labi jen Litoměřice, Ústí, Děčín a Hřensko, a to jen 2024–2026 s jedinou povodní (9/2024). Nejvýš proti proudu je Ústí, odkud voda do Děčína doteče za 4 h. Z balíčku tedy nejde vidět dál než pár hodin dopředu a s jednou povodní nejde nic ověřit. Přidaná data dávají dvě věci:
- **prostor:** stanice proti proudu, tedy delší předstih,
- **čas:** 20 let historie, tedy povodně na učení i na test.

**Které stanice a proč.** Labe do kraje přitéká třemi větvemi: Vltava, horní Labe a Ohře. Na každé bereme stanice v několika vzdálenostech („brány“), protože na delší horizont je potřeba vidět dál proti proudu. Doba putování do Ústí je změřená z dat ve dvou podobách: kdy se nejvíc projeví změna průtoku a medián, za jak dlouho dorazil vrchol povodně. Mezi povodněmi se hodně liší.

| Klíč | Stanice | Větev | Do Ústí (změna / vrchol) | Proč |
|---|---|---|---|---|
| `decin` | Děčín | Labe | Ústí → Děčín 4 h | cíl, nejbližší stanice k městu |
| `usti` | Ústí nad Labem | Labe | 0 | druhý cíl a pro Děčín nejbližší brána |
| `louny` | Louny | Ohře | 12 / 34 h | poslední stanice na Ohři před soutokem v Litoměřicích |
| `melnik` | Mělník | Labe pod soutokem s Vltavou | 9 / 14 h | všechna voda z Čech kromě Ohře na jednom místě |
| `vranany` | Vraňany | Vltava | 9 / 20 h | Vltava těsně před soutokem |
| `kostelec` | Kostelec nad Labem | horní Labe | 6 / 14 h | horní Labe těsně před soutokem |
| `praha` | Praha-Chuchle | Vltava | 14 / 22 h | Vltava s Berounkou; povodeň 2013 byla z 80 % Vltava |
| `nymburk` | Nymburk | horní Labe | 6 / 14 h | Labe nad Jizerou |
| `jizera` | Předměřice | Jizera | 15 / 26 h | největší přítok horního Labe |
| `beroun` | Beroun | Berounka | 18 / 36 h | velký přítok Vltavy, nejdelší předstih |
| `sazava` | Nespeky | Sázava | 20 / 24 h | velký přítok Vltavy |
| `prelouc` | Přelouč | horní Labe | 15 / 22 h | nejvzdálenější stanice na Labi |

U stanic proti proudu bereme jen **průtok**, ne hladinu. Průtok se mezi stanicemi sčítá (Mělník = Vraňany + Kostelec, ověřeno), kdežto hladina je místní a závisí na korytě a jezech.

**Co jsme nevzali a proč:**
- **Zbraslav (Vltava):** skoro totéž co Praha-Chuchle, jen bez Berounky.
- **Žatec, Kadaň, Karlovy Vary (Ohře):** Ohři reguluje přehrada Nechranice a informaci z nich z velké části nese Louny. Dají se přidat, kdyby Ohře modelu chyběla.
- **Litoměřice:** data až od 2017.
- **Hřensko (Labe):** leží pod Děčínem, pro předpověď nepomůže.
- **Přítoky v kraji** (Bílina a Ploučnice mezi Ústím a Děčínem, menší potoky): voda z nich do Labe doteče za 0–7 h. V průměru dají 12 m³/s, Děčín má proti Ústí o 4–8 % víc vody. Při vrcholu povodně přidaly 2–13 %: nejvíc v srpnu 2010 (188 m³/s, lokální deště), při povodni 2013 jen 2 %, v září 2024 jen 15 m³/s. Zkusili jsme je přidat do lineárního modelu (průtok Trmice a Benešov nad Ploučnicí, zpoždění 0–12 h) a na validaci nepomohly: chyba se zhoršila o 0,2–0,5 cm na 6, 12 i 24 h. Jejich vodu za 12 h a víc ještě nikdo nezměřil, záleží na dešti. Co už přiteklo, je vidět v hladině Děčína. Nechané mimo model.
- **Kamenice, Mandava, Chomutovka:** Kamenice ústí pod Děčínem, Chomutovka do Ohře nad Louny a Mandava do Lužické Nisy. Pro Děčín nepomůžou, stažené jsou na pozdější druhou zkoušku modelů.
- **Roky 2002–2005:** Kostelec a průtok v Mělníku a Nymburku chybí do konce 2005. Povodeň 2002 proto nemáme (Děčín má data až od 2003).
- **Rok 2026 z balíčku:** stanice proti proudu za 2026 nemáme, proto tabulka končí rokem 2025.
- **Srážky a počasí:** balíček má meteorologii jen 2024–2026, na 20 let nestačí. Bez srážek nejde předpovídat dál než zhruba den a půl. Možné rozšíření.

**Jak to ovlivňuje výsledek** (ověřeno, podrobně v `docs/NAPAD_LABE.md` a `docs/POKUSY.md`):
- Děčín +24 h, 6 povodní, které model neviděl: „jako teď“ 58 cm, jen kraj za 2 roky (jako balíček) 43 cm, kraj + proti proudu za 2 roky 28 cm, jen kraj za 20 let 38 cm, oboje 24 cm. Stanice proti proudu pomohly víc než dlouhá historie.
- Ústí: na 12 h stačí blízké brány (17 cm), na 36 h pomáhá každá další vrstva (37 cm se všemi, 52 cm jen s blízkými).
- Se společným rozdělením (`src/evaluate.py`): lineární model Děčín +24 h 15,5 cm na povodních proti 44,4 cm u „jako teď“.

**Limity:** neznáme srážky, takže předpověď dál než den a půl nejde. Doba putování se mezi povodněmi mění. V tréninku je jen jedna opravdu velká povodeň (2013). Aktuální data ČHMÚ v aplikaci brát jdou (odstavec „Aktuální data“ níže), jen Mělník a Nymburk se musí dopočítat.

Ověřeno:
- Začínáme rokem 2006, protože průtok v Kostelci, Mělníku a Nymburku za rok 2005 chybí celý.
- Chyba měření: 5.–7. 2. 2006 je v Děčíně hladina až 1 019 cm při průtoku kolem 120 m³/s, skoky o 1–3 m za hodinu, a do 8. 2. dopoledne hladina nesedí s průtokem. Vyřazeno 5. 2. až 8. 2. 9:00, 82 hodin hladiny v Děčíně (ověřeno so 0:01).
- Nic se nedoplňuje. Doplňování děr jsme zrušili, protože bralo hodnotu z hodiny po díře, tedy z budoucnosti. Surová data jiné díry nemají, kromě těch 82 hodin chybí v tabulce 0 hodnot.
- Skoky v Ústí o 50–65 cm za hodinu (2007, 2014, 2019, 2023) jsou skutečné, průtok jde s nimi. Nechané.
- Hladina v Nymburce chybí z třetiny, proto u stanic proti proudu bereme jen průtok.
- Mezi lety 2016 a 2020 nepřekročilo Labe v Děčíně ani 1. stupeň povodňové aktivity, byla to suchá léta.
- Stupně povodňové aktivity (metadata ČHMÚ): Děčín 400 / 490 / 560 cm, Ústí 450 / 530 / 600 cm.

**Kontrola správnosti** (pá 19:30, ověřeno):
- Data ČHMÚ jsou za 2024–2025 na hodinu i na centimetr stejná jako balíček od pořadatelů (Děčín, Ústí, Louny, 17 544 hodin, rozdíl 0, bez časového posunu).
- Bilance vody sedí každý rok: Mělník = Vraňany + Kostelec (poměr 1,00), Ústí = 1,01–1,04 × (Mělník + Louny), Děčín = 1,04–1,08 × Ústí. Navíc přitékají menší přítoky (Bílina, Ploučnice). Žádná stanice nemá v některém roce průtok posunutý.
- Měrná křivka se nemění: při průtoku 250–300 m³/s je hladina v Děčíně každý rok 204–214 cm, v Ústí 234–242 cm. V Děčíně za 20 let klesla asi o 5 cm, nejspíš kvůli dnu řeky (domněnka).
- Časy sedí: voda z Ústí do Děčína dorazí každý rok za 4–5 h, z Prahy do Vraňan za 4–5 h. Vrchol povodně šel z Mělníka do Ústí za 17 h v letech 2006, 2009, 2013 i 2024. Při vyšší vodě se zpoždění Mělník → Ústí zkrátilo z 8–11 h (2006–2013) na 6–7 h (2021–2024). Posun času v datech to není, ten by byl skokový. Nejspíš jde o jezy (domněnka). Modely trénované do 2018 se proto na testu můžou o hodinu dvě splést v načasování.
- Odlehlé hodnoty: jednohodinové výkyvy průtoku, které se hned vrátí, má Vraňany 35 hodin za 20 let, Mělník 3, Přelouč 2, Nymburk 1. Nejspíš manipulace na jezech. Vliv na modely je zanedbatelný, nechané.
- Stejná hodnota déle než 3 dny: Sázava v zimě 8krát (nejdéle 18 dní v lednu 2009) a Louny 2krát, vždy při malém průtoku. Jsou to odhady ČHMÚ při ledu. Na povodně to vliv nemá, nechané.
- Žádné nulové ani záporné hodnoty.

**Povodně v Děčíně nad 3. stupněm:** 4/2006 (875 cm), 8/2010 (560), 1/2011 (730), 6/2013 (1 072), 12/2023 (624), 9/2024 (649).

**Doba doběhu do Děčína** (ověřeno, `src/doba_dobehu.py`): posun s největší korelací změn průtoku za 6 h, jen trénovací část. Ústí 4 h (korelace 0,93), Kostelec 10 h, Nymburk 10 h, Mělník 13 h, Vraňany 13 h, Louny 16 h, Praha-Chuchle 17 h, Předměřice a Přelouč 18 h, Beroun 23 h, Nespeky 25 h. Při velké vodě (Děčín nad 300 cm) vychází skoro stejně, jen korelace je silnější (Mělník 0,76 místo 0,51). Do Ústí je to o 3–4 h méně (Mělník 9 h, Praha 13 h). Z Lounů a vzdálených stanic je korelace slabá (0,2–0,3), doba je tam jen přibližná.

**Rozdělení** (`src/evaluate.py`, dělení v čase, ne náhodně):
- train: 2006–2018 bez validačních povodní a 20 dní kolem nich,
- val: povodně 4/2006, 3/2009, 9/2010 a 1/2011 (14 dní před vrcholem až 5 dní po něm) a klidné roky 2019–2020,
- test: 2021–2025, povodně 12/2023 a 9/2024,
- řádek, jehož vstupy (36 h zpět) nebo cíl (t + horizont) zasahují do jiné části, se vynechá.

Proč takhle: mezi 2016 a 2020 povodeň nebyla, validace na pozdějších letech by nic neřekla. V tréninku zůstává největší povodeň 2013, ve validaci jsou dvě velké a dvě menší.

### Kolik historie a které stanice (ověřeno pá 20:44)

V letech 2014–2018 nebyl v Děčíně ani v Ústí dosažen 2. stupeň: maxima hladin jsou 465 proti prahu 490 cm a 490 proti prahu 530 cm. Okna 1, 2, 3 a 5 let končící rokem 2018 proto neobsahují povodeň na tomto stupni. Okna 8 a 13 let už zahrnují povodeň 2013; množství historie tedy zároveň mění zastoupení vysoké vody.

Na stejné validaci dává nezměněný Ridge se všemi stanicemi při 2 / 5 / 8 / 13 letech chybu na povodních 26,9 / 21,0 / 16,6 / 17,1 cm proti 44,3 cm u „bude jako teď“. Propásnutá varování jsou 4 / 3 / 0 / 0 z 24 případů. Dva roky se všemi stanicemi mají podobnou chybu jako 13 let jen z kraje (27,8 cm), ale slabší varování. Osm a třináct let se v chybě liší jen o 0,47 cm; obecný minimální počet let z toho určit nejde. Podrobnosti a všechny varianty v `docs/POKUSY.md`, graf `docs/grafy/kolik_dat.png`.

### Aktuální data (ověřeno pá 23. 10. večer)

Operativní data ČHMÚ pro předpověď na teď existují, jsou otevřená a bez registrace. Načítá je `app/aktualni.py` (`predpoved_dnes()`), stažené soubory jdou do `data/raw/chmu_aktualni/` (není v Gitu).

- **Odkud:** dnešek od 0:00 UTC po 10 minutách je v `https://opendata.chmi.cz/hydrology/now/data/0-203-1-<číslo stanice>.json`. Soubor se obnovuje zhruba každých 20 minut (viděno 18:20, 19:00 a 19:20 UTC), poslední hodnota je 10–30 minut stará. Předchozí dny jsou po jednom souboru na den v `https://opendata.chmi.cz/hydrology/recent/data/<RRRRMMDD>_0-203-1-<číslo stanice>.json`, od 1. 1. 2026 do včerejška; včerejšek se objeví kolem 0:20 UTC. Model potřebuje 37 hodin zpátky, bereme dnešek a tři předchozí dny (72–96 h), aby to šlo i těsně po půlnoci.
- **Formát:** JSON, `objList[0].tsList`, řady `H` (cm), `Q` (m³/s), `TH` (teplota vody) a k tomu předpověď ČHMÚ `H_F` a `Q_F` po hodinách na 3 dny dopředu. Data jsou nevalidovaná (popis `hydrologicka_data_now_a_recent_popis.pdf` na stejném serveru).
- **Čas je UTC**, i když popis píše SEČ a SELČ. Děčín 18:50 v JSON ukazuje hydro.chmi.cz/hpps jako 20:50 se stejnou hodnotou 90 cm a 85,2 m³/s a den přechodu na letní čas (29. 3. 2026) má všech 144 hodnot.
- **Z 10 minut na hodinu:** hodinové hodnoty v archivu, ze kterého se modely učily, jsou podle ČHMÚ „průměrné hodinové hodnoty“. Na Děčíně 2025 jsme je porovnali s 10minutovými okamžitými stavy: hodina t je průměr t:00 až t:50, po zaokrouhlení sedí v 90 % hodin (průměrná odchylka 0,3 cm). Hodnota přesně v celou hodinu sedí jen v 56 % (0,7 cm), průměr předchozí hodiny ve 43 % (1,1 cm). Aplikace proto počítá stejný průměr a hodinu bere, až když je u stanice celá. Čas vydání předpovědi je tak 1–2 h za skutečným časem.
- **Co chybí:** všech 12 stanic v now/ je, ale průtok v Nymburce ČHMÚ operativně nezveřejňuje vůbec (ani na hpps, jen hladinu) a v Mělníku jen dvakrát denně kolem 5:00 a 11:00 UTC. Oba dopočítáváme z bilance vody ověřené na archivu 2006–2020: Mělník = Vraňany + Kostelec o hodinu dřív (medián odchylky 0,5 %), Nymburk = Kostelec − Jizera (medián odchylky 8 %). Na validaci to Ridge zhorší málo: předpověď se v průměru posune o 1 cm, chyba na povodních Děčín +24 h 15,5 → 16,9 cm a +12 h 9,0 → 10,8 cm, pořád daleko pod „bude jako teď“ (44,3 cm). Dvě denní hodnoty v Mělníku se za 20.–23. 10. od dopočtu liší o 0–15 m³/s při průtoku kolem 60 m³/s. Aplikace u předpovědi vždy píše, co je dopočtené.
- **Navazuje na archiv:** při průtoku 80–90 m³/s je teď Děčín na 90 cm (archiv 2022–2025: 90–94 cm), Ústí při 72–82 m³/s na 125 cm (122–125 cm). Jednotky sedí a posun hladiny proti archivu tam není.
- **Nejnovější stažená hodnota** (pá 23. 10. 2026 v 18:50 UTC, 20:50 našeho času): Děčín 90 cm a 85 m³/s, Ústí 125 cm a 78 m³/s, oboje pod 1. stupněm. Ridge vydaný z hodiny 18:00 UTC: Děčín 98 / 98 / 98 cm za 12 / 24 / 36 h, ČHMÚ ve stejných časech 93 / 91 / 90 cm; Ústí 136 / 135 / 131 cm, ČHMÚ 126 / 126 / 125 cm. Při nízké vodě kolísá hladina v Děčíně a Ústí o 10–30 cm během pár hodin (nejspíš jezy, domněnka). Za 21.–23. 10. měl Ridge na 12 h průměrnou chybu 11 cm v Děčíně i v Ústí, „bude jako teď“ 8 a 12 cm. Na nízké vodě model nic nepřidá, dnešní data hlavně ukazují, že celý řetězec od ČHMÚ po předpověď funguje i naživo.

### N-leté vody a záplavová území (ověřeno pá 21:30)

Pro vrstvu rozlivu na 3D mapě (`app/rozliv.py`). Vlastní hydrauliku (výpočet proudění vody v údolí) neděláme. Předpovězenou hladinu převedeme na průtok, porovnáme ho s N-letými průtoky ČHMÚ (N-letá voda je průtok, který přijde v průměru jednou za N let) a ukážeme oficiální záplavové území pro tu N-letou vodu. Vrchol 2013 v Děčíně (1 072 cm, 3 700 m³/s) tak vyjde jako voda mezi dvacetiletou a padesátiletou.

- **N-leté průtoky:** ČHMÚ, vyhodnocení 2024, https://opendata.chmi.cz/hydrology/characteristic/data/hydrological_characteristic/ (soubory `NY_0-203-1-<číslo stanice>.json`). Děčín Q1 / Q5 / Q20 / Q100 = 1 050 / 1 960 / 2 970 / 4 410 m³/s, Ústí 1 010 / 1 870 / 2 860 / 4 290 m³/s, k tomu Q2, Q10 a Q50. Q1, Q5, Q10, Q50 a Q100 souhlasí s evidenčními listy hlásných profilů (https://hydro.chmi.cz/hppsevlist/download?seq=2497644 pro Děčín, `seq=307228` pro Ústí). Z nich je i nula vodočtu (nadmořská výška, od které se hladina měří): Děčín 120,07 m n. m., Ústí 130,94 m n. m. Hladina ke každé N-leté vodě je z oficiální měrné křivky ČHMÚ (`.../characteristic/data/discharge_rating_curve/RC_0-203-1-<číslo stanice>.json`, v Děčíně platí od 1. 7. 2024): Děčín Q5 707 cm, Q20 919 cm, Q100 1 206 cm. Všechno je v `data/external/n_lete_vody.csv`, zdroj u každého řádku.
- **Měrná křivka z našich dat** (převod hladiny na průtok): medián průtoku v pásmech hladiny po 10 cm za 2006–2025. S oficiální křivkou ČHMÚ se shoduje do 3 %, např. Děčín 400 cm: 782 proti 764 m³/s, 1 000 cm: 3 340 proti 3 370 m³/s. Nad nejvyšší změřenou hladinou (Děčín 1 072 cm) ji neprodlužujeme, aplikace to u popisu napíše.
- **Záplavová území:** DIBAVOD (databáze vodohospodářských dat VÚV TGM), vrstvy D01 (Q5), D02 (Q20), D03 (Q100) a D05 (aktivní zóna pro Q100), stav 30. 10. 2025, https://www.dibavod.cz/27/struktura-dibavod.html. Zipy za celou ČR mají asi 750 MB, leží v `data/raw/zaplavy/` a v Gitu nejsou. Bereme jen polygony toku Labe na úseku Ústí až Hřensko (13,95–14,35° v. d., 50,60–50,90° s. š.), rozdělené na úsek Ústí a úsek Děčín na 50,72° s. š. (zhruba v půli cesty mezi vodočty), zjednodušené s tolerancí 4 m a převedené z S-JTSK do WGS84. Výšku bodů bereme z terénu (dlaždice Terrarium), aby polygony ležely na 3D mapě. Výsledek je `data/external/zaplavova_uzemi.geojson` (0,26 MB), postaví ho `python app/rozliv.py --priprav`.

Limity: polygony platí pro ustálený N-letý průtok, ne pro naši konkrétní povodeň (průběh vlny, led, protipovodňové stěny a stav koryta v nich nejsou). Podle VÚV je průběh jen orientační, závazný ho má správce toku. N-letou vodu pro celý úsek určujeme z jednoho vodočtu. Rozliv v Děčíně ovlivňuje i Ploučnice, která ústí kousek nad vodočtem; její vlastní záplavové území nebereme. Území jsou jen pro Q5, Q20 a Q100, takže mezi nimi nic jemnějšího neukážeme: při průtoku mezi Q5 a Q20 svítí území Q5 a Q20 je jen obrysem.

### Předpověď srážek v aplikaci (ověřeno pá 23. 10. večer)

V režimu Dnešek ukazujeme vedle předpovědi hladiny, kolik má v povodí pršet (`app/pocasi.py`, `predpoved_srazek()`). Je to jen kontext a upozornění, do modelu srážky nevstupují: na horizontech 12 až 36 h je voda z deště už v řekách a srážky z 25 stanic ČHMÚ na validaci nepomohly (17,1 → 17,4 cm, `docs/POKUSY.md`, pá 20:44). Proto je model nevidí a věta v aplikaci to říká.

Zdroj je Open-Meteo Forecast API (https://api.open-meteo.com/v1/forecast, zdarma, bez klíče), hodinové srážky `precipitation` na 3 dny dopředu v UTC. Hodnota v čase t je součet za hodinu před t. Bereme 12 bodů v jednom dotazu: Vltava s Berounkou a Sázavou (Praha, Beroun, Příbram, Benešov, České Budějovice), horní Labe s Jizerou (Hradec Králové, Turnov, Pardubice, Vrchlabí) a Ohře (Karlovy Vary, Louny, Kadaň). Za každé povodí je průměr bodů za příštích 24 a 48 h od teď a nejvyšší úhrn jednoho bodu za 48 h. Nad 20 mm za 48 h v povodí aplikace varuje, že hladina za 36 h a dál může být vyšší, než model říká. Výsledek se drží v paměti 30 minut. Prahová hodnota 20 mm je odhad, ne vyzkoušená hranice (domněnka).

Limity: jsou to předpovědní modely počasí, ne měření, a 12 bodů je hrubý průměr přes povodí, takže lokální bouřka mezi body se ztratí. Zdroj dat: Open-Meteo.com, licence CC BY 4.0, v aplikaci a v prezentaci ho uvést.

### Rozliv z výškového modelu (ověřeno pá 23. 10. v noci)

Oficiální záplavová území jsou jen pro Q5, Q20 a Q100. Pro plynulý rozliv po 10 cm počítáme vlastní statický rozliv z výškového modelu terénu (`app/rozliv_dem.py`). Výška hladiny u vodočtu je nula vodočtu + hladina (Děčín 120,07 m n. m., Ústí 130,94 m n. m.), podél řeky stoupá se sklonem hladiny a zaplavený je každý bod terénu pod touto výškou, který je spojený s korytem (osa Labe z OpenStreetMap, 8 sousedů). Nic se tu neučí, je to jen porovnání výšek.

- **Terén:** ČÚZK DMR 5G (digitální model reliéfu z leteckého laserového skenování, otevřená data), služba https://ags.cuzk.cz/arcgis2/rest/services/dmr5g/ImageServer. Stahujeme rovnou v S-JTSK v nativním rozlišení 2 m, aby buňky byly čtverce a plocha seděla: čtverec 6 × 6 km kolem každého vodočtu po dlaždicích 2 × 2 km (`data/raw/dem/`, 76 MB, není v Gitu). DMR je terén bez budov a mostů, voda v něm má výšku hladiny z doby skenování.
- **Sklon hladiny 0,44 m/km:** z našich hodinových dat 2006–2025 jako rozdíl výšky hladiny v Ústí a v Děčíně o 4 h později na 25,4 km řeky. Medián je 0,438 m/km a v pásmech hladiny od nízké vody po 1 100 cm se mění jen mezi 0,43 a 0,44. Oba vodočty jsou pod jezem Střekov, takže vzdutí jezu to nekazí. Voda v DMR podél osy dává v Děčíně 0,40 až 0,44 m/km, to sedí. V Ústí je voda v DMR poskládaná z různých dnů skenování a na sklon použít nejde.
- **Jez Střekov** je 1,7 km nad vodočtem Ústí. Nad ním držíme hladinu aspoň na úrovni zdrže 141,55 m n. m. (voda v DMR nad jezem má 141,4 až 141,5 m). Bez toho vychází v Ústí IoU pro Q5 jen 0,75.
- **Výstup:** polygony pro hladiny po 10 cm, Děčín 300–1 250 cm a Ústí 350–1 200 cm (aby se vešla Q100 a rekord 2002), obrysy zjednodušené s tolerancí 2,5 m, ostrůvky a díry pod 400 m² vynechané. Soubory `data/external/rozliv_dem_decin.geojson` (3,0 MB) a `rozliv_dem_usti.geojson` (2,4 MB), každý polygon má `cil`, `hladina_cm`, `plocha_ha`, `vyska_hladiny_m`, `zdroj_dem`, `rozliseni_m` a `sklon_m_km`. Aplikace bere `polygon(cil, hladina_cm)` (nejbližší spočítaná hladina). Postaví je `python app/rozliv_dem.py --priprav` (asi 3 minuty), kontrolu vypíše `python app/rozliv_dem.py`.

Ověření proti oficiálním záplavovým územím DIBAVOD ve stejném čtverci 6 × 6 km, hladina N-leté vody z měrné křivky ČHMÚ. IoU je průnik děleno sjednocením, 1 znamená úplnou shodu.

| | hladina | náš rozliv | DIBAVOD | průnik | IoU |
|---|---|---|---|---|---|
| Děčín Q5 | 707 cm | 167 ha | 183 ha | 165 ha | 0,89 |
| Děčín Q20 | 919 cm | 219 ha | 229 ha | 209 ha | 0,87 |
| Děčín Q100 | 1 206 cm | 311 ha | 289 ha | 281 ha | 0,88 |
| Ústí Q5 | 738 cm | 123 ha | 134 ha | 122 ha | 0,90 |
| Ústí Q20 | 936 cm | 160 ha | 164 ha | 149 ha | 0,84 |
| Ústí Q100 | 1 157 cm | 252 ha | 223 ha | 213 ha | 0,82 |

Z jednoduchého porovnání výšek tak vyjde skoro stejné území jako z oficiálního hydraulického modelu. Na sklonu v okně ±3 km tolik nezáleží: s vodorovnou hladinou má Děčín Q5 IoU 0,84, se sklonem 0,3 m/km 0,88. Při 300 cm v Děčíně je zaplaveno 110 ha na 8,6 km řeky, to je pruh široký průměrně 127 m, tedy skoro jen koryto (dál než 100 m od osy jen 10 ha); v Ústí při 350 cm 78 ha. Plocha s hladinou nikde neklesá (Děčín 110 → 321 ha, Ústí 78 → 281 ha). Rozdíly: náš rozliv navíc zatéká do údolí přítoků, hlavně Bíliny v Ústí (většina z 39 ha navíc u Q100), a do nízkých míst v centru Děčína u ústí Ploučnice a v Podmoklech. DIBAVOD má navíc úzké pásy podél břehů a kus údolí Ploučnice nad jejím ústím (6 ha u Q5), kam v našem modelu hladina Labe nedosáhne.

Limity: je to statický model bez dynamiky, nepočítá proudění ani objem a průběh vlny a zaplaví všechno pod hladinou spojené s korytem, i kdyby se tam voda za povodeň nestihla dostat. Protipovodňové zdi, mobilní stěny a malé hráze užší než 2 m v terénu nejsou, mosty a podjezdy DMR nemá, takže voda projde i tam, kde ve skutečnosti nemusí. Vzdutí jezu Střekov je jen vodorovná hladina zdrže, při velké vodě se jez sklápí a hladina nad ním je jiná. Ploučnice a Bílina mají vlastní průtok, model jim dává jen hladinu Labe. Sklon je jeden pro celé okno a okno má jen 6 × 6 km. Ověřené je to jen proti modelovým územím DIBAVOD, ne proti skutečnému rozlivu (snímky povodní 2002 nebo 2013 jsme neporovnávali).

## Ovzduší

Z doby, kdy jsme zvažovali úlohu Ovzduší. Týkají se jí všechny sekce níž.

## Soubory

Balíček úlohy Ovzduší je rozbalený v `data/raw/ovzdusi/uloha_2/` (není v Gitu).

| Soubor | Co obsahuje |
|---|---|
| `Hlavní dataset/ovzdusi_hodinove_wide.csv` | hodinová měření ČHMÚ, 13 stanic, 1. 1. 2024 – 30. 9. 2026 (UTC), 312 369 řádků (ověřeno) |
| `Hlavní dataset/metadata/metadata.json` | 98 stanic ovzduší ČR, poloha v `Localization.Lat/Lon` ve stupních, minutách a vteřinách |
| `Hlavní dataset/metadata/ValueType.csv`, `AirQualityIndex.csv` | kódy kvality a stupně indexu kvality 1A–3B |
| `Doplňkové datasety/meteorologie_hodinove_wide.csv` | hodinová meteorologie, 32 stanic, bez názvů a poloh |
| `Geodata obcí/obce_ustecky_kraj.geojson` | hranice 354 obcí (13 MB) |

Data přidaná z internetu (`data/external/`, v Gitu, protože jsou veřejná):

| Soubor | Co obsahuje | Zdroj |
|---|---|---|
| `chmu_meteo_meta1-20261023.json` | seznam meteostanic ČHMÚ s názvy, polohou a výškou | https://opendata.chmi.cz/meteorology/climate/now/metadata/ |
| `stanice_ovzdusi.csv` | 13 stanic ovzduší s polohou v desetinných stupních | z `metadata.json` |
| `parovani_ovzdusi_meteo.csv` | ke každé stanici ovzduší nejbližší meteostanice s teplotou i větrem | `src/parovani_stanic.py` |

Všech 32 meteostanic z balíčku jsme v seznamu ČHMÚ našli (ověřeno). Nejbližší meteostanice je od stanice ovzduší 0–6 km, jen Chomutov 11,7 km a Štětí 14,5 km. Pozor: nejbližší neznamená stejná výška. Ústí-město (v údolí) dostalo Kočkov (375 m).

## Sloupce a jejich význam

- Ovzduší: `station, dt, PM10, PM2_5, NO2, NOx, O3, SO2, CO` v µg/m³ a ke každé látce `<látka>_quality`.
- Meteorologie: `T` teplota, `H` vlhkost, `P` tlak, `SRA1H` srážky za hodinu, `Fprum` rychlost větru, `Dprum` směr větru. Jednotky dokumentace uvádí jen jako „pravděpodobné“.
- Pozor: u meteostanic ČHMÚ je `GEOGR1` zeměpisná délka a `GEOGR2` šířka, v hydrologických metadatech naopak.

Co která stanice měří (podíl hodin s platnou hodnotou):
- PM10 má 11 stanic, chybí Doksany a Sněžník.
- PM2,5 nemá Chomutov, Rudolice a Ústí-město.
- CO měří jen Ústí-Všebořická.
- Chomutov měří jen PM10.

## Jak data vypadají

- **Sezóna** (z reportu): PM10 je v zimě zhruba dvojnásobné proti létu.
- **Poměr PM2,5/PM10** (ověřeno, medián): zima 0,78, léto 0,54, Silvestr 1. 1. 2025 0–3 h 0,91, 30.–31. 3. 2024 0,39. Domněnka: vysoký poměr znamená spalování, nízký prach. Březen 2024 by tak mohl být saharský prach, ověřit.
- **Inverze** (ověřeno): když je na Milešovce (830 m) tepleji než v Ústí-Vaňově (150 m), je inverze. Nastává ve 14 % hodin, v zimě v 19 %.

  | | PM10 Ústí-město při inverzi | bez inverze |
  |---|---|---|
  | celý rok | 32,6 | 18,3 |
  | zima (XI–II) | 41,9 | 24,1 |

  Korelace rozdílu teplot s PM10 je v zimě 0,5. Sedí to s fyzikou: studený vzduch zůstane v údolí pod teplejší vrstvou a znečištění nemá kam odejít.
- **Stanice jdou spolu:** PM10 jednotlivých stanic jde odhadnout z ostatních s chybou kolem 5 µg/m³. Výjimkou je Lom s chybou 11, ten má zřejmě místní zdroj. Ověřeno lineárním modelem na validaci 7–12/2025.
- **Labe a ovzduší v Děčíně spolu nesouvisejí** (ověřeno na denních průměrech):
  - Teplota vody a NO₂ mají korelaci −0,69, ale po odečtení ročního období jen −0,10. Je to jen léto proti zimě.
  - Při povodni v září 2024 byl během deště vzduch čistý (PM10 kolem 5). Společnou příčinou je počasí.

## Chybějící, chybné a podivné hodnoty

- Platné hodnoty mají kvalitu 9 (ověřená) a 8 (operativní). Kvalita 10 a 11 je hodnota pod detekčním limitem, nejspíš taky platná (ověřit). 6 a 7 jsou chyby.
- Hodnoty −5000 až −5011 jsou technické kódy, ne koncentrace. Převést na chybějící hodnotu.
- Rok 2026 má jen operativní data (kvalita 8 a 6), roky 2024–2025 jsou ověřené.
- V asi 28 tisících hodin je PM2,5 vyšší než PM10 (z reportu, neověřeno). Jsou to různé měřicí metody.
- Odlehlá hodnota SO₂ 1 096 µg/m³ (z reportu).
- Čas je v UTC. Pro denní průběh převést na Europe/Prague.

## Rozdělení na train / val / test

Návrh (ještě neschválený): trénink 1/2024–6/2025, validace 7–12/2025, test 2026. Dělení v čase, nikdy náhodně.

## Úpravy dat

Zatím žádné.
