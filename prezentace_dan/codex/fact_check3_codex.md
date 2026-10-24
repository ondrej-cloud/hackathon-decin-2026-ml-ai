**1. NESOULADY**

Zkratky: **DAN** = `prezentace_dan/DAN_VYSTUP.md`, **TÝM** = `prezentace_dan/TYM_RANO.md`, **OTÁZKY** = `prezentace_dan/OTAZKY_POROTY.md`, **PŘEHLED** = `prezentace_dan/PREHLED_POKUSU.md`. Gitové zdroje níže jsou z požadovaných větví `origin/dan-*`.

| Soubor:řádek | Tvrzení | Co říká zdroj s citací čísla | Zdroj | Návrh opravy |
|---|---|---|---|---|
| DAN:3–5 | Vstup dlouhý 60–90 s se vejde místo slajdu 5. | Slajd 5 má **40 s**, celý rozpis přesně **7 minut**. | `docs/PREZENTACE_7MIN.md:13–18` | Uvést nutnost ušetřit dalších **20–50 s** jinde. |
| DAN:12–13, 38–40 | Strom předpovídá pouze hodnoty, které viděl; příklad 823 cm. | Finální LightGBM předpovídá **změnu hladiny**. Výsledek **823 místo 1 072 cm** pochází z průzkumu před společným rozdělením. | `docs/PREHLED.md:32`; `docs/POKUSY.md:59–65` | „Stromy špatně extrapolují.“ Příklad 823 cm označit jako původní průzkum. |
| DAN:18, 42–44; TÝM:14 | Přidání 18 stanic zlepšilo všechny čtyři modely. | Fyzikální model využívá pouze **8 nových stanic**. Zlepšení **4,8–8,2 cm** platí pro **D24 na validaci**. | `ridge_dan/STANICE_VSEM.md`, tabulka; `prezentace_dan/grafy/README.md:87–115` | Doplnit „Děčín +24 h, validace; fyzika pouze +8 stanic“. |
| DAN:30–31, 47–48; TÝM:9–10 | LOFO 13,9/15,3 cm či 20 z 22 bez uvedení cíle a horizontu. | **13,94/15,29 cm a 20 z 22** je **D24**; **19,6/20,1 cm** je vícenásobná validace přes **6 kombinací**. | `ridge_dan/ZLEPSENI.md`, verdikt; `VALIDACE_ONDRA.md`, úvod | Přímo u LOFO doplnit **Děčín +24 h**. |
| DAN:21–22, 44–45, 57 | Srážky nepomohly, nejvýš o 1 cm; voda už je v řekách. | Šestihodinové srážky zlepšily validační průměr LightGBM o **1,18 cm**, ale přidaly **4 plané poplachy**. Dokonalá předpověď zlepšila Ústí +36 h **26,7 → 24,8 cm**. | `srazky_dan/ZPRAVA_SRAZKY.md`, výsledky; `docs/POKUSY.md:361–362` | „Nepřinesly dostatečně spolehlivé zlepšení pro nasazení.“ Maximum 1 cm vztáhnout jen k určenému průměru regrese. |
| TÝM:14 | Nové stanice celkovou chybu nezlepšují. | Na validaci přes 6 kombinací: fyzika **24,75 → 23,40 cm**, LightGBM **23,07 → 22,08 cm**, Ridge naopak **17,08 → 18,48 cm**. | `ridge_dan/STANICE_VSEM.md:53–58` | „Celkový výsledek je podle modelu smíšený.“ |
| DAN:59 | Nové stanice zhorší povodeň 2006. | U Ridge chyba **16,0 → 24,7 cm**; u fyziky **26,4 → 25,8**, u LightGBM **29,4 → 29,4 cm**. | `ridge_dan/STANICE_VSEM.md:53–58` | Zúžit na „u regrese“, případně také u sítě. |
| TÝM:15–16 | Formulace spojuje pásmo aplikace s hodnoceným 80% pásmem. | Aplikace původně ukazuje **90% pásmo**; pokrytí **58–72 %** patří k **80% variantě stejné metody**. | `nejistota_dan/ZPRAVA_NEJISTOTA.md:10–12` | Výslovně rozlišit aplikované **90%** a kontrolované **80%** pásmo. |
| TÝM:16; OTÁZKY:205, 373–374; PŘEHLED:46 | Nové 80% pásmo pokrývá 79–80 %. | Shrnutí zdroje to uvádí, ale podrobná tabulka obsahuje **78 % pro Ridge 30, Děčín +36 h**. | `nejistota_dan/ZPRAVA_NEJISTOTA.md:69` | Pro všechny kombinace uvést **78–80 %**, nebo jasně vymezit agregaci. Rozpor je už ve zdroji. |
| OTÁZKY:273, N2 | Po roce 2016 žádná povodeň nebyla. | Bez povodní bylo období **2016–2020**. Test obsahuje povodně **2021, 2023 a 2024**. | `docs/DATA.md:71`; `docs/PREHLED.md:51` | „V letech 2016–2020 nebyla…“ |
| OTÁZKY:319, N9 | ±7,7 cm je rozptyl mezi povodněmi. | **7,7 cm je směrodatná odchylka**, nikoli rozptyl. | `ridge_dan/VALIDACE_ONDRA.md:34`; `docs/POKUSY.md:399` | Nahradit slovem „směrodatná odchylka“. |

**2. Neověřitelná tvrzení**

- **TÝM:19:** úplná reprodukce hlavních čísel z čistého klonu není v zadaných zdrojích doložena. Rozdíl otisků kvůli CRLF/LF doložen je (`docs/DENIK.md:166–167`).
- **TÝM:38:** „patch 03: Dnešek nezamrzne“ je silnější než doložené ověření. Zpráva potvrzuje úpravu timeoutů a test **10/10**, nikoli bezproblémový provoz za všech síťových podmínek.
- **OTÁZKY:138:** tvrzení, že testový rozdíl **1,1 cm je náhoda**, nemá doložený statistický rozbor; kolísání seedů na validaci jej samo neprokazuje.
- **PŘEHLED:37:** kategorické „nepřeučuje“ nelze prokázat pouze porovnáním **19,7/15,5 cm**. Přesnější je formulace z otázky 17: „obvyklý znak přeučení nemá“.
- **PŘEHLED:55:** „strop dělají informace, ne model“ je interpretace výsledků, nikoli prokázaný obecný závěr. Doporučuji „výsledky naznačují…“.

**3. Počty**

Počítáno po obsahových blocích: odrážka, odpověď či řádek tabulky; všechny údaje uvnitř byly kontrolovány. Opakování jsou započtena zvlášť, nesoulad má přednost před neověřitelností. U PŘEHLEDU jsou zahrnuty fyzické řádky 35–38 **i položky č. 35–38**.

| Zkontrolováno | Sedí | Nesedí | Neověřitelné |
|---:|---:|---:|---:|
| **74** | **51** | **18** | **5** |

Hlavní výsledky G3, H30, testu a Borise sedí; opravy potřebují hlavně rozsah tvrzení, označení metrik a statistická terminologie.