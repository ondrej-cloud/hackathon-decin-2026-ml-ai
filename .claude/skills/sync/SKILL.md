---
name: sync
description: Commit a push vlastní práce a stažení práce ostatních. "/sync main" pošle hotovou práci i do main. Použij, když člověk řekne "commitni", "pushni" nebo "synchronizuj".
argument-hint: "[main]"
model: sonnet
---

Synchronizuj práci podle pravidel týmu:

1. Zjisti větev (`git branch --show-current`). Když je to `main`, zastav se a zeptej se, na čí větev se přepnout.
2. `git status`. Do commitu přidej soubory, na kterých se v této relaci pracovalo, a nové výsledky v `results/`. Nikdy ne `git add .` naslepo, data, `.env`, `kaggle.json` ani velké modely. Když jsou změněné soubory, o kterých nevíš, zeptej se.
3. Když se v relaci trénovalo, rozhodovalo nebo zjistilo něco o datech a v `docs/` to chybí, nejdřív to zapiš podle sekce Dokumentace v CLAUDE.md a přidej do commitu.
4. Commit česky jednou větou ve tvaru `<Jméno>: co a proč`. Bez `Co-Authored-By` a bez zmínek o Claude. Když není co commitnout, pokračuj dalším krokem.
5. `git fetch origin` a `git merge origin/main`. Na stejných souborech pracuje víc lidí, takže konflikt vyřeš tak, aby zůstaly změny obou stran. Když si nejsi jistý, zeptej se.
6. `git push origin <větev>`.
7. Když argumenty obsahují `main` ($ARGUMENTS): nejdřív ověř, že kód běží (spusť to, co se změnilo), pak `git push origin HEAD:main`. Když je push odmítnutý, někdo byl rychlejší: opakuj od kroku 5. Nikdy `--force`.
8. Když se změnilo něco, co používají ostatní (názvy souborů, struktura, rozhraní), připomeň, ať se to zapíše do Stavu v CLAUDE.md.
9. Na závěr jednou větou řekni, co odešlo a kam.
