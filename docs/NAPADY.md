# Tři pojetí úlohy Ovzduší

Všechny tři verze stojí na stejném základu (příprava dat, rozdělení, vyhodnocení, první model). Ten se staví hned a nezávisí na tom, kterou verzi vybereme. Verze se liší tím, co je hlavní výstup a kam jde nejvíc času.

## Společný základ

1. **Příprava dat** (`src/data.py`)
   - platné hodnoty mají kvalitu 8 nebo 9, případně 10 a 11 (hodnota pod detekčním limitem)
   - záporné kódy −5000 až −5011 převést na chybějící hodnotu
   - čas z UTC na místní (Europe/Prague), jinak nesedí denní průběh
   - pro každou látku tabulka čas × stanice
   - polohy a výšky stanic z `metadata/metadata.json`
2. **Rozdělení v čase**
   - trénink: 1/2024–6/2025
   - validace: 7–12/2025, obsahuje topnou sezónu
   - test: 2026, jednou na konci, rozhoduje Ondra (jsou to jen operativní, neověřená data, říct v prezentaci)
3. **Společné vyhodnocení** (`src/evaluate.py`)
   - průměrná chyba (MAE) podle horizontu, stanice a ročního období
   - u varování přesnost a záchyt (precision, recall)
   - vždy vedle baseline
4. **Baseline**
   - „bude jako teď“ má chybu 5,28 / 9,32 / 10,62 µg/m³ na 1 / 6 / 24 h
   - „stejně jako včera ve stejnou hodinu“
5. **Vstupy modelu** (`src/features.py`), všechno jen z minulosti:
   - hodnoty na stanici před 1, 2, 3, 6, 12 a 24 hodinami, průměr za posledních 24 h
   - současné hodnoty na ostatních stanicích (stanice se pohybují spolu, medián korelace 0,66)
   - hodina, den v týdnu, měsíc, topná sezóna
   - počasí, jen když se podaří spárovat meteostanice (zatím nemají polohy)
6. **Modely**
   - nejdřív lineární regrese, pak LightGBM
   - jeden model na každý horizont, stanice jako vstup
   - u každého ukázat, podle čeho rozhoduje (SHAP)

### Co se dá předpovídat

| Co | Typ úlohy | Proč to dává smysl | Srovnání | Metrika |
|---|---|---|---|---|
| PM10 za 6 a 24 h na každé stanici | regrese | hlavní problém kraje, data skoro úplná | „bude jako teď“ | MAE |
| PM2,5 totéž | regrese | zdravotně nejškodlivější | „bude jako teď“ | MAE |
| zítra překročen denní limit PM10 50 µg/m³? | klasifikace | srozumitelné varování pro lidi | „zítra jako dnes“ | záchyt a přesnost varování |
| stupeň indexu kvality zítra (1A–3B) | klasifikace | lidé rozumí „dobrá / špatná“ | „zítra jako dnes“ | přesnost po stupních |
| odpolední maximum O₃ zítra | regrese | léto, jiný mechanismus než prach | „jako dnes“ | MAE |
| neobvyklé hodnoty | detekce | zadání se na ně ptá | nic | kontrola na známých událostech |

Jak přesně se počítá index kvality, ověřit v dokumentaci ČHMÚ nebo u mentora.

## Verze 1: Interaktivní 3D mapa s předpovědí

**Otázka:** jak vypadá ovzduší v Ústeckém kraji teď a jak bude vypadat za 6 a 24 hodin?

**Co uvidí uživatel:**
- 3D sloupce na místech stanic: výška je koncentrace, barva stupeň indexu kvality
- hranice obcí z balíčku; obec obarvená podle nejbližší stanice, s upozorněním, že je to jen přiblížení
- filtry: látka, čas (posuvník s přehráváním), naměřeno / předpověď +6 h / +24 h, výběr stanic, jen překročení limitu
- po kliknutí na stanici graf posledních dní s předpovědí, typická chyba z validace a tři hlavní důvody předpovědi (SHAP)
- přehrávání historie: data končí 30. 9. 2026, takže „teď“ je zvolený okamžik v minulosti a hned je vidět, jestli předpověď vyšla. To je v demu zároveň nejlepší důkaz, že model funguje.

**Jak to postavit:**
- **Doporučení: Streamlit a pydeck.**
  - Pydeck (deck.gl) je stejná 3D technika, jakou používá Mapbox, a v prostředí už ji máme.
  - Všechno je v Pythonu. „Backend“ jsou funkce v témže programu: model se načte jednou (`st.cache_resource`) a pro zvolený čas spočítá předpověď.
  - Honza už má kostru aplikace ve Streamlitu.
- **Podklad mapy:** bez klíče jde Carto, výchozí v pydeck. Styl Mapboxu potřebuje token, ten je po registraci zdarma a patří do `.streamlit/secrets.toml`, který není v Gitu.
- **Samostatný frontend v Mapbox GL JS s backendem (FastAPI)** jen tehdy, když někdo JavaScript opravdu umí. Jsou to dva jazyky a dvakrát víc míst, kde se může něco rozbít.
- **Hranice obcí** mají 13 MB. Pro prohlížeč je zjednodušit (zaokrouhlit souřadnice), jinak se mapa bude sekat.
- **Předpovědi spočítat předem** pro celé validační a testovací období a uložit do souboru. Aplikace je pak jen čte, je rychlá a v demu nic nespadne.

**Body:** nejsilnější v prezentaci (10). Odbornost záleží na tom, jak dobře vysvětlíme model.

**Riziko:** mapa sežere nejvíc času, ale body za odbornost porota dá za model a vysvětlení, ne za 3D efekt. Na mapě proto pracuje nejvýš jeden člověk.

## Verze 2: Smogové varování na zítra

**Otázka:** bude zítra v mém městě překročen denní limit PM10 a proč?

- **Hlavní model:** zítřejší denní průměr PM10 pro každou stanici. Z něj vyplyne varování nad limitem / pod limitem. Pro srovnání přímá klasifikace (logistická regrese, LightGBM).
- **Vzácné události:** limit byl překročen jen ve 368 z 10 942 stanice-dní, skoro vždy v zimě. Model, který nikdy nevaruje, má úspěšnost skoro 97 %, a přesto je k ničemu. Proto měříme záchyt a přesnost varování a práh volíme vědomě. Tohle je silný bod pro odbornost.
- **Vysvětlení (SHAP):** co zvyšuje riziko. Topná sezóna, předchozí den, okolní stanice, se spárovaným počasím i vítr a teplota. Domněnka k ověření: rozdíl mezi Rudolicemi v Horách (840 m) a stanicemi v údolí ukazuje inverzi.
- **Výstup:** jednoduchý přehled. Stanice na mapě se semaforem rizika na zítra, kalendář minulých epizod a graf, jak model vyšel v zimě 2025/26 a v lednu 2026.

**Body:** nejsilnější v odbornosti (20) a splnění zadání. Praktický dopad ocení DCÚK. Malé riziko.

**Slabina:** méně efektní na pohled.

## Verze 3: Detektor neobvyklých událostí

**Otázka:** kdy se v ovzduší stalo něco, co nevysvětlí počasí, roční ani denní doba?

- **Princip:** model se naučí, kolik by na stanici „normálně“ mělo být. Neobvyklé je to, co je naměřeno výrazně nad tím, co model čeká. Rozdíl mezi měřením a předpovědí se porovná s tím, jak moc obvykle kolísá na dané stanici.
- **Co už v datech vidíme (rychlý výpočet, krajský průměr PM10):**
  - Silvestr 2024/25: v 1:00 60,5 µg/m³, běžný prosinec kolem 17. Ohňostroje.
  - Silvestr 2025/26: jen 21,2. Proč? Počasí? Otázka k prozkoumání.
  - 30.–31. 3. 2024: až 144 µg/m³, nejvíc v celých datech a na všech stanicích najednou. Domněnka: saharský prach, ověřit ve zprávách ČHMÚ.
- **Typ události podle toho, kolik stanic zasáhla:**
  - všechny najednou ukazují na počasí nebo dálkový přenos,
  - jediná stanice ukazuje na místní zdroj (požár, průmysl, doprava),
  - chyba měření se pozná podle nesmyslu: PM2,5 vyšší než PM10, SO₂ 1 096.
- **Výstup:** časová osa s vyznačenými událostmi, mapa šíření události hodinu po hodině a katalog deseti největších událostí s vysvětlením.

**Body:** originální, méně týmů to udělá, dobře se vypráví a přímo plní bod zadání „hledat neobvyklé hodnoty nebo události“.

**Slabina:** nemáme „správné odpovědi“. Ověřujeme jen na známých událostech a hrozí, že detektor najde hlavně chyby čidel.

## Doporučená kombinace

- **Jádro je verze 2:** odbornost a jasná metrika.
- **Verze 1 je prezentační vrstva:** mapa stanic s předpovědí a přehráváním. Na stanice stačí 3D sloupce, obce jsou bonus.
- **Verze 3 je jeden slajd** „Co model předpovědět neumí“: neobvyklé události jsou přesně to, co modelu zbude. Zadání chce v prezentaci bod „co model umí a co už z dat určit nelze“, a tohle je odpověď.

**Do 21:00 minimum:**
- čistá data a rozdělení
- společné vyhodnocení
- „bude jako teď“ a LightGBM pro PM10 na 24 h
- mapa se stanicemi a naměřenými hodnotami

**Návrh rozdělení** (role se mění podle potřeby):
- Ondra: rozdělení dat, vyhodnocení, kontrola výsledků
- Dan: modely od baseline po LightGBM, SHAP
- Honza: aplikace a mapa
- Tobias: příběh prezentace, grafy vzorů (den, týden, sezóna), Silvestr a březen 2024

## Otázky pro mentora

- Kde leží meteostanice (kódy `0-20000-0-114xx`)? Smíme je dohledat ve veřejném seznamu ČHMÚ?
- Smíme přidat další otevřená data, třeba zprávy ČHMÚ o epizodách nebo počasí?
- Je pro zadavatele zajímavější předpověď hodnoty, nebo varování před překročením limitu?
- Jak se přesně počítá index kvality ovzduší ze souboru `AirQualityIndex.csv`?
