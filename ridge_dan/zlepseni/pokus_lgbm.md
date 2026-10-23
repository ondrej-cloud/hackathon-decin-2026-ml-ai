# Podklady pro směsi G (LOFO předpovědi), stav k so 00:11

- Hotovo 23:27: `oof/ridge_12.parquet`, `oof/ridge_30.parquet` (LOFO 22 povodní, sloupce fold, cas, y, pred).
- LightGBM 30 (seed 42) **nedoběhl do 00:10**: skript čekal na volnou RAM (brána 1,5 GB, souběžně běželo 5 dalších
  pokusů) do 23:47 a pak počítá jen asi na třetině jádra (přetížené CPU). Proces `pokus_G_priprava.py` (PID 19968)
  dál běží a až doběhne, sám uloží `oof/lgbm_30.parquet`, `vysledky_lgbm.json`, pak `oof/lgbm_12.parquet`.
- Skóre LightGBM v LOFO proto zatím chybí; validace je ze `stanice_vsem`: lgbm_30 prumer 22,08, Děčín +24 20,4;
  lgbm_12 23,07 / 21,3.

## Doplněno so 00:27: LightGBM 30 doběhl (3 541 s, `oof/lgbm_30.parquet`, `vysledky_lgbm.json`)

| varianta | LOFO 22 povodní | rozdíl proti týmovému Ridge | zlepšeno z 22 | nejhorší zhoršení | splňuje | začátek | 2006 | plané 2./3. SPA |
|---|---|---|---|---|---|---|---|---|
| Ridge 12 (tým) | 15,29 | | | | | 41,9 | 16,7 | 4/1 |
| LightGBM 30 | 16,06 | +0,78 | 11 | +12,1 | ne | 37,9 | 28,9 | 7/2 |

LightGBM s novými stanicemi je v LOFO horší než týmový Ridge a má víc planých poplachů. LightGBM 12 dál běží
(soubor `oof/lgbm_12.parquet` přibude až po 00:30), srovnání LightGBM 30 proti LightGBM 12 tedy zatím chybí.
Validace ze `stanice_vsem`: lgbm_30 Děčín +24 20,4 (prumer 22,08), lgbm_12 21,3 (23,07).
