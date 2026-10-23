# Nálezy Codexu a co s nimi

Codex CLI (`codex exec -s read-only`, pravidla v promptu: nic neměnit, nečíst .env ani údaje Kaggle, výstup =
nálezy se souborem, řádkem a závažností). Prompty a plné odpovědi jsou v `codex/`.

## (a) po sestavení dat, pá 21:03–21:06 (`codex/kontrola_a_data.md`)
Celkově: přímý únik budoucích měření nenašel, posun denních srážek potvrdil jako správný.

| Nález | Závažnost | Co jsem udělal |
|---|---|---|
| `priznaky.py`: `nejstarsi` nezahrnuje stáří denních dat (srážkový součet až 47 h + posuny, sníh 48 h), takže řádek na začátku validace může obsahovat srážky z tréninkového období | střední | Opraveno: u srážek se přičítá 24·(k−1) + 23 + 25 h, u sněhu 72 + 23 + 25 h. Není to únik z budoucnosti (data jsou starší než t), ale porušovalo to pravidlo „řádky přes hranici splitu vyhodit“. Pokusy se srážkami a sněhem jsem pustil znovu. |
| `priznaky.py`: `vyplnit_h` (ffill) prodlužuje historii vstupu, ale `nejstarsi` se nezvětší | střední | Opraveno: `nejstarsi += vyplnit_h`. Volba zatím nebyla použitá. |
