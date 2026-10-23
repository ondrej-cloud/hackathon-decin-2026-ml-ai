# Nálezy Codexu a co s nimi

Codex (`codex exec -s read-only`, pravidla v promptu: nic neměnit, nečíst .env ani údaje Kaggle, nálezy se souborem,
řádkem a závažností). Prompty a plné odpovědi v `codex/`.

## (a) Časování srážek, `srazky.py` a `kontrola_casovani.py` (pá 23:00, 133 s)

Přímý únik z budoucnosti nenašel: `predbezne` obsahuje jen to, co bylo známé v termínu, dorovnání dílu 00/12 z 12h
úhrnu se nepoužije dřív než v 06/18, `hodinove` dává v hodině t termín floor((t − 1 h) / 6 h), skupiny průměrují
jen stanice ve stejném čase, bez doplňování dozadu a bez normalizace přes celou řadu.

| Závažnost | Nález | Reakce |
|---|---|---|
| střední | `srazky.py:28` 78 h nestačí: nejstarší 6h díl 72h okna se může počítat z 12h úhrnu, měření sahá na t − 84 h | **Opraveno**, `NEJSTARSI_SR = 90` (84 h + doplnění chybějícího termínu předchozím, o 6 h starším), obaly ho importují, značky částí s 90 h |
| střední | `kontrola_casovani.py:43` test bere zpoždění z kontrolovaného kódu (`R.ZPOZDENI`) | **Opraveno**, hodina je v testu napsaná pevně, přidané pevné případy t = E, E + 1 h, E + 6 h, E + 7 h, E + 72 h, E + 73 h |
| střední | `kontrola_casovani.py:59` shoda součtů se jen vypisuje | **Opraveno**, aserce: 24h součty se smí lišit od přímého výpočtu z 12h úhrnů jen o rozpor 6h > 12h (po odečtení 0,000 mm), žádné NaN; prošlo na Ústí i Doksanech |
| nízká | `srazky.py:100` oříznutí záporného rozdílu nezachová 12h úhrn (6h 15 mm, 12h 14 mm) | **Zdůvodněno**, politika je teď výslovně v hlavičce: 6h úhrn zůstává (model ho už 6 h používal, změnit ho zpětně by byl nekonzistentní záznam), druhý díl je 0; rozpory jsou v datech nejvýš 1 mm |
| poznámka | podmínka 3 podle dokumentace „začátek akumulace“ | Ověřeno na zprávách SYNOP v REM, v souborech od ~2013 nese běžně změřený úhrn; ponecháno |
| poznámka | kvalita 2/6 „podezřelé“ ponechaná | Vědomá volba, zapsaná v `PRUBEH.md` |

## (b) Stejné řádky a varianty, `obaly.py`, `spust_srazky.py`, `spolecne.py`, `tabulka_vysledku.py` (pá 23:16)

Potvrdil: obě varianty sdílejí index, `y`, `c` i vyhození hodin bez srážek, hranice částí s historií 90 h; modely
mají stejné parametry a transformace, Ridge srážky neodmocňuje, StandardScaler se fituje jen v tréninku; obal
LightGBM bez srážek dává přesně stejné předpovědi jako `lgbm_c.fit` ve všech 6 kombinacích; srážky se připojují
podle UTC času vydání bez posunu a bez `bfill`; CV jen v tréninku s mezerou 10 dní, test nikde; metriky odpovídají
týmovým a práh verdiktu ±1 cm je správně.

| Závažnost | Nález | Reakce |
|---|---|---|
| střední | `srazky.py:147` výběr stanic podle pokrytí 2006–2020 bere v úvahu i validační roky 2019–2020 a držené bloky CV | **Zdůvodněno a upraveno**: výběr používá jen dostupnost zpráv (ne stav řeky ani chybu modelu); s roky 2006–2018 i 2006–2017 vyjde stejných 9 stanic, takže na výsledky vliv nemá. `vyber()` teď bere jen 2006–2018, tabulka je bajtově stejná (otisk 0fa9e49a). V CV se výběr nedělá po foldech: stanice se vyřazují kvůli kódování nul v ISD od ~2015, ne kvůli datům, která by se ve foldu měnila |
| střední | `tabulka_vysledku.py:28` souhrn může spárovat záznamy z různých běhů (jiná historie, jiné řádky) | **Opraveno**: bere jen záznamy se stejným otiskem srážek i `nejstarsi_sr` jako nejnovější a assert hlídá stejný počet řádků tréninku i validace v každém páru; staré výsledky z první verze tabulky jsou smazané (logy ve `vysledky/stara_tabulka/`) |
