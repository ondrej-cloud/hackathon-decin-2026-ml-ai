## Pokus C: součty po dílčích povodích místo jednotlivých nových stanic

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
