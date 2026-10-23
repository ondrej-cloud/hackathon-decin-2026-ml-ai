# Labe: čtyři modely, jeden úkol

**Jsem:** ______ (Ondra / Dan / Honza / Tobias)

Do prázdného místa napiš své jméno. Pak ve složce repozitáře spusť `claude` a celý tenhle text tam vlož. Všechno ostatní udělá sám, ty jen kontroluj, co dělá, a odpovídej na otázky.

## O co jde

Předpovídáme hladinu Labe v Děčíně a v Ústí nad Labem za 12, 24 a 36 hodin. Vycházíme z toho, kolik vody teče teď a před pár hodinami na Labi, Vltavě, Ohři a jejich přítocích proti proudu. Voda z Prahy doteče do Děčína zhruba za den, takže to, co teče v Praze teď, víme dopředu. Data jsou z ČHMÚ za roky 2006–2025, po hodinách, 12 stanic.

Každý z nás vyzkouší jiný druh modelu. Úkol, data i vyhodnocení jsou pro všechny stejné, liší se jen model. Ve 21:00 výsledky porovnáme, nejlepší model půjde do aplikace a srovnání všech čtyř bude v prezentaci. Porota chce vidět, že jsme zkusili víc přístupů a umíme vysvětlit, proč jsme vybrali ten jeden.

| Kdo | Model | Soubor |
|---|---|---|
| Tobias | fyzikální model: posun vody o dobu putování a měrná křivka, skoro bez učení | `src/models/fyzika.py` |
| Honza | lineární regrese (Ridge) | `src/models/ridge.py` |
| Dan | LightGBM (rozhodovací stromy) | `src/models/lgbm.py` |
| Ondra | malá neuronová síť (MLP) | `src/models/mlp.py` |

## Co je hotové (v `main`)

| Soubor | Co dělá |
|---|---|
| `data/external/labe_hodinove.parquet` | hodinová tabulka stavů a průtoků 2006–2025, v Gitu, nic se nestahuje |
| `src/data.py` | seznam stanic, stupně povodňové aktivity, `nacti()` |
| `src/features.py` | `tabulka(cil, horizont)` vrátí vstupy X a cíl y, stejné pro všechny |
| `src/evaluate.py` | společné rozdělení train / val / test a vyhodnocení |
| `src/porovnej.py` | natrénuje model, vyhodnotí ho a uloží výsledek do `results/` |
| `src/models/jako_ted.py` | základ „bude jako teď“: hladina za h hodin je stejná jako teď |

**Vstupy X.** Řádek je okamžik t, kdy předpověď vydáváme. Sloupce:
- `decin_H_<z>`, `usti_H_<z>`: hladina v cm před z hodinami (z = 0, 1, 2, 3, 6, 12, 24),
- `<stanice>_Q_<z>`: průtok v m³/s před z hodinami (z = 0, 3, 6, 12, 18, 24, 36), stanice `decin, usti, louny, melnik, vranany, kostelec, praha, nymburk, jizera, beroun, sazava, prelouc`.

Hodnoty jsou syrové, bez úprav. Odmocninu, škálování a podobně si dělá každý model sám. **y** je hladina v cm v čase t + horizont.

**Rozdělení:**
- **train:** 2006–2018 bez validačních povodní a 20 dní kolem nich,
- **val:** 4 povodně, které model při tréninku neviděl (4/2006, 3/2009, 9/2010, 1/2011), a klidné roky 2019–2020; jen na nich se ladí,
- **test:** 2021–2025 s povodněmi 12/2023 a 9/2024. Pustí se jednou, na konci, spouští ho jen Ondra.

**Co znamenají čísla ve výsledku** (všechno na validaci):

| Sloupec | Význam |
|---|---|
| `mae` | průměrná chyba v cm za celou validaci, hlavně klidná voda |
| `mae_povodne` | průměrná chyba v cm během povodní (7 dní před vrcholem až 5 dní po něm). **Hlavní číslo.** |
| `chyba_vrcholu` | o kolik cm se spletla výška vrcholu, když jsme ho předpovídali h hodin předem |
| `spa2_predstih_h` | o kolik hodin dřív model varoval před 2. stupněm povodňové aktivity (Děčín 490 cm, Ústí 530 cm) |
| `spa2_propasnuto` | povodně, před kterými nevaroval vůbec |
| `spa2_plane_poplachy` | varování, po kterých povodeň nepřišla |
| `spa3_...` | totéž pro 3. stupeň (Děčín 560 cm, Ústí 600 cm) |
| `bias_povodne` | o kolik model na povodních v průměru nadhodnocuje (+) nebo podhodnocuje (−). Soustavné nadhodnocování zlepšuje předstih, proto se dívej na obojí. |

Předstih je nejvýš horizont a propásnutá povodeň se do něj počítá jako 0. Každý výsledek si ukládá otisk verze dat a vyhodnocení (`verze` v JSON). `--prehled` ukazuje jen výsledky s aktuální verzí, starší vypíše jako „pusť je znovu“.

**S čím se srovnáváme:**

| Děčín, chyba na povodních | +12 h | +24 h | +36 h |
|---|---|---|---|
| „bude jako teď“ (`jako_ted`) | 23,0 cm | 44,4 cm | 65,6 cm |
| rychlý lineární model při kontrole řetězce (orientačně) | 9,0 cm | 15,5 cm | 26,0 cm |

„Jako teď“ před žádnou povodní nevaruje, všechny propásne. Rychlý lineární model varoval 11–37 h předem, nic nepropásl a neměl planý poplach. Kdo je na povodních horší než „jako teď“, má někde chybu.

## Pokyny pro Claude

Pracuješ s člověkem, jehož jméno je nahoře. Postupuj krok za krokem a každý krok ověř, než půjdeš dál. Mluv česky a stručně. Platí všechno z `CLAUDE.md`: commity jen pod jménem člověka, seed 42, zápisy do `docs/`.

1. **Kdo je člověk.** Udělej, co říká `.claude/skills/<jméno malými písmeny bez diakritiky>/SKILL.md`, stejně jako po příkazu `/<jméno>`. Přepni se na jeho větev a pusť `git fetch origin` a `git merge origin/main`. Ověř, že existuje `data/external/labe_hodinove.parquet` a `src/porovnej.py`. Když ne, merge se nepovedl, zastav se a řekni to.
2. **Prostředí.** Použij `.venv` ve složce repozitáře, na Windows `.venv\Scripts\python`. Ověř, že jde `import pandas, sklearn, pyarrow`, pro Dana i `lightgbm`. Co chybí, doinstaluj přes `pip install`.
3. **Kontrola.** Pusť `python src/porovnej.py jako_ted --rychle`. Děčín za 24 h musí mít na povodních 44,4 cm. Když vyjde jinak, zastav se a řekni to člověku, ať napíše Ondrovi.
4. **Načti kontext.** Přečti `docs/NAPAD_LABE.md` (hlavně sekce Brány proti proudu), `src/features.py`, `src/evaluate.py` a níž zadání pro tohoto člověka. Člověku řekni ve třech větách, co bude dělat a proč.
5. **Model.** Napiš `src/models/<soubor>.py` podle zadání. Model je funkce `fit(X, y, cil, horizont)`, která vrátí funkci `predict(X)` (vzor je `src/models/jako_ted.py`). Funguje pro oba cíle (`decin`, `usti`) a všechny horizonty (12, 24, 36). První řádek docstringu je popis, který se uloží k výsledku. Nastavení dej do slovníku `PARAMETRY`.
6. **Běh.** Nejdřív `python src/porovnej.py <soubor bez .py> --rychle` (jen Děčín za 24 h), když to dává smysl, tak bez `--rychle` (všech 6 kombinací). Výsledek se uloží do `results/` a předpovědi do `results/predpovedi/`. Srovnání s ostatními ukáže `python src/porovnej.py --prehled`.
7. **Varianty.** Projdi pokusy ze zadání a pak iteruj podle pravidel níž (Jak dlouho iterovat). Každou variantu, kterou chceš mít ve srovnání, ulož jako `src/models/<soubor>_<co>.py`. Nejlepší varianta se nakonec jmenuje `<soubor>.py`. Ke každému pokusu přidej záznam do `docs/POKUSY.md`, i k nepovedenému: co se zkoušelo, proč, výsledek proti „jako teď“ a závěr.
8. **Vysvětlení.** U nejlepší varianty ukaž, podle čeho model rozhoduje, podle zadání níž. Graf ulož do `docs/grafy/<soubor>_<co>.png` a jednou větou ho popiš v `docs/POKUSY.md`.
9. **Co se nesmí.**
   - Nikdy nespouštěj `--test`, to dělá jen Ondra.
   - Neměň `data.py`, `features.py`, `evaluate.py` ani `porovnej.py`. Když potřebuješ jiný vstup nebo najdeš chybu, řekni to člověku, ať to probere s Ondrou, jinak výsledky nepůjdou srovnat.
   - Neladí se na tom, co vyjde v `--prehled` u ostatních, jen na vlastní validaci.
   - Podezřele dobrý výsledek (na povodních pod 5 cm za 24 h) dej zkontrolovat subagentu `kontrolor`.
10. **Odevzdání.** Rozbor podle vzoru z `CLAUDE.md` napiš člověku do chatu i do `docs/DENIK.md`. Pak `/sync main`: commitni jen svůj model, výsledky v `results/` a své zápisy v `docs/`. Polož člověku otázku poroty z rozboru.

### Jak dlouho iterovat

Zlepšuj model v cyklu: natrénovat, vyhodnotit, zjistit, kde chybuje, upravit a znovu. Pravidla:

- **Hlavní číslo** je `prumer_povodne`, který `porovnej.py` vypíše na konci plného běhu: průměr `mae_povodne` přes všech 6 kombinací cíle a horizontu. Nehoň zlepšení jen u jedné kombinace.
- **Každá varianta má důvod.** Nejdřív se podívej, kde model chybuje (která povodeň, stoupání nebo vrchol, který horizont), a z toho odvoď jednu změnu. Měň vždycky jen jednu věc. Žádné slepé zkoušení stovek nastavení.
- **Zlepšení se počítá od 1 cm** v `prumer_povodne`. Menší rozdíl je u 4 povodní jen náhoda.
- **Zlepšení nesmí zhoršit varování**: víc propásnutých povodní nebo planých poplachů znamená, že varianta neprošla.
- **Konec:** když 3 varianty po sobě nezlepší `prumer_povodne` aspoň o 1 cm, nebo po 10 variantách, nebo ve 20:50. Pak napiš rozbor.

Proč ne do nekonečna: validace má jen 4 povodně. Kdo zkusí sto variant, najde nějakou, která na těch čtyřech povodních náhodou vyjde dobře, a na testu pak propadne. Tomu se říká přeučení na validaci. Porota navíc ocení, že každý krok umíme zdůvodnit.

### Na co si dát pozor

Projdi u každé varianty, než ji vyhlásíš za lepší:

- **Povodně nejsou odlehlé hodnoty.** Data jsou zkontrolovaná (`docs/DATA.md`, sekce Labe) a jediná chyba (2/2006) je vyřazená. Nic dalšího nemaž, neořezávej ani nevyhlazuj, hlavně ne vysoké hodnoty, kvůli nim to celé děláme. Když narazíš na něco podezřelého v datech, řekni to člověku, ať to předá Ondrovi.
- **Žádné informace z budoucnosti.** Používej jen sloupce z X a nic nepočítej z y ani z pozdějších řádků. Žádné klouzavé průměry vycentrované kolem t, žádné míchání řádků a žádné náhodné dělení dat. Škálování a další úpravy se učí jen na trénovacích datech uvnitř `fit`, nejlíp přes `Pipeline`.
- **Přeučení.** U každé varianty porovnej chybu na trénovacích datech a na validaci. Když je na tréninku výrazně menší, třeba poloviční, model se učí nazpaměť. Pak ho zjednoduš: menší síť, méně listů, silnější regularizace. Týká se hlavně LightGBM a sítě.
- **Vrcholy nad rámec tréninku.** Validační povodně 2006 (875 cm) a 2011 (730 cm) jsou vyšší než všechno v tréninku kromě 2013. Sleduj `vrcholy_o_kolik` v JSONu: když model vrcholy soustavně podhodnocuje, neumí předpovědět víc, než viděl.
- **Rozumné předpovědi.** Předpověď nesmí být záporná, nesmí skákat o metr z hodiny na hodinu a při klidné vodě má být blízko „jako teď“. Nakresli jednu validační povodeň (skutečnost, „jako teď“ a tvůj model). Graf ukáže víc než tabulka, třeba jestli model stoupání předbíhá, nebo se opožďuje.
- **Náhoda.** Seed je 42. U sítě a LightGBM pusť nejlepší variantu i se seedy 43 a 44. Rozdíl menší, než jaký dělá změna seedu, není zlepšení.
- **Jednotky a čas.** Hladina je v cm, průtok v m³/s a čas v UTC. Číslo na konci názvu sloupce znamená, kolik hodin zpátky, ne dopředu.
- **Co nevíme, nehádej.** Když si nejsi jistý, jestli je něco únik informací, nebo chyba, zastav se a zeptej se. Radši jedna otázka navíc než výsledek, který na testu propadne.

**Časy:** první výsledek (`--rychle`) do 20:15, hotová nejlepší varianta s vysvětlením a `/sync main` do 21:00. Ve 21:00 porovnáváme.

## Zadání: Tobias, fyzikální model (`fyzika.py`)

Tobias má menší limit, takže pracuj úsporně: model Sonnet, žádní paralelně běžící agenti, krátké odpovědi.

Myšlenka: voda, která teď teče v Mělníku a v Lounech, bude za pár hodin v Ústí a Děčíně. Model se skoro nic neučí, jen dobu putování vody a měrnou křivku (vztah mezi průtokem a hladinou na stanici). Je to fyzikální základ, se kterým se učené modely srovnávají, a dá se celý vysvětlit na jednom obrázku.

1. **Doba putování.** Labe do Ústí přitéká třemi větvemi: Vltava (Vraňany), Labe (Kostelec) a Ohře (Louny). Pro každou větev zjisti z trénovacích dat, za kolik hodin se změna průtoku projeví v cíli. Hledej největší korelaci změn průtoku za 6 h mezi branou a cílem, posunutých o 0–48 h. Orientačně do Ústí: Kostelec 6–14 h, Vraňany 9–20 h, Louny 12–34 h. Z Ústí do Děčína jsou to asi 4 h.
2. **Průtok v cíli za h hodin:** průtok v cíli teď plus to, o kolik víc vody mezitím přiteklo branami. Pro bránu s dobou putování τ:
   - když τ ≥ h, je to `Q_brana(před τ − h) − Q_brana(před τ)`, obojí známe;
   - když τ < h, ta voda ještě nedotekla ani do brány. Vezmi poslední hodnotu, nebo podobně stanici dál proti proudu (Praha, Beroun a Sázava pro Vltavu, Nymburk, Jizera a Přelouč pro Labe).

   Používej jen zpoždění, která jsou v X (0, 3, 6, 12, 18, 24, 36), a zaokrouhli na nejbližší.
3. **Měrná křivka.** Z trénovacích dat cíle sestav vztah průtok → hladina, třeba medián hladiny v úzkých pásmech průtoku a `np.interp`. Předpověď pak je hladina teď + (křivka(předpovězený průtok) − křivka(průtok teď)). Takhle se zachová, co je na stanici právě teď jinak.
4. **Vysvětlení:** graf měrné křivky Děčína se stupni povodňové aktivity a obrázek tří větví s dobami putování. Řekni, o kolik je to lepší než „jako teď“ a o kolik horší než učené modely, a proč: neví o přítocích v kraji, doby putování se mezi povodněmi mění.

## Zadání: Honza, lineární regrese (`ridge.py`)

Náš hlavní kandidát: v kontrole řetězce vyšel nejlíp a dá se nejsnáz vysvětlit.

1. **v1:** odmocnina **jen na průtoky** (sloupce `_Q_`), hladiny nech, jak jsou. Ověřili jsme, že odmocnina na hladině zkazí vrchol povodně 2006 o metr. Pak `StandardScaler` a `Ridge(alpha=1)`. Orientačně by Děčín za 24 h měl na povodních vyjít kolem 15 cm.
2. **Síla regularizace:** alpha 0,1 / 1 / 10 / 100, vyber na validaci.
3. **Cíl jako změna:** model se učí `y − decin_H_0` (o kolik hladina stoupne nebo klesne) a k výsledku se hladina teď zase přičte. Pomůže to?
4. **Brány podle horizontu:** pro 12 h jen blízké stanice (Ústí, Louny, Mělník, Vraňany, Kostelec), pro 36 h všechny. V `docs/NAPAD_LABE.md` vyšlo, že čím dál dopředu předpovídáme, tím dál proti proudu se musíme dívat. Platí to i tady?
5. **Vysvětlení:** graf vah. Pro každou stanici vynes váhu podle zpoždění: kde je váha největší, tam je doba putování vody. To je nejlepší obrázek pro porotu, že model dělá fyzikálně rozumnou věc.

Po 21:00 se nejspíš vrátíš k aplikaci. Předpovědi všech modelů na validaci jsou v `results/predpovedi/<model>.parquet` (sloupce `cil, horizont, skutecnost, predpoved`, index `cas_vydani`), hodí se na graf „skutečnost a předpověď při povodni 2011“.

## Zadání: Dan, LightGBM (`lgbm.py`)

Rozhodovací stromy jsou na tabulková data obvykle nejsilnější. Mají ale jednu slabinu: neumí předpovědět víc, než viděly při tréninku. V trénovacích datech je jediná velká povodeň (2013).

1. **v1:** `LGBMRegressor(n_estimators=500, learning_rate=0.05, num_leaves=31, random_state=42)`, cíl je hladina. Podívej se, jak dopadnou vrcholy (`vrcholy_o_kolik` v JSONu).
2. **v2, cíl jako změna:** učit `y − <cil>_H_0` a hladinu teď přičíst zpět. V kontrole řetězce to vyšlo na povodních kolem 50 cm, hůř než „jako teď“ (44 cm). Zjisti proč. Tipy: přeučení na málo povodních (menší `num_leaves`, větší `min_child_samples`), méně stromů.
3. **Zastavení tréninku:** když chceš early stopping, odděl si na to poslední dva roky z trénovacích dat. Nikdy ne validaci.
4. **Monotónní omezení** (`monotone_constraints`): víc vody proti proudu nesmí znamenat nižší hladinu. Dobře se vysvětluje a může pomoct na povodních.
5. **Vysvětlení:** SHAP (`shap.TreeExplainer`) pro nejlepší variantu. Které stanice a zpoždění rozhodují, a graf pro jednu povodeň.

Můžeš pustit 2–3 agenty paralelně, každého na jinou variantu. Na konci napiš na rovinu, jestli stromy na povodních prohrávají s lineárním modelem a proč. I to je pro porotu dobrý výsledek.

## Zadání: Ondra, neuronová síť (`mlp.py`)

Zjišťujeme, jestli složitější model přidá něco, co lineární regrese neumí. Data jsou malá (asi 110 tisíc řádků, 98 sloupců), takže stačí scikit-learn na procesoru. PyTorch ani GPU nejsou potřeba.

1. **v1:** `Pipeline` s odmocninou na průtoky, `StandardScaler` a `MLPRegressor(hidden_layer_sizes=(64, 32), early_stopping=True, random_state=42, max_iter=300)`. Cíl je změna `y − <cil>_H_0`, škálovaná přes `TransformedTargetRegressor`.
2. **Velikost a regularizace:** (32,), (64, 32), (128, 64) a `alpha` 1e-4 / 1e-3 / 1e-2.
3. **Stabilita:** nejlepší variantu pusť se seedy 42, 43 a 44. Když se výsledky liší víc než o pár cm, je to slabina, kterou musíme říct.
4. **Vysvětlení:** permutační důležitost vstupů (`sklearn.inspection.permutation_importance`) na validaci a srovnání s vahami lineárního modelu.

Ondra navíc: ve 21:00 `python src/porovnej.py --prehled`, porovnat všechny čtyři modely na povodních, vybrat finální model a zapsat to do `docs/DENIK.md`. Finální test (`--test`) jednou v sobotu ráno.
