# Vstupy finálního modelu a jejich důležitost (Děčín, týmový Ridge)

Rozbor stávajícího týmového modelu (`src/models/ridge.py`). Do modelu se nic nepřidává a nic se nemění.
Skript `prezentace_dan/vstupy_dulezitost.py` běží asi 2 min. Výsledky jsou ve `vysledky/vstupy_dulezitost.csv`
(stanice) a `vysledky/vstupy_dulezitost_vetve.csv` (větve).
Používá jen trénovací a validační část, test 2021–2025 se nepoužil.
Kontrola Codexem jen čtením (`codex/vstupy_codex.md`): všech 84 čísel sedí s CSV, 3 hodnoty přepočítal nezávisle
(15,47 cm, +4,43 cm, +5,00 cm), metrika je shodná s `evaluate.vyhodnot`. Jeho 7 výhrad k formulacím je zapracovaných.

## Obrázky

| Obrázek | Na co |
|---|---|
| `grafy/V1_co_jde_do_modelu.png` | Slajd A: schéma povodí s dobou doběhu a 98 vstupů |
| `grafy/V4_dulezitost_vetvi.png` | Slajd B, hlavní: „čím dál dopředu, tím víc rozhoduje voda proti proudu“ |
| `grafy/V2_dulezitost_stanic.png` | Slajd B, detail po stanicích, nebo záloha k otázce poroty |
| `grafy/V3_dulezitost_permutace.png` | Záloha: kontrola zamícháním |

Na co to v main navazuje (nic z toho se neduplikuje):

- `docs/grafy/prezentace/03a_mapa_stanic.png` a mapa stanic v Honzově HTML prezentaci (`web/prezentace/index.html`)
  ukazují, kde stanice jsou. V1 k tomu přidává, co přesně z každé stanice model dostane. Může nahradit nebo doplnit
  Honzův slajd „98 vstupů“.
- `docs/grafy/prezentace/04_predpoved_je_soucet.png` (Ondra): povodeň Boris rozložená na příspěvky řek. Rozklad jedné
  povodně je tam hotový, proto ho tady nedělám znovu.
- `docs/grafy/prezentace/Z6_vahy_modelu.png`: váhy po jednotlivých sloupcích (Děčín +24 h). V2 a V4 ukazují to, co
  váhy ukázat nemůžou: kolik každá stanice a větev skutečně přidá.

## Slajd A: co jde do modelu

| Co | Stanice | Zpoždění | Počet |
|---|---|---|---|
| Hladina | Děčín, Ústí n. L. | teď a před 1, 2, 3, 6, 12, 24 h | 2 × 7 = 14 |
| Průtok | 12 stanic: Děčín, Ústí, Mělník, Vraňany, Praha-Chuchle, Beroun, Nespeky (Sázava), Louny, Kostelec n. L., Předměřice (Jizera), Nymburk, Přelouč | teď a před 3, 6, 12, 18, 24, 36 h | 12 × 7 = 84 |
| **Celkem** | | | **98** |

Úprava dat (`src/models/ridge.py`): z průtoků se bere odmocnina (hladina roste zhruba s odmocninou průtoku, měrná
křivka). Pak se všech 98 čísel škáluje na stejné měřítko (StandardScaler) a jde do Ridge regrese, `alpha` = 1. Pro
každý horizont se učí zvlášť. Cílem je hladina v Děčíně za 12, 24 nebo 36 h.

Doba doběhu ve schématu je posun s největší korelací změn průtoku (`docs/DATA.md`, `src/doba_dobehu.py`). U Loun a
vzdálených stanic je jen přibližná.

**Odrážky na slajd:**

- 98 čísel, všechna změřená do okamžiku předpovědi: hladina v Děčíně a Ústí za posledních 24 h a průtok na
  12 stanicích až 36 h zpátky.
- Průtoky pod odmocninou, všechno škálované na stejné měřítko, lineární regrese.
- Není v něm: srážky, sníh, teplota. Na 24 h rozhoduje voda, která už teče řekou. Zkusili jsme to:
  týmová regrese se srážkami, sněhem a teplotou z 25 stanic 17,1 → 17,4 cm (průměr přes Děčín i Ústí a 12/24/36 h,
  Ondra), 6h srážky SYNOP v LOFO u obou Ridge do 0,1 cm (Dan).

## Slajd B: jak jsou vstupy důležité

### Metoda

Vstupy jsou silně korelované: sousední zpoždění jedné stanice jsou skoro stejná a Praha s Vraňany měří podobnou vodu
s posunem asi 4 h. Proto se důležitost měří **po stanicích** (všechna zpoždění stanice dohromady), ne po sloupcích.

1. **Vyřazení (hlavní metoda).** Ze 98 sloupců se vyřadí všechny sloupce jedné stanice. To je 14 sloupců u Děčína a
   Ústí, 7 u ostatních. Model se znovu natrénuje stejně jako týmový (`ridge.fit(..., sloupce=...)`) na stejných
   trénovacích řádcích. Měří se, o kolik vzroste chyba na povodních ve validaci. Ta se počítá stejně jako
   `evaluate.vyhodnot` (`mae_povodne`): okna 7 dní před až 5 dní po vrcholu povodně, která přešla 2. stupeň (490 cm).
   Ve validaci jsou 4 povodně: 4/2006, 3/2009, 9/2010 a 1/2011.
2. **Vyřazení celé větve.** Stejně, jen najednou celá Vltava, celé horní Labe a všech 10 stanic proti proudu. Sousední
   stanice na stejné řece měří podobnou vodu, takže vyřazení po jedné stanici může jejich význam podceňovat.
3. **Kontrola, skupinová permutace.** Plný model se nepřeučuje. Ve validaci se všechny sloupce jedné stanice zamíchají
   stejnou permutací řádků. Udělá se to 5×, se seedem 42–46, a výsledek se zprůměruje. Směrodatná odchylka je nejvýš
   1,8 cm (Děčín). U všech hodnot pod 50 cm je do 0,5 cm.

Plný model dává 9,0 / 15,5 / 26,0 cm (+12 / +24 / +36 h), stejně jako týmová čísla (`results/`, G2).

### O kolik cm vzroste chyba na povodních, když stanici vyřadíme a model přeučíme (V2)

| Stanice (doba doběhu) | +12 h | +24 h | +36 h |
|---|---|---|---|
| Děčín (cíl) | **+4,7** | **+4,4** | **+3,8** |
| Ústí n. L. (4 h) | +1,4 | +1,5 | +1,8 |
| Mělník (13 h) | +1,2 | +1,2 | +0,6 |
| Vraňany (13 h) | −0,1 | +0,1 | −0,1 |
| Kostelec n. L. (10 h) | +0,2 | +0,3 | −0,1 |
| Nymburk (10 h) | +0,1 | +0,4 | +0,4 |
| Louny (16 h) | +0,6 | +1,4 | +1,9 |
| Praha-Chuchle (17 h) | 0,0 | −0,2 | −0,3 |
| Přelouč (18 h) | +0,4 | +1,4 | +1,3 |
| Předměřice (Jizera) (18 h) | −0,3 | −0,9 | −0,5 |
| Beroun (23 h) | −0,1 | +0,4 | +0,8 |
| Nespeky (Sázava) (25 h) | +0,1 | 0,0 | +0,6 |

### Celé větve (V4)

| Bez čeho | Sloupců | +12 h | +24 h | +36 h |
|---|---|---|---|---|
| vlastní hladina a průtok Děčína | 14 | +4,7 | +4,4 | +3,8 |
| Vltava (Praha, Beroun, Sázava, Vraňany) | 28 | −0,5 | +1,4 | +5,0 |
| horní Labe (Přelouč, Nymburk, Jizera, Kostelec) | 28 | −0,5 | +0,6 | +3,0 |
| všech 10 stanic proti proudu (zbude jen Děčín a Ústí) | 70 | +4,2 | +12,7 | **+20,9** |

### Kontrola zamícháním (V3), průměr z 5 opakování

| Stanice | +12 h | +24 h | +36 h |
|---|---|---|---|
| Děčín | +280,4 | +311,6 | +380,5 |
| Ústí n. L. | +82,0 | +165,8 | +247,4 |
| Mělník | **+104,2** | +68,2 | +8,6 |
| Vraňany | −0,3 | +0,7 | **+48,7** |
| Kostelec n. L. | +4,2 | +12,1 | +7,3 |
| Nymburk | +1,7 | +5,9 | +3,2 |
| Louny | +12,0 | +15,4 | +15,9 |
| Praha-Chuchle | +1,8 | **+35,0** | +15,3 |
| Přelouč | 0,0 | +8,9 | **+23,9** |
| Předměřice (Jizera) | −0,3 | +0,5 | +2,3 |
| Beroun | +0,5 | +1,3 | +2,6 |
| Nespeky (Sázava) | +1,1 | +2,1 | +5,4 |

### Co z toho plyne

- **Z jednotlivých stanic nejvíc chybí vlastní měření Děčína** (hladina i průtok, všechna zpoždění). Bez nich je chyba
  o 3,8–4,7 cm větší a s horizontem tahle důležitost klesá.
- **Čím dál dopředu, tím víc rozhoduje voda proti proudu.** Bez všech 10 stanic proti proudu je chyba o 4,2 cm větší na
  12 h, o 12,7 cm na 24 h a o 20,9 cm na 36 h. Vltava jako celek přidá na 36 h 5,0 cm, horní Labe 3,0 cm. Na 12 h
  vyřazení ani jedné větve nevadí (−0,5 cm, pod týmovou hranicí 1 cm). Po stanicích: Louny, Přelouč, Beroun a Sázava
  mají na 36 h větší přínos než na 12 h, Mělník naopak menší. V kontrole zamícháním má Mělník nejvyšší hodnotu na 12 h,
  Praha na 24 h, Vraňany a Přelouč na 36 h.
- **Sousední stanice se nejspíš zastoupí.** Praha, Vraňany a Jizera mají po jedné skoro nulový nebo záporný vliv. To je
  slučitelné s tím, že podobnou vodu měří jiná stanice na stejné řece, a celá Vltava najednou na 36 h chybí o 5 cm.
  Který vstup informaci převezme, pokus neurčí. Rozdíly pod 1 cm (týmová hranice) nebereme jako prakticky přesvědčivé,
  to platí i pro záporné hodnoty (Jizera −0,9 cm na 24 h). Nejistotu jsme nevyčíslili.

**Proč je zamíchání řádově větší:** při vyřazení se model přeučí a chybějící stanici nahradí sousedy. Při zamíchání
model stanici dál věří, ale dostane hodnoty z jiného dne. U Děčína a Ústí to znamená úplně jinou hladinu, a proto
chyba stovky cm. Zamíchání tedy ukazuje, na co se hotový model spoléhá, ne kolik by stanice chyběla. Proto hlavní
slajd stojí na vyřazení. Zamíchání je doplňkový pohled na to, na co se spoléhá hotový model. Stejné pořadí jako
vyřazení nedává: u Děčína vyřazení s horizontem klesá a zamíchání roste, u Prahy na 24 h je vyřazení −0,2 cm a
zamíchání +35,0 cm.

**Proč ne váhy (Z6):** Praha má velkou váhu (+49 u „Praha teď“ v Z6), ale bez samotné Prahy se model nezhorší,
nejspíš proto, že podobnou vodu vidí Vraňany o 4 h níž. Váhy korelovaných vstupů se mezi sebou přelévají, a proto jednotlivé váhy klamou.
Pozor u týmového slajdu vah („Hned po Děčíně má největší váhu Praha teď“, `src/grafy_slajdy.py`, `vahy_decin_24h`) a
u Z6: nadpis platí pro váhu, ale neříkat, že Praha je nejdůležitější stanice. Bez samotné Prahy je chyba na 24 h
o 0,2 cm menší. Bez celé Vltavy je o 1,4 cm větší.

**Omezení:** jen Děčín, jen týmový Ridge, jen validace se 4 povodněmi (test se nepoužil). Jedno rozdělení
train/validace, ne LOFO. Platí to pro tuto validaci, není to obecné pravidlo pro každou stanici.

**Odrážky na slajd (V4, případně V2):**

- Důležitost po stanicích: stanici vyřadíme, model přeučíme a měříme, o kolik vzroste chyba na povodních.
- Nejvíc chybí vlastní měření Děčína (+4 až +5 cm). Bez všech stanic proti proudu je to +4 cm na 12 h, +13 cm na
  24 h a +21 cm na 36 h.
- Čím dál dopředu, tím víc rozhoduje voda proti proudu: na 12 h hlavně Ústí a Mělník, na 36 h Vltava (+5 cm),
  horní Labe (+3 cm) a Louny (+1,9 cm).

## Mluvený text pro Dana (asi 35 s)

> Do modelu jde 98 čísel a všechna jsou v okamžiku předpovědi už změřená. Hladina v Děčíně a Ústí za posledních
> 24 hodin a průtoky na dvanácti stanicích až 36 hodin zpátky, od Prahy a Sázavy přes Přelouč až po Louny na Ohři.
> Srážky ani sníh tam nejsou: na den dopředu rozhoduje voda, která už teče řekou, a srážky jsme zkoušeli, celkovou chybu nezlepšily.
> Důležitost jsme měřili tak, že jsme stanici vyřadili a model přeučili. Nejvíc chybí vlastní měření Děčína. A čím dál
> dopředu, tím víc rozhoduje voda proti proudu: bez horních stanic je chyba na 12 hodin větší o 4 centimetry, na
> 36 hodin o 21.

## Otázky poroty, které to může vyvolat

- **„Proč má Praha velkou váhu, ale bez ní se model nezhorší?“** Nejspíš ji zastoupí Vraňany, jsou na Vltavě o 4 h níž
  a měří podobnou vodu. Celá Vltava najednou na 36 h chybí o 5 cm.
- **„Proč jsou některá čísla záporná?“** Na 4 validačních povodních je bez té stanice model o pár milimetrů lepší. Pod
  1 cm to nebereme jako přesvědčivý rozdíl a nejistotu jsme nevyčíslili, takže z toho neplyne, že stanice škodí.
- **„Proč ne SHAP nebo váhy?“** U lineárního modelu s korelovanými vstupy se váhy přelévají mezi sousedy. Vyřazení a
  přeučení odpovídá přímo na otázku, kolik stanice přidá.
