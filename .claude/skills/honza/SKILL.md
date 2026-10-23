---
name: honza
description: Kontext pro Honzu – výchozí zaměření aplikace a grafy. Spouští Honza na začátku relace.
disable-model-invocation: true
---

Pracuješ s Honzou. Má starší notebook a Claude Max. Jeho výchozí zaměření je aplikace a grafy, ale role se v týmu míchají, takže může dělat cokoli, co je zrovna potřeba.

Nejdřív:
1. Když nejsi na větvi `honza`, přepni se (`git switch honza`). Pak `git fetch origin` a `git merge origin/main`.
2. Přečti Stav v CLAUDE.md a poslední commity (`git log --all --oneline --since="3 hours ago"`).
3. Jednou nebo dvěma větami shrň stav a co je podle harmonogramu na řadě. Když ve Stavu není, na čem Honza teď dělá, zeptej se.

Honzův notebook je starší: těžké knihovny instaluj jen tehdy, když jsou opravdu potřeba, a dlouhý trénink na něm nepouštěj. Demo nejspíš poběží na Tobiasově Macu s M4, takže tam aplikace musí jít spustit.

Když jde o aplikaci:
- Nejdřív kostra s falešnou předpovědí se stejným rozhraním, jaké bude mít skutečný model (rozhraní je ve Stavu). Skutečný model se napojí, jakmile bude.
- Navrhuj pro laika: vstup → výsledek → jednoduché vysvětlení, proč to tak vyšlo. České popisky, srozumitelné grafy, žádný žargon. Na první pohled musí být jasné, komu aplikace pomáhá.
- Grafy pro prezentaci ukládej i jako obrázky.
- Udržuj seznam knihoven, které aplikace potřebuje (`requirements.txt`), ať jde spustit na jiném počítači.
- Do 13:00 v sobotu musí existovat záložní video dema pro případ, že na prezentaci něco selže.
