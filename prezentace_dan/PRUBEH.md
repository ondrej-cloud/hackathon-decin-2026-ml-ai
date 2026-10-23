# Průběh: podklady pro prezentaci a porotu

Dan (spí, noční úkol), větev `dan-prezentace` z `origin/main` 59956c9, worktree `hackathon-2026-prezentace`, vše v
`prezentace_dan/`. Prezentaci dělá Tobias (a Ondra slajdy), tady jsou jen podklady, jejich soubory se nemění.
Čas a jedna dvě věty, co a proč.

- 01:44 Worktree `hackathon-2026-prezentace` s větví `dan-prezentace`, upstream přenastavený na `origin/dan-prezentace`
  (jinak by holé `git push` šlo do main). Ostatní worktree (ridge, sit, srazky, nejistota) jen čtu.
- 01:45 Přečteno: `docs/PREHLED.md`, `POROZUMENI.md`, `CESTA_MODELU.md`, `PREZENTACE_7MIN.md`, nadpisy a vybrané
  záznamy `POKUSY.md`, část `DATA.md` a `DENIK.md`; Danovy zprávy `ridge_dan/ZPRAVA.md`, `STANICE_VSEM.md`,
  `ZLEPSENI.md`, `VALIDACE_ONDRA.md`, `smesi/pokus_G.md` (origin/dan-ridge), `srazky_dan/ZPRAVA_SRAZKY.md`
  (origin/dan-srazky), `sit_dan/SIT_VARIANTY.md` (origin/dan-sit). Čísla beru z commitnutých verzí na origin.
- Rozhodnutí: podklady míří hlavně na Danovy slajdy 5 („Žádná z 11 dalších cest nebyla lepší“) a 10 (limity) podle
  `docs/PREZENTACE_7MIN.md`, a na otázky po prezentaci.
- Rozhodnutí: grafy ve stylu týmových slajdů (`src/grafy_prezentace.py`: 16:9, 12 × 6,75 palce, 150 dpi, nadpis
  24 b. vlevo nahoře, týmové barvy), aby šly vložit vedle Ondrových. Kreslí je subagent podle přesného zadání (zdroje,
  kontrolní čísla), skript `prezentace_dan/grafy_dan.py`, nic se netrénuje.
- 01:49 Čistý klon `origin/main` (764984a) do dočasné složky mimo repo (scratchpad). Codex v něm (sandbox
  `workspace-write` jen v klonu, prompt `codex/prompt_reprodukovatelnost.txt`) podle README spouští, co jde bez velkého
  stahování, bez instalace a bez testu. Výsledek do `REPRODUKOVATELNOST.md`.
