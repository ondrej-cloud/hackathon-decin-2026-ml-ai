01–10 navazují bez kolizí při aplikaci pouze v paměti; výsledná syntaxe je platná. `git apply --check` prošel pro 01 i 10; **10 potřebuje 01 kvůli importu a API**, přestože samotná kontrola kontextu projde i bez něj.

Stav před 6 h je správně ze vstupního řádku v historii i Dnešku. Patch 10 správně používá archiv, čas vydání a posun grafu o horizont. Bez modulu či `kvantily.json` se použije původní pásmo, pokud existuje jeho JSON. Současný nový JSON obsahuje všechny potřebné kombinace.

- [vysoká] nejistota_dan/REVIZE_APLIKACE.md:61 – **85–90 % neověřuje přímo nasazené pásmo** – přísná kontrola používá kalibraci z 18 povodní, aplikace JSON ze všech 22, včetně validačních událostí. Čísla v CSV sedí, ale popsat je jako kontrolu metody s jinou kalibrací; případně nasadit odpovídající kvantily.

- [vysoká] nejistota_dan/PREZENTACE_PASMO.md:8 – „8 z 10 podobných situací“ přisuzuje konkrétnímu pásmu podmíněné pokrytí – 78–80 % je celkové zpětné pokrytí, při rychlém vzestupu jen 59–72 %. Nahradit formulací „metoda zpětně pokryla přibližně 80 % hodnocených hodin“ a slabinu uvést hned.

- [střední] nejistota_dan/REVIZE_APLIKACE.md:59 – původnímu **90% pásmu** přisuzuje výsledky **80% varianty** – CSV `tym_trenink` na úrovni 0,8 nedokládá pokrytí skutečného původního pásma. Totéž mate v PREZENTACE_PASMO.md:20. Výslovně označit srovnávanou 80% variantu; skutečné 90% pásmo těmito čísly nehodnotit.

- [střední] nejistota_dan/patche/01.patch:89 – `popis_pasma()` nezná skutečně použitou větev – při vynechaném `hladina_pred_6h` vrátí `interval()` staré pásmo, popis nové; při jiné úrovni stále říká 80 %. U nepodporovaného modelu popisuje neexistující pásmo a záložní větev postrádá upozornění pro `ridge_vse`. Odvozovat popis ze zdroje, úrovně a dostupnosti výsledku.

- [střední] nejistota_dan/patche/01.patch:60 – kontrola souboru nezaručuje bezpečné načtení – existující neplatný či neúplný JSON vyvolá neošetřenou výjimku v `pasmo()`; volání v 01 i 10 může přerušit stránku. Ověřit obsah a potřebné klíče před aktivací, při chybě použít zálohu s odpovídajícím popisem.

- [střední] nejistota_dan/ZPRAVA_NEJISTOTA.md:27 – starému pásmu pro Děčín +24 h připisuje šířku 32 cm – CSV uvádí **28,6524 cm**; 31,6064 cm je průměr přes stanice a horizonty. Pro uvedenou kombinaci napsat přibližně **29 cm**.

- [střední] nejistota_dan/PREZENTACE_PASMO.md:37 – „nestoupá ani … v Praze“ není definicí hodnoceného začátku vzestupu – výpočet sleduje místní změnu za 6 h a následný vzestup, Prahu nepodmiňuje. Zmínku o Praze odstranit.

- [nízká] nejistota_dan/PREZENTACE_PASMO.md:48 – „trefíme se skoro na centimetry“ přehání přesnost – doložené klidové pásmo má šířku 33 cm. Napsat „chyby bývají menší než při vzestupu“.

Šířky **−9 až +24 cm / −30 až +56 cm** odpovídají JSON (−9,4/+23,6 a −30,3/+56,0). Ostatní rozsahy ve shrnutí zprávy odpovídají CSV po zaokrouhlení.

Nic jsem nezměnil ani nezapsal, aplikaci nespustil, `.env` ani přihlašovací údaje nečetl a test 2021–2025 nepoužil.