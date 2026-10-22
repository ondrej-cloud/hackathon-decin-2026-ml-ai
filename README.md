# Hackathon ML/AI 2026 – plán týmu

FJFI ČVUT Děčín, od pátku 23. 10. 14:00 do soboty 24. 10. 17:00. Soutěž startuje v pátek v 16:00. V sobotu ve 14:00 odevzdáváme a od 14:30 prezentujeme porotě, každý tým nejvýš 15 minut. Ceny jsou 25, 15 a 10 tisíc Kč.

Každý má svou roli, svůj počítač a své soubory ve společném soukromém repozitáři na GitHubu. Pracujeme paralelně a nepřepisujeme si práci.

## Jak se tu vyhrávalo

| Ročník | Týmy / úlohy | 1. místo | Úloha vítěze | Co o tom víme |
|---|---|---|---|---|
| 2023 | 6 / 3 | SPŠE Plzeň | klasifikace fraktografických snímků (obrázky) | Porota hodnotila matematický model, grafické rozhraní a prezentaci. Stejnou úlohu řešilo i 3. místo. |
| 2024 | 10 / 5 | Robin & Honza, Gymnázium Děčín (dva lidi) | Energetický detektiv: poznat charakter objektu podle spotřeby energie (data Datového centra ÚK) | Mentoři z Datového centra se nejvíc věnovali týmům s jejich zadáním a jeden z těch týmů vyhrál. Týmy, které se mentorů neptaly, podle nich dopadly hůř. 2. a 3. místo měly klasifikaci výbojů z tokamaku GOLEM. |
| 2025 | 13 / 4 | Koranderium, SPŠ Tábor | nezveřejněno | 3. místo (SPŠ Teplice) mělo chatbota nad úředními deskami. Porota ocenila, že data nejen zpracoval, ale i srozumitelně vysvětlil. |

V roce 2024 porota hodnotila čtyři věci: splnění zadání, zvolený postup (vhodné metody, úpravu dat), odbornost řešení a prezentaci. Seděli v ní lidé z FJFI, z Datového centra a z IT firem.

### Co z toho plyne pro nás

1. **Za mentory chodit od první hodiny.** Sedí v porotě a vědí, co zadavatel opravdu potřebuje. Chodíme za nimi s konkrétními otázkami: na začátku s nápadem, večer s prvními výsledky, ráno s finální verzí.
2. **Každé kritérium má svého člověka.** Splnění zadání ověří Ondra u mentora hned na začátku a pak ho hlídá. Za postup odpovídají Ondra a Dan. Odbornost znamená, že každý umí vysvětlit svou část a Ondra celek. Prezentace je Tobiasova.
3. **Demo, kterému rozumí laik.** V roce 2023 se hodnotilo grafické rozhraní, v roce 2025 porota ocenila srozumitelný výstup. Tohle zajistí Honzova aplikace.
4. **Úloha, ve které budeme mít ve 21:00 celý řetězec.** V roce 2024 vyhrála úloha od Datového centra. Rozhoduje ale hlavně to, jestli v ní stihneme ověřený výsledek a jestli k ní máme ochotného mentora.
5. **Počet lidí nerozhoduje.** V roce 2024 vzaly 1. i 2. místo dvoučlenné týmy. Naše výhoda jsou tři účty Claude Max, díky kterým zkusíme víc přístupů. AI ale nejspíš budou používat i ostatní, takže rozhodne poctivé ověření, to, že řešení rozumíme, a prezentace.
6. **Dotáhnout to do konce.** V roce 2024 porota veřejně pokárala tým, který soutěž nebral vážně, a v roce 2025 jeden tým nedokončil. Celý řetězec ve 21:00 je naše pojistka.

## Kdo co dělá

| Kdo | Počítač | Claude | Role |
|---|---|---|---|
| Ondra | MacBook M1, 16 GB | Max 20x | vedení, ověřování, data |
| Dan | Lenovo Yoga 7i (Core Ultra 7 155H) | Max 20x | model a trénink |
| Honza | starší notebook | Max 20x | aplikace a vizualizace |
| Tobias | MacBook M4, 16 GB | Pro | prezentace, deník, počítač na demo |

**Ondra: vedení, ověřování, data**
- vede výběr tématu a rozhovory s mentory, hlídá čas a rozhoduje, když se neshodneme
- v první hodině rozdělí data na trénovací, validační a testovací část a napíše `evaluate.py`, jediné měření pro všechny
- výsledek se počítá, až ho zkontroluje: správná data, žádný únik testovacích dat, čísla dávají smysl
- testovací sadu pustí jen jednou, na finální model
- mezitím upravuje data a vymýšlí nové veličiny (`features.py`)
- rozumí celému řešení a odpovídá porotě na technické otázky

**Dan: model a trénink**
- začne jednoduchým modelem a postupuje k nejlepšímu, každý pokus vyhodnotí přes `evaluate.py`
- tabulková data a gradient boosting běží na procesoru Yogy, GPU na to není potřeba
- neuronové sítě trénuje zdarma na GPU na Kaggle nebo v Google Colabu, menší pokusy může pustit na Tobiasově M4
- před spaním pošle dlouhý trénink na Kaggle, kde běží, i když notebook spí
- dodá `predict.py` a finální model

**Honza: aplikace a vizualizace**
- od první hodiny staví aplikaci ve Streamlitu s falešnou předpovědí, později napojí skutečný model
- dělá grafy, kterým rozumí i člověk mimo obor
- aplikace musí jít spustit na Tobiasově Macu, ze kterého budeme prezentovat (Honzův notebook finální model utáhnout nemusí)
- natočí záložní video dema pro případ, že na prezentaci něco selže

**Tobias: prezentace, deník, uživatel**
- hned po výběru tématu sepíše zadání do `CLAUDE.md`
- hlídá otázku, kterou zdůrazňují pořadatelé: komu řešení pomáhá a jak poznáme, že funguje
- vede deník `docs/DENIK.md` (co se změnilo, proč a s jakým výsledkem) a zkouší aplikaci jako laik
- chodí s Ondrou za mentory a zapisuje, co řekli
- skládá prezentaci, jeho M4 je počítač na demo

Pokud vybereme úlohu s chatbotem: Dan postaví vyhledávání v dokumentech a napojení na jazykový model, Ondra připraví testovací otázky se správnými odpověďmi a měření, Honza chatovací rozhraní.

## Pátek do 17:30: výběr tématu

**14:00–15:30:** Příjezd, rozložit se a hned ověřit, že na místní Wi-Fi funguje Claude Code (záloha je hotspot z mobilu). Kdo chce, jde na úvod do strojového učení (14:30–15:30).

**15:30–17:30:**
1. Představení témat. Všichni poslouchají a píšou si.
2. Projdeme každé téma: jaká jsou data, co z toho jde za 22 hodin udělat, komu to pomůže. Vybereme jedno.
3. Brainstorming: komu řešení pomáhá a proč, kdo je cílový uživatel, jak to bude fungovat a jak poznáme, že funguje (metrika).
4. S prvním návrhem za mentory a upravit ho podle jejich zpětné vazby. Když se nápad nelíbí, vracíme se k bodu 2.
5. Nejpozději v 17:30 je rozhodnuto. Domluvíme, co bere a co vrací `predict.py`, a jdeme pracovat. Kdybychom se rozhodovali déle, nestihneme mít ve 21:00 celý řetězec.

## Harmonogram

Kontrolní body, kde se všichni na 10 minut sejdeme:

| Čas | Co musí platit |
|---|---|
| 19:00 | data jsou rozdělená, `evaluate.py` hotové, máme první jednoduchý model a kostru aplikace |
| 21:00 | celý řetězec od dat po aplikaci funguje, i když je model ještě slabý |
| 0:00 | stav a plán na noc, Dan chystá dlouhý trénink |
| 8:00 | výsledky z noci, vybíráme finální přístup |
| 11:00 | konec nových funkcí, dál už jen opravy a nácvik |
| 14:00 | odevzdání prezentace |

| Čas | Ondra | Dan | Honza | Tobias |
|---|---|---|---|---|
| 17:30–19:00 | rozbor dat, rozdělení dat, `evaluate.py` | první jednoduchý model | kostra aplikace s falešnou předpovědí | zadání do `CLAUDE.md`, komu řešení pomáhá |
| 19:00–21:00 | nové veličiny, kontrola prvních výsledků | pokusy s různými modely | napojení prvního modelu | deník, s Ondrou za mentory, osnova prezentace |
| 21:00–1:00 | kontrola úniku dat, plán na noc | ladění, v 1:00 pošle dlouhý trénink | grafy pro laiky | prezentace podle deníku |
| 1:00–5:00 | další úprava dat, hlídá noční trénink | spí | spí | grafika a texty prezentace |
| 5:00–8:00 | spí | vyhodnotí noční trénink | ladění aplikace | spí |
| 8:00–11:00 | výběr finálního modelu, jeden test na testovací sadě | finální model do `predict.py` | finální model v aplikaci na Tobiasově Macu | výsledky a grafy do prezentace |
| 11:00–14:00 | otázky poroty, nácvik | jen opravy, nácvik | záložní video dema, nácvik | dva nácviky celé prezentace, odevzdání |

Na jídlo podle programu (večeře 18–19, snídaně 7:30–9, oběd 12–13) chodíme postupně, ať práce nestojí.

## Repozitář

Každý soubor má jednoho vlastníka a jen ten ho mění, ostatní ho jen čtou. Tím odpadne většina konfliktů v Gitu.

```
hackathon-2026/
├── CLAUDE.md          Tobias   zadání, data, metrika, pravidla
├── data/
│   ├── raw/           nikdo    data od pořadatelů, NE do Gitu
│   └── split/         Ondra    pevné rozdělení train / val / test
├── src/
│   ├── evaluate.py    Ondra    jediné měření úspěšnosti
│   ├── features.py    Ondra    úprava dat a nové veličiny
│   ├── train_*.py     Dan      jeden soubor na přístup
│   └── predict.py     Dan      predict(vstup) -> výstup, používá aplikace
├── results/           všichni  jeden nový soubor na pokus
├── models/            Dan      malé modely, velké přes Google Disk
├── app/               Honza    Streamlit aplikace
└── docs/              Tobias   DENIK.md, prezentace, otázky poroty
```

Tři pravidla:

1. **Testovací sadu má na starosti Ondra.** Při ladění se používá jen validační část. Test se pustí jednou, na finální model.
2. **Jedno měření pro všechny.** Každý pokus se hodnotí přes `src/evaluate.py` a uloží jako nový soubor `results/<jméno>-<čas>-<popis>.json`. Když má každý pokus vlastní soubor, nevznikají konflikty.
3. **`predict.py` je dohoda mezi modelem a aplikací.** Honza zatím používá falešnou verzi, Dan ji pak vymění za skutečnou.

Claude Code čte `CLAUDE.md` automaticky při každém startu, takže všichni čtyři Claude mají stejný kontext. Na začátku každé relace stačí napsat: „Jsem Dan, přečti CLAUDE.md.“

```markdown
# Hackathon ML/AI 2026

## Zadání
(Tobias doplní hned po výběru tématu: co řešíme, pro koho, jak poznáme úspěch)

## Data
(kde leží: data/raw/, co obsahují, sloupce, velikost)

## Metrika
(jedna metrika, např. F1 nebo MAE; počítá ji jen src/evaluate.py na validační části)

## Kdo vlastní které soubory
- Ondra: data/split/, src/evaluate.py, src/features.py
- Dan: src/train_*.py, src/predict.py, models/
- Honza: app/
- Tobias: CLAUDE.md, docs/

## Pravidla pro Claude
- Měň jen soubory toho, kdo s tebou pracuje. Cizí soubory jen čti.
- Nikdy netrénuj ani nelaď na testovací části z data/split/.
- Každý pokus vyhodnoť přes src/evaluate.py a ulož jako nový soubor v results/.
- Po každém funkčním kroku: git pull --rebase, commit jen svých souborů, git push.
- Do commitu napiš jednou větou, co a proč.
- Nikdy git push --force. Data a .env nikdy do Gitu.
```

## Git

Všichni pracujeme přímo ve větvi `main`, každý jen ve svých souborech. Na 22 hodin je to rychlejší než větve a pull requesty.

**Dnes večer, Ondra:**

1. Na GitHubu založí repozitář `hackathon-2026` jako **Private**, bez README, `.gitignore` i licence. Všechno už je připravené a pushne se. Data od pořadatelů můžou být citlivá, proto Private.
2. V Settings → Collaborators pozve ostatní tři. Pozvánku přijmou v e-mailu.

`.gitignore` v repozitáři hlídá, aby se do Gitu nedostala data (`data/raw/`), virtuální prostředí, klíče (`.env`, `kaggle.json`) a velké modely.

**Dnes večer, každý:**

1. Přihlásit se: `gh auth login` (nebo přes GitHub Desktop).
2. Naklonovat: `git clone https://github.com/ondrej-cloud/hackathon-2026.git`
3. Zkušební commit: vytvořit `docs/test-<jméno>.txt`, pak `git add`, `git commit` a `git push`. Komu to projde, má přístup v pořádku.

**Pracovní cyklus během hackathonu:**

1. `git pull --rebase` stáhne práci ostatních.
2. Pracuješ se svým Claude jen ve svých souborech.
3. `git add` jen na svoje soubory, nikdy naslepo `git add .`
4. `git commit -m "Dan: LightGBM, val F1 0,81"`
5. `git push`

Cyklus opakuj po každém funkčním kroku, nejméně jednou za hodinu. Celý ho zvládne Claude, stačí mu říct „commitni a pushni“.

**Když něco nejde:**
- Push je odmítnutý: nejdřív `git pull --rebase`, pak push znovu.
- Konflikt: řekni Claude „vyřeš konflikt a zachovej změny obou stran“. Nikdy `git push --force`.
- Data a velké modely: přes AirDrop, flashku nebo Google Disk, u všech do stejné složky `data/raw/`.

## Deník a přehled

Tobias každou hodinu, nebo když někdo napíše „pushnuto“:

1. `git pull`
2. Řekne Claude: „Shrň, co se v repozitáři změnilo za poslední hodinu (git log a git diff). Vysvětli to jednoduše, tak aby se to dalo říct porotě, a připiš to do docs/DENIK.md.“
3. Čemu nerozumí, na to se zeptá v týmu. Dvě věty vysvětlení ušetří půl hodiny čtení kódu.

Ondra deník průběžně čte a opravuje, co v něm technicky nesedí.

```markdown
## 21:15
- Změna: Dan přešel z Random Forest na LightGBM
- Proč: o 6 % lepší F1 na validačních datech
- Výsledek: F1 0,81 (results/dan-2110-lgbm.json)
- Otázka pro mentory: je F1 pro zadavatele ta správná metrika?
```

**Prezentace:** Od 21:00 ji Tobias skládá z deníku v tomto pořadí: problém, pro koho, data, postup, výsledek a jak víme, že funguje, demo, co dál. V sobotu ráno s Ondrou sepíšou 15–20 pravděpodobných otázek poroty a nechají Claude hrát porotu.

## Claude

Každý má vlastní účet, a tedy i vlastní limit. Počítá se v pětihodinových oknech a k tomu je týdenní strop, stav ukáže příkaz `/usage`.

| Kdo | Model | Agentů najednou |
|---|---|---|
| Ondra | Opus na rozbor dat a kontroly, Sonnet na rutinu | 1–2 |
| Dan | Opus na návrh a ladění modelů, Sonnet na rutinu | 2–3 |
| Honza | Sonnet, Opus jen na těžké chyby | 1–2 |
| Tobias | Sonnet (přepnout příkazem `/model`) | 1 |

- Spouštěj jen tolik agentů, kolik stíháš kontrolovat. Neověřený kód nepushuj.
- Každý moc dobrý výsledek je podezřelý, dokud ho Ondra nezkontroluje.
- U každé větší změny ať Claude napíše do commitu co a proč. Porota se bude ptát „proč zrovna tohle?“.
- Bez internetu Claude nefunguje. Na místě hned ověřit Wi-Fi, zálohou je hotspot z mobilu.

**Pomohou další účty nebo placené GPU?** Na trénink ne. Claude model netrénuje, jen píše a spouští kód na našich počítačích. Další účty by přidaly jen další souběžné agenty, jenže brzdit nás bude kontrola výsledků, ne limit. Tři Max a jeden Pro stačí.

GPU zatím kupovat nemusíme. Na tabulková data stačí procesor. Na obrázky stačí GPU zdarma na Kaggle (kolem 30 hodin týdně) nebo v Google Colabu. Kdyby to nestačilo, dá se Colab Pro nebo GPU na hodiny (RunPod, vast.ai) koupit přímo na místě během pár minut. GeForce NOW nepomůže: je to streamování her a vlastní kód se na něm spustit nedá.

Kaggle má příkaz `kaggle`, přes který Claude Code umí poslat skript na GPU a stáhnout výsledek bez klikání v prohlížeči. Než tam nahrajeme data, zeptáme se pořadatelů, jestli smějí do cloudu.

Pokud vybereme úlohu s textem (chatbot nad dokumenty), může být jazykový model přímo součástí řešení. Aplikace pak potřebuje API klíč placený zvlášť podle spotřeby (předplatné ho nepokrývá), nebo lokální model přes Ollamu. Klíč patří do `.env`, nikdy do Gitu.

## Dnes večer

- [ ] Ondra: založit soukromý repozitář, pozvat ostatní, `.gitignore`, `CLAUDE.md` ze šablony
- [ ] Všichni: zkušební commit a push
- [ ] Všichni: Python 3.11 nebo novější, virtuální prostředí a balíčky níž
- [ ] Všichni: Claude Code nainstalovaný, přihlášený a vyzkoušený
- [ ] Všichni: účet Google kvůli Colabu a Disku
- [ ] Dan: účet na Kaggle s ověřeným telefonem (bez něj nejde GPU), API token, vyzkoušet poslat skript na GPU
- [ ] Ondra a Tobias: ověřit, že PyTorch vidí GPU Macu (příkaz níž)
- [ ] Honza: spustit ukázkovou aplikaci `streamlit hello`; PyTorch instalovat nemusí, finální demo poběží u Tobiase
- [ ] Tobias: založit prázdný `docs/DENIK.md`
- [ ] Všichni: přečíst [článek Datového centra](https://dcuk.cz/novinky/od-otazky-k-prototypu-co-se-da-vytvorit-za-jeden-hackathon/)
- [ ] Sbalit nabíječky, prodlužku, flashku, spacák a karimatku

```
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install pandas numpy scikit-learn lightgbm matplotlib plotly streamlit jupyter torch torchvision

# Mac: vidí PyTorch GPU? Má vypsat True.
python -c "import torch; print(torch.backends.mps.is_available())"
```

## Zdroje

- [Hackathon ML/AI 2026, stránka akce](https://ksi.fjfi.cvut.cz/udalosti/hackathon-mlai-2026)
- [Hackathon 2023 je za námi](https://www.ksi.fjfi.cvut.cz/informacni-deska/hackathon-2023-je-za-nami)
- [Hackathon ML/AI 2024 zná své vítěze](https://ksi.fjfi.cvut.cz/informacni-deska/hackathon-mlai-2024-zna-sve-viteze)
- [Hackathon ML/AI 2024, mentoři Datového centra](https://dcuk.cz/novinky/hackathon-ml-ai-2024-2/)
- [Hackathon ML/AI 2025, výsledky](https://ksi.fjfi.cvut.cz/udalosti/hackathon-mlai-2025)
- [Hackathon ML/AI 2025, reportáž Datového centra](https://dcuk.cz/novinky/hackathon-ml-ai-2025-kdyz-se-data-potkaji-s-kavou-kodem-a-velkymi-napady/)
- [SPŠ Teplice, 3. místo 2025](https://www.sostp.cz/aktuality/891-nasi-zaci-opet-obstali-na-hackathonu)
- [Od otázky k prototypu (Datové centrum, 2026)](https://dcuk.cz/novinky/od-otazky-k-prototypu-co-se-da-vytvorit-za-jeden-hackathon/)
