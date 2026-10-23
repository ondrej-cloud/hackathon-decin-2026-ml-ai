# Hackathon ML/AI 2026 – kontext pro Claude

Pracuješ v týmu čtyř středoškoláků na Hackathonu ML/AI 2026 (FJFI ČVUT Děčín). Soutěž startuje v pátek 23. 10. v 16:00, práce končí v sobotu 24. 10. ve 14:00 a od 14:30 prezentujeme porotě (max. 15 minut). Chceme vyhrát. Pořadatelé používání jazykových modelů povolili.

Na začátku relace člověk zadá `/ondra`, `/dan`, `/honza` nebo `/tobias`. Z toho poznáš, s kým pracuješ. Když to neudělá, zeptej se ho, kdo je.

## Stav (aktualizuje kdokoli, kdo má novou informaci)

- **Zadání:** zatím neznámé, témata se představí v pátek v 15:30
- **Komu řešení pomáhá:**
- **Data:** (kde leží v `data/raw/`, co obsahují, velikost)
- **Metrika:** (jedna hlavní metrika a s jakým jednoduchým řešením se srovnáváme)
- **Rozdělení a vyhodnocení:** (kde je společné rozdělení dat a jak se volá společné vyhodnocení)
- **Propojení modelu a aplikace:** (co předpověď bere a vrací, kde je)
- **Kdo teď na čem dělá:**
    - Ondra:
    - Dan:
    - Honza:
    - Tobias:
- **Smějí data do cloudu (Kaggle, Colab, jazykové modely)?** zeptat se pořadatelů

## Tým

| Kdo | Větev | Počítač a účet | Výchozí zaměření |
|---|---|---|---|
| Ondra | `ondra` | MacBook M1 16 GB, Claude Max | vede tým, ověřuje výsledky; v ML se vyzná nejvíc |
| Dan | `dan` | Lenovo Yoga 7i bez NVIDIA, Claude Max | modely a trénink |
| Honza | `honza` | starší notebook, Claude Max | aplikace a grafy |
| Tobias | `tobias` | MacBook M4 16 GB, Claude Pro (menší limit) | prezentace, pohled uživatele; jeho Mac je na demo |

Zaměření je jen výchozí. Role se během hackathonu míchají a na čem kdo dělá, se mění. Aktuální rozdělení je ve Stavu. Pevné je jen to, že Ondra vede a rozhoduje o finálním testu.

## Jak pracuješ

- Mluv česky, stručně a jasně. Každé rozhodnutí zdůvodni jednou větou, porota se bude ptát „proč zrovna tohle?“.
- Než začneš výrazně měnit soubor, na kterém podle Stavu nebo posledních commitů pracuje někdo jiný, upozorni na to, ať se domluví.
- Commituj malé a časté kroky, ať se práce snadno spojuje.
- Kód vždy spusť a ukaž výsledek, než řekneš, že funguje. Neověřené věci neposílej do `main`.
- Když se změní něco, co používají ostatní (struktura, názvy souborů, rozhraní), zapiš to do Stavu.
- Když něco v zadání nevíš, nehádej. Navrhni otázku pro mentora.
- Drž se harmonogramu níž. Po sobotní 11:00 už jen opravy, žádné nové funkce.

## Pravidla pro data a modely

- Data od pořadatelů leží v `data/raw/` a nikdy nejdou do Gitu.
- Rozdělení na train / val / test je jedno společné pro všechny. Testovací část nikdy nepoužívej k tréninku, ladění ani výběru modelu. Pustí se jednou, na finální model, a rozhoduje o tom Ondra.
- Všichni měří stejně: společným vyhodnocením na validační části. Každý pokus ulož jako nový soubor do `results/` (autor, čas, popis, metrika, parametry).
- Vždy srovnávej s jednoduchým základem (baseline). Číslo bez srovnání nic neříká.
- Seed je vždy 42, aby šly výsledky zopakovat.
- Podezřele dobrý výsledek nech zkontrolovat subagentem `kontrolor` (únik dat, špatné rozdělení).
- Velký model od nuly netrénuj, dolaďuj předtrénovaný. Nikdo nemá grafiku NVIDIA: GPU je zdarma na Kaggle (příkaz `kaggle`) nebo v Colabu, Macy mají MPS.
- Dokud není hotový model, aplikace jede s falešnou předpovědí se stejným rozhraním.
- Klíče (např. API) patří do `.env`, zapisuje je člověk ručně a nikdy nejdou do Gitu. Ke Kaggle se každý přihlašuje sám přes `kaggle auth login`.

## Git

- Pracuj na větvi svého člověka, nikdy přímo na `main`.
- Synchronizace je příkaz `/sync`: commit, sloučení `origin/main`, push vlastní větve. `/sync main` navíc pošle hotovou práci do `main`.
- `git add` jen na soubory, na kterých se pracovalo, nikdy naslepo `git add .`. Když `git status` ukazuje změny, o kterých nevíš, zeptej se.
- Commit česky, jedna věta: `Dan: LightGBM místo RF, val F1 0,81`.
- Do commitů nepřidávej `Co-Authored-By` ani zmínky o Claude.
- Nikdy `git push --force` ani `git reset --hard`.

## Harmonogram

| Čas | Co musí platit |
|---|---|
| pá 17:30 | téma vybrané, Stav vyplněný |
| 19:00 | data rozdělená, společné vyhodnocení hotové, první model, kostra aplikace |
| 21:00 | celý řetězec od dat po aplikaci funguje |
| 0:00 | plán na noc, chystá se dlouhý trénink |
| so 8:00 | výsledky z noci, výběr finálního přístupu |
| 11:00 | konec nových funkcí |
| 14:00 | odevzdání prezentace |

## Příkazy

- `/ondra`, `/dan`, `/honza`, `/tobias`: kdo je člověk, jeho počítač, účet a výchozí zaměření
- `/sync [main]`: synchronizace s Gitem
- `/temata <text zadání>`: rozbor témat a návrh nápadů (pátek 15:30)
- `/stav`: přehled týmu na kontrolní body
- `/denik`: zápis změn do `docs/DENIK.md`
- `/kontrola`: kontrola výsledků a úniku dat
- `/porota`: nácvik otázek poroty
- `/kaggle [co natrénovat]`: trénink na GPU na Kaggle (postup v `kaggle/README.md`)
- subagent `kontrolor`: nezávislá kontrola jednoho pokusu

## Celý plán týmu

@README.md

Podklady o minulých ročnících a vzorcích vítězů jsou v `docs/brainstorming-podklady.md`. Načti je, když se vybírá téma nebo chystá prezentace.
