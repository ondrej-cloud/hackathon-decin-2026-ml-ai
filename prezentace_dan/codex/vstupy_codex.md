Čísla i výpočet jsou v pořádku; výhrady se týkají interpretace. Kontrola proběhla bez zápisu souborů a bez vyhodnocení testu 2021–2025. V tabulce zkracuji `VSTUPY_DULEZITOST.md` na **MD**.

| Soubor:řádek | Tvrzení | Co říká zdroj / přepočet | Oprava |
|---|---|---|---|
| MD:31–37 | 98 vstupů, stanice, zpoždění, transformace, cíl | Souhlasí: 14 hladinových + 84 průtokových sloupců; seznam stanic i zpoždění odpovídá `features.py:12–23`. Odmocnina jen průtoků, StandardScaler, Ridge α=1, cíl budoucí hladina (`ridge.py:10–30`). | Bez opravy. |
| `vstupy_dulezitost.py:43–91` | Metrika, vyřazování, train | Metrika je shodná s `evaluate.vyhodnot` před zaokrouhlením: sjednocená okna −7/+5 dní, práh **≥490 cm**, jen validační řádky. Vyřazení odstraní všechny příslušné sloupce; model i scaler se učí jen na train. | Bez opravy. |
| `vstupy_dulezitost.py:63–73` | Skupinová permutace | Jedna permutace řádků společná všem sloupcům stanice, pouze ve validaci; 5 seedů 42–46. Plný model se při permutaci nepřeučuje. | Bez opravy. |
| MD:39,61,65–111,131,134–135 | Čísla a zdrojová opora | **Všech 84 výsledkových buněk** souhlasí s CSV na 0,1 cm; odpovídají i číselná opakování v textu, počty sloupců, základy a SD. Čtyři uvedené povodně potvrzeny. Doběhy odpovídají `DATA.md:85` a `grafy_dan.py:91`; Praha +49 odpovídá dokumentaci Z6 i koeficientu +49,341 cm/SD. | Bez číselné opravy. |
| MD:47–48,151 | „Srážky nepomohly“, 17,1 → 17,4; LOFO do 0,1 | Čísla mají oporu v `PREHLED_POKUSU.md:23,42`. **17,1 → 17,4 je průměr přes oba cíle a tři horizonty**, nikoli samotný Děčín +24 h; LOFO do 0,1 platí pro oba Ridge. | Uvést rozsah metriky a omezit závěr na vyzkoušené varianty Ridge a celkovou chybu. |
| MD:115,143,152 | Nejdůležitější je „hladina Děčína teď“ | Vyřazuje se všech **14 sloupců Děčína**, tedy hladina i průtok se všemi zpožděními. Samotný aktuální stav tento pokus neizoluje. | „Z jednotlivých stanic nejvíc chybí vlastní měření Děčína.“ |
| MD:119–120 | Přelouč a Sázava s horizontem rostou | Přelouč: **0,4 → 1,4 → 1,3**; Sázava: **0,1 → 0,0 → 0,6**. Růst není monotónní. | „Na 36 h mají větší přínos než na 12 h.“ |
| MD:118–119 | Na 12 h větve nepomáhají, protože voda ještě nedoteče | Vyřazení obou větví zlepší chybu asi o 0,5 cm; příčinu neprokazuje. Kostelec a Nymburk mají odhad doběhu **10 h**, navíc model používá i starší průtoky. | Ponechat pozorovaný výsledek, vypustit kategorické vysvětlení doběhem. |
| MD:122–123,126,131–132,158–159 | Prahu konkrétně zastoupí Vraňany | Korelace a skupinové vyřazení podporují možnost zastupitelnosti; neurčují, který vstup převzal informaci. | „Výsledek je slučitelný se zastupitelností korelovanými vstupy.“ |
| MD:123–124,160–161; `vstupy_dulezitost.py:235` | Rozdíly pod 1 cm jsou šum / neprůkazné | `PREHLED_POKUSU.md:6` stanovuje týmovou praktickou hranici. Statistickou neprůkaznost ani šum tím nelze doložit. | „Pod 1 cm nepovažujeme rozdíl za prakticky přesvědčivý; nejistotu jsme nevyčíslili.“ |
| MD:129 | Permutace potvrzuje pořadí po horizontech | Obecně nepotvrzuje: u Děčína vyřazení s horizontem klesá, permutace roste; Praha na 24 h má vyřazení −0,2, permutaci +35,0 cm. | „Permutace doplňuje pohled na závislost hotového modelu; shodné pořadí nepotvrzuje.“ |

Přepočtené hodnoty **moje × CSV**:

- Plný Děčín +24 h: **15,474749 × 15,475 cm** → 15,47 cm.
- Vyřazení Děčína +24 h: **+4,427437 × +4,427 cm** → +4,43 cm.
- Vyřazení Vltavy +36 h: **+5,003583 × +5,004 cm** → +5,00 cm.

Metoda vyřazení po přeučení poctivě měří přínos skupiny při zachování ostatních vstupů a stejného tréninku. Rostoucí přínos všech deseti horních stanic **4,2 → 12,7 → 20,9 cm** podporuje hlavní závěr pro tuto validaci, nikoli univerzální pravidlo pro každou stanici. Skupinová permutace zachová vztahy uvnitř stanice, ale poruší vztahy mezi stanicemi i časovou návaznost, takže její vysoké hodnoty nejsou realistickou ztrátou při výpadku stanice. Čtyři povodně a jedno rozdělení nestačí k doložení statistické významnosti ani konkrétního mechanismu zastupování.

**Počet nesouladů: 7 interpretačních, 0 číselných či implementačních; opakování stejného problému počítána jednou.**