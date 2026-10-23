# Strategie na výhru

Stav pá 21:30 (Honza), už se srážkami (nepomohly), učicí křivkou a nejistotou v aplikaci. Podklad pro kontrolní bod o půlnoci a pro sobotní ráno. Body poroty jsou náš odhad, porota nic nezveřejnila. Čísla jsou z `docs/PREHLED.md` a `docs/POKUSY.md`, co jsem dnes večer ověřoval sám, je označené „ověřeno pá 20:45“.

## 1. Kde jsme podle kritérií poroty

| Kritérium | Kdyby se prezentovalo teď | Reálně v 14:30 | Kde ztrácíme a proč |
|---|---|---|---|
| Splnění zadání (10) | 7 | 9 | Zadání chce v prezentaci 7 bodů (problém, data, příprava, vstupy, model, ověření, limity). Materiál máme na všechny, ale prezentace zatím neexistuje, v Gitu není ani osnova. Finální test 2021–2025 neběžel, a zadání výslovně chce model ověřit na datech, která neznal (validaci jsme použili k výběru modelu). Ve Stavu v `CLAUDE.md` je prázdné „Komu řešení pomáhá“. |
| Postup řešení (10) | 8 | 9 | Postup je silný: dělení v čase, vynechané povodně, laťka „jako teď“, čtyři modely od nejjednoduššího, pravidla iterace, nezávislá kontrola úniku dat. Ztrácíme na tom, že validace má jen 4 povodně a test chybí. Když to v prezentaci odříkáme jako seznam, porota neuvidí, proč jsme co udělali. |
| Odbornost (20) | 14 | 17 | Každý z nás umí svůj model, ale porota se ptá kohokoli na cokoli. Kdo neumí vysvětlit Ridge, rozdělení a metriku, bere body celému týmu. V `docs/POROZUMENI.md` jsou prázdné sekce „Úloha vlastními slovy“ a „Pojmy“, přesně to, na co se porota ptá jako první. Srážky jsme zkusili a nepomohly (17,1 → 17,4 cm). To je silná odpověď, ale jen když ji umí říct každý, ne jen Ondra. |
| Prezentace (10) | 4 | 8 | Není prezentace, záložní video ani nácvik. Aplikace a 18 grafů existují, ale čísel je moc (4 modely × 2 stanice × 3 horizonty). 3D mapa potřebuje internet. |
| **Celkem (50)** | **33** | **43** | |

Největší rezerva je v prezentaci (nejvíc bodů navíc) a v odbornosti (nejvíc bodů celkem). Na modelu se už body skoro nezískají: čtyři různé přístupy skončily na 17–25 cm, strop dělají vstupy.

## 2. Pět věcí do soboty 11:00

Seřazené podle odhadu bodů za hodinu práce. Dělají je různí lidé, takže jdou souběžně. Pořadí neříká, co je nejdůležitější: nejvíc bodů celkem přinese bod 4.

| # | Co | Kdo | Kdy | Hodin | Bodů navíc | Bodů za hodinu |
|---|---|---|---|---|---|---|
| 1 | Za mentory se třemi otázkami | Ondra, Tobias | pá do 22:30, jinak so 8:00 | 0,3 | +1 | 3 |
| 2 | Otázky poroty: každý umí celý řetězec | všichni, vede Ondra | pá 23:30 a so 9:30, po 30 min | 1 | +2 až 3 | 2,5 |
| 3 | Finální test s předem zapsaným plánem | Ondra | pá po 22:00, po Danově pokusu | 1 | +1,5 | 1,5 |
| 4 | Prezentace podle 7 bodů zadání a nácvik | Tobias, čísla Ondra | osnova pá 23:30, slajdy so 10:00, nácvik 10:15 | 4 | +4 | 1 |
| 5 | Záložní video dema a mapa bez internetu | Honza | so 9:30–10:30 | 1 | +0,8 (pojistka) | 0,8 |

**1. Mentoři.** Mentoři DCÚK sedí v porotě a v roce 2024 podle nich týmy, které za nimi nechodily, dopadly hůř. Tři otázky:
- Je v pořádku, že trénujeme na archivu ČHMÚ mimo balíček (stejný zdroj, za 2024–2025 shodný na centimetr), a jak to máme podat?
- Jaký předstih a jaká přesnost by povodňové komisi v Děčíně stačily? Z odpovědi bude věta „komu to pomáhá“, kterou nevymyslíme sami.
- Ukázat jim graf `docs/grafy/povoden_2011-01_decin_24h.png` a zeptat se, jestli mu rozumí bez vysvětlování.

Na zpoždění dat ČHMÚ se ptát nemusíme, ověřili jsme ho (sekce 4, živá data). Riziko: v noci tu mentoři nejsou, pak v 8:00. A nenechat se dotlačit k nové funkci po 11:00.

**2. Otázky poroty.** Odbornost má 20 bodů a porota se ptá různých členů. Postup: 20 otázek ze sekce 5, každou dostane nejdřív ten, kdo danou věc nedělal (Ridge vysvětluje Tobias, fyzikální model Dan, LightGBM Honza), Ondra opravuje. Před prvním kolem doplnit do `docs/POROZUMENI.md` „Úlohu vlastními slovy“ (dvě věty) a „Pojmy“ (chyba na povodních, laťka, validace, přeučení, regularizace, měrná křivka, doba putování, stupeň povodňové aktivity, předstih, planý poplach, bias, SHAP). Ve druhém kole pustit `/porota` naostro. Riziko: únava o půlnoci. Proto druhé kolo ráno a krátké odpovědi, ne přednášky.

**3. Finální test.** Bez testu stojí celé ověření na 4 povodních, ze kterých jsme vybírali model. Test v noci, ne ráno, ať je ráno čas na graf povodně 9/2024 a slajd. Postup:
- Podle Ondrova plánu (deník pá 21:20): po 22:00, až doběhne Danův pokus s dobou putování podle průtoku. Finální je Ridge, Danova varianta jen při zlepšení aspoň o 1 cm. Ridge se natrénuje na všem do 2020 a pak jednou test.
- Před spuštěním zapsat do `docs/DENIK.md`, co test rozhodne a co ne: „Pouštíme jednou, podle výsledku nic neladíme. Když vyjde hůř než validace, řekneme to a vysvětlíme proč.“ Vědci z FJFI tohle ocení víc než dobré číslo.
- `--test` jednou, výsledek do `docs/POKUSY.md`, graf 9/2024 a 12/2023 do `docs/grafy/`.

Riziko: test vyjde hůř. Možný důvod máme v `docs/DATA.md`: vrchol z Mělníka do Ústí po roce 2013 teče rychleji (6–7 h místo 8–11 h), takže model trénovaný do 2018 se může splést v načasování. Horší číslo s vysvětlením body nebere, dodatečné ladění podle testu ano.

**4. Prezentace.** Nejvíc bodů celkem. Osnova podle 7 bodů zadání, 14 minut a minuta rezerva:

| Čas | Slajd | Co tam je | Graf | Kdo mluví |
|---|---|---|---|---|
| 0:00 | Problém a komu pomáhá | Děčín, povodně 2013 (1 072 cm) a 2024 (649 cm). Otázka: dá se den předem říct, jak vysoko bude Labe? Uživatel: povodňová komise města a lidé u řeky | | Tobias |
| 1:00 | Data | balíček: 2024–2026, jediná povodeň, nejvýš Ústí (4 h před Děčínem). Jen se stanicemi z balíčku a dvěma roky by model nebyl lepší než „jako teď“ a propásl by polovinu povodní. Proto archiv ČHMÚ 2006–2025, 12 stanic, za 2024–2025 shodný s balíčkem na centimetr | `kolik_dat.png`, `app_mapa.png` | Ondra |
| 2:30 | Příprava dat | kontrola: bilance vody mezi stanicemi, měrná křivka, chyba 1 019 cm v 2/2006 vyřazená. Dělení v čase, 4 povodně ve validaci, test 2021–2025 jednou | | Ondra |
| 3:30 | Vstupy | „co teče v Praze, bude zítra v Děčíně“: doby putování (Ústí 4 h, Mělník 13 h, Praha 17 h, Beroun 23 h). Co jsme nevzali a proč | `fyzika_vetve.png` | Tobias |
| 4:30 | Modely | čtyři přístupy na stejném úkolu, vyhrál nejjednodušší. Proč stromy neumí vrchol vyšší než v tréninku. Co nepomohlo: srážky a sníh z 25 stanic (17,1 → 17,4 cm), průměr dvou modelů | `srovnani_procenta.png` | Dan |
| 6:00 | Jak model rozhoduje | váhy: průtok v Praze teď je hladina v Děčíně za 24 h, záporné váhy jsou trend | `ridge_vahy_decin.png` | Honza |
| 7:00 | Ověření | chyba na povodních o 61 % menší než „jako teď“, 24 z 24 nástupů povodní zachycených, 0 planých poplachů, varování před 2. stupněm v průměru 17 h předem. Test 2021–2025 | `povoden_2011-01_decin_24h.png`, graf testu | Ondra |
| 8:30 | Demo | „Teď“ na 15. 1. 2011, mapa s přehráním vlny, „Jak dobře to funguje“. Když něco selže, hned video | aplikace | Honza |
| 11:00 | Limity | dál než den a půl nevidíme (denní srážky ze stanic nepomohly), 36 h slabé, rozmezí u předpovědi na povodních sedí v 8 z 10 případů, povodeň z deště v kraji (9/2010) nevidí, data v provozu předběžná, validace jen 4 povodně, vrcholy mírně podhodnocuje | | Tobias |
| 12:30 | Co dál | doba putování podle průtoku, živá data ČHMÚ (ověřeno, že jsou), hodinové srážky (ČHMÚ je má až od 2018) a víc povodní na ověření | | Dan |
| 13:30 | Jedna věta na konec | „Z otevřených dat zdarma: o povodni v Děčíně den předem, s modelem, který se vejde na jeden obrázek.“ | | Tobias |

Pravidla: na slajdu nejvýš jedno hlavní číslo. Čísla jen z tabulky v `docs/PREHLED.md`, ať se mezi slajdy neliší. Tabulky pro slajdy generovat na Macu nebo brát z `PREHLED.md`: na Windows ukazuje `porovnej.py --prehled` jen Ridge, ostatní výsledky mají kvůli koncům řádků jiný otisk verze (Dan to hlásil). Nácvik se stopkami v 10:15, aby se do 11:00 dalo ještě škrtat, další po 12:30 a v 13:15. Odevzdat ve 13:45, ne ve 13:59.

Riziko: Tobias má menší limit, a když vypadne, nemá prezentaci kdo dělat. Proto osnova v Gitu už dnes do 23:30 a slajdy si můžou rozebrat ostatní podle sloupce „Kdo mluví“.

**5. Záložní video a mapa bez internetu.** Nahrát na Tobiasově Macu (na tom poběží demo) celou cestu dema podle slajdu 8, 2–3 minuty, až bude ve 9:30 finální model v aplikaci. Krátký výřez s mapou (vlna 1/2011 jde z Prahy do Děčína) dát rovnou do slajdu, ten je dobrý i bez výpadku. Mapa tahá dlaždice z internetu, záloha `docs/grafy/app_mapa.png` už je. Riziko: na starém notebooku se video seká, proto Mac. Po 11:00 nahrát znovu, jen když se změní aplikace.

**Hotové a patří do slajdů:** graf `docs/grafy/kolik_dat.png` (proč nestačil balíček) a rozmezí „nejspíš od–do“ u každé předpovědi v aplikaci.

**Když zbude čas** (nižší body za hodinu):
- Slajd o anomáliích (Dan po 22:00, 1 h, sekce 4).
- Živá data (sázka, sekce 4). Jen stahování přes noc, o funkci rozhodnout v 9:00.

**Co nedělat:** nové modely, další ladění LightGBM a sítě, skládání modelů (průměr Ridge a sítě dal 16,9 cm, nic), další pokusy se srážkami, cokoli nového po 11:00.

**Časová osa:**

| Kdy | Co |
|---|---|
| pá 21:30–22:00 | Dan doba putování podle průtoku, Ondra příprava testu, Honza screenshoty aplikace a případně stahování živých dat, Tobias osnova |
| 22:00 | Ondra a Tobias za mentory |
| 22:30–23:30 | finální model, plán testu do deníku, test (Ondra), Dan slajd o anomáliích |
| 23:30 | osnova v Gitu, první kolo otázek poroty |
| 0:00 | kontrolní bod: výsledek testu, plán na noc |
| 0:30–7:30 | spánek ve směnách |
| so 8:00 | výsledek testu, finální model v aplikaci, mentoři |
| 8:00–10:00 | slajdy, graf testu |
| 9:30 | druhé kolo otázek, `/porota` |
| 9:30–10:30 | záložní video |
| 10:15 | první nácvik se stopkami |
| 11:00 | konec nových věcí |
| 12:30, 13:15 | druhý a třetí nácvik |
| 13:45 | odevzdání |

## 3. Co udělají ostatní týmy na Labi a čím se odlišíme

Labe je nejnázornější z pěti úloh a zadání je volné, takže čekáme víc týmů na Labi. Kolik, nevíme. Silné školy z minulých let (SPŠ Teplice, SPŠE Plzeň, SPŠ Česká Lípa) mají letos týmy taky.

Co nejspíš udělají (odhad):
- Většina vezme jen balíček (2024–2026) a předpoví hladinu v Děčíně na pár hodin z Ústí a Litoměřic, často LightGBM, XGBoost nebo LSTM.
- Přesnost ukážou jako R² nebo chybu přes všechny hodiny. Na klidné řece je ale skoro dokonalá i předpověď „bude jako teď“ (u nás na všech hodinách 12,8 cm), takže číslo vypadá skvěle a nic neříká.
- Část rozdělí data náhodně nebo bez ochranného pásma a bude mít únik z budoucnosti. S jedinou povodní v balíčku nemají na čem ověřit to podstatné.
- Dashboard ve Streamlitu nebo webu s mapou stanic, grafy teploty vody a korelace srážek s hladinou za 2024–2026.
- Někdo zkusí detekci anomálií (Isolation Forest) nebo chatbota nad daty.
- Silnější týmy si můžou stáhnout data ČHMÚ proti proudu taky. Pak nás neodliší data, ale ověření a vysvětlení.

Čím se odlišíme:
1. **Měříme povodně, ne klidnou řeku.** Jeden slajd: „Na všech hodinách vyhraje i ‚nedělat nic‘ skoro stejně. Proto měříme chybu během povodní a varování.“ Bez jmenování ostatních, porota si to spojí sama.
2. **Ověření na šesti povodních, které model neviděl** (4 validace, 2 test), proti jediné v balíčku.
3. **Čtyři druhy modelů na stejném úkolu a vyhrál nejjednodušší.** Přesně to, co pořadatelé chtějí („radši jednodušší model, kterému rozumíte“), a máme to v číslech, ne jen jako názor.
4. **Model jde vysvětlit fyzikou.** Váhy odpovídají době putování vody, fyzikální model ukazuje, že učený model nedělá nic magického.
5. **Výstup pro uživatele:** stupně povodňové aktivity, předstih v hodinách, propásnuté povodně a plané poplachy. To povodňová komise použije, R² ne.
6. **Faktory povodní jsme otestovali, ne odbyli.** Srážky, sníh a teplota z 25 stanic za 20 let nepomohly, ani dokonalá předpověď deště na den dopředu (o 0,8 cm), a víme proč: na 12–36 h je voda z deště už v řekách proti proudu.
7. **Poctivé limity a nalezené pasti:** interpolace brala hodnotu z budoucnosti, denní srážky s časem „den D 06:00“ jsou déšť za následující den. Porota z FJFI pozná tým, který únik dat hledal sám.

## 4. Co z nabídky zadání neděláme a co se dá přidat

| Směr ze zadání | Děláme? | Kde to máme |
|---|---|---|
| předpověď vodního stavu | ano, hlavní úloha | celé řešení |
| předpověď průtoku | napůl | fyzikální model předpovídá průtok a převádí ho měrnou křivkou |
| neobvyklé nebo rychlé změny | napůl, nepojmenované | kontrola dat (`DATA.md`), „proč nestačí, že voda stoupá“ (`NAPAD_LABE.md`) |
| porovnání stanic | ano, nepojmenované | bilance vody, doby putování, podíl Vltavy na povodních |
| změna výše po toku → níž | ano, jádro řešení | doby putování, váhy modelu, mapa |
| počasí a řeka | ano, nepomohlo | srážky, sníh a teplota z 25 stanic, 17,1 → 17,4 cm (`POKUSY.md`, pá 21:15) |
| teplota vody | ne | |
| včasné upozornění | ano | varování před 2. a 3. stupněm, předstih, plané poplachy |
| aplikace se stavem a odhadem | ano, přehrávání historie | `app/app.py` |

Zadání chce jeden problém udělaný pořádně, to máme. Do prezentace stačí říct, že ostatní směry slouží hlavnímu problému, a ukázat dva z nich.

**Anomálie: ano, 1 h, Dan.** Dva kusy, oba z hotových dat:
- Kontrola dat jako hledání anomálií: Děčín 2/2006 hladina 1 019 cm při průtoku 120 m³/s (vyřazeno), skoky na jezech ve Vraňanech (35 hodin za 20 let), Sázava v zimě 18 dní stejná hodnota (odhad ČHMÚ při ledu), skoky v Ústí o 50–65 cm jsou skutečné (průtok jde s nimi).
- Neobvyklý vývoj ze zbytku modelu (ověřeno pá 20:45 na `results/predpovedi/ridge.parquet`, Děčín +12 h, validace): typická odchylka skutečnosti od předpovědi je 3,8 cm, 95 % hodin do 14,2 cm. Odchylka nad 50 cm byla jen ve 20 hodinách a všechny v září 2010, tedy u povodně z deště v kraji, kterou model nevidí. Nad 40 cm 34 hodin, z toho 24 v září 2010. V provozu to jde hlídat v reálném čase: v čase t známe skutečnost i předpověď vydanou v t − 12 h. Pro slajd: „Když se řeka chová jinak, než by měla podle vody proti proudu, přichází voda odjinud. Dá se to hlídat automaticky.“ Pozor: práh 50 cm je vybraný na validaci, na testu ho jen ověříme, ne ladíme.

**Porovnání stanic: ano, 20 min, Tobias.** Žádná nová práce, jen slajd z hotového: `docs/grafy/fyzika_vetve.png`, tabulka podílu Vltavy na vrcholu povodně (2013 80 %, ostatní 56–60 %, `NAPAD_LABE.md`) a bilance Mělník = Vraňany + Kostelec (poměr 1,00).

**Teplota vody: ne, nanejvýš jedna věta.** Ověřeno pá 20:45 na balíčku (`hydrologie_komplet_ml.csv`): teplotu mají Děčín a Hřensko jen za 2024–2025, měsíční průměr v Děčíně 2,3–21,2 °C, nejvíc 25,1 °C. V létě je voda teplejší při menším průtoku (korelace denních průměrů −0,47 v Děčíně, −0,53 v Hřensku). S povodněmi to nesouvisí a za dva roky se nic neověří. Zajímavé jsou dvě podezřelé řady, ty patří do slajdu o anomáliích: Louny mají v roce 2024 každý měsíc průměrnou teplotu 9,7–10,7 °C, v lednu i v srpnu (domněnka: čidlo neměří řeku), Ploučnice v Benešově měla v létě 2024 asi deset dní přes 30 °C (podezřelé, neověřeno).

**Živá data: sázka, ne jistota.** Ověřeno pá 20:45 na https://opendata.chmi.cz/hydrology/now/data/: pro všech 12 našich stanic jsou soubory `0-203-1-<číslo>.json` s hodnotami po 10 minutách, poslední hodnota byla asi 15 minut stará. Tím je zodpovězená otázka pro mentory o zpoždění dat. U 9 stanic (i Děčín a Ústí) je v souboru navíc předpověď hladiny a průtoku od ČHMÚ (`H_F`, `Q_F`) na 2,5 dne, u Mělníka a Kostelce jen průtoku. Problémy: soubor obsahoval jen data od půlnoci UTC (nejspíš drží jen aktuální den, domněnka), model ale potřebuje 36 h zpátky. Nymburk nemá průtok vůbec a Mělník měl jen 2 hodnoty (Mělník jde nahradit součtem Vraňan a Kostelce, bilance sedí). Když chceme živou předpověď na prezentaci, musí od dneška stahovat skript každou hodinu, jinak dnešní data zmizí. Dvě hodiny práce a riziko, proto až za pěticí výš. Předpověď ČHMÚ vedle naší by ale dobře odpověděla na otázku „ČHMÚ už předpovídá, k čemu jste tu vy?“.

## 5. Dvacet otázek poroty

V porotě čekáme vědce z FJFI (metoda a data), člověka z Datového centra ÚK (komu to pomůže) a člověka z IT firmy (aplikace a provoz). V závorce, kdo odpovídá. Při nácviku se ale ptát i ostatních.

**Metoda a odbornost**

1. *Proč nedělíte data náhodně a proč validujete na povodních 2006–2011, a ne na posledních letech?* (Ondra) Sousední hodiny jsou skoro stejné, při náhodném dělení by model znal odpověď z tréninku. Dělíme v čase a kolem validačních povodní vynecháváme 20 dní. Na posledních letech validovat nejde, 2016–2020 nebyla žádná povodeň.
2. *Jak víte, že model nevidí do budoucnosti?* (Ondra) Vstupy jsou jen hodnoty změřené do okamžiku předpovědi a řetězec prošel nezávislou kontrolou. Sami jsme našli a opravili dvě pasti: doplňování děr bralo hodnotu z budoucnosti a denní srážky s časem „den D 06:00“ jsou déšť za následujících 24 h, proto je bereme až od dalšího dne.
3. *Proč lineární regrese, když máte neuronovou síť a LightGBM?* (Honza) Na povodních, které neviděla, vyšla nejlíp (17,1 cm, síť 17,8, LightGBM 23,1, „jako teď“ 44,3). Síť je stejná v rámci náhody, mezi seedy kolísá o 0,9 cm, a hůř se vysvětluje. Při stejném výsledku bereme jednodušší.
4. *Proč odmocnina z průtoku?* (Honza) Hladina roste s průtokem zhruba jako odmocnina, je to tvar měrné křivky. Lineárnímu modelu pak vztah sedí jako přímka. Na hladinu ji nedáváme, tam zkazila vrchol 2006 o metr.
5. *Některé váhy jsou záporné. Dává to smysl?* (Honza) Ano. Model odečítá hodnotu před pár hodinami od hodnoty teď, tedy počítá, jestli voda stoupá a jak rychle. Hladina a průtok téže stanice nesou skoro stejnou informaci a váhy se navzájem dorovnávají, čte se proto celek.
6. *Model pro Ústí používá Děčín, který je po proudu. Není to podvod?* (Honza) Ne. Hladina v Děčíně je změřená v okamžiku předpovědi, je to tatáž voda změřená o 4 h později. Do budoucnosti tím nevidíme.
7. *Proč LightGBM prohrál, když je na tabulková data obvykle nejlepší?* (Dan) Strom umí předpovědět jen hodnoty, které viděl, a velká povodeň je v tréninku skoro jen jedna (2013). U povodně 1/2011 přestřelil asi o 60–70 cm. Vztah „víc vody, vyšší hladina“ je skoro přímka a lineární model ji prodlouží i nad to, co viděl.
8. *Proč je fyzikální model horší, když fyzika platí?* (Tobias) Má jednu pevnou dobu putování, ale při povodni se vlna rozlije do nivy a zpomalí (Mělník → Ústí 8 h při malé vodě, 16 h nad 1 500 m³/s). A předpokládá, že co jsme ještě nezměřili, se nezmění. Je to laťka a vysvětlení, učený model tu fyziku jen zpřesňuje.
9. *Validace má 4 povodně. Není rozdíl 17,1 proti 17,8 cm náhoda?* (Ondra) Je, proto ho tak bereme. Pravidla jsme si dali předem: jedna změna s důvodem, zlepšení aspoň o 1 cm, konec po třech neúspěších. Rozhodlo, že lineární model je jednodušší. Test na dalších dvou povodních pouštíme jen jednou.
10. *Proč je předpověď na 36 h dvakrát horší než na 24 h?* (Tobias) Voda, která bude v Děčíně za 36 h, z velké části ještě neteče žádnou naší stanicí. Z nejvzdálenějších (Beroun, Sázava) teče do Děčína zhruba 23–25 h, zbytek musí model odhadnout. Srážky z 25 stanic jsme zkusili a nepomohly (17,1 → 17,4 cm), ani dokonalá předpověď deště na den dopředu by chybu nesnížila o víc než 0,8 cm. Denní průměr srážek za povodí je na to hrubý, hodinové má ČHMÚ až od 2018.
11. *Model na povodních podhodnocuje. Proč to neopravíte?* (Ondra) Průměrně o 5 cm, hlavně vrcholy vyšší, než byly v tréninku. Opravu bychom museli naladit na 4 validačních povodních, to by bylo přeučení na validaci. Proto je to v limitech.
12. *Jak dopadl test a proč se liší od validace?* (Ondra) Doplnit po testu. Připravené vysvětlení: po roce 2013 teče vrchol z Mělníka do Ústí rychleji (6–7 h místo 8–11 h), model trénovaný do 2018 se může o hodinu dvě splést v načasování. Podle testu jsme nic neladili.
13. *Co když přijde povodeň větší než 2013?* (Tobias) Lineární model pokračuje přímkou, takže vrchol odhadne, jen spíš níž (2006: o 20 cm na 875 cm). Stromy by se zasekly na maximu z tréninku. Měrná křivka je nad 3 710 m³/s prodloužená přímkou, tam už je to odhad.

**Praktické využití**

14. *Komu to pomůže a co s tím udělá?* (Tobias) Povodňové komisi Děčína a lidem u řeky. O 2. stupni povodňové aktivity se dozví v průměru 17 h předem, „jako teď“ nevaruje nikdy dřív, než voda stupeň překročí. Na validaci 24 z 24 nástupů povodní zachycených a žádný planý poplach. U každé předpovědi ukazujeme rozmezí, na povodních se do něj skutečnost vešla v 8 z 10 případů. (Doplnit, co řekne mentor.)
15. *ČHMÚ už předpovědi dělá. K čemu je váš model?* (Tobias) Srovnávat se s ČHMÚ neumíme, jejich historické předpovědi nemáme a počítají i se srážkami. Náš model je doplněk: z otevřených dat zdarma, průhledný na jednom obrázku a každý vidí, proč předpovídá, co předpovídá.
16. *Proč jste nepoužili jen data z balíčku?* (Ondra) Balíček má 2024–2026, jedinou povodeň a nejvýš Ústí, odkud voda doteče za 4 h. Nešlo by předpovídat dál než pár hodin ani nic ověřit. Archiv ČHMÚ je stejný zdroj, za 2024–2025 shodný s balíčkem na centimetr. Ukazuje to graf `kolik_dat.png`: jen stanice z balíčku a dva roky (2017–2018) dají 44,6 cm, tedy totéž co „jako teď“, a propásnou 12 z 24 nástupů povodní. Víc stanic pomohlo víc než víc let.
17. *A povodeň z deště přímo v kraji?* (Dan) Tu model nevidí, voda nepřitekla přes naše stanice. Všechny modely v 9/2010 podhodnotily asi o 25 cm. Umíme ale poznat, že se děje něco neobvyklého: odchylka od předpovědi nad 50 cm byla na celé validaci jen v září 2010.

**Aplikace a provoz**

18. *Šlo by to nasadit? Jak rychle chodí data?* (Honza) ČHMÚ zveřejňuje operativní data po 10 minutách se zpožděním asi 15 minut (ověřeno pá večer). Chybí v nich průtok v Nymburce a v Mělníku je jen občas, Mělník jde nahradit součtem Vraňan a Kostelce. Operativní data jsou předběžná, takže v provozu bude chyba spíš větší než naše čísla.
19. *Jak náročný je provoz a co když na prezentaci nepůjde internet?* (Honza) Všech 6 modelů se natrénuje za sekundu na notebooku, předpověď je okamžitá, žádná grafika není potřeba. Aplikace je Streamlit, knihovny v `app/requirements.txt`. Bez internetu nejdou jen dlaždice mapy, na to máme screenshot a video.
20. *Co jste nestihli a co byste dělali dál?* (Dan) Dobu putování podle průtoku (výsledek doplnit), živá data ČHMÚ s jejich předpovědí vedle naší, hodinové srážky, až jich bude víc let, a ověření na dalších povodních. Jako druhou zkoušku modelů menší řeku v kraji (Kamenice).
