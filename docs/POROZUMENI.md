# Porozumění

Podklad pro prezentaci a otázky poroty: úloha a výsledky našimi slovy. Kdo něco pochopí nebo dostane odpověď od mentora, doplní příslušnou sekci.

## Úloha vlastními slovy

Co řešíme, pro koho a proč na tom záleží. Dvě tři věty, které řekne kdokoli z nás.

## Pojmy

Odborné výrazy ze zadání a z našeho řešení, vysvětlené jednoduše.

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
- Vyzkoušeli jsme to (pá 21:15): denní srážky, sníh a teplota z 25 stanic za 20 let model nezlepšily (17,1 → 17,4 cm). Ani kdybychom déšť znali den dopředu, zlepšení by bylo jen 0,8 cm. Na 12–36 h je voda z velkých dešťů už v řekách a model ji vidí v průtocích proti proudu.
- Nemáme a nedá se rozumně získat: vodní hodnota sněhu, plánované manipulace na přehradách, ledové zátarasy, protržení hrází, ucpání mostů. Poslední tři jsou vzácné a z dat nepředvídatelné, patří do limitů.
- Vzorce SCS-CN a racionální metoda počítají odtok z deště na malých povodích bez měření. Racionální metoda platí pro malá povodí, Labe nad Děčínem má přes 50 tisíc km² a průtok máme změřený.
- Povodně na Labi v Děčíně jsou regionální a sněhové (2006 tání, 2011 tání s deštěm, 2013 a 2024 dlouhé deště). Rozhoduje u nich objem vody z celého povodí, a ten měříme. Přívalové povodně jsou na malých tocích, ne na Labi.

**Proč lineární regrese (Ridge)** (Honza):
- Předpověď je vážený součet vstupů, každá stanice a zpoždění má jednu váhu. Vybrali jsme ji, protože na vynechaných povodních vyšla nejlíp a celá se dá ukázat na jednom obrázku (`docs/grafy/ridge_vahy_decin.png`). „Ridge“ znamená, že se velké váhy mírně penalizují; na našich datech na tom nezáleží (alpha 0,1 až 10 dává stejný výsledek).
- Odmocnina z průtoků: hladina roste s průtokem zhruba jako odmocnina (měrná křivka), takže lineárnímu modelu odmocnina průtoku sedí lépe. Na hladinu ji nedáváme, zkazila vrchol 2006 o metr.
- Učit „změnu hladiny“ místo hladiny je u lineárního modelu totéž (váha u hladiny teď se posune o 1), u stromů ne.

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

- Hodinové hodnoty ČHMÚ jsou průměry za hodinu a zveřejňují se se zpožděním. S jakým zpožděním jsou v provozu dostupné? Model bere hodnotu z času t jako známou v čase t; v provozu by se předstih zkrátil zhruba o to zpoždění.

## Otázky, které čekáme od poroty

- Proč lineární model a ne neuronová síť? Na povodních, které model neviděl, vyšel nejlíp, nemá se na čem přeučit a každou váhu vysvětlíme fyzikálně.
- Proč jsou některé váhy záporné? Model odečítá hodnotu před pár hodinami od hodnoty teď, tedy počítá trend (stoupá, nebo klesá).
- Proč model pro Ústí používá i Děčín, který je po proudu? Hladina v Děčíně je tatáž voda změřená podruhé o 4 h později, model si tím vyhlazuje šum měření. Je to hodnota známá v čase předpovědi, ne informace z budoucnosti.
- Proč nestačí sledovat, jestli voda stoupá? Pravidlo „stoupla o 40 cm za 6 h“ se plete pětkrát z šesti (`docs/NAPAD_LABE.md`). Model vidí vodu, která do Děčína teprve teče.
