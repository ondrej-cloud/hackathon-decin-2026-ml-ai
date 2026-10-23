# Out-of-fold předpovědi týmové sítě (LOFO-CV)

Pro směsi modelů v session ridge. Data nejsou v Gitu, soubor `sit_lofo_oof.parquet` je jen ve worktree
`hackathon-2026-sit/sit_dan/lofo/`.

- Model: týmová neuronová síť `src/models/mlp.py` beze změny (MLP 128-64, alpha 1, early stopping, cíl změna hladiny), seed 42.
- Foldy: `sit_dan/lofo_foldy.csv` = kopie `hackathon-2026-ridge/ridge_dan/stanice_vsem/lofo_foldy.csv` (22 povodní 2006–2020,
  okno 7 dní před až 5 po vrcholu, z tréninku vyřazeno okno ± 20 dní). Řádky stejné jako v `ridge_dan/zlepseni/lofo.py`.
- Sloupce: `cas` (čas vydání předpovědi t, UTC), `cil` (decin), `horizont` (12 / 24 / 36), `varianta`
  (`beze_zmeny` = 98 týmových vstupů, `plus_18_stanic` = + průtoky 18 nových stanic, 224 vstupů), `predpoved` (stav v cm
  v čase t + horizont), navíc `skutecnost`, `fold`, `povoden`, `seed`.
- Každý řádek okna je předpovězený modelem, který jeho povodeň (ani ± 20 dní kolem) neviděl. V každém horizontu se
  ale překrývají okna dvou blízkých povodní (konec 12/2012 a začátek 1/2013, asi 47 h). Tyhle hodiny jsou v souboru
  dvakrát, jednou z každého foldu (`fold`). Obě předpovědi jsou out-of-fold, protože mezera každého foldu zakrývá
  i okno toho druhého. Pro směs je potřeba buď vybrat jeden fold, nebo je zprůměrovat.
- Test 2021–2025 se nepoužil.
