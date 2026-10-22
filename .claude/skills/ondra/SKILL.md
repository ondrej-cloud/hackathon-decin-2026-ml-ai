---
name: ondra
description: Role Ondry – kapitán, ověřování, data. Spouští Ondra na začátku relace.
disable-model-invocation: true
---

Pracuješ s Ondrou. Je kapitán týmu a v ML se vyzná nejvíc (absolvoval pokročilé strojové učení), takže s ním mluv technicky a nevysvětluj základy.

Nejdřív:
1. Když nejsi na větvi `ondra`, přepni se (`git switch ondra`). Pak `git fetch origin` a `git merge origin/main`.
2. Podívej se, co je nového u ostatních: `git log --all --oneline --since="3 hours ago"` a sekce Stav v CLAUDE.md.
3. Jednou nebo dvěma větami shrň stav a co je podle harmonogramu teď na řadě.

Ondra má na starosti:
- Výběr tématu, rozhovory s mentory, čas a rozhodování sporů.
- Rozbor dat: velikost, typy, chybějící hodnoty, rozložení cílové proměnné, duplicity, skupiny nebo časová struktura (kvůli správnému rozdělení) a sloupce, které by mohly prozradit odpověď.
- Rozdělení dat do `data/split/` (stratifikace, skupiny nebo čas podle povahy dat; seed 42) a `src/evaluate.py` podle dohody v CLAUDE.md. Obojí potřebují ostatní do 19:00, takže hned potom `/sync main`.
- `src/features.py`: úprava dat a nové veličiny.
- Kontrolu výsledků ostatních (`/kontrola`). Výsledek se počítá, až ho Ondra uzná.
- Testovací část pouští jen jednou, na finální model (sobota 8:00–11:00).
- Technické odpovědi pro porotu: proč tahle metoda a metrika, jak víme, že výsledek není náhoda nebo únik dat.

Jak pomáháš:
- Navrhuj a piš kód do Ondrových souborů. Do cizích nezasahuj, napiš, co komu říct.
- Metodické chyby hlas dřív, než se z nich stane výsledek.
- Na kontrolních bodech (19:00, 21:00, 0:00, 8:00, 11:00) připrav `/stav`.
