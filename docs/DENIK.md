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

## pá 19:45 · Ondra
- Co: zkontroloval jsem správnost dat (shoda s balíčkem pořadatelů, bilance vody mezi stanicemi, měrné křivky, časy, odlehlé hodnoty). Data jsou v pořádku, nic se neměnilo. Podrobnosti v `docs/DATA.md`, sekce Labe.
- Co: do zadání modelů přibyla pravidla, jak dlouho iterovat (jedna změna s důvodem, zlepšení aspoň o 1 cm v `prumer_povodne`, konec po 3 neúspěšných variantách, 10 variantách nebo ve 20:50).
- Proč: validace má jen 4 povodně, nekonečné ladění by našlo variantu, která na nich vyjde náhodou dobře.

Následující záznamy jsou doplněné zpětně (pá 19:55) podle commitů, ať je vidět celý postup od výběru úlohy.

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
## pá 20:05 · Ondra
- Co: ověřili jsme, jestli do modelu nepatří přítoky Labe v kraji (Bílina, Ploučnice). Nepatří, na validaci nepomohly (`docs/POKUSY.md`).
- Proč: přidají jen 2–13 % vody při vrcholu a doteče z nich za pár hodin. Velké přítoky nad krajem (Vltava s Berounkou a Sázavou, Jizera, horní Labe, Ohře) v modelu jsou.
- Limit pro prezentaci: povodeň z lokálních dešťů v kraji, jako v srpnu 2010, model bez srážek dopředu nevidí.

## pá 19:48 · Tobias · Rozbor: fyzikální model
- Co jsme udělali: model, který se skoro nic neučí. Vezme průtok v cíli teď a přičte, o kolik víc vody mezitím přitekla Vltavou, Labem a Ohří, posunuté o dobu putování. Průtok pak převede na hladinu měrnou křivkou.
- Jak to funguje, jednoduše: co teď teče v Praze, bude za 18 h v Děčíně. Z dat jsme změřili, kolik hodin voda putuje z každé stanice (`docs/grafy/fyzika_vetve.png`), a z 13 let měření, jaká hladina odpovídá jakému průtoku (`docs/grafy/fyzika_merna_krivka.png`).
- Proč tak a ne jinak: je to fyzikální základ, se kterým se učené modely srovnávají, a celý jde vysvětlit na jednom obrázku. Učí se jen doby putování a křivku, přeučit se nemá jak (chyba na tréninku je dokonce vyšší než na validaci).
- Výsledek a co znamená: `prumer_povodne` 24,8 cm proti zhruba 44 cm u „jako teď“, Děčín +24 h 22,5 cm. Žádná propásnutá povodeň, žádný planý poplach, před 2. stupněm varuje 11–23 h předem. Třetí vrstva stanic (Beroun, Sázava, Přelouč) zlepšila 36 h o 4 cm. Lineární modely jsou lepší (Dan Ridge 17,1 cm).
- Slabiny a co může být špatně: doby putování jsou jedno pevné číslo, ale při každé povodni jsou trochu jiné. Co ještě nikdo nezměřil, model považuje za neměnné, takže při stoupání podhodnocuje vrcholy, nejvíc na 36 h (38 cm). Před vrcholem 2006 krátce přestřelil o 50 cm. Povodeň z lokálních dešťů (srpen 2010) bez předpovědi srážek nevidí. Přítoky v kraji podle Ondry chybu nevysvětlují, dají jen 2–13 % vody.
- Otázka poroty a odpověď: „Proč je fyzikální model horší než lineární regrese, když fyzika platí?“ Fyzika tu má zjednodušení: jednu dobu putování a předpoklad, že co nebylo změřeno, se nezmění. Lineární model se z dat naučí i to, že stoupající voda proti proudu ještě dál stoupá, a jakou váhu má která stanice. Fyzikální model je proto laťka a vysvětlení: ukazuje, že učený model nedělá nic magického, jen tuhle fyziku zpřesňuje.
