Prověřil jsem všech pět souborů i všechny nálezy prvního kola. **P = nedotažená původní oprava, N = nový nález.** Nic jsem nezměnil.

**1. NESOULADY**

Cesty v prvním sloupci jsou relativní k `prezentace_dan/`.

| Soubor:řádek | Tvrzení v podkladu | Co říká zdroj – přesné číslo / citace | Zdroj (soubor, sekce) | Návrh opravy |
|---|---|---|---|---|
| **P** PREHLED_POKUSU.md:16; OTAZKY_POROTY.md:118; TAHAK_DAN.md:41 | MLP: D24 trénink **5**, validace **22 cm**, prezentované jako chyba v povodňových oknech | Starý rozbor říká „**při velké vodě**“. Uložený běh má D24 `mae_povodne: 21.2`, `mae_nad_1spa: 23.5`. Samotné doplnění D24 rozdíl metrik neřeší. | `docs/POKUSY.md`, pá 20:00, MLP; `results/2026-10-23_195410_mlp_v1.json`, D24 | Označit **historický rozbor při vysoké vodě**, případně dvojici vypustit. |
| **P** OTAZKY_POROTY.md:74–75 | „Nalezené chyby jsou opravené a přepočítané“ | „**Přepočet B, D a G2 do 00:30 nedoběhl … v tabulce jsou čísla před opravou.**“ Následující výhrada v odpovědi neodstraňuje rozpor první věty. | `origin/dan-ridge:ridge_dan/ZLEPSENI.md`, Kontrola Codexu | „Kód byl opraven; přepočet B, D a G2 nedoběhl.“ |
| **P** OTAZKY_POROTY.md:191 | Všechny používané šestihodinové srážky jsou známé **1–6 h po měření** | Základní dostupnost je **E + 1 h**, ale díl končící v **00/12 UTC**, dorovnávaný z pozdějšího úhrnu, vstupuje až **07/19 UTC**. Rozmezí neplatí bez výjimky. | `origin/dan-srazky:srazky_dan/ZPRAVA_SRAZKY.md`, Data – Časování | Uvést „hodinu po konci období; dodatečně dorovnávané díly později“. |
| **P** OTAZKY_POROTY.md:211 | Děčín +36 h: **26,0 cm**, do ±20 cm **51 %** | **26,0 cm** je Děčín +36 h. **51 %** je souhrnný podíl přes **oba cíle** na 36 h, při vodě nad 1. SPA. | `results/2026-10-23_195917_ridge.json`, D36; `docs/POKUSY.md`, pá 20:15 | Rozdělit: „Děčín: 26,0 cm; přes oba cíle je 51 % předpovědí do ±20 cm.“ |
| **P** TAHAK_DAN.md:55 | „Jediné, co spolehlivě pomáhá, jsou stanice…“ | Srážky zlepšily začátek vzestupu sítě o **2,90 cm**, „**u všech seedů**“. | `origin/dan-sit:sit_dan/SIT_VARIANTY.md`, §3 | Vypustit „jediné“; doplnit menší přínos srážek. |
| **N** PREHLED_POKUSU.md:52 | Srážky pomáhají začátku vzestupu o **2–3 cm** obecně | Na validaci D24: týmový Ridge **−1,9 cm**, LightGBM **−4,6 cm**, síť **−2,90 cm**. | `ZPRAVA_SRAZKY.md`, Výsledky; `SIT_VARIANTY.md`, §3, příslušné větve | „Podle modelu přibližně o 1,9–4,6 cm na validaci D24.“ |
| **N** OTAZKY_POROTY.md:205–206 | „Chyba **14 cm**“ bez odlišení od úvodní definice metriky | **13,6 cm**, zaokrouhleně 14, pochází z **celých validačních oken**. Hlavní D24 `mae_povodne` je **15,5 cm**. Zdroj rozdíl výslovně vysvětluje. | `docs/POROZUMENI.md`, Jak číst výsledky; uvedený JSON Ridge, D24 | Doplnit, že jde o jiná okna, nebo použít hlavní D24 chybu přibližně **16 cm**. |
| **N** REPRODUKOVATELNOST.md:15 | Samotné načtení dat `nacti()` trvalo **24 s** | **23,6 s** je čas celého `import_check.py`: importy, načtení dat a kontroly uložených předpovědí. | `codex/reprodukovatelnost_codex.md`, Provedené kroky; doprovodný log, `import_check.py` | Přejmenovat řádek na „kontrola importů, dat a uložených předpovědí“. |
| **N** REPRODUKOVATELNOST.md:32 | Nedokončené běhy mají závažnost **střední** | Původní kontrola je označuje **„Vysoká“**, s větou „**Příčina nebyla určena**“. | `codex/reprodukovatelnost_codex.md`, Problémy, řádek 36 | Zachovat původní závažnost, případně změnu označit jako vlastní následné hodnocení. |
| **N** REPRODUKOVATELNOST.md:43 | „Uložené výsledky [MLP, TCN] sedí (`procenta.py`)“ | Spuštěno bylo `procenta.py ridge mlp lgbm fyzika jako_ted`. **TCN v kontrole nebyla.** | `codex/reprodukovatelnost_codex.md`, Provedené kroky | Omezit potvrzení na MLP; u TCN napsat „touto kontrolou neověřeno“. |
| **N** grafy/README.md:34 | Skript při každém běhu kontroluje shodu souřadnic do **0,001°** | Skutečný nynější rozdíl je přibližně **0,0008635°**, ale kód připouští **0,01°**: `max() > 0.01`. | `grafy_dan.py`, `nove_stanice()`; CSV a uvedená metadata ČHMÚ | Oddělit současnou naměřenou shodu od volnějšího limitu skriptu. |
| **N** grafy/README.md:45 | Doba doběhu **18 nových stanic se neměřila** | Pro nové stanice se doby odhadovaly uvnitř `fit`; zpráva uvádí například Bílina–Děčín **37 h** u LightGBM a **33 h** u fyziky, Litavka **42 h**, s výhradou spolehlivosti. | `origin/dan-ridge:ridge_dan/STANICE_VSEM.md`, Jak se srovnávalo; Poznámky | „G1 doby nových stanic nezobrazuje; experimentální odhady existují, některé jsou nespolehlivé.“ |

**2. Tvrzení, která nejde ze zdrojů ověřit**

- **OTAZKY_POROTY.md:246–248:** právní kompetence a odpovědnost podle zákona **254/2001 Sb.**; podklad chybí, jak text sám přiznává.
- **OTAZKY_POROTY.md:248–249:** úplnost shrnutí licenčních povinností. Uvedení licence CC BY 4.0 je doložené, úplný výklad jejích podmínek v podkladech není.
- **REPRODUKOVATELNOST.md:5:** celkových **27 minut** není v auditní zprávě doloženo měřením celkové délky.
- **REPRODUKOVATELNOST.md:9,32:** dvě další session, volná RAM **1–2 GB** a její pravděpodobná příčinná souvislost s nedokončenými běhy nejsou pro tento audit doloženy. Kontrola příčinu neurčila.

Všech **14 odkazovaných PNG** v tabulce „Kterým grafem odpovědět“ existuje.

**3. Počty**

Počítám výskyty obsahových čísel, opakování a meze intervalů zvlášť; vynechávám číslování, odkazy, cesty a identifikátory. Nesprávně přiřazenou metriku počítám jako nesoulad.

| Soubor | Zkontrolováno | Sedí | Nesedí | Neověřitelné |
|---|---:|---:|---:|---:|
| PREHLED_POKUSU.md | 224 | 220 | 4 | 0 |
| OTAZKY_POROTY.md | 353 | 346 | 5 | 2 |
| TAHAK_DAN.md | 159 | 157 | 2 | 0 |
| REPRODUKOVATELNOST.md | 58 | 54 | 1 | 3 |
| grafy/README.md | 270 | 269 | 1 | 0 |
| **Celkem** | **1 064** | **1 046** | **13** | **5** |

Hlavní výsledky a čísla grafů sedí; zbývají především nedotažená označení metrik a nepodložená zobecnění.