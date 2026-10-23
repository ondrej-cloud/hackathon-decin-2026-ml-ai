# Nápad: Labe v Děčíně, kdy přijde velká a kdy malá voda

Všechna čísla níž jsou spočítaná z dat (pá 17:50). Co je jen domněnka, je tak označené.

## Otázka a pro koho

**Hlavní otázka:** dokážeme den dopředu říct, jak vysoko bude Labe v Děčíně, a vysvětlit, odkud voda přichází?

- Pro město a obyvatele u řeky: varování před povodní s předstihem 12–24 h místo 4 h.
- Pro kraj (DCÚK): jak se mění Labe za 20 let, povodně i sucho.

## Data

| | Co obsahuje | Co z toho jde |
|---|---|---|
| **Balíček od pořadatelů** | 28 stanic v kraji, 2024–9/2026. Jen 4 na Labi: Litoměřice, Ústí, Děčín, Hřensko. Do 2025 po hodinách, 2026 po 10 minutách | Předpověď jen na 4–5 h (nejvýš proti proudu je Ústí). Jediná povodeň (9/2024). Teplota vody, přítoky |
| **Přidaná otevřená data ČHMÚ** (zdarma, staženo, `src/stahni_chmu_hydro.py`) | hodinový stav a průtok 2002–2025: Praha-Chuchle a Vraňany (Vltava), Kostelec nad Labem, Mělník, Ústí, Děčín | předpověď na 12–24 h, 31 povodní nad 1. stupněm (7 nad 3. stupněm), test na povodních, které model neviděl, vývoj za 20 let |
| **Co by ještě pomohlo** (neověřeno, jestli je volně) | srážky v povodí a jejich předpověď, vypouštění přehrad na Vltavě (Orlík, Slapy), historie oficiálních předpovědí ČHMÚ | předpověď dál než den a srovnání s ČHMÚ |

Kupovat se nemusí nic. Bez srážek ale nejde předpovídat dál než zhruba den: voda, která do Děčína přijde za dva dny, ještě nespadla nebo je v potocích, které neměříme.

## Co z dat umíme (ne jen povodně)

### 1. Předpověď stavu v Děčíně na 12 a 24 h (hlavní část)

- Voda do Děčína dorazí (největší korelace změn průtoku): z Ústí za 4 h, z Kostelce za 9 h, z Mělníka za 12 h, z Vraňan za 13 h, z Prahy za 17 h.
- Model: stav a průtok v Děčíně teď, průtok v Ústí, průtok v Mělníku teď a před 6–24 h, průtok v Praze teď a před 6–12 h.

### 2. Odkud voda při povodni přichází

Podíl Vltavy na vrcholu povodně v Mělníku:

| Povodeň | Vrchol v Mělníku | Vltava | Horní Labe | Podíl Vltavy |
|---|---|---|---|---|
| 4/2006 | 2 410 m³/s | 1 440 | 956 | 60 % |
| 1/2011 | 1 580 m³/s | 924 | 645 | 59 % |
| 6/2013 | 3 630 m³/s | 3 030 | 743 | 80 % |
| 9/2024 | 1 720 m³/s | 953 | 750 | 56 % |

Povodeň 2013 byla hlavně Vltava. Pro Děčín z toho plyne, že klíčová stanice je Praha.

### 3. Sucho a klesající hladina

- Počet dní, kdy byla hladina v Děčíně pod 150 cm: 2004 jen 8, 2015 181, 2018 236, 2025 263.
- Pozor na interpretaci. Při stejném průtoku 150–170 m³/s byla hladina v roce 2004 159 cm, v roce 2025 jen 143 cm. Hladina tedy klesá i při stejném množství vody. Část „sucha“ proto není méně vody, ale něco se změnilo v korytě nebo u vodočtu. Domněnka: prohlubování dna. Otázka na mentora.
- Skutečně suchá léta podle průtoku: průměr VI–IX kolem 100 m³/s v letech 2015, 2018, 2019, 2023 a 2025, proti 504 m³/s v roce 2013.
- Využití: lodní doprava na Labi potřebuje určitou hloubku. Jakou, je potřeba zjistit.

### 4. Jak rychle putuje vlna

Z Mělníka do Děčína 12 h při malém průtoku, 13 h při velkém. Při malém průtoku je ale souvislost slabá (korelace 0,08), změny jsou malé a ruší je jezy.

## Jak dobré to bude

**Test 2017–2025, model se učil na 2003–2016** (lineární regrese bez ladění):

| | +12 h | +24 h |
|---|---|---|
| celkově, model / „bude jako teď“ | 7,8 / 8,0 cm | 10,8 / 11,2 cm |
| voda nad 1. stupněm povodňové aktivity (1 061 h), model / „jako teď“ | 12,0 / 22,5 cm | 24,7 / 44,6 cm |

**Povodeň 2013, kterou model při tréninku neviděl:**

| | +12 h | +24 h |
|---|---|---|
| chyba model / „jako teď“ | 22 / 34 cm | 37 / 68 cm |
| vrchol skutečně / model | 1 072 / 1 106 cm | 1 072 / 1 179 cm |
| varování před 3. stupněm (560 cm) | 11 h předem | 18 h předem |

**Kolik povodní máme** (Děčín 11/2004–2025, po vyřazení chybných hodnot):

| Stupeň povodňové aktivity | Povodní | Hodin | Podíl času |
|---|---|---|---|
| 1. (400 cm) | 31 | 5 434 | 2,9 % |
| 2. (490 cm) | 14 | 1 904 | 1,0 % |
| 3. (560 cm) | 7 | 1 073 | 0,6 % |

Povodně nad 3. stupněm: 3/2005 (624 cm), 4/2006 (875), 8/2010 (560), 1/2011 (730), 6/2013 (1 072), 12/2023 (624), 9/2024 (649).

**Každá velká povodeň zvlášť** (+24 h). Model se pokaždé učil bez ±20 dní kolem povodně a testoval se na týdnu před vrcholem a 5 dnech po něm:

| Povodeň | Vrchol | Chyba model / „jako teď“ | Vrchol podle modelu | Varování před 3. stupněm |
|---|---|---|---|---|
| 4/2006 | 875 | 25 / 53 cm | 881 | 23 h předem |
| 8/2010 | 560 | 29 / 45 cm | 612 | 29 h předem |
| 1/2011 | 730 | 20 / 48 cm | 727 | 12 h předem |
| 6/2013 | 1 072 | 60 / 99 cm | 1 179 | 18 h předem |
| 12/2023 | 624 | 25 / 44 cm | 631 | 13 h předem |
| 9/2024 | 649 | 29 / 64 cm | 690 | 25 h předem |

Povodeň 3/2005 nejde otestovat, chybí data ze stanic nad krajem.

**Proč stačí i málo povodní:** model se neučí „povodně“, ale to, jak voda putuje po řece. To se děje každou hodinu všech 20 let a povodeň je jen totéž s větším množstvím vody. Proto lineární model vyšel na všech šesti povodních, které neviděl.

**Proč ne LightGBM:** u povodně 2013 předpověděl vrchol jen 823 cm místo 1 072. Rozhodovací stromy neumí předpovědět víc, než kdy viděly v tréninku. Lineární model ano. Tady je jednodušší model doopravdy lepší a porota to ocení.

**Co z toho plyne:**
- Za běžného stavu se řeka skoro nehýbe a „jako teď“ je skoro stejně dobré. Model pomáhá hlavně při velké vodě, kdy na předpovědi záleží.
- Při všech šesti velkých povodních měl model chybu zhruba poloviční a varoval 12–29 h předem.
- Na 24 h vrchol obvykle mírně přestřelí, u 2013 o 10 %. Na varování to nevadí, na přesnou výšku ano.
- Na přesnost u extrémních povodní (nad 8 m) máme jen 2013, tam je závěr nejistý.
- ČHMÚ s profesionálními modely a srážkami nepřekonáme a netvrdíme to.

## Přidaná hodnota

Porota se nejspíš zeptá: „ČHMÚ už předpovědi dělá, k čemu je váš model?“ Odpověď:

1. **Je průhledný.** Jedna rovnice: „za 12 h přijde do Děčína to, co teď teče Mělníkem“. Každý pochopí, proč model předpovídá, co předpovídá.
2. **Analýza za 20 let:** odkud přicházejí povodně, jak se mění sucho a že hladina klesá i při stejném průtoku.
3. **Ukázka, kolik se dá zjistit jen z otevřených dat** zdarma.

## Model a vyhodnocení

- **Cíl:** stav v Děčíně (cm) za 6, 12 a 24 h a z něj stupeň povodňové aktivity (1. 400, 2. 490, 3. 560 cm).
- **Postup modelů:** „bude jako teď“, pak lineární regrese, pak LightGBM. Složitější jen když výrazně pomůže.
- **Metriky:**
  - průměrná chyba (cm) celkově a zvlášť nad 1. stupněm,
  - správně určený stupeň povodňové aktivity,
  - předstih varování v hodinách.
- **Ověření:**
  - časové rozdělení (trénink 2003–2016, validace 2017–2020, test 2021–2025),
  - k tomu vynechané povodně: model se pokaždé učí bez jedné povodně (2006, 2011, 2013, 2024) a na ní se testuje.
- **Vysvětlení:** váhy lineárního modelu a SHAP. Která stanice a jaké zpoždění rozhoduje.

## Aplikace a mapa

- Mapa řeky od Prahy po Hřensko se stanicemi, barva podle stupně povodňové aktivity.
- Přehrání povodně 2013 hodinu po hodině: vlna putuje z Prahy přes Mělník do Děčína.
- Panel Děčín: graf stavu, předpověď na 12 a 24 h a pásma stupňů povodňové aktivity.
- Graf „odkud voda přišla“ u každé povodně.

## Prezentace (15 min)

1. Děčín a povodně 2002, 2013, 2024 (fotka, výška hladiny).
2. Otázka: dá se den dopředu říct, co přijde?
3. Data: co bylo v balíčku a proč nestačilo (jedna povodeň, žádné stanice nad krajem). Co jsme přidali a odkud.
4. Fyzika: voda putuje, Praha 17 h, Mělník 12 h, Ústí 4 h.
5. Model a výsledky. Za běžného stavu nic moc, při povodni poloviční chyba, 2013 varování 18 h předem.
6. Odkud povodně přicházejí (2013 80 % Vltava).
7. Sucho a záhada klesající hladiny při stejném průtoku.
8. Demo: přehrání 2013.
9. Limity: bez srážek ne dál než den, vrchol přestřelí, ČHMÚ je lepší.

## Rozdělení práce (návrh)

| Kdo | Co |
|---|---|
| Ondra | rozdělení a vyhodnocení, vynechané povodně, kontrola výsledků |
| Dan | modely od baseline po LightGBM, SHAP |
| Honza | mapa a přehrávání povodně |
| Tobias | příběh, analýza „odkud voda“ a sucho, grafy |

**Do 21:00 minimum:** data všech stanic v jedné tabulce, baseline a lineární model na 12 a 24 h s vyhodnocením, mapa se stanicemi.

## Rizika

- **Opíráme se o data mimo balíček.** Pořadatelé je dovolili, ale v prezentaci musí být jasně, odkud jsou.
- **Za běžného stavu je zlepšení malé.** Prezentace musí ukazovat povodně a vysvětlit proč.
- **Velkých povodní je málo.** 7 nad 3. stupněm, extrémní jen 2013. Na předpověď to stačí (model se učí putování vody), ale přesnost u extrémů stojí na jednom případu.
- **Chyby v datech:** 6.–7. 2. 2006 je v Děčíně zapsaná hladina 1 019 cm při průtoku 120 m³/s, a Ústí přitom ukazuje 161 cm. Je to chyba měření (25 hodin), vyřadit. Hledat podobné: hladina, která nesedí s průtokem, a skoky o víc než 1 m za hodinu.
- **Data 2026 jsou z balíčku po 10 minutách**, historie ČHMÚ po hodinách. Sjednotit.

## Srovnání s ovzduším

| | Labe | Ovzduší |
|---|---|---|
| Data z balíčku stačí? | ne, potřeba přidat ČHMÚ (hotovo) | ano |
| Originalita | vysoká | nízká, víc týmů |
| Jasný výsledek | ano: při povodni poloviční chyba, varování 18 h předem | ano: model vs. „jako teď“ na 6–24 h |
| Šíře | povodně, odkud voda, sucho, rychlost vlny | předpověď, otisky zdrojů, inverze, události |
| Místní příběh | Děčín, povodně | smog v kraji |
| Hlavní riziko | zlepšení jen při velké vodě | splyneme s ostatními |
