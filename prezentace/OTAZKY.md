# Otázky poroty

Nejpravděpodobnější otázky po 7 minutách, odpověď na dvě tři věty a kdo odpovídá. Kde je záložní slajd, ukázat ho rovnou (v decku End a šipkou zpět). Delší odpovědi jsou v `docs/POROZUMENI.md` (sekce Otázky, které čekáme od poroty) a celá cesta modelu v `docs/CESTA_MODELU.md`.

Kdo odpovídá: Ondra data, ověřování a výsledky, Honza model jako součet, aplikace a rozliv, Dan modely, srážky a limity, Tobias uživatel a k čemu to je. Když řečník neví, předá Ondrovi.

## Model

**1. Proč lineární regrese a ne neuronová síť?** (Dan, slajd Z1)
Na čtyřech povodních, které model neviděl, vyšla nejlíp: 17,1 cm, síť 17,8, LightGBM 23,1, fyzikální 24,8. Velkých povodní je v tréninku málo, síť s přes 20 tisíci vahami se z nich naučí i náhodu, regrese má 98 vah. A každou váhu umíme ukázat a vysvětlit.

**2. Na testu vyšla síť lépe. Proč jste ji nevzali?** (Ondra, slajd Z8)
Finální model jsme zapsali před testem a podle testu ho neměníme, jinak by test přestal být nezávislý. Síť byla na testu o 1,1 cm lepší, ve vícenásobné validaci o 0,9 cm horší, je to v rámci náhody. Regrese je jednodušší a ve vícenásobné validaci se ve varování pletla méně (1 propásnutá a 3 plané proti 4 a 5 u sítě).

**3. Nepřeučil se váš model?** (Ondra)
Kontrolovali jsme to: v Děčíně na 24 h je chyba na trénovacích povodních 19,7 cm a na validačních 15,5, na tréninku tedy není lepší, jak by u přeučeného modelu byla (síť měla 5 proti 22 cm). 98 vah se odhaduje ze 108 tisíc hodin. Když jsme přidali stovky vstupů (polynom), přeučení se objevilo a model byl horší.

**4. Proč jsou některé váhy záporné?** (Honza, slajd Z6)
Model odečítá hodnotu před pár hodinami od hodnoty teď, tedy počítá trend: stoupá, nebo klesá. Proto je oranžové políčko vždycky hned vedle modrého.

**5. Proč model pro Ústí bere i Děčín, který je po proudu?** (Honza)
Hladina v Děčíně je tatáž voda změřená podruhé o 4 h později, model si tím vyhlazuje šum měření. Je to hodnota známá v okamžiku předpovědi, ne informace z budoucnosti.

**6. Jak znáte hladinu, když neznáte šířku a tvar koryta?** (Honza)
Šířku potřebujeme jen tam, kde hladinu předpovídáme, v Děčíně a v Ústí, a tam ji model zná z 20 let měření: kdy tekl jaký průtok a jaká byla hladina. ČHMÚ hladinu měří přímo a průtok z ní počítá přes měrnou křivku. Proti proudu bereme průtok v m³/s, a ten na šířce koryta nezávisí.

## Data a ověření

**7. Proč jste brali data mimo balíček?** (Ondra, slajd 2)
Balíček má dva roky a stanice v kraji, nejvýš proti proudu je Ústí, 4 hodiny před Děčínem. S ním by model měl chybu 44,6 cm, stejně jako „bude jako teď“, a propásl by polovinu povodní. Archiv ČHMÚ je stejný zdroj, za 2024 a 2025 sedí s balíčkem na centimetr.

**8. Jak jste data připravili?** (Ondra)
Hodinové hladiny a průtoky ČHMÚ 2006–2025, každá hodnota je průměr za hodinu. Zkontrolovali jsme bilanci vody mezi stanicemi, měrné křivky a časy, vyřadili jsme jen 5. až 8. 2. 2006 v Děčíně (hladina 1 019 cm při průtoku 120 m³/s, nejspíš led). Díry nedoplňujeme a z průtoků bereme odmocninu, protože hladina roste s průtokem zhruba jako odmocnina.

**9. Jak víte, že model nepoužívá informace z budoucnosti?** (Ondra, slajd 6)
Dělíme v čase, nikdy náhodně, a kolem validačních povodní vynecháváme z učení 20 dní. Vstupy jsou jen hodnoty změřené do okamžiku předpovědi. Našli jsme dvě pasti, které budoucnost do vstupů pouštěly, doplňování děr a denní srážky, a obě jsme vyřadili.

**10. Nemáte výsledek jen ze šťastně vybrané validace?** (Ondra, slajd 7)
Proto vícenásobná validace: každou z 8 povodní 2006–2020 jsme jednou vynechali a model naučili na ostatních. Chyba 20,1 ± 7,7 cm proti 45,2 u „bude jako teď“, o 55 % méně, stejně jako na testu. Chyba víc záleží na povodni (11 až 34 cm) než na modelu.

**11. Co je „bude jako teď“ a proč se s tím srovnáváte?** (Ondra, slajd Z2)
Předpověď, že za 24 h bude stejně jako teď. Je to nejjednodušší možná předpověď, na klidné řece přesná, při povodni je vždycky o den pozadu. Každý model ji musí porazit, jinak nemá smysl.

**12. Funguje to i na jiné povodni než Boris?** (Ondra, slajd Z5)
Leden 2011 z validace: 3. stupeň hlášen 15 hodin předem. Na testu 2021–2025 model před 3. stupněm varoval pokaždé a ve vícenásobné validaci byl lepší než „bude jako teď“ na každé z 8 povodní.

**13. Kolikrát model propásl povodeň nebo vyhlásil planý poplach?** (Ondra)
Na testu 2021–2025 třetí stupeň zachytil pokaždé. U druhého stupně 17 z 21 případů a propásnuté byly hraniční o pár centimetrů (únor 2024 vrchol 496 cm, hranice 490), plané poplachy tři.

## Limity a provoz

**14. Proč ne srážky?** (Dan, slajd 3 a Z3)
Zkusili jsme horní mez: model dostal skutečný déšť na 3 dny dopředu, jako by předpověď byla dokonalá, a chyba klesla jen o 1 cm. Voda, která přijde za 12 až 36 h, už teče v řekách a vidíme ji v průtocích proti proudu. Srážky by pomohly na 2 až 3 dny u dešťových povodní, jenže archiv starých předpovědí na trénink nemáme.

**15. Proč jen 36 hodin dopředu?** (Dan, slajd Z9)
Z nejvzdálenějších stanic, Berounu a Nespek na Sázavě, doteče voda do Děčína za 23 až 25 h. Voda, která do Děčína přijde později, ještě neprotekla žádnou naší stanicí, je v potocích nebo ještě nespadla. Proto je chyba na 36 h skoro dvakrát větší než na 24 h.

**16. Jak moc se dá předpovědi věřit?** (Honza, slajd Z4)
K předpovědi ukazujeme rozmezí od–do, spočítané z 90 % chyb na tréninku podle výšky vody a ověřené na validaci. Na klidné vodě se do něj skutečnost vejde v 9 z 10 hodin, na povodních, které model neviděl, asi v 8 z 10.

**17. Jak jste na tom proti oficiální předpovědi ČHMÚ?** (Ondra)
V Dnešku ji ukazujeme hned vedle naší. Na starých povodních se srovnat neumíme, historické předpovědi ČHMÚ nemáme. ČHMÚ má navíc předpověď srážek, kterou my nemáme.

**18. Fungovalo by to v provozu?** (Honza)
Aplikace v Dnešku stahuje živá data ČHMÚ a předpověď počítá sama. ČHMÚ zveřejňuje hodinu až po jejím konci, data jsou stará 1 až 3 h a o to se předstih zkrátí. Průtok v Mělníku a Nymburce operativně nezveřejňuje, dopočítáváme ho z bilance vody (v archivu odchylka 0,5 a 8 %).

**19. Je rozliv v mapě hydraulický model?** (Honza, slajd 8 a Z7)
Není. Výška terénu z ČÚZK proti výšce hladiny, ověřená proti úřední mapě záplavových území: při pětileté vodě shoda 0,89. Zdi a hráze pod rozlišením terénu nevidí.

**20. Komu to pomůže a co byste dělali dál?** (Tobias, dál Dan)
Povodňové komisi města, hasičům a lidem u řeky: den navíc znamená odvézt auta, postavit pytle a vyklidit sklepy. Dál předpověď srážek na 2 až 3 dny, víc stanic proti proudu a dvoustupňové varování, nejdřív předběžná výstraha podle horní meze rozmezí, pak ostrá podle předpovědi.

**21. Proč nepoužíváte vlhkost, tlak a vítr?** (Dan, slajd 3)
Zkusili jsme je: s vlhkostí 17,2 cm, s tlakem 17,0, s větrem 17,0 proti 17,1 bez nich, a i kdybychom je dokonale znali den předem, vyjde 17,0. Do řeky vodu nepřidají, jsou jen náznak, že bude pršet, a ani dokonale známý déšť nepomohl o víc než 1 cm. Vítr hladinu zvedá u moře nebo jezera, ne v řece.

**22. Proč neukazujete živé demo?** (Honza)
Sedm minut je málo a demo závisí na Wi-Fi a na tom, jestli ČHMÚ zrovna zveřejnil data, proto je na slajdu 8 mapa rozlivu a snímek aplikace z dnešního rána je v záloze Z10. Web field-zero.netlify.app je otevřený v druhé kartě, rádi ho teď ukážeme: dnešek, mapu rozlivu a přehrávání povodní.

**23. Proč je ve vahách nejdůležitější hladina v Děčíně teď, když předpovídáte zítřek?** (Ondra, slajd Z6)
Hladina zítra je hladina teď plus to, o kolik se za den změní, dnešní voda do zítřka neodteče celá. Změnu model čte z toho, co právě teče proti proudu: voda z Prahy doteče do Děčína za 17 h, proto váží Praha teď, ne Praha před 24 h, ta už je v dnešní hladině Děčína. Záporné políčko hned vedle kladného je výpočet trendu, jestli voda stoupá.

**24. Když je to lineární regrese, proč je předpověď v grafu křivka?** (Ondra, slajd Z11)
Přímka je vztah mezi vstupy a hladinou, naučí se jednou: zjednodušeně s jedním vstupem hladina za 24 h = 111 + 0,41 × průtok v Mělníku. Každou hodinu do ní dosadíme nová měření a vyjde jeden bod; body za sebou v čase dají křivku. Skutečný model dělá totéž s 98 vstupy najednou (vážený součet, slajd 5).

**25. Jak vypadá ta přímka, když je vstupů 98?** (Ondra, slajd Z12)
Proti jednomu vstupu ji nakreslit nejde, potřebovala by 98 os. Když na osu x dáme celý vážený součet (předpověď) a na osu y skutečnost, je to zase přímka a body leží těsně u úhlopříčky: na validaci průměrná chyba 7,5 cm proti 26,5 cm s jediným vstupem.

## Jak model počítá a jak se učí

**26. Jak přesně vypadá vzorec modelu?** (Ondra)
Hladina za h hodin = bias + váha₁ × vstup₁ + … + váha₉₈ × vstup₉₈. Vstupy: průtok na 12 stanicích (Děčín, Ústí a 10 proti proudu) teď a před 3, 6, 12, 18, 24 a 36 h (84 čísel) a hladina v Děčíně a Ústí teď a před 1, 2, 3, 6, 12 a 24 h (14 čísel). Každý zvlášť pro Děčín a Ústí a 12, 24 a 36 h, tedy 6 sad vah. Ne každou hodinu, protože sousední hodnoty jsou skoro stejná čísla (průtok v Praze teď a před 3 h má korelaci 0,998).

**27. Jak se model učí?** (Ondra)
Tři kroky v `src/models/ridge.py`: 1) z průtoků se vezme odmocnina, protože hladina roste s průtokem čím dál pomaleji (koryto se rozšiřuje); 2) každý vstup se převede na „o kolik obvyklých výkyvů je nad průměrem“ (StandardScaler), aby šly váhy srovnat; 3) metoda nejmenších čtverců s malou pokutou za velké váhy (Ridge, alpha = 1) najde bias a 98 vah. Krok 3 je jedna soustava 99 rovnic o 99 neznámých, počítač ji vyřeší přesně za 0,4 s ze 108 tisíc hodin let 2006–2018. Nic se nezkouší ani neladí po krůčcích, trénink je právě ten výpočet.

**28. Proč čtverce chyb?** (Ondra)
Obyčejné rozdíly by se odečetly (+50 a −50 dá 0). Čtverec trestá velkou chybu víc (jedna chyba 100 cm je 10 000, dvě po 50 cm jen 5 000), a při povodni nám jde hlavně o to, aby model neudělal obří chybu. A pro čtverce existuje přesný vzorec. Jestli se čtverce sčítají, nebo průměrují, je jedno, nejlepší přímka vyjde stejná. Výsledky hlásíme jako průměrnou chybu v cm bez čtverců, protože ta se dá říct člověku.

**29. Jak se spočítá sklon a bias?** (Ondra, slajd Z11)
S jedním vstupem: sklon = Σ (x − x̄)(y − ȳ) / Σ (x − x̄)², bias = ȳ − sklon × x̄, kde x je průtok v Mělníku v nějakou hodinu, y hladina v Děčíně o 24 h později a pruh nahoře znamená průměr. Sklon říká, o kolik je v průměru zítra v Děčíně víc než obvykle, když je dnes v Mělníku víc než obvykle; bias posune přímku středem mraku bodů. Ze 20 let vyjde hladina za 24 h = 111 + 0,41 × průtok v Mělníku. Vzorce plynou z toho, že součet čtverců chyb tvoří „mísu“ a její dno je tam, kde je derivace nulová. S 98 vstupy je to stejný postup, jen místo dvou rovnic 99.

**30. Co je Ridge a proč pokuta za velké váhy?** (Ondra)
Ridge je lineární regrese, která k součtu čtverců chyb přičte alpha × součet čtverců vah. Sousední vstupy jsou skoro stejná čísla a bez pokuty by si mezi ně model mohl rozdělit obří váhy, které se navzájem odečtou (+500 a −490). S alpha 1 klesne největší váha ze 104 na 88 a přesnost se nezmění (bez pokuty i s ní 15,5 cm u Děčína na 24 h); alpha 100 už přesnost zhorší (16,1 cm).

**31. Čím se učení liší od neuronové sítě?** (Ondra)
Lineární regrese má přesný vzorec, spočítá váhy jedním výpočtem a vyjdou vždycky stejně. Síť vzorec nemá, protože mezi vrstvami jsou ohyby: začne s náhodnými vahami, spočítá, kterým směrem chyba klesá, posune všechny váhy o malý krok a opakuje to tisíckrát (gradientní sestup). Proto trvá minuty, výsledek trochu záleží na náhodném začátku (seed) a s 20 tisíci vahami na dvě velké povodně se snadno přeučí. Pokutu za velké váhy můžou mít obě, naše síť ji měla taky.

**32. Proč nepoužijete předpověď počasí, když na 3 dny pomůže?** (Dan, slajd 9 a Z3)
Budoucí déšť nezná nikdo, existuje jen předpověď počasí, která se plete hlavně v tom, kde a kolik naprší. Číslo 16,1 cm je myšlenkový pokus se skutečně naměřeným budoucím deštěm, tedy horní mez, kterou žádná předpověď nedá. Na 12–36 h pomohl i dokonalý déšť jen o 1 cm, protože voda, která přijde do 36 h, už teče řekou. Velký přínos byl jen na 72 h a jen u jediné dešťové povodně ve validaci (9/2010: 79,7 → 48,0 cm, −40 %); 72 h je přitom úplně jiná úloha, chyba je tam kolem 78 cm proti 16 cm na 24 h. A hlavně: aby se model naučil s předpovědí pracovat, potřebuje archiv starých předpovědí, tedy co předpověď říkala v každé hodině 2006–2018. Ten volně není (Open-Meteo má historické předpovědi až od 2021–2022). Kdybychom model učili na skutečném dešti a pak mu dávali předpověď, věřil by jí jako dokonalé a ověřit by to nešlo. Proto je to v „co dál“.

**33. Co přesně model potřebuje k učení a k předpovědi?** (Dan)
Jen hodinová měření ČHMÚ: průtok na 12 stanicích (Vltava s Berounkou a Sázavou, horní Labe s Jizerou, Ohře, Mělník, Ústí, Děčín) teď a před 3 až 36 h a hladinu v Děčíně a Ústí teď a před 1 až 24 h. K učení navíc hladinu v Děčíně a Ústí o 12, 24 a 36 h později, tu se model učí předpovídat. Nic dalšího: žádné počasí, šířku koryta ani tvar povodí.

**34. Předpovídáte jen povodně, které přitečou odjinud, a ne ty z deště přímo v kraji?** (Dan)
Ano, to je hlavní limit. Model vidí vodu, až když teče některou z našich stanic. Velké povodně na Labi v Děčíně (2006, 2011, 2013, 2024) přitekly z celého povodí, tedy z Vltavy, horního Labe a Ohře, a ty vidí den předem. Když silně zaprší přímo v kraji, voda přiteče přítoky, které neměříme: Ploučnice ústí do Labe kousek nad vodočtem v Děčíně, Bílina v Ústí. Je to vidět na povodni 8/2010 z deště v Lužických horách: ve vícenásobné validaci měla druhou největší chybu (28,6 cm) a nejmenší zlepšení proti „jako teď“ (34 %). Přívalové povodně na malých potocích model nevidí vůbec, to je jiná úloha, potřebuje srážky a předpověď počasí.

## Rozliv v mapě: jak počítáme, kam voda dojde

**35. Jak přesně počítáte, kam voda při dané hladině dojde?** (Honza, slajd 8 a Z7)
Porovnáním výšek, nic se tu neučí (`app/rozliv_dem.py`):
1. Výška hladiny u vodočtu v metrech nad mořem = nula vodočtu + hladina. Nula je v Děčíně 120,07 m n. m., v Ústí 130,94 m n. m. Při 707 cm v Děčíně (pětiletá voda) je hladina 120,07 + 7,07 = 127,14 m n. m.
2. Proti proudu hladina stoupá se sklonem 0,44 m/km: výška hladiny v místě = výška u vodočtu + 0,44 × vzdálenost od vodočtu proti proudu v km. 2 km nad vodočtem je to 127,14 + 0,88 = 128,02 m n. m. Sklon jsme změřili z našich dat: rozdíl hladin Ústí a Děčín (o 4 h později) na 25,4 km řeky, medián 0,438 m/km, skoro stejný při nízké i velké vodě.
3. Terén: výškový model ČÚZK DMR 5G z leteckého laserového skenování, bod každé 2 m, čtverec 6 × 6 km kolem vodočtu.
4. Zaplavený je bod, který je níž než hladina v tom místě **a zároveň je s korytem spojený** přes jiné zaplavené body (8 sousedů). Prohlubeň za kopcem, kam se voda nemá jak dostat, zaplavená není.
5. V Ústí je 1,7 km nad vodočtem jez Střekov, nad ním držíme hladinu aspoň na úrovni zdrže 141,55 m n. m.
6. Spočítáno předem pro hladiny po 10 cm (Děčín 300 až 1 250 cm), aplikace vezme nejbližší k předpovědi.

**36. Jak víte, že to sedí?** (Honza, slajd 8)
Porovnali jsme to s oficiálními záplavovými územími (DIBAVOD, VÚV TGM), která vznikla hydraulickým modelem, pro pětiletou, dvacetiletou a stoletou vodu. Shoda (průnik děleno sjednocením) je 0,82 až 0,90, například Děčín Q5: náš rozliv 167 ha, úřední 183 ha, společných 165 ha. Rozdíly: my navíc zatékáme do údolí přítoků (hlavně Bílina v Ústí), úřední mapa má navíc úzké pásy podél břehů a kus údolí Ploučnice.

**37. Berete v úvahu proudění, zdi, mosty nebo kanalizaci?** (Honza)
Ne, je to statický rozliv: zaplaví všechno pod hladinou, co je spojené s korytem, jako by voda měla dost času se rozlít. Nepočítá rychlost proudění ani objem vlny, takže krátká špička může ve skutečnosti zaplavit méně. Protipovodňové zdi, mobilní stěny a valy užší než 2 m v terénu nejsou, mosty a podjezdy DMR nemá. Kanalizace v modelu není vůbec: voda se ve skutečnosti může dostat za zeď zpětně kanály, nebo naopak odtéct, to statický model neukáže. Přítoky (Ploučnice, Bílina) mají vlastní průtok, model jim dává jen hladinu Labe. Na orientační mapu „kam až voda dojde“ to stačí, shoda s úřední mapou je 82 až 90 %; na stavbu hrází ne.

**38. Učili jste i na povodních z deště v kraji? Nekazí to model?** (Ondra)
Učili jsme na všech hodinách 2006–2018, tedy na klidu, na povodních, které přitekly z povodí, i na povodni 8/2010 z deště v kraji. Vybírat jen „hezké“ povodně by bylo podvádění: v provozu předem nevíte, jaká povodeň přijde, a model by pak vypadal lepší, než je. Na povodni z deště v kraji se model nic špatného nenaučí, jen tam nemá z čeho předpovídat, protože ta voda neteče žádnou naší stanicí; těch hodin je málo, takže váhy skoro nezmění. Ověřovali jsme taky na všech povodních, i na 8/2010, takže −55 % už v sobě má i ty, kde je model slabší. Model na ni reaguje přes hladinu v Děčíně a Ústí teď, tedy později, ale i tak o 34 % lépe než „jako teď“. Zlepšit by to šlo stanicí na Ploučnici jako dalším vstupem, nebo srážkami v reálném čase.

## K čemu to je

**39. Den předem je přece každému jasné, že přijde povodeň. K čemu je model, který chybu sníží jen ze 44 na 17 cm?** (Ondra, slajd 7)
Těch 44 a 17 cm je průměr přes celé povodňové okno (7 dní před vrcholem a 5 po), kde se hladina většinu času mění pomalu. Rozdíl je vidět ve chvíli, kdy se rozhoduje. Boris, předpověď vydaná 14. 9. 2024 v 11:00 na 15. 9. v 11:00:

| | předpověď | co by to znamenalo |
|---|---|---|
| zítra jako dnes | 389 cm | pod 1. stupněm, žádné varování |
| náš model | 577 cm | 3. stupeň, varovat |
| skutečnost | 551 cm, 3. stupeň o 3 h později | |

Proto je hlavní výsledek varování, ne centimetry: na validaci model zachytil předem všech 24 překročení 2. a 3. stupně a neudělal žádný planý poplach, „zítra jako dnes“ nezachytil ani jedno. Že hodně prší, ví každý, ale ne jestli Děčín dosáhne 450, nebo 650 cm a kdy; mezi 2. a 3. stupněm je jen 70 cm a podle toho se staví mobilní stěny a evakuuje. Spousta silných dešťů povodeň neudělá a povodně v Děčíně často přitečou odjinud nebo z tání sněhu (2006). Pravidlo „voda stoupla o 40 cm za 6 h“ se v našich datech pletlo pětkrát z šesti.

**40. Proč nepředpovídáte na týden dopředu?** (Dan, slajd 9 a Z9)
Z řek to fyzikálně nejde: z nejvzdálenější stanice doteče voda do Děčína za 25 h, voda na týden dopředu je ještě v mracích. Na delší předpověď je potřeba předpověď počasí a ta je na 5 až 7 dní u srážek hodně nejistá; i ČHMÚ, které ji má, vydává předpověď hladiny pro Děčín jen na pár dní dopředu a evropské systémy na týden dávají jen pravděpodobnostní upozornění pro velké oblasti, ne centimetry pro Děčín. Nepřevrátili jsme předpověď povodní, ČHMÚ pro Děčín předpovídá už dnes a 24. 10. ráno vyšlo skoro stejně jako my (94 a 90 cm). Naše hodnota je, že je to z otevřených dat, poctivě ověřené třikrát, vysvětlitelné do posledního čísla, s mapou rozlivu a s otevřeně řečenými limity.

