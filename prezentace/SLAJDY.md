# Slajdy a texty řečníků

Devět slajdů na 6:45, rezerva 15 s do 7:00, pak dvanáct záložních. Každý slajd odpovídá na jednu otázku, kterou by porota položila; nadpis slajdu je odpověď a pod ním jsou věci, které musí zaznít. Text řečníka je napsaný tak, jak se říká nahlas, na zhruba 130 slov za minutu. `[mezerník]` je další krok decku. Živé demo neděláme, web otevíráme až při otázkách. Body zadání: 1 co řešíme, 2 data, 3 příprava dat, 4 vstupy, 5 model, 6 ověření, 7 limity.

| # | Čas | Řečník | Otázka poroty | Nadpis (odpověď) | Bod |
|---|---|---|---|---|---|
| 1 | 0:00–0:40 | Honza | Co řešíte a pro koho? | Den předem víme, kam v Děčíně dosáhne voda | 1 |
| 2 | 0:40–1:20 | Dan | Jaká data jste použili? | Jen z balíčku by to nešlo: bereme 20 let a 12 stanic proti proudu | 2 |
| 3 | 1:20–2:10 | Dan | Co model bere? | Bereme jen řeku, počasí nepomohlo | 3, 4 |
| 4 | 2:10–3:15 | Ondra | Jak jste vybrali model? | Čtyři modely, vyhrál nejjednodušší | 5 |
| 5 | 3:15–3:55 | Ondra | Proč zrovna přímka? | Voda v Děčíně je součet řek | 5 |
| 6 | 3:55–4:30 | Honza | Jak ověřujete? | Ověřeno třikrát na povodních, které model neviděl | 3, 6 |
| 7 | 4:30–5:25 | Honza | Funguje to doopravdy? | Na všech povodních o polovinu menší chyba, Boris 27 hodin předem | 6 |
| 8 | 5:25–5:55 | Tobias | Co z toho má město? | Z předpovědi mapa: kam až voda dosáhne | 1 |
| 9 | 5:55–6:45 | Tobias | Kde to selže? | Co neumíme a co dál | 7 |

Celkem 714 slov, při 130 slovech za minutu 5:29 mluvení. Zbytek do 6:45 je video (20 s bez mluvení) a pauzy na kroky decku.

## 1 · Den předem víme, kam v Děčíně dosáhne voda (0:00–0:40, Honza)

- Otázka: Co řešíte a pro koho?
- Musí zaznít: hladina v Děčíně a Ústí za 12, 24 a 36 h; varování před 2. a 3. stupněm; komise, hasiči, lidi u řeky.
- Na slajdu: video rozlivu Borise přes celou obrazovku, bez zvuku (`web/prezentace/video/boris_decin_720.mp4`, 24 s, náhled `grafy/video_decin_poster.jpg`). Po videu zůstane poslední snímek, nadpis a velké **27 h**.

Video běží 20 s bez mluvení, pak Honza přes konec videa:

> Tohle je Děčín v září 2024. Náš model to hlásil 27 hodin předem. Předpovídáme hladinu v Děčíně a Ústí na 12, 24 a 36 hodin a varujeme před druhým a třetím stupněm. Pro komisi, hasiče a lidi u řeky je to den navíc.

43 slov (strop 43, mluví se od 20. sekundy videa).

## 2 · Jen z balíčku by to nešlo: bereme 20 let a 12 stanic proti proudu (0:40–1:20, Dan)

- Otázka: Jaká data jste použili?
- Musí zaznít: balíček má 2 roky a stanice jen v kraji, nejvýš proti proudu je Ústí 4 h před Děčínem; jen z něj chyba 44,6 cm, stejně jako „bude jako teď“, a polovina povodní propásnutá; proto hodinový archiv ČHMÚ, 20 let a 12 stanic na Vltavě, horním Labi a Ohři až 25 h proti proudu; stejný zdroj jako balíček; chyba 17,1 cm.
- Na slajdu: vlevo mapa stanic (`grafy/02a_mapa_stanic.png`), vpravo `grafy/02b_proc_externi_data.png` (po mezerníku se odkryje třetí sloupec). Tři čísla **20 let · 12 stanic · 175 320 hodin**.

> Balíček od pořadatelů má dva roky dat a stanice jen v kraji. Nejvýš proti proudu je Ústí, jen čtyři hodiny před Děčínem. Model jen z něj se plete o 44,6 centimetru, stejně jako „bude jako teď“, a polovinu povodní propásne.
>
> [mezerník]
>
> Proto jsme vzali hodinový archiv ČHMÚ: dvacet let a dvanáct stanic na Vltavě, horním Labi a Ohři, až 25 hodin proti proudu. Je to stejný zdroj jako balíček, jen delší a s víc stanicemi. Chyba klesla na 17 centimetrů.

79 slov (strop 86).

## 3 · Bereme jen řeku, počasí nepomohlo (1:20–2:10, Dan)

- Otázka: Co model bere?
- Musí zaznít: 98 čísel, hladina Děčín a Ústí a průtok 12 stanic teď a až 36 h zpátky; srážky, sníh, teplota, vlhkost, tlak a vítr nepomohly ani o 1 cm, protože co přijde do 36 h, už teče řekou; dvě pasti z budoucnosti v přípravě dat.
- Na slajdu: vlevo **Bereme:** hladina Děčín a Ústí, průtok 12 stanic, teď až 36 h zpátky = 98 čísel. Vpravo `grafy/03_co_model_bere.png`. Po mezerníku rámeček „Dvě pasti z budoucnosti: doplňování děr, denní srážky“.

> Model bere jen to, co je v tu chvíli změřené na řece: hladinu v Děčíně a v Ústí a průtok na dvanácti stanicích, teď a až 36 hodin zpátky. Dohromady 98 čísel.
>
> [mezerník]
>
> Srážky, sníh, teplotu, vlhkost, tlak i vítr jsme zkusili. Nic nepomohlo ani o centimetr. Co do Děčína přiteče do 36 hodin, už teče řekou a vidíme to v průtoku. I kdybychom déšť na tři dny dopředu znali přesně, chyba klesne jen o centimetr.
>
> [mezerník]
>
> A při přípravě dat jsme našli dvě pasti, které braly informaci z budoucnosti: doplňování děr v datech a čas denních srážek. Obě jsme opravili.

99 slov (strop 108).

Čísla v grafu (validace, chyba na povodních, finální model 17,1 cm): naměřené srážky 17,1; teplota vzduchu a sníh 17,3; voda ve sněhu 17,8; vlhkost 17,2; tlak 17,0; vítr 17,0; víc stanic proti proudu 17,4; myšlenkový pokus, déšť na 3 dny dopředu přesně, 16,1. Zdroje `docs/POKUSY.md` pá 20:44, pá 22:32, pá 23:14, so 0:19, so 8:42. Teplotu vody jsme nezkoušeli, s povodní nesouvisí.

## 4 · Čtyři modely, vyhrál nejjednodušší (2:10–3:15, Ondra)

- Otázka: Jak jste vybrali model?
- Musí zaznít: laťka „bude jako teď“ 44 cm; čtyři modely se stejnými pravidly a u každého jedna věta, proč prohrál; výběr před testem; úpravy přímky nic přes 1 cm.
- Na slajdu: `grafy/04_cesta_k_modelu.png`, tři skupiny sloupců (začátek, čtyři modely, úpravy přímky), odkrývají se mezerníkem.

> Začali jsme laťkou: předpovědí, že bude jako teď. Při povodních se plete o 44 centimetrů.
>
> [mezerník]
>
> Pak čtyři modely, každý dělal jeden z nás, se stejnými pravidly: stejná data, stejné ověření a změna musí zlepšit aspoň o centimetr. Fyzikální model, 25 centimetrů: počítá s pevnou dobou putování vody, jenže ta se mezi povodněmi mění. LightGBM, rozhodovací stromy, 23: neumí předpovědět víc, než kdy viděly, u povodně 2013 daly vrchol o dva a půl metru níž. Neuronová síť, 18: skoro stejně dobrá, ale má přes dvacet tisíc vah na dvě velké povodně a snadno se přeučí. Lineární regrese, 17: nejlepší a nejjednodušší. Vybrali jsme ji před testem.
>
> [mezerník]
>
> Pak jsme zkoušeli vylepšit i ji: polynom, větší váhu povodní, všechna malá zlepšení dohromady. Nic nebylo lepší o víc než centimetr.

126 slov (strop 140).

Zdroje: `docs/CESTA_MODELU.md` (sekce 1, 2 a 6). LightGBM a povodeň 2013: první pokus pá 17:46, vrchol 823 místo 1 072 cm. Síť 128-64 má asi 21 tisíc vah, verze 64-32 měla na tréninku 5 cm a na validaci 22 cm.

## 5 · Voda v Děčíně je součet řek (3:15–3:55, Ondra)

- Otázka: Proč zrovna přímka?
- Musí zaznít: voda v Děčíně je součet Vltavy, horního Labe a Ohře, lineární regrese je vážený součet; příklad Borise den předem 198 → 577 cm, nad 3. stupněm; každé číslo umíme vysvětlit; citát ze zadání.
- Na slajdu: `grafy/05_soucet_rek.png` (v HTML decku animovaný součet, šest kroků mezerníkem), vpravo číslo, které roste 198 → 577 cm, a štítek **3. stupeň · nad 560 cm**. Dole citát „Cílem není vytvořit co nejsložitější model.“ (zadání).

> Proč vyhrála přímka? Voda v Děčíně je součet toho, co přiteče po Vltavě, horním Labi a Ohři, a lineární regrese je přesně vážený součet. Tady je předpověď z Borise, vydaná den předem. Průměr 198 centimetrů,
>
> [mezerník] Děčín a Ústí plus 80, [mezerník] Vltava 89, [mezerník] horní Labe 116, [mezerník] Mělník 96, [mezerník] Ohře minus 2.
>
> [mezerník] Vyjde 577, nad třetím stupněm, a model varoval. Každé číslo umíme vysvětlit. A zadání samo říká: cílem není co nejsložitější model.

71 slov (strop 86).

## 6 · Ověřeno třikrát na povodních, které model neviděl (3:55–4:30, Honza)

- Otázka: Jak ověřujete?
- Musí zaznít: dělení v čase, nikdy náhodně; výběr na 4 vynechaných povodních; vícenásobná validace na 8 povodních; test 2021–2025 jednou na konci.
- Na slajdu: `grafy/06_jak_overujeme.png`, vpravo tři kroky a věta „Dělení v čase, nikdy náhodně“.

> Jak víme, že to funguje? Data dělíme v čase, nikdy náhodně, a ověřujeme vždycky na povodních, které model při učení neviděl. Model jsme vybrali na čtyřech vynechaných povodních. Pak jsme každou z osmi povodní 2006 až 2020 jednou vynechali a model naučili na zbytku, to je vícenásobná validace. A test na letech 2021 až 2025 jsme pustili jen jednou, úplně na konci.

62 slov (strop 75).

## 7 · Na všech povodních o polovinu menší chyba, Boris 27 hodin předem (4:30–5:25, Honza)

- Otázka: Funguje to doopravdy?
- Musí zaznít: Boris je z testu, model ho neviděl, 3. stupeň hlášen 27 h předem; není to jedna šťastná povodeň: ve vícenásobné validaci menší chyba na všech 8 povodních, o 34 až 66 %; test 22,4 proti 50,2 cm, o 55 % menší.
- Na slajdu: vlevo `grafy/07a_boris_2024.png`, po mezerníku vpravo `grafy/07b_vicenasobna_validace.png`. Velká čísla **27 h** („před 3. stupněm v Děčíně, Boris“) a **−55 %** („test 22,4 proti 50,2 cm · vícenásobná validace 20,1 proti 45,2 cm“).

> Funguje to doopravdy? Tohle je Boris, září 2024, z testu, takže ho model nikdy neviděl. Černá je skutečnost, modrá naše předpověď vydaná den předem. Šedá je „bude jako teď“, ta je vždycky o den pozadu. Třetí stupeň model hlásil 27 hodin předem.
>
> [mezerník]
>
> A není to jedna šťastná povodeň. Ve vícenásobné validaci jsme každou z osmi povodní jednou vynechali a chyba byla menší na všech osmi, o 34 až 66 procent. Na testu 2021 až 2025 je 22,4 centimetru proti 50,2, o 55 procent menší.

84 slov (strop 119).

Zdroje: `docs/PREHLED.md` (test), `results/krizova_validace/` a `docs/POKUSY.md` pá 23:27 (vícenásobná validace, opravené procento so 1:15).

## 8 · Z předpovědi mapa: kam až voda dosáhne (5:25–5:55, Tobias)

- Otázka: Co z toho má město?
- Musí zaznít: z předpovězené hladiny mapa rozlivu; výška terénu proti výšce hladiny; proti úřední mapě záplavových území shoda 82 až 90 %; vlevo předpověď den předem, vpravo skutečnost; běží živě na webu.
- Na slajdu: `grafy/08_mapa_rozlivu.png` přes celý slajd (povodeň 4/2006 v Děčíně, vlevo rozliv z předpovědi vydané 24 h předem, vpravo ze skutečné hladiny: 869 proti 829 cm, pod vodou 208 proti 194 ha), dole adresa field-zero.netlify.app a QR kód.

> Co z toho má město? Z předpovězené hladiny aplikace nakreslí, kam až voda dosáhne: porovná výšku terénu s výškou hladiny. Proti úřední mapě záplavových území to sedí z 82 až 90 procent. Vlevo rozliv z předpovědi vydané den předem, vpravo ze skutečnosti. Běží to živě na webu, každou hodinu nová předpověď.

51 slov (strop 65).

Čísla: `docs/DATA.md` (rozliv z ČÚZK DMR 5G, shoda s DIBAVOD IoU 0,82 až 0,90). Kdyby se porota zeptala, jestli je to hydraulický model: záložní Z7.

## 9 · Co neumíme a co dál (5:55–6:45, Tobias)

- Otázka: Kde to selže?
- Musí zaznít: na 36 h skoro dvakrát větší chyba; vyšší vrchol, než jaký model viděl, podhodnotí; přívalové povodně na malých přítocích nevidí; na 2 až 3 dny by pomohla předpověď počasí, ale archiv starých předpovědí na trénink není; závěrečná věta.
- Na slajdu: tři karty (Neumíme, Počasí na 2–3 dny, Dál), po mezerníku závěrečná věta, Děkujeme a QR kód na repozitář.

> Kde to selže? Na 36 hodin je chyba skoro dvakrát větší než na 24, voda, která přijde, ještě neteče žádnou stanicí. Vrchol vyšší, než jaký model kdy viděl, podhodnotí. A přívalové povodně na malých přítocích, jako je Ploučnice nebo Kamenice, nevidí vůbec. Na dva až tři dny dopředu by pomohla předpověď počasí: s přesnou předpovědí by u dešťové povodně 2010 chyba na 72 hodin klesla o 40 procent. Jenže archiv starých předpovědí, na kterém by se model učil, neexistuje.
>
> [mezerník]
>
> Z otevřených dat zdarma: o povodni v Děčíně víte den předem, s modelem, který se vejde na jeden obrázek. Děkujeme.

99 slov (strop 108).

„Skoro dvakrát“: na testu v Děčíně 17,5 cm na 24 h a 29,9 cm na 36 h, tedy 1,7krát. Počasí na 72 h: `docs/POKUSY.md` pá 22:46, dešťová povodeň 9/2010, 79,7 → 69,8 cm s dokonale známým deštěm (horní mez); archiv předpovědí má Open-Meteo až od 2021–2022.

## Záložní slajdy

Ukážou se jen na otázku poroty. V decku jsou za Děkujeme, klávesou End se skočí na konec a šipkou zpět na ten, který je potřeba. Na každém je otázka jako nadpis, graf a jedna dvě věty.

### Z1 · Proč jen lineární regrese?

Graf `grafy/Z1_srovnani_ctyr_modelu.png`. Odpovídá Dan nebo Ondra.

Na čtyřech povodních, které model neviděl, vyšla nejlíp: 17,1 cm, neuronová síť 17,8, LightGBM 23,1, fyzikální model 24,8. Voda v Děčíně je součet řek posunutých o dobu, než doteče, a velké povodně jsou v tréninku jen dvě, složitý model by se z nich naučil náhodu. Nepřeučí se: v Děčíně na 24 h má chybu na tréninku 19,7 cm a na validaci 15,5. Nic z dalšího zkoušení nebylo lepší o víc než 1 cm.

### Z2 · Co znamená „bude jako teď“?

Graf `grafy/Z2_co_je_jako_ted.png`. Odpovídá Ondra.

Předpověď, že hladina za 24 h bude stejná jako teď. Nakreslená v čase, pro který platí, je to skutečná křivka posunutá o den doprava, takže vzestup ohlásí až den poté, co se stal. Proto má při povodních chybu 44 až 50 cm a každý model ji musí porazit.

### Z3 · Proč ne srážky?

Graf `grafy/Z3_proc_ne_srazky.png`. Odpovídá Dan.

Zkusili jsme horní mez: model dostal skutečný déšť na 3 dny dopředu, jako by předpověď počasí byla dokonalá. Chyba klesla jen o 1 cm (17,1 → 16,1) a varování nepřišlo dřív. První nárůst vody vidíme v průtocích proti proudu 12 až 40 h předem, déšť, který spadne teď, doteče do Děčína většinou až za víc než 36 h. Pomohl by na 2 až 3 dny u dešťových povodní, jenže archiv starých předpovědí na trénink nemáme.

### Z4 · Jak moc se pletete?

Graf `grafy/Z4_jak_moc_se_pleteme.png`. Odpovídá Honza.

K předpovědi ukazujeme rozmezí od–do. Je spočítané z chyb modelu na tréninku (90 % chyb) podle toho, jak vysoko voda je, a ověřené na validaci: na klidné vodě se do něj skutečnost vejde v 9 z 10 hodin, na povodních asi v 8 z 10.

### Z5 · Funguje to i na jiné povodni?

Graf `grafy/Z5_povoden_2011.png`. Odpovídá Ondra.

Leden 2011, povodeň z validace, kterou model při učení neviděl: 3. stupeň hlášen 15 hodin předem, vrchol 730 cm. A ve vícenásobné validaci byla chyba menší než u „bude jako teď“ na každé z 8 povodní.

### Z6 · Podle čeho model rozhoduje?

Graf `grafy/Z6_vahy_modelu.png`. Odpovídá Honza.

Každé políčko je váha jednoho vstupu: o kolik centimetrů se předpověď změní, když je hodnota o obvyklý rozkmit vyšší než průměr. Nejvíc váží Děčín teď (+88 cm) a Praha teď (+49 cm). Oranžová políčka vedle modrých znamenají, že model odečítá starší hodnotu od nové, tedy počítá, jestli voda stoupá.

### Z7 · Je rozliv hydraulický model?

Podklad `grafy/mapbox3_decin.jpg`. Odpovídá Honza.

Není. Porovnáváme výšku terénu (ČÚZK DMR 5G) s výškou hladiny a zaplavíme to, co je níž a spojené s řekou. Ověřeno proti úřední mapě záplavových území: při pětileté vodě náš rozliv 167 ha, úřední 183 ha, průnik 165 ha, shoda 0,89. Zdi a hráze pod rozlišením terénu nevidí.

### Z8 · Jak dopadl test?

Graf `grafy/Z8_test_2021_2025.png`. Odpovídá Ondra.

Test 2021 až 2025 jsme pustili jednou, na model vybraný předem a naučený na všem do 2020. Chyba při povodních 22,4 cm proti 50,2 u „bude jako teď“, o 55 % méně, a před 3. stupněm model varoval pokaždé. Neuronová síť tam vyšla o 1,1 cm lépe, výběr jsme podle testu neměnili, jinak by test přestal být nezávislý.

### Z9 · Proč jen 36 hodin dopředu?

Graf `grafy/Z9_doba_dobehu.png`. Odpovídá Dan.

Z nejvzdálenějších stanic, Berounu a Nespek na Sázavě, doteče voda do Děčína za 23 až 25 h, z Prahy za 17 h, z Ústí za 4 h. Voda, která do Děčína přijde později, ještě neprotekla žádnou naší stanicí, je v potocích nebo ještě nespadla, a z měření na řece ji nevidí nikdo. Proto je chyba na 36 h skoro dvakrát větší než na 24 h a dál by pomohla jen předpověď srážek. Doby jsou z korelace změn průtoku na trénovací části (`docs/DATA.md`).

### Z10 · Jak vypadá aplikace dnes?

Snímek `grafy/Z10_aplikace_dnes.png`. Odpovídá Honza.

Web field-zero.netlify.app se otevře rovnou na Dnešku: hladina v Děčíně a Ústí teď, předpověď na 12, 24 a 36 h s rozmezím nejistoty a vedle oficiální předpověď ČHMÚ. Na snímku z 24. 10. v 6:00: Děčín 84 cm, za 24 h 94 cm, ČHMÚ 90 cm. Data se stahují živě z ČHMÚ, chodí se zpožděním 1 až 3 h. Pokud porota chce, otevřeme web živě.

### Z11 · Proč je předpověď v grafu křivka, když je to lineární regrese?

Graf `grafy/Z11_primka_a_krivka.png`. Odpovídá Ondra.

Přímka je vztah mezi tím, co teče proti proudu, a hladinou v Děčíně, ne tvar v čase. Zjednodušeně s jedním vstupem: vlevo je každá hodina 2006–2018 jeden bod (průtok v Mělníku v tu hodinu a hladina v Děčíně o 24 h později, protože se učíme dvojice „co víme dnes“ a „co bylo zítra“) a přímka se jimi proloží jednou, hladina za 24 h = 111 + 0,41 × průtok v Mělníku. Vpravo se do té samé přímky každou hodinu dosadí nový průtok a body v čase dají křivku. Skutečný model má 98 vstupů, takže místo přímky v rovině je to vážený součet, který nejde nakreslit; pro jednu hodinu ho ukazuje slajd 5. Jedna stanice nestačí: po vrcholu jde jednovstupová přímka na 800 cm, protože nepozná, že voda už nepřibývá.

### Z12 · Jak je to s přímkou, když je vstupů 98?

Graf `grafy/Z12_jeden_a_98_vstupu.png`. Odpovídá Ondra.

S 98 vstupy nejde nakreslit přímku proti jednomu z nich, potřebovala by 98 os. Když ale na osu x dáme celý vážený součet, tedy předpověď modelu, a na osu y skutečnou hladinu o 24 h později, je model zase přímka a přesná předpověď leží na úhlopříčce. Na validaci (hodiny, které model neviděl, Děčín +24 h): s jediným vstupem (průtok v Mělníku) jsou body rozházené, průměrná chyba 26,5 cm, a nad 1. stupněm se přímka ohýbá vedle; s 98 vstupy leží těsně u úhlopříčky, 7,5 cm. Je to chyba přes všechny hodiny, při povodních je u Děčína na 24 h 15,5 cm (naše hlavní číslo 17,1 cm je průměr přes Děčín, Ústí a 12, 24, 36 h). Každý vstup zvlášť barevně do jednoho grafu dát nejde: mají různé jednotky (cm a m³/s) a přímka patří k jejich součtu, ne k jednomu z nich; po řekách sečtené příspěvky pro jednu hodinu ukazuje slajd 5.

