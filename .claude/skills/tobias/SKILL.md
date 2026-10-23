---
name: tobias
description: Kontext pro Tobiase – výchozí zaměření prezentace a pohled uživatele. Spouští Tobias na začátku relace.
disable-model-invocation: true
model: sonnet
---

Pracuješ s Tobiasem. Má MacBook M4 16 GB (nejvýkonnější Mac v týmu, nejspíš z něj poběží demo) a Claude Pro s menším limitem. Jeho výchozí zaměření je prezentace a pohled běžného uživatele, ale role se v týmu míchají, takže může dělat cokoli, co je zrovna potřeba. Vysvětluj mu věci jednoduše, aby je porotě uměl říct vlastními slovy.

Šetři jeho limit:
- Hned mu připomeň, ať přepne model příkazem `/model sonnet`.
- Odpovídej stručně, čti jen to, co je potřeba (diffy a výsledky, ne celé soubory), a nespouštěj paralelní agenty.
- Když je potřeba velký kus práce s kódem, navrhni, ať ho vezme někdo s účtem Max.

Nejdřív:
1. Když nejsi na větvi `tobias`, přepni se (`git switch tobias`). Pak `git fetch origin` a `git merge origin/main`.
2. Jednou nebo dvěma větami shrň stav a co je podle harmonogramu na řadě. Když ve Stavu není, na čem Tobias teď dělá, zeptej se.

Když jde o prezentaci:
- Hlídej otázku, kterou zdůrazňují pořadatelé: komu řešení pomáhá a jak poznáme, že funguje.
- Deník (`/denik`), poznámky od mentorů (kdo, kdy, co řekl, co z toho plyne) a osnova prezentace patří do `docs/`.
- Pořadí prezentace: problém → pro koho → data → postup → výsledek a jak víme, že funguje → demo → co dál. Nejvýš 15 minut. Čísla ber jen z výsledků, které zkontroloval Ondra.
- Zkoušej aplikaci jako laik a řekni, čemu nerozumíš.
