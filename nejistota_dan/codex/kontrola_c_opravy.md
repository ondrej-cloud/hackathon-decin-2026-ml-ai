Opravy jsou **částečné**. Nic jsem nezměnil ani nezapsal, test 2021–2025 jsem nepoužil; Python dotazy běžely pouze s `-B`, bez trénování.

`bloky()` pro všechny tři horizonty správně vytváří 14 bloků včetně řetězových překryvů. `vnorene()` správně vyřazuje celý blok. Opravy NaN, prázdných kalibračních chyb a kombinace skalárů s 1D poli fungují.

Nálezy; cesty jsou vůči kořeni projektu:

- **[vysoká] `nejistota_dan/overeni.py:120`** – Kontrola aplikace není plně nezávislá: kalibrační chyby pocházejí z LOFO modelů trénovaných i na hodnocené validaci, včetně let 2019–2020. Vynechání kalibračních řádků bloku na ř. 131 toto neodstraňuje. **Oprava:** přepočítat kalibrační předpovědi modely bez hodnocené validace; současná čísla označit jako orientační kontrolu přenosu kalibrace.

- **[střední] `nejistota_dan/prisne.py:37`** – Kalibrační modely správně vyřazují celý vnější blok, ale hodnocené předpovědi zůstávají z obyčejného LOFO, které vyřazuje pouze vlastní mezeru. Nejde tedy o úplné ověření s vynecháním bloku ze všech fitů. **Oprava:** také hodnoticí model fitovat bez celého bloku. Tvrzení na ř. 7 o přenositelnosti výsledku na LightGBM odstranit.

- **[střední] `nejistota_dan/patche/01.patch:45`** – Záloha zachycuje pouze `ImportError`. Existující modul bez `kvantily.json` skončí `FileNotFoundError`; ponechaná složka bez souboru modulu může být importována jako namespace a následně selhat na chybějícím `pasmo`. **Oprava:** před použitím ověřit dostupnost funkce a kalibračního souboru, ošetřit jejich nedostupnost.

- **[střední] `nejistota_dan/patche/01.patch:31`** – Při skutečně chybějícím modulu vrací Ridge původní 90% tréninkové pásmo, ale nový popisek stále tvrdí „8 z 10“ na 22 povodních. **Oprava:** vracet také identitu použité metody a podle ní měnit legendu i vysvětlení.

- **[střední] `nejistota_dan/patche/01.patch:64`** – Alias `ridge_vse → ridge` technicky funguje, jeho pokrytí však nebylo ověřeno. Aplikace přesto zobrazí stejné tvrzení o ověření jako u historického modelu. **Oprava:** pro `ridge_vse` viditelně uvést, že jde o neověřený odhad, a svázat kalibraci s verzí modelu.

- **[střední] `nejistota_dan/ZPRAVA_NEJISTOTA.md:137`** – Graf neukazuje přesně to, co by aplikace tehdy nabídla: používá LOFO model a kalibraci bez bloku, patch používá model aplikace a kvantily ze všech povodní; navíc jsou zahrnuty budoucí roky vůči zobrazenému datu. **Oprava:** označit graf jako retrospektivní ověření metody. Stejně zpřesnit odpověď porotě na ř. 162.

- **[střední] `nejistota_dan/ZPRAVA_NEJISTOTA.md:18`** – Několik neúspěšných variant nedokazuje, že začátek vzestupu „se nedá poznat“. Ani 14 časových bloků samo nedokazuje nezávislost deklarovanou na ř. 150. **Oprava:** psát „zkoušené signály nepomohly“, „14 oddělených bloků“ a „rekordní v hodnoceném souboru“ místo neomezených tvrzení.

- **[nízká] `nejistota_dan/ZPRAVA_NEJISTOTA.md:122`** – Ústí +12 h, 95% pásmo v klidu: CSV obsahuje **97,48 %**, tedy **97 %**, nikoli 98 %. Na ř. 14–15 je také rozsah „79–80 % u všech kombinací“ příliš úzký: minimum je **78,33 %**. **Oprava:** opravit buňku a rozsah na 78–80 %.

- **[nízká] `nejistota_dan/nejistota_dan.py:98`** – Broadcasting není úplný pro vícerozměrná pole: krátký dotaz se vstupy tvaru `(2, 1)` skončil `IndexError`. **Oprava:** explicitně přijímat pouze skaláry a 1D pole, nebo zachovat společný tvar celým výpočtem.

- **[nízká] `nejistota_dan/nejistota_dan.py:59`** – Docstring stále slibuje nepodkročení nominálního pokrytí; ořez pořadí na ř. 65 navíc u malých vzorků vrací konečné meze místo nedostupných krajních kvantilů. **Oprava:** odstranit garanci a krajní pořadí reprezentovat nekonečnými mezemi, případně malý vzorek odmítnout.

Číselná kontrola: všech **228 buněk hlavních tabulek** souhlasí se `souhrn_variant.csv` po zaokrouhlení. Namátkové hodnoty:

| Kontrola | CSV → zpráva |
|---|---|
| Ridge, Děčín +24 h: pokrytí / šířka | 79,52 % / 46,5673 cm → 80 % / 47 cm |
| G3, Děčín +24 h: šířka | 43,0288 cm → 43 cm |
| Model aplikace, Děčín +24 h: povodně / klid | 84,04 % / 85,91 % → 84 % / 86 % |
| Přísná / obyčejná kontrola, průměr 80% pokrytí | 79,4358 % / 78,9283 % → 79,4 % / 78,9 % |
| Přísná kontrola: šířka / rychlý vzestup | 54,3246 cm / 66,7658 % → 54,3 cm / 66,8 % |
| Povodeň 6/2013, Ridge Děčín +24 h | 41,52 % / 66,44 % → 42 % / 66 % |

Patch má odpovídající kontexty a po aplikaci **pouze v paměti** syntakticky prochází. Stav před 6 h bere správně z `radek[f"{cil}_H_6"]`.