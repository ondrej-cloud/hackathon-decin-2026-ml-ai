# Pokusy: vlastní Ridge pro Děčín +24 h

Každý pokus: co, proč, výsledek, ponecháno ano/ne. Nové záznamy na konec. Všechna čísla jsou v cm, Děčín +24 h.

Protokol proti přeladění validace:
- Rozhoduje časová křížová validace uvnitř tréninku (`pokus.cv`): 6 bloků let (2006–07, 2008–09, 2010–11, 2012–13,
  2014–15, 2016–18), model se trénuje na ostatních blocích, kolem drženého bloku mezera 10 dní. Hlavní číslo
  `CV povodně` = průměr přes 18 povodní z tréninku (vrchol nad 400 cm) chyby v okně 7 dní před až 5 dní po vrcholu,
  každá povodeň má stejnou váhu (jinak by o všem rozhodl červen 2013 s 1 072 cm). Alpha se vybírá taky touto CV.
- Validace (4 vynechané povodně + 2019–2020) se pouští jen u milníků, každé nahlédnutí se počítá
  (`poradi_nahlednuti_val` ve `vysledky/pokusy.jsonl`). Test 2021–2025 jednou na konci (`test_jednou.py`).
- Změna se nechává, když zlepší CV povodně aspoň o 0,3 cm a nezhorší CV vzestup; jinak ne (jednodušší vyhrává).

Laťky na validaci (stejné řádky): týmový Ridge 15,5 cm (Děčín +24 h; 17,1 je jeho průměr přes 6 kombinací),
„jako teď“ 44,4 cm.

## pá 20:56 · základ: týmové vstupy na vlastní tabulce
- Co: přesně týmové vstupy (98 sloupců: stav Děčína a Ústí se 7 zpožděními, průtoky 12 stanic se 7 zpožděními,
  odmocnina průtoků), Ridge alpha 1 (`tym`); totéž s alphou z CV (`tym_cv`) a s cílem „změna hladiny“ (`tym_zmena`).
- Proč: ověřit, že vlastní tabulka a převzaté vyhodnocení dávají totéž co týmový model, a mít laťku pro CV.
- Výsledek: CV povodně 15,64 cm (CV vzestup 33,8, podhodnocuje o 27 cm). Alpha z CV 0,1 → 15,63, změna hladiny
  15,63: obojí beze změny (Ridge s hladinou teď mezi vstupy je na volbě cíle skoro nezávislý, regularizace je malá).
  Na validaci stejné řádky jako týmový model, 15,5 cm (viz PRUBEH 20:44).
- Ponecháno: jako laťka. Cíl „změna hladiny“ ne (nic nedává, jednodušší je hladina).

## pá 20:57 · všech 30 stanic (`b_vse`)
- Co: k 12 týmovým stanicím 18 dalších (Ploučnice ×3, Bílina, Ohře ×2, Berounka ×5, Vltava Zbraslav, Sázava ×2,
  Orlice, Chrudimka, Cidlina, Jizera Bakov), stejná zpoždění 0–36 h, odmocnina.
- Proč: Ploučnice a Bílina se vlévají mezi Ústím a Děčínem, dnes je model nevidí; vzdálenější stanice dávají náskok.
- Výsledek: CV povodně 14,17 cm (−1,47), CV vzestup 28,8 (−5,0), podhodnocení vzestupu −21 místo −27.
- Ponecháno: ano, nový základ.

## pá 20:58 · změny za 1/3/6/12 h a zrychlení (`c_vse_zmeny`)
- Co: k `b_vse` změny průtoku a stavu za 1, 3, 6, 12 h a zrychlení (Q(t) − 2Q(t−3) + Q(t−6)).
- Proč: začátek vlny poznáme podle toho, že se stoupání zrychluje.
- Výsledek: CV povodně 13,90 (−0,27), CV vzestup 28,2 (−0,6). Lineární model si většinu změn umí složit ze zpoždění
  sám, nové jsou jen změny za 1 h.
- Ponecháno: zatím ne (pod hranicí 0,3 cm), zkusím znovu v kombinaci na konci.

## pá 20:59 · transformace průtoku (`c_vse_log`, `c_vse_bez_transformace`)
- Výsledek: log 16,82, bez transformace 24,22, odmocnina 14,17. Odmocnina nejlíp napodobí měrnou křivku
  (stav roste s průtokem zhruba jako odmocnina), log ji přehne, lineární průtok ji nenapodobí vůbec.
- Ponecháno: odmocnina (beze změny).

## pá 21:06–21:08 · jednotlivé doplňky k `b_vse` (14,17)
Každý zvlášť, alpha vždy z CV. CV povodně / CV vzestup:

| Pokus | Co a proč | CV povodně | CV vzestup | Ponecháno |
|---|---|---|---|---|
| `d_srazky` | denní srážky po 11 povodích, součty za 1/2/3/5 dní (déšť, který ještě nedotekl do stanic) | 14,18 (po opravě hranic z Codexu a 14,17) | 28,9 | ne |
| `d_snih` | výška sněhu po povodích, její změna za 1 a 3 dny, teplota, tání = sníh × kladná teplota (3 ze 4 val povodní s táním) | 14,45 | 28,9 | ne |
| `d_sezona` | sin/cos dne v roce | 14,07 | 28,8 | ne (−0,10) |
| `d_interakce` | stav × změna stavu za 6 h | 14,32 | 29,0 | ne |
| `d_soucty` | součty průtoků přes disjunktní povodí (Praha+Kostelec+Louny+Bílina+Ploučnice atd.) převedené měrnou křivkou Děčína na cm, zpoždění 0/6/12 h | 14,95 | 28,8 | ne |
| `d_vahy2` | řádky, kdy za 24 h stoupne o ≥ 50 cm, s váhou 2 | 14,21 | 27,8 | ne (lepší jen vzestup) |
| `d_vahy5` | totéž s váhou 5 | 14,91 | 27,2 | ne (horší celkem i MAE 8,06) |
| `d_dlouhe` | zpoždění průtoků až 48 a 60 h | 14,35 | 28,8 | ne |
| `d_huste` | hustší zpoždění průtoků 0/1/2/3/6/9/12/18/24/36 h | 13,90 | 28,1 | ne (−0,27, pod hranicí) |

Co z toho plyne: denní srážky a sníh model v CV nezlepšily. Denní úhrn je známý až den po začátku měřicího dne,
takže déšť, který spadne těsně před povodní, model stejně nevidí, a co spadlo dřív, už ukazují vodoměry proti proudu.
Pomáhá jen jemnější časové rozlišení nedávných změn (zpoždění 1–2 h, změny za 1 h), ale málo.
Váhy na vzestup zmenšují podhodnocení na stoupání (−21 → −16 cm), ale zhoršují zbytek.

## pá 21:09 · cíl = průtok v Děčíně, na stav převedený měrnou křivkou (`e_prutok_*`)
- Co: Ridge se učí průtok v Děčíně za 24 h (průtoky se po proudu sčítají, takže lineární vztah v průtocích je
  fyzikálně přirozený), předpověď se převede na stav měrnou křivkou Děčína z tréninku (medián stavu v 200 pásmech
  log průtoku, nad rozsahem přímka).
- Výsledek: CV povodně 29,4 (surové průtoky), 40,0 (odmocnina), 29,2 (+ změny); i v tréninku samém MAE 18,6 cm.
  Křivka sama je v pořádku (převod tam a zpět ±0,01 cm, od dat 2,2 cm, mezi roky se posouvá jen o ±5 cm, u malých
  průtoků za 20 let o −14 cm). Chyba je v tom, že čtverce chyb v průtoku jsou dané velkou vodou: chyba 35 m³/s je
  na povodni zanedbatelná, ale při 150 m³/s je to ±15 cm stavu.
- Ponecháno: ne, slepá ulička.

## pá 21:10 · kombinace hustých zpoždění a změn (`f_huste_zmeny`)
- Výsledek: CV povodně 13,90, vzestup 28,1, stejně jako každá z nich zvlášť (13,90 / 13,90). Nesčítají se, nesou
  stejnou informaci (co se dělo v posledních 1–2 hodinách).
- Ponecháno: ne (pod hranicí, 469 sloupců místo 224).

## pá 21:11 · které nové stanice pomáhají: ablace po skupinách (`g_*`)
- Co: z 30 stanic vždy jednu skupinu vynechat (`g_bez_*`, laťka `b_vse` 14,17) a k 12 týmovým vždy jednu skupinu
  přidat (`g_tym_plus_*`, laťka `tym` 15,64).
- Proč: zjistit, odkud je zisk 1,5 cm, a nenechat v modelu stanice, které jen přidávají šum.

| Skupina | bez ní (z 30) | tým + ona | Závěr |
|---|---|---|---|
| horní Ohře (Žatec, Karlovy Vary) | 14,65 (+0,48) | 14,90 (−0,74) | nejužitečnější |
| horní Labe (Orlice Týniště, Chrudimka Nemošice, Cidlina Sány) | 14,52 (+0,35) | 15,12 (−0,52) | užitečné |
| horní Berounka (Zbečno, Liblín, Plzeň, Střela, Litavka) | 14,30 (+0,13) | 15,20 (−0,44) | užitečné |
| Jizera Bakov | 14,31 (+0,14) | 15,37 (−0,27) | užitečné |
| Bílina Trmice | 14,25 (+0,08) | 15,58 (−0,06) | skoro nic |
| Vltava Zbraslav | 14,24 (+0,07) | 15,53 (−0,11) | skoro nic |
| horní Sázava (Kácov, Zruč) | 14,20 (+0,03) | 15,57 (−0,07) | nic |
| Ploučnice (Benešov, Stružnice, Česká Lípa) | 14,05 (−0,12) | 15,83 (+0,19) | škodí |

- Co z toho plyne: zisk dávají stanice, které vidí vlnu dřív (horní Ohře, horní Labe, Berounka). Přítoky mezi Ústím
  a Děčínem jsou při povodních malé: Ploučnice má na vrcholech 32–189 m³/s proti 1 160–3 710 m³/s v Děčíně (2–14 %),
  Bílina 13–52 m³/s. Vlna „z ničeho“ u Děčína tedy z nich nevzniká, větší podíl má neměřené území a načasování.
- Ponecháno: zatím 30 stanic, štíhlejší sady se zkouší v `i_*`.

## pá 21:14 · štíhlejší sady a dva režimy (`i_*`, `h_*`)
- `i_bez_pl_saz_zbr` (bez Ploučnice, horní Sázavy a Zbraslavi) 14,19, `i_jen_uzitecne` (tým + horní Ohře, horní Labe,
  Berounka, Jizera) 14,23: stejně jako všech 30 (14,17), vzestup o 0,5 horší. Ponecháno: ne.
- Dva režimy: všechny vstupy ještě jednou vynásobené indikátorem „Děčín ≥ 250 / 350 cm“ (`h_rezim*`) 14,26 / 15,16,
  nebo „za 6 h stouplo o ≥ 5 / 15 cm“ (`h_stoupa*`) 14,28 / 14,55. Model se dvěma sklony je přeučený (448 sloupců).
  Ponecháno: ne.

## pá 21:17 · MILNÍK, validace nahlédnutí č. 1 a 2 (`tym`, `b_vse`)
- Výsledek na val (stejných 19 264 řádků):

| | týmové vstupy (`tym`) | 30 stanic (`b_vse`) | „jako teď“ |
|---|---|---|---|
| chyba na povodních (`mae_povodne`) | 15,5 | **17,8** | 44,4 |
| chyba celkem | 7,5 | 6,9 | 12,7 |
| v klidu 2019–2020 | 6,9 | 6,1 | |
| rychlé stoupání (≥ 50 cm za 24 h) | 31,5 (bias −21) | 28,5 (bias −12) | |
| začátek vzestupu | 35,4 (bias −31) | 28,1 (bias −21) | |
| předstih 1./2./3. SPA | 13,8 / 15,5 / 19,0 h | 16,5 / 16,8 / 21,5 h | |
| plané poplachy 1. SPA | 2 | 0 | |

- Rozpad po povodních (`rozbor_val.py`): 2006 (875 cm) 16,0 → 24,6, 2009 10,1 → 9,1, 2010 20,8 → 20,7,
  2011 14,9 → 16,7. Horší je hlavně jarní povodeň 2006 (tání): na stoupání přestřelí o 20–65 cm (např. 28. 3. 22:00
  předpověď 742 při skutečnosti 677), na vrcholu podstřelí o 37 cm.
- Proč: s alphou 0,01 je model skoro čistá metoda nejmenších čtverců s obrovskými protichůdnými vahami
  (příspěvky v 1. 4. 2006: Děčín +398 cm, Ústí −165, Mělník +192, Vraňany −36, Zruč −36…). V neobvyklé povodni se
  přestanou vyrušovat. Ve CV (18 povodní) je přitom 30 stanic lepší skoro u všech povodní včetně tání (2010-03,
  2012-03, 2013-02), rozdíl −1,47 cm se směrodatnou chybou 0,38. Na validaci rozhodují 4 povodně, rozdíl +2,3 cm
  se směrodatnou chybou 2,2, tedy v rámci náhody.
- Rozhodnutí: dál se řídím CV (pravidlo úlohy), ale zkusím zmenšit protichůdné váhy (regularizace, menší sady).

## pá 21:18–21:30 · pokusy proti protichůdným vahám
- Alpha: CV je plochá do 30 (14,17 → 14,27) a pak roste (100: 14,45, 1 000: 15,72). Pravidlo jedné směrodatné chyby
  jasný výběr nedává (rozdíly jsou všude asi 1,2–1,5 SE). Ponecháno: alpha z CV.
- Brzda jen na 18 nových stanic (standardizované sloupce × 1/k, tj. penalizace k²; `k_brzda10/30/100`): CV vždy
  vybere nejmenší alphu a výsledek je 14,17 / 14,17 / 14,21. Ponecháno: ne.
- Řidší zpoždění průtoků 0/6/12/24 h (`j_ridke_q`) 14,26 s o 40 % méně sloupci; 0/12/24/36 h 14,56. Ponecháno: ne.
- Bez průtoku Děčína a Ústí (stav a průtok jsou přes měrnou křivku skoro totéž, `j_bez_q_cilu`) 15,60, výrazně horší:
  nelineární vztah stav–průtok modelu pomáhá skládat zakřivení. Ponecháno: ne.
- Aktualizace podle poslední chyby (`korekce.py`): předpověď + b1·e(t) + b2·ē6(t), e(t) = H(t) − předpověď vydaná
  v t − 24 h, učeno na chybách mimo vlastní blok (vnořená CV). Tým 15,63 → 15,57, 30 stanic 14,17 → 14,08.
  Chyby se za 24 h skoro rozpadnou. Ponecháno: ne.

## pá 21:34 · dopředná volba skupin stanic (`l_tym_plus_*`)
- Co: k týmovým stanicím přidávat skupiny v pořadí podle jejich samostatného přínosu, CV po každém kroku.
- Výsledek: tým 15,64 → + horní Ohře 14,90 (−0,74) → + horní Labe 14,41 (−0,49) → + Berounka 14,29 (−0,12) →
  + Jizera 14,23 (−0,06) → + Bílina 14,19 (−0,04) → + Zbraslav 14,10 (−0,09) → + horní Sázava 14,05 (−0,05).
- Ponecháno: podle pravidla (krok aspoň 0,3 cm) končí volba po dvou skupinách: **tým + horní Ohře (Žatec,
  Karlovy Vary) + horní Labe (Orlice Týniště, Chrudimka Nemošice, Cidlina Sány)**, 133 sloupců, CV 14,41
  (`l_tym_plus_2`). Zbylé kroky (do 14,05 s 203 sloupci, tj. všech 30 stanic bez Ploučnice) jsou každý pod hranicí. Proti `b_vse` (224 sloupců, 14,17) je `l_tym_plus_2` o 0,24 horší, viz oprava ve 21:43.

## pá 21:35 · doplňky ke kompaktnímu základu `l_tym_plus_2` (14,41)

| Pokus | CV povodně | velké | CV vzestup | Ponecháno |
|---|---|---|---|---|
| husté zpoždění 0/1/2/3/6/9/12/18/24/36 h (`m_huste`) | 14,23 | 22,8 | 29,9 | ne (−0,18) |
| změny za 1/3/6/12 h a zrychlení (`m_zmeny`) | 14,23 | 22,7 | 30,0 | ne (−0,18) |
| sezónnost (`m_sezona`) | 14,29 | 22,8 | 30,4 | ne |
| váhy 2 na stoupání (`m_vahy2`) | 14,30 | 23,4 | 29,2 | ne |
| denní srážky (`m_srazky`) | 14,41 | 23,3 | 30,6 | ne |
| sníh a teplota (`m_snih`) | 14,59 | 23,0 | 30,2 | ne |
| zpoždění až 48 h (`m_dlouhe`) | 14,49 | 23,3 | 30,3 | ne |

„velké“ = CV jen na 5 tréninkových povodních s vrcholem nad 490 cm (2. SPA), jako týmová metrika.

## pá 21:43 · oprava podle Codexu (b): pravidla, evidence validace, finální kandidát
- Pravidla výběru, teď výslovně (platí pro všechny záznamy výš, rozhodnutí podle nich se nemění):
  přidání se ponechá, když zlepší CV povodně aspoň o 0,3 cm a nezhorší CV vzestup; náhrada ponechaného modelu
  jednodušším jen tehdy, když CV povodně nezhorší o víc než 0,1 cm a CV vzestup o víc než 0,3 cm.
  Alpha: z nezaokrouhlených hodnot CV, ze všech alph do 0,01 cm od nejlepší ta největší (víc regularizace).
- `l_tym_plus_2` (kompaktní, 133 sloupců) tím pravidlem neprojde: proti ponechanému `b_vse` CV povodně
  14,41 vs 14,17 (+0,24) a CV vzestup 30,34 vs 28,75 (+1,6). Že jsem ho v 21:33 označil za kandidáta, bylo
  ovlivněné rozborem validace 2006 (hledal jsem model s menšími protichůdnými vahami), ne CV. **Vracím se k `b_vse`.**
- Evidence všech nahlédnutí do validace (Codex správně upozornil, že `pokusy.jsonl` jich ukazoval jen část):
  1. pá 20:44, zkušební běh bez zápisu: týmový Ridge na mé tabulce 15,5 a „jako teď“ 44,4 (reprodukce laťky,
     model se podle toho nevybíral);
  2. pá 21:17, milník: `tym` 15,5 a `b_vse` 17,8 (záznamy 1 a 2 v `pokusy.jsonl`);
  3. pá 21:18–21:22, rozbor téhož běhu po povodních a fázích (`rozbor_val.py`), průběh předpovědí 2006 a příspěvky
     stanic 1. 4. 2006. To už bylo adaptivní použití validace: motivovalo pokusy s regularizací, brzdou, řidšími
     zpožděními a kompaktní sadou (`k_*`, `j_*`, `l_*`, `m_*`). O nich ale rozhodovala jen CV a žádný z nich
     nakonec nebyl ponechán;
  4. pá 21:42, `finalni` = `b_vse` s alphou 1 podle nového pravidla pro shody: val 17,8 (popis finálního modelu).
- Nejistota po blocích a epizodách místo jen přes 18 povodní (povodně 29. 12. 2012 a 8. 1. 2013 se překrývají):

| Rozdíl CV povodně | přes povodně (n = 18) | přes epizody (n = 17) | přes bloky (n = 5) | lepší v blocích |
|---|---|---|---|---|
| `b_vse` − `tym` | −1,48 ± 0,38 | −1,50 ± 0,38 | −1,56 ± 0,62 | 4 z 5 (horší 2008–09) |
| `l_tym_plus_2` − `tym` | −1,24 ± 0,27 | −1,26 ± 0,28 | −1,35 ± 0,39 | 5 z 5 |
| `l_tym_plus_2` − `b_vse` | +0,24 ± 0,29 | +0,24 ± 0,30 | +0,21 ± 0,28 | 1 z 5 |
| `g_bez_ploucnice` − `b_vse` | −0,11 ± 0,19 | −0,13 ± 0,20 | −0,21 ± 0,26 | 2 z 5 |
| `d_huste` − `b_vse` | −0,27 ± 0,14 | −0,29 ± 0,15 | −0,26 ± 0,10 | 5 z 5 |

  (± = směrodatná chyba průměru rozdílů.) Přínos 18 nových stanic proti týmu je vidět i po blocích. Husté zpoždění
  je proti `b_vse` malé, ale konzistentní zlepšení; podle předem daného prahu 0,3 cm ho nepřidávám.
- Finální model: **`b_vse` = všech 30 stanic, zpoždění jako v týmu (stav 0/1/2/3/6/12/24 h, průtok 0/3/6/12/18/24/36 h),
  odmocnina průtoků, StandardScaler + Ridge(alpha = 1)**, 224 vstupů. CV povodně 14,17 (tým 15,64), CV vzestup 28,8
  (33,8). Val povodně 17,8 (tým 15,5), vzestup 28,5 (31,5), začátek vzestupu 28,1 (35,4), klid 6,1 (6,9).
