# Pokus D: vnořený dopředný výběr nových stanic (Ridge Děčín +24 h)

- Co: v každém z 22 foldů LOFO-CV zvlášť začne model s týmovými 98 vstupy a po jedné přidává novou stanici (všech
  7 zpoždění), vždy tu, která nejvíc sníží vnitřní LOFO chybu přes zbylých 21 povodní (modely bez mezer k i j);
  přidá ji jen při striktním zlepšení. Alpha 1, odmocnina průtoků jako v týmu. Validace: tentýž výběr jen z tréninku
  týmového splitu (vnitřní LOFO přes jeho 18 povodní). Skript `pokus_D.py`, výsledky `vysledky_D.json`, 18 min.
- Proč: všech 18 stanic přidává šum a protichůdné váhy; výběr jen užitečných stanic by mohl zisk zachovat a
  přeučení zmenšit.

| Varianta | LOFO 22 | rozdíl | zlepšeno z 22 | nejhorší zhoršení | znam. test p | splňuje | VAL | začátek (LOFO) | 2006 (LOFO) | plané 2. SPA (LOFO) |
|---|---|---|---|---|---|---|---|---|---|---|
| týmový Ridge (12 stanic) | 15,29 | | | | | | 15,5 | 41,9 | 16,7 | 4 |
| Ridge 30 stanic | 14,79 | −0,49 | 15 | +6,5 | 0,13 | ne | 17,8 | 34,1 | 23,3 | 3 |
| **D: vnořený výběr** | **14,68** | **−0,61** | **16** | **+4,7** (2006) | 0,053 | **ne** | 17,2 | 36,1 | 21,4 | 3 |

- Výběr je velmi stabilní: ve všech 22 foldech Žatec, Karlovy Vary, Plzeň-Bílá Hora, Litavka, Orlice Týniště,
  Jizera Bakov, ve 21 Zbraslav, v 10 Bílina Trmice; Stružnice, Zruč, Sány po jednom; Ploučnice Benešov, Česká Lípa,
  Zbečno, Liblín, Střela, Kácov, Chrudimka nikdy. Na validačním tréninku vybráno 10 stanic (tytéž + Zruč, Střela,
  Trmice). Vnitřní chyba klesá z ~15,4 na ~14,4 cm.
- Zhoršení po povodních malá: nejvíc 2006 (+4,7), pak 1/2011 +0,9, 6/2013 +0,4, 8/2010 +0,3.
- Závěr: oproti všem 30 stanicím je výběr o 0,1 cm lepší, zlepší 16 z 22 povodní a největší zhoršení (2006) zmenší
  z 6,5 na 4,7 cm. Pravidlo ale **nesplní**: průměrné zlepšení proti týmovému Ridge je jen 0,61 cm (< 1 cm).
  Na validaci 17,2 proti týmovým 15,5.
