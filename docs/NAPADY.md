# Tři pojetí úlohy Ovzduší

Tři úplně odlišné přístupy. Každý se ptá na něco jiného, používá jiný druh strojového učení a je pro jiného uživatele. Mapa se hodí do všech tří jako způsob, jak výsledek ukázat. Rozdíl je v tom, jakou otázku mapa zodpovídá.

| | A: Smogová předpověď | B: Odkud smog je | C: Chytrá měřicí síť |
|---|---|---|---|
| Otázka | Jaké bude ovzduší zítra? | Proč je špatné a co ho způsobuje? | Měříme správně a dost? |
| Druh ML | učení s učitelem, předpověď do budoucna | bez učitele, hledání skupin (shlukování) | učení s učitelem, odhad jedné stanice z ostatních |
| Pro koho | obyvatelé | kraj, úředníci (DCÚK) | ČHMÚ, kraj při plánování |
| Výstup | 3D mapa s předpovědí a varováním | „otisky“ zdrojů znečištění po stanicích a dnech | mapa nenahraditelných stanic, doplněné díry v datech |
| Originalita | nízká, udělá to víc týmů | vysoká | vysoká |

## Co mají všechny společné

- Vyčištěná data:
  - platná kvalita je 8, 9, 10 nebo 11,
  - kódy −5000 převést na chybějící hodnotu,
  - čas převést z UTC na místní.
- Rozdělení v čase:
  - trénink 1/2024–6/2025,
  - validace 7–12/2025,
  - test 2026 jednou na konci (jen neověřená data).
- Vždy srovnání s jednoduchým základem.

## A: Smogová předpověď v 3D mapě

**Otázka:** jaká bude koncentrace PM10 za 6 a 24 hodin a bude zítra překročen denní limit 50 µg/m³?

**ML:**
- Předpověď z hodnot za poslední hodiny, ze sousedních stanic, z hodiny a měsíce, případně z počasí.
- Postup modelů: „bude jako teď“, pak lineární model, pak LightGBM.
- Laťka: „bude jako teď“ má chybu 9,3 / 10,6 µg/m³ na 6 / 24 h.
- Varování před limitem: limit byl překročen jen ve 368 z 10 942 stanice-dní. Úspěšnost je tu zavádějící, měříme záchyt a přesnost varování.

**Výstup:**
- 3D mapa (Streamlit + pydeck): sloupce na stanicích, filtry látka / čas / naměřeno / +6 h / +24 h, semafor varování.
- Po kliknutí na stanici graf s předpovědí a tři hlavní důvody (SHAP).
- Přehrávání historie, kde porota hned vidí, jestli předpověď vyšla.

**Body:** nejsilnější vizuálně, jasná metrika.

**Riziko:** stejné téma bude mít víc týmů a mapa sežere hodně času.

## B: Odkud smog je (otisky zdrojů)

**Otázka:** co v Ústeckém kraji smog způsobuje? Topení, doprava, průmysl, nebo něco, co přijde odjinud?

**Princip:** každý zdroj zanechává v datech „otisk“ v podobě poměru látek a denního průběhu.
- Spalování (topení, ohňostroje) dává hodně jemných částic, takže poměr PM2,5/PM10 je vysoký.
- Prach (vítr, saharský písek, stavby) dává hrubé částice, poměr je nízký.
- Doprava dává ranní špičku NO₂.
- Uhelné elektrárny a průmysl dávají SO₂.
- Událost zasáhne všechny stanice najednou, když přichází zdaleka. Jediná stanice ukazuje na místní zdroj.

**Už ověřeno na datech** (medián poměru PM2,5/PM10):

| Situace | Poměr | Co to znamená |
|---|---|---|
| zima (XII–II) | 0,78 | jemné částice ze spalování, topná sezóna |
| léto (VI–VIII) | 0,54 | víc hrubého prachu |
| Silvestr, 1. 1. 2025 0–3 h | 0,91 | ohňostroje, skoro čistě jemné částice |
| 30.–31. 3. 2024, nejvyšší PM10 v celých datech | 0,39 | hrubé částice, sedí na saharský prach (ověřit ve zprávách ČHMÚ) |

**ML:**
- Každý den na každé stanici popsat několika čísly: poměry látek, denní průběh, kolik stanic je zasaženo zároveň.
- Pak shlukování (k-means): model sám najde typy dní, třeba „zimní topení s inverzí“, „letní ozon“, „dopravní špička“, „dálkový přenos“ nebo „čistý větrný den“.
- Každý typ pojmenujeme podle toho, čím se liší.
- Ověření: známé události musí padnout do správné skupiny. Silvestr do spalování, březen 2024 do prachu, topná sezóna do topení.

**Výstup:**
- kalendář, kde každý den má barvu podle typu,
- mapa stanic s podílem typů,
- závěr pro kraj: „v Lomu a Mostě rozhoduje topení a místní zdroje, v Ústí doprava…“ (to je zatím odhad, výsledek ukáže, jak to opravdu je).

**Body:** silné v odbornosti i porozumění. Každý krok je vysvětlitelný fyzikou a porota uvidí, že datům rozumíme. Plní body zadání „vzory“, „podobné polutanty“ a „neobvyklé události“.

**Riziko:**
- U shlukování neexistuje „správná odpověď“, obhajujeme ho jen na známých událostech.
- Pojmenování skupin musí vycházet z dat, ne z toho, co chceme vidět.
- Zadání varuje, že souvislost neznamená příčinu. Mluvíme o „otiscích“, ne o dokázaných zdrojích.

## C: Chytrá měřicí síť (virtuální stanice)

**Otázka:**
- Které stanice jsou nenahraditelné a které by šly odhadnout z ostatních?
- Dá se dopočítat, co se na stanici neměří nebo co vypadlo?

**ML:**
- Pro každou stanici model, který odhadne její PM10 z ostatních stanic ve stejnou hodinu.
- Ověřujeme na datech, která model neviděl, a pokaždé jednu stanici vynecháme.
- Kde je chyba malá, stanice nese málo nové informace. Kde je velká, měří něco, co jinde není.

**Už ověřeno** (jednoduchý lineární model, validace 7–12/2025):

| Stanice | Chyba odhadu z ostatních | Průměr PM10 | Co to znamená |
|---|---|---|---|
| Ústí-Všebořická, Ústí-město, Štětí | kolem 5 µg/m³ | 17 | jdou dobře odhadnout ze sousedů |
| Lom | 11,1 µg/m³ | 24 | nejšpinavější a zároveň nejhůř odhadnutelná, má místní zdroj |
| Rudolice v Horách | 4,5 µg/m³ | 8 | průměr ostatních stanic by se spletl o 10, stanice je nad inverzí a chová se jinak |

**Další použití:**
- **Virtuální PM2,5** pro Chomutov, Rudolice a Ústí-město, kde se PM2,5 neměří.
- **Doplnění děr:** u PM10 je nejdelší výpadek až 7 dní.
- **Kontrola neověřených dat 2026:** když stanice náhle ukazuje něco jiného, než odpovídá sousedům, je to podezřelé.

**Výstup:**
- mapa sítě: velikost kruhu ukazuje, jak je stanice nenahraditelná,
- graf „virtuální vs. skutečná stanice“,
- doporučení, kde by síť potřebovala další stanici.

**Body:** velmi poctivé ověření a jednoduché modely, plní bod zadání „porovnat chování stanic“. Praktické pro DCÚK, protože se týká kvality dat a nákladů na síť.

**Riziko:**
- Pro obyvatele méně poutavé, příběh se musí dobře vyprávět.
- Stanic s PM10 je jen 11, takže závěry o síti stojí na malém vzorku.

## Doporučení

**Já bych šel do B.** Nejlíp odpovídá hodnocení, kde je nejvíc bodů za odbornost a porozumění:
- Celé to stojí na jednoduchých věcech, které umí vysvětlit každý z nás.
- Už teď máme ověřená „aha“ místa: Silvestr 0,91, saharský prach 0,39, zima proti létu.
- Málokterý jiný tým to udělá.

A je nejbezpečnější a nejefektnější, ale budeme jedni z mnoha. C je nejpoctivější metodicky, ale nejhůř se prodává.

## Otázky pro mentora

- Kde leží meteostanice (kódy `0-20000-0-114xx`)? Pro B by pomohl směr větru, pro A počasí.
- Smíme přidat další otevřená data, třeba zprávy ČHMÚ o epizodách?
- Je pro zadavatele zajímavější předpověď, vysvětlení příčin, nebo stav měřicí sítě?
