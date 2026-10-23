---
name: denik
description: Kontrola dokumentace. Dohledá, co se od posledního zápisu udělalo na všech větvích a v docs/ chybí, a doplní to. Spouští se jednou za hodinu.
disable-model-invocation: true
model: sonnet
---

Zápisy dělá každý Claude průběžně (sekce Dokumentace v CLAUDE.md). Tenhle příkaz dohledá, co se nezapsalo.

1. `git fetch origin`. Najdi čas posledního záznamu `Shrnutí` v `docs/DENIK.md` a projdi commity na všech větvích od té doby: `git log --all --since="<čas>" --stat`.
2. Porovnej je se záznamy v `docs/DENIK.md` a `docs/POKUSY.md` na všech větvích (`git show origin/<větev>:docs/POKUSY.md`), ať nevznikají dvojí, a s novými soubory v `results/`. Co chybí, doplň:
   - pokus nebo trénink bez záznamu do `docs/POKUSY.md`,
   - rozhodnutí nebo změnu postupu bez vysvětlení do `docs/DENIK.md`,
   - nové zjištění o datech do `docs/DATA.md`.
3. Co z commitů nepoznáš, třeba proč to někdo udělal, nevymýšlej. Napiš „proč: zeptat se <jméno>“ a řekni to člověku.
4. Piš jednoduše, aby se to dalo říct porotě. Odborné výrazy vysvětli v závorce. Formát záznamů je v hlavičce každého souboru.
5. Na konec `docs/DENIK.md` připiš záznam `## <čas> · Shrnutí` se třemi body: co se za poslední hodinu posunulo, nejlepší výsledek zatím a co je nejasné nebo chybí v `docs/POROZUMENI.md`.
6. Proveď `/sync`.

Šetři limit: čti diffy a výsledky, ne celé soubory.
