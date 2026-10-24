**Nálezy: žádné závady** kritické, vysoké, střední ani nízké závažnosti.

- `src/models/h30.py:12–21`: úseky, zpoždění 0/6/12/24 h a výpočet v m³/s odpovídají předem zapsané definici i `pokus_H.py`. Bez úniku z budoucnosti; ukazatele zůstávají neodmocněné.
- `src/models/h30.py:24–27`, `src/models/h12.py:7–8`: rozhraní odpovídá validaci, alpha = 1, vstupní X se nemění. H12 nepřidává nové stanice, H30 přidává všech 18.
- Ověřeno pro oba cíle a horizonty 12/24/36 h pouze na datech do roku 2020; jeden skutečný fit H30 a predikce na nesouvislých řádcích roku 2006 prošly. Návrh oprav: žádný.

Oba moduly jsou připravené pro `src/krizova_validace.py` jako průzkumné varianty.