# Nálezy Codexu a co s nimi

Codex (`codex exec -s read-only`, pravidla v promptu: nic neměnit, nečíst .env ani přihlašovací údaje, test
2021–2025 nepoužít, nálezy se souborem, řádkem a závažností). Prompty a plné odpovědi v `codex/`.

## (a) Metodika a kód pásma nejistoty (so 02:44–02:56)

Bez nálezu: režimy používají jen předpověď, stav teď a stav před 6 h; skutečný vývoj jen pro hodnocení; Winklerovo
(intervalové) skóre správně; pořadí kvantilů s opravou n + 1 správně; G3 odpovídá `g3.py`; rychlý Ridge = sklearn
(5,9·10⁻⁹ cm); `pasmo()` funguje pro čísla i pole.

| Závažnost | Nález | Reakce |
|---|---|---|
| vysoká | `overeni.py:79` okna 12/2012 a 1/2013 sdílejí 48 h, při vynechání jen `fold == k` zůstanou v kalibraci | **Opraveno**: vnoření po blocích (14 bloků, povodně, jejichž mezery ± 20 dní se překrývají); pásmo povodně k jen z povodní mimo její blok |
| vysoká | `overeni.py:79`, `oof.py:83` modely ostatních povodní povodeň k při učení viděly | **Opraveno pro Ridge, zdůvodněno pro G3**: `prisne.py` počítá chyby pro kalibraci znovu modely bez celého bloku k (Ridge, Ridge 30, ze součtů); vyšlo skoro stejně jako obyčejné vnoření (viz zpráva). U LightGBM by to bylo 462 fitů na kombinaci, G3 je proto vnořený jen obyčejně a ve zprávě to stojí |
| vysoká | `nejistota_dan.py:55` oprava n + 1 nic nezaručuje (autokorelace, 22 modelů) | **Opraveno ve formulaci**: pokrytí je všude označené jako empirické, ověřené vnořeně po blocích; ve zprávě, že nezávislých pozorování je 22 povodní (14 bloků), ne 6 358 hodin |
| vysoká | `overeni.py:150`, `app/predikce.py:40` kalibrace z LOFO modelů ≠ modely aplikace | **Ověřeno**: `kontrola_aplikace()` přímo na modelu aplikace (Ridge do 2018) na neviděné validaci: 80% pásmo 84–88 % na povodních, 86–94 % v klidu 2019–2020, tedy opatrné; pro model do 2025 (Dnešek) neověřitelné, ve zprávě napsané |
| střední | `prisne.py:7` shoda u Ridge nedokazuje platnost pro LightGBM/G3 | **Přijato**: ve zprávě je G3 výslovně „obyčejně vnořený“, závěr o přísnosti jen pro Ridge |
| střední | `lgbm_stanice.py:49`, `lgbm_a.py:25` týmové doby doběhu LightGBM odhadnuté na tréninku s částí povodní | **Zdůvodněno**: je to vlastnost kandidáta G3 (pevné `lgbm_a.DOBA` z týmového modelu), ne pásma; měnit by znamenalo měnit model; ve slabinách |
| střední | `nejistota_dan.py:70` 200 hodin není 200 nezávislých pozorování, vážení hodin × povodní | **Opraveno**: `kvantily.json` má u každé skupiny počet hodin, počet povodní a příznak náhrady; povodně mají v oknech stejný počet hodin (289), uvnitř skupiny se váží hodinami, to je ve zprávě |
| střední | `overeni.py:138` výběr a vykázání vítěze na stejných datech | **Přijato**: všechny zkoušené varianty i zamítnuté (Mělník, poslední chyba) jsou ve zprávě s čísly; rozdíly mezi variantami jsou malé, výběr to nepřikrášlí o víc než pár procent skóre |
| střední | `overeni.py:136` celkové pokrytí zakrývá slabé vzestupy | **Přijato**: rychlý vzestup a začátek vzestupu jsou v každé tabulce a ve shrnutí, i v grafu `pokryti.png` |
| střední | `app/predikce.py:68` nové pásmo není zapojené | **Návrh**: `patche/01_pasmo_nejistoty.patch` (aplikace v main se nemění) |
| střední | `oof.py:103` Ústí jen na děčínských oknech, klid mimo povodně neověřen | **Částečně**: klid ověřen na validaci 2019–2020 (model aplikace); Ústí na stejných událostech, ve slabinách |
| nízká | `nejistota_dan.py:59` prázdný vzorek → IndexError | **Opraveno**: `kvantil()` odmítne prázdné nebo neplatné chyby výjimkou |
| střední | `nejistota_dan.py:44` NaN není ošetřené | **Opraveno**: `pasmo()` vrátí NaN, když chybí předpověď nebo stav, žádné zdánlivě platné pásmo |
| nízká | `nejistota_dan.py:93` smíšené tvary se tiše zkrátí | **Opraveno**: vstupy se rozšíří na společný tvar (`np.broadcast_arrays`), číslo vrací jen když jsou všechny vstupy čísla |

## (c) Kontrola oprav (so 03:53–04:07)

Potvrdil: `bloky()` dává pro všechny horizonty 14 bloků včetně řetězových překryvů, `vnorene()` vyřazuje celý blok,
ošetření NaN, prázdných chyb a čísel s poli funguje; všech 228 buněk hlavních tabulek zprávy souhlasí s CSV; patch 01
bere stav před 6 h správně z řádku vstupů.

| Závažnost | Nález | Reakce |
|---|---|---|
| vysoká | `overeni.py:120` kontrola modelu aplikace není nezávislá: kalibrační LOFO modely viděly validaci (i 2019–2020) | **Opraveno**: `prisne.py` `kontrola_aplikace_prisne()`: kalibrace jen z 18 tréninkových povodní z modelů učených na trénovací části bez té povodně; 80% pásmo 85–90 % (povodně), 87–94 % (klid), původní verze označená jako méně přísná |
| střední | `prisne.py:37` hodnocená předpověď je z modelu bez vlastní mezery, ne celého bloku; tvrzení o přenosu na LightGBM | **Opraveno**: hodnocená předpověď přepočítaná bez celého bloku (výsledek 79,4 / 94,2 %); věta o LightGBM změněná na „naznačuje, G3 přísně ověřený není“ |
| střední | `patche/01.patch:45` záloha jen na ImportError, chybějící `kvantily.json` shodí aplikaci | **Opraveno**: `_nejistota()` použije modul jen s funkcí `pasmo` a existujícím `kvantily.json`; ověřeno, že bez modulu aplikace vrátí staré pásmo |
| střední | `patche/01.patch:31` při záloze popisek dál tvrdí „8 z 10“ | **Opraveno**: `popis_pasma()` vrací legendu a větu podle toho, které pásmo se opravdu použilo |
| střední | `patche/01.patch:64` `ridge_vse` dostane tvrzení o ověření, které nemá | **Opraveno**: u `ridge_vse` věta „model pro dnešek se na neviděných datech ověřit nedá, rozmezí je u něj odhad“ |
| střední | `ZPRAVA_NEJISTOTA.md:137` grafy nejsou to, co by aplikace tehdy ukázala | **Opraveno ve formulaci**: „zpětné ověření metody“, s vysvětlením proč |
| střední | `ZPRAVA_NEJISTOTA.md:18, 150` „nedá se poznat“, „nezávislá“, „rekordní“ | **Opraveno**: „zkoušené signály nepomohly“, „14 oddělených časových bloků“, „největší povodeň v hodnoceném souboru“ |
| nízká | `ZPRAVA_NEJISTOTA.md:122` Ústí +12 h 95 % v klidu 97, ne 98; rozsah 78–80, ne 79–80 | **Opraveno** (tabulka modelu aplikace je teď z přísné kontroly, rozsah 78–80 %) |
| nízká | `nejistota_dan.py:98` vícerozměrná pole | **Opraveno**: `pasmo()` bere jen čísla a jednorozměrná pole, jinak výjimka |
| nízká | `nejistota_dan.py:59` docstring slibuje pokrytí, ořez pořadí u malých vzorků | **Opraveno**: docstring bez záruky, na malý vzorek výjimka místo ořezu (skupiny pod 200 hodin stejně dostanou kvantily ze všech chyb) |

## (d) Patche 01 a 10 a texty pro tým (so 04:38–04:40)

Potvrdil: 01–10 jdou po sobě bez kolizí, 10 potřebuje 01; stav před 6 h správně v historii i Dnešku; patch 10 bere
archiv a posun o horizont správně; šířky −9 až +24 a −30 až +56 cm sedí s `kvantily.json`.

| Závažnost | Nález | Reakce |
|---|---|---|
| vysoká | `REVIZE_APLIKACE.md` 85–90 % neověřuje přímo nasazené pásmo (jiná kalibrace) | **Opraveno ve formulaci**: „kontrola metody“, nasazené kvantily jsou z 22 povodní včetně validačních |
| vysoká | `PREZENTACE_PASMO.md` „8 z 10 podobných situací“ = podmíněné pokrytí | **Opraveno**: „zpětně asi v 8 z 10 hodin; při rychlém vzestupu jen asi ve 2 ze 3“ |
| střední | srovnání s „dnešním pásmem“ používá 80% variantu týmové metody, ne skutečné 90% pásmo | **Opraveno**: dopočteno skutečné 90% pásmo (`vysledky/tym_pasmo_90.csv`: 72–83 %, rychlý vzestup 33–44 %), graf `pokryti.png` popisuje šedé sloupce jako „týmová metoda (také 80 %)“ |
| střední | `01.patch` `popis_pasma()` nezná použitou větev a úroveň | **Opraveno**: `popis_pasma(nazev, uroven)` s úrovní v textu, volá se jen tam, kde `interval()` dostává stav před 6 h; poznámka o `ridge_vse` i u starého pásma |
| střední | `01.patch` rozbitý `kvantily.json` shodí stránku | **Opraveno**: `_nejistota()` modul zkusí jedním voláním, při chybě zůstane staré pásmo (ověřeno s podvrženým rozbitým JSON) |
| střední | `ZPRAVA_NEJISTOTA.md` šířka 32 cm je průměr, ne Děčín +24 h | **Opraveno**: 29 cm |
| střední | `PREZENTACE_PASMO.md` „ani v Praze“ není v definici začátku vzestupu | **Opraveno** |
| nízká | „trefíme se skoro na centimetry“ | **Opraveno**: „bývají chyby malé“ |
