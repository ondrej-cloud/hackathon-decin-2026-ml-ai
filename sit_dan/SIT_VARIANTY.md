# Týmová neuronová síť: beze změny, + 18 stanic, + srážky

Síť je `src/models/mlp.py` z main beze změny (MLP 128-64, alpha 1, early stopping, cíl změna hladiny, odmocnina
průtoků, škálování). Varianty se liší jen vstupy a v každém srovnání běží na stejných řádcích (ověřil i Codex,
`codex/kontrola_sit.md`). Počítalo se na Kaggle (scikit-learn na CPU, 4 jádra), postup je v `PRUBEH.md`.
Test 2021–2025 se nespouštěl.

**Reprodukce:** varianta a se seedem 42 dává na Kaggle 17,83 cm (po kombinacích 9,3 / 18,4 / 25,7 / 9,0 / 16,5 / 28,1),
na desetinu stejně jako týmový výsledek (`results/2026-10-23_195305_mlp.json`).

## 1. Beze změny proti + 18 stanic: CV v tréninku a validace

Seedy 42, 43, 44, průměr ± rozptyl (směrodatná odchylka přes seedy). CV = časová CV v tréninku po blocích let
(`hodnoceni.bloky_cv`, stejně jako `ridge_dan/pokus.py`), Děčín +24 h, průměr přes 18 povodní nad 400 cm.
Validace = průměr `mae_povodne` přes 6 kombinací cíle a horizontu jako `porovnej.py`. Začátek vzestupu a povodně
2006 a 2010 jsou z validace, Děčín +24 h. Poplachy a propásnuté povodně jsou součty přes 6 kombinací.

| varianta | CV povodně | CV vzestup | validace povodně | začátek vzestupu | povodeň 2006 | povodeň 2010 | plané poplachy 2.+3. st. | propásnuto 2.+3. st. |
|---|---|---|---|---|---|---|---|---|
| a: beze změny (98 vstupů) | 16,05 ± 0,20 | 32,65 ± 0,64 | 19,01 ± 1,18 | 32,40 ± 0,22 | 22,17 ± 0,74 | 23,03 ± 0,91 | 0,3 | 0,3 |
| b: + 18 stanic (224 vstupů) | 15,53 ± 0,47 | 28,13 ± 0,69 | 21,14 ± 0,59 | 26,73 ± 0,66 | 30,10 ± 2,38 | 21,50 ± 0,16 | 0,0 | 1,7 |
| **b − a** (párově po seedech) | **−0,52 ± 0,45** | −4,52 ± 1,05 | +2,12 ± 0,62 | −5,67 ± 0,49 | +7,93 ± 2,69 | −1,53 ± 1,07 | −0,3 | +1,3 |

Verdikt: **beze změny.** Podle CV se zlepší jen o 0,5 cm, to je pod hranicí 1 cm. Na validaci je + 18 stanic horší
o 2,1 cm a propásne víc povodní před 2. stupněm (1–2 na seed proti 0–1). U jarní povodně 2006 je horší o 8 cm a víc
přestřeluje (největší přestřelení při stoupání 50–84 cm proti 41–52 cm). Lepší je jen na začátku vzestupu (o 5,7 cm,
v CV o 4,5 cm na rychlém stoupání) a u povodně 2010 (o 1,5 cm).

Pozor na náhodu: validace sítě kolísá mezi seedy až o 2,8 cm (varianta a 17,8–20,6 cm), u CV jen o 0,5 cm.
Rozdíl na validaci je proto jen orientační, rozhoduje CV.

Tabulka po seedech (`souhrn_beh1.md`, předpovědi `kaggle/vystup/labe-sit-dan-beh/`, mimo Git):

| varianta | seed | CV povodně | validace povodně | začátek vzestupu | 2006 | 2010 | propásnuto |
|---|---|---|---|---|---|---|---|
| a | 42 | 15,78 | 17,83 | 32,7 | 21,8 | 24,3 | 0 |
| a | 43 | 16,07 | 20,63 | 32,3 | 23,2 | 22,2 | 1 |
| a | 44 | 16,28 | 18,58 | 32,2 | 21,5 | 22,6 | 0 |
| b | 42 | 15,59 | 20,45 | 27,6 | 27,4 | 21,3 | 2 |
| b | 43 | 14,92 | 21,88 | 26,0 | 29,7 | 21,7 | 2 |
| b | 44 | 16,07 | 21,08 | 26,6 | 33,2 | 21,5 | 1 |

## 2. LOFO-CV přes 22 povodní 2006–2020

Foldy ze session ridge (`lofo_foldy.csv`): drží se okno povodně (7 dní před až 5 po vrcholu), z tréninku se vyřadí
okno ± 20 dní, trénuje se na všem ostatním z let 2006–2020. Děčín, 3 horizonty × 22 foldů × 2 varianty = 132 tréninků
na 5 souběžných kernelech. **Jen seed 42**, se třemi seedy by to do 00:10 nedoběhlo. Out-of-fold předpovědi:
`lofo/sit_lofo_oof.parquet` (mimo Git, formát v `lofo/README.md`).

| horizont | a | b | b − a | povodní lepších s b | znaménkový test p | největší zhoršení | začátek vzestupu a / b | jarní povodeň 2006 a / b |
|---|---|---|---|---|---|---|---|---|
| +12 h | 8,00 | 8,97 | +0,97 | 7 z 22 | 0,13 | +9,2 | 20,8 / 17,6 | 8,0 / 10,8 |
| +24 h | 15,07 | 16,05 | +0,98 | 8 z 22 | 0,29 | +8,0 | 39,2 / 34,1 | 15,6 / 23,4 |
| +36 h | 26,89 | 26,02 | −0,87 | 15 z 22 | 0,13 | +12,4 | 61,4 / 54,2 | 39,7 / 29,7 |

Chyba po povodních, Děčín +24 h (a / b / b − a):
2006-04-02 15,6 / 23,4 / +7,8; 2006-05-31 18,8 / 11,8 / −7,0; 2006-07-01 14,2 / 13,5 / −0,7; 2006-08-09 12,4 / 13,8 / +1,4;
2007-12-08 10,1 / 7,5 / −2,6; 2008-03-03 10,5 / 9,6 / −0,9; 2009-03-06 8,3 / 9,8 / +1,5; 2009-06-30 21,2 / 26,3 / +5,1;
2010-03-02 8,3 / 9,9 / +1,6; 2010-03-22 6,4 / 6,7 / +0,3; 2010-06-03 11,3 / 9,9 / −1,4; 2010-08-08 30,6 / 35,6 / +5,0;
2010-09-28 20,5 / 28,5 / +8,0; 2011-01-16 15,1 / 17,6 / +2,5; 2012-01-24 10,1 / 10,3 / +0,2; 2012-03-01 12,9 / 11,7 / −1,2;
2012-12-29 12,9 / 11,0 / −1,9; 2013-01-08 11,0 / 11,9 / +0,9; 2013-02-01 11,3 / 13,4 / +2,1; 2013-06-05 44,4 / 44,6 / +0,2;
2013-06-26 14,9 / 17,2 / +2,3; 2015-01-11 10,8 / 9,1 / −1,7.

Verdikt LOFO: **beze změny.** Rozdíly jsou pod 1 cm a znaménkový test nic neukazuje (p 0,13–0,29). Na 12 a 24 h je
+ 18 stanic spíš horší (lepší jen u 7 a 8 povodní z 22), na 36 h spíš lepší (15 z 22). To sedí s tím, že nové stanice
jsou hlavně dál proti proudu a jejich voda doteče až za víc než den. Začátek vzestupu je s novými stanicemi lepší
na všech horizontech (o 3–7 cm). Jarní povodeň 2006 je na 12 a 24 h horší, na 36 h lepší. Jeden seed: síť kolísá mezi
seedy víc, než jsou tyhle rozdíly, proto to beru jen jako směr.

## 3. + srážky

Doplním po přepočtu (běh na 4 kernelech doběhl, stahuje se).

## Celkově

Pro síť 18 nových stanic nepomohly: CV i LOFO beze změny (pod 1 cm), na validaci spíš horší a s víc propásnutými
povodněmi. Jediné, co pomáhá soustavně, je začátek vzestupu. U Ridge a LightGBM vyšly nové stanice v CV lépe
(o 1,5 a 2,0 cm, session ridge). Domněnka: síť s 224 vstupy a jen pár povodněmi v tréninku z nich vytáhne víc šumu než užitku.
