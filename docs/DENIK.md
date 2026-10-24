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

## pá 20:50 · Dan · Rozbor: doba doběhu podle průtoku
- Co jsme udělali: změřili jsme dobu doběhu z každé stanice zvlášť pro pásma průtoku v Ústí, jen na trénovacích datech, a dali ji do LightGBM a do lineárního modelu místo jedné stálé doby.
- Jak to funguje, jednoduše: když je v Ústí málo vody, bere model z Ústí průtok před 6 h, když je vody víc, tak před 3 h, protože vlna jde rychleji. U ostatních stanic podobně podle naměřené tabulky.
- Proč tak a ne jinak: při povodni se vlna rozlije do nivy a zpomalí (transformace povodňové vlny). Doby jsme měřili jen na tréninku, aby se do modelu nedostala validace. Kde bylo v pásmu málo dat nebo slabá souvislost, vzali jsme sousední pásmo, nic jsme nevymýšleli.
- Výsledek a co znamená: nepomohlo to. LightGBM 23,1 cm stejně jako bez pásem, lineární model se stejnými vstupy o 0,4 cm lépe, pod hranicí 1 cm. Zpomalení vlny při velké povodni se z trénovacích dat změřit nedá, nad 1 500 m³/s je tam jen červen 2013.
- Slabiny a co může být špatně: doby nad 1 500 m³/s by šly změřit s validačními povodněmi, to ale nesmíme. Pásma podle průtoku v Ústí jsou hrubá a zpoždění v X jsou jen po 3–12 h, takže rozdíl 1–2 h se po zaokrouhlení ztratí. Ondrova tabulka se s mou shoduje, jen Louny nad 1 500 m³/s vychází 10 h místo 23 h, což je stejně jen jedna povodeň.
- Otázka poroty a odpověď: „Když víte, že se vlna při povodni zpomalí, proč to model nepoužívá?“ Zkusili jsme to a na validaci to nepomohlo. Na trénovacích datech je nad 1 500 m³/s jediná povodeň, takže zpomalení neumíme spolehlivě změřit. Lineární model si dobu doběhu stejně najde sám z vah přes všechna zpoždění 0–36 h, proto mu ruční doba nic nepřidá.
## pá 20:38 · Ondra
- Co: Honza dostal vedle aplikace úkol „kolik let dat model potřebuje“ (učicí křivka lineární regrese, jen kraj proti všem stanicím, zadání v `docs/UKOL_MODELY.md`). Sepsali jsme inventuru všech dat `docs/ZDROJE_DAT.md`: co je v balíčku, kolik z toho používáme a proč, co jsme přidali a jaké parametry modely dostávají.
- Zjištění: denní úhrn srážek ČHMÚ s časem „den D 06:00“ je déšť za následujících 24 h, ne za předchozích (ověřeno na hodinových srážkách v Praze 5–7/2020). Kdybychom ho brali od jeho časové značky, model by viděl den deště z budoucnosti. Bereme ho až od D+1 07:00.
- Proč: graf o množství dat odpovídá na otázku poroty, proč nestačil balíček. Inventura dat je podklad pro slajd „Jaká data jsme použili“, který zadání výslovně chce.

## pá 20:44 · Honza · Rozbor: kolik let dat model potřebuje
- Co jsme udělali: nezměněnou lineární regresi jsme naučili na 1, 2, 3, 5, 8 a 13 letech do konce 2018, vždy jen na třech stanicích z kraje a pak na všech 12. Celkem 72 tréninků, stejná validace a společné vyhodnocení.
- Jak to funguje, jednoduše: měníme jen to, kolik minulých let a odkud model dostane měření. Stejné čtyři povodně mu při učení pokaždé schováme. Graf `docs/grafy/kolik_dat.png` ukazuje, jak klesá chyba.
- Proč tak a ne jinak: oddělíme přínos delší historie od přínosu stanic proti proudu, aniž bychom ladili model nebo nahlíželi do finálního testu. Pokus běžel v oddělené pracovní kopii kvůli souběžným úpravám aplikace.
- Výsledek a co znamená: všechny stanice a 8 / 13 let mají chybu 16,6 / 17,1 cm proti 44,3 cm u „bude jako teď“, bez propásnutí i planých poplachů. Dva roky všech stanic mají podobnou chybu jako 13 let jen z kraje (26,9 / 27,8 cm), ale propásnou 4 z 24 hodnocených nástupů; dlouhý kraj nepropásne žádný, má však dva plané poplachy. Osm a třináct let se liší méně než o 1 cm, finální model necháváme beze změny.
- Slabiny a co může být špatně: krátká okna do pěti let nemají ani jednu hodinu na 2. stupni; delší zahrnují povodeň 2013. Nerozhoduje tedy jen počet let, ale i zastoupení povodní. Validace je retrospektivní, některé povodně jsou starší než trénink. Čtyři povodně nedokazují, že osm let stačí všude; test 2021–2025 jsme nepoužili. Nezávislá kontrola potvrdila stejné validační řádky, správné hranice oken i shodu plného tréninku s Ridge 17,1 cm.
- Otázka poroty a odpověď: „Takže model potřebuje přesně osm let?“ Ne. Na této validaci osm let funguje podobně jako třináct, ale tato okna už obsahují velkou povodeň 2013. Dva suché roky mohou stačit k menší průměrné chybě, přesto některá povodňová varování propásnou. Historii potřebujeme i k nezávislému ověření na několika povodních.
## pá 20:55 · Honza · Rozbor: kolik let dat model potřebuje
- Co jsme udělali: učicí křivku lineární regrese: trénink na 1 až 13 letech před validací, jednou jen se stanicemi z balíčku (Děčín, Ústí, Louny), jednou se všemi 12. Graf `docs/grafy/kolik_dat.png`.
- Jak to funguje, jednoduše: stejný model, jen mu dáváme méně historie nebo méně stanic, a měříme chybu na stejných 4 povodních.
- Proč tak a ne jinak: porota se zeptá, proč jsme nevystačili s balíčkem. Odpověď chceme ukázat číslem, ne tvrdit.
- Výsledek a co znamená: balíček (2 roky, jen kraj) = 45 cm, horší než „jako teď“ (44,3), a 12 z 24 nástupů povodní propásne. Stanice proti proudu srazí chybu na 27 cm i se 2 roky; velká povodeň v tréninku (2013) srazí propásnuté na 0; obojí dohromady 17 cm. Víc stanic pomohlo víc než víc let.
- Slabiny a co může být špatně: krátká okna končí vždy rokem 2018, takže „2 roky“ znamená 2017–2018 (suchá léta); jiné dva roky by vyšly jinak. Validace má 4 povodně.
- Otázka poroty a odpověď: „Nestačila by data, která jste dostali?“ Ne. S nimi by model nebyl lepší než „bude jako teď“ a propásl by polovinu povodní, protože v letech 2024–2026 je jediná povodeň a stanice jen v kraji. Proto jsme přidali 20 let a 9 stanic z otevřených dat ČHMÚ.
## pá 20:44 · Ondra
- Co: srážky, sníh a teplotu z 25 stanic v povodí do modelu nepřidáváme. Na validaci nepomohly (lineární regrese 17,1 → 17,4 cm, síť 17,8 → 21,2 cm) a ani dokonalá předpověď srážek na den dopředu by nepomohla o víc než 0,8 cm.
- Proč: otestovali jsme názor, že přesnější model potřebuje všechny faktory povodní. Na horizontu 12–36 h je ale voda z deště a tání už v řekách a model ji vidí v průtocích proti proudu. Faktory, které se nemění (sklon, půda, tvar povodí), jsou už ve změřené době putování a měrné křivce. Víc vstupů při stejném počtu povodní znamená hlavně riziko přeučení (síť se zhoršila o 3,4 cm).
- Pro porotu: „Zkoušeli jste srážky?“ Ano, z 25 stanic za 20 let, a nepomohly, ani kdybychom znali déšť den dopředu. Proto zůstáváme u jednoduššího modelu.

## pá 20:46 · Honza · sjednocení učicí křivky při synchronizaci
- Co: zachovali jsme oba záznamy souběžných pokusů; výsledný `src/kolik_dat.py` ukládá metriky a hlídá, aby z vybraného období pocházelo i všech 36 hodin historie. Graf obsahuje chybu i počty propásnutí.
- Proč se čísla trochu lišila: starší maska připouštěla u krátkých oken prvních 36 řádků se vstupy z předchozího roku. Oprava mění jen krátká okna (kraj a dva roky 45,1 → 44,6 cm), ne 8 a 13 let ani počty propásnutí.
- Pro porotu: dva roky všech stanic dávají podobnou chybu jako 13 let jen kraje, nikoli průkazně lepší. „Dva roky“ jsou zde 2017–2018; výsledek není měřením skutečného balíčku 2024–2026. Nevyvozujeme obecné minimum osmi let.
## pá 20:46 · Ondra
- Co: vlastní model na předpověď deště dělat nebudeme.
- Proč: myšlenkový pokus ukázal, že ani dokonalá předpověď srážek na den dopředu by nezlepšila chybu o víc než 0,8 cm (`docs/POKUSY.md`, pá 20:44). Náš vlastní model deště by byl horší než dokonalý, takže by přinesl ještě méně. Předpověď počasí navíc potřebuje modely atmosféry (tlakové pole, družice), které z dat ze stanic za večer neuděláme.
- Plán k finálnímu modelu: lineární regrese je hotová, ladění skončilo podle pravidel. Počkáme na Danův pokus s dobou putování podle průtoku (do 22:00), protože může změnit finální model. Pak finální model natrénujeme na všem do 2020 a jednou pustíme test 2021–2025 (`python src/porovnej.py jako_ted <model> --test`). Po testu přetrénovat model pro aplikaci na všech datech do 2025 (`src/uloz_model.py` zatím trénuje jen na train).

## pá 21:20 · Honza · Rozbor: animace povodně
- Co jsme udělali: čtvrtá záložka aplikace „Animace povodně“ (`app/animace.py`): plynulá 3D animace v prohlížeči (deck.gl), terén a satelit, skutečné linie řek z OpenStreetMap (`data/external/reky.geojson`, 11 úseků mezi stanicemi), po nich tečou kapky rychlostí podle doby putování a nesou průtok ze stanice proti proudu, sloupce stanic rostou s průtokem, panel ukazuje hladinu v Děčíně a Ústí, předpověď modelu za 24 h a stupeň. Play, pauza, rychlost 1 až 16 h/s, posuvník času. Čtyři validační povodně na výběr.
- Jak to funguje, jednoduše: je to naše věta „co teče Prahou teď, je zítra v Děčíně“ nakreslená v čase. Kapka, která projede Prahou při 840 m³/s, dorazí za den do Děčína.
- Proč tak a ne jinak: hydraulický model koryta (rozliv, hloubky) by za noc byl vymyšlený a porota by to poznala. Tohle ukazuje jen to, co máme změřené: průtoky, doby putování, předpověď. Rozliv řešíme zvlášť přes oficiální záplavová území.
- Doby putování mezi stanicemi (h, odhad z našich dat a tabulky v `docs/DATA.md`): Přelouč → Nymburk 8, Nymburk → Kostelec 5, Jizera → Kostelec 6, Kostelec → Mělník 3, Beroun → Praha 4, Sázava → Praha 5, Praha → Vraňany 4,5, Vraňany → Mělník 2, Mělník → Ústí 12, Louny → Ústí 20, Ústí → Děčín 4. Z délek úseků to dává 4 až 11 km/h. Mezi povodněmi se liší, model s nimi nepočítá, jen animace.
- Slabiny a co může být špatně: dlaždice jdou z internetu (záloha: screenshoty `docs/grafy/animace_*.png` a video); na telefonu se popisky překrývají; panel ukazuje i skutečnou hladinu o 24 h později, v provozu bychom ji neznali, je tam jen pro srovnání s předpovědí.
- Otázka poroty a odpověď: „Je ta animace model, nebo jen obrázek?“ Obrázek naměřených dat a naší předpovědi; rychlost kapek je doba putování odhadnutá z dat, ne výpočet proudění. Model je lineární regrese v záložce Teď, animace ho jen vysvětluje.
## pá 20:55 · Dan
- Co: odpověď na otázku poroty k době doběhu podle průtoku, jak ji budeme říkat. Zapsaná i do `docs/POROZUMENI.md`, sekce Otázky, které čekáme od poroty.
- Otázka poroty a odpověď: „Když víte, že se vlna při povodni zpomalí, proč to model nepoužívá?“ Zkusili jsme to a nepomohlo to (21,8 vs 22,2 cm, pod hranicí 1 cm). Lineární model má 98 zpožděných hodnot (z každé stanice 7 zpoždění 0–36 h) a dobu doběhu včetně roztažení vlny si z vah najde sám. Zpomalení při velkých povodních nejde spolehlivě změřit – nad 1 500 m³/s je v tréninku jen jedna povodeň (6/2013, 227 h).

## pá 20:58 · Ondra · Rozhodnutí: finální model
- Co: finální model je lineární regrese `src/models/ridge.py` (alpha 1, odmocnina průtoků, všech 98 vstupů). Rozhodnuto před spuštěním testu, test se pouští jednou.
- Proč: na validaci nejlepší (17,1 cm na povodních, 61 % méně než „jako teď“), nic nepropásl, žádný planý poplach, trénink za sekundu a každá váha jde vysvětlit. Všechny pokusy o zlepšení skončily pod hranicí 1 cm nebo horší: síť 17,8, průměr ridge a sítě 16,9, srážky a sníh 17,4, doba putování podle průtoku (Dan) 21,8, větší váha povodní (Honza) 17,2, kratší historie (Honza) 16,6 při 8 letech, rozdíl pod 1 cm.
- Test: finální model se natrénuje na všem do konce 2020 (train i validace) a vyhodnotí na 2021–2025 (`python src/porovnej.py jako_ted ridge --test`). Pro srovnání pustíme na test i ostatní tři přístupy, výběr je už uzavřený a podle testu se nemění.
- Čekáme: výsledek na testu může být jiný než na validaci, jsou to jiné povodně (12/2023 a 9/2024 jsou menší než 2006 a 2011) a model má víc tréninkových dat.

## pá 21:02 · Ondra · Rozbor: finální test
- Co jsme udělali: finální model (lineární regrese) jsme natrénovali na všem do konce 2020 a jednou vyhodnotili na letech 2021–2025, které jsme při ladění nikdy nepoužili.
- Jak to funguje, jednoduše: stejná zkouška jako validace, jen na nových povodních (2021, Vánoce 2023, únor 2024, Boris 2024).
- Výsledek a co znamená: chyba na povodních 22,4 cm proti 50,2 cm u „jako teď“, o 55 % menší (na validaci 61 %). Při povodni Boris model hlásil 3. stupeň v Děčíně 27 h předem (předpověď na 24 h). Před 3. stupněm varoval pokaždé.
- Slabiny a co může být špatně: na testu je chyba o 5 cm větší než na validaci, testové povodně stoupaly rychleji (i laťka je horší). Čtyři hraniční překročení 2. stupně o pár cm model propásl. Vrcholy podhodnocuje, Boris o 38 cm. Síť vyšla na testu o 1,1 cm lépe, na validaci o 0,7 cm hůř, je to náhoda a výběr podle testu neměníme.
- Otázka poroty a odpověď: „Proč jste nevzali neuronovou síť, když je na testu lepší?“ Model jsme vybrali před testem podle validace a zapsali to do deníku. Kdybychom ho teď vyměnili, vybírali bychom podle testu a ten by přestal být poctivý. Rozdíl 1 cm je navíc menší, než jak se síť liší sama se sebou při jiném seedu.

## pá 21:30 · Honza · Rozbor: předpověď na dnešek z živých dat ČHMÚ
- Co jsme udělali: `app/aktualni.py` stahuje operativní data ČHMÚ (opendata.chmi.cz/hydrology/now a recent, po 10 minutách, 10–30 min stará) pro našich 12 stanic, sestaví stejný řádek vstupů jako `features.py` a vydá předpověď na teď. V aplikaci je přepínač „Dnešek“ v levém menu; vedle naší předpovědi se ukáže i oficiální předpověď ČHMÚ (řada H_F) na stejné hodiny.
- Jak to funguje, jednoduše: totéž, co děláme na historii, jen s dnešními čísly. Dnes ve 20:00: Děčín 90 cm, model za 24 h 98 cm, ČHMÚ 91 cm, všechno hluboko pod 1. stupněm.
- Proč tak a ne jinak: zadání výslovně jmenuje „aplikaci, která zobrazuje aktuální stav a odhad dalšího vývoje“. Bez dneška je to jen analýza historie.
- Slabiny a co může být špatně: ČHMÚ operativně nezveřejňuje průtok v Nymburce vůbec a v Mělníku jen dvakrát denně; dopočítáváme je z bilance vody (Mělník = Vraňany + Kostelec o hodinu dřív, Nymburk = Kostelec − Jizera). Na validaci to zhorší Děčín +24 h z 15,5 na 16,9 cm; aplikace u předpovědi vždy vypíše, co je dopočtené. Operativní hodnoty jsou nevalidované a vydání je 1–2 h za skutečným časem. Na klidné vodě (jako teď) model nepřidá nic proti „jako teď“, jeho hodnota je při povodni. Pro dnešek používat `ridge_vse` (učený na všem do 2025).
- Otázka poroty a odpověď: „Funguje to i dnes, ne jen na starých datech?“ Ano: přepínač Dnešek stáhne poslední měření ČHMÚ a vydá předpověď; vedle ní ukazujeme i oficiální předpověď ČHMÚ pro srovnání.

## pá 21:40 · Honza · Rozbor: rozliv z oficiálních záplavových území
- Co jsme udělali: `app/rozliv.py` převede předpovězenou hladinu na průtok (měrná křivka z našich dat, ověřená proti oficiální křivce ČHMÚ, rozdíl do 3 %), srovná ho s N-letými průtoky ČHMÚ (Q1 až Q100, `data/external/n_lete_vody.csv`, zdroj opendata.chmi.cz hydrological_characteristic a evidenční listy) a na 3D mapě vyplní oficiální záplavové území DIBAVOD (VÚV TGM) pro tu N-letou vodu, kterou předpověď dosáhne (`data/external/zaplavova_uzemi.geojson`, Q5, Q20, Q100, úsek Ústí a Děčín). Pod mapou věta: „739 cm odpovídá asi 2 050 m³/s, to je mezi pětiletou a desetiletou vodou.“
- Jak to funguje, jednoduše: neumíme spočítat, kam se voda rozlije, ale stát to má změřené pro pětiletou, dvacetiletou a stoletou vodu. My jen řekneme, které z nich je naše předpověď nejblíž, a tu mapu ukážeme.
- Proč tak a ne jinak: vlastní hydraulický model koryta (tvar dna, drsnost, kalibrace) za noc poctivě nejde a porota by to poznala. Takhle je předpověď naše, převod z měření a polygony oficiální.
- Slabiny a co může být špatně: polygony platí pro ustálený N-letý průtok, ne pro konkrétní tvar naší povodně; rozliv v Děčíně ovlivňuje i Ploučnice, kterou nemáme; pod pětiletou vodou se mimo koryto nic nerozlije, takže na většině dat je mapa jen s obrysy. Polohu polygonů na terénu jsme ověřili jen v prohlížeči, ne proti skutečnosti.
- Otázka poroty a odpověď: „To je váš hydraulický model?“ Ne. Je to oficiální záplavové území, které vybíráme podle naší předpovědi průtoku. Vlastní hydrauliku jsme záměrně nedělali.

## pá 22:10 · Honza · Rozbor: počasí ne do modelu, ale do aplikace
- Co jsme udělali: v režimu Dnešek aplikace pod předpovědí ukáže, kolik má příštích 24 a 48 h pršet v povodí Vltavy, horního Labe a Ohře (`app/pocasi.py`, Open-Meteo, průměr z 12 bodů po povodích), s větou pro laika a varováním nad 20 mm. Do modelu srážky nevstupují.
- Jak to funguje, jednoduše: model říká, co přiteče z vody, která už teče. Předpověď deště říká, co přibude až potom. Ukazujeme obojí vedle sebe, ale nemícháme je.
- Proč tak a ne jinak: Ondra ověřil, že srážky, sníh ani teplota z 25 stanic modelu nepomohly (17,1 → 17,4 cm) a ani dokonalá předpověď deště na den dopředu nedá víc než 0,8 cm. Na 12–36 h je voda z velkých dešťů už v řekách proti proudu. Vlastní model na předpověď srážek by byl nesmysl, to dělají meteorologické modely. Historické předpovědi počasí z let 2006–2013 nemáme, takže by se vliv nedal poctivě ověřit.
- Slabiny a co může být špatně: hranice 20 mm („hodně“) a 5 mm („skoro nic“) jsou odhad, ne výpočet. Open-Meteo není ČHMÚ. Déšť rozhoduje od zhruba 48 h dál, tam naše předpověď nesahá.
- Otázka poroty a odpověď: „A co když zaprší?“ Na dnešek a zítřek to model nepotřebuje, voda z deště teče řekami den a víc. Na pozítří by to potřeboval, proto předpověď srážek ukazujeme vedle a říkáme, že za 36 h a dál může být hladina vyšší, než model říká.

## pá 22:20 · Honza
- Co: grafy do prezentace v jednom stylu jsou v `docs/grafy/slajdy/` (vyrábí `src/grafy_slajdy.py` jen z uložených výsledků): srovnání modelů (61 % méně), test 2021–2025 (55 % méně, Boris 27 h předem), učicí křivka, váhy Děčín +24 h, Boris 2024, povodeň 2011, co jsme zkoušeli a nepomohlo, pokrytí rozmezí nejistoty. 16:9, nadpis jako tvrzení, zdroj a podmínky pod grafem, šedá = jako teď, modrá = lineární regrese, oranžová = ostatní.
- Proč: slajdy mají působit jako jeden celek; dosud byly grafy ve třech stylech. Tobias bere do prezentace tyhle.
- Pozor: balíček 2 roky jen kraj je v grafech 44,6 cm (opravená verze učicí křivky), ne 45,1 z prvního běhu; LightGBM je „o 48 % méně“ (podíl průměrů), v PREHLED.md 49 % (průměr procent); povodeň 2011 hlásil model 15 h předem, ne „den“.

## pá 22:55 · Honza · Rozbor: mapa v Mapbox GL
- Co jsme udělali: záložka Mapa povodí má nové hlavní zobrazení v Mapbox GL JS (`app/mapbox_mapa.py`): satelit s popisky ulic, 3D terén, 3D budovy v Děčíně a Ústí, oficiální záplavové území přilepené na terén a vyplněné podle předpovědi, stanice s popupem, přelet kamerou mezi celým povodím a městy, panel s předpovědí a větou o N-leté vodě. Pydeck mapa zůstává pro režim Dnešek, přehrání povodně a provoz bez tokenu. Screenshoty `docs/grafy/mapbox_*.png`.
- Jak to funguje, jednoduše: stejná data jako dřív (průtoky, předpověď, záplavová území), jen je kreslí mapový engine, který umí terén a budovy. Při pětileté vodě v Děčíně je vidět, které domy u Labe a Ploučnice stojí ve vyplněném území.
- Proč tak a ne jinak: v deck.gl se polygony na terén lepily ručně a malá území zanikala; Mapbox GL je přilepí sám a dá k tomu budovy a ulice, takže rozliv má měřítko, kterému laik rozumí. Vlastní hydraulický model jsme záměrně nedělali.
- Slabiny a co může být špatně: potřebuje internet a token Mapboxu (veřejný, v `.env`); každé překreslení je jedno načtení mapy do bezplatného limitu; budovy jsou jen od zoomu 15; polygony platí pro ustálený N-letý průtok, ne pro konkrétní povodeň, a rozliv ovlivňuje i Ploučnice, kterou nemáme. Při rychlém přepínání v Streamlitu se v konzoli objeví zrušené požadavky staré mapy, nevadí to.
- Otázka poroty a odpověď: „Ta modrá plocha je výstup vašeho modelu?“ Ne. Model předpoví hladinu, z ní převedeme průtok a vybereme oficiální záplavové území (DIBAVOD) pro nejbližší N-letou vodu. Modrá plocha je tedy úřední mapa, náš je výběr, které z nich právě platí.
## pá 22:46 · Ondra · srážky: kdy dávají smysl
- Co: Ondra navrhl předpovídat déšť a přes něj průtok a hladinu dřív. Vyzkoušeli jsme to na horizontech až 72 h (`docs/POKUSY.md`, pá 22:46).
- Zjištění: s dokonalou předpovědí deště se dešťová povodeň 9/2010 zlepší o 23 % na 36 h a o 40 % na 72 h. Povodně z tání sněhu (2006, 2009, 2011) se nezlepší. Naměřené denní srážky nepomáhají vůbec, známe je až ráno po konci dne, kdy voda už teče v řekách.
- Rozhodnutí: finální model zůstává bez srážek, test už proběhl a výběr neměníme. Do prezentace jako „co dál“: s předpovědí srážek od ČHMÚ by šlo dešťové povodně předpovídat na 2–3 dny. Vlastní model předpovědi deště neděláme, potřebuje modely atmosféry.
- Pro porotu: „Proč nepoužíváte předpověď deště?“ Na 12–24 h by nepomohla, voda už je v řekách. Na 2–3 dny a u dešťových povodní ano, i s dokonalou předpovědí by to ale byl jen odhad horní meze z jedné povodně a skutečné historické předpovědi deště na trénink nemáme.

## pá 23:27 · Ondra · Rozbor: vícenásobná validace
- Co jsme udělali: každou z 8 povodní 2006–2020 jsme jednou vynechali, modely naučili na zbytku a změřili na ní. Test se nepoužil.
- Jak to funguje, jednoduše: s jednou validací můžeme mít štěstí nebo smůlu na to, které povodně v ní jsou. Povodně jsou různě těžké (3/2009 11 cm, 6/2013 34 cm), takže se vyzkouší všechny a výsledek se zprůměruje.
- Proč tak a ne jinak: náhodné dělení po hodinách by bylo špatně, sousední hodiny jsou skoro stejné a model by „viděl“ odpověď. Proto po celých povodních s 20 dny odstupu.
- Výsledek a co znamená: lineární regrese 20,1 ± 7,7 cm, síť 21,0, LightGBM 22,7, fyzikální 26,7, „jako teď“ 45,2. Regrese je o 56 % lepší než „jako teď“, stejně jako na testu (55 %). Výběr modelu tedy nebyl náhoda výběru povodní.
- Slabiny a co může být špatně: model se učí i na povodních po té vynechané (budoucnost v tréninku). Pro vztahy v řece to nevadí, ale přísnější by bylo učit jen na minulosti, na to máme málo povodní. Regrese a síť se liší míň, než kolísá chyba mezi povodněmi.
- Otázka poroty a odpověď: „Nemáte výsledek jen ze šťastně vybrané validace?“ Ne, ověřili jsme to na všech 8 povodních 2006–2020, každá jednou vynechaná. Pořadí modelů i zlepšení proti „jako teď“ zůstalo stejné a sedí s testem.

## pá 23:52 · Ondra · starší povodně a data odjinud nepřidáváme
- Co: zjišťovali jsme, jestli by model zlepšily starší povodně (hlavně 8/2002) nebo data z jiných řek.
- Zjištění: hodinová data mají celou sadu stanic až od 2006. Povodeň 2002 v nich nemá hladinu v Děčíně ani v Ústí. Starší data jsou jen denní průměrné průtoky (Děčín od 1887), které rozmažou vlnu putující 4–40 h. Jiné řeky mají jiné stanice a doby putování, náš model se učí váhy konkrétních stanic na Labi.
- Rozhodnutí: zůstáváme u 2006–2025. Denní data od 1887 by šla použít na předpověď na několik dní nebo na četnost velkých povodní, do „co dál“.
- Pro porotu: „Proč jen od 2006?“ Od té doby měří po hodinách všech 12 stanic, které model potřebuje. Starší povodně buď nemají hodinová data, nebo chybí hladina v Děčíně.

## so 0:10 · Honza · Rozbor: mapa ve stylu Mapbox Standard, rozliv z terénu, porovnání předpověď × skutečnost
- Co jsme udělali: záložka Mapa má dva režimy. „Zvolený okamžik“: mapa v Mapbox GL se stylem Standard (realistické 3D budovy a stromy, osvětlení svítání/den/soumrak/noc, barevná témata, satelit, popisky), panely Pohledy a Zobrazení, přelet kamerou, celá obrazovka, rozliv pro předpovězenou hladinu. „Celá povodeň: předpověď × skutečnost“: čas běží po hodinách přes celou povodeň, vlevo rozliv z hladiny předpovězené 24 h předem, vpravo ze skutečné, posuvník uprostřed, v panelu rozdíl v cm a v hektarech. Rozliv počítá `app/rozliv_dem.py` z výškového modelu ČÚZK DMR 5G (2 m): zaplaví se vše, co je níž než hladina (nula vodočtu + hladina, sklon 0,44 m/km změřený z našich dat, nad jezem Střekov kóta vzdutí) a je spojené s řekou; polygony po 10 cm hladiny.
- Jak to funguje, jednoduše: model řekne hladinu, převedeme ji na nadmořskou výšku vody a na mapě vybarvíme všechno, co je pod ní a kam se voda od řeky dostane. Vpravo totéž pro hladinu, která opravdu nastala, takže je vidět, o kolik se model spletl v ploše.
- Proč tak a ne jinak: skutečný hydraulický model (proudění) poctivě za noc nejde. Statický rozliv z terénu je uznávaný zjednodušený postup a dá se ověřit: proti úředním záplavovým územím Q5/Q20/Q100 (DIBAVOD) vychází shoda IoU 0,82–0,90 (Děčín Q5: 167 ha náš, 183 ha úřední, průnik 165 ha). Mapbox Standard dává budovy a terén, na kterých má rozliv měřítko pro laika.
- Výsledek a co znamená: při povodni 4/2006 v Děčíně 2. 4. 15:00 předpověď 869 cm proti skutečným 829 cm, pod vodou 208 proti 194 ha; o den později 856 proti 865 cm a plocha stejná (206 ha). Chyba modelu v cm se tím překládá na hektary a ulice.
- Slabiny a co může být špatně: statický model bez dynamiky, protipovodňové zdi a hráze pod rozlišením 2 m nevidí, Ploučnice a Bílina dostávají jen hladinu Labe, polygony neověřené proti skutečnému rozlivu z fotek, jen proti úředním mapám. Potřebuje internet a token Mapboxu; dvě mapy Standard jsou náročné na slabší počítač (na Macu netestováno).
- Otázka poroty a odpověď: „Jak víte, že ten rozliv sedí?“ Při hladině pětileté vody vychází z našeho terénu 167 ha, úřední mapa pětileté vody má 183 ha a 165 ha se překrývá. Není to hydraulický model, je to výška terénu proti výšce hladiny, a tohle srovnání říká, že na Děčín to stačí.

## so 0:50 · Honza · Rozbor: konvoluční síť po čase (TCN), ověření na validaci
- Co jsme udělali: TCN (kauzální dilatované konvoluce, 16 kanálů, okno 48 h surových hodinových řad všech 14 veličin, cíl změna hladiny), `src/models/tcn.py`, seedy 42/43/44, jen validace; finální test se nepouštěl.
- Jak to funguje, jednoduše: místo námi vybraných zpoždění (0, 3, 6, 12, 18, 24, 36 h) dostane síť posledních 48 hodin všech stanic a sama si vybere, které hodiny jsou důležité.
- Proč tak a ne jinak: poslední otázka, kterou jsme chtěli mít změřenou: nezahazujeme ručním výběrem zpoždění něco důležitého? TCN je síť, která by to měla najít.
- Výsledek a co znamená: 20,3 cm na povodních proti 17,1 (Ridge) a 17,8 (síť); seedy 42/43/44 na Děčín +24 h 18,2 / 17,2 / 15,2 cm, rozpětí 3 cm stejné jako odstup od Ridge; 3 propásnuté nástupy 2. stupně v Ústí. Naučené odezvy stanic (impulz v hodině k) mají vrchol v hodině 0 a skoro stejná čísla jako váhy Ridge: Praha +50,0 proti +49,3 cm, Beroun +17 proti +14, Louny +14 proti +18. Graf `docs/grafy/tcn_odezvy.png`.
- Slabiny a co může být špatně: přeučení (nad 1. stupněm trénink 11,1 cm, validace 19,4), nejhorší na povodni 2006, která je vyšší než trénink; „zuby“ v odezvách v hodinách 4, 8, 16, 32 jsou z dilatací sítě, ne z fyziky; zastavení tréninku na 10/2017–12/2018 bez jediné hodiny nad 1. stupněm.
- Otázka poroty a odpověď: „Nezahazujete ručním výběrem zpoždění informaci?“ Síť, která si z 48 hodin vybírala sama, našla skoro stejné váhy jako náš lineární model a byla horší. Co jsme vybrali ručně, stačí.

## so 1:50 · Honza · Rozbor: nový vzhled aplikace (povodňový pult s vodočtem)

Aplikace vypadala jako tmavý Streamlit ze šablony a prvky na sebe nenavazovaly, proto jsme ji předělali na jeden systém postavený kolem vodočtu (měrné latě, podle které se u řeky hladina opravdu čte). V záložce Teď je lať se stupni povodňové aktivity, vodou do současné hladiny a značkami předpovědi za 12, 24 a 36 h s pruhy rozmezí nejistoty, vedle ní přesné odečty se stupněm; v Dnešku je na lati i oficiální předpověď ČHMÚ. Všechny části jsou ve stejných kartách se stejným štítkem, písmem a barvami, grafy mají vlastní šablonu a čáry stupňů se štítky, výběr povodně je všude stejný segmentový přepínač a v Mapě povodí je nahoře přehrávač s výběrem povodně a tlačítkem Přehrát povodeň, aby šla povodeň pustit bez hledání v menu. Ověřili jsme kontrolu `python app/test_app.py` (9 z 9, s živými daty 10 z 10), screenshoty všech záložek na 1440 px a Teď s Mapou na 390 px (nic nepřetéká) a Dnešek s živými daty ČHMÚ. Po úpravě `app/styl.py` je potřeba restartovat server, Streamlit ho sám nenačte. Zbývá projít aplikaci na Tobiasově Macu a natočit záložní video; screenshoty jsou v `docs/grafy/ui2_*.png`.

## so 2:00 · Honza · Rozbor: přehrávač povodně a budovy z dálky

- Co jsme udělali: V mapě Celá povodeň je úvodní okno s jedním tlačítkem Přehrát povodeň a dole přehrávač přes celou šířku: datum a hodina, skutečná a předpovězená hladina se stupněm, rychlost 2/6/12 h za sekundu a časová osa s grafem hladiny, prahy stupňů a vrcholem, kliknutím se skáče v čase. Porovnání má popisky Předpověď 24 h předem a Skutečnost. Města mají pohled z dálky (zoom 13,6) a budovy jsou vidět v celém Děčíně a Ústí.
- Jak to funguje, jednoduše: Mapbox kreslí 3D budovy až zblízka. Obrysy a počty pater 36 tisíc budov jsme jednou stáhli z OpenStreetMap (`app/budovy.py`, `data/external/budovy_*.json`) a mapa je vytáhne do výšky, dokud se nepřiblíží natolik, že je převezmou budovy Mapboxu.
- Proč tak a ne jinak: Dlaždice Mapbox Streets mají v pohledu na Děčín pod zoomem 15 jen 3 až 30 budov (změřeno), takže přes ně to nešlo. Přehrávač je dole a velký, protože porota má hlavně vidět, že předpověď 24 h předem sedí na skutečnost.
- Výsledek a co znamená: Na jednom záběru je vidět město, řeka, rozliv i domy, které stojí ve vodě. Povodeň 1/2011 se přehraje zhruba za minutu. `python app/test_app.py` 9 z 9.
- Slabiny a co může být špatně: Výška budov bez údaje v OSM je odhad (9 m, garáže 3 m). Budovy jsou jen ve čtverci asi 8 × 8 km kolem každého vodočtu, jinde od zoomu 15 ze Standardu. Výkon na slabším notebooku jsme neměřili; nejtěžší je porovnání dvou map v Ústí.
- Otázka poroty a odpověď: Odkud máte budovy a jak víte, jak jsou vysoké? Z OpenStreetMap, výška je z tagu výšky nebo z počtu pater krát 3 m, jinak odhad 9 m. Pro rozliv výška domů nehraje roli, budovy jsou jen pro orientaci.

## so 2:40 · Honza · Rozbor: video rozlivu Borise pro prezentaci

- Co jsme udělali: Dvě videa `docs/grafy/video_povoden_decin.mp4` a `video_povoden_usti.mp4` (1920 x 1080, 30 fps, 24 s, bez zvuku): povodeň Boris od 13. 9. 2024 0:00 do 18. 9. 12:00, mapa Celá povodeň se skutečnou hladinou, boční panely skryté, dole lišta s datem, hodinou a hladinou. Snímek na každou hodinu z přehrávače v mapě (`skoc(i)` v `app/mapbox_mapa.py`), kamera se pomalu otáčí a přibližuje, ffmpeg složí 30 fps; u Děčína jsou plynulé přechody mapy a ostrá lišta zvlášť.
- Jak to funguje, jednoduše: Mapa už umí skočit na libovolnou hodinu povodně, takže video je jen 133 snímků mapy za sebou. Nic není kreslené ručně, všechno je z dat ČHMÚ a z rozlivu z výškového modelu terénu.
- Proč tak a ne jinak: Nahrávání obrazovky v reálném čase trhá a závisí na výkonu notebooku; snímek po hodině je deterministický a dá se znovu vyrobit stejným skriptem. Rozsah končí na vrcholu v Děčíně (646 cm), pokles by se do 25 s nevešel.
- Výsledek a co znamená: Nezávislá kontrola potvrdila rozlišení, délku, nárůst vody (190 → 646 cm, stupně bez → 3.) a čitelnou lištu. Video je úvod prezentace a záloha dema. Pro web je verze 1280 x 720 (8 MB), originály (24 až 30 MB) nejsou v Gitu.
- Slabiny a co může být špatně: Otáčení kamery je krokované po hodinách (5,5 kroků za sekundu), na plátně to působí jako jemné tikání. V liště zůstal přepínač rychlosti a ikona přehrát v klidovém stavu. V Ústí končí klip hodinu před vrcholem.
- Otázka poroty a odpověď: Je to simulace, nebo měření? Hladina je změřená (ČHMÚ), plocha vody je výška terénu ČÚZK proti výšce hladiny se sklonem, ověřená proti úředním záplavovým územím; není to hydraulický model.

## so 4:30 · Honza · Rozbor: web na Netlify a prezentace jako HTML deck

- Co jsme udělali: Statická webová aplikace ve složce `web/` nasazená na https://field-zero.netlify.app (Teď s vodočtem, Jak dobře to funguje, Mapa povodí, Animace povodně, Dnešek z živých dat ČHMÚ) a prezentace jako HTML deck na https://field-zero.netlify.app/prezentace/ (10 slajdů podle `docs/PREZENTACE_7MIN.md` plus 7 záložních, video rozlivu Borise na úvod, animovaná linie řeky, Ondrovy grafy, odkrývání součtu řek na slajdu 4, poznámky řečníka na klávesu N, tisk do `docs/prezentace.pdf`). Data pro web vyrábí `src/export_web.py` (předpočítané hodinové řady 5 povodní pro obě stanice, metriky, koeficienty modelu ridge_vse jako JSON, stránky map a animací s tokenem, které nejsou v Gitu), Dnešek vyrábí `src/dnesek_export.py` a hodinová GitHub Action `.github/workflows/dnesek.yml` (potřebuje secrets MAPBOX_TOKEN, NETLIFY_AUTH_TOKEN, NETLIFY_SITE_ID; návod v `docs/WEB.md`). Nasazení z počítače: `netlify deploy --prod --dir web`.
- Jak to funguje, jednoduše: Web nic nepočítá na serveru. Stejný model jako v aplikaci spočítal předpovědi pro každou hodinu každé povodně a uložil je jako čísla; prohlížeč je jen vykreslí. Mapy jsou stejné stránky, jaké generuje aplikace, jen uložené do souborů. Dnešek počítá jednou za hodinu robot na GitHubu a nahraje nový soubor.
- Proč tak a ne jinak: Streamlit na Netlify běžet nemůže a na hackathonu potřebujeme web, který se otevře komukoli hned a nespadne; statický web s předpočítanými daty má na desktopu Lighthouse 100/100/100 a hlavní stránku do 230 kB. Deck je v HTML, protože Canva přes API neumí písma, animace ani vloženou živou mapu; Canva zůstává jako záloha.
- Výsledek a co znamená: Čtyři nezávislé kontroly (desktop, mobil, rychlost, čeština) našly 3 kritické a 25 vážných nálezů (přetékající tabulky na telefonu, rozbitá věta „Proč to tak vyšlo“ v prvních hodinách povodně, dva různé modely pro Borise v decku a na webu, interní klíče modelů v textech, nečitelné popisky), opravy je odstranily a druhé kolo potvrdilo: bez přetečení na 390 i 768 px, CLS 0, konzole bez chyb, čísla sjednocená (Boris 14. 9. 2024 11:00: 577 cm, vrchol 649 předpovězen na 611, 3. stupeň 27 h předem, model učený do roku 2020 pro test).
- Slabiny a co může být špatně: Veřejný token Mapboxu je ve stránkách map; musí být v účtu Mapbox omezený na doménu. Dnešek je starý, dokud neběží GitHub Action se secrets (web pak po 6 h ukáže varování). Mapy a animace v iframu stahují písma z Google Fonts a deck.gl z unpkg, bez připojení nejdou; přehrávání historie a grafy fungují i offline z lokální kopie. Na telefonu je mapa otevřená jako samostatná stránka, ne v rámu.
- Otázka poroty a odpověď: „Proč web a ne jen aplikace?“ Protože povodňová komise ani lidé u řeky nebudou spouštět Python; web otevře kdokoli na telefonu, a protože je předpočítaný, nejde shodit zátěží v den povodně.
