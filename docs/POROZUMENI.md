# Porozumění

Podklad pro prezentaci a otázky poroty: úloha a výsledky našimi slovy. Kdo něco pochopí nebo dostane odpověď od mentora, doplní příslušnou sekci.

## Úloha vlastními slovy

Co řešíme, pro koho a proč na tom záleží. Dvě tři věty, které řekne kdokoli z nás.

## Pojmy

Odborné výrazy ze zadání a z našeho řešení, vysvětlené jednoduše.

- **„Bude jako teď“** (základ, baseline): každou hodinu se vydá předpověď, že za 24 h bude hladina stejná jako teď. V pondělí v 10:00 je 249 cm, tak na úterý 10:00 předpoví 249 cm. V 11:00 je hladina jiná, tak vydá jinou předpověď. Nakreslené v čase, pro který platí, dají skutečnou křivku posunutou o den doprava: vzestup „ohlásí“ až den poté, co se stal, a nikdy nevaruje předem. Na klidné řece je přesná, při povodni se plete o metr i víc. Každý model ji musí porazit, jinak nemá smysl. Graf `docs/grafy/jako_ted_vysvetleni.png` (Boris 9/2024: 13. 9. ve 12:00 bylo 249 cm, předpověď na další den 249, skutečně 406 cm).

- **Lineární regrese a proč je předpověď v grafu křivka:** s jedním vstupem je to přímka bodům v grafu (vstup na ose x, výsledek na ose y). My máme 98 vstupů, takže je to vážený součet: předpověď = základ + váha₁ × vstup₁ + … + váha₉₈ × vstup₉₈, váhy se naučí jednou a pak jsou pořád stejné. „Přímka“ je vztah mezi vstupy a výsledkem (o 100 m³/s víc v Praze znamená vždycky o stejný kus výš v Děčíně), ne tvar v čase. V grafu povodně je na ose x čas a každou hodinu do stejného vzorce vstoupí jiná čísla z řek, proto výsledek jde nahoru a dolů jako řeka. Jako taxametr: cena = nástupní sazba + sazba × km + sazba × minuty je lineární vzorec, ale ceny jízd za celý den v grafu přímku netvoří. Nakreslené zjednodušeně s jedním vstupem (průtok v Mělníku teď) v `docs/grafy/primka_vysvetleni.png` (`python src/graf_primka.py`): vlevo učení, každá hodina 2006–2018 je bod a přímka se proloží jednou (hladina za 24 h = 111 + 0,41 × průtok v Mělníku), vpravo stejná přímka použitá hodinu po hodině za Borise. Po vrcholu jde jednovstupová přímka na 800 cm, protože nevidí, že voda v Mělníku už nepřibývá a do Děčína dotéká pomaleji; proto skutečný model bere 98 vstupů.

## Proč tahle metoda

Co jsme zvolili, s čím jsme to srovnávali a proč jsme jiné možnosti nevzali.

**Proč zpoždění 0–36 h a horizonty 12, 24, 36 h** (Labe):
- Doba putování vody do Ústí se liší podle stanice a hlavně podle povodně. Z Vraňan šel vrchol jednou 12 h, jindy 45 h. Jedno pevné číslo na stanici by bylo špatně, proto model dostane od každé stanice průtok před 0, 3, 6, 12, 18, 24 a 36 h a sám si najde, které zpoždění je důležité. Z jeho vah pak dobu putování vyčteme.
- Kolik zpoždění je potřeba: nejvzdálenější stanice (Beroun) je od Děčína asi 40 h, nejkratší horizont je 12 h. Voda, která do Děčína přijde za 12 h, prošla Berounem asi před 28 h. Nejstarších 36 h to pokryje i s rezervou na to, že se doba mezi povodněmi mění.
- Proč ne každou hodinu: zpoždění blízko sebe nesou skoro stejnou informaci, jen by přibyly sloupce (444 místo 84). Doba putování navíc kolísá o víc hodin, než je rozestup.
- Proč nejvýš 36 h dopředu: voda, která do Děčína přijde za víc než 40 h, ještě neprotekla žádnou naší stanicí. Je v potocích nebo ještě nespadla. Na to by byly potřeba srážky.
- Pro horizont h pomáhá hlavně stanice, odkud voda teče déle než h. Proto čím dál dopředu, tím dál proti proudu se musíme dívat.

**Proč jen hladina a průtok, a ne srážky, půda, tvar povodí a další faktory povodní:**
- Většina faktorů z učebnice popisuje, jak se z deště stane voda v řece (srážky, nasycenost půdy, půda, les, tvar povodí, metoda SCS-CN). My předpovídáme až další krok, jak voda, která už v řece teče, doteče do Děčína. Průtok změřený v Praze, Mělníku nebo Lounech je výsledek všech těch dějů nad stanicí, déšť, půda i přehrady jsou v něm už započítané. Pro předpověď kratší, než je doba putování (do zhruba 1,5 dne), proto stačí.
- Faktory, které se v čase nemění (plocha a tvar povodí, sklon, půda, geologie, krajinný pokryv, tvar koryta, drsnost), se model nemůže naučit. Na jedné řece se stejnými stanicemi jsou pořád stejné a už jsou ve váhách modelu a v měrné křivce. Měrná křivka je změřená hydraulika vodočtu, totéž, co by Manningova rovnice počítala z tvaru koryta. Hodily by se, kdybychom předpovídali na řece bez měření.
- Už v datech jsou: výchozí průtoky a nasycenost povodí (základní průtok), manipulace na přehradách (měříme odtok pod nimi), soutoky a skládání vln (každá větev zvlášť), zploštění vlny rozlivem (model se ho učí ze zpoždění).
- Chybí a pomohlo by: srážky, sníh a teplota. To, co právě spadlo nebo leží na horách, ještě v řece není. Proto je chyba na 36 h skoro dvojnásobná a povodeň z deště v kraji (8/2010) model nevidí. ČHMÚ má denní srážky, výšku sněhu a index předchozích srážek (API30) od 1946 na asi 1 500 stanicích, hodinové až od 2018 (ověřeno).
- Vyzkoušeli jsme to (pá 20:44): denní srážky, sníh a teplota z 25 stanic za 20 let model nezlepšily (17,1 → 17,4 cm). Ani kdybychom déšť znali den dopředu, zlepšení by bylo jen 0,8 cm. Na 12–36 h je voda z velkých dešťů už v řekách a model ji vidí v průtocích proti proudu.
- Proč déšť nepomáhá, když povodně dělá déšť: déšť je příčina, ale my předpovídáme jen 12–36 h dopředu a na to stačí změřit, co z deště už teče v řekách. Průtok v Praze nebo Přelouči je déšť po tom, co se část vsákla, odpařila nebo zůstala v přehradách, takže je přesnější než samotný déšť. Je to jako s balíkem: co přijde zítra, poznáš líp z toho, že už jede v dodávce, než z toho, kolik lidí si dnes něco objednalo. Boris 9/2024 (`docs/grafy/boris_dest_prutoky_decin.png`): nejvíc pršelo 13.–15. 9., Praha, Přelouč a Mělník stoupaly od 13. 9. a Mělník měl 14. 9. ve 12:00 už 1 080 m³/s (normálně kolem 90). Pršet přestalo 17. 9. ráno a hladina v Děčíně stoupala ještě 36 h, vrchol 649 cm byl 18. 9. v 18:00 UTC. Kdo předpovídal vrchol 24 h předem, už žádný další déšť nečekal, všechna voda byla v řekách. Srážky by pomohly, kdybychom předpovídali dál, než voda teče, tedy na 2–5 dní.
- Nemáme a nedá se rozumně získat: vodní hodnota sněhu, plánované manipulace na přehradách, ledové zátarasy, protržení hrází, ucpání mostů. Poslední tři jsou vzácné a z dat nepředvídatelné, patří do limitů.
- Vzorce SCS-CN a racionální metoda počítají odtok z deště na malých povodích bez měření. Racionální metoda platí pro malá povodí, Labe nad Děčínem má přes 50 tisíc km² a průtok máme změřený.
- Povodně na Labi v Děčíně jsou regionální a sněhové (2006 tání, 2011 tání s deštěm, 2013 a 2024 dlouhé deště). Rozhoduje u nich objem vody z celého povodí, a ten měříme. Přívalové povodně jsou na malých tocích, ne na Labi.

**Proč lineární regrese (Ridge)** (Honza):
- Předpověď je vážený součet vstupů, každá stanice a zpoždění má jednu váhu. Vybrali jsme ji, protože na vynechaných povodních vyšla nejlíp a celá se dá ukázat na jednom obrázku (`docs/grafy/ridge_vahy_decin.png`). „Ridge“ znamená, že se velké váhy mírně penalizují; na našich datech na tom nezáleží (alpha 0,1 až 10 dává stejný výsledek).
- Odmocnina z průtoků: hladina roste s průtokem zhruba jako odmocnina (měrná křivka), takže lineárnímu modelu odmocnina průtoku sedí lépe. Na hladinu ji nedáváme, zkazila vrchol 2006 o metr.
- Učit „změnu hladiny“ místo hladiny je u lineárního modelu totéž (váha u hladiny teď se posune o 1), u stromů ne.

**Proč vyhrála lineární regrese nad ostatními** (shrnutí důkazů, pá 23:52):
- Fyzika je součet. Voda v Děčíně je zhruba Vltava + horní Labe + Ohře, každá posunutá o dobu, než doteče. Vážený součet zpožděných průtoků je přesně tvar lineární regrese, takže se nemusí nic „hledat“. Jediný ohyb, který fyzika potřebuje (měrná křivka, hladina roste s průtokem jako odmocnina), dostane model přes odmocninu z průtoků.
- Velkých povodní je málo. V tréninku jsou dvě nad 3. stupněm (8/2010, 6/2013). Lineární regrese má 98 vah a odhaduje je ze 108 tisíc hodin. Neuronová síť má přes 20 tisíc vah, LightGBM stovky stromů; z pár povodní se naučí i náhodu.
- Musí umět výš, než viděla. LightGBM předpovídá průměry z tréninku a nad nejvyšší viděnou vodu nevystoupá (2013: 823 místo 1 072 cm). Polynom se při vysoké vodě ohne špatným směrem (17,1 → 19,9 a 22,8 cm, `docs/POKUSY.md` pá 23:44). Přímka v trendu pokračuje.
- Ověřeno třikrát: validace 17,1 cm (síť 17,8, LightGBM 23,1, fyzikální 24,8), vícenásobná validace přes 8 povodní 20,1 cm (síť 21,0, LightGBM 22,7, fyzikální 26,7), test 22,4 cm (síť 21,3). Proti „jako teď“ pokaždé o 55–61 % lepší.
- Síť je stejně dobrá v rámci náhody (na testu o 1,1 cm lepší, ve vícenásobné validaci o 0,9 cm horší). Vybrali jsme regresi, protože je jednodušší, má méně chyb ve varování a každou její váhu umíme ukázat a vysvětlit.

## Jak číst výsledky

Co znamená naše metrika, jaké číslo je dobré a proč, s čím ho srovnáváme.

**Výsledky v procentech** (validace: 4 povodně, které modely neviděly, Děčín a Ústí, 12 / 24 / 36 h; `python src/procenta.py ridge mlp lgbm fyzika jako_ted`, graf `docs/grafy/srovnani_procenta.png`):

| Model | Chyba na povodních | O kolik menší než „jako teď“ | Do ±10 cm | Do ±20 cm | Zachycené povodně | Plané poplachy |
|---|---|---|---|---|---|---|
| lineární regrese | 17,1 cm | 61 % | 46 % | 72 % | 100 % (24 z 24) | 0 |
| neuronová síť | 17,8 cm | 60 % | 46 % | 67 % | 100 % (24 z 24) | 1 |
| LightGBM | 23,1 cm | 49 % | 38 % | 61 % | 100 % (24 z 24) | 0 |
| fyzikální | 24,8 cm | 44 % | 31 % | 55 % | 100 % (24 z 24) | 0 |
| „bude jako teď“ | 44,3 cm | 0 % | 15 % | 29 % | 0 % (0 z 24) | 0 |

Do ±20 cm podle horizontu (lineární regrese): za 12 h 88 %, za 24 h 76 %, za 36 h 51 %.

Chyba v procentech výšky hladiny při vodě nad 1. stupněm (lineární regrese / „jako teď“): za 12 h 1,6 / 4,5 %, za 24 h 2,9 / 8,8 %, za 36 h 5,3 / 12,8 %. Do ±30 cm: 96 / 85 / 71 %. Pozor, procenta z výšky hladiny vypadají malá, protože hladina je při povodni 4–9 m. Poctivější je chyba v cm a podíl do ±20 cm.

**Je chyba 9 / 16 / 26 cm hodně?** Ta čísla jsou chyba během povodní, ne v běžné dny. Děčín, validace, lineární regrese:

| | Horizont | Průměrná hladina | O kolik se voda za tu dobu skutečně změní (průměr / nejvíc) | Chyba modelu |
|---|---|---|---|---|
| klidná voda 2019–2020 | 12 h | 168 cm | 7,5 / 75 cm | 4,9 cm |
| | 24 h | 168 cm | 10,4 / 93 cm | 6,9 cm |
| | 36 h | 168 cm | 13,3 / 126 cm | 9,6 cm |
| povodně | 12 h | 425 cm | 18,7 / 122 cm | 7,6 cm |
| | 24 h | 430 cm | 35,1 / 172 cm | 13,6 cm |
| | 36 h | 435 cm | 51,4 / 242 cm | 23,1 cm |

Při povodni voda za 36 h stoupne až o 2,4 m a model se v průměru splete o 23 cm. Stupně povodňové aktivity v Děčíně jsou od sebe 90 a 70 cm (400 / 490 / 560 cm), takže chyba 14 cm na 24 h je menší než vzdálenost mezi stupni. I v klidu se hladina mění o 7–13 cm (jezy, vypouštění přehrad), model se plete o 5–10 cm. (Čísla se trochu liší od `mae_povodne`, tady jsou celá validační okna a jen Děčín.)

Jak to číst:
- „Do ±20 cm“ se počítá jen v hodinách, kdy je voda nad 1. stupněm povodňové aktivity. Na klidné řece je přesná i předpověď „jako teď“, proto ji nepočítáme.
- „Zachycené povodně“: kolikrát model varoval před 2. stupněm dřív, než voda stupeň překročila. 24 = 4 povodně × 2 stanice × 3 horizonty.
- Procenta nejsou „přesnost“ jako u klasifikace. Předpovídáme číslo v cm, takže úspěšnost vyjadřujeme tím, jak často se trefíme do ±20 cm a o kolik menší je chyba než u laťky.

Jsou to dobré výsledky?
- Proti laťce ano: chyba na povodních je o 61 % menší, žádná povodeň propásnutá, varování v průměru 17 h předem místo 0.
- Na 12 h dobré (9 cm, 88 % do ±20 cm), na 24 h použitelné (16 cm), na 36 h slabé (26 cm, jen polovina do ±20 cm).
- Proti profesionální předpovědi ČHMÚ to srovnat neumíme, jejich chyby nemáme. ČHMÚ navíc počítá se srážkami, my ne.
- Validace má jen 4 povodně, rozdíly do 1–2 cm jsou náhoda.

Proč jsou modely tak podobné a dá se to ještě zlepšit?
- Čtyři úplně odlišné přístupy skončily na 17–25 cm. Strop tedy nedělá model, ale informace, kterou mu dáváme. Model, který vidí jen vodu, která už teče, víc nevymáčkne.
- Zprůměrování dvou nejlepších modelů (lineární + síť) dalo 16,9 cm proti 17,1, tedy nic.
- Zbytek chyby je hlavně na 36 h a u povodní z dešťů v kraji (9/2010). Tam voda ještě neteče žádnou naší stanicí. Pomohly by srážky v povodí (historie ČHMÚ a v provozu předpověď srážek), to je další krok, ne lepší model.

## Co model umí a co ne

Limity, na jakých datech by selhal, co jsme nestihli.

- Umí předpovědět na 12 až 24 h z vody, která už teče proti proudu. Neumí déšť, který teprve spadne: proto je 36 h dvakrát horší než 24 h a dál než den a půl by to bez srážek nešlo.
- Vrcholy vyšší, než jaké viděl v tréninku, podhodnocuje (2006: o 20 cm na 875 cm). Lineární model aspoň extrapoluje, stromy ne.
- Doba putování vody se mezi povodněmi mění (Mělník → Ústí 6 až 11 h), model má jednu průměrnou.
- Archivní data ČHMÚ jsou zpětně ověřená. V provozu jsou průtoky při povodni předběžné a chodí se zpožděním, takže naše čísla jsou proti provozu spíš optimistická. Srovnání modelů mezi sebou to neovlivní.

## Otázky pro mentory a odpovědi

Připraveno pá 21:00 (Ondra jde za mentory). Odpověď dopsat pod každou otázku.

1. Předpovídáme hladinu Labe v Děčíně a Ústí na 12–36 h dopředu a varujeme před 2. a 3. stupněm povodňové aktivity. Je to směr, který od úlohy chcete, nebo by vás víc zajímalo něco jiného (sucho, rychlé změny, teplota vody)?
2. Trénujeme na otevřeném archivu ČHMÚ 2006–2025 i se stanicemi mimo kraj (Praha, Mělník, Louny). Data z balíčku se s ním shodují, používáme je jako kontrolu a pro prahy stupňů. Je v pořádku, že jsme sáhli i mimo balíček?
3. S jakým zpožděním ČHMÚ v provozu zveřejňuje hodinové průtoky? A jak moc se předběžné průtoky při povodni liší od ověřených v archivu?
4. Existují historické oficiální předpovědi ČHMÚ pro Děčín (třeba z povodní 2013 nebo 2024), se kterými bychom se mohli srovnat? Jak přesné bývají?
5. Hodnotíme chybu jen během povodní a předstih varování, ne přesnost za celý rok, protože na klidné řece je přesný i odhad „zůstane to stejné“. Je to podle vás správné, nebo chcete jinou metriku?
6. Pro koho má být výstup: krizový štáb, obec, nebo lidi u řeky? Co by na obrazovce chtěli vidět jako první?
7. Ocenili byste v aplikaci data z balíčku za rok 2026 jako „aktuální stav řeky“?

- Hodinové hodnoty ČHMÚ jsou průměry za hodinu a zveřejňují se se zpožděním. S jakým zpožděním jsou v provozu dostupné? Model bere hodnotu z času t jako známou v čase t; v provozu by se předstih zkrátil zhruba o to zpoždění.

## Otázky, které čekáme od poroty

- Proč lineární model a ne neuronová síť? Na povodních, které model neviděl, vyšel nejlíp, nemá se na čem přeučit a každou váhu vysvětlíme fyzikálně.
- Proč jsou některé váhy záporné? Model odečítá hodnotu před pár hodinami od hodnoty teď, tedy počítá trend (stoupá, nebo klesá).
- Proč model pro Ústí používá i Děčín, který je po proudu? Hladina v Děčíně je tatáž voda změřená podruhé o 4 h později, model si tím vyhlazuje šum měření. Je to hodnota známá v čase předpovědi, ne informace z budoucnosti.
- Proč nestačí sledovat, jestli voda stoupá? Pravidlo „stoupla o 40 cm za 6 h“ se plete pětkrát z šesti (`docs/NAPAD_LABE.md`). Model vidí vodu, která do Děčína teprve teče.
- Když víte, že se vlna při povodni zpomalí, proč to model nepoužívá? Zkusili jsme to a nepomohlo to (21,8 vs 22,2 cm, pod hranicí 1 cm). Lineární model má 98 zpožděných hodnot (z každé stanice 7 zpoždění 0–36 h) a dobu doběhu včetně roztažení vlny si z vah najde sám. Zpomalení při velkých povodních nejde spolehlivě změřit – nad 1 500 m³/s je v tréninku jen jedna povodeň (6/2013, 227 h). Podrobnosti v `docs/POKUSY.md` (pá 20:45).
- Jak znáte hladinu, když neznáte šířku a tvar koryta? Šířku potřebujeme jen tam, kde hladinu předpovídáme, tedy v Děčíně a v Ústí, a tam ji model zná z historie. Hladinu ČHMÚ na vodočtu měří přímo a průtok z ní dopočítává, šířku koryta v datech nemáme a nepotřebujeme. ČHMÚ na každém vodočtu několikrát do roka změří průřez koryta a rychlost vody (průtok = rychlost × plocha průřezu) a z toho sestaví měrnou křivku: při jakém průtoku je jaká hladina. Model má 20 let hodin, kdy v Děčíně tekl známý průtok a byla známá hladina (od 76 do 1 072 cm v 6/2013), takže tvar koryta je schovaný v jeho vahách. Mezi stanicemi šířku nepotřebujeme, protože proti proudu bereme průtok v m³/s, a ten na šířce nezávisí: voda, která proteče Mělníkem, za pár hodin doteče do Děčína, jen později a trochu roztažená. Kdy a jak moc roztažená, se model naučil ze zpoždění 0–36 h. Selže, když se koryto změní (ledová zácpa jako v Děčíně 2/2006, kterou jsme z dat vyřadili, bagrování, nová stavba) nebo když voda vystoupí výš než kdy v tréninku.
- Proč nepředpovídáte déšť a nedáte ho do modelu? Zkusili jsme horní mez: model dostal skutečný déšť na 3 dny dopředu, jako by předpověď počasí byla dokonalá. Chyba klesla jen o 1 cm (na 36 h o 1,8 cm) a varování nepřišlo dřív. První nárůst vody vidíme v průtocích proti proudu 12–40 h předem a déšť, který spadne teď, do Děčína většinou doteče až za víc než 36 h. Skutečná předpověď deště se navíc plete. Srážky by pomohly u předpovědi na 2–5 dní nebo na malých řekách (`docs/POKUSY.md`, pá 22:32).
- Nemáte výsledek jen ze šťastně vybrané validace? Ověřili jsme to vícenásobnou validací: každou z 8 povodní 2006–2020 jsme jednou vynechali a model naučili na ostatních. Lineární regrese vyšla 20,1 ± 7,7 cm, síť 21,0, LightGBM 22,7, fyzikální 26,7, „jako teď“ 45,2. Zlepšení proti „jako teď“ 55 %, stejně jako na testu. Chyba víc záleží na povodni (11 až 34 cm) než na modelu (`docs/grafy/krizova_validace.png`).
- Nepřeučil se váš model? Lineární regrese se přeučit může, když má moc vstupů na málo dat. Kontrolovali jsme to: chyba na trénovacích povodních je 19,7 cm a na validačních 15,5 cm (Děčín +24 h), na tréninku tedy není lepší, jak by u přeučeného modelu byla (síť 64-32 měla 5 proti 22 cm). Bez regularizace vyjde totéž, 98 vah se odhaduje ze 108 tisíc hodin. Ridge je pojistka proti velkým vahám, protože sousední zpoždění jsou skoro stejná. Když jsme přidali stovky vstupů (polynom), přeučení se objevilo a model byl horší.
- Proč je ve vahách nejdůležitější hladina v Děčíně teď, když předpovídáte zítřek? Hladina za 24 h je hladina teď plus to, o kolik se za den změní. Velká řeka se za den nezmění o celou svou výšku, voda, která je teď v Děčíně, do zítřka neodteče celá, takže dnešní hladina je výchozí bod (proto je „bude jako teď“ v klidných dnech skoro přesné). Změnu pak model čte z toho, co právě teče proti proudu: Praha teď má velkou váhu, protože voda z Prahy doteče do Děčína za 17 h, tedy ještě v rámci těch 24 h. Voda, která prošla Prahou před 24 h, už je v Děčíně a je obsažená v dnešní hladině, proto starší sloupce váží málo. Oranžové políčko hned vedle modrého (Děčín teď +88, před 1 h záporné) znamená, že model odečítá starší hodnotu od nové a počítá, jestli voda stoupá. Váhy jednotlivých políček nejde číst každou zvlášť, sousední zpoždění a stanice na stejné řece jsou skoro stejná čísla (korelace 0,998) a model si mezi ně váhu rozdělí; čitelnější je součet po řekách (slajd 5).
