# Pásmo nejistoty předpovědi: zpráva

Dan, větev `dan-nejistota` (z `origin/main` 59956c9), noc 23./24. 10. 2026. Průběh v `PRUBEH.md`, nálezy Codexu
v `NALEZY_CODEX.md`. Test 2021–2025 se nepoužil.

## Shrnutí

- Ke každé předpovědi (Děčín a Ústí, 12/24/36 h) je pásmo, do kterého má skutečnost padnout v 80 % a 95 % hodin.
  Počítá se pro týmový Ridge (finální model) a pro Danovy kandidáty Ridge 30 stanic a G3 (½ Ridge 30 + ½ LightGBM 30).
- **Dnešní týmové pásmo je na povodních moc úzké.** `src/nejistota.py` bere chyby modelu na učicích datech (kde je model
  zná) a ve vnořené kontrole na 22 povodních 2006–2020 „80% pásmo“ v jeho stylu pokrývá jen 58–72 % hodin, při rychlém
  vzestupu 27 % a na začátku vzestupu 15 %. Aplikace ukazuje 90% pásmo z téhož postupu.
- **Nové pásmo** bere chyby předpovědí mimo trénink (LOFO přes 22 povodní) zvlášť podle toho, jakou změnu model čeká
  (6 pásem předpovězené změny). Ve vnořené kontrole (pásmo každé povodně jen z ostatních povodní) pokrývá **79–80 %**
  (cíl 80 %) a **94–95 %** (cíl 95 %) u všech tří modelů, obou stanic a všech horizontů.
- **Slabina zůstává na vzestupu:** když hladina za horizont stoupne aspoň o 50 cm, 80% pásmo pokrývá 59–72 % hodin, na
  začátku vzestupu 60–69 %, 95% pásmo 82–91 %. Model začátek vzestupu podceňuje a z toho, co je známé v čase vydání,
  se to nedá poznat (zkoušeno: trend za 6 h, výška hladiny, průtok v Mělníku, poslední ověřená chyba).
- **Rekordní povodeň 6/2013** je mimo rozsah: 80% pásmo 42 % hodin, 95% pásmo 66 %. Nejhorší povodeň má u každého
  modelu pokrytí 36–54 % (80 %).
- **Na modelu, který aplikace používá pro přehrávání** (Ridge učený do 2018), je nové 80% pásmo na neviděných validačních
  povodních opatrnější, než musí: 84–88 %, v klidu 2019–2020 86–94 %. Pro „Dnešek“ (model učený do 2025) se to ověřit
  nedá.
- Šířka 80% pásma (Děčín +24 h): týmový Ridge 47 cm, Ridge 30 46 cm, **G3 43 cm** (nejpřesnější model má nejužší
  pásmo při stejném pokrytí). Dnešní týmové pásmo má 32 cm, ale netrefí se do něj třetina hodin.

## Metoda

1. **Předpovědi mimo trénink** (`oof.py`): leave-one-flood-out přes 22 povodní 2006–2020 se stejnými foldy jako ostatní
   (`kandidati/lofo_foldy.csv`): fold drží okno povodně (7 dní před až 5 dní po vrcholu) a z tréninku vyřadí okno
   ± 20 dní. Pro Ústí stejné časy oken. Týmový Ridge a Ridge 30 ze součtů (shoda se sklearn 6·10⁻⁹ cm), LightGBM 30
   přesně jako uvnitř `g3.py` (přísná doba doběhu), G3 = ½ + ½. Kontrola: LOFO Děčín +24 h 15,29 / 14,79 / 13,91 cm
   (Danovy výsledky 15,29 / 14,79 / 13,94; LightGBM 30 16,05 proti 16,06).
2. **Chyba** e = skutečnost − předpověď. **Skupiny** podle toho, co je známé v čase vydání: předpovězená změna
   d = předpověď − stav teď v 6 pásmech (≤ −P, −P až −P/3, ±P/3, P/3 až P, P až 2P, ≥ 2P; P = 10 / 20 / 30 cm pro
   12 / 24 / 36 h). V každé skupině dolní a horní kvantil chyb (pořadí s opravou n + 1), pásmo = [předpověď + dolní,
   předpověď + horní], tedy nesymetrické. Skupina s méně než 200 hodinami dostane kvantily ze všech chyb.
3. **Vnořené ověření** (`overeni.py`): pásmo povodně k jen z chyb povodní mimo její blok (14 bloků: povodně, jejichž
   mezery ± 20 dní se překrývají, např. 12/2012 a 1/2013, jejichž okna sdílejí 48 h). Pokrytí, šířka a intervalové skóre
   (šířka + 2/α × o kolik skutečnost pásmo minula) po povodních, po režimech v čase vydání a po skutečném vývoji.
4. **Výběr varianty** předem daným pravidlem: nejmenší průměrné intervalové skóre, pokud pokrytí nikde neklesne o víc
   než 3 p. b. pod cíl. Varianty: jedno pásmo pro vše 128,4, trend za 6 h 123,7, vzestup/pokles/klid 121,4, totéž × výška
   124,4, **6 pásem změny 120,0** (vybraná). U týmového Ridge samotného: nové 125, dnešní týmové 167. Mimo pravidlo zkoušeno a zamítnuto: signál z Mělníka
   a poslední ověřená chyba (horší skóre i pokrytí při vzestupu). Výběr i hodnocení jsou na stejných povodních, rozdíly
   mezi variantami jsou ale malé (do 7 %).
5. **Kvantily pro aplikaci** (`kvantily.json`) ze všech 22 povodní, s počtem hodin a povodní za každou skupinou.
6. **Přísná kontrola** (`prisne.py`): modely ostatních povodní při obyčejném LOFO povodeň k viděly. U Ridge a Ridge 30
   jsou chyby pro kalibraci znovu spočítané modely bez celého bloku povodně k. Výsledek (průměr přes oba Ridge,
   cíle a horizonty): 80% pásmo 79,4 % přísně proti 78,9 % obyčejně, šířka 54,3 proti 54,0 cm, rychlý vzestup 66,8
   proti 66,5 %; 95% pásmo 94,2 proti 94,0 %. Obyčejné vnoření tedy pokrytí nepřikrašluje (`vysledky/prisne_vnorene.csv`).

## Výsledky (vnořeně po blocích, 22 povodní 2006–2020)

Pokrytí v % hodin, šířka pásma v cm. „Rychlý vzestup“ = za horizont stoupne aspoň o 50 cm, „začátek vzestupu“ = navíc
posledních 6 h stouplo méně než o 10 cm. Dnešní týmové = pásmo z `src/nejistota.py` stejné úrovně.

### Pásmo 80 %

| model | cíl | h | pokrytí | šířka | rychlý vzestup | začátek vzestupu | pokles | nejhorší povodeň | dnešní týmové |
|---|---|---|---|---|---|---|---|---|---|
| Ridge (tým) | Děčín | 12 | 79 | 25 | 61 | 61 | 74 | 41 | 72 |
| | Děčín | 24 | 80 | 47 | 69 | 60 | 77 | 42 | 66 |
| | Děčín | 36 | 79 | 84 | 71 | 63 | 75 | 53 | 58 |
| | Ústí | 12 | 79 | 30 | 64 | 61 | 73 | 40 | 71 |
| | Ústí | 24 | 79 | 54 | 69 | 63 | 76 | 49 | 65 |
| | Ústí | 36 | 79 | 90 | 70 | 62 | 75 | 54 | 59 |
| Ridge 30 | Děčín | 12 | 79 | 26 | 59 | 69 | 74 | 42 | |
| | Děčín | 24 | 79 | 46 | 66 | 66 | 76 | 40 | |
| | Děčín | 36 | 78 | 79 | 69 | 66 | 76 | 47 | |
| | Ústí | 12 | 79 | 30 | 63 | 65 | 74 | 40 | |
| | Ústí | 24 | 79 | 51 | 66 | 66 | 76 | 40 | |
| | Ústí | 36 | 79 | 86 | 71 | 67 | 76 | 43 | |
| G3 | Děčín | 12 | 79 | 25 | 65 | 68 | 75 | 39 | |
| | Děčín | 24 | 79 | 43 | 70 | 66 | 77 | 36 | |
| | Děčín | 36 | 79 | 78 | 72 | 68 | 76 | 41 | |
| | Ústí | 12 | 79 | 28 | 67 | 64 | 75 | 43 | |
| | Ústí | 24 | 79 | 48 | 70 | 67 | 77 | 46 | |
| | Ústí | 36 | 79 | 86 | 71 | 67 | 75 | 46 | |

### Pásmo 95 %

| model | cíl | h | pokrytí | šířka | rychlý vzestup | začátek vzestupu | pokles | nejhorší povodeň | dnešní týmové |
|---|---|---|---|---|---|---|---|---|---|
| Ridge (tým) | Děčín | 12 | 94 | 51 | 83 | 88 | 92 | 64 | 90 |
| | Děčín | 24 | 94 | 94 | 87 | 82 | 92 | 66 | 85 |
| | Děčín | 36 | 94 | 147 | 90 | 88 | 91 | 75 | 81 |
| | Ústí | 12 | 94 | 61 | 83 | 86 | 91 | 57 | 89 |
| | Ústí | 24 | 94 | 106 | 88 | 85 | 91 | 64 | 85 |
| | Ústí | 36 | 94 | 161 | 91 | 89 | 90 | 78 | 81 |
| Ridge 30 | Děčín | 12 | 94 | 54 | 82 | 88 | 92 | 60 | |
| | Děčín | 24 | 94 | 92 | 87 | 84 | 92 | 56 | |
| | Děčín | 36 | 94 | 140 | 89 | 88 | 92 | 72 | |
| | Ústí | 12 | 94 | 63 | 84 | 86 | 91 | 54 | |
| | Ústí | 24 | 94 | 104 | 88 | 84 | 91 | 61 | |
| | Ústí | 36 | 94 | 152 | 90 | 88 | 90 | 75 | |
| G3 | Děčín | 12 | 95 | 46 | 87 | 88 | 92 | 69 | |
| | Děčín | 24 | 94 | 84 | 87 | 84 | 93 | 62 | |
| | Děčín | 36 | 94 | 139 | 89 | 89 | 91 | 57 | |
| | Ústí | 12 | 94 | 54 | 84 | 85 | 92 | 61 | |
| | Ústí | 24 | 94 | 93 | 89 | 86 | 92 | 65 | |
| | Ústí | 36 | 94 | 149 | 90 | 89 | 91 | 69 | |

Průměr přes cíle a horizonty (80 %): týmový Ridge pokrytí 79,1 %, šířka 55 cm, rychlý vzestup 67 %, začátek 62 %,
pokles 75 %, klid 86 %; Ridge 30 78,8 / 53 / 66 / 66 %; G3 79,2 / 51 / 69 / 67 %. Dnešní týmové 65,2 % / 32 cm /
27 % / 15 %. Po povodních a po režimech: `vysledky/pokryti_povodne.csv`, `vysledky/pokryti_rezimy.csv`.

Po povodních (týmový Ridge, Děčín +24 h): 80% pásmo pokrývá u 19 z 22 povodní 74–93 % hodin, horší jsou 6/2009 (63 %),
8/2010 (62 %) a 6/2013 (42 %). 95% pásmo u 18 z 22 povodní 93–100 %, horší 8/2010 (81 %), 9/2010 (86 %), 6/2013 (66 %)
a druhá vlna 6/2013 (86 %). Na vrcholu rekordní povodně model čeká malou změnu, takže pásmo je úzké, a skutečnost leží
až 100 cm nad ním (`grafy/pasmo_2013-06-05.png`).

### Model aplikace na neviděných datech

Ridge učený na trénovací části 2006–2018 (jako `app/predikce.py`), pásmo nové metody, validace týmového splitu
(4 povodně: kvantily bez bloku té povodně; klid 2019–2020: kvantily ze všech 22 povodní):

| cíl | h | 80 %: povodně | 80 %: klid 2019–2020 | 95 %: povodně | 95 %: klid | šířka 80 % povodně / klid (cm) |
|---|---|---|---|---|---|---|
| Děčín | 12 | 84 | 88 | 96 | 98 | 25 / 21 |
| Děčín | 24 | 84 | 86 | 97 | 98 | 47 / 36 |
| Děčín | 36 | 85 | 92 | 98 | 99 | 86 / 69 |
| Ústí | 12 | 85 | 88 | 97 | 98 | 29 / 24 |
| Ústí | 24 | 87 | 86 | 97 | 98 | 56 / 42 |
| Ústí | 36 | 88 | 94 | 99 | 99 | 94 / 77 |

Pásmo je kalibrované na oknech povodní, proto je v klidu zbytečně široké (Děčín +24 h 36 cm, i když se hladina skoro
nehýbe). Model učený do 2018 je na validaci o něco přesnější než LOFO modely na „těžkých“ povodních, odtud pokrytí nad
cílem. Pro „Dnešek“ (učený do 2025) chybí neviděná data, pásmo tam je odhad.

## Grafy (`grafy/`, světlé, na projektor, styl slajdů týmu)

- `pokryti.png`: pokrytí 80% pásma, dnešní týmové proti novému, celkem a při rychlém vzestupu.
- `pasmo_2011-01-16.png`: leden 2011 (výchozí obrazovka aplikace), skutečnost v 80% pásmu 78 % hodin, v 95% 98 %.
- `pasmo_2010-09-28.png`: září 2010, déšť nad Děčínem, 81 % / 86 %: vzestup přijde rychleji, než model čeká.
- `pasmo_2013-06-05.png`: červen 2013, rekordní povodeň, 42 % / 66 %: pásmo je moc úzké.

Pásmo v grafech je vnořené (bez této povodně a sousedních), ukazuje tedy, co by aplikace tehdy opravdu nabídla.

## Pro aplikaci

`nejistota_dan.pasmo(model, cil, horizont, pred, hladina_ted, hladina_pred_6h, uroven=0.8)` vrátí (dolní, horní) v cm,
pro číslo i pole; `model` je `ridge` (i `ridge_vse`), `ridge30` nebo `g3`. Chybějící vstup dá NaN, ne zdánlivě platné
pásmo. Kvantily v `kvantily.json`. Napojení do aplikace je jako návrh v `patche/01_pasmo_nejistoty.patch` (aplikace
v main se nemění): `interval()` v `app/predikce.py` zavolá `pasmo()` se stavem před 6 h z řádku vstupů, popisky „90 %
chyb na tréninku“ se změní na „8 z 10 případů (ověřeno na 22 povodních)“.

## Slabiny a co by se dalo dál

- **Pokrytí je empirické, ne zaručené.** Hodiny jedné povodně nejsou nezávislé a chyby jsou z 22 různých modelů;
  nezávislých „pozorování“ je ve skutečnosti 22 povodní (14 bloků), ne 6 358 hodin.
- **Vzestup:** 80% pásmo pokrývá 59–72 %. Lepší by bylo pásmo podmíněné srážkovou předpovědí nebo stavem horních
  stanic, které model zatím nevidí; signál z Mělníka ani poslední chyba nepomohly.
- **Rekordní povodně** (6/2013) jsou mimo rozsah 21 ostatních povodní, pásmo je tam moc úzké. V aplikaci by se při
  hladině nad historickým rozsahem mělo psát, že pásmo neplatí.
- **G3:** obyčejné LOFO (modely ostatních povodní viděly povodeň k); přísná kontrola je jen pro Ridge, kde vyšla skoro
  stejně. LightGBM v G3 má týmové doby doběhu (`lgbm_a.DOBA`) odhadnuté na týmovém tréninku, který část povodní obsahuje;
  to je vlastnost modelu, ne pásma.
- **Ústí** se hodnotí na oknech děčínských povodní (tytéž události), klidné období mimo povodně jen na validaci 2019–2020.
- **Klid:** pásmo je v klidu zbytečně široké (kalibrace jen z oken povodní).

Otázka poroty a odpověď: „Jak víte, že rozmezí „nejspíš 690 až 790 cm“ platí?“ – Ověřili jsme ho na 22 povodních tak,
že pro každou povodeň jsme pásmo spočítali jen z ostatních, jako by ji model ani pásmo nikdy neviděly. Skutečnost padla
do 80% pásma v 79–80 % hodin. Při rychlém vzestupu jen asi v 2 ze 3 případů a na rekordní povodni 2013 ve 4 z 10,
to říkáme otevřeně.
