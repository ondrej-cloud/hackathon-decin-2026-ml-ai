## Pokus B: silnější regularizace nových stanic

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
- Vnořená varianta B (doběhla 00:05): ve všech 22 foldech vnitřní LOFO vybralo f = 1, takže B = Ridge 30:
  LOFO 14,79, rozdíl −0,49, zlepšeno 15 z 22, nejhorší zhoršení +6,5, nesplňuje. Validace B (vnořený výběr na
  týmovém splitu přes 18 tréninkových povodní, taky f = 1): val povodně 17,8 (tým 15,5), začátek vzestupu 28,1,
  2006 24,6 (přestřelení na stoupání 68 cm), plané 2./3. SPA 0/0.
- Závěr: silnější penalizace nových stanic průměr nezlepší (nejlíp f = 1, −0,49 cm). Zmenší jen nejhorší zhoršení
  (6,5 → 4,4 cm) a chybu 2006 (23,3 → 21,1), ale o tolik zhorší začátek vzestupu (34,1 → 38,7). Pravidlo nesplní
  žádné f.
