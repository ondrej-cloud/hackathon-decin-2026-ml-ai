# Prezentace: vizuální jazyk a stavba v Canvě

Obsah a pořadí slajdů určuje Ondrova kostra na 7 minut v `docs/PREZENTACE_7MIN.md` (10 slajdů, 5 záložních). Tenhle soubor říká, jak deck vypadá a jak je postavený v Canvě. Deck: https://www.canva.com/d/xVAIR8am2CrRslj (1920 x 1080, 17 stránek, u každé poznámky řečníka s časem). Grafy jsou z `docs/grafy/prezentace/` (bez nadpisů, nadpis je na slajdu), snímky aplikace z `docs/grafy/`.

## Myšlenka a vizuální jazyk

Jedna věta, která drží celou prezentaci: **„Co teče Prahou teď, je zítra v Děčíně.“** Nese ji **linie řeky**: tenká modrá čára Vltavy a Labe od Prahy po Děčín (z `data/external/reky.geojson`), velká na titulu, malá vpravo dole na každém dalším slajdu; rozsvícená tečka ukazuje, o kterém úseku se mluví (Praha modrá, Mělník oranžová, Děčín červená).

- Barvy jako v aplikaci: pozadí #111820, karty #1a232d, voda #3aa0c9 a #7cc6e4, stupně #f2c437 / #ef6c00 / #c62828, text #ffffff a #c8d1d9, tlumený #8b98a5, „bude jako teď“ #666666. Nic jiného.
- Písmo: nadpisy a čísla Sofia Sans Extra Condensed (náhrada Barlow Condensed nebo Oswald), text Schibsted Grotesk (náhrada Archivo). Canva přes API rodinu písma nastavit neumí, viz „Co dodělat ručně“.
- Každý slajd má jedno tvrzení jako nadpis, jedno velké číslo nebo jeden obrázek, nejvýš tři věty textu. Žádné odrážkové stěny, ikony z knihoven, stock fotky ani přechody.
- Grafy jako bílé karty vlevo, čísla a text vpravo. Snímky mapy přes celý slajd se ztmavením.
- Patička: zdroj dat a map. Štítek vlevo nahoře: číslo bloku a téma (01 · CO ŘEŠÍME …), u záložních slajdů otázka poroty, na kterou odpovídají.

## Stránky v Canvě

| Stránka | Slajd kostry | Nadpis | Podklad |
|---|---|---|---|
| 1 | (titul, do času se nepočítá; kdo začíná videem, smaže ho) | Kolik vody přiteče do Děčína | `mapbox2_porovnani.png`, linie řeky Praha–Děčín |
| 2 | 1 video | bez nadpisu, věta „Tohle je Děčín v září 2024. Náš model to hlásil 27 hodin předem.“ | zatím snímek `mapbox2_animace.png`, nahradit videem |
| 3 | 2 | Den předem víte, kam až voda dosáhne | `prezentace/02_mapa_decin.png` přes celý slajd, velké 27 h |
| 4 | 3 | Co teče Prahou teď, je zítra v Děčíně | `03a_mapa_stanic.png`, `03b_proc_externi_data.png`, 20 let · 12 stanic · 175 320 hodin |
| 5 | 4 | Model vidí jen to, co je v tu chvíli změřené | `04_vahy_modelu.png` |
| 6 | 5 | Zkusili jsme 12 cest, vyhrál nejjednodušší | `05_co_jsme_zkouseli.png`, velké „12 cest“ |
| 7 | 6 | Ověřujeme třikrát, pokaždé na povodních, které model neviděl | `06_jak_overujeme.png` |
| 8 | 7 | Boris: 3. stupeň hlášen 27 hodin předem | `07_boris_2024.png`, velké 27 h |
| 9 | 8 | O 55 % menší chyba na testu i na všech 8 povodních | `08a_test_2021_2025.png`, `08b_vicenasobna_validace.png`, velké −55 % |
| 10 | 9 | Živé demo (Dnešek, mapa Borise, rozliv), 70 s | pozadí `mapbox2_animace.png` ztmavené |
| 11 | 10 | Co umíme, co ne a co dál | čtyři karty, závěrečná věta, „Děkujeme. Otázky?“ |
| 12 | záloha | Rozliv: výška terénu proti hladině, ověřená proti úřední mapě | `mapbox_decin.png`, 167 / 183 / 165 ha |
| 13–17 | Z1–Z5 | Jak dopadly jednotlivé modely · „Bude jako teď“ je vždycky o den pozadu · Když se blíží vrchol, už neprší · Do rozmezí od–do se vejde 8 až 9 z 10 hodnot · Povodeň 2011: 3. stupeň hlášen 15 hodin předem | `Z1`–`Z5` |

Časy, řečníci a co se říká jsou v `docs/PREZENTACE_7MIN.md` a v poznámkách řečníka v Canvě. Oprava proti dřívějšímu plánu: neříkat, že „Děčín dnes vidí jen 4 hodiny dopředu“; ČHMÚ pro Děčín oficiální předpověď vydává a aplikace ji ukazuje, 4 h platí jen pro data z balíčku.

## Co dodělat ručně v Canvě

1. Písma: na každé stránce vybrat vše (Ctrl+A), nadpisy a velká čísla přepnout na Sofia Sans Extra Condensed, text na Schibsted Grotesk. Po přechodu na kondenzované písmo zvětšit nadpisy a čísla o 10 až 20 %, místa je dost.
2. Stránka 2: vyměnit obrázek na pozadí za video z aplikace (Děčín, Boris 9/2024, 4 h za s, celá obrazovka, 25 s, bez zvuku), ztmavení dole nechat kvůli větě.
3. Přechody vypnout, animace prvků žádné.
4. Export do PDF jako záloha bez videa; na flashku i s videem.
5. Dva nácviky s časomírou: sobota 11:00 a 13:00; na druhém Ondra hraje porotu.

## Otázky poroty

Odpovědi jsou v `docs/POROZUMENI.md` (sekce Otázky, které čekáme od poroty), v `docs/CESTA_MODELU.md` a v `docs/STRATEGIE.md` (větev `honza-vyzkum`). Záložní slajdy 12 až 17 odpovídají rovnou grafem: proč lineární regrese, co je „bude jako teď“, proč ne srážky, jak moc se pleteme, další povodeň mimo trénink, a jestli je rozliv hydraulický model (není, je to výška terénu proti hladině ověřená proti úřední mapě).
