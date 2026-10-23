---
name: ondra
description: Kontext pro Ondru – kapitán týmu, ověřování výsledků. Spouští Ondra na začátku relace.
disable-model-invocation: true
---

Pracuješ s Ondrou. Je kapitán týmu a v ML se vyzná nejvíc (absolvoval pokročilé strojové učení), takže s ním mluv technicky a nevysvětluj základy. Má MacBook M1 16 GB a Claude Max.

Nejdřív:
1. Když nejsi na větvi `ondra`, přepni se (`git switch ondra`). Pak `git fetch origin` a `git merge origin/main`.
2. Podívej se, co je nového: Stav v CLAUDE.md a `git log --all --oneline --since="3 hours ago"`.
3. Jednou nebo dvěma větami shrň stav a co je podle harmonogramu na řadě. Když ve Stavu není, na čem Ondra teď dělá, zeptej se.

Co Ondra drží vždycky:
- Vede tým: výběr tématu, mentory, čas a rozhodnutí, když se neshodneme.
- Hlídá poctivé ověření: společné rozdělení dat, jedno vyhodnocení pro všechny, kontrola výsledků (`/kontrola`) a jediný test na testovací části na finální model.
- Rozumí celému řešení a odpovídá na technické otázky poroty: proč tahle metoda a metrika, jak víme, že výsledek není náhoda nebo únik dat.

Kromě toho dělá, co je zrovna potřeba, nejčastěji data a ověřování. Metodické chyby hlas dřív, než se z nich stane výsledek. Na kontrolních bodech (19:00, 21:00, 0:00, 8:00, 11:00) připrav `/stav`.
