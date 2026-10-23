# Průběh: pásmo nejistoty předpovědi a revize aplikace

Dan, větev `dan-nejistota` (z `origin/main` 59956c9), worktree `hackathon-2026-nejistota`, noc 23./24. 10. Čas + jedna věta.

- 01:43 Worktree `hackathon-2026-nejistota` s větví `dan-nejistota` z `origin/main`; ostatní worktree jen čtu, v `hackathon-2026-ridge` nic nespouštím.
- 01:44 Přečten `src/nejistota.py` (tým): 5. a 95. percentil chyby Ridge na TRÉNINKU podle pásma hladiny teď, ukládá `models/ridge_intervaly.json`, čte ho aplikace; navazuju na něj (stejný formát pásma, stejné místo použití), jen kvantily beru z předpovědí mimo trénink.
- 01:45 Kandidáti: G3 = ½ Ridge 30 + ½ LightGBM 30 (`src/models/g3.py`, `ridge30.py` z `dan-ridge` c53a491), LOFO předpovědi mimo trénink existují jen pro Děčín +24 h (`ridge_dan/zlepseni/oof/`); kód zkopírovaný přes `git show` do `nejistota_dan/kandidati/`, zbytek dopočítám tady.
- 01:57 Prototyp na týmovém Ridge: dnešní týmové pásmo (chyby na tréninku) pokrývá na povodních místo 80 % jen 59–72 % a na začátku vzestupu 9–22 %; konformní pásmo z chyb mimo trénink dává celkem 79–80 % / 94–95 %, při rychlém vzestupu ale jen 47–71 %. Předem dané varianty: globální, trend za 6 h, režim podle předpovězené změny, režim × výška, 6 pásem předpovězené změny; výběr podle intervalového skóre. Zkoušený a zamítnutý signál proti proudu (změna průtoku v Mělníku za 12 h): horší skóre i pokrytí při vzestupu.
