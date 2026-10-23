# Dá se ze stanic vytěžit zlepšení, které projde přísným hodnocením?

Dan, větev `dan-ridge`, pá 23. 10. 2026 23:15–00:30. Kód `ridge_dan/zlepseni/` (motor `lofo.py`, pokusy
`pokus_<X>.py`, výsledky `vysledky_<X>.json`, zápisy `pokus_<X>.md`), směsi od Codexu v `ridge_dan/smesi/`.
Test 2021–2025 je spotřebovaný, nespouštěl se a nic se podle něj nerozhodovalo.

## Verdikt

*(doplní se, až doběhnou pokusy)*

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

## Pokusy

*(průběžně doplňováno; stav: A–F a směsi G běží od 23:21)*
