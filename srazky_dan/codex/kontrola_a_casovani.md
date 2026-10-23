**Přímý únik zpráv z budoucnosti jsem nenašel.** Našel jsem však podhodnocenou délku měřené historie a slabiny testu. Nic jsem nezměnil; Python běžel s `-B`, bez zápisu.

- [závažnost: střední] `srazky_dan/srazky.py:28` – **78 h nestačí pro celou měřenou historii** – pro 72h příznak v termínu E = 00/12 se nejstarší díl může počítat jako `u12(E−66) − u6(E−72)`. Oba úhrny zasahují až k E−78; při t = E+6 jde o **t−84 h**. Ověřeno změnou vstupu, která změnila výsledek. Nastavit 84 h i v `obaly.py:27`, pokud konstanta chrání celé měřené období; 78 h stačí pouze pro stáří razítek zpráv.

- [závažnost: střední] `srazky_dan/kontrola_casovani.py:43` – **test přebírá kontrolované zpoždění z implementace** – při změně `ZPOZDENI` na nulu se zpráva použije už v E a tato kontrola přesto projde; ověřeno v paměti. Očekávání odvodit nezávisle z pevného pravidla 1 h a přidat explicitní případy t = E, E+1, E+6.

- [závažnost: střední] `srazky_dan/kontrola_casovani.py:59` – **správnost součtů se pouze vypisuje** – jediný závěrečný `assert` kontroluje únik; rozdíl součtů ani neočekávané chybějící výsledky test neshodí. Doplnit aserce s výslovnou tolerancí a kontrolou NaN. U deterministických změn rovněž vyžadovat očekávaný účinek, nikoli jen počítat `bez_ucinku`.

- [závažnost: nízká] `srazky_dan/srazky.py:100` – **oříznutí záporného rozdílu nezachovává 12h úhrn** – například 6. 7. 2010 je předchozí 6h úhrn 15 mm, ale navazující 12h úhrn 14 mm; rozklad ponechá 15+0 mm. Proto test skutečně hlásí rozdíl 1 mm. Stanovit explicitní politiku rozporů, například nekonzistentní dvojici označit jako chybějící, a samostatně ji testovat.

Ostatní ověření:

- `nacti_zpravy` správně rozděluje AA1–AA4, čte délku v hodinách, dělí úhrn deseti a rozpoznává `9999`. DATE je čas pozorování v UTC; pro běžné zpětné 6/12h úhrny odpovídá konci období. Výběr termínů odpovídá zadání. Viz [formát NOAA ISD](https://www.ncei.noaa.gov/pub/data/noaa/isd-format-document.pdf).
- `predbezne` obsahuje pouze tehdejší `u6`. Dorovnání dílu 00/12 z následujícího 06/18 se předčasně nepoužije. `shift(1)` a rolling zahrnují správné starší díly.
- `hodinove` správně používá `floor((t−1 h)/6 h)`: v E platí E−6, od E+1 do E+6 platí E.
- `postav():143` průměruje stanice pouze ve stejném čase. Normalizaci přes budoucnost, zpětné doplňování ani interpolaci jsem nenašel.
- Podmínka **3** podle dokumentace znamená začátek akumulace, nikoli obecně platný úhrn. V přečtených místních zprávách však nenulové hodnoty odpovídají SYNOP v REM; zde je výjimka empiricky podložená. Doplnil bych regresní příklady po roce 2013.
- Kvalita **2/6** znamená obecně „podezřelé“; příčinu ani velikost chyby neurčuje. Ponechání je obhajitelné jako vědomá volba. Stopové = 0 je rozumné přiblížení; 150/250 mm jsou vlastní filtry, nikoli limity formátu. Viz [NOAA](https://www.ncei.noaa.gov/pub/data/noaa/isd-format-document.pdf).

Původní test prošel: **300 změn, 0 předčasných změn**, rozdíl součtů až **1 mm**. Další kontrola shody výpočtu z celé řady s výpočtem pouze z dostupných zpráv prošla pro 60 syntetických termínů. Test ale neověřuje dekodér, skupinové průměry ani celých 84 h měřené historie.