Ověřeno pouze na letech 2006–2020: finální konfigurace, týmových 98 vstupů, split i týmové predikce souhlasí. Hlavní čísla CV a validace včetně **17,8 / 15,5 / 44,4** sedí. Joblib funguje a `predikuj(T)` zachová posledních 24 h bez cíle při dostatečné historii. Přímý únik budoucnosti jsem nenašel; scaler se učí jen na tréninku.

1. **Střední — [model_ridge.py:69](C:/Users/danie/Documents/hackathon-2026-ridge/ridge_dan/model_ridge.py:69), také ř. 73.** Export modelu predikuje poslední řádek a následně celé `X`, tedy také roky 2021–2025, mimo ochranu jednorázového testu. **Oprava:** kontrolní predikce omezit na train/val a poslední řádek vybírat z těchto částí.

2. **Střední — [app/predikce.py:11](C:/Users/danie/Documents/hackathon-2026-ridge/app/predikce.py:11), také ř. 16 a 54.** Současná aplikace nový model nepodporuje: nepřidává `ridge_dan/` do `sys.path`, hledá model v jiné složce a předává 98 týmových vstupů místo vlastních 224. Samotné přenesení joblib souboru nestačí. **Oprava:** doplnit načítání modulu a adaptér pro Děčín +24 h používající `predikuj(T)`.

3. **Střední — [pokus.py:281](C:/Users/danie/Documents/hackathon-2026-ridge/ridge_dan/pokus.py:281).** Otisk obsahuje commit a pouze příznak změn; poslední běhy mají `zmeny=true`. Konkrétní použitý kód proto nelze jednoznačně rekonstruovat. Otisk `evaluate.py` je navíc konstanta. **Oprava:** před testem zaznamenat skutečné obsahové hashe modelu, příznaků, stanic, splitu a testovacího skriptu.

4. **Nízká — [POKUSY_RIDGE.md:132](C:/Users/danie/Documents/hackathon-2026-ridge/ridge_dan/POKUSY_RIDGE.md:132).** Pro alphu 100 text uvádí CV **14,46**, všechny odpovídající záznamy `b_vse` uvádějí **14,45**. **Oprava:** sjednotit na 14,45.

Samotný `test_jednou.py` je podle zkontrolované logiky připravený na jednorázový test: používá `finalni=True`, společné řádky, správné baseline, atomickou značku a absence let 2019–2020 nezpůsobí pád `mae_klid`.