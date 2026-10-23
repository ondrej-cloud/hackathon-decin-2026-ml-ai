# Podklady pro brainstorming – Hackathon ML/AI 2026

Podklady pro agenta, který generuje a hodnotí nápady. V pátek v 15:30 mu k nim stačí přidat text zadání.

Značky v textu:
- **[S1]–[S19]** jsou fakta převzatá ze zdrojů, seznam je na konci.
- **(odvozeno)** jsou naše závěry z těch faktů. Nejsou nikde oficiálně potvrzené.

## 1. Akce 2026

- FJFI ČVUT, pracoviště Děčín, pořádá Katedra softwarového inženýrství. Spolupořádá Datové centrum Ústeckého kraje (DCÚK) v rámci projektu Transformační centrum Ústeckého kraje. [S1][S2]
- Pátek 23. 10. 2026: od 14:00 prezence, 14:30–15:30 nepovinný úvod do ML, **15:30 představení témat**, **16:00 start**. [S1]
- Sobota 24. 10.: **14:00 konec práce a odevzdání prezentací**, 14:30–16:30 prezentace v losovaném pořadí (max. 15 minut na tým), pak hodnocení odbornou komisí a vyhlášení. [S1]
- Na práci i prezentaci je 22 hodin, přespává se v učebně. Týmy mají 2–4 studenty středních škol, programování ideálně v Pythonu. [S1]
- Ceny od Ústeckého kraje: 25 000 / 15 000 / 10 000 Kč. [S1]
- Při nevhodném chování nebo podezření na nedovolené látky může organizátor tým vyřadit. [S1]
- Přihlášených je 11 týmů, ze škol v Děčíně, Ústí nad Labem, Teplicích, České Lípě, Pardubicích, Plzni, Olomouci a Brně. Mezi názvy jsou Bageta14, tokenmaxeři, Koalice českých engineerů a Ještě nevíme. [S3]
- Na stránce KSI je 9 týmů se školami: Eigenvectors (SPŠE Pardubice), Bageta14 (SPŠ Ústí n. L.), NetFramework (SPŠ Teplice), VibeCZECH (VOŠ a SPŠE Plzeň), Field Zero (Gymnázium Olomouc-Hejčín), tokenmaxeři (SPŠ Česká Lípa), Shadoxx – Faulty Brakes (SPŠ Ústí n. L. + SPŠ Brno, Purkyňova), nullbyte (SŠ AGC), Jihomoravské datacentrum (SPŠ Brno, Purkyňova + gymnázium Brno, Vídeňská). [S1]
- Kontakty: odborné dotazy RNDr. Petr Kubera, Ph.D., organizační Helena Hauzírková (helena.hauzirkova@fjfi.cvut.cz). [S1]

## 2. Co letos zdůrazňují pořadatelé

Citace z článků DCÚK k ročníku 2026:

- „Žádný projekt nezačíná větou ‚použijeme AI'. Nejdřív je nutné vědět, komu tím chceme pomoci, co potřebujeme zjistit a jak poznáme, že navržené řešení funguje. Teprve potom přichází výběr dat, postupu a způsobu, jak výsledek představit.“ [S4]
- „Není nutné stihnout všechno. Důležité je vybrat podstatu nápadu a přesvědčivě ji ověřit.“ [S4]
- „Výsledkem může být model, aplikace, doporučený postup, analýza, vizualizace nebo kombinace několika přístupů.“ [S4]
- „I funkční a zajímavý prototyp může zůstat nedoceněný, pokud tým nedokáže srozumitelně ukázat, jaký problém řeší, co se mu podařilo ověřit a proč na výsledku záleží.“ [S4]
- „…představit výsledek tak, aby mu rozuměli i lidé mimo jejich obor.“ [S4]
- „Úkolem je během omezeného času najít cestu, která funguje dost dobře na to, aby ji tým mohl ukázat a obhájit.“ [S5]
- „Někdo umí rozebrat problém na menší části. Někdo rychle najde vzorec v datech. Další promění výsledek v přehlednou vizualizaci a někdo dokáže během pár minut vysvětlit, proč celé řešení dává smysl.“ [S5]
- „Hackathon není přehlídka dokonale připravených řešení. […] Zadání dostanete na místě a postupně z něj vytvoříte prototyp, který na konci představíte odborné porotě.“ [S6]
- „…vlastní prototyp řešení, které může mít reálný dopad.“ Pozvánka zmiňuje i „zajímavé ceny či nabídky spolupráce“. [S7]
- „Právě tady dostane vedle technických dovedností prostor také schopnost srozumitelně vysvětlit vlastní nápad. I funkční a zajímavé řešení totiž může zůstat nedoceněné, pokud z prezentace není jasné, co umí a komu může pomoci.“ [S3]

(odvozeno) Zadání dostaneme od pořadatelů, ale v rámci zadání je prostor pro vlastní nápad, komu a jak řešení pomůže. Body přinese ověřený prototyp, který dokážeme srozumitelně vysvětlit, ne co nejširší rozsah.

## 3. Jak se hodnotí

| Ročník | Kritéria poroty | Porota |
|---|---|---|
| 2023 | zpracování matematického modelu, grafické rozhraní aplikace, prezentace výsledků [S8] | 3× KSI FJFI, 1× Autodesk, 2× DCÚK [S8] |
| 2024 | splnění zadání, zvolený postup (vhodné metody, úprava dat), odbornost řešení, prezentace [S9] | 3× FJFI (z toho jeden i FIT), 1× Autodesk, 1× DCÚK; předseda RNDr. Petr Kubera [S9] |
| 2025 | nezveřejněno | nezveřejněno; část mentorů zasedla i v porotě [S11] |

- Týmům pomáhají tutoři z řad studentů FJFI a IT odborníků, mentoři DCÚK chodí mezi týmy a radí. [S9][S10]

(odvozeno) Porota je smíšená: vědci z FJFI ocení správnou metodu a práci s daty, lidé z DCÚK a firem praktické využití. Nápad musí obstát u obou skupin.

## 4. Historie ročníků

### 2023 (6 týmů, 3 úlohy) [S8]

| # | Úloha | Kdo dodal data | Umístění |
|---|---|---|---|
| 1 | klasifikace pulsů ze scintilačního detektoru | katedra jaderných reaktorů FJFI | 2. SPŠ Teplice |
| 2 | klasifikace fraktografických snímků (obrázky lomových ploch) | katedra materiálů FJFI | 1. SPŠE Plzeň, 3. SPŠ Česká Lípa |
| 3 | čištění 2D spekter z rentgenové fluorescenční analýzy | katedra dozimetrie a aplikace ionizujícího záření FJFI | – |

Ceny tehdy byly 8 000 / 4 000 / 2 000 Kč. [S8]

Postup 2. místa (SPŠ Teplice) z jejich vlastní reportáže [S12]:
- nejdřív zkusili jednoduchý postup v Excelu a zjistili, že to tak jednoduché nebude
- dva lidé stavěli neuronovou síť v Pythonu, jeden mezitím od začátku chystal prezentaci
- model byl hotový a zkontrolovaný v pátek večer, uváděli přesnost 99,8 %
- tým se vyspal, v sobotu ráno udělal aplikaci a doladil prezentaci
- prezentoval jeden člen, kterého tým vyzdvihuje

3. místo (SPŠ Česká Lípa) řešilo rozpoznávání obrázků. [S13]

### 2024 (10 přihlášených týmů, 5 úloh) [S9]

| # | Úloha | Kdo dodal data | Umístění |
|---|---|---|---|
| 1 | teplota plazmatu z měření Thomsonova rozptylu (tokamak COMPASS) | Ústav fyziky plazmatu AV ČR | – |
| 2 | teplota plazmatu z jeho vyzařování (COMPASS) | Ústav fyziky plazmatu AV ČR | – |
| 3 | reverzní regrese parametrů simulace | FJFI | – |
| 4 | klasifikace výbojů z databáze tokamaku GOLEM | FJFI | 2. Tým se nedostavil, 3. RessA2 |
| 5 | Energetický detektiv: odhalování charakteru objektů pomocí analýzy spotřeby energie | DCÚK | **1. Robin & Honza** |

- 1. místo: Robin & Honza, 2 lidi, Gymnázium Děčín. 2. místo: 2 lidi, Podještědské gymnázium + SPŠ Liberec. 3. místo: 3 lidi, SPŠ Resslova + Gymnázium Jateční Ústí n. L. [S9]
- Mentor DCÚK: „Některé týmy se však na nás neobracely, což se často odrazilo na jejich horším umístění v závěrečném hodnocení. Nejvíce jsme se zaměřili na týmy, které si zvolily zadání od DCÚK, protože jsme o něm měli nejvíce informací. Jeden z těchto týmů, kterému jsme věnovali značnou pozornost, nakonec vyhrál první místo.“ [S10]
- DCÚK označuje za velký přínos to, že dodalo „data set, který obsahoval reálná data“. [S10]
- Porota veřejně vytkla jednomu týmu, že se bez omluvy nedostavil, a druhému, že akci pojal „po svém bez snahy o řešení“. [S9]
- Ceny 25 000 / 15 000 / 10 000 Kč věnovaly Ústecký kraj a Město Děčín, věcné ceny Complus CZ a IT Děčín. [S9]

### 2025 (13 přihlášených, 12 dorazilo, 4 úlohy) [S11]

- Před akcí DCÚK napsalo: „Některá témata se zaměří na propojení reálných dat z našeho regionu s moderními technologiemi. Týmy se utkají ve zpracování dat, hledání chytrých algoritmů a tvorbě přehledných vizualizací, které mohou mít praktické využití v každodenním životě.“ [S14]
- Zveřejněná je jen jedna úloha: **AI chatbot pro zpracování dat z úředních desek**, tedy nástroj, který se orientuje ve veřejně dostupných informacích a dává lidem přehledné a srozumitelné odpovědi. [S15]
- 1. Koranderium (SPŠ Tábor), 2. Lookey (SPŠ Ústí n. L.), 3. Křížová výprava (SPŠ Teplice). Úlohy 1. a 2. místa nejsou zveřejněné. [S11]
- 3. místo s chatbotem: „funkčního chatbota, který data nejen zpracovává, ale také srozumitelně interpretuje. Porota ocenila jejich přístup i technické provedení.“ [S15]
- Jeden tým nedokončil. Jiný byl v sobotu dopoledne blízko vzdání, mentoři a ostatní mu pomohli projekt dotáhnout. [S11]

## 5. Kdo zadává úlohy a odkud jsou data

- **FJFI a spolupracující ústavy** (2023, 2024): katedra jaderných reaktorů, materiálů a dozimetrie, Ústav fyziky plazmatu AV ČR (COMPASS), tým tokamaku GOLEM, autoři simulací. Šlo o vědecká data: signály, obrázky, spektra, měření plazmatu. [S8][S9]
- **DCÚK** (2024, 2025): reálná data veřejné správy z regionu. V roce 2024 spotřeba energie objektů, v roce 2025 úřední desky. [S9][S15]
- Čím se DCÚK zabývá: provozuje datovou platformu PORTABO pro zpracování a vizualizaci dat. [S16] Krajský katalog otevřených dat má sady o vzdělávání, kultuře a sportu (32), regionech a městech (19), zdraví (19), dopravě (18), populaci (11) a životním prostředí (3). [S17] Datový portál kraje má sekci energetika (index energetické chudoby, screening energetických zdrojů obcí pro Energetické centrum ÚK). [S18] Transformační centrum má pilíře data pro veřejnou správu, inovace, komunitní energetika a revitalizace krajiny. [S19]

(odvozeno) Regionální úloha 2026 bude nejspíš zase z dat veřejné správy. Nejpravděpodobnější oblasti jsou energetika, dokumenty úřadů, doprava, školství, zdraví a obyvatelstvo. Vědecká úloha z FJFI se nejspíš objeví také, protože byla v každém ročníku.

## 6. Vzorce vítězů (odvozeno)

Vzorek je malý (3 ročníky, 9 známých umístění), takže jde o tendence, ne pravidla.

1. **Na stupních převažují úlohy s jasným cílem a měřitelnou úspěšností.** Všech 6 umístění z let 2023–2024 patří klasifikačním úlohám (pulsy, snímky, výboje GOLEM, a nejspíš i Energetický detektiv). Tři regresní úlohy z roku 2024 se neumístily. [S8][S9]
2. **Stejnou úlohu může řešit víc týmů na stupních.** V roce 2023 byla stejná úloha na 1. a 3. místě, v roce 2024 na 2. a 3. místě. Rozhodlo provedení, ne originalita volby. [S8][S9]
3. **Regionální úloha s ochotnými mentory se vyplácí.** V roce 2024 vyhrál tým s úlohou DCÚK, kterému mentoři DCÚK věnovali hodně času. [S10]
4. **Nejdřív funkční model, potom aplikace a prezentace.** Teplice 2023 měly model hotový a ověřený v pátek večer, sobotu věnovaly aplikaci a prezentaci. Prezentaci chystal jeden člen souběžně od začátku. [S12]
5. **Srozumitelný výstup pro laika.** V roce 2023 se hodnotilo grafické rozhraní, v roce 2025 porota ocenila, že chatbot data srozumitelně interpretuje. Články k roku 2026 to opakují pořád dokola. [S8][S15][S4][S3]
6. **Velikost týmu nerozhoduje.** V roce 2024 vyhrály 1. i 2. místo dvoučlenné týmy. [S9]
7. **Zkušené školy se vracejí.** SPŠ Teplice byla na stupních v letech 2023 i 2025, letos má tým NetFramework. SPŠE Plzeň (vítěz 2023) má VibeCZECH a SPŠ Česká Lípa (3. místo 2023) má tokenmaxery. [S8][S11][S1]

## 7. Čeho se vyvarovat

- Nechodit za mentory: podle mentorů DCÚK to vedlo k horšímu umístění. [S10]
- Nedotáhnout řešení nebo ho nebrat vážně: porota to v roce 2024 veřejně vytkla. [S9]
- Ukázat zajímavé řešení, ze kterého není jasné, co umí a komu pomůže. Pořadatelé na to letos upozorňují opakovaně. [S3][S4]
- (odvozeno) Hlásit skvělé číslo bez poctivé kontroly. Vědci v porotě si všimnou, když se testovací data dostala do tréninku nebo když chybí srovnání s jednoduchým řešením.

## 8. Náš tým

Podrobnosti jsou v README.md, tady jen to, co agent potřebuje pro realistické nápady. Zaměření jsou jen výchozí, role se během hackathonu budou míchat.

- **Ondra:** vede tým a ověřuje výsledky. Absolvoval přednášku z pokročilého strojového učení. MacBook M1 16 GB, Claude Max.
- **Dan:** výchozí zaměření modely a trénink. Lenovo Yoga 7i (Core Ultra 7 155H, bez grafiky NVIDIA), Claude Max.
- **Honza:** výchozí zaměření aplikace a grafy. Starší notebook, Claude Max.
- **Tobias:** výchozí zaměření prezentace a pohled laika. MacBook M4 16 GB, nejspíš na něm poběží demo. Claude Pro s menším limitem.
- Nástroje: Python, scikit-learn, LightGBM, PyTorch, Streamlit, Claude Code. GPU zdarma na Kaggle nebo v Colabu, lokálně jen Macy (MPS).
- Omezení: 22 hodin. Celý řetězec od dat po aplikaci chceme mít ve 21:00, v 11:00 končí nové funkce. Velký model od nuly nenatrénujeme, jen dolaďujeme předtrénované. U textových úloh by jazykový model v aplikaci potřeboval API klíč placený zvlášť nebo lokální model.

## 9. Jak hodnotit nápad (naše kritéria)

Každý nápad by měl mít:

1. **Komu pomáhá** – konkrétní člověk nebo instituce a jeho problém v jedné větě.
2. **Vstup → výstup** – co do řešení vstupuje a co z něj vychází.
3. **Metrika** – jak poznáme, že funguje, a s jakým jednoduchým řešením se srovnáme.
4. **Minimum do 21:00** – nejmenší verze, která projde celým řetězcem.
5. **Demo** – co na prezentaci uvidí laik.
6. **Otázka pro mentora** – co si potřebujeme ověřit jako první.

Bodování 1–5:

| Kritérium | Na co se ptát |
|---|---|
| Splnění zadání | Řeší to přesně to, co zadavatel chce? |
| Postup | Je metoda vhodná pro data a máme ji s čím srovnat? |
| Odbornost | Umí každý z nás vysvětlit svou část a Ondra celek? |
| Prezentace a dopad | Pochopí laik do 2 minut, komu to pomáhá? |
| Proveditelnost | Stihneme celý řetězec do 21:00 na našich počítačích? |
| Riziko | Co nejspíš selže a máme pro to zálohu? |

Kritéria 1–3 odpovídají hodnocení poroty z roku 2024, 4 přidávají důraz pořadatelů z roku 2026, 5 a 6 jsou naše omezení.

## 10. Co nevíme

- Letošní témata. Ukážou se v pátek v 15:30.
- Úlohy 2025 kromě chatbota a co postavili Koranderium a Lookey.
- Kritéria a složení poroty pro rok 2026. Kritéria z roku 2024 jsou nejbližší známá.
- Jestli smíme data od pořadatelů nahrát do cloudu (Kaggle, Colab, jazykové modely). Zeptat se hned na začátku.

## Zdroje

- [S1] Hackathon ML/AI 2026, stránka KSI: https://ksi.fjfi.cvut.cz/udalosti/hackathon-mlai-2026
- [S2] DCÚK, Registrace na Hackathon ML/AI 2026 pokračuje (28. 8. 2026): https://dcuk.cz/novinky/mate-napad-dejte-mu-jeden-vikend-registrace-na-hackathon-ml-ai-2026-pokracuje/
- [S3] DCÚK, Hackathon ML/AI 2026 má jedenáct týmů (15. 10. 2026): https://dcuk.cz/novinky/hackathon-ml-ai-2026-ma-jedenact-tymu-ted-uz-zbyva-jen-zacit/
- [S4] DCÚK, Od otázky k prototypu (29. 9. 2026): https://dcuk.cz/novinky/od-otazky-k-prototypu-co-se-da-vytvorit-za-jeden-hackathon/
- [S5] DCÚK, AI není sólová disciplína (11. 9. 2026): https://dcuk.cz/novinky/ai-neni-solova-disciplina-jake-misto-muzete-mit-v-hackathonovem-tymu/
- [S6] = [S2]
- [S7] DCÚK, Hackathon ML/AI 2026 – Nápady, kód a umělá inteligence v akci (15. 5. 2026): https://dcuk.cz/novinky/hackathon-ml-ai-2026-napady-kod-a-umela-inteligence-v-akci/
- [S8] KSI, Hackathon 2023 je za námi: https://ksi.fjfi.cvut.cz/informacni-deska/hackathon-2023-je-za-nami
- [S9] KSI, Hackathon ML/AI 2024 zná své vítěze: https://ksi.fjfi.cvut.cz/informacni-deska/hackathon-mlai-2024-zna-sve-viteze
- [S10] DCÚK, Hackathon ML/AI 2024 (30. 10. 2024): https://dcuk.cz/novinky/hackathon-ml-ai-2024-2/
- [S11] DCÚK, Hackathon ML/AI 2025: když se data potkají s kávou, kódem a nápady (14. 10. 2025): https://dcuk.cz/novinky/hackathon-ml-ai-2025-kdyz-se-data-potkaji-s-kavou-kodem-a-velkymi-napady/ a výsledky na KSI: https://ksi.fjfi.cvut.cz/udalosti/hackathon-mlai-2025
- [S12] SPŠ Teplice, Hackathon na ČVUT v Děčíně – velký úspěch (16. 10. 2023): https://www.sostp.cz/aktuality-stredni-prumyslova-skola-aktuality/511-hackathon-na-cvut-v-decine-velky-uspech
- [S13] SPŠ Česká Lípa, Hackathon ČVUT Děčín – 3. místo (18. 10. 2023): https://sps-cl.cz/article/2023-hackathon-cvut-decin-3-misto
- [S14] DCÚK, Hackathon ML/AI 2025: Plno! Třináct týmů (7. 10. 2025): https://dcuk.cz/novinky/hackathon-ml-ai-2025-plno-trinact-tymu-dva-dny-nekonecno-moznosti/
- [S15] SPŠ Teplice, Naši žáci opět obstáli na hackathonu (16. 10. 2025): https://www.sostp.cz/aktuality/891-nasi-zaci-opet-obstali-na-hackathonu
- [S16] Datové centrum Ústeckého kraje: https://dcuk.cz/
- [S17] Otevřená data Ústeckého kraje: https://lkod.portabo.cz/
- [S18] Datový portál Ústeckého kraje, Energetika: https://datauk.cz/temata/energetika/
- [S19] DCÚK, Transformační centrum Ústeckého kraje: https://dcuk.cz/projekty/transformacni-centrum-usteckeho-kraje/
