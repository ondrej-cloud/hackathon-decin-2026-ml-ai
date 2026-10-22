---
name: tobias
description: Role Tobiase – prezentace, deník, pohled uživatele. Spouští Tobias na začátku relace.
disable-model-invocation: true
model: sonnet
---

Pracuješ s Tobiasem. Má na starosti prezentaci, deník a pohled běžného uživatele. Bude prezentovat, takže mu všechno vysvětluj jednoduše, aby to porotě uměl říct vlastními slovy.

Tobias má Claude Pro s menším limitem:
- Hned mu připomeň, ať přepne model příkazem `/model sonnet`.
- Odpovídej stručně, čti jen to, co je potřeba (diffy a výsledky, ne celé soubory), a nespouštěj paralelní agenty.

Nejdřív:
1. Když nejsi na větvi `tobias`, přepni se (`git switch tobias`). Pak `git fetch origin` a `git merge origin/main`.
2. Jednou nebo dvěma větami shrň stav a co je podle harmonogramu teď na řadě.

Úkoly:
1. Hned po výběru tématu vyplň sekci Stav v CLAUDE.md (zadání, komu řešení pomáhá, data, metrika, predict.py) podle toho, co tým domluvil, a pošli ji přes `/sync main`. Potřebují ji všichni.
2. Každou hodinu spusť `/denik`.
3. Poznámky od mentorů zapisuj do `docs/mentori.md`: kdo, kdy, co řekl a co z toho plyne.
4. Od 21:00 skládej osnovu prezentace v `docs/prezentace.md`: problém → pro koho → data → postup → výsledek a jak víme, že funguje → demo → co dál. Celá prezentace má max. 15 minut. Čísla ber jen z výsledků, které uznal Ondra.
5. Zkoušej aplikaci jako laik a piš Honzovi, čemu nerozumíš.
6. V sobotu ráno s Ondrou `/porota`, pak dva nácviky celé prezentace a ve 14:00 odevzdání.

Tobiasův Mac s M4 je počítač, ze kterého poběží demo.
