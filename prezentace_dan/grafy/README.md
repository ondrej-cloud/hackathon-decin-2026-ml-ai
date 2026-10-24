# Grafy do prezentace (Dan): G1–G4

Kreslí je `prezentace_dan/grafy_dan.py`. Skript nic netrénuje a jen čte uložené výsledky a předpovědi. Ostatní worktree
(`hackathon-2026-ridge`, `hackathon-2026-sit`) jen čte a nic v nich nespouští. Grafy se dají kdykoli nakreslit znovu:

```
set PYTHONUTF8=1
C:\Users\danie\.venvs\hackathon\Scripts\python.exe prezentace_dan\grafy_dan.py
```

Styl je stejný jako u týmových slajdů (`src/grafy_prezentace.py`): 16:9, 150 dpi, nadpis-tvrzení vlevo nahoře, písmo
Segoe UI a týmové barvy. Skript při každém běhu porovná čísla s kontrolními hodnotami ze zadání a rozdíly vypíše
na konci. Při posledním běhu (so 24. 10.) **nesedělo nic**, všechna kontrolní čísla odpovídají.

Nadpisy G2, G3 a G4 se skládají podle čísel. Když by tvrzení přestalo platit (třeba po novém běhu modelu), skript
dá neutrální nadpis.

---

## G1 · `G1_stanice_doby_dobehu.png` · Za kolik hodin doteče voda do Děčína

Graf ukazuje 12 týmových stanic rozmístěných podle zeměpisné polohy. U každé stanice je doba, za kterou voda doteče
do Děčína. Barva rozlišuje větev povodí: Vltava s Berounkou a Sázavou, horní Labe s Jizerou, Ohře a Labe pod Mělníkem.
Šipky ukazují směr toku. Šedé body jsou 18 nových stanic, které používá G3.

- **Souřadnice:** `C:\Users\danie\Documents\hackathon-2026-prezentace\data\external\stanice_hydro.csv` (lat, lon).
- **Doby doběhu (h):** `C:\Users\danie\Documents\hackathon-2026-prezentace\docs\DATA.md`, odstavec „Doba doběhu do
  Děčína“, a skript `src/doba_dobehu.py` (větev dan). Doba je posun s největší korelací změn průtoku za 6 h a je
  změřená na trénovací části 2006–2018. Čísla jsou v grafu přesně podle zadání: Ústí 4, Kostelec 10, Nymburk 10,
  Mělník 13, Vraňany 13, Louny 16, Praha-Chuchle 17, Předměřice (Jizera) 18, Přelouč 18, Beroun 23, Nespeky (Sázava) 25.
- **18 nových stanic (šedě):** souřadnice jsou z metadat ČHMÚ
  `C:\Users\danie\Documents\hackathon-2026-ridge\ridge_dan\cache\hydrology\historical\metadata\meta1.json`
  (sloupce GEOGR1/GEOGR2). Seznam stanic (čísla DBC) je z `ridge_dan\stanice.py`. Souřadnice jsou spolehlivé: u 12
  týmových stanic se metadata od `stanice_hydro.csv` teď liší nejvýš o 0,0009°. Skript při každém běhu hlídá, aby rozdíl nepřekročil 0,01°.
  Když soubor chybí nebo nesedí, šedé body vynechá.

**Výhrady**
- Je to **schéma, spojnice nejsou skutečný tok řek.** Body leží na správném místě, ale mezi stanicemi vedou rovné
  čáry. Osy jsou upravené tak, aby 1 km na sever byl v obrázku stejně dlouhý jako 1 km na východ.
- Na dvou krátkých spojnicích (Vraňany → Mělník, Předměřice → Kostelec) šipka není, protože by splynula s body.
- Doba doběhu z Loun a ze vzdálených stanic je jen přibližná, korelace je tam slabá (0,2–0,3, viz DATA.md). Při velké
  vodě (Děčín nad 300 cm) vychází doba skoro stejně.

**Co chybí**
- Doba doběhu 18 nových stanic v G1 není. Experimentální odhady stejnou metodou existují (`ridge_dan/STANICE_VSEM.md`),
  u malých řízených toků jsou ale fyzikálně divné (Bílina → Děčín 37 h u LightGBM a 33 h u fyziky, Litavka 42 h),
  proto u šedých bodů nejsou štítky ani hodiny. V `main`/`stanice_hydro.csv`
  jejich souřadnice nejsou, jsou jen v cache session ridge (viz výš).

---

## G2 · `G2_chyba_podle_horizontu.png` · Lineární regrese chybuje 2–3× méně než „bude jako teď“

Graf ukazuje průměrnou chybu během povodní (`mae_povodne`, cm) na validaci pro 12, 24 a 36 h dopředu. Jeden panel je
pro Děčín, druhý pro Ústí nad Labem. Je v něm všech 5 modelů. Čím dál dopředu předpovídáme, tím je chyba větší
u všech modelů. „Bude jako teď“ chybuje 2,4× až 2,9× víc než lineární regrese.

**Zdroje** (pro každý model nejnovější soubor podle pole `cas`, `"verze": "9a31181e"`, `"cast": "val"`,
`"rychle": false`, 6 kombinací), vše v `C:\Users\danie\Documents\hackathon-2026-prezentace\results\`:

| model | soubor | Děčín 12 / 24 / 36 h | Ústí 12 / 24 / 36 h | průměr 6 |
|---|---|---|---|---|
| lineární regrese (ridge) | `2026-10-23_195917_ridge.json` | 9,0 / 15,5 / 26,0 | 9,6 / 15,7 / 26,7 | 17,1 |
| neuronová síť (mlp) | `2026-10-23_195305_mlp.json` | 9,3 / 18,4 / 25,7 | 9,0 / 16,5 / 28,1 | 17,8 |
| LightGBM (lgbm) | `2026-10-23_200717_lgbm.json` | 10,2 / 21,3 / 36,4 | 11,9 / 21,8 / 36,8 | 23,1 |
| fyzikální model | `2026-10-23_195916_fyzika.json` | 13,5 / 22,5 / 38,5 | 14,4 / 22,1 / 37,5 | 24,8 |
| „bude jako teď“ | `2026-10-23_195106_jako_ted.json` | 23,0 / 44,4 / 65,6 | 23,4 / 44,2 / 65,1 | 44,3 |

Všechna kontrolní čísla ze zadání sedí. Soubor `lgbm` s verzí 9a31181e existuje, takže náhradní `lgbm_c` nebyl
potřeba. Jeho čísla (`2026-10-23_200025_lgbm_c.json`) jsou ostatně stejná.

**Výhrady**
- Validace jsou 4 povodně (4/2006, 3/2009, 9/2010, 1/2011) a klidné roky 2019–2020. Číslo je chyba jen v oknech povodní.
- Lineární regrese není nejlepší ve všech 6 kombinacích. Neuronová síť je o kousek lepší v Děčíně na 36 h
  (25,7 proti 26,0) a v Ústí na 12 h (9,0 proti 9,6). Proto nadpis neříká „nejlepší všude“. Tvrzení 2–3× (přesně 2,44
  až 2,86×) platí ve všech šesti kombinacích.
- V Ústí na 12 h se body lineární regrese a sítě skoro kryjí (9,6 a 9,0).

**Co chybí**
- Čísla z testu 2021–2025 (`*_test.json`) v grafu nejsou, jde jen o validaci.
- Chybí TCN (`2026-10-24_*_tcn*.json`), protože má jinou verzi (69a6db32).

---

## G3 · `G3_zacatek_vzestupu_stanice.png` · Nové stanice vidí vlnu dřív

Graf ukazuje chybu na **začátku vzestupu** v Děčíně za 24 h (validace) pro čtyři modely. Každý model je spočítaný
dvakrát: jen s 12 týmovými stanicemi a s dalšími 18 novými stanicemi ČHMÚ (30 celkem). Začátek vzestupu jsou hodiny,
kdy hladina v Děčíně za 24 h stoupne aspoň o 50 cm, ale za posledních 6 h stoupla o méně než 10 cm. Takových hodin je
na validaci 269 (`n_zacatek`, stejné u všech běhů). Definice je v `ridge_dan\hodnoceni.py`. Chyba se zmenší
**u všech čtyř modelů**, proto nadpis platí.

| model | 12 týmových | + 18 nových | rozdíl |
|---|---|---|---|
| lineární regrese | 35,4 | 28,1 | −7,3 |
| LightGBM | 36,3 | 28,1 | −8,2 |
| fyzikální model | 37,1 | 32,3 | −4,8 |
| neuronová síť (průměr 3 seedů) | 32,4 | 26,7 | −5,7 |

**Zdroje**
- Lineární regrese, LightGBM a fyzikální model:
  `C:\Users\danie\Documents\hackathon-2026-ridge\ridge_dan\stanice_vsem\vysledky.jsonl`. Bral jsem řádky
  `"cast": "val"`, varianty `ridge_12`/`ridge_30`, `lgbm_12`/`lgbm_30` (seed 42) a `fyzika_12`/`fyzika_30`, hodnotu
  `decin24.mae_zacatek`, a u opakované varianty vždy poslední řádek. LightGBM 30 se seedem 42 je tam dvakrát, obakrát
  vyšlo 28,1. Seedy 43 a 44 dávají přesně stejná čísla (36,3 a 28,1).
- Neuronová síť: `C:\Users\danie\Documents\hackathon-2026-sit\sit_dan\vysledky\beh1_a_b.json`, `val.decin24.mae_zacatek`,
  průměr přes seedy 42, 43 a 44:
  - varianta a (12 stanic, 98 vstupů): 32,7 / 32,3 / 32,2, průměr 32,40, rozpětí 0,5 cm, směrodatná odchylka 0,26,
  - varianta b (+ 18 stanic, 224 vstupů): 27,6 / 26,0 / 26,6, průměr 26,73, rozpětí 1,6 cm, směrodatná odchylka 0,81.
- Všechna kontrolní čísla ze zadání sedí.

**Výhrady**
- **Fyzikální model zapojuje jen 8 z 18 nových stanic** (víc jich do jeho stromu toků nejde zapojit, viz
  `ridge_dan\POKUSY_RIDGE.md`). Proto je jeho zlepšení menší. V grafu je to napsané pod názvem modelu.
- Je to jen Děčín +24 h a jen validace (4 povodně), žádný test.
- Lepší začátek vzestupu neznamená menší chybu celkově. Ve stejném souboru má lineární regrese na validačních
  povodních (Děčín +24 h, `mae_povodne`) s 30 stanicemi chybu 17,8 cm, tedy horší než s 12 stanicemi (15,5 cm).
  LightGBM se zlepší z 21,3 na 20,4 cm a fyzikální model z 22,5 na 21,9 cm. U povodní s táním sněhu (2006, 2011)
  model s novými stanicemi přestřelí, viz `ridge_dan\ROZHODNUTI_G3.md`.

**Co chybí**
- Samotný G3 (směs) tu není, je jen v G4. Podle `ROZHODNUTI_G3.md` má G3 začátek vzestupu 27,8 cm proti 35,4.
- Ústí a horizonty 12 a 36 h tu nejsou.

---

## G4 · `G4_cerven_2013_g3_vs_tym.png` · Červen 2013: G3 blíž skutečnosti než týmový model

Graf ukazuje povodeň z června 2013 (vrchol 1 072 cm 6. 6. 2013 ve 2:00 českého času) a předpověď hladiny v Děčíně
vydanou 24 h předem. Jsou v něm tři čáry: skutečnost, týmový model (lineární regrese s 12 stanicemi) a G3. Na ose x je
čas, pro který předpověď platí (čas vydání + 24 h), v českém čase. Vodorovné čáry jsou 1., 2. a 3. stupeň povodňové
aktivity v Děčíně (400, 490 a 560 cm).

**Co je G3:** směs dvou modelů po hodinách, ½ × lineární regrese s 30 stanicemi + ½ × LightGBM s 30 stanicemi
(12 týmových + 18 nových stanic ČHMÚ). Váha je pevná. Ve větvi dan-ridge je to `src/models/g3.py`, rozhodnutí
popisuje `ridge_dan\ROZHODNUTI_G3.md`.

**Zdroje**
- Předpovědi out-of-fold z LOFO-CV (sloupce fold, cas, y, pred):
  `C:\Users\danie\Documents\hackathon-2026-ridge\ridge_dan\zlepseni\oof\ridge_12.parquet` (týmový model),
  `...\oof\ridge_30.parquet` a `...\oof\lgbm_30.parquet` (LightGBM se seedem 42). Skript ověřil, že `fold`, `cas` i `y`
  jsou ve všech třech souborech stejné řádek po řádku (6 358 řádků).
- Fold: `C:\Users\danie\Documents\hackathon-2026-ridge\ridge_dan\stanice_vsem\lofo_foldy.csv`, horizont 24,
  **fold 19**, povodeň `2013-06-05` (vrchol 1 072 cm). Druhou červnovou povodeň `2013-06-26` (548 cm) skript
  nebere. Okno jsou časy vydání 29. 5. 2013 0:00 až 10. 6. 2013 0:00 UTC, tj. 289 hodin. V grafu je to doba
  platnosti od 30. 5. 2:00 do 11. 6. 2:00 českého času.
- Kontrola `y`: sedí přesně na `decin_H` v čase vydání + 24 h z
  `C:\Users\danie\Documents\hackathon-2026-prezentace\data\external\labe_hodinove.parquet`.

**Klíčová čísla** (průměrná absolutní chyba v okně, cm)

| | spočítáno skriptem | uložené `po_povodnich["2013-06-05"]` |
|---|---|---|
| týmový model (ridge_12) | 47,82 | 47,8 (`zlepseni\vysledky_C.json`, `nazev == "ridge_12"`) |
| G3 | 41,83 | 41,8 (`zlepseni\vysledky_G34.json`, `G3_pul_ridge30_lgbm30`) |
| „bude jako teď“ (v grafu není) | 97,39 | – |

Rozdíl proti uloženým číslům je pod 0,1 cm. Každá složka G3 je sama horší než týmový model: Ridge 30 má 50,6 a
LightGBM 30 má 52,9. Lépe vychází až jejich průměr.

Další čísla, která se dají říct u slajdu:
- Na vrcholu (1 072 cm) předpověděl týmový model 952 cm a G3 965 cm. Vrchol tedy podcenily oba, nejvyšší předpověď
  v okně byla 978 a 986 cm.
- Při stoupání týmový model přestřelil až o 162 cm (platnost 4. 6. 0:00, předpověď 934 cm, skutečnost 772 cm).
  G3 přestřelí nejvíc o 63 cm, a to až na poklesu 10. 6.
- Do vrcholu je chyba týmového modelu 54,2 cm a G3 45,4 cm, po vrcholu 38,9 a 36,8 cm. G3 je blíž skutečnosti
  v 56 % hodin.

**Výhrady**
- Předpovědi jsou **out-of-fold z LOFO-CV**: model, který předpovídal tuto povodeň, se učil bez ní a bez 20 dní před
  a po. Je to jen **Děčín +24 h a jedna povodeň, není to test.** Skutečný týmový model (učený 2006–2018) povodeň 2013
  v tréninku má, takže v ostré předpovědi by vyšel jinak.
- Povodeň je vybraná, protože je největší a je na ní vidět rozdíl. Celkově je obrázek smíšený. V LOFO přes 22 povodní
  je G3 lepší (13,94 proti 15,29 cm, lepší ve 20 z 22). Na 4 validačních povodních je ale horší (Děčín +24 h 18,2 proti
  15,5 cm) a prohrává u povodní s táním sněhu (2006, 2011). Tým proto G3 do finále nevzal, viz `ROZHODNUTI_G3.md`.

**Co chybí**
- Čára „bude jako teď“ v grafu není, aby zůstal čitelný. Její chyba v okně je 97,4 cm.
- Chybí Ústí a horizonty 12 a 36 h. Ostatních 5 velkých povodní je v grafu session ridge
  `ridge_dan\grafy\srovnani_g3_tym_povodne.png`.

---

## V1–V4 · vstupy finálního modelu a jejich důležitost

Kreslí je `prezentace_dan/vstupy_dulezitost.py`. Na rozdíl od G1–G4 tenhle skript trénuje: týmový Ridge pro Děčín
+12/+24/+36 h, pokaždé bez jedné stanice nebo větve, jen na train části, vyhodnocení na validaci, test se nepoužije.
Běží asi 2 min. S `--jen-grafy` jen překreslí obrázky z uložených CSV. Čísla, metoda a text pro slajdy jsou
v `prezentace_dan/VSTUPY_DULEZITOST.md`.

- `V1_co_jde_do_modelu.png`: schéma povodí s dobou doběhu (jako G1) a 98 vstupů (slajd A).
- `V4_dulezitost_vetvi.png`: o kolik vzroste chyba bez vlastních měření Děčína, bez Vltavy, bez horního Labe a bez všech
  10 stanic proti proudu (slajd B, hlavní).
- `V2_dulezitost_stanic.png`: totéž po jednotlivých stanicích, heatmapa stanice × horizont.
- `V3_dulezitost_permutace.png`: kontrola skupinovou permutací v plném modelu. Barva je oříznutá, čísla platí.
