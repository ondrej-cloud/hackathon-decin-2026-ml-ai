---
name: stav
description: Přehled stavu celého týmu na kontrolní body (19:00, 21:00, 0:00, 8:00, 11:00).
disable-model-invocation: true
---

Připrav podklad na desetiminutovou poradu:

1. `git fetch origin`.
2. Pro každou větev (`main`, `ondra`, `dan`, `honza`, `tobias`) projdi commity za poslední 3 hodiny: `git log origin/<větev> --since="3 hours ago" --oneline`.
3. Projdi výsledky v `results/` na všech větvích (`git ls-tree -r --name-only origin/<větev> results/`, obsah přes `git show`). Najdi nejlepší výsledek na validační části a porovnej ho s baseline.
4. Porovnej to s harmonogramem v CLAUDE.md: co mělo být k tomuto času hotové.

Výstup:
- tabulka Kdo | Hotovo | Rozpracované | Co ho blokuje
- nejlepší výsledek zatím (a jestli ho Ondra uznal)
- největší rizika
- co musí být hotové do dalšího kontrolního bodu
