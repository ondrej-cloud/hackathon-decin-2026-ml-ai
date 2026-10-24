# Provozní test: jak by model fungoval dnes naživo

Dan, so 24. 10. 2026 03:50–06:00, větev `dan-ridge`, kód `ridge_dan/provoz/`. Odpovídá na otevřenou otázku
v `docs/PREHLED.md`: s jakým zpožděním jsou data ČHMÚ v provozu. Test 2021–2025 se nespouštěl.

> **Upozornění:** předpovědi a varování před povodněmi vydává ČHMÚ a povodňové orgány. Naše porovnání s provozními
> daty a s předpovědí ČHMÚ je jen ukázka pro porotu; data ČHMÚ se tu nepoužívají k vydávání varování a naše
> předpověď varováním není.

## Shrnutí

- **Zpoždění dat je malé:** ČHMÚ zveřejňuje provozní data po 20 minutách v dávkách (:00, :20, :40 UTC) a poslední
  hodnota je v okamžiku zveřejnění stará 10–20 min (průtok v Kostelci 30 min). Hodnota z celé hodiny HH:00 je
  u všech 30 stanic venku nejpozději v HH:40.
- **Ale model na zpoždění citlivý je:** kdyby aplikace počítala v HH:00 a za chybějící poslední hodinu dosadila
  poslední známou hodnotu, týmový Ridge (Děčín +24 h) se v LOFO zhorší o 1,8 cm (15,3 → 17,1), při 3 h o 7 cm.
  Model si bere trend z poslední hodiny a ten se doplněním ztratí. **Doporučení: počítat v HH:45 z dat do HH:00**,
  ztráta je pak nulová a předpověď jen vyjde o 45 minut později.
- **V provozních datech chybí průtok Mělníka a Nymburka** (týmové stanice): Mělník má 1–2 hodnoty denně, Nymburk
  žádné. Doplnit jde bilancí: Mělník ≈ Vraňany + Kostelec před 3 h (chyba 2,3 %), Nymburk ≈ 1,1 × (Přelouč + Sány)
  před 6 h (6,6 %).
- **Živá ukázka (25. 9.–23. 10. 2026, nízký stav):** oficiální předpověď ČHMÚ je přesnější než naše (Děčín +24 h
  5,0 proti 7,5 cm, „jako teď“ 5,0). Při nízké vodě hladina denně kolísá o 10–30 cm (řízené odtoky) a náš model
  tyto výkyvy přenáší, jeho předpověď kmitá. Model byl laděný na povodně, ne na nízký stav.

## Odkud jsou provozní data

- `https://opendata.chmi.cz/hydrology/now/data/0-203-1-<DBC>.json`: posledních ~1,5 h po 10 min (H, Q, teplota vody)
  a poslední předpověď ČHMÚ H_F/Q_F; výpis složky ukazuje čas poslední změny každého souboru.
- `https://opendata.chmi.cz/hydrology/recent/data/<YYYYMMDD>_0-203-1-<DBC>.json`: denní soubory od 1. 1. 2026, H a Q
  po 10 min (Kostelec Q po 15 min) a **jedna předpověď ČHMÚ denně**: hodinová od D 11:00 UTC na 67 h dopředu.
- Staženo šetrně (po jednom, pauza 1,5–2 s, cache, nic dvakrát): 900 denních souborů (30 stanic × 24. 9.–23. 10.),
  výpis `now/` každých 10 min od 01:54 do 03:50 UTC a jen změněné soubory 30 stanic. Seznam adres v `STAZENO.csv`
  a `provoz/zaznamy_now.csv`. Data ČHMÚ jsou pod licencí CC BY 4.0, nejsou v Gitu.

## Zpoždění po stanicích

<!-- ZPOZDENI -->

## Co v provozu chybí a jak to doplnit

| Stanice | co chybí (25. 9.–23. 10.) | náhrada | chyba náhrady na roce 2025 |
|---|---|---|---|
| Mělník (Labe) | průtok: 1–2 hodnoty denně (658 z 720 hodin doplněno) | 1,00 × (Vraňany + Kostelec) před 3 h | 2,3 % (3,6 m³/s) |
| Nymburk (Labe) | průtok úplně (708 hodin) | 1,125 × (Přelouč + Sány) před 6 h | 6,6 % (3,0 m³/s) |
| Praha-Chuchle | průtok, 32 hodin | poslední známá hodnota ≤ 2 h (21 h), zbytek bez předpovědi | |
| ostatní | 1–8 hodin výpadků | poslední známá hodnota ≤ 2 h | |

Koeficienty bilance jsou z tréninkových let 2006–2018. Měrná křivka ze stavu by byla horší (Mělník 20 %, Nymburk 33 %
na roce 2025), protože Mělník ovlivňuje vzdutí pod soutokem. Doplnění je jen pro ukázku; do aplikace patří až po
ověření na povodních.

## Dopad zpoždění na chybu (LOFO-CV 22 povodní, Děčín, bez ladění)

Vstupy všech stanic o d hodin starší. „Naivně“ = model natrénovaný na čerstvých datech, chybějící poslední hodiny
doplněné poslední známou hodnotou (vstup „před z h“ = hodnota v t − max(z, d)). „Model ví“ = model natrénovaný na
stejně starých vstupech (předpověď na h + d hodin z čerstvých dat). Zhoršení proti čerstvým vstupům v cm:

| Model (čerstvě) | 1 h naivně / model ví | 2 h | 3 h | 6 h |
|---|---|---|---|---|
| týmový Ridge 24 h (15,29) | +1,79 / +0,80 | +4,03 / +1,62 | +7,01 / +2,47 | +15,29 / +5,23 |
| Ridge 30 stanic 24 h (14,79) | +1,25 / +0,64 | +3,18 / +1,31 | +5,79 / +2,00 | +12,56 / +4,25 |
| týmový Ridge 36 h (26,39) | +2,09 / +1,03 | +4,68 / +2,06 | +8,40 / +3,11 | +17,97 / +6,29 |
| Ridge 30 stanic 36 h (23,96) | +1,75 / +0,88 | +4,35 / +1,78 | +7,90 / +2,71 | +15,86 / +5,57 |

Při naměřeném zpoždění a výpočtu v HH:45 jsou všechny vstupy z HH:00 k dispozici, zhoršení je 0. Při výpočtu v HH:00
platí řádek „1 h naivně“.

Citlivost na jednu stanici (Ridge 30, 24 h, jen ta stanice o 6 h starší, ostatní čerstvé): Děčín sám +1,14 cm,
Mělník +0,60, Zbraslav +0,41, Praha +0,39, Kostelec +0,35, Jizera Bakov +0,24, ostatní do +0,2. Na zpoždění vlastního
vodočtu a stanic na Vltavě a Labi těsně nad Mělníkem záleží nejvíc, vzdálené přítoky skoro nevadí.

Simulace bez úniku z budoucnosti potvrzena Codexem (m), viz `NALEZY_CODEX.md`.

## Živá ukázka proti ČHMÚ (`grafy/provoz_ridge_chmu.png`)

Provozní data 24. 9.–23. 10. 2026 (hodnota v celou hodinu), týmový Ridge natrénovaný jako `src/uloz_model.py`
(trénovací část 2006–2018), Ridge 30 na 36 h z `models/ridge30_<cil>_36.joblib` (2006–2025). Předpověď ČHMÚ beru jako
vydanou v 11:00 UTC (začátek její hodinové řady); náš model vydávám ve stejný čas z dat do 11:00 UTC. 29 dní:

| Průměrná chyba (cm) | ČHMÚ | týmový Ridge | Ridge 30 | jako teď | rozsah reality |
|---|---|---|---|---|---|
| Děčín +24 h | **5,0** | 7,5 | | **5,0** | 81–106 cm |
| Děčín +36 h | **5,7** | 8,1 | 6,4 | 6,8 | |
| Ústí +24 h | **6,0** | 8,5 | | 9,0 | 115–149 cm |
| Ústí +36 h | **6,0** | 8,7 | 8,0 | 8,1 | |

Průměrný posun (bias): ČHMÚ v Děčíně −4,2 cm (podstřeluje), naše modely −1,9 až +2,7 cm. Rozdíl je v šumu: hodinová
změna naší předpovědi má směrodatnou odchylku 6,4 cm (Ridge 30 na 36 h 4,9), reality 2,3 cm. Model bere hodinové
průtoky proti proudu, které při nízké vodě kolísají podle odtoku z vodních děl, a přenáší je do předpovědi.
Ukázka je jen nízký stav (žádná povodeň), o přesnosti na povodních nic neříká; ČHMÚ navíc vydává jednu předpověď
denně a přesný čas vydání (11:00 UTC) je náš předpoklad.

## Doporučení pro aplikaci

1. Počítat předpověď v HH:45 z hodnot do HH:00 (všech 30 stanic je venku), ne v HH:00. Platnost předpovědi zobrazit
   od času dat (HH:00 + h), ne od času výpočtu.
2. Nikdy nedoplňovat chybějící poslední hodiny poslední známou hodnotou mlčky: ztrácí se trend, +1,8 cm už při 1 h.
   Když některá stanice chybí víc než hodinu, použít model natrénovaný bez ní nebo na starší data (zhruba poloviční
   ztráta) a zobrazit upozornění se stářím dat.
3. Průtok Mělníka a Nymburka v provozu nebrat z ČHMÚ (chybí), ale dopočítat bilancí (viz tabulka).
4. Při nízké vodě předpověď kmitá: zobrazovat ji vyhlazenou nebo jen na povodňové stavy (to jsme netestovali).
5. Vedle naší předpovědi vždy ukázat oficiální předpověď a výstrahy ČHMÚ s odkazem; naše předpověď není varování.
