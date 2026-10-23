# Dá se ze stanic vytěžit zlepšení, které projde přísným hodnocením?

Dan, větev `dan-ridge`, pá 23. 10. 2026 23:15 – so 00:30. Kód `ridge_dan/zlepseni/` (motor `lofo.py`, pokusy
`pokus_<X>.py`, výsledky `vysledky_<X>.json`, zápisy `pokus_<X>.md`), směsi od Codexu v `ridge_dan/smesi/`.
Test 2021–2025 je spotřebovaný, nespouštěl se a nic se podle něj nerozhodovalo.

## Verdikt

**Děčín +24 h: přísné pravidlo průkazně splní směs G3 = ½ Ridge 30 stanic + ½ LightGBM 30 stanic** (pevná
váha, nic se nevybírá, byla předem v zadání): LOFO 13,94 proti 15,29 cm, **−1,35 cm, lepší 20 z 22 povodní**
(znaménkový test p = 0,0001), nejhorší zhoršení +8,2 cm. Dopočteno v 00:28, až po kontrole Codexu (h), ta ji
neviděla. Cena: v oknech povodní 6 planých poplachů 2. SPA proti 4 u týmového Ridge, povodeň 2006 25,0 proti 16,7,
na validaci 18,2 proti 15,5 (0 planých, začátek vzestupu 27,8 proti 35,4). Každý z obou modelů sám je slabší
(Ridge 30 −0,49, LightGBM 30 +0,78), zisk dělá to, že chybují jinak. Vnořeně zvolená váha (G4, jen přibližně
vnořená) vychází 0,6 pro Ridge ve 21 z 22 foldů a dává totéž (−1,33, 20 z 22).

Dál číselně splní jen **H30 = Ridge 30 stanic
+ ukazatel útlumu v nivě** (LOFO 14,15 proti 15,29 cm týmového Ridge, −1,13 cm, lepší 18 z 22 povodní, znaménkový
test p = 0,004, nejhorší zhoršení +5,9 cm; Codex výsledek nezávisle přepočítal). Je to ale **průzkumný výsledek**:
nápad vznikl z rozboru povodně 2006, která je mezi 22 hodnocenými (a ve validaci), takže návrh modelu z hodnocených
dat nebyl oddělený (nález Codexu h). Zmírňuje to citlivost: bez povodně 2006 je zlepšení −1,46 cm (lepší 17 z 21,
nejhorší +1,0), bez 2006 i 2011 −1,53 cm. Zisk tedy nevzniká na povodni, ze které nápad je, tam je H30 naopak
horší. Na validaci je H30 horší než týmový Ridge (17,5 proti 15,5). Nezávislé potvrzení chybí, test je spotřebovaný.
Ostatní varianty hranici 1 cm nedosáhnou, i když většina zlepší 15–18 z 22 povodní: samotných 30 stanic (−0,49),
silnější penalizace nových stanic (vnořeně f = 1 ve všech foldech), součty po povodích (−0,67), vnořený výběr
stanic (−0,61), Huber (+0,62, horší), směsi Ridge 12 + 30 (−0,64 / −0,56) a se sítí (−0,64 / −0,56), síť sama
(−0,22; s novými stanicemi +0,76).

**Děčín +36 h: pravidlo splní samotný Ridge s 30 stanicemi** (26,39 → 23,96, −2,43 cm, 17 z 22, nejhorší +7,0
v roce 2006). Bez ladění, jen 30 stanic a týmové nastavení, tedy bez výhrady k návrhu. Delší zpoždění 48–72 h nic
nepřidají. Na validaci 26,6 proti 26,0, rozdíl zase dělá povodeň 2006.

Ve všech variantách s novými stanicemi se výrazně zlepší začátek vzestupu (LOFO 41,9 → 33–37 cm) a zhorší se
povodeň 2006. Přestřelení 2006 vzniká útlumem vlny v nivě Polabí, ne chybou dat (rozbor A).

**Doporučení pro Ondru:** jediný přísně ověřený kandidát pro +24 h je G3 (průměr Ridge 30 a LightGBM 30): v LOFO
jasně lepší (20 z 22 povodní), ale na validaci horší než týmový Ridge (18,2 / 15,5), s víc planými poplachy
v oknech povodní, složitější (dva modely) a bez nezávislého testu. Když chce tým jednoduchost a validaci, zůstat
u týmového Ridge; když věří širšímu LOFO, G3. Já bych pro finále nechal týmový Ridge a G3 ukázal jako ověřené
zlepšení, protože pravidlo „radši jednodušší model“ a horší validace převažují. Pro +36 h je Ridge s 30 stanicemi
přísně ověřené zlepšení (−2,4 cm, 17 z 22 povodní); když se horizont 36 h v aplikaci ukazuje, dává smysl ho použít,
s poznámkou, že na validaci je kvůli 2006 o 0,6 cm horší. Do prezentace jako zjištění: nové stanice spolehlivě
zlepšují začátek vzestupu, přestřelení velkých povodní je fyzika rozlivu do nivy a ukazatel útlumu (schodek průtoku
v úseku) je slibný průzkumný nápad (24 h −1,1 cm v LOFO), ne ověřený model.

**Nedoběhlo do 00:30** (volná RAM ~0,5 GB, sdílená se session srážek a sítě): Huber s 30 stanicemi (F30); opravený přepočet vnořených B, D a G2 po nálezu
Codexu (h). U těch tří to závěr nemění: chyba ve vnitřním hodnocení mohla vnořený výběr jen přikrášlit
(výběr viděl část hodin blízké držené povodně), a i tak žádná z nich hranici nedosáhla.

## Protokol (pevný)

- **Leave-one-flood-out CV přes všech 22 povodní 2006–2020** v Děčíně (vrchol nad 400 cm, 18 tréninkových +
  4 validační). Fold k: hodnotí se okno povodně (7 dní před až 5 dní po vrcholu, jako týmová metrika), z tréninku
  se vyřadí okno ± 20 dní, trénuje se na všem ostatním z let 2006–2020. Foldy jsou v `stanice_vsem/lofo_foldy.csv`
  (stejné použije session se sítí). Všechny varianty mají stejné řádky (131 234 hodin pro Děčín +24 h).
- Ke každé variantě: průměr přes 22 povodní, chyba po povodních, kolik povodní se proti týmovému Ridge zlepšilo
  (znaménkový test), největší zhoršení.
- **Pravidlo:** zlepšení platí jen když je průměr aspoň o 1 cm lepší, zlepší se většina povodní (aspoň 12 z 22)
  a žádná se nezhorší o víc než 10 cm.
- Výběry uvnitř varianty (faktor penalizace, stanice, váhy směsi) jen vnořeně: vnitřní leave-one-flood-out přes
  zbylých 21 povodní v tréninku foldu. U validace totéž přes 18 tréninkových povodní týmového splitu.
- Validace (4 povodně + 2019–2020, týmové rozdělení) je vedle jen pro srovnání s týmem.
- Ridge přes rychlé normální rovnice ze součtů (shoda se sklearn `ridge.fit` na 5e-5 cm, reprodukce validace
  15,5 / 17,8 cm).

## Laťky

| Varianta | LOFO 22 povodní | zlepšeno z 22 | nejhorší zhoršení | val Děčín +24 | začátek vzestupu (LOFO) | 2006 (LOFO) | plané 2. SPA (LOFO) |
|---|---|---|---|---|---|---|---|
| týmový Ridge (12 stanic) | 15,29 | základ | | 15,5 | 41,9 | 16,7 | 4 |
| Ridge 30 stanic | 14,79 (−0,49) | 15 | +6,5 | 17,8 | 34,1 | 23,3 | 3 |

Ridge s 30 stanicemi tedy přísné pravidlo nesplní: zlepšení 0,49 cm je pod 1 cm, i když se zlepší 15 z 22 povodní.

## Všechny varianty (Děčín +24 h, není-li uvedeno jinak; základ = týmový Ridge, LOFO 22 povodní)

| Pokus | Varianta | LOFO 22 | rozdíl | zlepšeno z 22 | nejhorší zhoršení | znam. p | splňuje | val Děčín | začátek (LOFO) | 2006 (LOFO) | plané 2. SPA (LOFO) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| — | týmový Ridge (12 stanic) | 15,29 | | | | | | 15,5 | 41,9 | 16,7 | 4 |
| — | Ridge 30 stanic | 14,79 | −0,49 | 15 | +6,5 | 0,13 | ne | 17,8 | 34,1 | 23,3 | 3 |
| B | penalizace nových stanic, f vnořeně (všude f = 1) | 14,79 | −0,49 | 15 | +6,5 | 0,13 | ne | 17,8 | 34,1 | 23,3 | 3 |
| B | pevné f = 0,01 (diagnostika) | 15,02 | −0,26 | 16 | +4,4 | 0,05 | ne | | 38,7 | 21,1 | 3 |
| C | C1 součet odmocnin po 8 povodích | 14,61 | −0,67 | 18 | +7,3 | 0,004 | ne | 17,4 | 33,9 | 24,0 | 3 |
| C | C2 odmocnina součtu po 8 povodích | 14,63 | −0,65 | 18 | +6,5 | 0,004 | ne | 17,2 | 34,1 | 23,2 | 3 |
| D | vnořený dopředný výběr stanic | 14,68 | −0,61 | 16 | +4,7 | 0,05 | ne | 17,2 | 36,1 | 21,4 | 3 |
| F | Huber, 12 stanic | 15,91 | +0,62 | 3 | +5,2 | 0,001 | ne | 17,4 | 44,5 | 22,0 | 4 |
| F | Huber, 30 stanic | nedoběhlo | | | | | | | | | |
| G | G1 ½ Ridge 12 + ½ Ridge 30 | 14,65 | −0,64 | 17 | +2,4 | 0,017 | ne | 16,0 | 37,5 | 19,1 | 3 |
| G | G2 váha Ridge 12/30 striktně vnořeně | 14,73 | −0,56 | 17 | +4,6 | 0,017 | ne | | 36,6 | 21,4 | 3 |
| G | LightGBM 12 (týmový) | 16,94 | +1,66 | 9 | +8,5 | | ne | 21,3 | | 22,9 | 6 |
| G | LightGBM 30 sám (proti LightGBM 12: −0,88, 15 z 22) | 16,06 | +0,78 | 11 | +12,1 | 1,0 | ne | 20,4 | 37,9 | 28,9 | 7 |
| G | **G3 ½ Ridge 30 + ½ LightGBM 30 (pevně)** | **13,94** | **−1,35** | **20** | +8,2 | 0,0001 | **ano** | 18,2 | 34,5 | 25,0 | 6 |
| G | G4 váha přibližně vnořeně (0,6 Ridge) | 13,95 | −1,33 | 20 | +7,6 | 0,0001 | ano | | 34,4 | 24,3 | 5 |
| G | síť beze změny | 15,07 | −0,22 | 14 | +6,4 | 0,29 | ne | | 39,2 | 15,6 | 3 |
| G | síť + 18 stanic | 16,05 | +0,76 | 12 | +7,7 | 0,83 | ne | | 34,1 | 23,4 | 1 |
| G | G5 ½ Ridge 30 + ½ síť + 18 | 14,65 | −0,64 | 16 | +5,7 | 0,05 | ne | | 33,6 | 22,4 | 0 |
| G | G6 ½ Ridge 12 + ½ síť beze změny | 14,72 | −0,56 | 16 | +2,8 | 0,05 | ne | | 40,2 | 15,4 | 3 |
| H | H12 týmový Ridge + útlum | 14,61 | −0,68 | 16 | +0,6 | 0,05 | ne | **14,8** | 41,0 | 14,3 | 6 |
| H | **H30 Ridge 30 + útlum** (průzkumný, viz verdikt) | **14,15** | **−1,13** | **18** | +5,9 | 0,004 | **ano*** | 17,5 | 33,5 | 22,6 | 4 |
| E (36 h) | týmový Ridge 36 h | 26,39 | | | | | | 26,0 | 66,5 | 28,3 | 6 |
| E (36 h) | **Ridge 30 stanic 36 h** | **23,96** | **−2,43** | **17** | +7,0 | 0,017 | **ano** | 26,6 | 53,5 | 35,3 | 7 |
| E (36 h) | + zpoždění 48/60/72 h | 24,10 | −2,28 | 17 | +11,6 | 0,017 | ne | 27,1 | 53,6 | 40,0 | 8 |

Plané poplachy z LOFO jsou jen v oknech povodní (2. SPA = 490 cm), validace je týmové rozdělení Děčín +24 h
(u 36 h Děčín +36 h). Mnohonásobné porovnávání: na 24 h je to asi 15 variant; při tolika pokusech může jedna
varianta těsně nad hranicí (H30, −1,13) vyjít i náhodou, proto výhrady ve verdiktu.

## Pokusy

*(hotovo A, B, C, D, E, F12, H, LightGBM 12 a 30, směsi G1–G6 a síť; nedoběhlo: F30, opravený přepočet B/D/G2)*

### Pokus C: součty po dílčích povodích místo jednotlivých nových stanic

- Co: místo 126 sloupců (18 stanic × 7 zpoždění) jen 8 skupin (Ploučnice, Bílina, horní Ohře, horní Berounka,
  Zbraslav, horní Sázava, horní Labe, horní Jizera) × 7 zpoždění = 56 sloupců k týmovým 98. Dvě předem dané varianty:
  C1 součet odmocnin průtoků stanic skupiny, C2 odmocnina součtu průtoků skupiny. Alpha 1, nic se nevybírá.
- Proč: méně vstupů = menší přeučení a menší protichůdné váhy podobných stanic (příčina přestřelení 2006).
- Výsledek (LOFO-CV 22 povodní, Děčín +24 h, základ týmový Ridge 15,29 cm):

| Varianta | sloupců | LOFO | rozdíl | zlepšeno z 22 | nejhorší zhoršení | znaménkový p | splňuje | val | začátek (LOFO) | 2006 (LOFO) | plané 2. SPA (LOFO) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| týmový Ridge | 98 | 15,29 | | | | | | 15,5 | 41,9 | 16,7 | 4 |
| Ridge 30 (jednotlivé stanice) | 224 | 14,79 | −0,49 | 15 | +6,5 | 0,13 | ne | 17,8 | 34,1 | 23,3 | 3 |
| C1 součet odmocnin | 154 | 14,61 | −0,67 | 18 | +7,3 | 0,004 | ne | 17,4 | 33,9 | 24,0 | 3 |
| C2 odmocnina součtu | 154 | 14,63 | −0,65 | 18 | +6,5 | 0,004 | ne | 17,2 | 34,1 | 23,2 | 3 |

- Na validaci (týmový split): přestřelení na stoupání 2006 C1 72,8 cm, C2 71,4 cm (Ridge 30 68,2, tým 56,7),
  chyba povodně 2006 na validaci 24,6 / 23,6 (tým 16,0); 2. SPA bez planých poplachů i propásnutí u všech.
- Závěr: součty jsou o kousek lepší než jednotlivé stanice (−0,67 proti −0,49 cm, zlepší 18 z 22 povodní,
  znaménkový test p = 0,004), ale průměrné zlepšení nedosáhne 1 cm, takže pravidlo **nesplní ani jedna varianta**.
  Přestřelení v roce 2006 se tím nespraví (zhorší se o 3–4 cm), problém tedy není v počtu vstupů.
- Soubory: `zlepseni/pokus_C.py`, `zlepseni/vysledky_C.json`.

### Pokus E: delší zpoždění u vzdálených stanic, Děčín +36 h

- Co: k Ridge s 30 stanicemi při horizontu 36 h přidat zpoždění 48/60/72 h u nejvzdálenějších stanic (horní Berounka,
  horní Ohře, horní Sázava, Chrudimka, Orlice; 11 stanic, +33 sloupců). Alpha 1, nic se nevybírá. Skript `pokus_E.py`,
  čísla `vysledky_E.json`.
- Proč: na 36 h je doba doběhu z Plzně, Liblína nebo Karlových Varů do Děčína (29–42 h) blízko nebo nad nejdelším
  týmovým zpožděním 36 h, starší průtoky by mohly nést vlnu, která do Děčína teprve přijde.
- Výsledek (LOFO-CV 22 povodní, Děčín +36 h, základ týmový Ridge):

| Varianta | LOFO | rozdíl | zlepšeno z 22 | nejhorší zhoršení | splňuje | val | začátek (LOFO) | 2006 (LOFO) | plané 2. SPA (LOFO) |
|---|---|---|---|---|---|---|---|---|---|
| týmový Ridge 36 h | 26,39 | | | | | 26,0 | 66,5 | 28,3 | 6 |
| Ridge 30 stanic 36 h | 23,96 | −2,43 | 17 (p = 0,017) | +7,0 (2006) | **ano** | 26,6 | 53,5 | 35,3 | 7 |
| E: + 48/60/72 h | 24,10 | −2,28 | 17 (p = 0,017) | +11,6 (2006) | ne | 27,1 | 53,6 | 40,0 | 8 |

- Proti Ridge 30 při 36 h je E o 0,15 cm horší, zlepší jen 10 z 22 povodní (nejhorší +4,7).
- Závěr: delší zpoždění nepomáhají, zhorší povodeň 2006 (o dalších 4,7 cm) a přidají planý poplach. Samotných
  30 stanic při 36 h pravidlo proti týmovému Ridge splní (−2,4 cm, 17 z 22, nejhorší +7,0 v roce 2006), na validaci
  ale vychází o 0,6 cm hůř (26,6 proti 26,0), opět kvůli 2006 (36,2 proti 26,8, přestřelení 84 cm).


### Pokus A · rozbor přestřelení v povodni 2006 (a 2011), Ridge 12 vs 30 stanic, Děčín +24 h

Skript `pokus_A.py`, čísla `vysledky_A.json`, příspěvky po 6 h `prispevky_A_2006.csv` a `prispevky_A_2011.csv`, denní bilance `bilance_A_2006.csv`. Nic se neladilo ani nemazalo.

- Už týmový Ridge (12 stanic) v roce 2006 na stoupání přestřelí o 40 cm (29. 3. 00:00, validační split; ve foldu LOFO 39 cm). S 30 stanicemi o 62 cm (LOFO 59 cm); rozdíl obou předpovědí je v tu chvíli +22 cm.
- Příspěvky 30 − 12 stanic (cm, validační split), stoupání a vrchol:

| čas (vydání) | skut. za 24 h | 12 st. | 30 st. | horní Labe | horní Berounka | Zbraslav | horní Sázava | Ploučnice | Děčín+Ústí | Beroun | Vltava tým | Nespeky |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 27. 3. 12:00 | 549 | 539 | 552 | +44 | +15 | +7 | +3 | +8 | −24 | −10 | −13 | −9 |
| 28. 3. 12:00 | 642 | 682 | 703 | +38 | +17 | +36 | +12 | +4 | −33 | −17 | −26 | −12 |
| 29. 3. 00:00 | 682 | 722 | 744 | +34 | +24 | +16 | +11 | +13 | −35 | −21 | −22 | −13 |
| 1. 4. 12:00 | 829 | 867 | 886 | +25 | +17 | +7 | −17 | +10 | −47 | −23 | −16 | +11 |
| 3. 4. 00:00 | 875 | 852 | 842 | +14 | +14 | −4 | −28 | +1 | −48 | −19 | −2 | +20 |

- Mechanismus: nové stanice proti proudu (hlavně horní Labe s Orlicí, Chrudimkou a Cidlinou, horní Berounka, Zbraslav, horní Sázava) přidají na stoupání +80 až +110 cm a model to vyrovnává zápornými změnami vah týmových stanic (Děčín −148 / Ústí +113 cm, Beroun, Vraňany, Nespeky). Výsledkem je čistých +20 cm. Na vrcholu je to obráceně: horní Sázava už opadá (−28 cm) a 30 stanic vrchol podstřelí (842 proti 875).
- Proč model přestřelí: v roce 2006 se vlna na Labi v Polabí utlumila. Kostelec měl 28.–31. 3. o 18–21 % méně vody než Nymburk + Jizera (498 proti 610, 566 proti 719, 693 proti 862 m³/s) a dorovnal se až 3. 4. Také Mělník proti Vraňanům + Kostelci (29. 3. 1 578 proti 1 803) a Ústí proti Mělníku + Lounům (1 580 proti 1 780). Lineární model se naučil, že vzestup nahoře dorazí celý. V roce 2006 se ale zhruba pětina vody několik dní držela v nivě. Čím víc vzdálených stanic model má, tím víc tomuto signálu věří.
- Chyba dat to není. Bilance sedí (Praha ≈ Zbraslav + Beroun do 8 %, Nymburk ≈ Přelouč + Cidlina do 5 %). Drobnosti: Cidlina Sány 60 h konstantně 4,05 m³/s (16.–19. 3., před povodní), Žatec 38 h konstantně (řízený odtok z Nechranic). Zbraslav má stav o 71 cm výš než obvykle při stejném průtoku (vzdutí nebo led), její průtok ale bilanci sedí. Nic nemažu.
- 2011 (tání, 730 cm) má stejný mechanismus. Přestřelení 30 stanic je 60 cm proti 36–39 cm (14. 1. 18:00), rozdíl +35 cm. Nahoru táhne horní Berounka (+31 až +34), horní Labe (+21), horní Jizera (+20), horní Ohře (+16 až +18), Zbraslav (+15), dolů Děčín/Ústí (−39 až −43), Beroun (−27 až −31) a Vltava tým (−15 až −19). Průměrná chyba povodně je ale u 30 stanic stejná nebo lepší (13,8–14,1 proti 14,4–14,5).
- Co by pomohlo: menší váha vzdálených stanic, aby jejich protichůdné váhy s týmovými stanicemi byly menší (pokusy B a C). Pak nelineární útlum velkých vln, tedy vstup, který pozná, že vlna je tak velká, že se rozlije do nivy, například rozdíl Kostelec − (Nymburk + Jizera) jako ukazatel. Ten musí projít LOFO; neladil jsem ho.


### Pokus D: vnořený dopředný výběr nových stanic (Ridge Děčín +24 h)

- Co: v každém z 22 foldů LOFO-CV zvlášť začne model s týmovými 98 vstupy a po jedné přidává novou stanici (všech
  7 zpoždění), vždy tu, která nejvíc sníží vnitřní LOFO chybu přes zbylých 21 povodní (modely bez mezer k i j);
  přidá ji jen při striktním zlepšení. Alpha 1, odmocnina průtoků jako v týmu. Validace: tentýž výběr jen z tréninku
  týmového splitu (vnitřní LOFO přes jeho 18 povodní). Skript `pokus_D.py`, výsledky `vysledky_D.json`, 18 min.
- Proč: všech 18 stanic přidává šum a protichůdné váhy; výběr jen užitečných stanic by mohl zisk zachovat a
  přeučení zmenšit.

| Varianta | LOFO 22 | rozdíl | zlepšeno z 22 | nejhorší zhoršení | znam. test p | splňuje | VAL | začátek (LOFO) | 2006 (LOFO) | plané 2. SPA (LOFO) |
|---|---|---|---|---|---|---|---|---|---|---|
| týmový Ridge (12 stanic) | 15,29 | | | | | | 15,5 | 41,9 | 16,7 | 4 |
| Ridge 30 stanic | 14,79 | −0,49 | 15 | +6,5 | 0,13 | ne | 17,8 | 34,1 | 23,3 | 3 |
| **D: vnořený výběr** | **14,68** | **−0,61** | **16** | **+4,7** (2006) | 0,053 | **ne** | 17,2 | 36,1 | 21,4 | 3 |

- Výběr je velmi stabilní: ve všech 22 foldech Žatec, Karlovy Vary, Plzeň-Bílá Hora, Litavka, Orlice Týniště,
  Jizera Bakov, ve 21 Zbraslav, v 10 Bílina Trmice; Stružnice, Zruč, Sány po jednom; Ploučnice Benešov, Česká Lípa,
  Zbečno, Liblín, Střela, Kácov, Chrudimka nikdy. Na validačním tréninku vybráno 10 stanic (tytéž + Zruč, Střela,
  Trmice). Vnitřní chyba klesá z ~15,4 na ~14,4 cm.
- Zhoršení po povodních malá: nejvíc 2006 (+4,7), pak 1/2011 +0,9, 6/2013 +0,4, 8/2010 +0,3.
- Závěr: oproti všem 30 stanicím je výběr o 0,1 cm lepší, zlepší 16 z 22 povodní a největší zhoršení (2006) zmenší
  z 6,5 na 4,7 cm. Pravidlo ale **nesplní**: průměrné zlepšení proti týmovému Ridge je jen 0,61 cm (< 1 cm).
  Na validaci 17,2 proti týmovým 15,5.


### Pokus H (doplňkový): ukazatel útlumu vlny v nivě z týmových stanic

- Co: z rozboru A (2006: ~20 % vody se několik dní drží v nivě Polabí) přidán vstup „schodek v úseku“ = průtok po
  proudu − součet přítoků nad ním, pro Kostelec − (Nymburk + Jizera), Mělník − (Vraňany + Kostelec) a
  Ústí − (Mělník + Louny), zpoždění 0/6/12/24 h, 12 sloupců v m³/s. H12 = k týmovému Ridge, H30 = k Ridge 30.
  Alpha 1, nic se neladí. Zapsáno předem (PRUBEH 23:37) jako jediný doplňkový nápad; skript `pokus_H.py`.
- Výhrada: nápad vznikl z rozboru povodně 2006, která je ve validaci a v LOFO je jedním z 22 foldů.

| Varianta | LOFO 22 | rozdíl | zlepšeno z 22 | nejhorší zhoršení | znam. p | splňuje | val Děčín | začátek (LOFO) | 2006 (LOFO) | plané 2. SPA (LOFO) |
|---|---|---|---|---|---|---|---|---|---|---|
| týmový Ridge | 15,29 | | | | | | 15,5 | 41,9 | 16,7 | 4 |
| H12 tým + útlum | 14,61 | −0,68 | 16 | +0,6 | 0,053 | ne | **14,8** | 41,0 | 14,3 | 6 |
| Ridge 30 | 14,79 | −0,49 | 15 | +6,5 | 0,13 | ne | 17,8 | 34,1 | 23,3 | 3 |
| **H30 Ridge 30 + útlum** | **14,15** | **−1,13** | **18** | +5,9 | 0,004 | **ano** | 17,5 | 33,5 | 22,6 | 4 |

- Validace H12: 2006 13,4 cm (tým 16,0), přestřelení 2006 56 cm (57), 1 planý 2. SPA; H30: 2006 23,9, přestřelení 73.
- Závěr: ukazatel útlumu sám pomáhá týmovému modelu hlavně v roce 2006 (validace 14,8 proti 15,5), ale v LOFO
  jen o 0,68 cm. S 30 stanicemi pravidlo těsně splní (−1,13 cm, 18 z 22, žádná povodeň horší o víc než 5,9 cm),
  na validaci je ale pořád horší než týmový Ridge (17,5) – přestřelení 2006 z nových stanic ukazatel nespraví.


### Pokus B: silnější regularizace nových stanic

- Co: Ridge s 30 stanicemi (alpha 1), 126 sloupců nových stanic po standardizaci × f, tj. penalizace alpha/f² jen
  pro ně; týmových 98 sloupců beze změny. Násobení před StandardScalerem by škálování zrušilo, proto až po něm.
  Mřížka f ∈ {1; 0,75; 0,5; 0,25; 0,1; 0,05; 0,02; 0,01} (0,25–1 podle zadání; s alphou 1 a 130 000 řádky má
  skoro nulový účinek, proto i menší). Hlavní varianta: f vnořeně z vnitřního LOFO přes 21 povodní bez povodně k.
- Proč: menší váhy nových stanic by mohly zmenšit přestřelení (2006) a protichůdné váhy.
- Výsledek, pevná f (jen diagnostika, ne výběr; základ = týmový Ridge 15,29):

| f | LOFO 22 | rozdíl | zlepšeno z 22 | nejhorší zhoršení | splňuje | začátek vzestupu | 2006 | plané 2. SPA |
|---|---|---|---|---|---|---|---|---|
| 1 (= Ridge 30) | 14,79 | −0,49 | 15 | +6,5 | ne | 34,1 | 23,3 | 3 |
| 0,5 | 14,79 | −0,49 | 15 | +6,5 | ne | 34,1 | 23,3 | 3 |
| 0,25 | 14,80 | −0,49 | 15 | +6,5 | ne | 34,1 | 23,2 | 3 |
| 0,1 | 14,81 | −0,47 | 16 | +6,4 | ne | 34,4 | 23,1 | 3 |
| 0,05 | 14,85 | −0,43 | 16 | +6,1 | ne | 35,1 | 22,8 | 3 |
| 0,02 | 14,96 | −0,33 | 16 | +5,5 | ne | 36,8 | 22,3 | 3 |
| 0,01 | 15,02 | −0,26 | 16 | +4,4 | ne | 38,7 | 21,1 | 3 |

  (týmový Ridge: začátek vzestupu 41,9, 2006 16,7, plané 2. SPA 4)
- Vnořená varianta B a validace: CHYBÍ, výpočet do termínu 00:05 nedoběhl (stroj měl volných jen ~0,5 GB RAM,
  vnitřní foldy se odkládaly na disk; první běh čekal 20 min na paměť a pak skončil bez hlášky). Skript `pokus_B.py`
  ji spočítá a zapíše do `vysledky_B.json`. Na závěru to nic nemění: vnořený výběr volí po foldech jen z těchto
  hodnot f a žádné f se k hranici −1 cm ani nepřiblíží.
- Závěr: silnější penalizace nových stanic průměr nezlepší (nejlíp f = 1, −0,49 cm). Zmenší jen nejhorší zhoršení
  (6,5 → 4,4 cm) a chybu 2006 (23,3 → 21,1), ale o tolik zhorší začátek vzestupu (34,1 → 38,7). Pravidlo nesplní
  žádné f.


### Směsi G (Codex jako samostatný experimentátor, `smesi/`)

Děčín +24 h; 22 LOFO povodní 2006–2020, test 2021–2025 nepoužit; jednotky cm.
G1/G3/G5 pevně 0,5; G2 striktně vnořené bez mezer k i j; váhy po foldech jsou v JSON.

| Varianta | LOFO | rozdíl | zlepšeno z 22 | nejhorší zhoršení | splňuje | val |
|---|---:|---:|---:|---:|---|---:|
| Ridge12 | 15.29 | +0.00 | — | 0.0 | — | 15.5 |
| Ridge30 | 14.79 | -0.49 | 15 | 6.5 | ne | 17.8 |
| G1 | 14.65 | -0.64 | 17 | 2.4 | ne | 16.0 |
| G2 | 14.73 | -0.56 | 17 | 4.6 | ne | — |
| G3 | nedodáno | — | — | — | nehodnoceno | 18.2 |
| G4 | nedodáno | — | — | — | nehodnoceno | — |
| G5 | nedodáno | — | — | — | nehodnoceno | — |
*G4 je pouze přibližně vnořená: modely ostatních foldů viděly vlastní povodeň k; splnění pravidla platí s touto výhradou.
Chybí externí LOFO: LOFO LightGBM30 zatím nedodáno.; V C:\Users\danie\Documents\hackathon-2026-sit\sit_dan\lofo nebyly nalezeny použitelné LOFO předpovědi sítě (2026-10-23 23:32:02). Čekání pokračuje v limitu 35 minut.
Závěr: Žádná dostupná striktně hodnocená směs nesplňuje celé stanovené pravidlo.


### Pokus F: Ridge s Huberovou ztrátou (IRLS)

- Co: místo součtu čtverců Huberova ztráta přes IRLS. StandardScaler bez vah (μ, sd z tréninku foldu jako týmová
  pipeline), pak vážený Ridge(alpha 1) jako sklearn `Ridge(sample_weight=w)`. Váhy w = min(1, δ/|r|),
  δ = 1,345 · 1,4826 · MAD reziduí (asi 9,8 cm, přepočítané v každé iteraci), start z obyčejného Ridge, 10 iterací.
  Nic se neladí (δ je standardní volba), takže není co vnořovat.
- Proč: menší vliv extrémů (velké chyby na povodních táhnou čtvercovou ztrátu).
- Kontrola (fold 0, 12 stanic): start IRLS = obyčejný Ridge z motoru (rozdíl 2e-9 cm), vážený Ridge = sklearn se
  stejnými vahami (4e-9 cm). Ztráta „srazí“ váhu asi 22 % tréninkových hodin.

| Varianta | LOFO 22 | rozdíl proti týmu | zlepšeno z 22 | nejhorší zhoršení | splňuje | val Děčín +24 | začátek vzestupu (LOFO) | 2006 (LOFO) | plané 2. SPA (LOFO) |
|---|---|---|---|---|---|---|---|---|---|
| týmový Ridge (základ) | 15,29 | | | | | 15,5 | 41,9 | 16,7 | 4 |
| F12 Huber, 12 stanic | 15,91 | +0,62 | 3 (19 horší) | 5,2 | ne | 17,4 | 44,5 | 22,0 | 4 |
| F30 Huber, 30 stanic | nedoběhlo do 00:05 | | | | | | | | |

- F12 na validaci: začátek vzestupu 37,6 (tým 35,4), 2006 21,8 (tým 16,0), přestřelení na stoupání 2006 43 cm
  (tým 57), plané 2./3. SPA 0/0.
- Závěr: Huber týmovému Ridge škodí (horší 19 z 22 povodní, znaménkový test p = 0,0009). Povodně jsou přesně ty
  „extrémy“, které Huber potlačuje, takže se model učí hlavně klid a na povodních podhodnocuje. Méně přestřelí
  v roce 2006, ale za cenu horší chyby. F30 nedoběhl: počítač byl v souběhu s dalšími 6 agenty a session se sítí
  bez volné RAM (pod 0,5 GB volno), výpočet `pokus_F.py` dál běží a výsledek F30 připíše do `vysledky_F.json`.
  Vzhledem k F12 se neočekává, že by F30 pravidlo splnil.
- Soubory: `pokus_F.py`, `vysledky_F.json` (F12), `pokus_F_beh1_float64.log` (první úplný běh F12 s kontrolou).


### Síť a směsi se sítí (G5, G6; počítáno zde, LOFO předpovědi sítě ze session se sítí)

Síť (týmová `mlp`, seed 42) dodala LOFO předpovědi na stejných foldech v 00:03 (`hackathon-2026-sit/sit_dan/lofo/`),
řádky ověřené proti oknům (stejné časy i skutečnost). Směsi s pevnou vahou 0,5 předem zapsané (PRUBEH 00:05),
nic se nevybírá. Skript `zlepseni/pokus_G5.py`, čísla `zlepseni/vysledky_G5.json`.

| Varianta | LOFO 22 | rozdíl proti týmovému Ridge | zlepšeno z 22 | nejhorší zhoršení | znam. p | splňuje | začátek (LOFO) | 2006 (LOFO) | plané 2. SPA (LOFO) |
|---|---|---|---|---|---|---|---|---|---|
| síť beze změny | 15,07 | −0,22 | 14 | +6,4 | 0,29 | ne | 39,2 | 15,6 | 3 |
| síť + 18 stanic | 16,05 | +0,76 | 12 | +7,7 | 0,83 | ne | 34,1 | 23,4 | 1 |
| G5 = ½ Ridge 30 + ½ síť + 18 | 14,65 | −0,64 | 16 | +5,7 | 0,053 | ne | 33,6 | 22,4 | **0** |
| G6 = ½ Ridge 12 + ½ síť beze změny | 14,72 | −0,56 | 16 | +2,8 | 0,053 | ne | 40,2 | 15,4 | 3 |

Síť s novými stanicemi je proti síti beze změny horší (+0,98 cm, lepší jen 8 z 22 povodní): síť nové vstupy
nevyužije, jen se víc přeučí. Směsi zmenší rozptyl, ale hranici 1 cm nedosáhnou.

## Kontrola Codexu (h, jen čtení, `codex/kontrola_h_zlepseni.md`)

Ověřil: odečítání mezer v tréninkových součtech je správné, všech 22 foldů odpovídá `lofo_foldy.csv`, řádků
131 234; přepočet `lofo.skore` reprodukoval laťky i H12/H30 bez rozdílu (H30 `splnuje = true`); budoucí vstupy
v posunech nenašel; přibližná vnořenost G4 je přiznaná.

| Nález | Závažnost | Co jsem udělal |
|---|---|---|
| Vnitřní hodnocení bralo celé okno povodně j včetně hodin v mezeře vnějšího foldu k (překryv 12/2012 a 1/2013 o 48 h a dalších 4 dvojic blízkých povodní), vnořené výběry B, D, G2 tak viděly část cílů držené povodně | vysoká | Opraveno v motoru (`Motor.okno_vnitrni`: okno j bez mezery k, prázdná okna se vynechají). Přepočet B, D a G2 do 00:30 nedoběhl (D ~400 s na fold kvůli RAM), v tabulce jsou čísla před opravou. Závěr platí: chyba výběr jen zvýhodňovala a žádná z těch variant hranici nedosáhla. |
| H30 vznikla z rozboru hodnocené povodně 2006, výhrada nestačí k tvrzení o přísně potvrzeném zlepšení | vysoká | Souhlasím. Verdikt přepsán: pro 24 h žádná varianta průkazně, H30 je průzkumný výsledek. Doplněna citlivost bez 2006 (−1,46, 17 z 21) a bez 2006 i 2011 (−1,53). |
| Zpráva tvrdila, že vnořené B chybí, JSON ho už má | nízká | Opraveno (B kompletní včetně validace 17,8, f = 1 ve všech foldech). |

\* H30 splní pravidlo čísly, ale jako průzkumný výsledek, ne přísné potvrzení.
