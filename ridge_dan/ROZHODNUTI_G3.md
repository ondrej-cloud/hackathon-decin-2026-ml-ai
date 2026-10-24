# Rozhodnutí: G3 (nové stanice) jako finální model? Pro Ondru

Dan, so 24. 10. 2026 01:50. G3 = ½ Ridge s 30 stanicemi + ½ LightGBM s 30 stanicemi (12 týmových + 18 nových
stanic ČHMÚ), pevná váha. Moduly `src/models/g3.py` a `ridge30.py` ve větvi `dan-ridge`.

## Doporučení

**Pro finále nechat týmový Ridge (lineární regrese). G3 ani Ridge 30 nepřekonají nejlepší týmový model o 1 cm,
kterou jsme si dali jako hranici.** Body (a)–(d) nočního úkolu (seedy, druhá revize, finální G3 do `models/`)
se proto nedělaly.

## Čísla ze všech tří hodnocení (cm, menší = lepší)

| Hodnocení | týmový Ridge | síť | G3 | Ridge 30 | rozdíl G3 − Ridge |
|---|---|---|---|---|---|
| validace, 4 povodně (Děčín +24 h, `porovnej.py` rozdělení) | **15,5** | 18,4 | 18,2 | 17,8 | +2,7 (horší) |
| Ondrova vícenásobná validace, 8 povodní × 6 kombinací | 20,1 ± 7,7 | 21,0 ± 8,0 | **19,6 ± 7,1** | 20,2 ± 8,4 | −0,5, lepší v 6 z 8 povodní |
| LOFO-CV 22 povodní (Děčín +24 h) | 15,29 | 15,07 | **13,94** | 14,79 | −1,35, lepší v 20 z 22 povodní |

V Ondrově validaci na 36 h (bod 2, náhradní větev): Ridge 30 proti Ridge pro Děčín −0,71 cm (lepší v 5 z 8),
pro Ústí −1,00 (počítáno ze zaokrouhlených chyb, 5 z 8), oba cíle dohromady −0,86 cm. Hranice 1 cm tím není
přesvědčivě splněná (pro Děčín, kde LOFO 36 h ukázalo −2,4 cm, chybí 0,3 cm), proto ani tady (a)–(d).

## Pro G3

- Nejlíp vychází v obou vícepovodňových hodnoceních: LOFO 22 (−1,35 cm, 20 z 22 povodní) i Ondrova validace
  (nejlepší v 5 z 8 povodní, lepší ve všech 6 kombinacích cíl × horizont).
- Výrazně lepší začátek vzestupu (validace 27,8 proti 35,4 cm), dřívější varování: nové stanice proti proudu
  (horní Ohře, horní Labe, Berounka) vidí vlnu dřív.
- Varování srovnatelná: v Ondrově validaci 1 propásnuté jako Ridge, planých 4 proti 3.

## Proti G3

- **Prohrává u povodní s táním sněhu:** duben 2006 (Ondrova validace +5,7 cm proti Ridge, LOFO 25,0 proti 16,7)
  a leden 2011 (+1,9). Přestřelí na stoupání: vlna se v Polabí rozlije do nivy (~20 % vody se drží několik dní,
  rozbor v `ZLEPSENI.md`, pokus A) a model s víc vzdálenými stanicemi tomuto signálu věří víc. Proto je i na
  4 validačních povodních horší (18,2 proti 15,5), dvě z nich jsou tání.
- V Ondrově validaci jen −0,5 cm: pod hranicí 1 cm a 6 z 8 povodní je v rámci náhody (znaménkový test p ≈ 0,29).
- Těch 8 povodní je podmnožina 22, na kterých byl G3 vybrán: není to nezávislé potvrzení. Test 2021–2025 je
  spotřebovaný, jinak ověřit nejde.
- Složitější: dva modely, 30 stanic živě v aplikaci místo 12 (víc míst, kde může vypadnout data), LightGBM
  se hůř vysvětluje porotě.

## Průzkumně: horizont 36 h s ukazatelem útlumu (H30)

Ridge 30 stanic + ukazatel útlumu vlny v nivě (schodek průtoku v úsecích Polabí) je na **36 h** lepší ve všech třech
hodnoceních: validace Děčín +36 h 25,0 proti 26,0; Ondrova validace Děčín −2,1 cm a Ústí −2,3 cm (6 z 8 povodní);
LOFO 22 Děčín −3,44 cm (18 z 22, nejhorší +3,1). Na 24 h nic nepřináší (Ondrova validace −0,3 cm).
Je to ale průzkumný výsledek (nápad z povodně 2006, horizont 36 h vybraný dodatečně), ne předem ověřená volba.
**Pro tým k rozhodnutí:** jestli aplikace ukazuje 36 h, dá se H30 nabídnout jako „model pro delší předpověď“
s touto výhradou; finální model pro 24 h zůstává týmový Ridge. Modul `src/models/h30.py` je hotový
(fit/predict jako ostatní), joblib pro aplikaci zatím nevznikl.

## Co do prezentace

Nové stanice spolehlivě zlepší začátek vzestupu a ve dvou ze tří hodnocení i průměrnou chybu, ale u velkých
povodní s táním přestřelí, protože lineární model nepočítá s rozlivem do nivy. Tým je proto nepoužil ve finále,
jako „co jsme zkoušeli a proč to nešlo“ je to silný příběh.
