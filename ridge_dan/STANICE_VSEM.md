# Pomůže 18 nových stanic všem týmovým modelům?

Dan, větev `dan-ridge`, pá 23. 10. 2026 22:25–23:10. Kód `ridge_dan/stanice_vsem/` (společný základ `spolecne.py`,
obaly `ridge_stanice.py`, `lgbm_stanice.py`, `fyzika_stanice.py`, běh `spust.py`, tabulka `souhrn.py`), záznam
všech běhů `stanice_vsem/vysledky.jsonl`. Test 2021–2025 se nespouštěl.

## Odpověď

**Některým.** Podle rozhodující časové CV v tréninku pomáhají **Ridge (−1,5 cm) a LightGBM (−2,0 cm)**, stabilně
po blocích let; fyzikálnímu modelu jen o 0,7 cm, pod hranicí 1 cm. Na validaci je obraz smíšený: fyzika o 1,35 cm
lepší, LightGBM o 0,99 cm (těsně pod hranicí), Ridge o 1,40 cm horší (povodeň 2006). Všem třem modelům se ale výrazně zlepší **začátek
vzestupu** (na validaci o 5–8 cm) a varování přichází o 1–3 h dřív. Cena: LightGBM má na validaci 3 plané poplachy
2. stupně navíc (horizont 36 h). Přestřelení v roce 2006 není obecný problém nových stanic: u Ridge se zvětší,
u LightGBM zmenší a v CV se 95. percentil přestřelení u všech tří modelů zmenší.

Síť: počítá se zvlášť na Kaggle (větev dan-sit).

## Jak se srovnávalo

- Týmové vstupy beze změny (`features.tabulka`, Ondrova tabulka), k nim podle času UTC 126 sloupců: průtoky 18 nových
  stanic z `tabulka/labe_ridge.parquet` se stejnými zpožděními 0/3/6/12/18/24/36 h. Nové stanice nemají v letech
  2006–2025 žádnou díru, takže obě varianty mají u všech 6 kombinací cíl × horizont **identické řádky** (např. Děčín
  +24 h 175 130 hodin, z toho 19 264 val), split `evaluate.casti` beze změny. Nic se znovu nestahovalo.
- Varianta „beze změny“ volá původní `fit` (Ridge, LightGBM) nebo jeho věrnou parametrizovanou kopii (fyzika) a dává
  přesně uložené týmové výsledky: prumer_povodne Ridge 17,08, LightGBM 23,07, fyzika 24,75 (u fyziky shoda
  předpovědí s `fyzika.fit` na 0,0 cm).
- „+ stanice“ = jen nové stanice, zpracované jako ostatní v daném modelu:
  - **Ridge**: stejná odmocnina průtoků, škálování, alpha 1. Navíc rozpad 2 × 2 (odmocnina ano/ne × 12/30 stanic);
    týmový Ridge odmocninu už má, takže „jen odmocnina“ = týmový model.
  - **LightGBM** (`lgbm` = `lgbm_c`): pro každou novou stanici nad cílem průtok, který do cíle doteče za horizont,
    a jeho rozdíl proti tomu, co dotéká teď (jako `lgbm_a.vstupy`). Doba doběhu stejnou metodou jako
    `src/doba_dobehu.py`, odhadnutá uvnitř `fit` jen z hodin, na kterých se model učí (po nálezu Codexu, viz níž).
    Moje reimplementace dává pro Děčín přesně týmové doby. Ploučnice a Bílina jen pro Děčín (do Ústí netečou).
    Parametry, sezónnost a trend beze změny.
  - **Fyzika**: nové stanice zapojené do stromu řeky, kam fyzikálně patří a kam dosáhnou 3 vrstvy modelu: Louny ←
    Žatec ← Karlovy Vary, Cidlina Sány nad Nymburkem, Jizera ← Bakov, pro Děčín přímé brány Ploučnice (Benešov ←
    Stružnice ← Česká Lípa) a Bílina Trmice. Doby putování stejnou funkcí `doba_putovani`. **Nejde 10 z 18**:
    Zbraslav (Vltava i se Sázavou, která v týmovém stromu visí přímo pod Prahou, přidání by vodu Sázavy počítalo
    dvakrát nebo by se musel přestavět týmový strom) a horní Berounka, horní Sázava, Orlice a Chrudimka (všechny až
    ve 4. vrstvě, model bere 3; víc vrstev by změnilo model, ne jen stanice).
- Rozhoduje časová CV v tréninku pro Děčín +24 h (6 bloků let, mezera 10 dní, průměr chyby přes 18 povodní nad
  400 cm, každá stejnou vahou), validace s metrikami jako `porovnej.py` (průměr `mae_povodne` přes 6 kombinací,
  varování 2. a 3. stupně sečtené přes 6 kombinací). Zlepšení se počítá od 1 cm.
- LightGBM: seedy 42/43/44 dávaly přesně stejné výsledky (rozptyl 0, týmový LightGBM nemá náhodný výběr řádků ani
  vstupů), proto po opravě jen seed 42.

## Tabulka

CV a podrobnosti pro Děčín +24 h, validace `prumer_povodne` a poplachy přes všech 6 kombinací. V cm, poplachy v kusech.

| Model | varianta | CV povodně | CV vzestup | VAL prumer_povodne | VAL Děčín +24 | VAL začátek vzestupu | VAL 2006 (přestřelení na stoupání) | 2./3. SPA propásnuto | 2./3. SPA plané | 2./3. SPA předstih h |
|---|---|---|---|---|---|---|---|---|---|---|
| Ridge | beze změny | 15,64 | 33,8 | **17,08** | **15,5** | 35,4 | **16,0** (57) | 0/0 | 0/0 | 17,4/15,8 |
| Ridge | + 18 stanic | **14,17** | **28,8** | 18,48 | 17,8 | **28,1** | 24,7 (68) | 0/0 | 0/0 | **19,0/18,6** |
| LightGBM | beze změny | 18,05 | 37,2 | 23,07 | 21,3 | 36,3 | 29,4 (111) | 0/0 | **0**/0 | 14,2/15,1 |
| LightGBM | + 18 stanic | **16,01** | **32,4** | **22,08** | **20,4** | **28,1** | 29,4 (**99**) | 0/0 | 3/0 | **16,9/16,8** |
| fyzika | beze změny | 18,53 | 39,4 | 24,75 | 22,5 | 37,1 | 26,4 (**55**) | 0/0 | 0/2 | 16,2/15,7 |
| fyzika | + 8 stanic | **17,88** | **36,0** | **23,40** | **21,9** | **32,3** | **25,8** (59) | 0/0 | 0/2 | **17,2/17,2** |
| síť | | počítá se zvlášť na Kaggle (větev dan-sit) | | | | | | | | |

Stabilita rozdílu v CV („+ stanice“ − „beze změny“, ± směrodatná chyba):

| | přes 18 povodní | přes 5 bloků s povodní | lepší v blocích |
|---|---|---|---|
| Ridge | −1,47 ± 0,39 | −1,56 ± 0,63 | 4 z 5 |
| LightGBM | −2,04 ± 0,37 | −1,98 ± 0,28 | 5 z 5 |
| fyzika | −0,66 ± 0,33 | −0,90 ± 0,45 | 4 z 5 |

Rozpad Ridge 2 × 2 (CV povodně / VAL prumer_povodne):

| | 12 stanic | 30 stanic |
|---|---|---|
| bez odmocniny | 23,15 / 26,68 | 24,64 / 32,67 |
| s odmocninou | 15,64 / 17,08 (= týmový Ridge) | **14,17** / 18,48 |

Odmocnina je u Ridge zásadní (CV −7,5 cm, lepší ve všech 5 blocích). Nové stanice pomáhají jen s ní: bez odmocniny
CV zhorší (+1,5) a na validaci 2006 přestřelí až o 169 cm. Lineární vztah k surovému průtoku je u velkých přítoků
moc strmý.

## Začátek vzestupu

Hodiny, kdy Děčín za 24 h stoupne aspoň o 50 cm, ale posledních 6 h ještě skoro nestoupal (269 val hodin): chyba
Ridge 35,4 → 28,1, LightGBM 36,3 → 28,1, fyzika 37,1 → 32,3; podhodnocení se zmenší o 10, 6 a 7 cm. V CV
(rychlé stoupání) −5,1, −4,8 a −3,4 cm. Tady nové stanice pomáhají všem a nejvíc, protože vidí vlnu dřív (horní
Ohře, horní Labe, Berounka).

## Povodeň 2006 a přestřelení

- Na stoupání v roce 2006 přestřelují **všechny** týmové modely už bez nových stanic: Ridge o 57 cm, LightGBM
  o 111 cm, fyzika o 55 cm. Nové stanice to u Ridge zhorší (68 cm, chyba povodně 16,0 → 24,7), u fyziky mírně
  (59 cm, chyba ale 26,4 → 25,8) a u LightGBM zlepší (99 cm, chyba stejná 29,4).
- V CV (18 povodní) se 95. percentil přestřelení v oknech povodní s novými stanicemi zmenší u všech: Ridge 21 → 18 cm,
  LightGBM 28 → 24, fyzika 29 → 28. Největší jednotlivé přestřelení: Ridge 150 → 163, LightGBM 104 → 103, fyzika
  299 → 299.
- Závěr: přestřelení 2006 není obecná vlastnost nových stanic. U Ridge vzniká tím, že model je skoro bez
  regularizace a podobné stanice mají velké protichůdné váhy, které se v neobvyklé povodni přestanou vyrušovat
  (rozbor v `POKUSY_RIDGE.md`, 21:17).

## Nálezy Codexu (kontrola d, jen pro čtení, `codex/kontrola_d_stanice_vsem.md`)

Potvrdil: obě varianty mají shodné řádky, „beze změny“ odpovídá originálům, spojení podle času nemá budoucí vstupy,
strom fyzikálního modelu nepočítá vodu dvakrát.

- Vysoký nález: doby doběhu nových stanic u LightGBM byly odhadnuté z celého tréninku včetně drženého bloku CV.
  Opraveno, odhad uvnitř `fit` jen z trénovací části foldu: CV 16,20 → 16,01, validace 22,10 → 22,08, závěr stejný.
  Týmové pevné doby (`lgbm_a.DOBA`) jsou z celého tréninku taky, to je vlastnost týmového modelu, obě varianty ji
  mají stejně.
- Střední: metrika „max. přestřelení“ byla průměr maxim, opraveno na 95. percentil a skutečné maximum.
- Nízký: tři seedy LightGBM nejsou tři nezávislá ověření (deterministický model), dál jen seed 42.

## Poznámky

- Doba doběhu stejnou metodou dává u malých řízených toků fyzikálně divná čísla (Bílina Trmice → Děčín 37 h
  u LightGBM a 33 h u fyziky, skutečně spíš 3–4 h; Litavka 42 h). Nechal jsem je, ať je zpracování stejné jako
  u týmových stanic; obě stanice jsou při povodních malé (Bílina 1–3 % průtoku Děčína).
- Pro Ridge Děčín +24 h s 30 stanicemi (to je můj model z prvního úkolu) už existuje jednorázový test z předchozího
  úkolu (`ZPRAVA.md`, pá 21:49): 16,1 proti 17,5 cm týmového Ridge. Teď se žádný test nespouštěl a ostatní modely
  s novými stanicemi test nemají. Finální test pustí Ondra.
