# Porozumění

Podklad pro prezentaci a otázky poroty: úloha a výsledky našimi slovy. Kdo něco pochopí nebo dostane odpověď od mentora, doplní příslušnou sekci.

## Úloha vlastními slovy

Co řešíme, pro koho a proč na tom záleží. Dvě tři věty, které řekne kdokoli z nás.

## Pojmy

Odborné výrazy ze zadání a z našeho řešení, vysvětlené jednoduše.

## Proč tahle metoda

Co jsme zvolili, s čím jsme to srovnávali a proč jsme jiné možnosti nevzali.

**Proč zpoždění 0–36 h a horizonty 12, 24, 36 h** (Labe):
- Doba putování vody do Ústí se liší podle stanice a hlavně podle povodně. Z Vraňan šel vrchol jednou 12 h, jindy 45 h. Jedno pevné číslo na stanici by bylo špatně, proto model dostane od každé stanice průtok před 0, 3, 6, 12, 18, 24 a 36 h a sám si najde, které zpoždění je důležité. Z jeho vah pak dobu putování vyčteme.
- Kolik zpoždění je potřeba: nejvzdálenější stanice (Beroun) je od Děčína asi 40 h, nejkratší horizont je 12 h. Voda, která do Děčína přijde za 12 h, prošla Berounem asi před 28 h. Nejstarších 36 h to pokryje i s rezervou na to, že se doba mezi povodněmi mění.
- Proč ne každou hodinu: zpoždění blízko sebe nesou skoro stejnou informaci, jen by přibyly sloupce (444 místo 84). Doba putování navíc kolísá o víc hodin, než je rozestup.
- Proč nejvýš 36 h dopředu: voda, která do Děčína přijde za víc než 40 h, ještě neprotekla žádnou naší stanicí. Je v potocích nebo ještě nespadla. Na to by byly potřeba srážky.
- Pro horizont h pomáhá hlavně stanice, odkud voda teče déle než h. Proto čím dál dopředu, tím dál proti proudu se musíme dívat.

**Proč lineární regrese (Ridge)** (Honza):
- Předpověď je vážený součet vstupů, každá stanice a zpoždění má jednu váhu. Vybrali jsme ji, protože na vynechaných povodních vyšla nejlíp a celá se dá ukázat na jednom obrázku (`docs/grafy/ridge_vahy_decin.png`). „Ridge“ znamená, že se velké váhy mírně penalizují; na našich datech na tom nezáleží (alpha 0,1 až 10 dává stejný výsledek).
- Odmocnina z průtoků: hladina roste s průtokem zhruba jako odmocnina (měrná křivka), takže lineárnímu modelu odmocnina průtoku sedí lépe. Na hladinu ji nedáváme, zkazila vrchol 2006 o metr.
- Učit „změnu hladiny“ místo hladiny je u lineárního modelu totéž (váha u hladiny teď se posune o 1), u stromů ne.

## Jak číst výsledky

Co znamená naše metrika, jaké číslo je dobré a proč, s čím ho srovnáváme.

## Co model umí a co ne

Limity, na jakých datech by selhal, co jsme nestihli.

- Umí předpovědět na 12 až 24 h z vody, která už teče proti proudu. Neumí déšť, který teprve spadne: proto je 36 h dvakrát horší než 24 h a dál než den a půl by to bez srážek nešlo.
- Vrcholy vyšší, než jaké viděl v tréninku, podhodnocuje (2006: o 20 cm na 875 cm). Lineární model aspoň extrapoluje, stromy ne.
- Doba putování vody se mezi povodněmi mění (Mělník → Ústí 6 až 11 h), model má jednu průměrnou.
- Archivní data ČHMÚ jsou zpětně ověřená. V provozu jsou průtoky při povodni předběžné a chodí se zpožděním, takže naše čísla jsou proti provozu spíš optimistická. Srovnání modelů mezi sebou to neovlivní.

## Otázky pro mentory a odpovědi

- Hodinové hodnoty ČHMÚ jsou průměry za hodinu a zveřejňují se se zpožděním. S jakým zpožděním jsou v provozu dostupné? Model bere hodnotu z času t jako známou v čase t; v provozu by se předstih zkrátil zhruba o to zpoždění.

## Otázky, které čekáme od poroty

- Proč lineární model a ne neuronová síť? Na povodních, které model neviděl, vyšel nejlíp, nemá se na čem přeučit a každou váhu vysvětlíme fyzikálně.
- Proč jsou některé váhy záporné? Model odečítá hodnotu před pár hodinami od hodnoty teď, tedy počítá trend (stoupá, nebo klesá).
- Proč model pro Ústí používá i Děčín, který je po proudu? Hladina v Děčíně je tatáž voda změřená podruhé o 4 h později, model si tím vyhlazuje šum měření. Je to hodnota známá v čase předpovědi, ne informace z budoucnosti.
- Proč nestačí sledovat, jestli voda stoupá? Pravidlo „stoupla o 40 cm za 6 h“ se plete pětkrát z šesti (`docs/NAPAD_LABE.md`). Model vidí vodu, která do Děčína teprve teče.
