---
name: denik
description: Zapíše do docs/DENIK.md, co se v týmu změnilo od posledního zápisu. Spouští Tobias každou hodinu.
disable-model-invocation: true
model: sonnet
---

1. Najdi čas posledního zápisu v `docs/DENIK.md` (nadpis `## HH:MM`). Když soubor neexistuje, vytvoř ho s nadpisem `# Deník týmu`.
2. `git fetch origin` a projdi commity na všech větvích od toho času: `git log --all --since="<čas>" --stat`. Nové výsledky z `results/` si přečti přes `git show`.
3. Ke každé podstatné změně připiš záznam:

```
## HH:MM
- Změna: …
- Proč: …
- Výsledek: … (soubor v results/)
- Otázka pro mentory: … (jen když dává smysl)
```

4. Piš jednoduše, aby to Tobias mohl říct porotě. Odborné výrazy vysvětli v závorce.
5. Změň jen `docs/DENIK.md` a pak proveď `/sync`.

Šetři limit: čti jen diffy a výsledky, ne celé soubory.
