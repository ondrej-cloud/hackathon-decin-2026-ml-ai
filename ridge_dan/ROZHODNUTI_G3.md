# Rozhodnutí: nové stanice ve finálním modelu? Pro Ondru

Dan, so 24. 10. 2026 03:30. G3 = ½ Ridge s 30 stanicemi + ½ LightGBM s 30 stanicemi (12 týmových + 18 nových
stanic ČHMÚ), pevná váha; Ridge 30 = týmový Ridge + 18 nových stanic. Moduly `src/models/g3.py`, `ridge30.py`
(větev `dan-ridge`). Test 2021–2025 se nepoužil.

## Doporučení

- **24 h: nechat týmový Ridge.** G3 v Ondrově vícenásobné validaci nepřekoná nejlepší týmový model o 1 cm (−0,5 cm),
  na 4 validačních povodních je horší. V LOFO-CV 22 povodní ale překoná Ridge (−1,35 cm, 20 z 22 povodní) i síť
  (−1,14 cm, 17 z 22) – hodnocení se tedy rozcházejí podle toho, kolik povodní s táním obsahují.
- **36 h: týmový Ridge, nebo Ridge 30, rozhodnutí je na týmu.** Ridge 30 je na 36 h lepší, ale přísnou hranici
  splní jen pro Ústí, a to přesně na hraně (viz tabulka). Model je připravený (bod c).

## Čísla (cm, menší = lepší)

| Hodnocení | týmový Ridge | síť | G3 | Ridge 30 |
|---|---|---|---|---|
| validace 4 povodně, Děčín +24 h | **15,5** | 18,4 | 18,2 | 17,8 |
| Ondrova validace, 8 povodní × 6 kombinací | 20,1 ± 7,7 | 21,0 ± 8,0 | **19,6 ± 7,1** (−0,5; 6 z 8) | 20,2 ± 8,4 |
| LOFO-CV 22 povodní, Děčín +24 h | 15,29 | 15,07 | **13,94** (−1,35; 20 z 22) | 14,79 |
| validace 4 povodně, 36 h Děčín / Ústí | **26,0** / 26,7 | | | 26,6 / **26,6** |
| Ondrova validace, 36 h Děčín / Ústí | 29,8 / 31,1 | 33,9 / 32,8 | 29,7 / 30,8 | **29,0** (−0,71; 5 z 8) / **30,1** (−1,00; 5 z 8) |
| LOFO-CV 22 povodní, Děčín +36 h | 26,39 | | | **23,96** (−2,43; 17 z 22) |

Ústí 36 h: −1,00 cm počítáno z chyb zaokrouhlených na desetiny (tak je ukládá `krizova_validace.py`), tedy na hraně.
Validace G3: `zlepseni/vysledky_G3_val.json`. Síť na 4 povodních: týmový výsledek `results/*_mlp.json`.

## Pro a proti nových stanic

- **Pro:** výrazně lepší začátek vzestupu (G3 na validaci 27,8 proti 35,4 cm) a dřívější varování, stanice proti
  proudu (horní Ohře, horní Labe, Berounka) vidí vlnu dřív; v obou vícepovodňových hodnoceních vyhrávají nejčastěji.
- **Proti:** prohrávají u povodní s táním sněhu: duben 2006 (Ondrova validace G3 +5,7 cm, Ridge 30 na 36 h +7,1)
  a leden 2011. Vlna se v Polabí rozlije do nivy a lineární model s víc vzdálenými stanicemi tomu nevěří (rozbor
  v `ZLEPSENI.md`). 8 povodní Ondrovy validace je podmnožina 22, na kterých se vybíralo, nezávislé potvrzení chybí.
  30 stanic živě je víc míst, kde mohou vypadnout data; G3 jsou dva modely.

## Body (a)–(d) pro Ridge 30 na 36 h (podle pravidla nočního úkolu, kvůli Ústí)

- (a) Seedy: Ridge je deterministický, různé seedy nic nemění (LightGBM v něm není).
- (b) Druhá nezávislá revize celého řetězce Codexem (`codex/kontrola_l_ridge30.md`): bez kritických a vysokých
  nálezů, data, stanice, UTC, foldy i čísla sedí; závěr Codexu: „věrohodné jako retrospektivní CV, ale soustavná
  převaha aspoň o 1 cm doložená není“. Znaménkové testy jsou jen přibližné (okna 12/2012 a 1/2013 se překrývají).
- (c) Finální modely trénované na 2006–2025: `models/ridge30_decin_36.joblib`, `models/ridge30_usti_36.joblib`
  (`python ridge_dan/uloz_ridge30.py`, 15 kB, joblib s `predict(X)` jako `src/uloz_model.py`, X = 98 týmových vstupů
  z `features.tabulka`; nejsou v Gitu, `models/*.joblib` je v `.gitignore`).
- (d) Co potřebuje aplikace: (1) `src/` v `sys.path` (jako dnes) a lokálně `ridge_dan/tabulka/labe_ridge.parquet`
  (postaví `ridge_dan/stahni_hydro.py` + `data_ridge.py`, asi 20 min šetrného stahování), model si z ní k času řádku
  připojí 18 nových stanic; pro historické přehrávání 2006–2025 to stačí. (2) Živě: hodinové průtoky všech 30 stanic
  za posledních 36 h bez děr. Při výpadku kterékoli nové stanice spadnout zpět na týmový Ridge. (3) Zpoždění dat
  ČHMÚ jsem v noci neověřoval: model bere čas t jako čas posledního měření, takže když data přijdou o d hodin později,
  předpověď platí jen na 36 − d h dopředu od okamžiku zobrazení. Ověřit na živém zdroji ČHMÚ, než se to v aplikaci ukáže.

## Průzkumně: ukazatel útlumu v nivě (H30)

Ridge 30 + ukazatel útlumu vlny (schodek průtoku v úsecích Polabí) je na **36 h** lepší ve všech třech hodnoceních:
validace Děčín +36 h 25,0 proti 26,0; Ondrova validace Děčín −2,1 cm, Ústí −2,3 cm (6 z 8); LOFO 22 Děčín
−3,44 cm (18 z 22, nejhorší +3,1). Na 24 h nic (Ondrova validace Děčín −0,21, Ústí +0,01). Je to ale **průzkumné**:
nápad vznikl z povodně 2006 a horizont 36 h jsem vybral až po rozpadu výsledků. Modul `src/models/h30.py` je hotový,
joblib ne. Kdyby se tým rozhodl pro 36 h použít nové stanice, je to silnější kandidát než Ridge 30, ale s touto výhradou.
