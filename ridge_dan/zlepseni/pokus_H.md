## Pokus H (doplňkový): ukazatel útlumu vlny v nivě z týmových stanic

- Co: z rozboru A (2006: ~20 % vody se několik dní drží v nivě Polabí) přidán vstup „schodek v úseku“ = průtok po
  proudu − součet přítoků nad ním, pro Kostelec − (Nymburk + Jizera), Mělník − (Vraňany + Kostelec) a
  Ústí − (Mělník + Louny), zpoždění 0/6/12/24 h, 12 sloupců v m³/s. H12 = k týmovému Ridge, H30 = k Ridge 30.
  Alpha 1, nic se neladí. Zapsáno předem (PRUBEH 23:37) jako jediný doplňkový nápad; skript `pokus_H.py`.
- Výhrada: nápad vznikl z rozboru povodně 2006, která je ve validaci a v LOFO je jedním z 22 foldů.

| Varianta | LOFO 22 | rozdíl | zlepšeno z 22 | nejhorší zhoršení | znam. p | splňuje | val Děčín | začátek (LOFO) | 2006 (LOFO) | plané 2. SPA (LOFO) |
|---|---|---|---|---|---|---|---|---|---|---|
| týmový Ridge | 15,29 | | | | | | 15,5 | 41,9 | 16,7 | 4 |
| H12 tým + útlum | 14,61 | −0,68 | 16 | +0,6 | 0,053 | ne | **14,8** | 41,0 | 14,3 | 6 |
| Ridge 30 | 14,79 | −0,49 | 15 | +6,5 | 0,13 | ne | 17,8 | 34,1 | 23,3 | 3 |
| **H30 Ridge 30 + útlum** | **14,15** | **−1,13** | **18** | +5,9 | 0,004 | **ano** | 17,5 | 33,5 | 22,6 | 4 |

- Validace H12: 2006 13,4 cm (tým 16,0), přestřelení 2006 56 cm (57), 1 planý 2. SPA; H30: 2006 23,9, přestřelení 73.
- Závěr: ukazatel útlumu sám pomáhá týmovému modelu hlavně v roce 2006 (validace 14,8 proti 15,5), ale v LOFO
  jen o 0,68 cm. S 30 stanicemi pravidlo těsně splní (−1,13 cm, 18 z 22, žádná povodeň horší o víc než 5,9 cm),
  na validaci je ale pořád horší než týmový Ridge (17,5) – přestřelení 2006 z nových stanic ukazatel nespraví.
