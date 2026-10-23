# Porovnání modelů: čtyři lidé, čtyři modely, jeden úkol

Každý natrénuje jiný druh modelu na svém počítači a výsledky porovnáme. Aby srovnání platilo, musí všichni řešit **stejný úkol na stejných datech se stejným vyhodnocením**. Liší se jen model.

## Úkol

- **Cíl:** výška hladiny v Děčíně (a v Ústí) za 12, 24 a 36 h.
- **Vstupy:** stejná tabulka pro všechny (`src/features.py`). Hladina v Děčíně a Ústí za posledních 24 h a průtoky 12 stanic se zpožděním 0–36 h. Hodnoty jsou syrové, odmocninu a škálování si dělá každý model sám.
- **Data:** `python src/stahni_chmu_hydro.py` (ČHMÚ 2002–2025) a balíček (2024–2026).

## Proč ne nejdřív na malých řekách

Ověřeno na datech ČHMÚ 2004–2025. Data na malé řeky jsou: 13–50 velkých vod na řece. Ale chovají se jinak než Labe:

| Řeka | Voda z horní stanice dorazí za | Chyba +3 h: „jako teď“ / vlastní historie / + horní stanice (m³/s) |
|---|---|---|
| Kamenice (Srbská Kamenice → Hřensko) | 2 h | 1,10 / 0,88 / 0,39 |
| Ohře (Žatec → Louny) | 6 h | 1,72 / 1,55 / 1,05 |
| Chomutovka | 7 h | 0,28 / 0,27 / 0,23 |
| Bílina | 1 h | 0,58 / 0,53 / 0,52 |
| Mandava | 0 h | 1,04 / 0,71 / 0,63 |

- Na malé řece voda doteče za 0–7 h, takže předpovídat jde jen pár hodin dopředu. Dál rozhoduje déšť, ne voda výš po proudu.
- Model, který vyhraje na malé řece, nemusí vyhrát na Labi. Je to jiný problém: na malé řece déšť a rychlá odezva, na Labi putování vlny přes celé povodí.

**Proto:** model vybíráme na Labi, na úkolu, který nakonec ukazujeme. Malé řeky (Kamenice, Ohře) použijeme jako **druhou zkoušku**. Pustíme na ně stejné čtyři modely a podíváme se, jestli pořadí vydrží. Když vydrží, je výběr spolehlivý. Když ne, umíme vysvětlit proč, a to je pro porotu dobrý bod.

## Čtyři modely

| Model | Kdo (návrh) | Proč ho chceme | Na co si dát pozor |
|---|---|---|---|
| fyzikální: součet průtoků proti proudu posunutých o dobu putování, převedený na výšku přes měrnou křivku | Tobias | co řekne fyzika bez učení, nejsnáz se vysvětlí | doby putování jsou jen přibližné |
| lineární regrese (Ridge) | Honza | náš hlavní kandidát, zatím nejlepší výsledky | hodně podobných vstupů, proto Ridge místo obyčejné |
| LightGBM | Dan | obvykle nejsilnější na tabulková data | neumí předpovědět víc, než viděl v tréninku (2013: 823 místo 1 072 cm) |
| malá neuronová síť (MLP) | Ondra | zjistit, jestli složitější model něco přidá | normalizovat vstupy, pevný seed, hlídat přeučení |

Role jsou jen návrh, kdo si chce vzít jiný model, prohodí se. Data jsou malá (asi 180 tisíc řádků), všechno se natrénuje za minuty na procesoru, Kaggle není potřeba.

## Co je společné (staví se první, do 19:30)

Bez toho srovnání neplatí:

1. `src/data.py`: načte všechny stanice do jedné hodinové tabulky. Vyřadí chybné hodnoty (6.–7. 2. 2006 v Děčíně), sjednotí balíček (2026 po 10 minutách) s ČHMÚ.
2. `src/features.py`: z ní udělá vstupní tabulku pro zvolený cíl, horizont a brány. Jedna funkce pro všechny.
3. `src/evaluate.py`: jedno vyhodnocení pro všechny.
   - chyba celkově a zvlášť nad 1. stupněm povodňové aktivity,
   - varování před 3. stupněm: planý poplach, propásnuto, předstih v hodinách,
   - doba tréninku a předpovědi.
4. **Rozdělení:**
   - validace: vynechané povodně 4/2006, 3/2009, 9/2010, 1/2011 a klidné roky 2019–2020, na nich se ladí. Povodeň 2013 zůstává v tréninku, jinak by v něm žádná velká nebyla,
   - test: 2021–2025 s povodněmi 12/2023 a 9/2024. Pustí se jednou na konci, rozhoduje Ondra.
   - Hotové, podrobnosti v `docs/DATA.md` a zadání pro každého v `docs/UKOL_MODELY.md`.
5. Každý model je soubor `src/models/<nazev>.py` s funkcí `fit(X, y, cil, horizont)`, která vrátí funkci `predict(X)`. Skript `src/porovnej.py` pustí všechny modely na všech rozděleních a uloží výsledky do `results/`.

## Pravidla

- Nikdo nemění vstupní tabulku ani vyhodnocení jen pro svůj model. Když chce nový vstup, přidá ho do `features.py` pro všechny a řekne to ostatním.
- Ladí se jen na validačních povodních, nikdy na testu.
- Každý pokus do `docs/POKUSY.md`, i ten, který nevyšel.
- U každého modelu ukázat, podle čeho rozhoduje: váhy, důležitost vstupů, SHAP.

## Harmonogram

| Čas | Co |
|---|---|
| do 19:30 | společný základ (data, vstupy, vyhodnocení, „bude jako teď“) |
| 19:30–21:00 | každý první verzi svého modelu |
| 21:00 | první srovnání, porada |
| noc | vylepšení na validaci, druhá zkouška na Kamenici a Ohři, aplikace |
| so 8:00 | výběr modelu |
| so dopoledne | test jednou (Ondra), prezentace |

## Co čekáme (domněnka)

Lineární regrese nejspíš vyhraje nebo bude stejně dobrá jako ostatní. LightGBM selže u největších povodní. Neuronová síť bude podobná lineární regresi, ale hůř se vysvětlí. Ať to dopadne jakkoli, samotné srovnání je obsah prezentace: „zkusili jsme čtyři přístupy a vybrali jsme tenhle, protože…“
