Našel jsem 3 problémy. **Ve vyhlazování jsem únik budoucích hodnot nenašel.**

- **[závažnost: vysoká] [nejistota_dan/kmitani.py:70](/C:/Users/danie/Documents/hackathon-2026-nejistota/nejistota_dan/kmitani.py:70)** – Varování se hodnotí na neúplné řadě povodňových oken. `evaluate.varovani()` vyžaduje 96 předchozích hodin pod prahem; chybějící kontext vyřadí skutečné události z hodnocení. Ověřeno pro Ústí +24 h, 3. SPA: zachytí jen **1 ze 3** začátků; události 2006 a 2013 vypadnou. **Oprava:** začátky určit z úplné skutečnosti 2006–2020, předpovědi hodnotit po foldech s dostatečným okolím; chybějící skutečnost nesmí znamenat nepřekročení prahu.

- **[závažnost: střední] [nejistota_dan/kmitani.py:123](/C:/Users/danie/Documents/hackathon-2026-nejistota/nejistota_dan/kmitani.py:123)** – Provozní varianty používají různé hodiny. `rolling(..., min_periods=1)` zpřístupní i některé původně chybějící průtoky, takže maska `ok` závisí na variantě. U Děčína +24 h má týmová varianta **583** hodnocených řádků, b/c **618**; mění se i SD skutečnosti. Rozdíl metrik proto zahrnuje změnu vzorku. **Oprava:** předpovědi spočítat s vlastní historií, potom MAE hodnotit na společném průniku časů a SD na společných sousedních hodinových dvojicích.

- **[závažnost: střední] [src/models/ridge_kmit_vystup.py:16](/C:/Users/danie/Documents/hackathon-2026-nejistota/src/models/ridge_kmit_vystup.py:16)** – Varianty a/c vyhlazují pouze uvnitř aktuálního volání predikce. Při hodinovém volání s jediným řádkem se nevyhladí nic; výsledek závisí na rozdělení do dávek. Ověřeno: surové `[0, 3, 9]` dávají společně `[0, 1.5, 4]`, samostatně `[0, 3, 9]`. **Oprava:** předávat také poslední dvě hodiny historie stejného modelu a až potom oříznout požadované výsledky, případně historii uchovávat.

Ostatní kontrolované body:

- `sort_index().rolling("3h").mean().reindex(index)` je kauzální; na hodinovém indexu bere t, t−1, t−2. Při dírách průměruje dostupné hodnoty v tomto intervalu.
- Ověřený index 2006–2020 je seřazený, unikátní a bez hodinových děr. Vstupní `rolling(6)` následovaný nezáporným `shift(z)` používá pouze minulost, bez centrování.
- LOFO `ext` používá tentýž model foldu a starší řádky; provozní rolling, kladné posuny a `ffill` jsou také kauzální. Záporný posun slouží cíli.
- Modelové varianty zachovávají týmový Ridge včetně škálování a α. Výpočet SD sousedních hodin i podepsaného posunu prvních maxim je správný; posun obou časů o horizont se odečte.

Nic jsem nezměnil ani nezapsal; dlouhé skripty jsem nespouštěl a test 2021–2025 nepoužil.