# Prezentace: 7 minut mluvení, 5 minut otázek

Deck je v Canvě: https://www.canva.com/d/xVAIR8am2CrRslj (9 slajdů, 1920 x 1080, tmavý „povodňový pult“). Poznámky řečníka s časem a textem jsou u každého slajdu přímo v Canvě. Podklady: grafy `docs/grafy/slajdy/`, snímky aplikace a mapy `docs/grafy/`. Porota z FJFI, DCÚK a firem; hodnotí splnění (10), postup (10), odbornost (20) a prezentaci (10). Pořadí je pevné: ukázat výsledek, vysvětlit, dokázat, přiznat limity.

## Myšlenka a vizuální jazyk

Jedna věta, která drží celou prezentaci: **„Co teče Prahou teď, je zítra v Děčíně.“** Vizuálně ji nese **linie řeky**: tenká modrá čára Vltavy a Labe od Prahy po Děčín (z `data/external/reky.geojson`), velká na titulu, malá vpravo dole na každém dalším slajdu; rozsvícená tečka ukazuje, o které stanici se mluví (Praha modrá, Mělník oranžová, Děčín červená).

- Barvy jako v aplikaci: pozadí #111820, karty #1a232d, voda #3aa0c9 a #7cc6e4, stupně #f2c437 / #ef6c00 / #c62828, text #ffffff a #c8d1d9, tlumený #8b98a5, „bude jako teď“ #666666. Nic jiného.
- Písmo: nadpisy a čísla Sofia Sans Extra Condensed (náhrada Barlow Condensed nebo Oswald), text Schibsted Grotesk (náhrada Archivo). Canva přes API rodinu písma nastavit neumí, viz „Co dodělat ručně“.
- Každý slajd má jedno tvrzení jako nadpis, jedno velké číslo nebo jeden obrázek, nejvýš tři věty textu. Žádné odrážkové stěny, ikony z knihoven, stock fotky ani přechody.
- Grafy jako bílé karty vlevo, čísla a text vpravo. Snímky mapy přes celý slajd se ztmavením.
- Patička: „Data ČHMÚ · otevřená data 2006–2025“ a zdroje map.

## Slajdy a čas (celkem 7:00)

| # | Čas | Nadpis (tvrzení) | Obsah a podklad | Kdo |
|---|---|---|---|---|
| 1 | 0:00 | Kolik vody přiteče do Děčína | titul přes celý slajd: `docs/grafy/mapbox2_porovnani.png` ztmavený, linie řeky Praha–Děčín, věta „Co teče Prahou teď, je zítra v Děčíně.“, jména týmu | Tobias |
| 2 | 0:20 | Model hlásil 3. stupeň v Děčíně 27 hodin předem | `slajdy/boris_2024.png`, velké „27 h“; varování 14. 9. 2024 11:00, voda 15. 9. 14:00; test 2021–2025 o 55 % menší chyba | Tobias |
| 3 | 0:50 | Děčín dnes vidí 4 hodiny dopředu. My dáváme 24. | velká čísla 4 h (šedě) a 24 h (modře); Ústí je 4 h proti proudu, Praha den; pro koho: komise, lidé u řeky; metrika = stupeň a hodiny předstihu | Tobias |
| 4 | 1:30 | S daty z balíčku by model byl horší než nic | `slajdy/kolik_dat.png`; 20 let · 12 stanic · 175 320 hodin; dělení trénink / 4 povodně / test 2021–2025, 20 dní kolem povodní vynecháno | Ondra |
| 5 | 2:15 | Největší váhu má Praha teď: voda z Prahy je v Děčíně za den | `slajdy/vahy_decin_24h.png`; 98 vstupů, odmocnina průtoků, záporné váhy = trend, na 12 h Mělník | Honza |
| 6 | 3:00 | Čtyři modely na stejném úkolu, vyhrál nejjednodušší | `slajdy/srovnani_modelu.png`, velké „−55 %“ (22,4 proti 50,2 cm); co nepomohlo: srážky 17,4, váhy 18,5, TCN 20,3, síť 17,8; rozmezí 9 z 10 a 8 z 10; 4 povodně, 0 propásnutých, 0 planých | Ondra, Dan |
| 7 | 3:45 | Živé demo (2 minuty) | pozadí `docs/grafy/mapbox2_animace.png` (nahradit videem); 1) Teď 15. 1. 2011 9:00: 646 → 738 cm, 3. stupeň, rozmezí 712–794; 2) Dnešek: živá data ČHMÚ + oficiální předpověď; 3) Mapa: vybrat povodeň, Přehrát, předpověď × skutečnost, rozliv v ulicích | Honza |
| 8 | 5:45 | Předpověď v centimetrech znamená ulice a domy | `docs/grafy/mapbox_decin.png`; rozliv z terénu ČÚZK: 167 ha náš, 183 ha úřední, 165 ha společných; není to hydraulický model, shoda 82–90 % | Honza |
| 9 | 6:20 | Co model neumí a co bychom dělali dál | čtyři karty: 36 h dvakrát horší, vrcholy nad trénink (Boris −38 cm), rozliv statický, provozní data se zpožděním; co dál: doba putování podle průtoku, živá data, hodinové srážky; „Děkujeme. Otázky?“ | Dan, Tobias |

Demo má pevné 2 minuty, nacvičené klik po kliku. Když se zadrhne, pustí se záložní video a jede se dál. Čísla v tabulce jsou čas od začátku.

## Otázky poroty (5 minut)

Odpovědi na 20 otázek jsou v `docs/STRATEGIE.md` (větev `honza-vyzkum`) a rozbory v `docs/DENIK.md`. Ke každému slajdu patří jedna otázka, kterou si řečník nacvičí:

- slajd 4: „Proč nestačil balíček?“ a „Proč nedělíte náhodně?“ (sousední hodiny jsou skoro stejné, náhodné dělení by výsledek falešně vylepšilo)
- slajd 5: „Proč záporné váhy?“ (model počítá trend) a „Proč odmocnina?“ (hladina roste s průtokem zhruba jako odmocnina)
- slajd 6: „Proč ne neuronová síť?“ (17,8 proti 17,1, a nejde vysvětlit) a „A co když zaprší?“ (déšť už teče v řekách, průtoky ho vidí dřív)
- slajd 6: „Jak moc se pletete?“ (rozmezí od–do, 9 z 10 a 8 z 10)
- slajd 8: „To je váš hydraulický model?“ (ne, výška terénu proti výšce hladiny, ověřeno proti úřední mapě)
- slajd 9: „Co když přijde větší povodeň než 2013?“ (podhodnotí, Boris o 38 cm; stupeň ale hlásí včas)

## Co dodělat ručně v Canvě

1. Písma: na každém slajdu vybrat vše (Ctrl+A) a nastavit nadpisy a velká čísla na Sofia Sans Extra Condensed, text na Schibsted Grotesk. Po přechodu na kondenzované písmo zvětšit nadpisy a čísla o 10 až 20 %, textu zůstane místo.
2. Slajd 7: vyměnit pozadí za video animace povodně (`docs/grafy/video_povoden.mp4`, až bude natočené), ztmavení nechat.
3. Přechody vypnout, animace prvků žádné.
4. Export do PDF jako záloha bez videa; na flashku i s videem.
5. Dva nácviky s časomírou: sobota 11:00 a 13:00; na druhém Ondra hraje porotu.
