Kritický ani vysoký nález jsem nezjistil.

- **Střední — [lofo.py:240](C:/Users/danie/Documents/hackathon-2026-ridge/ridge_dan/zlepseni/lofo.py:240):** znaménkový test předpokládá nezávislé povodně, ale některá hodnoticí okna sdílejí hodiny; například foldy 16 a 17 sdílejí 48 hodin ([lofo_foldy.csv:62](C:/Users/danie/Documents/hackathon-2026-ridge/ridge_dan/stanice_vsem/lofo_foldy.csv:62)). Hodnotu **p = 0,0169** proto nelze interpretovat jako přesný test 22 nezávislých událostí. **Oprava:** pro statistický test seskupit překrývající se události; Ondrovu validaci neměnit.

- **Nízká — [vysledky_E.json:43](C:/Users/danie/Documents/hackathon-2026-ridge/ridge_dan/zlepseni/vysledky_E.json:43):** základní model má `znamenkovy_p: NaN`, což není standardní JSON a přísný čteč soubor odmítne. **Oprava:** při nulovém počtu nenulových rozdílů ukládat `null`. Průměrné chyby tím nejsou zpochybněny.

Kontrola **2006–2020** potvrdila správná ID stanic, jednotky, UTC, hodinovou návaznost roků a shodu 450 zdrojových souborů s tabulkou. Ledová oprava odpovídá týmové tabulce. Nové stanice nevyřazují žádné další řádky; zpoždění jsou shodná a pouze do minulosti. Všech 22 foldů pro 36 h odpovídá CSV a mezery oddělují i časy použité v příznacích a cílech.

Uložená čísla souhlasí s `ROZHODNUTI_G3.md`:

| Hodnocení 36 h | Ridge → Ridge 30 |
|---|---|
| Ondra, Děčín | 29,76 → 29,05 cm; −0,71, lepší 5/8 |
| Ondra, Ústí | 31,14 → 30,14 cm; −1,00, lepší 5/8 |
| LOFO, Děčín, oba JSON | 26,39 → 23,96 cm; −2,43, lepší 17/22 |
| Pevná validace, Děčín / Ústí | 26,0 → 26,6 / 26,7 → 26,6 cm |

Kontrolní přepočet fitů nebyl dokončen; uvedené metriky jsou z uložených výsledků. Nic jsem nezměnil, internet ani výpočty na letech 2021–2025 jsem nepoužil.

**Výsledek Ridge 30 na 36 h je věrohodný jako retrospektivní CV výsledek, ale jeho soustavná převaha alespoň o 1 cm doložená není.**