## Pokus E: delší zpoždění u vzdálených stanic, Děčín +36 h

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
