# Porozumění

Podklad pro prezentaci a otázky poroty: úloha a výsledky našimi slovy. Kdo něco pochopí nebo dostane odpověď od mentora, doplní příslušnou sekci.

## Úloha vlastními slovy

Co řešíme, pro koho a proč na tom záleží. Dvě tři věty, které řekne kdokoli z nás.

## Pojmy

Odborné výrazy ze zadání a z našeho řešení, vysvětlené jednoduše.

## Proč tahle metoda

Co jsme zvolili, s čím jsme to srovnávali a proč jsme jiné možnosti nevzali.

- Lineární regrese (Ridge): předpověď je vážený součet vstupů, každá stanice a zpoždění má jednu váhu. Vybrali jsme ji, protože na vynechaných povodních vyšla nejlíp a celá se dá ukázat na jednom obrázku (`docs/grafy/ridge_vahy_decin.png`). „Ridge“ znamená, že se velké váhy mírně penalizují; na našich datech na tom nezáleží (alpha 0,1 až 10 dává stejný výsledek).
- Odmocnina z průtoků: hladina roste s průtokem zhruba jako odmocnina (měrná křivka), takže lineárnímu modelu odmocnina průtoku sedí lépe. Na hladinu ji nedáváme, zkazila vrchol 2006 o metr.
- Učit „změnu hladiny“ místo hladiny je u lineárního modelu totéž (váha u hladiny teď se posune o 1), u stromů ne.

## Jak číst výsledky

Co znamená naše metrika, jaké číslo je dobré a proč, s čím ho srovnáváme.

## Co model umí a co ne

Limity, na jakých datech by selhal, co jsme nestihli.

- Umí předpovědět na 12 až 24 h z vody, která už teče proti proudu. Neumí déšť, který teprve spadne: proto je 36 h dvakrát horší než 24 h a dál než den a půl by to bez srážek nešlo.
- Vrcholy vyšší, než jaké viděl v tréninku, podhodnocuje (2006: o 20 cm na 875 cm). Lineární model aspoň extrapoluje, stromy ne.
- Doba putování vody se mezi povodněmi mění (Mělník → Ústí 6 až 11 h), model má jednu průměrnou.

## Otázky pro mentory a odpovědi

- Hodinové hodnoty ČHMÚ jsou průměry za hodinu a zveřejňují se se zpožděním. S jakým zpožděním jsou v provozu dostupné? Model bere hodnotu z času t jako známou v čase t; v provozu by se předstih zkrátil zhruba o to zpoždění.

## Otázky, které čekáme od poroty

- Proč lineární model a ne neuronová síť? Na povodních, které model neviděl, vyšel nejlíp, nemá se na čem přeučit a každou váhu vysvětlíme fyzikálně.
- Proč jsou některé váhy záporné? Model odečítá hodnotu před pár hodinami od hodnoty teď, tedy počítá trend (stoupá, nebo klesá).
- Proč model pro Ústí používá i Děčín, který je po proudu? Hladina v Děčíně je tatáž voda změřená podruhé o 4 h později, model si tím vyhlazuje šum měření. Je to hodnota známá v čase předpovědi, ne informace z budoucnosti.
- Proč nestačí sledovat, jestli voda stoupá? Pravidlo „stoupla o 40 cm za 6 h“ se plete pětkrát z šesti (`docs/NAPAD_LABE.md`). Model vidí vodu, která do Děčína teprve teče.
