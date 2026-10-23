---
name: kontrola
description: Kontrola nových výsledků a kódu – únik dat, rozdělení, metrika, baseline. Obvykle ji spouští Ondra.
argument-hint: "[co zkontrolovat]"
disable-model-invocation: true
---

Zkontroluj nové výsledky a kód od poslední kontroly. Pokud jsou zadané argumenty, zkontroluj jen to: $ARGUMENTS

1. `git fetch origin` a najdi nové soubory v `results/` a nové commity na všech větvích.
2. Na každý nový výsledek, který něco tvrdí, pusť subagenta `kontrolor`. Víc výsledků kontroluj paralelně.
3. Shrň to tabulkou Výsledek | Autor | Metrika | Verdikt (platí / neplatí / nejasné) | Proč.
4. Na závěr napiš, co komu říct, aby to opravil.
