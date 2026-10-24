Níže jsou otázky mířené na skutečné slabiny podkladů. **D24 znamená Děčín +24 hodin**; čísla přebírám z dokumentace, nic jsem netrénoval ani nespouštěl test.

1. **Otázka:** „Těch 17,1 cm počítáte jen kolem povodní, jejichž vrchol znáte až zpětně. Co přesně tím měříte a kolik obtížných hodin vám průměr schová?“

   **Proč je záludná:** Zaměňuje se zde podmíněná přesnost během vybraných událostí s celkovou provozní užitečností.

   **Slabé místo v podkladech:** [src/evaluate.py](C:/Users/danie/Documents/hackathon-2026-prezentace/src/evaluate.py), funkce `vyhodnot`: chybí citlivost výsledku na délku oken a samostatné hodnocení vzestupu, kulminace a poklesu.

   **Doporučená odpověď:** „Hlavní metrika používá okna sedm dní před vrcholem až pět dní po něm, přičemž událost musí dosáhnout 2. SPA. Uvnitř každé kombinace stanice a horizontu průměrujeme chyby hodin v těchto oknech, potom šest kombinací. Na validaci máme 17,1 proti 44,3 cm; přes všechny validační hodiny 8,2 proti 12,8 cm. Zpětné vymezení událostí není samo o sobě únik do vstupů, ale citlivost na vymezení oken doloženou nemáme.“ *(Zdroj: `src/evaluate.py::vyhodnot`, `docs/POKUSY.md`, pá 20:15.)*

2. **Otázka:** „Proč právě tyto čtyři validační povodně? A proč jednou prezentujete čtyři, podruhé osm a potřetí 22 — nejsou to tři různé úlohy?“

   **Proč je záludná:** Změna prahu a skladby událostí může změnit pořadí modelů i bez jakéhokoli zlepšení.

   **Slabé místo v podkladech:** [docs/POKUSY.md](C:/Users/danie/Documents/hackathon-2026-prezentace/docs/POKUSY.md), pá 23:27, a `origin/dan-ridge:ridge_dan/ZLEPSENI.md`: soubory popisují rozdílné soubory událostí, ale nedokládají nezávislost původního výběru čtyř povodní na prvním průzkumu.

   **Doporučená odpověď:** „Validace obsahuje 4/2006, 3/2009, 9/2010 a 1/2011; podle našeho rozboru jsou tři události z tání a jedna dešťová. Vícenásobná validace vybírá osm bloků nad 2. SPA v Děčíně, ale chybu počítá kolem vrcholů nad 1. SPA. Danovo LOFO zahrnuje 22 povodní nad 400 cm, takže obsahuje i menší události a jeho průměr nelze přímo zaměňovat s hlavní validací. Předem doložené zdůvodnění výběru právě původních čtyř povodní v předložených podkladech nemáme.“ *(Zdroj: `docs/POKUSY.md`, pá 22:46 a 23:27; `src/krizova_validace.py`; uvedené `ZLEPSENI.md`.)*

3. **Otázka:** „Obhajujete 98 vah pomocí 108 tisíc hodin. Kolik máte nezávislých hydrologických situací — a proč má vyšší chyba na tréninku dokazovat, že se nepřeučujete?“

   **Proč je záludná:** Velký počet silně závislých hodin ani obtížnější trénovací povodně nevylučují přeučení.

   **Slabé místo v podkladech:** [prezentace_dan/OTAZKY_POROTY.md](C:/Users/danie/Documents/hackathon-2026-prezentace/prezentace_dan/OTAZKY_POROTY.md), otázka 17, a `docs/POKUSY.md`, so 0:48: kategorické „nepřeučuje se“ není uvedeným srovnáním prokázáno.

   **Doporučená odpověď:** „108 tisíc hodin není 108 tisíc nezávislých příkladů; například průtok Prahy nyní a před třemi hodinami má korelaci 0,998. Chyba D24 na trénovacích povodních 19,7 proti validačním 15,5 cm souvisí také s tím, že trénink obsahuje mimořádný rok 2013. Toto srovnání přeučení nevylučuje, pouze neukazuje obvyklý velký rozdíl ve prospěch tréninku. Opíráme se proto také o vynechávání celých událostí; efektivní počet nezávislých situací jsme neodhadli.“ *(Zdroj: `docs/POKUSY.md`, so 0:48; `prezentace_dan/TAHAK_DAN.md`.)*

4. **Otázka:** „Říkáte dělení v čase, ale při předpovídání povodně 2006 učíte model také na roce 2013. Jak byste tuto informaci měli k dispozici v roce 2006?“

   **Proč je záludná:** Oddělení událostí není totéž jako skutečná simulace postupného nasazení.

   **Slabé místo v podkladech:** [docs/POKUSY.md](C:/Users/danie/Documents/hackathon-2026-prezentace/docs/POKUSY.md), pá 23:27: tvrzení, že u fyzikálních vztahů pozdější trénovací události „nevadí“, neověřuje jejich časovou stabilitu.

   **Doporučená odpověď:** „Naše validace a LOFO jsou retrospektivní: hodnotí přenos na vynechanou událost, nikoli tehdejší provozní předpověď. Ve vícenásobné validaci se učíme na ostatních datech 2006–2020, tedy i na pozdějších povodních. Chronologicky dopředný je deklarovaný test 2021–2025 s tréninkem do konce 2020, kde Ridge dosáhl 22,4 cm. Soustavné hodnocení s postupným posouváním tréninku v čase doložené nemáme.“ *(Zdroj: `docs/POKUSY.md`, pá 21:00 a 23:27; `src/krizova_validace.py::casti_blok`.)*

5. **Otázka:** „Tvrdíte, že dobu doběhu počítáte jen z tréninku. Z tréninku kterého foldu — a jsou po opravách opravdu přepočítaná všechna čísla, která ukazujete?“

   **Proč je záludná:** Informace může uniknout přes přípravu příznaků a vnitřní výběr modelu, přestože finální regrese držené řádky nevidí.

   **Slabé místo v podkladech:** `origin/dan-ridge:ridge_dan/STANICE_VSEM.md`, `ZLEPSENI.md` a `VALIDACE_ONDRA.md`: přiznané pevné týmové doby doběhu a nedokončený opravený přepočet B, D a G2.

   **Doporučená odpověď:** „U nových stanic LightGBM byl odhad původně proveden i z drženého bloku; po opravě uvnitř foldu se CV změnila z 16,20 na 16,01 cm. Pevné týmové doby `lgbm_a.DOBA` ale zůstávají výhradou při pozdějším vynechávání povodní, které původní odhad obsahoval. U B, D a G2 našla kontrola také překryv vnitřního hodnocení s ochrannou mezerou vnějšího foldu, například 48 hodin mezi 12/2012 a 1/2013, a opravený přepočet nedoběhl. Jejich stará čísla tedy nesmíme vydávat za výsledky opraveného postupu ani zaručovat směr změny bez přepočtu.“ *(Zdroj: uvedené tři zprávy, sekce kontrol a nálezů.)*

6. **Otázka:** „Jak mohl být test 2021–2025 nedotčený, když vaše první průzkumné pokusy už používaly data až do roku 2025 a Dan pak test spustil ještě zvlášť?“

   **Proč je záludná:** Jednorázové spuštění finálního příkazu neprokazuje, že výsledky testového období dříve neovlivnily návrh.

   **Slabé místo v podkladech:** [docs/POKUSY.md](C:/Users/danie/Documents/hackathon-2026-prezentace/docs/POKUSY.md), pá 17:46, 18:36 a 18:44, proti tvrzení u pá 21:00; `origin/dan-ridge:ridge_dan/ZPRAVA.md` uvádí další test ve 21:49.

   **Doporučená odpověď:** „Finální týmový model je podle zápisu vybraný ve 20:58 a týmový test proběhl ve 21:00; Danův samostatný test D24 následoval ve 21:49. Předchozí průzkumy ale uvádějí rozsahy 2004–2025 a 2005–2025, včetně experimentu s balíčkem 2024–2025. Z těchto zápisů nedokážeme vyloučit, že informace z pozdějšího testového období ovlivnila návrh úlohy nebo modelu. Poctivě proto rozlišujeme jednorázový finální běh od silnějšího, zde nedoloženého tvrzení o úplně nedotčeném testu.“ *(Zdroj: uvedené záznamy `docs/POKUSY.md`; uvedená `ZPRAVA.md`, sekce Vyhodnocení.)*

7. **Otázka:** „Proč test znovu nespustíte? A jestli mu věříte, proč vám nestačí k přijetí lepší sítě nebo Danova modelu?“

   **Proč je záludná:** Prověřuje rozdíl mezi reprodukcí výpočtu, výběrem podle známého výsledku a nezávislým potvrzením nové varianty.

   **Slabé místo v podkladech:** [prezentace_dan/REPRODUKOVATELNOST.md](C:/Users/danie/Documents/hackathon-2026-prezentace/prezentace_dan/REPRODUKOVATELNOST.md): test se při reprodukční kontrole neověřoval a otisk nezahrnuje kód modelu ani verze knihoven.

   **Doporučená odpověď:** „Opakování stejného zmrazeného běhu kvůli reprodukci samo o sobě není ladění; problém by byl měnit model podle již známého testového výsledku. Síť má na testu 21,3 proti 22,4 cm Ridge, ale podle tohoto rozdílu jsme finální výběr nezměnili. Danův Ridge má na D24 16,1 proti 17,5 cm, což není test později navržených G3 nebo H30. Pro ty potřebujeme další nezávislé období nebo předem stanovené prospektivní ověření; opakováním známého testu nové nezávislé události nezískáme.“ *(Zdroj: `docs/PREHLED.md`, Finální test; `origin/dan-ridge:ridge_dan/ZPRAVA.md`; `prezentace_dan/REPRODUKOVATELNOST.md`.)*

8. **Otázka:** „Po desítkách pokusů jste našli G3 a H30. Proč jim říkáte ověřené zlepšení, když jste na stejných povodních také hledali, co vůbec vyzkoušet?“

   **Proč je záludná:** Pevná váha směsi ani vnořené ladění parametrů neodstraní přizpůsobení samotných nápadů výsledkům.

   **Slabé místo v podkladech:** `origin/dan-ridge:ridge_dan/ZLEPSENI.md` uvádí přibližně 15 variant na 24 h a vznik H30 z povodně 2006; závěr [prezentace_dan/PREHLED_POKUSU.md](C:/Users/danie/Documents/hackathon-2026-prezentace/prezentace_dan/PREHLED_POKUSU.md) používá silnější formulace.

   **Doporučená odpověď:** „G3 zlepšil LOFO D24 z 15,29 na 13,94 cm, ale na původní validaci je horší: 18,2 proti 15,5 cm. H30 dosáhl 14,15 cm, jenže jeho návrh vznikl z rozboru hodnocené povodně 2006, takže je průzkumný. Pravidlo zlepšení alespoň o 1 cm a zastavení po neúspěších není korekce mnohonásobného porovnávání. G3 je slibný kandidát a H30 průzkumný výsledek; nezávislé potvrzení jejich přínosu chybí.“ *(Zdroj: uvedené `ZLEPSENI.md`; `origin/dan-ridge:ridge_dan/VALIDACE_ONDRA.md`.)*

9. **Otázka:** „Co přesně znamená vaše p = 0,0001? Jsou povodně nezávislé, zohledňuje test velikost zhoršení a je následných šest vítězství z osmi nové potvrzení?“

   **Proč je záludná:** Malá p-hodnota znaménkového testu se snadno vydává za důkaz praktického přínosu a nezávislé replikace.

   **Slabé místo v podkladech:** `origin/dan-ridge:ridge_dan/ZLEPSENI.md`: není doložena nezávislost událostí ani interval nejistoty průměrného přínosu po výběru varianty; `VALIDACE_ONDRA.md` naopak závislost osmi událostí výslovně přiznává.

   **Doporučená odpověď:** „G3 vyhrál u 20 z 22 povodní, což dává uvedené malé p za předpokladů znaménkového testu pro předem dané srovnání. Test hodnotí znaménka rozdílů, nikoli jejich velikost: nejhorší zhoršení G3 je přesto 8,2 cm a planých poplachů 2. SPA je v LOFO šest proti čtyřem. Osm následně hodnocených povodní je podmnožinou původních 22; výsledek 19,6 proti 20,1 cm a šest vítězství z osmi s p přibližně 0,29 tedy není nezávislá replikace. Navíc 20,1 ± 7,7 cm označuje směrodatnou odchylku mezi povodněmi, nikoli interval spolehlivosti průměru.“ *(Zdroj: uvedené `ZLEPSENI.md` a `VALIDACE_ONDRA.md`.)*

10. **Otázka:** „Síť prezentujete číslem 17,8 cm. Proč ne průměrem 19,0 cm přes seedy — a proč mají tři identické běhy LightGBM dokazovat stabilitu výsledku?“

    **Proč je záludná:** Náhodnost optimalizace, výběr seedu a nejistota přenosu na další povodeň jsou různé věci.

    **Slabé místo v podkladech:** `origin/dan-sit:sit_dan/SIT_VARIANTY.md`: hlavní týmové číslo odpovídá seedu 42, zatímco LOFO sítě bylo provedeno jen pro tento seed.

    **Doporučená odpověď:** „Seed 42 reprodukuje týmových 17,83 cm, ale přes seedy 42–44 má základní síť 19,01 ± 1,18 cm a rozpětí 17,83–20,63 cm. Proto rozdíl 0,7 cm mezi jedním během sítě a Ridge není pevný důkaz pořadí. LOFO sítě máme pouze pro seed 42, takže jeho citlivost na inicializaci neznáme. LightGBM bez náhodného výběru řádků a vstupů dává stejné výsledky konstrukčně; nulový rozptyl mezi seedy nevypovídá o nejistotě na nových povodních.“ *(Zdroj: uvedené `SIT_VARIANTY.md`; `origin/dan-ridge:ridge_dan/STANICE_VSEM.md`.)*

11. **Otázka:** „Jak může předpověď na 24 hodin varovat 27 hodin předem, když váš vlastní hodnoticí kód předstih omezuje na 24 hodin? Které číslo máme považovat za pravdivé?“

    **Proč je záludná:** Tým musí odlišit první předčasné překročení předpovězeného prahu od přesně časované předpovědi skutečného překročení.

    **Slabé místo v podkladech:** [docs/PREZENTACE_7MIN.md](C:/Users/danie/Documents/hackathon-2026-prezentace/docs/PREZENTACE_7MIN.md), slajdy 1 a 7, a `docs/PREHLED.md` uvádějí 27 h pro +24 h; `src/evaluate.py::varovani` předstih explicitně zastropuje horizontem.

    **Doporučená odpověď:** „Podklady uvádějí u Borise 27 hodin pro předpověď na 24 hodin, ale současná funkce `varovani` takový výsledek vrátit nemůže. První alarm může nastat dříve, pokud model předpoví překročení prahu předčasně, což zároveň znamená chybu načasování. Bez doložení konkrétního času vydání, platnosti a skutečného překročení 560 cm tento rozpor neumíme uzavřít. Číslo 27 h proto nesmíme vydávat za předstih vypočtený současnou metrikou pro +24 h.“ *(Zdroj: `src/evaluate.py::varovani`; `docs/POKUSY.md`, pá 21:00; uvedená prezentace.)*

12. **Otázka:** „Co znamená hodnota označená 10:00 — měření dostupné v 10:00, nebo průměr obsahující ještě 10:50? Kolik hodin předstihu vám po skutečném zveřejnění zbude?“

    **Proč je záludná:** Čas měření není čas dostupnosti a hodinová agregace může zpětnému vyhodnocení přidat téměř hodinu informací.

    **Slabé místo v podkladech:** [src/features.py](C:/Users/danie/Documents/hackathon-2026-prezentace/src/features.py) považuje hodnotu v čase `t` za známou, ale `docs/DATA.md`, Aktuální data, popisuje průměr `t:00–t:50` a zpožděné vydání.

    **Doporučená odpověď:** „Archivní hodina t podle našeho porovnání odpovídá průměru t:00 až t:50, takže není celá známá už v t:00. Živá aplikace čeká na úplnou hodinu a její označený čas vydání je podle dokumentace 1–2 hodiny za skutečným časem. Předpověď pro t + 24 h má tedy při zpoždění dostupnosti δ skutečný zbývající horizont 24 − δ hodin. Rozdělení zpoždění všech potřebných stanic při povodni ani celé hodnocení podle skutečných časů příchodu dat nemáme.“ *(Zdroj: `docs/DATA.md`, Aktuální data; `src/features.py`.)*

13. **Otázka:** „Používáte při historickém hodnocení průtoky opravené až po povodni? Proč tvrdíte, že to neovlivní pořadí modelů, když každý používá průtok jinak?“

    **Proč je záludná:** Zpětně revidované vstupy mohou nést znalost, kterou operativní předpověď neměla, a jejich dopad nemusí být pro modely stejný.

    **Slabé místo v podkladech:** [docs/POROZUMENI.md](C:/Users/danie/Documents/hackathon-2026-prezentace/docs/POROZUMENI.md), Co model umí a co ne: tvrzení, že archivní ověření neovlivní srovnání modelů, není doložené.

    **Doporučená odpověď:** „Hodnotíme na zpětně ověřeném archivu a historické verze vstupů dostupné při vydání předpovědi nemáme. Průtok je podle podkladů odvozen z hladiny měrnou křivkou, jejíž změny mohou být významné: při 1 000 m³/s odpovídá v různých letech Děčín 453–478 cm. Rozdíl mezi tehdejší předběžnou a dnešní archivní hodnotou jsme ale nezměřili. Proto připouštíme optimismus absolutních výsledků i možné změny pořadí modelů; tvrzení o neovlivněném pořadí nemáme čím podložit.“ *(Zdroj: `docs/DATA.md`, Hladina je měřená, průtok dopočtený; `docs/POROZUMENI.md`, limity.)*

14. **Otázka:** „V provozu vám vypadne jedna stanice a dvě další dopočítáváte. Vydáte předpověď, odmítnete ji, nebo potichu použijete starou hodnotu — a kde máte ověřenou přesnost právě v takové situaci?“

    **Proč je záludná:** Dobrá přesnost pouze na úplných řádcích neprokazuje dostupnost a spolehlivost služby během výpadků.

    **Slabé místo v podkladech:** [docs/DATA.md](C:/Users/danie/Documents/hackathon-2026-prezentace/docs/DATA.md), Aktuální data, a `src/features.py::tabulka`: historické neúplné řádky se zahazují, ale chybí úplné vyhodnocení výpadků a pravidel náhradního provozu.

    **Doporučená odpověď:** „Operativní Nymburk nemá průtok a Mělník jej má jen přibližně dvakrát denně, proto používáme bilanční dopočty. Jejich dosazení na validaci zhoršilo D24 z 15,5 na 16,9 cm a +12 h z 9,0 na 10,8 cm. To ověřuje konkrétní náhrady, nikoli libovolný výpadek stanice ani souběh výpadků s chybnými předběžnými daty. Obecnou dostupnost a přesnost při výpadcích neznáme; v provozu bychom museli výslovně rozlišovat platnou, náhradní a nevydanou předpověď.“ *(Zdroj: `docs/DATA.md`, Aktuální data; `src/features.py`; `origin/dan-srazky:srazky_dan/ZPRAVA_SRAZKY.md` popisuje také vyřazování hodin při chybějících srážkách.)*

15. **Otázka:** „Z několika hrubých srážkových vstupů usuzujete, že déšť nepomáhá. Proč má znalost denního úhrnu představovat horní mez přínosu hodinového radaru nebo předpovědi počasí?“

    **Proč je záludná:** Dokonalá znalost agregovaného úhrnu neobsahuje časové a prostorové rozložení srážek a neprokazuje strop jiného modelu.

    **Slabé místo v podkladech:** [docs/POKUSY.md](C:/Users/danie/Documents/hackathon-2026-prezentace/docs/POKUSY.md), pá 22:32 a 23:14: příliš silné označení „horní mez“; `origin/dan-srazky:srazky_dan/ZPRAVA_SRAZKY.md` přiznává jen devět použitelných stanic.

    **Doporučená odpověď:** „Prokázali jsme pouze malý přínos vyzkoušených reprezentací: denní meteorologie změnila 17,1 na 17,4 cm a dokonale známé třídenní srážky na 16,1 cm. Šestihodinové srážky v LOFO změnily oba Ridge o méně než 0,1 cm a LightGBM zlepšily asi o 0,5 cm. To není horní mez pro radar, časový průběh deště nebo jiný model; na jediné dešťové validační povodni 9/2010 pomohly dokonale známé srážky na 36 h o 23 %. Vyloučení srážek obhajujeme výsledkem konkrétních pokusů, nikoli obecným tvrzením, že na 12–36 h nemohou pomoci.“ *(Zdroj: `docs/POKUSY.md`, pá 20:44, 22:32, 22:46 a 23:14; uvedená srážková zpráva.)*

16. **Otázka:** „Na slajdu přičítáte centimetry od Vltavy, horního Labe a Mělníka. Jenže Mělníkem už voda z těchto větví protekla — není vaše fyzikální vysvětlení dvojím započítáním téže vody?“

    **Proč je záludná:** Rozklad statistické předpovědi na příspěvky vstupů není bilanční ani kauzální rozklad vody.

    **Slabé místo v podkladech:** [docs/PREZENTACE_7MIN.md](C:/Users/danie/Documents/hackathon-2026-prezentace/docs/PREZENTACE_7MIN.md), slajd 4, a `docs/CESTA_MODELU.md`, §7: analogie s fyzikálním součtem je silnější než omezení skutečného Ridge.

    **Doporučená odpověď:** „Příspěvky jsou rozkladem lineární rovnice vůči zvolenému výchozímu stavu, nikoli množstvím vody dodaným jednotlivými řekami. Na ukázce Borise jsou Vltava +89 cm, horní Labe +116 cm a Mělník +95 cm korelované statistické příspěvky, které nelze chápat jako nezávislé příčiny. Ridge navíc sčítá standardizované odmocniny průtoků a hladiny, takže přímo nevynucuje zachování vody. Záporné váhy mohou vystihovat trend nebo kompenzovat souběžné vstupy, ale samy o sobě nedokazují fyzikální mechanismus.“ *(Zdroj: `docs/PREZENTACE_7MIN.md`, slajd 4; `src/models/ridge.py`; `docs/POKUSY.md`, pá 19:50.)*

17. **Otázka:** „Proč máme věřit extrapolaci na další rekordní povodeň, když rok 2002 nemáte a ledovou situaci 2006 jste odstranili? Umíte odlišit vadné čidlo od skutečně neobvyklé hydrauliky?“

    **Proč je záludná:** Schopnost lineárně pokračovat za trénovací rozsah nezaručuje správnost při změně fyzikálního režimu.

    **Slabé místo v podkladech:** [docs/DATA.md](C:/Users/danie/Documents/hackathon-2026-prezentace/docs/DATA.md), Starší povodně a kontrola správnosti; `src/data.py::postav`: ledová epizoda je pevně vyřazená a nezávislé doložení její příčiny v podkladech chybí.

    **Doporučená odpověď:** „Pro povodeň 2002 nemáme potřebné hodinové hladiny a v původním tréninku jsou jen dvě události dosahující 3. SPA. Ledovou epizodu jsme vyřadili v rozsahu 82 hodin kvůli hladině až 1 019 cm při průtoku kolem 120 m³/s, ale z nesouladu samotného nelze obecně odlišit chybu měření od změněného vztahu hladiny a průtoku. Při vynechání povodně 2013 předpověděl týmový Ridge na skutečném vrcholu 1 072 cm jen 952 cm. Extrapolaci tedy umíme vypočítat, nikoli zaručit její spolehlivost pro rekord, led nebo změněné koryto.“ *(Zdroj: `docs/DATA.md`; `src/data.py`; `prezentace_dan/grafy/README.md`, G4.)*

18. **Otázka:** „Ukazujete pásmo z 5. a 95. percentilu jako nejistotu. Proč se do údajně devadesátiprocentního pásma při povodni vejde někdy jen 76 % hodnot — a proč podle něj chcete spouštět výstrahy?“

    **Proč je záludná:** Celkové pokrytí ovládané klidnými hodinami může zakrývat nebezpečně malé pokrytí právě během povodní.

    **Slabé místo v podkladech:** [docs/POKUSY.md](C:/Users/danie/Documents/hackathon-2026-prezentace/docs/POKUSY.md), pá 20:40 a so 0:01: pásma vycházejí z tréninkových reziduí, chybí doložená kalibrace pravděpodobnosti překročení SPA.

    **Doporučená odpověď:** „Pásmo je empirické rozmezí tréninkových chyb podle aktuální hladiny, nikoli záruka 90% pokrytí nové povodně. Na validaci pokrývá 89–92 % všech hodnot, ale jen 76–88 % během povodní, na 36 h přibližně 76–78 %. Varování podle horní meze přišlo o 3–4 hodiny dříve, ale přidalo čtyři plané poplachy. Bez další kalibrace je proto můžeme označit za orientační rozmezí; pravděpodobnost překročení konkrétního SPA z něj spolehlivě určit neumíme.“ *(Zdroj: `docs/POKUSY.md`, uvedené dva pokusy; `prezentace_dan/TAHAK_DAN.md`, Pásmo nejistoty.)*

19. **Otázka:** „O 55 % lepší než ‚bude jako teď‘ — ale jste lepší než ČHMÚ nebo alespoň než rozumná předpověď trendu? Co jste přidali profesionální službě?“

    **Proč je záludná:** Velké zlepšení proti snadno porazitelné základní metodě nemusí znamenat přínos proti dostupnému řešení.

    **Slabé místo v podkladech:** [docs/POROZUMENI.md](C:/Users/danie/Documents/hackathon-2026-prezentace/docs/POROZUMENI.md), Jak číst výsledky, a `docs/PREZENTACE_7MIN.md`: historické srovnání s ČHMÚ chybí, přesto prezentace používá silný příslib varování den předem.

    **Doporučená odpověď:** „Proti ČHMÚ převahu doložit neumíme, protože nemáme historické předpovědi se skutečnými časy vydání. Na validaci jsme porovnali také pokračování šestihodinového trendu: mělo 39,4 cm proti 17,1 cm Ridge, ale v Děčíně přidalo 2, 5 a 16 planých poplachů podle horizontu. Testových 22,4 proti 50,2 cm tedy prokazuje přínos proti perzistenci, nikoli proti profesionální službě. Spravedlivé srovnání by vyžadovalo stejné časy vydání a platnosti, události i skutečně dostupná vstupní data.“ *(Zdroj: `docs/POKUSY.md`, pá 19:35; `docs/PREHLED.md`, Finální test; `docs/POROZUMENI.md`.)*

20. **Otázka:** „Říkáte lidem, kam až voda dosáhne. Kdo rozhodne o varování, kdo odpovídá za chybu a kde máte doložené podmínky použití všech dat — nejen ČHMÚ?“

    **Proč je záludná:** Přesná předpověď vodočtu, bezpečné rozhodnutí o varování, správná mapa rozlivu a oprávnění k použití dat jsou čtyři samostatné závazky.

    **Slabé místo v podkladech:** [prezentace_dan/OTAZKY_POROTY.md](C:/Users/danie/Documents/hackathon-2026-prezentace/prezentace_dan/OTAZKY_POROTY.md), otázka 40, výslovně přiznává nedoložený právní výklad; `docs/DATA.md` přiznává neověření rozlivu proti skutečné povodni.

    **Doporučená odpověď:** „Jde o studentský doplňkový nástroj, nikoli ověřený systém pro samostatné rozhodování o varování; provozní odpovědnost a rozhodovací postup nemáme doložené. Statický rozliv má proti modelovým územím DIBAVOD IoU 0,82–0,90, ale nebyl ověřen proti skutečnému rozlivu a neřeší plnou dynamiku ani všechny ochranné stavby. Podklady uvádějí pro ČHMÚ CC BY 4.0, ale u všech dalších zdrojů a konkrétního způsobu nasazení nemáme úplné právní ověření. Uvedení zdroje proto nesmíme prezentovat jako důkaz vyřešené odpovědnosti a všech licenčních podmínek.“ *(Zdroj: `prezentace_dan/OTAZKY_POROTY.md`, otázka 40; `docs/DATA.md`, Rozliv z výškového modelu; `origin/dan-ridge:ridge_dan/ZPRAVA.md`, Data.)*

Nejnebezpečnější je **otázka 6**, protože zpochybňuje nezávislost hlavního důkazu a samotné tvrzení „test jednou“ ji nevyřeší.  
Druhá je **otázka 11**, protože rozpor mezi 27hodinovým předstihem a zastropováním na 24 hodin zasahuje hlavní příběh prezentace.  
Třetí je **otázka 8**, protože adaptivní hledání na stejných událostech oslabuje tvrzení o potvrzeném zlepšení G3/H30 i přes působivé výsledky LOFO.