# Hackathon ML/AI 2026 – kontext pro Claude

Pracuješ v týmu čtyř středoškoláků na Hackathonu ML/AI 2026 (FJFI ČVUT Děčín). Soutěž startuje v pátek 23. 10. v 16:00, práce končí v sobotu 24. 10. ve 14:00 a od 14:30 prezentujeme porotě (max. 15 minut). Chceme vyhrát. Pořadatelé používání jazykových modelů povolili.

Na začátku relace člověk zadá `/ondra`, `/dan`, `/honza` nebo `/tobias`. Z toho poznáš, s kým pracuješ a jakou má roli. Když to neudělá, zeptej se ho, kdo je.

## Stav (doplňuje Tobias hned po výběru tématu)

- **Zadání:** zatím neznámé, témata se představí v pátek v 15:30
- **Komu řešení pomáhá:**
- **Data:** (kde leží v `data/raw/`, co obsahují, velikost)
- **Metrika:** (jedna hlavní metrika a s jakým jednoduchým řešením se srovnáváme)
- **predict.py:** (co bere a co vrací, domluví Dan s Honzou)
- **Smějí data do cloudu (Kaggle, Colab, jazykové modely)?** zeptat se pořadatelů

## Tým a vlastníci souborů

| Kdo | Větev | Role | Vlastní soubory |
|---|---|---|---|
| Ondra | `ondra` | kapitán, ověřování, data | `data/split/`, `src/evaluate.py`, `src/features.py`, `.claude/` |
| Dan | `dan` | model a trénink | `src/train_*.py`, `src/predict.py`, `models/` |
| Honza | `honza` | aplikace a grafy | `app/` |
| Tobias | `tobias` | prezentace, deník, sekce Stav | `CLAUDE.md`, `docs/` |

Do `results/` píšou všichni, každý pokus jako nový soubor.

## Jak pracuješ

- Mluv česky, stručně a jasně. Každé rozhodnutí zdůvodni jednou větou, porota se bude ptát „proč zrovna tohle?“.
- Měň jen soubory svého člověka. Cizí soubory jen čti. Když je potřeba změna jinde, napiš, komu to říct.
- Kód vždy spusť a ukaž výsledek, než řekneš, že funguje. Neověřené věci neposílej do `main`.
- Když něco v zadání nevíš, nehádej. Navrhni otázku pro mentora.
- Drž se harmonogramu níž. Po sobotní 11:00 už jen opravy, žádné nové funkce.

## Pravidla pro data a modely

- Data od pořadatelů leží v `data/raw/` a nikdy nejdou do Gitu.
- Rozdělení na train / val / test dělá jen Ondra (`data/split/`). Testovací část nikdy nepoužívej k tréninku, ladění ani výběru modelu. Pouští ji jen Ondra, jednou, na finální model.
- Každý pokus vyhodnoť přes `src/evaluate.py` na validační části a ulož přes `save_result` jako nový soubor `results/<jmeno>-<HHMM>-<popis>.json`.
- Vždy srovnávej s jednoduchým základem (baseline). Číslo bez srovnání nic neříká.
- Seed je vždy 42, aby šly výsledky zopakovat.
- Podezřele dobrý výsledek nech zkontrolovat subagentem `kontrolor` (únik dat, špatné rozdělení).
- Velký model od nuly netrénuj, dolaďuj předtrénovaný. Nikdo nemá grafiku NVIDIA: GPU je zdarma na Kaggle (příkaz `kaggle`) nebo v Colabu, Macy mají MPS.
- Klíče (API, Kaggle) patří do `.env` nebo `kaggle.json`. Zapisuje je člověk ručně a nikdy nejdou do Gitu.

## Dohody v kódu

- `src/evaluate.py` (Ondra): `load_split()` vrací trénovací a validační část (testovací nikdy), `score(y_true, y_pred)` vrací slovník metrik s hlavní metrikou pod klíčem `metrika`, `save_result(autor, popis, metriky, info)` uloží výsledek do `results/`.
- `src/predict.py` (Dan): `predict(vstup)` vrací výstup pro aplikaci. Přesný tvar je v sekci Stav.
- Než bude `predict.py` hotové, aplikace používá `app/fake_predict.py` se stejnou funkcí.
- U úlohy s chatbotem nahradí metriku sada testovacích otázek se správnými odpověďmi, kterou připraví Ondra.

## Git

- Pracuj na větvi svého člověka, nikdy přímo na `main`.
- Synchronizace je příkaz `/sync`: commit vlastních souborů, sloučení `origin/main`, push vlastní větve. `/sync main` navíc pošle hotovou práci do `main`.
- `git add` jen na konkrétní soubory, nikdy naslepo `git add .`.
- Commit česky, jedna věta: `Dan: LightGBM místo RF, val F1 0,81`.
- Do commitů nepřidávej `Co-Authored-By` ani zmínky o Claude.
- Nikdy `git push --force` ani `git reset --hard`.

## Harmonogram

| Čas | Co musí platit |
|---|---|
| pá 17:30 | téma vybrané, sekce Stav vyplněná |
| 19:00 | data rozdělená, `evaluate.py` hotové, první model, kostra aplikace |
| 21:00 | celý řetězec od dat po aplikaci funguje |
| 0:00 | plán na noc, Dan chystá dlouhý trénink |
| so 8:00 | výsledky z noci, výběr finálního přístupu |
| 11:00 | konec nových funkcí |
| 14:00 | odevzdání prezentace |

## Příkazy

- `/ondra`, `/dan`, `/honza`, `/tobias`: role a úkoly daného člověka
- `/sync [main]`: synchronizace s Gitem
- `/temata <text zadání>`: rozbor témat a návrh nápadů (pátek 15:30)
- `/stav`: přehled týmu na kontrolní body
- `/denik`: zápis změn do `docs/DENIK.md` (Tobias)
- `/kontrola`: kontrola výsledků a úniku dat (Ondra)
- `/porota`: nácvik otázek poroty
- subagent `kontrolor`: nezávislá kontrola jednoho pokusu

## Celý plán týmu

@README.md

Podklady o minulých ročnících a vzorcích vítězů jsou v `docs/brainstorming-podklady.md`. Načti je, když se vybírá téma nebo chystá prezentace.
