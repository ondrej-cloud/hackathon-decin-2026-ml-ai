# Hackathon ML/AI 2026 – plán týmu

FJFI ČVUT Děčín, od pátku 23. 10. 14:00 do soboty 24. 10. 17:00. Soutěž startuje v pátek v 16:00. V sobotu ve 14:00 odevzdáváme a od 14:30 prezentujeme porotě, každý tým nejvýš 15 minut. Ceny jsou 25, 15 a 10 tisíc Kč.

Každý má výchozí zaměření, ale role se budou míchat podle toho, co je zrovna potřeba a co nás během práce napadne. Pracujeme ve společném soukromém repozitáři, každý na své větvi.

## Jak se tu vyhrávalo

| Ročník | Týmy / úlohy | 1. místo | Úloha vítěze | Co o tom víme |
|---|---|---|---|---|
| 2023 | 6 / 3 | SPŠE Plzeň | klasifikace fraktografických snímků (obrázky) | Porota hodnotila matematický model, grafické rozhraní a prezentaci. Stejnou úlohu řešilo i 3. místo. |
| 2024 | 10 / 5 | Robin & Honza, Gymnázium Děčín (dva lidi) | Energetický detektiv: poznat charakter objektu podle spotřeby energie (data Datového centra ÚK) | Mentoři z Datového centra se nejvíc věnovali týmům s jejich zadáním a jeden z těch týmů vyhrál. Týmy, které se mentorů neptaly, podle nich dopadly hůř. 2. a 3. místo měly klasifikaci výbojů z tokamaku GOLEM. |
| 2025 | 13 / 4 | Koranderium, SPŠ Tábor | nezveřejněno | 3. místo (SPŠ Teplice) mělo chatbota nad úředními deskami. Porota ocenila, že data nejen zpracoval, ale i srozumitelně vysvětlil. |

V roce 2024 porota hodnotila čtyři věci: splnění zadání, zvolený postup (vhodné metody, úpravu dat), odbornost řešení a prezentaci. Seděli v ní lidé z FJFI, z Datového centra a z IT firem.

### Co z toho plyne pro nás

1. **Za mentory chodit od první hodiny.** Sedí v porotě a vědí, co zadavatel opravdu potřebuje. Chodíme za nimi s konkrétními otázkami: na začátku s nápadem, večer s prvními výsledky, ráno s finální verzí.
2. **Pokrýt všechna čtyři kritéria.** Splnění zadání si ověříme u mentora hned na začátku. Postup a odbornost znamenají, že každý umí vysvětlit, co dělal, a Ondra celek. Na prezentaci potřebujeme čas, ne jen poslední hodinu.
3. **Demo, kterému rozumí laik.** V roce 2023 se hodnotilo grafické rozhraní, v roce 2025 porota ocenila srozumitelný výstup.
4. **Úloha, ve které budeme mít ve 21:00 celý řetězec.** V roce 2024 vyhrála úloha od Datového centra. Rozhoduje ale hlavně to, jestli v ní stihneme ověřený výsledek a jestli k ní máme ochotného mentora.
5. **Počet lidí nerozhoduje.** V roce 2024 vzaly 1. i 2. místo dvoučlenné týmy. Naše výhoda jsou tři účty Claude Max, díky kterým zkusíme víc přístupů. AI ale nejspíš budou používat i ostatní, takže rozhodne poctivé ověření, to, že řešení rozumíme, a prezentace.
6. **Dotáhnout to do konce.** V roce 2024 porota veřejně pokárala tým, který soutěž nebral vážně, a v roce 2025 jeden tým nedokončil. Celý řetězec ve 21:00 je naše pojistka.

## Tým

| Kdo | Počítač | Claude | Výchozí zaměření |
|---|---|---|---|
| Ondra | MacBook M1, 16 GB | Max 20x | vedení a ověřování výsledků |
| Dan | Lenovo Yoga 7i (Core Ultra 7 155H, bez NVIDIA) | Max 20x | modely a trénink |
| Honza | starší notebook | Max 20x | aplikace a grafy |
| Tobias | MacBook M4, 16 GB | Pro | prezentace a pohled uživatele |

Zaměření je jen výchozí bod. Kdo má hotovo nebo dostane nápad, vezme si další věc, a na čem kdo dělá, se bude během noci měnit. Na kontrolních bodech si práci přerozdělíme. Kdo na čem zrovna dělá, píšeme do sekce **Stav** v `CLAUDE.md`, aktualizovat ji může kdokoli.

Pevné je jen tohle: Ondra vede (téma, mentoři, čas, rozhodnutí, když se neshodneme) a hlídá, aby výsledky byly poctivě ověřené.

**Oblasti práce**, mezi kterými se budeme přesouvat:

- **Data:** rozbor dat, společné rozdělení na trénovací, validační a testovací část, úprava dat a nové veličiny.
- **Ověřování:** jedno společné vyhodnocení, kontrola výsledků a úniku dat, finální test.
- **Modely:** od jednoduchého základu (baseline) k lepším přístupům.
- **Aplikace a grafy:** demo pro laika, grafy do prezentace, záložní video dema.
- **Prezentace a příběh:** komu řešení pomáhá, deník, poznámky od mentorů, slajdy, nácvik.

Co víme o počítačích:
- Tabulková data a gradient boosting stačí na procesoru, na neuronové sítě je GPU zdarma na Kaggle nebo v Colabu. Lokálně mají GPU jen Macy (MPS).
- Nejvýkonnější Mac je Tobiasův M4, demo na prezentaci nejspíš poběží z něj.
- Honzův notebook je starší, těžký trénink na něm nepouštíme.
- Tobias má Claude Pro s menším limitem, takže na něj nedáváme práci, která spotřebuje hodně Claude.

## Pátek do 17:30: výběr tématu

**14:00–15:30:** Příjezd, rozložit se a hned ověřit, že na místní Wi-Fi funguje Claude Code (záloha je hotspot z mobilu). Kdo chce, jde na úvod do strojového učení (14:30–15:30).

**15:30–17:30:**
1. Představení témat. Všichni poslouchají a píšou si.
2. Projdeme každé téma: jaká jsou data, co z toho jde za 22 hodin udělat, komu to pomůže. Pomůže `/temata`. Vybereme jedno.
3. Brainstorming: komu řešení pomáhá a proč, kdo je cílový uživatel, jak to bude fungovat a jak poznáme, že funguje (metrika).
4. S prvním návrhem za mentory a upravit ho podle jejich zpětné vazby. Když se nápad nelíbí, vracíme se k bodu 2.
5. Nejpozději v 17:30 je rozhodnuto. Domluvíme, kdo začne na čem a jak propojíme model s aplikací (co předpověď bere a vrací), zapíšeme to do Stavu a jdeme pracovat. Kdybychom se rozhodovali déle, nestihneme mít ve 21:00 celý řetězec.

## Harmonogram

Kontrolní body, kde se všichni na 10 minut sejdeme (`/stav`) a případně přerozdělíme práci:

| Čas | Co musí platit |
|---|---|
| 19:00 | data jsou rozdělená, společné vyhodnocení hotové, máme první jednoduchý model a kostru aplikace |
| 21:00 | celý řetězec od dat po aplikaci funguje, i když je model ještě slabý |
| 0:00 | stav a plán na noc, chystáme dlouhý trénink |
| 8:00 | výsledky z noci, vybíráme finální přístup |
| 11:00 | konec nových funkcí, dál už jen opravy a nácvik |
| 14:00 | odevzdání prezentace |

Co se kdy hlavně děje:

| Čas | Hlavní práce |
|---|---|
| 17:30–19:00 | rozbor a rozdělení dat, společné vyhodnocení, první jednoduchý model, kostra aplikace s falešnou předpovědí, sepsat zadání a komu řešení pomáhá |
| 19:00–21:00 | pokusy s modely, napojení aplikace, za mentory s prvními výsledky |
| 21:00–1:00 | zlepšování, kontrola úniku dat, osnova prezentace, plán na noc |
| 1:00–8:00 | spíme ve dvou směnách (domluvíme na místě), přes noc běží dlouhý trénink |
| 8:00–11:00 | výběr finálního přístupu, jeden test na testovací části, finální model v aplikaci, výsledky do prezentace |
| 11:00–14:00 | jen opravy, záložní video dema, dva nácviky prezentace, odevzdání |

Na jídlo podle programu (večeře 18–19, snídaně 7:30–9, oběd 12–13) chodíme postupně, ať práce nestojí.

## Repozitář

Výchozí struktura. Klidně ji měňte, přejmenovávejte a přidávejte, co bude potřeba. Když se změní něco, co používají ostatní, zapište to do Stavu.

```
hackathon-decin-2026-ml-ai/
├── CLAUDE.md          kontext pro Claude, sekce Stav
├── .claude/           role, příkazy a nastavení pro Claude
├── zadani/            všech pět zadání (PDF a text), přehled v README
├── data/
│   ├── raw/           data od pořadatelů, NE do Gitu
│   └── split/         společné rozdělení train / val / test
├── src/               kód: příprava dat, vyhodnocení, modely, předpověď
├── results/           výsledky pokusů, každý jako nový soubor
├── models/            malé modely, velké přes Google Disk
├── app/               aplikace
└── docs/
    ├── POKUSY.md      každý trénink a pokus: co, jak, výsledek, závěr
    ├── DENIK.md       rozhodnutí, proč, co je špatně
    ├── DATA.md        jak data vypadají, chyby v nich, rozdělení
    ├── POROZUMENI.md  úloha a výsledky našimi slovy, limity, otázky
    └── grafy/         grafy do prezentace
```

Pár pravidel, která platí, ať se struktura změní jakkoli:

1. **Testovací část dat se nepoužívá k ladění.** Pustí se jednou, na finální model, a rozhoduje o tom Ondra.
2. **Jedno společné vyhodnocení.** Všichni měří stejně, jinak nejdou výsledky srovnat. Každý pokus se uloží jako nový soubor do `results/`, takže nevznikají konflikty.
3. **Propojení modelu a aplikace je dohoda.** Co předpověď bere a vrací, je zapsané ve Stavu. Dokud model není, aplikace jede s falešnou předpovědí.
4. **Data a klíče nikdy do Gitu.**

Když dva lidé potřebují stejný soubor, stačí si to říct. Git změny většinou spojí sám, a když ne, Claude konflikt vyřeší.

## Claude Code v repozitáři

Claude Code při každém startu sám načte `CLAUDE.md`: kontext hackathonu, pravidla, aktuální Stav, harmonogram a tento plán. Všichni čtyři Claude tak vědí totéž. Na začátku relace napiš svoje jméno jako příkaz. Claude se dozví, kdo jsi, na jakém počítači a s jakým účtem pracuješ a jaké je tvoje výchozí zaměření. Na čem děláš teď, zjistí ze Stavu nebo se zeptá.

| Příkaz | Kdy | Co dělá |
|---|---|---|
| `/ondra`, `/dan`, `/honza`, `/tobias` | začátek relace | kdo jsi, tvůj počítač, účet a výchozí zaměření |
| `/sync` | průběžně | commit tvé práce, stažení práce ostatních, push tvé větve |
| `/sync main` | když je něco hotové | totéž a hotovou práci pošle i do `main` |
| `/temata <text zadání>` | pátek 15:30 | rozbor témat a návrhy nápadů podle vzorců vítězů |
| `/stav` | kontrolní body | přehled, co je hotové, kdo na čem dělá a co blokuje |
| `/denik` | jednou za hodinu | dohledá, co se na všech větvích udělalo a v `docs/` chybí, doplní to a shrne |
| `/kontrola` | po nových výsledcích | kontrola výsledků (únik dat, rozdělení, metrika) |
| `/porota` | sobota ráno | nácvik otázek poroty |
| `/kaggle [co natrénovat]` | neuronové sítě, noční trénink | nahraje data, pošle trénink na GPU na Kaggle, ohlídá ho a stáhne výsledky |

Subagent `kontrolor` nezávisle zkontroluje jeden pokus. Commity z Claude jsou bez podpisu Claude, jen pod jménem autora.

V `.claude/settings.json` je povolené spouštět Python, Streamlit, Kaggle a běžné příkazy Gitu bez ptaní. Zakázané jsou `git push --force`, `git reset --hard` a čtení `.env` a přihlašovacích údajů ke Kaggle. Povolení začnou platit, až Claude Code při prvním spuštění ve složce potvrdíš, že jí důvěřuješ.

## Git

Každý má svou větev: `ondra`, `dan`, `honza`, `tobias`. Na ni pushuje kdykoli a nikomu tím nic nerozbije. Do `main` posíláme to, co funguje a co se hodí ostatním, nejméně na každém kontrolním bodě. Na stejných souborech může pracovat víc lidí. Čím častěji `/sync`, tím menší konflikty.

**Před odjezdem, každý:**

1. Přijmout pozvánku z e-mailu od GitHubu.
2. Přihlásit se: `gh auth login` (nebo přes GitHub Desktop).
3. Naklonovat: `git clone https://github.com/ondrej-cloud/hackathon-decin-2026-ml-ai.git`
4. Přepnout na svou větev: `cd hackathon-decin-2026-ml-ai` a `git switch dan` (svoje jméno).
5. Spustit `claude`, potvrdit důvěru ve složku a napsat `/dan` (svoje jméno).
6. Zkušební commit: vytvořit `docs/test-dan.txt` a napsat `/sync`. Komu to projde, má přístup v pořádku.

**Pracovní cyklus během hackathonu** (celý ho udělá `/sync`):

1. commit tvé práce na tvé větvi
2. `git fetch` a `git merge origin/main` stáhne práci ostatních
3. `git push origin <větev>`
4. s `/sync main` navíc `git push origin HEAD:main`

`/sync` spouštěj po každém funkčním kroku, nejméně jednou za hodinu. `/sync main` vždy, když máš něco, co potřebují ostatní.

**Když něco nejde:**
- Push do `main` je odmítnutý: někdo byl rychlejší, pusť `/sync main` znovu.
- Konflikt: řekni Claude „vyřeš konflikt a zachovej změny obou stran“. Nikdy `git push --force`.
- Data a velké modely: přes AirDrop, flashku nebo Google Disk, u všech do stejné složky `data/raw/`.

## Deník a prezentace

Porota hodnotí hlavně, jak úloze rozumíme a jak to vysvětlíme. Proto každý Claude zapisuje průběžně a sám, bez připomínání, ve stejném commitu jako kód (pravidla jsou v CLAUDE.md, sekce Dokumentace):

| Soubor | Co tam je |
|---|---|
| `docs/POKUSY.md` | každý trénink a pokus, i nepovedený: otázka, data, vstupy, model, výsledek proti baseline, závěr |
| `docs/DENIK.md` | rozhodnutí a proč, změny postupu, co je špatně a jak to řešíme |
| `docs/DATA.md` | soubory, sloupce, rozložení, chybějící a chybné hodnoty, rozdělení, úpravy |
| `docs/POROZUMENI.md` | úloha a pojmy našimi slovy, proč tahle metoda, jak číst výsledky, limity, odpovědi mentorů |

Do deníku a pokusů se jen připisuje na konec a Git záznamy z různých větví spojí bez konfliktu. Jednou za hodinu někdo spustí `/denik`: Claude projde všechny větve, doplní, co se nezapsalo, a napíše krátké shrnutí. Čemu nerozumíme, na to se zeptáme v týmu nebo mentora.

Od 21:00 se z `docs/` skládá prezentace v tomto pořadí: problém, pro koho, data, postup, výsledek a jak víme, že funguje, demo, co dál. V sobotu ráno sepíšeme 15–20 pravděpodobných otázek poroty a necháme Claude hrát porotu (`/porota`).

## Claude

Každý má vlastní účet, a tedy i vlastní limit. Počítá se v pětihodinových oknech a k tomu je týdenní strop, stav ukáže příkaz `/usage`.

| Účet | Model | Agentů najednou |
|---|---|---|
| Max 20x (Ondra, Dan, Honza) | Opus na náročné věci (rozbor, návrh modelů, těžké chyby), Sonnet na rutinu | 1–3 podle toho, kolik stíháš kontrolovat |
| Pro (Tobias) | Sonnet (přepnout příkazem `/model`) | 1 |

- Spouštěj jen tolik agentů, kolik stíháš kontrolovat. Neověřený kód nepushuj.
- Každý moc dobrý výsledek je podezřelý, dokud ho nezkontroluje Ondra nebo subagent `kontrolor`.
- U každé větší změny ať Claude napíše do commitu co a proč. Porota se bude ptát „proč zrovna tohle?“.
- Bez internetu Claude nefunguje. Na místě hned ověřit Wi-Fi, zálohou je hotspot z mobilu.

**Pomohou další účty nebo placené GPU?** Na trénink ne. Claude model netrénuje, jen píše a spouští kód na našich počítačích. Další účty by přidaly jen další souběžné agenty, jenže brzdit nás bude kontrola výsledků, ne limit. Tři Max a jeden Pro stačí.

GPU zatím kupovat nemusíme. Na tabulková data stačí procesor. Na obrázky stačí GPU zdarma na Kaggle (kolem 30 hodin týdně) nebo v Google Colabu. Kdyby to nestačilo, dá se Colab Pro nebo GPU na hodiny (RunPod, vast.ai) koupit přímo na místě během pár minut. GeForce NOW nepomůže: je to streamování her a vlastní kód se na něm spustit nedá.

Kaggle má příkaz `kaggle`, přes který Claude Code umí poslat skript na GPU a stáhnout výsledek bez klikání v prohlížeči. Než tam nahrajeme data, zeptáme se pořadatelů, jestli smějí do cloudu.

Pokud vybereme úlohu s textem (chatbot nad dokumenty), může být jazykový model přímo součástí řešení. Aplikace pak potřebuje API klíč placený zvlášť podle spotřeby (předplatné ho nepokrývá), nebo lokální model přes Ollamu. Klíč patří do `.env`, nikdy do Gitu.

## Před odjezdem

Celý postup krok za krokem, i s vysvětlením proč, je v `PRIPRAVA.md`. Dá se vložit rovnou do Claude Code, který ho provede.

- [ ] Všichni: přijmout pozvánku, naklonovat, přepnout na svou větev, spustit `claude` se svým příkazem a zkušební `/sync` (postup v sekci Git)
- [ ] Všichni: Python 3.11 nebo novější, virtuální prostředí a balíčky níž
- [ ] Všichni: Claude Code nainstalovaný, přihlášený a vyzkoušený
- [ ] Všichni: účet Google kvůli Colabu a Disku
- [ ] Kdo bude trénovat na Kaggle: kroky 1–4 z `kaggle/README.md` (účet s ověřeným telefonem, `kaggle auth login`, test GPU)
- [ ] Majitelé Maců: `brew install libomp`, jinak LightGBM na Macu nejde spustit
- [ ] Majitelé Maců: ověřit, že PyTorch vidí GPU (příkaz níž)
- [ ] Všichni: vyzkoušet `streamlit hello`
- [ ] Všichni: přečíst [článek Datového centra](https://dcuk.cz/novinky/od-otazky-k-prototypu-co-se-da-vytvorit-za-jeden-hackathon/)
- [ ] Sbalit nabíječky, prodlužku, flashku, spacák a karimatku

```
python3 --version                # musí být 3.11 nebo novější; na Macu jinak brew install python@3.12 a dál python3.12
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install pandas numpy scikit-learn lightgbm xgboost optuna shap matplotlib plotly streamlit jupyter torch torchvision kaggle

# Mac: vidí PyTorch GPU? Má vypsat True.
python -c "import torch; print(torch.backends.mps.is_available())"
```

Na starším notebooku stačí bez `torch torchvision`.

## Zdroje

- [Hackathon ML/AI 2026, stránka akce](https://ksi.fjfi.cvut.cz/udalosti/hackathon-mlai-2026)
- [Hackathon 2023 je za námi](https://www.ksi.fjfi.cvut.cz/informacni-deska/hackathon-2023-je-za-nami)
- [Hackathon ML/AI 2024 zná své vítěze](https://ksi.fjfi.cvut.cz/informacni-deska/hackathon-mlai-2024-zna-sve-viteze)
- [Hackathon ML/AI 2024, mentoři Datového centra](https://dcuk.cz/novinky/hackathon-ml-ai-2024-2/)
- [Hackathon ML/AI 2025, výsledky](https://ksi.fjfi.cvut.cz/udalosti/hackathon-mlai-2025)
- [Hackathon ML/AI 2025, reportáž Datového centra](https://dcuk.cz/novinky/hackathon-ml-ai-2025-kdyz-se-data-potkaji-s-kavou-kodem-a-velkymi-napady/)
- [SPŠ Teplice, 3. místo 2025](https://www.sostp.cz/aktuality/891-nasi-zaci-opet-obstali-na-hackathonu)
- [Od otázky k prototypu (Datové centrum, 2026)](https://dcuk.cz/novinky/od-otazky-k-prototypu-co-se-da-vytvorit-za-jeden-hackathon/)
