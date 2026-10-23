### Srážky: hlavní sada (blizko + dal, 10 sloupců), podle ní verdikt

| model | varianta | CV povodně | CV začátek vzestupu | CV 8/2010 | VAL Děčín +24 povodně | VAL průměr 6 kombinací | VAL začátek vzestupu | VAL 9/2010 | VAL 4/2006 | plané 2. SPA | plané 3. SPA | propásnuto 2. SPA | propásnuto 3. SPA | verdikt |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Ridge týmový | beze změny | 15,64 | 35,00 | 27,6 | 15,5 | 17,08 | 35,4 | 20,8 | 16,0 | 0 | 0 | 0 | 0 |  |
|  | + srážky | 15,65 | 34,14 | 26,6 | 15,4 | 17,05 | 33,5 | 20,4 | 15,6 | 0 | 0 | 0 | 0 |  |
|  | rozdíl | +0,01 | −0,86 | −1,0 | −0,1 | −0,03 | −1,9 | −0,4 | −0,4 | +0 | +0 | +0 | +0 | **beze změny** |
| Ridge Danův | beze změny | 14,16 | 28,95 | 26,0 | 17,8 | – | 28,1 | 20,7 | 24,6 | 0 | 0 | 0 | 0 |  |
|  | + srážky | 14,10 | 29,03 | 25,5 | 18,1 | – | 28,4 | 21,0 | 25,4 | 0 | 0 | 0 | 0 |  |
|  | rozdíl | −0,07 | +0,08 | −0,5 | +0,3 | – | +0,3 | +0,3 | +0,8 | +0 | +0 | +0 | +0 | **beze změny** |
| LightGBM | beze změny | 17,77 ± 0,00 | 36,40 ± 0,00 | 27,2 ± 0,0 | 20,8 ± 0,0 | 23,03 ± 0,00 | 36,4 ± 0,0 | 21,1 ± 0,0 | 28,9 ± 0,0 | 0,0 ± 0,0 | 0,0 ± 0,0 | 0,0 ± 0,0 | 0,0 ± 0,0 |  |
|  | + srážky | 16,81 ± 0,00 | 35,54 ± 0,00 | 27,4 ± 0,0 | 20,3 ± 0,0 | 21,85 ± 0,00 | 31,8 ± 0,0 | 22,9 ± 0,0 | 28,1 ± 0,0 | 0,0 ± 0,0 | 4,0 ± 0,0 | 0,0 ± 0,0 | 0,0 ± 0,0 |  |
|  | rozdíl | −0,96 ± 0,00 | −0,86 ± 0,00 | +0,2 ± 0,0 | −0,5 ± 0,0 | −1,18 ± 0,00 | −4,6 ± 0,0 | +1,8 ± 0,0 | −0,8 ± 0,0 | +0,0 ± 0,0 | +4,0 ± 0,0 | +0,0 ± 0,0 | +0,0 ± 0,0 | **beze změny** |

- Ridge týmový: seedy –, srážky 0fa9e49a, řádky train/val Děčín +24 107314/18982, CV train 107314, validace 6 kombinací, nejnovější 2026-10-23T23:22:14
- Ridge Danův: seedy –, srážky 0fa9e49a, řádky train/val Děčín +24 107314/18982, CV train 107314, validace 1 kombinací, nejnovější 2026-10-23T23:21:54
- LightGBM: seedy 42, 43, 44, srážky 0fa9e49a, řádky train/val Děčín +24 107314/18982, CV train 107314, validace 6 kombinací, nejnovější 2026-10-24T00:36:39

### Srážky: citlivostní sada (blizko + dílčí povodí)

| model | varianta | CV povodně | CV začátek vzestupu | CV 8/2010 | VAL Děčín +24 povodně | VAL průměr 6 kombinací | VAL začátek vzestupu | VAL 9/2010 | VAL 4/2006 | plané 2. SPA | plané 3. SPA | propásnuto 2. SPA | propásnuto 3. SPA | verdikt |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Ridge týmový | beze změny | 15,64 | 34,92 | 27,6 | 15,5 | 17,08 | 35,4 | 20,8 | 16,0 | 0 | 0 | 0 | 0 |  |
|  | + srážky | 15,66 | 33,69 | 26,6 | 15,3 | 17,07 | 32,8 | 19,9 | 15,6 | 0 | 0 | 0 | 0 |  |
|  | rozdíl | +0,02 | −1,22 | −1,0 | −0,2 | −0,01 | −2,6 | −0,9 | −0,4 | +0 | +0 | +0 | +0 | **beze změny** |
| Ridge Danův | beze změny | 14,16 | 28,84 | 26,0 | 17,8 | – | 28,1 | 20,7 | 24,6 | 0 | 0 | 0 | 0 |  |
|  | + srážky | 14,15 | 28,76 | 25,4 | 18,0 | – | 28,2 | 20,6 | 25,2 | 0 | 0 | 0 | 0 |  |
|  | rozdíl | −0,01 | −0,08 | −0,6 | +0,2 | – | +0,1 | −0,1 | +0,6 | +0 | +0 | +0 | +0 | **beze změny** |

- Ridge týmový: seedy –, srážky 0fa9e49a, řádky train/val Děčín +24 107008/18982, CV train 107008, validace 6 kombinací, nejnovější 2026-10-23T23:23:51
- Ridge Danův: seedy –, srážky 0fa9e49a, řádky train/val Děčín +24 107008/18982, CV train 107008, validace 1 kombinací, nejnovější 2026-10-23T23:22:29

Rozdíl = + srážky − beze změny (záporný = menší chyba). Verdikt: lepší / horší od 1 cm, zvlášť CV povodně a VAL Děčín +24 povodně; když se liší, vypíšou se oba. Plané a propásnuté poplachy jsou součty přes kombinace z validace (u Danova Ridge jen Děčín +24 h).
