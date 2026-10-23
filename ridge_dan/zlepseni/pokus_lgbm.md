# Podklady pro směsi G (LOFO předpovědi), stav k so 00:11

- Hotovo 23:27: `oof/ridge_12.parquet`, `oof/ridge_30.parquet` (LOFO 22 povodní, sloupce fold, cas, y, pred).
- LightGBM 30 (seed 42) **nedoběhl do 00:10**: skript čekal na volnou RAM (brána 1,5 GB, souběžně běželo 5 dalších
  pokusů) do 23:47 a pak počítá jen asi na třetině jádra (přetížené CPU). Proces `pokus_G_priprava.py` (PID 19968)
  dál běží a až doběhne, sám uloží `oof/lgbm_30.parquet`, `vysledky_lgbm.json`, pak `oof/lgbm_12.parquet`.
- Skóre LightGBM v LOFO proto zatím chybí; validace je ze `stanice_vsem`: lgbm_30 prumer 22,08, Děčín +24 20,4;
  lgbm_12 23,07 / 21,3.
