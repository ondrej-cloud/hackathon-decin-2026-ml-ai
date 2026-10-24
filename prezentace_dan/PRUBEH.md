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
- 01:52 `PREHLED_POKUSU.md`: 34 řádků, všechny pokusy týmu i Dana (co, proč, výsledek v cm, rozhodnutí, zdroj). Čísla
  LightGBM jsou z přepočtu na opravené verzi dat (pá 20:15), ostatní z commitnutých zpráv.
- 01:55 `OTAZKY_POROTY.md`: 40 otázek v 11 tématech, odpovědi s čísly a zdrojem. U otázky 40 (kdo vyhlašuje stupně
  povodňové aktivity, vodní zákon) výslovně psáno, že to v repu podložené není a je to k ověření u mentora.
- Session nejistoty (`hackathon-2026-nejistota`) začala 01:43 a výsledky ještě nemá. Otázka 32 o nejistotě je zatím jen
  z Honzova `src/nejistota.py`, před ranní zprávou se podívám znovu.
- 02:02 Grafy G1–G4 hotové (subagent, `grafy_dan.py`, popis `grafy/README.md`). Zkontroloval jsem každý PNG a opravil tři
  věci: v G1 a G4 žargon v legendě („z G3“, „G3 (30 stanic)“ → „G3 = ½ regrese + ½ LightGBM“), v G4 legendu, která
  překrývala křivku, a v G1 legendu, která po prodloužení zakryla „Děčín · cíl“. Skript při každém běhu ověřuje čísla
  proti kontrolním hodnotám, nesedí nic.
- 02:08 Fact-check Codexem (`codex/prompt_fact_check.txt`, jen čtení, 351 s, výstup `codex/fact_check_codex.md`):
  704 čísel, 669 sedí, 31 nesedí, 4 tvrzení neověřitelná. Většina nesouladů je špatně označená metrika (D12/D24 proti
  průměru 6 kombinací, starší běhy) a příliš obecné věty. Všech 31 opraveno jedním skriptem (každá náhrada ověřená, že
  sedí právě jednou). Důležité: „12 z 24“ jsou varování, ne povodně; 44,6 cm je balíček napodobený na 2017–2018;
  fyzika zapojí jen 8 z 18 stanic; přísným LOFO prošla na D36 i regrese s 30 stanicemi; Boris (649 cm) není vrchol
  nad rámec tréninku (2013: 1 072 cm); rozliv bere nejvyšší dosaženou N-letou vodu, ne nejbližší.
- Nález pro tým (Codex): v aplikaci je výchozí model `ridge` učený do 2018 i v režimu Dnešek; model učený do 2025
  (`ridge_vse`) se musí zvolit v menu. Zapsáno do otázky 39 a do ranní zprávy.
- U otázky 26 (Danova odpověď) jsem upřesnil závorku: 98 hodnot = průtok 12 stanic 0–36 h a hladina Děčína a Ústí
  0–24 h, vždy 7 zpoždění. V main (`docs/POROZUMENI.md`) zůstává starší znění „z každé stanice 7 zpoždění 0–36 h“,
  main neměním, jen to hlásím.
- 02:19 Kontrola reprodukovatelnosti Codexem doběhla (27 min, sandbox jen v klonu, internet blokovaný). Ridge, „jako teď“,
  procenta, vícenásobná validace a test aplikace jdou z čistého klonu zopakovat a sedí s PREHLED na desetinu. Nové běhy
  LightGBM a fyziky nedoběhly v jeho limitech (6 a 2 min), nejspíš kvůli RAM s dalšími session, uložené výsledky sedí.
  Hlavní problém: otisk verze závisí na koncích řádků (Windows × Mac). Sepsáno do `REPRODUKOVATELNOST.md` s návrhy oprav,
  v main nic neměním.
- 02:24 K otázkám poroty přidaná tabulka „Kterým grafem odpovědět“ (Danovy G1–G4 a Ondrovy slajdy a záložní slajdy).
- 03:01 Druhé kolo fact-checku Codexem (29 min, `codex/fact_check2_codex.md`) přes pět souborů (i `REPRODUKOVATELNOST.md`
  a `grafy/README.md`): 1 064 čísel, 1 046 sedí, 13 nesedí, 5 neověřitelných. Všech 14 odkazovaných grafů existuje.
  Opraveno všech 13: hlavně označení metrik (síť 64-32 = starší rozbor D24 při velké vodě; 13,6 cm jsou celá validační
  okna, hlavní D24 je 15,5), přínos srážek na začátku vzestupu podle modelu 1,9–4,6 cm, v REPRODUKOVATELNOST závažnost
  podle kontroly „vysoká“ a příčina „domněnka“, TCN kontrolou neověřená. Legenda G1 „doba neměřena“ → „bez doby
  doběhu“, protože experimentální odhady pro nové stanice existují (u malých toků nespolehlivé).
