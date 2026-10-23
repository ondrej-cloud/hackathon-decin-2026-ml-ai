# Pokusy: vlastní Ridge pro Děčín +24 h

Každý pokus: co, proč, výsledek, ponecháno ano/ne. Nové záznamy na konec. Všechna čísla jsou v cm, Děčín +24 h.

Protokol proti přeladění validace:
- Rozhoduje časová křížová validace uvnitř tréninku (`pokus.cv`): 6 bloků let (2006–07, 2008–09, 2010–11, 2012–13,
  2014–15, 2016–18), model se trénuje na ostatních blocích, kolem drženého bloku mezera 10 dní. Hlavní číslo
  `CV povodně` = průměr přes 18 povodní z tréninku (vrchol nad 400 cm) chyby v okně 7 dní před až 5 dní po vrcholu,
  každá povodeň má stejnou váhu (jinak by o všem rozhodl červen 2013 s 1 072 cm). Alpha se vybírá taky touto CV.
- Validace (4 vynechané povodně + 2019–2020) se pouští jen u milníků, každé nahlédnutí se počítá
  (`poradi_nahlednuti_val` ve `vysledky/pokusy.jsonl`). Test 2021–2025 jednou na konci (`test_jednou.py`).
- Změna se nechává, když zlepší CV povodně aspoň o 0,3 cm a nezhorší CV vzestup; jinak ne (jednodušší vyhrává).

Laťky na validaci (stejné řádky): týmový Ridge 15,5 cm (Děčín +24 h; 17,1 je jeho průměr přes 6 kombinací),
„jako teď“ 44,4 cm.
