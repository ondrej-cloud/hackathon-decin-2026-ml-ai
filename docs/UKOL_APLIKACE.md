# Aplikace: co má umět a jak se napojí na model

Zadání pro aplikaci (Honza). Rozhraní níž platí pro každý model, který Ondra ve 21:00 vybere; aplikace se píše proti Ridge a jiný model se jen přepne názvem souboru.

## Komu pomáhá

Město Děčín (povodňová komise, krizový štáb) a lidé u řeky: dřív vědí, jak vysoko bude Labe za 12, 24 a 36 h a jaký stupeň povodňové aktivity to znamená. Jediné, co aplikace ukazuje, je „co teče proti proudu, dorazí k nám“.

## Rozhraní modelu

- `models/<model>_<cil>_<h>.joblib`: natrénovaný objekt s metodou `predict(X)`. `cil` je `decin` nebo `usti`, `h` je 12, 24 nebo 36. Pro Ridge soubory uloží `python src/uloz_model.py` (trénink na trénovací části, stejně jako `porovnej.py`, 5 s). Soubory nejsou v Gitu (`.gitignore`), takže když chybí, aplikace je sama vytvoří stejným postupem jako `uloz_model.py`.
- `X` je tabulka s 98 sloupci z `src/features.py`: `tabulka(cil, h)` vrátí X a y pro všechny hodiny 2006–2025, jeden řádek je jeden okamžik vydání předpovědi. `predict` vrátí hladinu v cm v čase vydání + h.
- Načítání: aplikace nejdřív přidá `src/` do `sys.path` (`sys.path.insert(0, str(ROOT / "src"))`) a teprve pak `joblib.load(...)`. Bez toho se model nenačte, potřebuje modul `models.ridge`.
- Stupně povodňové aktivity: `data.SPA` (Děčín 400 / 490 / 560 cm, Ústí 450 / 530 / 600 cm). Názvy stanic: `data.CILE` a `data.PROTI_PROUDU`.
- Předpovědi na validaci pro grafy: `results/predpovedi/<model>.parquet`, sloupce `cil, horizont, skutecnost, predpoved`, index `cas_vydani` (UTC). Hodnota na řádku platí pro `cas_vydani + horizont`, na osu ji vykreslit posunutou.
- Metriky: poslední `results/*_<model>.json` bez `"rychle": true`, pole `vysledky` (`mae_povodne`, `spa2_predstih_h`, `spa2_propasnuto`, `spa2_plane_poplachy`).

## Co musí být

Do 21:00 body 1 a 2 (kostra celého řetězce), do 23:00 zbytek.

1. **Obrazovka „Teď“.** Výběr stanice (Děčín / Ústí) a okamžiku. Zatím přehrávání historie: datum a hodina z let 2006–2025, výchozí 15. 1. 2011 8:00 (validační povodeň). Zobrazí hladinu teď, předpověď za 12 / 24 / 36 h a stupeň povodňové aktivity teď i předpovězený, barevně (bez stupně, 1., 2., 3.). K tomu jedna věta pro laika, proč to tak vyšlo, z největších vstupů modelu: „Za 24 h bude v Děčíně asi 615 cm, to je 3. stupeň. Voda, která to způsobí, teď teče Prahou (870 m³/s) a Mělníkem (1 020 m³/s).“ Stačí průtok v Praze a Mělníku teď a před 6 h.
2. **Graf posledních 3 dnů** hladiny v cíli, k tomu tři body předpovědi (12, 24, 36 h) a vodorovné čáry stupňů povodňové aktivity.
3. **Obrazovka „Jak dobře to funguje“.** Graf jedné validační povodně (výběr 4/2006, 3/2009, 9/2010, 1/2011): skutečnost, „bude jako teď“, model, čáry stupňů; přepínač horizontu. Pod grafem tabulka z `results/`: chyba na povodních, předstih varování, propásnuté povodně a plané poplachy, model vedle „jako teď“. Jedna věta pod tabulkou, co čísla znamenají.
4. **Srozumitelnost.** České popisky, žádný žargon, na první pohled je jasné, komu aplikace pomáhá. Čísla zaokrouhlená na celé cm, časy v českém čase (data jsou v UTC).
5. **Spuštění.** `streamlit run app/app.py` z kořene repozitáře, knihovny v `app/requirements.txt` (streamlit, pandas, pyarrow, scikit-learn, joblib, matplotlib nebo plotly). Musí běžet na Macu, demo poběží z Tobiasova.
6. Grafy z aplikace jdou uložit jako PNG do `docs/grafy/app_<co>.png`.

## Co je navíc, když zbude čas

7. **Aktuální data ČHMÚ.** Zjistit, jestli opendata.chmi.cz má operativní (dnešní) hodinové hodnoty hladiny a průtoku pro našich 12 stanic (čísla stanic v `src/data.py`, historický archiv stahuje `src/stahni_chmu_hydro.py`). Když ano: tlačítko „Načíst dnešek“ sestaví X stejně jako `features.py` a ukáže skutečnou předpověď na teď. Když ne: zapsat do `docs/DATA.md`, co přesně jsme zjistili, a nechat přehrávání historie.
8. **Mapa stanic** od Prahy po Děčín s barvou podle stupně. Souřadnice stanic v repu nemáme, bez nich přeskočit.

## Co se nesmí

- Neměnit `src/data.py`, `features.py`, `evaluate.py`, `porovnej.py` ani nic v `src/models/`. Když něco chybí, napsat to Honzovi.
- Testovací roky 2021–2025 se neukazují jako „přesnost“. Povodeň 9/2024 do dema až po sobotním finálním testu, rozhoduje Ondra. Přehrávání libovolného data je v pořádku, je to jen zobrazení naměřených dat.
- Falešná předpověď se nikde netváří jako skutečná. Dokud model chybí, je u čísla napsáno „ukázka“.
