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

*(průběžně doplňováno; hotovo C, E; běží A, B, D, F, LightGBM, směsi G)*

### Pokus C: součty po dílčích povodích místo jednotlivých nových stanic

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

### Pokus E: delší zpoždění u vzdálených stanic, Děčín +36 h

- Co: k Ridge s 30 stanicemi při horizontu 36 h přidat zpoždění 48/60/72 h u nejvzdálenějších stanic (horní Berounka,
  horní Ohře, horní Sázava, Chrudimka, Orlice; 11 stanic, +33 sloupců). Alpha 1, nic se nevybírá. Skript `pokus_E.py`,
  čísla `vysledky_E.json`.
- Proč: na 36 h je doba doběhu z Plzně, Liblína nebo Karlových Varů do Děčína (29–42 h) blízko nebo nad nejdelším
  týmovým zpožděním 36 h, starší průtoky by mohly nést vlnu, která do Děčína teprve přijde.
- Výsledek (LOFO-CV 22 povodní, Děčín +36 h, základ týmový Ridge):

| Varianta | LOFO | rozdíl | zlepšeno z 22 | nejhorší zhoršení | splňuje | val | začátek (LOFO) | 2006 (LOFO) | plané 2. SPA (LOFO) |
|---|---|---|---|---|---|---|---|---|---|
| týmový Ridge 36 h | 26,39 | | | | | 26,0 | 66,5 | 28,3 | 6 |
| Ridge 30 stanic 36 h | 23,96 | −2,43 | 17 (p = 0,017) | +7,0 (2006) | **ano** | 26,6 | 53,5 | 35,3 | 7 |
| E: + 48/60/72 h | 24,10 | −2,28 | 17 (p = 0,017) | +11,6 (2006) | ne | 27,1 | 53,6 | 40,0 | 8 |

- Proti Ridge 30 při 36 h je E o 0,15 cm horší, zlepší jen 10 z 22 povodní (nejhorší +4,7).
- Závěr: delší zpoždění nepomáhají, zhorší povodeň 2006 (o dalších 4,7 cm) a přidají planý poplach. Samotných
  30 stanic při 36 h pravidlo proti týmovému Ridge splní (−2,4 cm, 17 z 22, nejhorší +7,0 v roce 2006), na validaci
  ale vychází o 0,6 cm hůř (26,6 proti 26,0), opět kvůli 2006 (36,2 proti 26,8, přestřelení 84 cm).

