Našel jsem dva nálezy:

- [závažnost: střední] `srazky_dan/srazky.py:147` – **Výběr stanic využívá validaci i držené bloky CV.** `vyber()` posuzuje pokrytí za celé období 2006–2020, včetně validačních let 2019–2020. Informace o dostupnosti validačních dat tak ovlivňuje složení tréninkových příznaků. Synteticky ověřeno: změna pouze pokrytí roku 2019 změní výběr stanice. **Oprava:** vybírat stanice podle příslušného tréninku, v CV uvnitř každého foldu, případně jejich seznam stanovit nezávisle na hodnocených datech.

- [závažnost: střední] `srazky_dan/tabulka_vysledku.py:28` – **Souhrn může porovnat různé experimenty.** Záznamy páruje pouze podle modelu, sady, varianty, seedu, části a otisku srážek; ignoruje `nejstarsi_sr`, identitu řádků a počet kombinací. Po částečném opakování běhu může spojit například CV s historií 90 h se staršími výsledky s historií 78 h a vydat neplatný verdikt. Synteticky potvrzeno. **Oprava:** ukládat společné ID/verzi experimentu a otisky indexů tréninku/hodnocení; přijímat pouze úplné, vzájemně odpovídající páry.

V ostatních požadovaných bodech jsem chybu nenašel:

- Obě varianty sdílejí index, `y`, `c` a odstranění řádků s chybějícími srážkami; hranice používají historii 90 h.
- Modely zachovávají parametry a transformace. Ridge srážky neodmocňuje; scalery se fitují uvnitř tréninku.
- LightGBM zachovává cíl `y − H_0`, seed i původní vstupy. Bez přidaných sloupců dal obal přesně stejné predikce ve všech šesti kombinacích.
- Srážky se připojují podle UTC indexu času vydání, bez posunu či `bfill`.
- CV používá jen trénink a desetidenní mezeru; test nevstupuje do fitu ani metrik.
- Týmové metriky, průměr šesti kombinací, začátek vzestupu a okna povodní 2006/2010 odpovídají definicím. Práh verdiktu správně zahrnuje přesně ±1 cm.

Nic jsem nezměnil. Python běžel pouze s `-B` na syntetických datech do roku 2020; experiment ani testovací roky jsem nespustil.