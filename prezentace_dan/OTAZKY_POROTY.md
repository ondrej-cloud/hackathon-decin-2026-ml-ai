# Otázky poroty a odpovědi

40 pravděpodobných otázek po 7 minutách prezentace. Odpovědi jsou psané krátce, s čísly a zdrojem. Čísla jsou chyba
hladiny během povodní v cm. „Validace“ = 4 vynechané povodně 2006–2011 a klidné roky 2019–2020, průměr přes Děčín
a Ústí × 12 / 24 / 36 h, pokud není napsáno jinak. „D24“ = jen Děčín za 24 h.

Nejpravděpodobnější podle `docs/PREZENTACE_7MIN.md`: 15, 29, 17, 12, 13, 1.

**Kterým grafem odpovědět** (ukázat graf místo slov působí nejlíp). Danovy grafy jsou v `prezentace_dan/grafy/`,
Ondrovy slajdy a záložní slajdy v `docs/grafy/prezentace/`:

| Otázka | Graf |
|---|---|
| 1 data mimo balíček | `03b_proc_externi_data.png` |
| 12 šťastná validace? | `08b_vicenasobna_validace.png` |
| 13 co je „jako teď“ | `Z2_co_je_jako_ted.png` |
| 15 proč lineární regrese | `Z1_srovnani_ctyr_modelu.png`, `04_predpoved_je_soucet.png` |
| 18 záporné váhy | `Z6_vahy_modelu.png` |
| 22 směs G3 | `G4_cerven_2013_g3_vs_tym.png` |
| 23 test, Boris | `08a_test_2021_2025.png`, `07_boris_2024.png` |
| 24 doba doběhu | `G1_stanice_doby_dobehu.png` |
| 25 proč nejvýš 36 h | `G2_chyba_podle_horizontu.png` |
| 29, 30 srážky | `Z3_proc_ne_srazky.png` |
| 32 nejistota | `Z4_jak_moc_se_pleteme.png` |
| 36 co dál, víc stanic | `G3_zacatek_vzestupu_stanice.png` |

## Data a jejich kvalita

**1. Odkud máte data a proč ne jen z balíčku?**
Hodinový archiv ČHMÚ 2006–2025, 12 stanic na Labi, Vltavě, Ohři a přítocích. Za 2024–2025 je na hodinu i na centimetr
stejný jako balíček (17 544 hodin, rozdíl 0). Balíček má nejvýš proti proudu Ústí (4 h před Děčínem) a jedinou povodeň.
Model naučený jako balíček (2 roky, jen stanice v kraji, napodobeno na letech 2017–2018) má chybu 44,6 cm a propásne
12 z 24 varování (4 povodně × 2 stanice × 3 horizonty), stejně špatně jako „bude jako teď“ (44,3). *Zdroj: docs/PREHLED.md (Data), docs/DATA.md (Kontrola správnosti), docs/POKUSY.md (pá 20:44 a 20:46, Honza).*

**2. Jak víte, že data jsou správná?**
Bilance vody sedí každý rok (Mělník = Vraňany + Kostelec, poměr 1,00; Děčín = 1,04–1,08 × Ústí), měrná křivka je
skoro stálá, mezi roky se jen mírně posouvá (při 300 m³/s je Děčín 218–227 cm), voda z Ústí do Děčína doteče každý rok za 4–5 h, žádné nulové
ani záporné hodnoty. Jediná chyba: Děčín 5.–8. 2. 2006, hladina 1 019 cm při průtoku 120 m³/s (led), vyřazená.
*Zdroj: docs/DATA.md, sekce Labe.*

**3. Neořezali jste povodně jako odlehlé hodnoty?**
Ne, povodně jsou to, co předpovídáme. Vyřadili jsme jen ověřenou chybu z 2/2006. Jednohodinové výkyvy (Vraňany 35 hodin
za 20 let, nejspíš jezy) jsme nechali, na model vliv nemají. *Zdroj: docs/DATA.md.*

**4. Proč až od roku 2006 a ne s povodní 2002?**
Hodinově je celá sada stanic až od 2006 (Kostelec, Nymburk). Povodeň 8/2002 nemá v hodinových datech hladinu v Děčíně
ani v Ústí. Denní data od 1887 by rozmazala vlnu, která do Děčína putuje 4–40 h. *Zdroj: docs/DATA.md (Starší povodně).*

**5. Co je měřené, hladina, nebo průtok?**
Hladinu ČHMÚ měří čidlem na vodočtu, průtok z ní dopočítá měrnou křivkou. Předpovídáme hladinu v cm (podle ní se
vyhlašují stupně), proti proudu bereme průtoky, protože se po proudu sčítají a hladina je místní (koryto, jezy).
*Zdroj: docs/DATA.md, docs/PREHLED.md (Co ve vstupech není).*

## Únik informací

**6. Nepoužívá model informace z budoucnosti?**
Vstupy jsou jen to, co je v čase vydání změřené: hladina a průtok teď a 1–36 h zpět. Řádky, jejichž vstupy nebo cíl
zasahují do jiné části dat, vyhazujeme, škálování se učí jen na tréninku. Kontrola našla dvě pasti a obě jsme opravili:
doplňování děr (bralo hodnotu z budoucnosti) a denní srážky (úhrn je známý až další den v 07:00 UTC).
*Zdroj: docs/CESTA_MODELU.md §3, docs/PREZENTACE_7MIN.md (slajd 6), ridge_dan/ZPRAVA.md (Data).*

**7. Proč model pro Ústí používá Děčín, který je níž po proudu?**
Hladina v Děčíně je známá ve stejném okamžiku, není z budoucnosti. Je to tatáž voda změřená o 4 h později, model si tím
vyhlazuje šum měření. *Zdroj: docs/POROZUMENI.md.*

**8. Jak víte, že jste se nenaladili na validaci?**
Pravidla jsme dali předem: jedna změna s důvodem, zlepšení aspoň o 1 cm, po třech neúspěších konec. Finální model jsme
zapsali před testem (pá 20:58) a test pustil jen Ondra, jednou (21:00). U Danovy regrese s 30 stanicemi rozhodovala CV
v tréninku, do validace nahlédl 4×, všechno zapsal a přiznal, že rozbor validace ovlivnil směr hledání. Pozdější pokusy
hodnotil přísným LOFO. *Zdroj: docs/PREHLED.md (Rozhodnutí), ridge_dan/ZPRAVA.md.*

**9. Kontroloval to někdo jiný než autor?**
Ano. Nezávislá kontrola řetězce (subagent kontrolor) a u Danových větví Codex, jen pro čtení. Našly třeba povodeň, která
u 36 h vypadla z varování, a dobu doběhu LightGBM odhadnutou i z drženého bloku CV. Kód je opravený a hlavní výsledky přepočítané.
Přepočet tří vnořených variant (B, D, G2) po opravě nedoběhl a týmové pevné doby doběhu LightGBM zůstávají výhradou,
obojí je zapsané.
*Zdroj: docs/CESTA_MODELU.md §3, ridge_dan/STANICE_VSEM.md (Nálezy Codexu), ridge_dan/ZLEPSENI.md.*

## Rozdělení a validace

**10. Proč nedělíte data náhodně?**
Sousední hodiny jsou skoro stejné. Model by je znal z tréninku a výsledek by byl falešně dobrý. Dělíme v čase a kolem
validačních povodní vynecháváme 20 dní. *Zdroj: docs/DENIK.md (pá 19:20, Ondra).*

**11. Proč validujete na starých povodních, a ne na posledních letech?**
V letech 2016–2020 nebyla v Děčíně ani jedna povodeň. Validace jsou proto 4 vynechané povodně (4/2006, 3/2009, 9/2010,
1/2011) a klidné roky 2019–2020. Test je 2021–2025 s povodněmi 2/2021, 12/2023, 2/2024 a 9/2024. *Zdroj: docs/PREHLED.md.*

**12. Nemáte výsledek jen ze šťastně vybrané validace?**
Ověřili jsme to dvakrát. Ve vícenásobné validaci (každá z 8 povodní 2006–2020 jednou vynechaná) má regrese 20,1 ± 7,7 cm
a „jako teď“ 45,2 cm, tedy o 55 % méně, stejně jako na testu. Danova LOFO přes 22 povodní: týmová regrese D24 15,29 cm.
Chyba víc záleží na povodni (3/2009 11 cm, 6/2013 34 cm) než na modelu. *Zdroj: docs/PREHLED.md, ridge_dan/ZLEPSENI.md.*

**13. Proč hodnotíte chybu jen během povodní?**
Na klidné řece je skoro přesné i „bude jako teď“: přes celou validaci (většina hodin je klid) má chybu 12,8 cm proti
8,2 cm u regrese. Při povodni se ale plete o metr. Hodnotíme proto okno 7 dní před vrcholem až 5 dní po něm a varování před 2. a 3. stupněm. *Zdroj: docs/POKUSY.md
(pá 20:15, srovnání čtyř modelů), docs/PREHLED.md.*

**14. Čtyři povodně na validaci, není to málo?**
Je, proto rozdíly do 1–2 cm bereme jako náhodu a zlepšení počítáme až od 1 cm. Proto jsme přidali vícenásobnou validaci
(8 povodní) a Dan LOFO (22 povodní). *Zdroj: docs/POROZUMENI.md, ridge_dan/ZLEPSENI.md.*

## Proč lineární model

**15. Proč lineární regrese, a ne neuronová síť?**
Fyzika je součet: voda v Děčíně je zhruba Vltava + horní Labe + Ohře, každá posunutá o dobu doběhu. Přesně to je
lineární regrese a ohyb měrné křivky dostane přes odmocninu průtoků. Ověřeno třikrát: validace 17,1 (síť 17,8),
vícenásobná validace 20,1 (21,0), test 22,4 (21,3). Síť je stejná jen v rámci náhody. Regrese je jednodušší, má méně
chyb ve varování a každou váhu vysvětlíme. *Zdroj: docs/POROZUMENI.md, docs/CESTA_MODELU.md §7.*

**16. Proč ne LightGBM, když bývá na tabulková data nejlepší?**
Stromy předpovídají jen hodnoty, které viděly: u povodně 2013 vrchol 823 místo 1 072 cm. Na 98 syrových vstupech si
pamatoval povodně z tréninku (starší běh, Děčín +12 h: trénink 4,7 cm, validace 27,8 cm). S fyzikálně připravenými vstupy 23,1 cm, pořád o 6 cm
horší než regrese. A když opravoval zbytek po regresi, ještě ji zhoršil (17,1 → 18,7).
*Zdroj: docs/POKUSY.md (pá 19:45–20:15, so 0:48), docs/CESTA_MODELU.md §1.*

**17. Nepřeučil se váš model?**
Obvyklý znak přeučení nemá: na trénovacích povodních má chybu 19,7 cm, na validačních 15,5 cm (D24), bez regularizace
vyjde totéž, 98 vah se odhaduje ze 108 tisíc hodin. Úplně vyloučit to ale nejde, sousední hodiny nejsou nezávislé, proto
hodnotíme na celých vynechaných povodních (viz N3). Přeučení jsme viděli u sítě 64-32 (starší rozbor D24 při velké vodě: trénink 5, validace 22 cm) a u polynomu (19,9 a 22,8).
*Zdroj: docs/POKUSY.md (so 0:48), docs/CESTA_MODELU.md §2.*

**18. Proč jsou některé váhy záporné?**
Sousední zpoždění jsou skoro stejná (průtok v Praze teď a před 3 h má korelaci 0,998). Model odečítá starší hodnotu od
novější, takže počítá, jestli voda stoupá. *Zdroj: docs/POKUSY.md (so 0:48), docs/POROZUMENI.md.*

**19. Co znamená „Ridge“ a jak jste zvolili alphu?**
Ridge mírně penalizuje velké váhy. Na našich datech na alfě skoro nezáleží (alpha 0,1 až 10 dává stejný výsledek), je to
pojistka proti velkým protichůdným vahám u skoro stejných zpoždění. *Zdroj: docs/POROZUMENI.md, docs/CESTA_MODELU.md §2.*

## Výběr modelu a test

**20. Kdy a jak jste vybrali finální model?**
V pátek ve 20:58, zapsané před testem: lineární regrese, protože je nejlepší na validaci, nejjednodušší a bez planých
poplachů. Test 2021–2025 jednou ve 21:00: 22,4 cm proti 50,2 u „jako teď“, o 55 % méně. *Zdroj: docs/PREHLED.md.*

**21. Síť byla na testu lepší (21,3). Proč jste ji nevzali?**
Kdybychom vybírali podle testu, test by přestal být nezávislý. Rozdíl 1,1 cm je menší než kolísání sítě: ve vícenásobné validaci
byla síť o 0,9 cm horší a mezi seedy kolísá na validaci až o 2,8 cm (seedy 42–44: 19,0 ± 1,2 cm, týmových 17,8 je seed 42). *Zdroj: docs/PREHLED.md, sit_dan/SIT_VARIANTY.md.*

**22. Dan má směs G3, která je v LOFO lepší. Proč není finální?**
G3 (½ regrese s 30 stanicemi + ½ LightGBM s 30 stanicemi) má v LOFO 13,94 proti 15,29 cm, lepší u 20 z 22 povodní. Na
validaci D24 je ale horší (18,2 proti 15,5), v oknech povodní LOFO má víc planých poplachů (6 proti 4), jsou to dva modely a nemá
nezávislý test. Ve vícenásobné validaci 19,6 proti 20,1, lepší 6 z 8 (p ≈ 0,29, mohlo by to vyjít i náhodou). Ukazujeme ji jako ověřený směr,
ne jako finále. *Zdroj: ridge_dan/ZLEPSENI.md, ridge_dan/VALIDACE_ONDRA.md.*

**23. Jak model dopadl na testu podrobně?**
Děčín +12 / +24 / +36 h: 10,2 / 17,5 / 29,9 cm („jako teď“ 23,3 / 44,8 / 65,5). Před 3. stupněm varoval pokaždé (3 z 3),
v průměru 11 / 21 / 27 h předem. Boris 9/2024: od vydání prvního varování před 3. stupněm do skutečného překročení uběhlo 27 h (model překročení čekal
o 3 h dřív, viz N11), vrchol 649 cm předpověděl na 611 cm.
*Zdroj: docs/PREHLED.md (Finální model na testu podrobně).*

## Fyzika a doba doběhu

**24. Za jak dlouho doteče voda do Děčína?**
Podle korelace změn průtoku na trénovací části: Ústí 4 h, Kostelec a Nymburk 10 h, Mělník a Vraňany 13 h, Louny 16 h,
Praha-Chuchle 17 h, Jizera a Přelouč 18 h, Beroun 23 h, Sázava 25 h. Vrcholy velkých povodní putují různě, z Vraňan do
Ústí jednou 12 h, jindy 45 h. *Zdroj: docs/DATA.md (Doba doběhu), docs/POROZUMENI.md, graf grafy/G1.*

**25. Proč předpovídáte nejvýš 36 h dopředu?**
Voda, která do Děčína přijde za víc než asi 40 h, ještě neprotekla žádnou naší stanicí. Je v potocích nebo ještě
nespadla, a už na 36 h jí část chybí. Proto je chyba na 36 h skoro dvojnásobná (Děčín, validace 26,0 proti 15,5 cm na 24 h). *Zdroj: docs/POROZUMENI.md,
docs/PREHLED.md, graf grafy/G2.*

**26. Když se vlna při povodni zpomalí, proč to model nepoužívá?**
Zkusili jsme to a nepomohlo to (21,8 vs 22,2 cm, pod hranicí 1 cm). Lineární model má 98 zpožděných hodnot (průtok
12 stanic 0–36 h a hladina Děčína a Ústí 0–24 h, vždy 7 zpoždění) a dobu doběhu včetně roztažení vlny si z vah najde sám. Zpomalení při velkých povodních nejde
spolehlivě změřit – nad 1 500 m³/s je v tréninku jen jedna povodeň (6/2013, 227 h). *Zdroj: docs/POROZUMENI.md,
docs/POKUSY.md (pá 20:45).*

**27. K čemu je fyzikální model, když je nejhorší?**
Ukazuje, že učené modely nedělají nic magického. Samotné doby putování a měrná křivka dají 24,8 cm (o 44 % méně než
„jako teď“), regrese je fyziku jen zpřesňuje na 17,1. *Zdroj: docs/PREHLED.md, docs/CESTA_MODELU.md §2.*

**28. Jak víte hladinu, když neznáte šířku a tvar koryta?**
Šířku potřebujeme jen tam, kde hladinu předpovídáme, a tam ji model zná z 20 let hodin (Děčín 76 až 1 072 cm). Proti
proudu bereme průtok v m³/s a ten na šířce koryta nezávisí. Selže, když se koryto změní (led 2/2006) nebo když voda
vystoupí výš než kdy v tréninku. *Zdroj: docs/POROZUMENI.md.*

## Srážky

**29. Proč nepoužíváte srážky?**
Zkusili jsme je třikrát. Denní srážky, sníh a teplota z 25 stanic: 17,1 → 17,4. Dokonalá předpověď deště na 3 dny:
jen −1,0 cm a varování nepřišlo dřív. Šestihodinové srážky ze SYNOP: beze změny u všech tří modelů. Na 12–36 h je voda
z deště už v řekách a model ji vidí v průtocích proti proudu.
*Zdroj: docs/PREHLED.md, docs/CESTA_MODELU.md §6, srazky_dan/ZPRAVA_SRAZKY.md.*

**30. Povodně ale dělá déšť, ne?**
Ano, ale předpovídáme jen 12–36 h a na to stačí změřit, co z deště už teče. U Borise přestalo pršet 17. 9. ráno a vrchol
649 cm byl 18. 9. v 18:00 UTC: kdo předpovídal vrchol 24 h předem, žádný další déšť nečekal. Srážky by pomohly na 2–5 dní
u dešťových povodní (9/2010 s dokonalou předpovědí o 23 % lépe na 36 h a o 40 % na 72 h), jenže archiv předpovědí na
trénink nemáme. *Zdroj: docs/POROZUMENI.md, docs/CESTA_MODELU.md §6.*

**31. Proč nepomohly ani šestihodinové srážky, které jsou známé hodinu po konci období (některé díly později)?**
Úplnou řadu má jen 9 stanic (2 u Děčína, 7 proti proudu), u 12 z 21 stanic v NOAA ISD po roce ~2013 chybí suché termíny.
Na bouřky je to málo bodů a déšť, který spadl dřív, už ukážou vodoměry. LightGBM se srážkami přestřelil 9/2010 (575 místo
526 cm) a dal 4 plané poplachy 3. stupně. *Zdroj: srazky_dan/ZPRAVA_SRAZKY.md.*

## Nejistota

**32. Jak moc se předpovědi dá věřit?**
Rozmezí „nejspíš od–do“ je z 5. a 95. percentilu chyb na tréninku podle výšky hladiny. Na validaci se do něj vejde
89–92 % hodnot celkem, na povodních 76–88 %. Šířka na povodních: Děčín 33 / 53 / 72 cm (12 / 24 / 36 h). Na povodních je
užší, než by mělo být, a přísnější kontrola na 22 povodních to potvrdila: 90% pásmo aplikace pokrylo jen 72–83 % hodin
(80% stejnou metodou 58–72 %). Dan v noci připravil pásmo z chyb mimo trénink, které pokrývá 78–80 % a 94–95 % (cíl 80 a 95 %), slabé zůstává
na rychlém vzestupu (59–72 %). Jestli ho tým dá do aplikace, rozhodne ráno (viz N18).
*Zdroj: docs/POKUSY.md (pá 20:40, Honza), nejistota_dan/ZPRAVA_NEJISTOTA.md (větev dan-nejistota).*

**33. Je chyba 16 cm hodně?**
Za 24 h se voda při povodni změní v průměru o 35 cm a nejvíc o 1,7 m. Stupně v Děčíně jsou od sebe 90 a 70 cm
(400 / 490 / 560), chyba 13,6 cm (v celých validačních oknech Děčína; hlavní číslo D24 je 15,5 cm) je menší. Do ±20 cm je 76 % předpovědí na 24 h. *Zdroj: docs/POROZUMENI.md (Jak číst výsledky).*

## Slabiny

**34. Kde model selhává?**
Na 36 h (Děčín 26,0 cm; přes Děčín a Ústí je při vodě nad 1. stupněm do ±20 cm jen 51 % předpovědí). Vrcholy velkých povodní podhodnocuje (test 9/2024: 649 cm
předpovězeno na 611; na testu D24 bias na povodních −10,5 cm, chyba vrcholu 21,4 cm), velké povodně jsou v tréninku
jen dvě (8/2010, 6/2013). Povodně z deště v kraji (8/2010) nevidí. Na testu propásl 2. stupeň v únoru
2024 (vrchol 496 cm, práh 490). *Zdroj: docs/PREHLED.md, docs/POROZUMENI.md (Co model umí a co ne).*

**35. Proč je na testu chyba větší než na validaci (22,4 proti 17,1)?**
Testové povodně stoupaly rychleji, i „jako teď“ je na testu horší (50,2 proti 44,3). Zlepšení proti laťce je podobné
(55 % proti 61 %). *Zdroj: docs/CESTA_MODELU.md §5.*

**36. Co byste dělali dál?**
Předpověď srážek ČHMÚ pro 2–3 dny u dešťových povodní. Víc stanic proti proudu: Danova regrese s 30 stanicemi dala na
jednorázovém testu D24 16,1 proti 17,5 cm a nejvíc pomáhá na začátku vzestupu (27,0 proti 32,0). Dvoustupňové varování:
předběžné podle horní meze nejistoty, ostré podle předpovědi. *Zdroj: docs/CESTA_MODELU.md §8, ridge_dan/ZPRAVA.md.*

## Aplikace a provoz

**37. Funguje to i dnes na živých datech?**
Ano. Přepínač „Dnešek“ stáhne operativní data ČHMÚ (10–30 min stará, vydání je 1–2 h za skutečným časem) a vedle naší
předpovědi ukáže oficiální předpověď ČHMÚ. Mělník a Nymburk operativně nejsou celé, dopočítáme je z bilance vody. Na
validaci to D24 zhorší z 15,5 na 16,9 cm. Provozní test v noci: ČHMÚ zveřejňuje data po 20 min, hodnota z celé hodiny
je u všech stanic venku nejpozději v HH:40, proto počítat v HH:45 (to platí pro okamžité hodnoty v celou hodinu;
aplikace bere hodinový průměr t:00–t:50, ten je kompletní později, je potřeba to sladit). Za posledních 29 dní nízké vody byla oficiální
předpověď ČHMÚ přesnější než naše (D24 5,0 proti 7,5 cm), náš model při nízké vodě kmitá; na povodních srovnání nemáme.
*Zdroj: docs/DENIK.md (pá 21:30, Honza), ridge_dan/PROVOZ.md (koncept, větev dan-ridge).*

**38. Ta modrá plocha na mapě je váš hydraulický model?**
Ne. Model předpoví hladinu, převedeme ji na průtok (naše měrná křivka, do 3 % od oficiální) a ukážeme oficiální záplavové
území DIBAVOD pro nejvyšší N-letou vodu, které předpovězený průtok dosáhne. Plynulý rozliv po 10 cm je z výškového modelu ČÚZK DMR 5G, s DIBAVOD se shoduje
na IoU 0,82–0,90. Vlastní hydrauliku jsme záměrně nedělali. *Zdroj: docs/DENIK.md (pá 21:40), docs/DATA.md, CLAUDE.md (Stav).*

**39. Jak rychlé je to a jak to udržujete aktuální?**
Regrese se natrénuje za 1 s (všech 6 kombinací), předpověď je okamžitá. Pro dnešek je připravený model učený na všech datech
do 2025 (`ridge_vse`, `src/uloz_model.py --vse`), v menu aplikace ho je ale potřeba zvolit: výchozí je `ridge` učený
do 2018, který slouží k přehrávání povodní. *Zdroj: docs/POKUSY.md (pá 20:15), CLAUDE.md (Stav), docs/DENIK.md (pá 21:30), app/app.py.*

## Odpovědnost za varování a licence

**40. Kdo odpovídá za to, když model nevaruje? A smíte data ČHMÚ použít?**
Náš model není oficiální předpověď a za oficiální ho nevydáváme, proto aplikace vedle něj ukazuje předpověď ČHMÚ. Je to
doplňková informace na přípravu den předem. Oficiální hydrologické předpovědi vydává ČHMÚ a stupně povodňové aktivity
vyhlašují povodňové orgány obcí a krajů podle vodního zákona (č. 254/2001 Sb.). Tohle v repu podložené nemáme, je to
obecná znalost a je dobré ji ověřit u mentora. Data: otevřená data ČHMÚ jsou pod licencí CC BY 4.0, podmínkou je uvést autora
a licenci (v aplikaci „Měření a N-leté průtoky © ČHMÚ“). Open-Meteo je pod CC BY 4.0, záplavová území DIBAVOD (VÚV TGM) uvádíme,
DMR 5G jsou otevřená data ČÚZK, srážky NOAA ISD jsou dílo vlády USA bez omezení,
jen data výměny WMO jsou podle Resolution 40 pro nekomerční použití s uvedením zdroje.
*Zdroj: docs/DENIK.md (pá 21:30), ridge_dan/ZPRAVA.md (Data), app/mapbox_mapa.py (atribuce), docs/DATA.md,
srazky_dan/ZPRAVA_SRAZKY.md.*

## Nejtěžší otázky (simulace přísné poroty)

Otázky vymyslel Codex jako přísná porota z těchto podkladů (`codex/porota_codex.md`), odpovědi jsou zpřesněné
a ověřené ve zdrojích. Pravidlo pro všechny: říct poctivě, co nevíme, a neprodávat víc, než čísla unesou.

**N1. „17,1 cm počítáte jen v oknech kolem povodní, jejichž vrchol znáte až zpětně. Co tím měříte?“**
Měříme přesnost během povodní, protože tam na předpovědi záleží: okno 7 dní před vrcholem až 5 dní po něm u povodní
nad 2. stupněm, průměr přes Děčín a Ústí a 12 / 24 / 36 h. Okna slouží jen k hodnocení, do vstupů nic z budoucnosti
nevstupuje. Přes všechny validační hodiny je to 8,2 proti 12,8 cm u „jako teď“. Jak moc výsledek závisí na délce oken,
jsme nezkoušeli. *Zdroj: src/evaluate.py (vyhodnot), docs/POKUSY.md (pá 20:15).*

**N2. „Proč zrovna tyhle 4 validační povodně? A proč jednou ukazujete 4, jindy 8 a jindy 22 povodní?“**
Validaci jsme vybrali tak, aby v tréninku zůstala největší povodeň 2013 a ve validaci byly dvě velké a dvě menší
(4/2006, 3/2009, 9/2010, 1/2011); v letech 2016–2020 žádná povodeň nebyla. Čtyři je málo, proto vícenásobná validace (8 povodní
nad 2. stupněm, každá jednou vynechaná) a LOFO (22 povodní nad 400 cm). Jsou to různé sady povodní, čísla se nedají
zaměňovat: týmová regrese D24 má 15,5 (validace), 18,5 (vícenásobná) a 15,29 cm (LOFO). Pořadí regrese, sítě, LightGBM
a fyziky je ve validaci i ve vícenásobné validaci stejné, v LOFO D24 je síť o 0,2 cm lepší než regrese. *Zdroj: docs/DATA.md (Rozdělení), ridge_dan/VALIDACE_ONDRA.md, ridge_dan/ZLEPSENI.md.*

**N3. „108 tisíc hodin není 108 tisíc nezávislých příkladů. Jak víte, že se lineární model nepřeučil?“**
Máte pravdu, sousední hodiny jsou skoro stejné (průtok v Praze teď a před 3 h má korelaci 0,998). Na tréninku nemá
regrese menší chybu než na validaci (D24 19,7 proti 15,5 cm), takže obvyklý znak přeučení chybí, ale vyloučené tím
přeučení není. Proto hodnotíme na celých vynechaných povodních (vícenásobná validace, LOFO), ne na hodinách. Kolik je
nezávislých situací, jsme neodhadovali. *Zdroj: docs/POKUSY.md (so 0:48).*

**N4. „Povodeň 2006 předpovídáte modelem, který se učil i na roce 2013. To jste v roce 2006 neměli.“**
Ano, validace a LOFO jsou zpětné: měří, jestli se model přenese na povodeň, kterou neviděl, ne jak by fungoval tehdy.
Chronologicky poctivý je test 2021–2025 s tréninkem jen do konce 2020: 22,4 proti 50,2 cm. Postupné posouvání tréninku
v čase jsme nedělali. *Zdroj: docs/PREHLED.md (Finální test), docs/POKUSY.md (pá 23:27).*

**N5. „Doby doběhu odhadujete z dat. Z jakých? A jsou po opravách přepočítaná všechna čísla?“**
U nových stanic v LightGBM se doba původně odhadla i z drženého bloku CV, po opravě jen z trénovací části foldu (CV
16,20 → 16,01 cm). Týmové doby LightGBM jsou pevné z celého tréninku 2006–2018, to zůstává výhradou. Přepočet tří
vnořených variant (B, D, G2) po nálezu kontroly nedoběhl, jejich čísla jsou před opravou a za výsledek je nevydáváme.
Finální lineární regrese doby doběhu vůbec nepoužívá, váhy zpoždění si najde sama. *Zdroj: ridge_dan/STANICE_VSEM.md,
ridge_dan/ZLEPSENI.md.*

**N6. „Jak může být test 2021–2025 nedotčený, když jste lineární model ráno zkoušeli i na povodních 2023 a 2024?“**
Poctivě: v průzkumu před stanovením rozdělení (pá 17:46–18:44, data 2004–2025) jsme lineární model zkoušeli i na
povodních 12/2023 a 9/2024. To ovlivnilo volbu úlohy a typu modelu. Konkrétní model (vstupy, rozdělení, odmocnina,
alpha) jsme ale zafixovali a zapsali před spuštěním testu (20:58) a test pustili jednou (21:00). Proto se opíráme
i o vícenásobnou validaci bez testových let, která dala stejné zlepšení, o 55 %. *Zdroj: docs/POKUSY.md (pá 17:46),
docs/NAPAD_LABE.md, docs/PREHLED.md.*

**N7. „Proč test nepustíte znovu? A když mu věříte, proč nevezmete síť, která na něm byla lepší?“**
Znovu pustit stejný zmrazený model nic nového neřekne. Problém by byl vybírat podle známého testu, proto síť
(21,3 proti 22,4 cm) nebereme, i když na testu vyšla lépe. Danův model s 30 stanicemi měl jeden vlastní test D24
(16,1 proti 17,5), ale G3 a H30 vznikly až potom, test nemají a známý test jim nové potvrzení dát nemůže. Na to by bylo
potřeba nové období, třeba sledovat předpovědi v příštích povodních. *Zdroj: docs/PREHLED.md, ridge_dan/ZPRAVA.md.*

**N8. „Po desítkách pokusů jste našli G3 a H30. Není to jen šťastný výběr?“**
To riziko je skutečné, na 24 h bylo asi 15 variant. Proto G3 neprohlašujeme za lepší model: v LOFO je lepší (13,94
proti 15,29 cm, 20 z 22 povodní), na validaci D24 horší (18,2 proti 15,5) a ve vícenásobné validaci jen o 0,5 cm
lepší. H30 je výslovně průzkumný, nápad vznikl z povodně 2006, která je mezi hodnocenými. Naše pravidlo „aspoň 1 cm“
není statistická korekce na mnoho pokusů. *Zdroj: ridge_dan/ZLEPSENI.md, ridge_dan/ROZHODNUTI_G3.md.*

**N9. „Co znamená vaše p = 0,0001? A ± 7,7 cm?“**
Znaménkový test říká, jak nepravděpodobné by bylo vyhrát u 20 z 22 povodní, kdyby oba modely byly stejně dobré a
povodně nezávislé. Velikost rozdílu neměří: nejhorší zhoršení G3 je 8,2 cm a v oknech povodní má 6 planých poplachů
proti 4. Osm povodní vícenásobné validace je podmnožina těch 22, takže 6 z 8 (p ≈ 0,29) není nezávislé zopakování.
± 7,7 cm je směrodatná odchylka mezi povodněmi, ne interval spolehlivosti průměru. *Zdroj: ridge_dan/ZLEPSENI.md,
ridge_dan/VALIDACE_ONDRA.md.*

**N10. „Síť uvádíte 17,8 cm. Proč ne průměr přes seedy?“**
17,8 je týmový běh se seedem 42. Přes seedy 42–44 má síť 19,0 ± 1,2 cm (17,8–20,6), proto rozdíl 0,7 cm proti
regresi není pevné pořadí, a i proto jsme vybrali jednodušší regresi. Regrese a LightGBM náhodu nemají, nulový rozptyl
mezi seedy u nich ale neříká nic o nejistotě na nové povodni. *Zdroj: sit_dan/SIT_VARIANTY.md.*

**N11. „Předpověď na 24 h hlásila Borise 27 h předem? Vaše metrika přece předstih omezuje na 24 h.“**
Obojí platí, jsou to dvě různá čísla. Předpověď vydaná 14. 9. 2024 v 11:00 na 15. 9. 11:00 dala 577 cm, nad
3. stupněm (560); skutečně bylo 551 cm a práh voda překročila o 3 h později. Od vydání varování do skutečného překročení
tedy uběhlo 27 h, model ale překročení čekal o 3 h dřív. Metrika v tabulkách dřívější hlášení počítá nejvýš jako
horizont, protože je to chyba načasování; na testu je předstih 3. stupně D24 v průměru 21 h.
*Zdroj: docs/grafy/prezentace/README.md (graf 4), src/evaluate.py (varovani), docs/PREHLED.md.*

**N12. „Hodnota v 10:00 je měření dostupné v 10:00, nebo průměr do 10:50? Kolik předstihu reálně zbude?“**
Archivní hodina t je průměr t:00 až t:50, takže v t:00 ještě celá známá není. Operativní data ČHMÚ chodí 10–30 min
po měření a vydání předpovědi je 1–2 h za skutečným časem. Když data přijdou se zpožděním d hodin, zbývá předpovědi
na 24 h jen 24 − d h. V noci jsme zpoždění změřili na provozních datech: poslední hodnota je při zveřejnění stará 10–20 min a celá
hodina je venku do HH:40. Kdyby aplikace počítala v HH:00 a chybějící hodinu doplnila poslední hodnotou, zhorší se LOFO
D24 o 1,8 cm (ztratí se trend), proto počítat v HH:45 z okamžitých hodnot; pro hodinový průměr t:00–t:50 až později. Zpoždění během povodně jsme neměřili. *Zdroj: docs/DATA.md (Aktuální data),
docs/DENIK.md (pá 21:30).*

**N13. „Učíte se na archivních průtocích, které ČHMÚ po povodni opravil. V provozu je nemáte.“**
Ano, archiv je zpětně ověřený a průtok je dopočtený z hladiny měrnou křivkou, která se mezi roky posouvá (při
1 000 m³/s je Děčín 453–478 cm). Předběžné hodnoty z doby povodní nemáme, takže rozdíl jsme nezměřili. Naše čísla jsou
proti provozu spíš optimistická a nemůžeme vyloučit, že by se pořadí modelů změnilo. *Zdroj: docs/DATA.md (Hladina je
měřená, průtok dopočtený), docs/POROZUMENI.md (Co model umí a co ne).*

**N14. „V provozu vypadne stanice. Co uděláte?“**
Dvě stanice dopočítáváme už teď (Mělník a Nymburk operativně nejsou celé), na validaci to zhorší D24 z 15,5 na 16,9 cm
a +12 h z 9,0 na 10,8 cm. Jiné výpadky ani jejich souběh jsme nezkoušeli. Pro model s 30 stanicemi je navržené pravidlo:
při výpadku kterékoli nové stanice spadnout zpět na týmový model. V provozu by aplikace musela jasně odlišit platnou,
náhradní a nevydanou předpověď. *Zdroj: docs/DATA.md (Aktuální data), ridge_dan/ROZHODNUTI_G3.md (bod d).*

**N15. „Z pár hrubých srážkových vstupů usuzujete, že déšť nepomáhá. Není to moc silné tvrzení?“**
Je, proto ho říkáme úzce: vyzkoušené reprezentace srážek nepomohly. Denní srážky 17,1 → 17,4, dokonale známé srážky na
3 dny 16,1, šestihodinové ze 9 stanic v LOFO pod 0,1 cm u regrese a asi −0,5 cm u LightGBM. Neznamená to, že nepomůže
radar nebo jiný model: u dešťové povodně 9/2010 by dokonalá předpověď na 36 h pomohla o 23 %. *Zdroj: docs/POKUSY.md
(pá 20:44, 22:32, 22:46), srazky_dan/ZPRAVA_SRAZKY.md.*

**N16. „Na slajdu přičítáte centimetry od Vltavy, horního Labe a Mělníka. Mělníkem ale voda z Vltavy a Labe už protekla,
není to dvojí počítání?“**
Je to rozklad lineární předpovědi na příspěvky skupin vstupů proti průměrnému stavu, ne bilance vody. Mělník,
Vltava a horní Labe nesou zčásti stejnou vodu, takže příspěvky jsou statistické a korelované, ne nezávislé příčiny.
Model zachování vody nevynucuje, sčítá škálované odmocniny průtoků a hladiny. Správně je říkat „kolik centimetrů
přidá každá skupina vstupů“. *Zdroj: docs/PREZENTACE_7MIN.md (slajd 4), src/models/ridge.py.*

**N17. „Proč věřit předpovědi příští rekordní povodně, když 2002 nemáte a v tréninku jsou velké povodně dvě?“**
Neumíme to zaručit. Když jsme povodeň 2013 vynechali, předpověděla týmová regrese na vrcholu 1 072 cm jen 952 cm
(G3 965) a 80% pásmo nejistoty tam pokrylo jen 42 % hodin. Lineární model aspoň pokračuje v trendu, stromy ne, ale při
ledu, změně koryta nebo rekordu je to extrapolace bez záruky. *Zdroj: prezentace_dan/grafy/README.md (G4),
nejistota_dan/ZPRAVA_NEJISTOTA.md.*

**N18. „Pásmo nejistoty slibuje 90 %, při povodni se do něj vejde míň. Proč ho ukazujete?“**
Dnešní pásmo v aplikaci je z chyb na trénovacích datech. Ve vnořené kontrole na 22 povodních pokrylo 90% pásmo, které
aplikace ukazuje, jen 72–83 % hodin (80% stejnou metodou 58–72 %, na začátku vzestupu 15 %). Dan v noci připravil pásmo z chyb mimo trénink: pokrývá 78–80 %
a 94–95 % (cíl 80 a 95 %), na rychlém vzestupu ale jen 59–72 % a u rekordní povodně 2013 42 %. Je to orientační
rozmezí, pravděpodobnost překročení stupně z něj nepočítáme. *Zdroj: nejistota_dan/ZPRAVA_NEJISTOTA.md, docs/POKUSY.md
(pá 20:40).*

**N19. „O 55 % lepší než ‚bude jako teď‘. Ale jste lepší než ČHMÚ?“**
To nevíme, historické předpovědi ČHMÚ s časy vydání nemáme, a netvrdíme to. Laťka „jako teď“ je jednoduchá, proto
jsme zkoušeli i pokračování trendu (39,4 cm a v Děčíně 2 / 5 / 16 planých poplachů) a fyzikální model (24,8 cm). V režimu
Dnešek ukazujeme naši předpověď vedle oficiální ČHMÚ: za 29 dní nízké vody (podzim 2026) byla ČHMÚ přesnější
(D24 5,0 proti 7,5 cm). Spravedlivé srovnání na povodních by chtělo stejné časy vydání a stejná data.
*Zdroj: docs/POKUSY.md (pá 19:35), docs/POROZUMENI.md, docs/DENIK.md (pá 21:30).*

**N20. „Kdo odpovídá, když na základě vaší aplikace někdo nevaruje? A máte vyřešené licence všech dat?“**
Je to studentský doplňkový nástroj, ne systém pro rozhodování o varování, a tak ho i prezentujeme. Provozní odpovědnost
ani postup jsme neřešili, oficiální předpověď dává ČHMÚ (právní výklad je potřeba ověřit u mentora). Rozliv má proti
DIBAVOD shodu IoU 0,82–0,90, proti skutečnému rozlivu ověřený není. Licenci CC BY 4.0 máme doloženou u ČHMÚ a
Open-Meteo; úplné právní posouzení všech zdrojů a nasazení nemáme. *Zdroj: otázka 40, docs/DATA.md,
ridge_dan/ZPRAVA.md (Data).*
