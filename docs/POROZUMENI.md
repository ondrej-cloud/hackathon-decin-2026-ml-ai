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

## Jak číst výsledky

Co znamená naše metrika, jaké číslo je dobré a proč, s čím ho srovnáváme.

## Co model umí a co ne

Limity, na jakých datech by selhal, co jsme nestihli.

## Otázky pro mentory a odpovědi

## Otázky, které čekáme od poroty
