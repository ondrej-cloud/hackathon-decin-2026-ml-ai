# Tahák pro Dana: pojmy na našich číslech

Chyba = průměrná chyba hladiny během povodní v cm (okno 7 dní před vrcholem až 5 dní po něm). Validace = průměr přes
Děčín a Ústí × 12 / 24 / 36 h, D24 = Děčín za 24 h. Zdroje čísel jsou v `PREHLED_POKUSU.md` a `OTAZKY_POROTY.md`.

## Úloha a data

| Pojem | Co to je | Naše čísla |
|---|---|---|
| **učení s učitelem** | model se učí z příkladů, kde známe vstup i správnou odpověď | vstup = 98 čísel dostupných v čase t (měřených v t až t − 36 h), odpověď = hladina za h hodin; asi 108 tisíc trénovacích hodin |
| **vstupy (příznaky)** | čísla, ze kterých model počítá | hladina Děčín a Ústí a průtok 12 stanic, jen to, co je v čase t už změřené |
| **zpoždění** | hodnota před z hodinami | průtok teď a před 3, 6, 12, 18, 24, 36 h; hladina teď a před 1, 2, 3, 6, 12, 24 h |
| **horizont** | jak daleko dopředu předpovídáme | 12, 24 a 36 h; voda, která přijde za víc než asi 40 h, ještě neprotekla žádnou naší stanicí |
| **doba doběhu** | za jak dlouho voda doteče do Děčína | Ústí 4 h, Mělník 13 h, Praha 17 h, Sázava 25 h (korelace změn průtoku) |
| **měrná křivka** | vztah průtok → hladina na vodočtu | hladina roste s průtokem zhruba jako odmocnina, proto odmocnina průtoků |
| **SPA** (stupně povodňové aktivity) | prahy hladiny pro bdělost, pohotovost, ohrožení | Děčín 400 / 490 / 560 cm, Ústí 450 / 530 / 600 cm |

## Jak měříme

| Pojem | Co to je | Naše čísla |
|---|---|---|
| **„bude jako teď“** (laťka) | předpověď: za h hodin bude stejně jako teď | validace 44,3 cm, nikdy nevaruje předem |
| **chyba na povodních** (MAE) | průměr absolutních chyb v okně povodní | regrese 17,1; síť 17,8; LightGBM 23,1; fyzika 24,8 |
| **bias** | soustavná chyba jedním směrem | test D24 −10,5 cm: model povodně spíš podhodnocuje |
| **předstih, propásnuto, planý poplach** | o kolik hodin dřív model varoval, kolik povodní nevaroval, kolik varování bylo zbytečných | test: 3. stupeň zachycen 3 z 3, Boris 27 h předem; 2/2024 propásnutý (vrchol 496, práh 490) |
| **dělení v čase** | trénink ze starších let, ověření na jiných | train 2006–2018, validace 4 povodně + 2019–2020, test 2021–2025 jednou |
| **únik dat** | model omylem vidí budoucnost a vypadá lepší, než je | našli jsme dvě pasti: doplňování děr a denní srážky (známé až další den 07:00 UTC), obě opravené |
| **validace × test** | validace je na ladění, test jen jednou na konci | validace 17,1, test 22,4 (proti 50,2 u „jako teď“, o 55 % méně) |
| **vícenásobná validace** | každá z 8 povodní jednou vynechaná | regrese 20,1 ± 7,7, „jako teď“ 45,2 |
| **CV v tréninku** | 6 bloků let, model se učí bez jednoho bloku a hodnotí se na něm | 18 povodní; Ridge 30 stanic 14,2 proti 15,6 |
| **LOFO** (leave-one-flood-out) | každá z 22 povodní 2006–2020 jednou vynechaná, i s ± 20 dny | týmový Ridge D24 15,29; G3 13,94 |
| **znaménkový test** | kolikrát z N povodní je model lepší a jestli to může být náhoda | G3 lepší 20 z 22 (p = 0,0001, náhodou by to vyšlo jen velmi těžko); ve vícenásobné validaci 6 z 8 (p ≈ 0,29, mohla by to být náhoda) |
| **seed** | počáteční náhoda při tréninku | síť na validaci kolísá mezi seedy 17,8–20,6; LightGBM a regrese náhodu nemají |

## Modely

| Pojem | Co to je | Naše čísla |
|---|---|---|
| **lineární regrese** | vážený součet vstupů, každý vstup má jednu váhu | 98 vah; Boris: 198 cm průměr + Vltava 89 + horní Labe 116 + Mělník 95 + Děčín a Ústí 80 − Ohře 2 ≈ 577 cm (příspěvky jsou zaokrouhlené) |
| **Ridge a regularizace** | malá pokuta za velké váhy, ať se nepřeučí | alpha 0,1 až 10 dává stejně; záporné váhy = model odečítá starší hodnotu, počítá trend |
| **přeučení** | model se naučí trénink nazpaměť a na nových datech selže | síť 64-32 (starší rozbor D24 při velké vodě): trénink 5 cm, validace 22; LightGBM (starší běh, Děčín +12 h): 4,7 proti 27,8; regrese (D24): 19,7 proti 15,5, tedy ne |
| **neuronová síť** | vrstvy lineárních součtů s ohyby mezi nimi | 128-64 neuronů, přes 20 tisíc vah; 17,8, test 21,3 |
| **LightGBM** | stovky malých rozhodovacích stromů za sebou | 23,1; neumí výš, než viděl (2013: 823 místo 1 072 cm) |
| **směs modelů** | průměr předpovědí dvou modelů | G3 = ½ Ridge 30 + ½ LightGBM 30: LOFO −1,35 cm, ale validace D24 18,2 proti 15,5; regrese + síť 16,9 proti 17,1 |
| **SHAP** | kolik každý vstup přidal k předpovědi | LightGBM D24: nejvíc přírůstek průtoku v Praze, při povodni 2011 v průměru kolem 18–19 cm |
| **pásmo nejistoty** | „nejspíš od–do“ z 5. a 95. percentilu chyb | na povodních se vejde 76–88 % (cíl 90 %), šířka Děčín 33 / 53 / 72 cm |
| **začátek vzestupu** | za 24 h stoupne aspoň o 50 cm, ale posledních 6 h skoro nestoupalo | 18 nových stanic: Ridge 35,4 → 28,1, síť 32,4 → 26,7 |

## Tři věty ke slajdu 5 („Žádná z 11 dalších cest nebyla lepší“)

1. Zkusili jsme čtyři úplně různé modely a k tomu srážky, sníh, víc stanic, polynom, váhy na povodně a směsi, a nic
   co jde použít, nepřekonalo finální regresi aspoň o centimetr (o 1,0 cm jen dokonalá předpověď deště, která neexistuje).
2. Přímka vyhrála, protože voda v Děčíně je součet Vltavy, Labe a Ohře posunutých o dobu putování, a velké povodně jsou
   v tréninku jen dvě. Složitý model se z nich naučí i náhodu.
3. Na začátku vzestupu pomáhají hlavně stanice dál proti proudu (o 5–8 cm), méně i srážky. Celkově to ale
   v přísném LOFO prošla na 24 h jen směs dvou modelů (G3) a na 36 h regrese s 30 stanicemi, na validaci jsou obě
   horší, proto zůstáváme u jednoduché regrese.

## Tři věty ke slajdu 10 (co umíme a co ne)

1. Na 12 h se pleteme o 9 cm, na 24 h o 16 a na 36 h o 26: část vody, která přijde za 36 h, ještě neteče žádnou naší stanicí.
2. Vrcholy velkých povodní podhodnotí (Boris 649 cm předpověděl na 611), velké povodně jsou v tréninku jen dvě, a povodeň
   z deště přímo v kraji nevidí.
3. Dál by pomohla předpověď srážek na 2–3 dny a víc stanic proti proudu. S oficiální předpovědí ČHMÚ se srovnat neumíme,
   jejich historické chyby nemáme.
