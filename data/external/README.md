# Data, která používáme

Všechno tady je v Gitu a dá se otevřít přímo na GitHubu. Soubory `.parquet` GitHub neumí zobrazit, proto je ke každému ukázka v CSV ve složce `nahled/`. Data od pořadatelů a surová data stažená z ČHMÚ jsou v `data/raw/` a do Gitu nejdou (pořadatelé to nechtějí a jsou velká, ČHMÚ asi 2 GB). Celý soupis zdrojů a proč co bereme je v `docs/ZDROJE_DAT.md`.

## Co jde do modelu

**`labe_hodinove.parquet`**: jediná tabulka, ze které se model učí. 175 320 řádků, jeden za každou hodinu 2006–2025 (čas `cas` v UTC), 14 sloupců. Postaví ji `python src/data.py` z hodinového archivu ČHMÚ. Ukázka: `nahled/labe_hodinove_boris_2024-09.csv` (povodeň Boris 10.–22. 9. 2024).

| Sloupec | Co to je | Stanice a řeka |
|---|---|---|
| `decin_H`, `usti_H` | hladina v cm (měřená čidlem na vodočtu) | Děčín a Ústí nad Labem, Labe; tohle předpovídáme |
| `decin_Q`, `usti_Q` | průtok v m³/s (dopočtený z hladiny měrnou křivkou ČHMÚ) | Děčín a Ústí |
| `louny_Q` | průtok | Louny, Ohře |
| `melnik_Q` | průtok | Mělník, Labe pod soutokem s Vltavou |
| `vranany_Q`, `praha_Q` | průtok | Vraňany a Praha-Chuchle, Vltava |
| `beroun_Q`, `sazava_Q` | průtok | Beroun (Berounka) a Nespeky (Sázava), přítoky Vltavy |
| `kostelec_Q`, `nymburk_Q`, `prelouc_Q` | průtok | Kostelec nad Labem, Nymburk a Přelouč, horní Labe |
| `jizera_Q` | průtok | Předměřice, Jizera |

Nic se nedoplňuje. Chybí jen 82 hodin hladiny v Děčíně 5.–8. 2. 2006, kterou jsme vyřadili jako chybu měření (nejspíš led).

**Vstupy modelu** se neukládají, z téhle tabulky je pokaždé postaví `src/features.py`. Pro každou hodinu (okamžik předpovědi) vezme hladinu Děčína a Ústí teď a před 1, 2, 3, 6, 12 a 24 h a průtok všech 12 stanic teď a před 3, 6, 12, 18, 24 a 36 h, celkem 98 sloupců. Název `praha_Q_18` znamená průtok v Praze před 18 h. Cíl `y` je hladina za 12, 24 nebo 36 h. Ukázka přesně toho, co model dostane, je `nahled/vstupy_decin_24h_boris.csv` (Děčín +24 h, Boris, každých 6 h).

**`stanice_hydro.csv`**: 12 stanic. Klíč jako v kódu, číslo ČHMÚ, název, řeka, souřadnice a hranice 1.–3. stupně povodňové aktivity v cm (z metadat balíčku). Aplikace z něj bere polohy na mapu. Prahy pro vyhodnocení varování má kód přímo v `src/data.py` (`SPA`).

## Jen pro aplikaci (Honza)

- `n_lete_vody.csv`: průtoky a hladiny 1- až 100leté vody v Děčíně a Ústí z ČHMÚ, včetně odkazu na oficiální měrnou křivku. Aplikace podle nich kreslí rozliv.
- `zaplavova_uzemi.geojson`: oficiální záplavová území (DIBAVOD) pro mapu.
- `reky.geojson`: úseky řek mezi stanicemi s délkou a dobou putování vody pro mapu a animaci.

## Vyzkoušeno, v modelu není

- `labe_meteo.parquet`: srážky, výška sněhu, index předchozích srážek (API30) a teplota, průměr po větvích povodí (Vltava, horní Labe, Ohře) z 25 meteostanic, denní data rozepsaná do hodin. Každá hodnota je v tabulce až od chvíle, kdy byla známá. Postaví `python src/meteo.py`. Na validaci nepomohly (`docs/POKUSY.md`). Ukázka `nahled/labe_meteo_2024-09.csv` (září 2024, jeden řádek za den).
- `labe_meteo_o_den_driv.parquet`: totéž o den dřív, jako by byla předpověď počasí dokonalá. Jen na myšlenkový pokus, kolik by srážky mohly pomoct nejvýš. Do modelu se nesmí, je to únik z budoucnosti.
- `chmu_meteo_meta1-20261023.json`: polohy a výšky meteostanic ČHMÚ, podle nich jsme vybrali 25 stanic v povodí.

## Z úlohy Ovzduší, kterou jsme nakonec nevybrali

- `stanice_ovzdusi.csv`, `parovani_ovzdusi_meteo.csv`
