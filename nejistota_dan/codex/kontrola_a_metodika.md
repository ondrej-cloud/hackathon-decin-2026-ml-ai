Našel jsem závažné problémy v nezávislosti ověření. Současné výsledky nestačí k tvrzení, že aplikace poskytuje ověřené 80% a 95% pásmo. Nic jsem nezměnil; test 2021–2025 jsem nepoužil.

Cesty jsou relativní ke kořeni projektu.

- [závažnost: vysoká] `nejistota_dan/overeni.py:79`, `prisne.py:46` – **Přímý překryv kalibrace a hodnocení.** Prosincový a lednový fold 2012/2013 sdílejí 48 hodin při každém horizontu; vyřazení pouze `fold == k` je ponechá v kalibraci. Ani „přísná“ varianta je neodstraní. Oprava: spojit související povodně do společných bloků a vynechat celý hodnocený blok.

- [závažnost: vysoká] `nejistota_dan/overeni.py:79`, `oof.py:83` – **Kalibrační modely mohly vidět hodnocenou povodeň.** Model foldu j vyřazuje jen mezeru j. U +24 h například model pozdější březnové povodně 2010 trénuje na 15 hodinách okna předchozí; červnový model 2013 na 30 hodinách předchozího okna. Tato dvě hodnocená okna se přitom přímo nepřekrývají. Oprava: vnější blok vyřadit ze všech vnitřních fitů; vlastní okno každého současného OOF modelu vyřazené je.

- [závažnost: střední] `nejistota_dan/prisne.py:7`, `PRUBEH.md:11` – **Shoda dvou Ridge variant nedokazuje platnost pro LightGBM/G3.** Kontrola navíc stále obsahuje překryté kalibrační hodiny. Oprava: po odstranění překryvů ověřit vnořeně také LightGBM/G3 a závěr omezit na skutečně ověřené modely.

- [závažnost: střední] `nejistota_dan/kandidati/lgbm_stanice.py:49`, `src/models/lgbm_a.py:25` – **Část předzpracování zůstává mimo fold.** Týmové stanice používají pevné doby doběhu odhadnuté na původním tréninku, který obsahuje některé vynechávané povodně. `prisne=True` toto neřeší. Oprava: i jejich doby odhadovat uvnitř příslušného tréninku.

- [závažnost: vysoká] `nejistota_dan/nejistota_dan.py:55` – **Oprava n+1 sama nezaručuje nominální pokrytí.** Hodinové chyby jsou autokorelované a pocházejí z různých LOFO modelů; nejde o standardní split conformal s jedním nezávisle kalibrovaným modelem. Oprava: označit výsledky jako empirické, ověřovat po nezávislých epizodách a použít odpovídající blokovou metodu. Viz [Barber et al.](https://www.stat.berkeley.edu/~ryantibs/papers/nexcp.pdf).

- [závažnost: střední] `nejistota_dan/nejistota_dan.py:70` – **200 hodin není 200 nezávislých pozorování.** Globální náhrada funguje programově, ale nezajišťuje pokrytí malé skupiny. Celkově mají foldy shodně 289 hodin; uvnitř skupin však povodně váží podle počtu příslušných hodin. Oprava: vykazovat také počet zastoupených epizod a četnost náhrady; explicitně zvolit vážení hodin versus povodní.

- [závažnost: střední] `nejistota_dan/overeni.py:138`, `PRUBEH.md:8` – **Výběr a vykázání vítěze používají stejná hodnocení.** Pevné pravidlo nezruší optimismus výběru. Zkoušeno bylo nejméně sedm rodin variant, včetně Mělníka a poslední ověřené chyby. Oprava: zahrnout výběr varianty do vnějšího ověření a zveřejnit všechny pokusy.

- [závažnost: střední] `nejistota_dan/overeni.py:136`, `vysledky/prisne_vnorene.csv:26` – **Celkové pokrytí zakrývá slabé vzestupy.** U „přísného“ ověření Ridge/Ridge30 dosahuje 80% pásmo při skutečném rychlém vzestupu jen 61–71 %. Oprava: tato omezení uvádět vedle celkového výsledku; případné požadavky na kritické režimy zahrnout do výběru předem.

- [závažnost: vysoká] `nejistota_dan/overeni.py:150`, `app/predikce.py:40` – **Kalibrace neodpovídá modelům aplikace.** Chyba pokrytí ani posun hranic pro model do 2018 či do 2025 nejsou těmito výsledky určeny; nemusí jít o konzervativní pásmo. Oprava: svázat kalibraci s verzí modelu, přehrávání ověřit časově do 2020; pro dnešní model sbírat nové ověřené chyby. Test 2021–2025 ponechat nedotčený.

- [závažnost: střední] `app/predikce.py:68` – **Nové pásmo není zapojené.** Aplikace stále vrací původní 90% interval jen pro Ridge. Oprava: připojit `pasmo()`, předat historii 6 h, úroveň a správnou identitu modelu; aktualizovat popisky.

- [závažnost: střední] `nejistota_dan/oof.py:103` – **Rozsah platnosti je užší než provoz aplikace.** Společná děčínská okna jsou rozumná pro párové srovnání obou měst, ale neověřují všechny ústecké epizody ani běžné hodiny mimo povodně. Oprava: doplnit samostatné hodnocení Ústí a klidných období do 2020.

- [závažnost: nízká] `nejistota_dan/nejistota_dan.py:59` – **Malé/prázdné vzorky porušují deklarovaný kontrakt.** Prázdný vzorek vyvolá `IndexError`; ořezání krajních pořadí na minimum/maximum ruší obecnou konformní garanci. Oprava: prázdný vstup explicitně odmítnout, nedostupná krajní pořadí reprezentovat nekonečnými mezemi.

- [závažnost: střední] `nejistota_dan/nejistota_dan.py:44`, `:56` – **NaN není ošetřené.** Chybějící stav může dostat režim „klid“, u `zmena6` krajní skupinu; NaN v kalibraci může znehodnotit kvantil. Oprava: kontrolovat konečnost potřebných vstupů a při chybě nevydávat zdánlivě platné pásmo.

- [závažnost: nízká] `nejistota_dan/nejistota_dan.py:93` – **Smíšené tvary se tiše zkrátí.** Skalární `pred` s vektorovým stavem vrátí pouze první výsledek. Oprava: požadovat skaláry nebo stejně dlouhá 1D pole, případně důsledně implementovat broadcasting.

Bez nálezu: režimy používají pouze `pred`, `h0`, `h6`; skutečný vývoj slouží jen hodnocení. Winklerovo skóre je správně. Dolní `floor`, horní `ceil` i převod pořadí na index jsou pro dostatečné n správně. `pasmo()` funguje pro skaláry a stejně dlouhá 1D pole.

G3 odpovídá `kandidati/g3.py`: pevné 0,5/0,5, správný LightGBM fit a kontrola společných řádků. Pro Děčín jsem shodu řádků ověřil u všech horizontů; rychlý Ridge proti sklearn má maximální rozdíl **5,9 × 10⁻⁹ cm**. V kontrolovaném stavu chyběly kompletní OOF LightGBM pro Ústí a `kvantily.json`, takže úplný G3 a finální výběr nebylo možné číselně potvrdit.