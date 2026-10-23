# Prezentace: plán slajdů a vizuální jazyk

15 minut, 4 lidi, porota z FJFI, DCÚK a firem. Staví se v Canvě (Honza), obsah z `docs/`, grafy z `docs/grafy/slajdy/`, snímky aplikace z `docs/grafy/`. Pořadí je pevné: ukázat, vysvětlit, dokázat, přiznat limity.

## Myšlenka a vizuální jazyk

Jedna věta, která drží celou prezentaci: **„Co teče Prahou teď, je zítra v Děčíně.“** Vizuálně ji nese **linie řeky**: tenká modrá čára Vltavy a Labe od Prahy po Děčín (z `data/external/reky.geojson`), která se na každém slajdu posune a rozsvítí další stanici. Na titulním slajdu začíná v Praze, na posledním končí v Děčíně.

- Tmavý povodňový pult jako aplikace: pozadí #111820, panely rgba(15,20,25,0.92), voda #3aa0c9 (světlejší #7cc6e4), stupně žlutá #f2c437, oranžová #ef6c00, červená #c62828, šedá #666666 pro „bude jako teď“. Žádné jiné barvy.
- Písmo: čísla a nadpisy Sofia Sans Extra Condensed (v Canvě ověřit; náhrada Barlow Condensed nebo Oswald), text Schibsted Grotesk (náhrada Archivo). Čísla velká, nejmíň 120 bodů, s desetinnou čárkou.
- Každý slajd má jedno tvrzení jako nadpis, nejvýš 12 slov textu a jedno číslo nebo obrázek. Žádné odrážkové stěny, žádné ikony z knihovny, žádné stock fotky, žádné přechody (jen posun linie řeky).
- Pozadí snímků z aplikace a mapy přes celý slajd se ztmavením dolů, text vlevo dole v panelu.
- Patička: číslo slajdu a „Data ČHMÚ, otevřená data“. U grafů zdroj a podmínky pod grafem (už jsou v obrázcích).

## Slajdy

| # | Čas | Nadpis (tvrzení) | Obsah a podklad | Kdo |
|---|---|---|---|---|
| 1 | 0:00 | Kolik vody přiteče do Děčína | titul přes celý slajd: `docs/grafy/mapbox2_porovnani.png` ztmavený, linie řeky v Praze, jména týmu | Tobias |
| 2 | 0:15 | (bez nadpisu) | video animace povodně Boris 2024 v mapě (30 s, nahrát z aplikace, bez komentáře čísel); pak jedna věta: „14. 9. 2024 v 11:00 model hlásí 3. stupeň. Voda přišla 15. 9. ve 14:00.“ | Tobias |
| 3 | 1:00 | Dnes vidí Děčín 4 hodiny dopředu, my dáváme 24 | pro koho (povodňová komise, lidé u řeky), „bude jako teď“ propásne každou povodeň; číslo 4 h → 24 h | Tobias |
| 4 | 2:30 | S daty z balíčku by model byl horší než nic | `slajdy/kolik_dat.png`; 2 roky a jen kraj = 45 cm, 20 let a 12 stanic = 17 cm | Ondra |
| 5 | 3:30 | 20 let, 12 stanic, 175 320 hodin | mapa stanic `docs/grafy/mapbox_povodi.png`, tři velká čísla, zdroj ČHMÚ; kontrola dat (shoda s balíčkem na cm, bilance vody) jednou větou | Ondra |
| 6 | 4:30 | Testujeme na povodních, které model neviděl | pruh času 2006–2025: trénink / 4 povodně a 2019–20 / test 2021–25; „20 dní kolem povodní vynecháno“; dvě pasti, které jsme našli (interpolace z budoucnosti, denní srážky za následující den) | Ondra |
| 7 | 5:30 | Model vidí jen to, co je v tu chvíli změřené | 98 vstupů jako mřížka 14 řad × zpoždění 0–36 h (nakreslit v Canvě tečkami), odmocnina průtoků jednou větou | Honza |
| 8 | 6:15 | Největší váhu má Praha teď: voda z Prahy je v Děčíně za den | `slajdy/vahy_decin_24h.png`; záporné váhy = trend; na 12 h rozhoduje Mělník | Honza |
| 9 | 7:15 | Čtyři modely, vyhrál nejjednodušší | `slajdy/srovnani_modelu.png`: 44,3 → 24,8 → 23,1 → 17,8 → 17,1 cm | Ondra, Dan |
| 10 | 8:00 | Na povodních, které neviděl, o 55 % menší chyba | `slajdy/test_2021_2025.png` a `slajdy/boris_2024.png`; Boris 27 h předem | Ondra |
| 11 | 8:45 | Co jsme zkoušeli a nepomohlo | `slajdy/co_jsme_zkouseli.png` + řádek TCN 20,3; srážky nepomohly, protože voda z deště už teče v řekách | Dan |
| 12 | 9:30 | Říkáme od–do, a víme, jak často se trefíme | `slajdy/nejistota.png`: 9 z 10 na klidné vodě, 8 z 10 při povodni | Honza |
| 13 | 10:00 | Živé demo | aplikace: Teď 15. 1. 2011 → Dnešek (živá data, vedle ČHMÚ) → Mapa, Celá povodeň 4/2006, posuvník předpověď × skutečnost; 3 minuty, nacvičené kliknutí po kliknutí; záloha video | Honza |
| 14 | 13:00 | Předpověď v centimetrech znamená ulice a domy | `docs/grafy/mapbox2_porovnani.png` přes celý slajd; rozliv z terénu ČÚZK, shoda s úřední mapou 165 ha ze 183 | Honza |
| 15 | 13:40 | Limity | čtyři karty: 36 h dvakrát horší (voda ještě neteče), vrcholy nad trénink podhodnotí, rozliv je statický, v provozu data se zpožděním | Dan |
| 16 | 14:20 | Co dál a díky | doba putování podle průtoku, nasazení na živá data ČHMÚ, hodinové srážky až bude historie; QR na repozitář; linie řeky končí v Děčíně | Tobias |

Čísla v tabulce jsou čas od začátku. Demo má pevné 3 minuty; když se zadrhne, pustí se video a jede se dál.

## Poznámky pro řečníky (do Canvy jako poznámky)

Odpovědi na 20 otázek poroty jsou v `docs/STRATEGIE.md` (větev `honza-vyzkum`) a rozbory v `docs/DENIK.md`. Ke každému slajdu patří jedna otázka, kterou si řečník nacvičí: slajd 4 „proč nestačil balíček“, 6 „proč nedělíte náhodně“, 8 „proč záporné váhy“, 9 „proč ne síť“, 11 „a co když zaprší“, 12 „jak moc se pletete“, 14 „to je váš hydraulický model?“ (ne, je to výška terénu proti výšce hladiny, ověřeno proti úřední mapě), 15 „co když přijde větší povodeň než 2013“.

## Stavba v Canvě

1. Prezentace 16:9, barvy z tohoto souboru do sady značky, písma ověřit.
2. Nahrát všech 8 grafů z `docs/grafy/slajdy/`, snímky `mapbox2_*.png`, `mapbox_povodi.png`, `app_mapbox_decin.png`, `animace_2.png` a video dema (nahrát z aplikace, Win+G, 1920×1080).
3. Linii řeky vyexportovat jako PNG s průhledným pozadím (z `reky.geojson`, Honza) a dát na každý slajd ve stejné poloze; stanice jako tečky, aktivní rozsvícená.
4. Přechody vypnout, animace prvků žádné, jen video na slajdu 2 a 13.
5. Export do PDF jako záloha (bez videa) a na flashku i s videem.
6. Dva nácviky s časomírou: sobota 11:00 a 13:00; na druhém Ondra hraje porotu.
