# Deník týmu

Rozhodnutí, změny postupu a problémy, chronologicky. Nový záznam na konec, nic nepřepisovat. Git záznamy z různých větví spojí sám.

```
## pá 18:40 · Ondra
- Co: co se rozhodlo nebo změnilo
- Proč: důvod jednou dvěma větami
- Problém: co nefunguje nebo je špatně a jak to řešíme (jen když je)
- Otázka pro mentory: (jen když je)
```

Po každém dokončeném kusu práce rozbor, aby ho pochopil i ten, kdo u toho nebyl:

```
## pá 19:20 · Dan · Rozbor: první model
- Co jsme udělali:
- Jak to funguje, jednoduše:
- Proč tak a ne jinak:
- Výsledek a co znamená:
- Slabiny a co může být špatně:
- Otázka poroty a odpověď:
```

## pá 19:20 · Ondra
- Co: jdeme rovnou na Labe, ne na malé řeky. Každý zkusí jiný model na stejném úkolu: Tobias fyzikální model, Honza lineární regresi, Dan LightGBM, Ondra neuronovou síť. Zadání pro všechny je v `docs/UKOL_MODELY.md`, srovnání ve 21:00.
- Proč: výsledek, který ukážeme, je na Labi, a model vybraný na malé řece by se pro Labe musel vybírat znovu. Srovnání čtyř přístupů je samo o sobě obsah prezentace.
- Společný základ je hotový: tabulka 2006–2025 (`data/external/labe_hodinove.parquet`), vstupy (`src/features.py`), rozdělení a vyhodnocení (`src/evaluate.py`), spouštění (`src/porovnej.py`), základ „bude jako teď“.
- Problém: mezi 2016 a 2020 nebyla povodeň, takže validace nemůže být jen poslední roky před testem. Validujeme na čtyřech vynechaných povodních a klidných letech 2019–2020.

## pá 19:20 · Ondra · Rozbor: společný základ a první srovnání
- Co jsme udělali: jedna tabulka pro všechny, stejné rozdělení a vyhodnocení, základ „bude jako teď“ a rychlá kontrola celého řetězce lineárním modelem.
- Jak to funguje, jednoduše: v každé hodině vezmeme hladiny v Děčíně a Ústí a průtoky na 12 stanicích teď a před pár hodinami a model z nich odhadne hladinu za 12, 24 a 36 h.
- Proč tak a ne jinak: hodnotíme hlavně chybu během povodní a varování před 2. a 3. stupněm, protože na klidné řece je skoro dokonalá i předpověď „bude jako teď“.
- Výsledek a co znamená: Děčín za 24 h, chyba na povodních: „jako teď“ 44,4 cm, lineární model 15,5 cm. Lineární model varoval před 2. stupněm v průměru 15,5 h předem, nic nepropásl a neměl planý poplach. „Jako teď“ propásl všechny.
- Slabiny a co může být špatně: ve validaci jsou jen 4 povodně, čísla berte jako směr. Odmocnina na hladinu (místo jen na průtok) zkazila vrchol 2006 o metr, pozor na to v každém modelu.
- Otázka poroty a odpověď: „Proč netestujete na náhodně vybraných hodinách?“ Sousední hodiny jsou skoro stejné, model by je znal z tréninku a výsledek by byl falešně dobrý. Proto dělíme v čase a kolem validačních povodní vynecháváme 20 dní.

## pá 19:30 · Ondra
- Co: zkontroloval jsem správnost dat (shoda s balíčkem pořadatelů, bilance vody mezi stanicemi, měrné křivky, časy, odlehlé hodnoty). Data jsou v pořádku, nic se neměnilo. Podrobnosti v `docs/DATA.md`, sekce Labe.
- Co: do zadání modelů přibyla pravidla, jak dlouho iterovat (jedna změna s důvodem, zlepšení aspoň o 1 cm v `prumer_povodne`, konec po 3 neúspěšných variantách, 10 variantách nebo ve 20:50).
- Proč: validace má jen 4 povodně, nekonečné ladění by našlo variantu, která na nich vyjde náhodou dobře.

Následující záznamy jsou doplněné zpětně (pá 19:35) podle commitů, ať je vidět celý postup od výběru úlohy.

## pá 17:10 · Ondra
- Co: zvažovali jsme úlohu Ovzduší, sepsali tři pojetí (předpověď znečištění, otisky zdrojů, měřicí síť) a spárovali stanice ovzduší s meteostanicemi ČHMÚ.
- Zjištění: inverze zhruba zdvojnásobí PM10 v Ústí. Labe a ovzduší v Děčíně spolu nesouvisejí, společná příčina je roční období a počasí (`docs/DATA.md`, sekce Ovzduší).

## pá 17:33 · Ondra
- Co: zkusili jsme Labe s historickými daty ČHMÚ ze stanic nad krajem. První lineární model předpovídá hladinu v Děčíně na 12 a 24 h.
- Proč: balíček má nejvýš Ústí (4 h před Děčínem) a jedinou povodeň. Bez dat proti proudu a bez historie nejde předpovídat dál než pár hodin a nejde nic ověřit.
- Problém: v Děčíně je 5.–7. 2. 2006 chybná hladina (1 019 cm při 120 m³/s). Vyřazeno.

## pá 17:46 · Ondra
- Co: model otestovaný na šesti velkých povodních, každá vynechaná z tréninku i s 20 dny kolem. Chyba zhruba poloviční proti „jako teď“ a varování před 3. stupněm 12–29 h předem.
- Rozhodnutí: lineární model místo LightGBM. LightGBM u povodně 2013 předpověděl vrchol 823 cm místo 1 072, protože stromy neumí víc, než viděly.
- Co: ukázali jsme, proč nestačí pravidlo „stoupající voda = povodeň“: dává plané poplachy.

## pá 18:00 · Ondra
- Co: vybrali jsme úlohu Labe místo Ovzduší.
- Proč: měřitelný přínos (chyba poloviční, varování o den dřív), fyzikálně vysvětlitelný model a jasný uživatel (město a lidé u řeky). U Ovzduší jsme podobně silný a ověřitelný výsledek neměli.

## pá 18:20 · Ondra
- Problém: při stahování dat ČHMÚ došlo místo na disku, 13 souborů zůstalo useknutých. Smazali jsme je a stáhli znovu. Stahování teď jde přes dočasný soubor, takže se to nemůže opakovat.

## pá 18:36 · Ondra
- Co: přidali jsme stanice na všech třech větvích, které do kraje přitékají (Vltava, horní Labe, Ohře), v několika vzdálenostech.
- Zjištění: čím dál dopředu chceme předpovídat, tím dál proti proudu se musíme dívat. Na 12 h stačí blízké stanice, na 36 h pomáhá každá další vrstva.

## pá 18:44 · Ondra
- Co: porovnali jsme, jestli stačí jen data z kraje (jako balíček), nebo je potřeba stanice proti proudu a historie.
- Zjištění: samotný balíček funguje (43 proti 58 cm), ale nedá se na něm ověřit. Stanice proti proudu pomohly víc než 20 let historie. Nejlepší je obojí (24 cm).

## pá 18:52 · Ondra
- Co: rozhodli jsme, že začneme rovnou na Labi, ne na malých řekách. Každý vyzkouší jiný model, malé řeky budou jen druhá zkouška.
- Proč: na malých řekách voda doteče za 0–7 h a rozhoduje déšť, je to jiný problém. Model vybraný tam by se pro Labe musel vybírat znovu.

## pá 19:40 · Ondra
## pá 19:35 · Honza
- Problém: `src/porovnej.py` na Windows spadne při ukládání JSON (`UnicodeEncodeError`, výchozí kódování cp1252). Obcházím to proměnnou `PYTHONUTF8=1`, soubor neměním. Oprava pro Ondru: `write_text(..., encoding="utf-8")`. Dan na Windows narazí na totéž, zapsáno do Stavu.

## pá 19:50 · Honza · Rozbor: lineární regrese (Ridge)
- Co jsme udělali: lineární model `src/models/ridge.py` pro Děčín a Ústí na 12, 24 a 36 h, k tomu varianty (síla regularizace, změna hladiny jako cíl, výběr stanic podle horizontu), graf vah a graf dvou povodní.
- Jak to funguje, jednoduše: předpověď je vážený součet. Každá stanice a každé zpoždění má jednu váhu, model vstupy vynásobí a sečte. Průtoky bere jako odmocninu (hladina roste s průtokem zhruba jako odmocnina), hladiny nechává. Váhy si našel z let 2006–2018.
- Proč tak a ne jinak: jediný druh modelu, u kterého jde ukázat celou rovnici na jednom obrázku, a v kontrole řetězce vyšel nejlíp. Varianty jsme zkoušeli po jedné a s důvodem, žádná nezlepšila průměrnou chybu na povodních o 1 cm, tak zůstala nejjednodušší.
- Výsledek a co znamená: chyba na povodních průměrně 17,1 cm proti 44,3 cm u „jako teď“ (6 kombinací), Děčín +24 h 15,5 cm. Varování před 2. stupněm 11–37 h předem, nic nepropásnuto, žádný planý poplach. Chyba na tréninku a na validaci je stejná, přeučení není.
- Slabiny a co může být špatně: 36 h je skoro dvakrát horší než 24 h, protože ta voda ještě neteče ani Prahou a srážky nemáme. Vrcholy nad rámec tréninku (2006, 875 cm) model podhodnotí o 20 cm. Model pro Ústí hodně používá hladinu v Děčíně, který je po proudu: je to druhé měření téže vody, ne únik z budoucnosti, ale porota se zeptá. Vstup z času t bereme jako známý v čase t; ČHMÚ ale zveřejňuje hodinové průměry se zpožděním, v provozu by model měl vstupy asi o hodinu starší, čísla na validaci se nemění, jen by se zkrátil předstih.
- Otázka pro mentory: s jakým zpožděním jsou hodinová data ČHMÚ v provozu dostupná?
- Otázka poroty a odpověď: „Proč lineární model a ne něco chytřejšího?“ Protože na povodních, které model neviděl, vyhrál (15,5 cm proti 50 cm u stromů v kontrole řetězce), nemá se na čem přeučit a každou váhu umíme vysvětlit fyzikálně: průtok v Praze teď je hladina v Děčíně za den.

## pá 20:00 · Ondra
- Co: nezávislá kontrola společného řetězce (únik dat, rozdělení, vyhodnocení, data proti surovým souborům) dopadla „platí“. Opravili jsme, co našla:
  - validační okna na 16 dní, jinak u Děčína +36 h vypadla povodeň 2006 z varování,
  - předstih varování je nejvýš horizont a přibyl `bias_povodne`, protože soustavné nadhodnocování dřív předstih uměle zlepšovalo,
  - předpověď s NaN shodí běh místo tichého vynechání,
  - data se už nedoplňují interpolací (díry v nich nejsou a doplňování bralo hodnotu z budoucnosti), chyba v Děčíně z 2/2006 vyřazená až do 8. 2. dopoledne,
  - výsledky si ukládají otisk verze dat a vyhodnocení a `--prehled` staré verze nemíchá s novými.
- Proč: všichni čtyři porovnávají modely na stejném řetězci, chyba v něm by zkreslila všechno. Kontrolní hodnota „jako teď“ (44,4 cm) se nezměnila.
- Dopad: výsledky spočítané před touto opravou `--prehled` ignoruje. Modely je potřeba pustit znovu, srovnání ve 21:00 děláme na jednom počítači.

## pá 20:00 · Ondra · Rozbor: neuronová síť
- Co jsme udělali: malá neuronová síť (dvě vrstvy, 128 a 64 neuronů), čtyři varianty podle pravidel iterace.
- Jak to funguje, jednoduše: síť je hodně lineárních regresí poskládaných za sebou s ohyby mezi nimi, takže umí i zakřivené vztahy. Učí se, o kolik hladina za h hodin stoupne nebo klesne.
- Proč tak a ne jinak: chtěli jsme zjistit, jestli složitější model přidá něco proti lineární regresi. Data jsou malá, stačí procesor.
- Výsledek a co znamená: na povodních 17,8 cm proti 44,3 cm u „jako teď“, chyba menší o 60 %. Ze 24 nástupů povodní (4 povodně × 6 kombinací cíle a horizontu) žádný nepropásla, jeden planý poplach. Když je voda nad 1. stupněm, vejde se do ±20 cm 90 % předpovědí na 12 h, 58–70 % na 24 h a 46–51 % na 36 h („jako teď“: 51 %, 22–24 %, 12–14 %).
- Slabiny a co může být špatně: síť se snadno přeučí, na povodních pořád podhodnocuje (o 5–13 cm na 24 a 36 h), validace má jen 4 povodně a hůř se vysvětluje než lineární model.
- Otázka poroty a odpověď: „Proč nepoužijete rovnou tu neuronovou síť?“ Je zhruba stejně dobrá jako lineární model, ale hůř se vysvětluje a víc kolísá podle náhody. Když je jednodušší model stejně dobrý, bereme jednodušší.
## pá 19:48 · Tobias · Rozbor: fyzikální model
- Co jsme udělali: model, který se skoro nic neučí. Vezme průtok v cíli teď a přičte, o kolik víc vody mezitím přitekla Vltavou, Labem a Ohří, posunuté o dobu putování. Průtok pak převede na hladinu měrnou křivkou.
- Jak to funguje, jednoduše: co teď teče v Praze, bude za 18 h v Děčíně. Z dat jsme změřili, kolik hodin voda putuje z každé stanice (`docs/grafy/fyzika_vetve.png`), a z 13 let měření, jaká hladina odpovídá jakému průtoku (`docs/grafy/fyzika_merna_krivka.png`).
- Proč tak a ne jinak: je to fyzikální základ, se kterým se učené modely srovnávají, a celý jde vysvětlit na jednom obrázku. Učí se jen doby putování a křivku, přeučit se nemá jak (chyba na tréninku je dokonce vyšší než na validaci).
- Výsledek a co znamená: `prumer_povodne` 24,8 cm proti zhruba 44 cm u „jako teď“, Děčín +24 h 22,5 cm. Žádná propásnutá povodeň, žádný planý poplach, před 2. stupněm varuje 11–23 h předem. Třetí vrstva stanic (Beroun, Sázava, Přelouč) zlepšila 36 h o 4 cm. Lineární modely jsou lepší (Dan Ridge 17,1 cm).
- Slabiny a co může být špatně: doby putování jsou jedno pevné číslo, ale při každé povodni jsou trochu jiné. Co ještě nikdo nezměřil, model považuje za neměnné, takže při stoupání podhodnocuje vrcholy, nejvíc na 36 h (38 cm). Před vrcholem 2006 krátce přestřelil o 50 cm. Povodeň z lokálních dešťů (srpen 2010) bez předpovědi srážek nevidí. Přítoky v kraji podle Ondry chybu nevysvětlují, dají jen 2–13 % vody.
- Otázka poroty a odpověď: „Proč je fyzikální model horší než lineární regrese, když fyzika platí?“ Fyzika tu má zjednodušení: jednu dobu putování a předpoklad, že co nebylo změřeno, se nezmění. Lineární model se z dat naučí i to, že stoupající voda proti proudu ještě dál stoupá, a jakou váhu má která stanice. Fyzikální model je proto laťka a vysvětlení: ukazuje, že učený model nedělá nic magického, jen tuhle fyziku zpřesňuje.

## pá 20:15 · Honza
- Co: aplikace `app/app.py` běží s modelem Ridge. Obrazovka „Teď“: hladina teď, předpověď za 12 / 24 / 36 h, stupně povodňové aktivity barevně, věta pro laika (co teče Prahou a Mělníkem) a graf posledních 3 dnů s předpovědí. Obrazovka „Jak dobře to funguje“: validační povodeň, skutečnost proti modelu a „jako teď“, tabulka chyb z `results/`. Přehrávání historie, výchozí okamžik 15. 1. 2011 9:00.
- Proč: kontrolní bod 21:00 chce celý řetězec od dat po aplikaci. Model se vybírá až ve 21:00, proto aplikace načítá kterýkoli `models/<model>_<cil>_<h>.joblib` a model se volí v menu; Ondrův finální model se jen přidá.
- Co dál: 3D mapa povodí (`app/mapa.py`, zadání `docs/UKOL_APLIKACE.md` bod 8), odhad nejistoty předpovědi, screenshoty a záložní video.
## pá 20:15 · Ondra · Rozbor: srovnání čtyř modelů
- Co jsme udělali: každý z nás vyzkoušel jiný druh modelu na stejném úkolu. Nejlepší variantu každého jsme přepočítali na jednom počítači a na stejné verzi dat i vyhodnocení.
- Jak to funguje, jednoduše: všechny modely dostanou stejné vstupy (hladiny v Děčíně a Ústí, průtoky 12 stanic proti proudu) a předpovídají hladinu za 12, 24 a 36 h. Hodnotíme je na 4 povodních, které při tréninku neviděly.
- Výsledek a co znamená: chyba na povodních lineární regrese 17,1 cm, neuronová síť 17,8, LightGBM 23,1, fyzikální model 24,8, „jako teď“ 44,3. Žádný model nepropásl povodeň, „jako teď“ propásne všechny.
- Návrh na finální model: lineární regrese (`src/models/ridge.py`). Je nejlepší, nejjednodušší, trénuje se za sekundu, nemá planý poplach a celá se vysvětlí na grafu vah. Síť je stejně dobrá jen v rámci náhody a hůř se vysvětluje. Čeká na potvrzení, finální test 2021–2025 se pustí jednou na vybraný model.
- Slabiny a co může být špatně: validace má jen 4 povodně, všechny modely na povodních mírně podhodnocují (bias −5 až −8 cm) a na 36 h je chyba skoro dvojnásobná. Data ČHMÚ v archivu jsou zpětně ověřená, v provozu jsou průtoky při povodni předběžné, takže čísla jsou proti provozu optimistická.
- Otázka poroty a odpověď: „Proč jste nevzali složitější model, když jste ho měli?“ Zkusili jsme čtyři přístupy na stejných datech. Neuronová síť ani LightGBM nebyly lepší, LightGBM navíc přestřeluje vrcholy, které jsou vyšší než všechno v tréninku. Jednodušší model, který umíme vysvětlit, vyhrál i v číslech.
## pá 20:05 · Dan
- Co: LightGBM dělám přes Ondrovo společné rozdělení a `porovnej.py`, horizonty 12, 24 a 36 h. Varianta se srážkami nejde, srážky v tabulce nejsou a balíček pořadatelů s meteorologií má jen Ondra (`data/raw` není v Gitu). Externí data jsem nestahoval.
- Proč: stejné vyhodnocení jako u ostatních, jinak by nešly výsledky srovnat.
- Problém: na notebooku je volno jen kolem 1 GB RAM, jeden běh potřebuje 0,75 GB, takže varianty běžely po sobě, ne souběžně.
- Problém: větev `dan` synchronizuju přes `git merge origin/main`, ne `git pull --rebase`. Rebase by přepsal už pushnuté commity a pak by šel pushnout jen s `--force`.
- Otázka pro Ondru: podle mých podkladů se v Děčíně 1. 7. 2024 měnila měrná křivka, podle tvé kontroly v `DATA.md` se hladina při stejném průtoku nemění. Je to v testovací části, tak jsem to neověřoval. Model a) i c) průtok v Děčíně stejně nepoužívají, jen hladinu.

## pá 20:05 · Dan · Rozbor: LightGBM na Labi
- Co jsme udělali: doby doběhu vody do Děčína a Ústí, základy (lineární trend, Ridge na změnu stavu), LightGBM ve čtyřech variantách a sedm pokusů proti přeučení, seedy a SHAP.
- Jak to funguje, jednoduše: LightGBM skládá stovky malých rozhodovacích stromů, každý opravuje chybu těch předchozích. Předpovídá, o kolik hladina stoupne nebo klesne. Nejlíp funguje, když mu ke každé stanici proti proudu řekneme, kolik vody navíc proti dnešku je na cestě do Děčína (průtok posunutý o dobu doběhu).
- Proč tak a ne jinak: změna místo stavu, protože strom neumí předpovědět víc, než viděl. Posunuté průtoky, protože s 98 syrovými sloupci si stromy pamatovaly povodeň 2013 a přenášely ji na jiné povodně (vrchol 2006 o metr výš).
- Výsledek a co znamená: chyba na povodních přes 6 kombinací: „jako teď“ 44,3 cm, trend 39,4, LightGBM na syrových vstupech 40,9, LightGBM s posunutými průtoky 22,8, Ridge 17,1. Nic nepropásl a nemá planý poplach. Stromy na povodních prohrávají s lineárním modelem o 5,7 cm.
- Slabiny a co může být špatně: přeučení (na trénovacích povodních 5–10 cm, na validaci 10–36 cm), schody a přestřelení při rychlém stoupání (2011 asi o 70 cm), povodně 2006 a 2011 jsou vyšší než všechno v tréninku kromě 2013. Povodeň 9/2010 podhodnotí o 25 cm všechny modely, nejspíš déšť blízko kraje, a srážky nemáme. Ve validaci jsou jen 4 povodně.
- Otázka poroty a odpověď: „Proč jste nevybrali LightGBM, když je na tabulková data obvykle nejlepší?“ Na povodních je o 5,7 cm horší než Ridge. Stromy umí předpovědět jen hodnoty, které viděly, a velká povodeň je v tréninku skoro jen jedna (2013). Vztah „víc vody, vyšší hladina“ je skoro přímka a lineární model ji prodlouží i nad to, co viděl. I když stromy jen opravovaly Ridge, výsledek zhoršily ze 17,1 na 18,9 cm.
## pá 20:15 · Ondra · Rozbor: srovnání čtyř modelů
- Co jsme udělali: každý z nás vyzkoušel jiný druh modelu na stejném úkolu. Nejlepší variantu každého jsme přepočítali na jednom počítači a na stejné verzi dat i vyhodnocení.
- Jak to funguje, jednoduše: všechny modely dostanou stejné vstupy (hladiny v Děčíně a Ústí, průtoky 12 stanic proti proudu) a předpovídají hladinu za 12, 24 a 36 h. Hodnotíme je na 4 povodních, které při tréninku neviděly.
- Výsledek a co znamená: chyba na povodních lineární regrese 17,1 cm, neuronová síť 17,8, LightGBM 23,1, fyzikální model 24,8, „jako teď“ 44,3. Žádný model nepropásl povodeň, „jako teď“ propásne všechny.
- Návrh na finální model: lineární regrese (`src/models/ridge.py`). Je nejlepší, nejjednodušší, trénuje se za sekundu, nemá planý poplach a celá se vysvětlí na grafu vah. Síť je stejně dobrá jen v rámci náhody a hůř se vysvětluje. Čeká na potvrzení, finální test 2021–2025 se pustí jednou na vybraný model.
- Slabiny a co může být špatně: validace má jen 4 povodně, všechny modely na povodních mírně podhodnocují (bias −5 až −8 cm) a na 36 h je chyba skoro dvojnásobná. Data ČHMÚ v archivu jsou zpětně ověřená, v provozu jsou průtoky při povodni předběžné, takže čísla jsou proti provozu optimistická.
- Otázka poroty a odpověď: „Proč jste nevzali složitější model, když jste ho měli?“ Zkusili jsme čtyři přístupy na stejných datech. Neuronová síť ani LightGBM nebyly lepší, LightGBM navíc přestřeluje vrcholy, které jsou vyšší než všechno v tréninku. Jednodušší model, který umíme vysvětlit, vyhrál i v číslech.

## pá 20:20 · Ondra
- Co: Dan dokončil LightGBM, srovnání všech čtyř je finální (`docs/POROZUMENI.md`, sekce Jak číst výsledky, i v procentech). Lineární regrese 17,1 cm, síť 17,8, LightGBM 23,1, fyzikální 24,8, „jako teď“ 44,3.
- Návrh: finální model je lineární regrese. Nejlepší a nejjednodušší, trénuje se za sekundu, nemá planý poplach a každou váhu vysvětlíme. Síť je stejná jen v rámci náhody a průměr obou nepomohl (16,9 cm).
- Zjištění: čtyři různé modely skončily blízko sebe. Strop dělají vstupy, ne model. Další zlepšení by přinesly srážky v povodí, ne složitější model.
- Problém: výsledky z Windows byly uložené v kódování cp1250. Převedli jsme je na UTF-8 a `porovnej.py` je teď ukládá i čte správně.

## pá 20:20 · Honza
- Co: aplikace má třetí záložku „Mapa povodí“: 3D terén (veřejné výškové dlaždice bez klíče, podklad OpenStreetMap) a na něm 12 stanic jako sloupce, výška = průtok, barva = stupeň povodňové aktivity (u stanic bez hladiny percentil průtoku, není to oficiální stupeň). Okamžik se řídí z levého menu stejně jako ostatní záložky. Modely pro aplikaci (`models/`) a předpovědi Ridge přepočítané na opraveném vyhodnocení: `results/2026-10-23_201351_ridge.json`, 17,1 cm, `bias_povodne` −1,5 (12 h) až −11,6 cm (36 h).
- Proč: obrázek k větě „co teče Prahou teď, je zítra v Děčíně“. Staré výsledky nový `--prehled` ignoruje, proto přepočet.
- Problém: dlaždice mapy se stahují z internetu. Na prezentaci je záloha `docs/grafy/app_mapa.png`, v sobotu přibude video.
## pá 20:30 · Ondra
- Co: sepsali jsme celkový přehled řešení `docs/PREHLED.md`: co předpovídáme, které vstupy každý model používá, co jsme nevzali a proč, rozdělení, výsledky a tabulku všech rozhodnutí s důvody.
- Proč: rozhodnutí byla rozesetá po deníku, pokusech a datech. Pro prezentaci a otázky poroty je potřebujeme pohromadě.

## pá 20:20 · Dan
- Co: všech 14 mých modelů jsem pustil znovu na opravené verzi dat a vyhodnocení. Závěry platí: LightGBM c 23,1 cm na povodních (stejně jako Ondrovi na Macu), Ridge 17,1, zbytek po Ridge 18,7. Grafy jsou překreslené.
- Problém: otisk verze v `porovnej.py` vychází na Windows jinak než na Macu (u mě 69a6db32, u Ondry 9a31181e), i když data a kód jsou stejné. Git na Windows (`core.autocrlf=true`) ukládá `.py` soubory s konci řádků CRLF a `verze()` je hashuje i s nimi. Po převodu `.py` na LF vyjde přesně 9a31181e. Následek: `--prehled` na Macu schová výsledky z Windows (Dan, Honza) jako „starou verzi“ a na Windows zase chybí výsledky z Maců. Čísla jdou srovnat, jen je přehled neukáže vedle sebe.
- Návrh pro Ondru: v `verze()` u `.py` souborů před hashováním nahradit `\r\n` za `\n`, nebo do `.gitattributes` přidat `*.py text eol=lf`. Je to Ondrův soubor, neměnil jsem ho.
- Problém: Python na Windows zapisuje text v cp1250, pokud se nezadá kódování. Moje starší výsledky tak nešly v novém `porovnej.py` přečíst. Ondra i já jsme je převedli do UTF-8, nový `porovnej.py` už zapisuje UTF-8.
## pá 20:45 · Ondra
- Co: zjistili jsme, že doba putování vody závisí na průtoku. Při povodni se vlna zpomalí (Mělník → Ústí 8 h při malé vodě, 16 h nad 1 500 m³/s), protože se rozlije do nivy. Modely zatím počítají s jednou dobou na stanici.
- Kdo co: Dan zkusí dobu putování podle průtoku (zadání v `docs/UKOL_MODELY.md`, sekce Další úkol), Ondra srážky, sníh a teplotu z 25 stanic ČHMÚ v povodí.
- Proč: čtyři modely skončily blízko sebe, strop dělají vstupy. Oba pokusy přidávají informaci, kterou modely zatím nemají. Sklon a vzdálenost samotné se nemění, jejich vliv je už ve změřené době putování.
