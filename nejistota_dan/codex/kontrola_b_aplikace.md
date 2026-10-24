Pouze statická kontrola: nic jsem nezměnil, aplikaci ani testy nespustil a tajné soubory nečetl. Kritickou chybu jsem nepotvrdil.

- **[závažnost: vysoká] [app/animace.py:29](C:/Users/danie/Documents/hackathon-2026-nejistota/app/animace.py:29)** – Animace načítá deck.gl z CDN; mapy potřebují internet i bez MAPBOX_TOKEN (OSM/AWS, `mapa.py:128`). Offline budou chybět podklady, animace bez knihovny nefunguje. **Oprava:** přibalit JavaScript lokálně a pro demo připravit dostupné offline video či snímky map.

- **[závažnost: vysoká] [app/app.py:151](C:/Users/danie/Documents/hackathon-2026-nejistota/app/app.py:151)** – „Dnešek“ ponechá výchozí `ridge` učený do 2018. Obráceně lze historii přehrávat přes `ridge_vse`, který ji při tréninku viděl. Porota může sledovat nesprávný model nebo nepoctivé historické srovnání. **Oprava:** svázat model s režimem; historii hodnotit uloženými nezávislými předpověďmi.

- **[závažnost: vysoká] [app/app.py:243](C:/Users/danie/Documents/hackathon-2026-nejistota/app/app.py:243)** – Boris je chybně označen jako předpověď modelu do 2018. Uložený test vzniká s tréninkem do 2020 (`src/porovnej.py:47`, PREHLED:77), zatímco animace počítají z historického `ridge` do 2018. **Oprava:** sjednotit Borisovy pohledy na uložené testovací předpovědi a opravit popisek; test neopakovat.

- **[závažnost: vysoká] [app/app.py:76](C:/Users/danie/Documents/hackathon-2026-nejistota/app/app.py:76)** – `dnes_c` kešuje na 600 sekund také návrat `ok=False`. Krátký výpadek tak vyřadí Dnešek na celé vystoupení; vypnutí a zapnutí přepínače nepomůže. **Oprava:** dlouze kešovat pouze úspěch, chybu krátce a přidat tlačítko opakování s vymazáním této cache.

- **[závažnost: střední] [app/aktualni.py:60](C:/Users/danie/Documents/hackathon-2026-nejistota/app/aktualni.py:60)** – Stahuje se 48 souborů v osmi vláknech, každý s timeoutem 30 s. Kontext executor čeká na zbývající úlohy i při chybě; špatná síť může blokovat stránku řádově minuty. **Oprava:** zavést celkový časový limit, rušení čekajících úloh a rychlou nabídku historie.

- **[závažnost: střední] [app/predikce.py:34](C:/Users/danie/Documents/hackathon-2026-nejistota/app/predikce.py:34)** – Modely nejsou v Gitu; při chybění se trénují a zapisují během načítání. Lokálně navíc chybí `ridge_vse_usti_12/36`. Na cizím Macu hrozí prodleva; chyba zápisu v historické větvi není zachycena. **Oprava:** předem připravit všech šest souborů každé varianty a při startu ověřit úplnost.

- **[závažnost: střední] [app/app.py:172](C:/Users/danie/Documents/hackathon-2026-nejistota/app/app.py:172)** – Zpracují se i neotevřené záložky; navíc `vstupy_c` a animace drží samostatné velké tabulky. Jedna matice vstupů má odhadem 140 MB, `cache_data` vytváří kopie. Zpomaluje to první obrazovku i ovládání. **Oprava:** podmíněně načítat zvolený pohled a sdílet neměnné vstupy přes `cache_resource`. ([Záložky](https://docs.streamlit.io/develop/api-reference/layout/st.tabs), [cache](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_data).)

- **[závažnost: střední] [app/predikce.py:74](C:/Users/danie/Documents/hackathon-2026-nejistota/app/predikce.py:74)** – Hranice pásem nejistoty nesouhlasí s kalibrací přes `pd.cut` (`src/nejistota.py:24`). Při přesně 450 cm použije Děčín +24 h odchylky −37/+9 místo −19/+19 cm. **Oprava:** použít totožné pravostranně uzavřené intervaly a ošetřit hodnoty mimo rozsah.

- **[závažnost: střední] [app/predikce.py:71](C:/Users/danie/Documents/hackathon-2026-nejistota/app/predikce.py:71)** – `ridge_vse` dostává intervaly kalibrované pro jiný model, historický `ridge`. Jejich pokrytí pro nový model není doloženo; porota může „90 %“ chápat jako ověřenou spolehlivost Dnešku. **Oprava:** intervaly vázat na konkrétní model a do ověření je pro `ridge_vse` skrýt nebo výslovně označit.

- **[závažnost: střední] [app/mapbox_mapa.py:73](C:/Users/danie/Documents/hackathon-2026-nejistota/app/mapbox_mapa.py:73)** – Nejbližší DEM polygon se vybírá i mimo vypočtený rozsah. Nízká voda tak dostane rozliv pro minimálně 300 cm v Děčíně nebo 350 cm v Ústí, ale popisek uvádí skutečnou předpověď. **Oprava:** kontrolovat rozsah a zobrazit „rozliv pro tuto hladinu není vypočten“.

- **[závažnost: střední] [app/app.py:278](C:/Users/danie/Documents/hackathon-2026-nejistota/app/app.py:278)** – Po výběru Borise tabulka ukazuje souhrn celého testu, přesto popisek stále tvrdí „průměr přes 4 povodně“. Porota může čísla připsat vybranému Borisovi. **Oprava:** nadepsat tabulku „Souhrn testu 2021–2025“ a uvést rozsah a počet událostí pro danou metriku.

- **[závažnost: střední] [app/requirements.txt:1](C:/Users/danie/Documents/hackathon-2026-nejistota/app/requirements.txt:1)** – Verze nejsou uzamčené. Čerstvá instalace na Macu může mít jiné knihovny než stroj, který vytvořil joblib modely; instalace podle README navíc vyžaduje síť. **Oprava:** připravit předem ověřené prostředí přímo na cílovém Macu a uložit přesné verze.

- **[závažnost: nízká] [app/app.py:159](C:/Users/danie/Documents/hackathon-2026-nejistota/app/app.py:159)** – Při podzimní změně času lze vybrat jen druhou hodinu 02:00; jarní neexistující 02:00 se bez upozornění posune. Historický okamžik není jednoznačný. **Oprava:** rozlišit SEČ/SELČ a na automatický posun upozornit.

- **[závažnost: nízká] [app/styl.py:148](C:/Users/danie/Documents/hackathon-2026-nejistota/app/styl.py:148)** – Popisky metrik mají 11 px, grafy 13 px (`app.py:114`). Na projektoru budou obtížně čitelné; fonty se navíc stahují z Googlu. **Oprava:** přidat prezentační velikosti alespoň 16–18 px a použít lokálně dostupné písmo.

Uložené souhrny **17,1 cm na validaci a 22,4 cm na testu odpovídají PREHLEDu**. V hlavních grafech jsem nenašel chybný posun o horizont ani záměnu UTC a českého času.