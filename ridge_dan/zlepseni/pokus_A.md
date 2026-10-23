## Pokus A · rozbor přestřelení v povodni 2006 (a 2011), Ridge 12 vs 30 stanic, Děčín +24 h

Skript `pokus_A.py`, čísla `vysledky_A.json`, příspěvky po 6 h `prispevky_A_2006.csv` a `prispevky_A_2011.csv`, denní bilance `bilance_A_2006.csv`. Nic se neladilo ani nemazalo.

- Už týmový Ridge (12 stanic) v roce 2006 na stoupání přestřelí o 40 cm (29. 3. 00:00, validační split; ve foldu LOFO 39 cm). S 30 stanicemi o 62 cm (LOFO 59 cm); rozdíl obou předpovědí je v tu chvíli +22 cm.
- Příspěvky 30 − 12 stanic (cm, validační split), stoupání a vrchol:

| čas (vydání) | skut. za 24 h | 12 st. | 30 st. | horní Labe | horní Berounka | Zbraslav | horní Sázava | Ploučnice | Děčín+Ústí | Beroun | Vltava tým | Nespeky |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 27. 3. 12:00 | 549 | 539 | 552 | +44 | +15 | +7 | +3 | +8 | −24 | −10 | −13 | −9 |
| 28. 3. 12:00 | 642 | 682 | 703 | +38 | +17 | +36 | +12 | +4 | −33 | −17 | −26 | −12 |
| 29. 3. 00:00 | 682 | 722 | 744 | +34 | +24 | +16 | +11 | +13 | −35 | −21 | −22 | −13 |
| 1. 4. 12:00 | 829 | 867 | 886 | +25 | +17 | +7 | −17 | +10 | −47 | −23 | −16 | +11 |
| 3. 4. 00:00 | 875 | 852 | 842 | +14 | +14 | −4 | −28 | +1 | −48 | −19 | −2 | +20 |

- Mechanismus: nové stanice proti proudu (hlavně horní Labe s Orlicí, Chrudimkou a Cidlinou, horní Berounka, Zbraslav, horní Sázava) přidají na stoupání +80 až +110 cm a model to vyrovnává zápornými změnami vah týmových stanic (Děčín −148 / Ústí +113 cm, Beroun, Vraňany, Nespeky). Výsledkem je čistých +20 cm. Na vrcholu je to obráceně: horní Sázava už opadá (−28 cm) a 30 stanic vrchol podstřelí (842 proti 875).
- Proč model přestřelí: v roce 2006 se vlna na Labi v Polabí utlumila. Kostelec měl 28.–31. 3. o 18–21 % méně vody než Nymburk + Jizera (498 proti 610, 566 proti 719, 693 proti 862 m³/s) a dorovnal se až 3. 4. Také Mělník proti Vraňanům + Kostelci (29. 3. 1 578 proti 1 803) a Ústí proti Mělníku + Lounům (1 580 proti 1 780). Lineární model se naučil, že vzestup nahoře dorazí celý. V roce 2006 se ale zhruba pětina vody několik dní držela v nivě. Čím víc vzdálených stanic model má, tím víc tomuto signálu věří.
- Chyba dat to není. Bilance sedí (Praha ≈ Zbraslav + Beroun do 8 %, Nymburk ≈ Přelouč + Cidlina do 5 %). Drobnosti: Cidlina Sány 60 h konstantně 4,05 m³/s (16.–19. 3., před povodní), Žatec 38 h konstantně (řízený odtok z Nechranic). Zbraslav má stav o 71 cm výš než obvykle při stejném průtoku (vzdutí nebo led), její průtok ale bilanci sedí. Nic nemažu.
- 2011 (tání, 730 cm) má stejný mechanismus. Přestřelení 30 stanic je 60 cm proti 36–39 cm (14. 1. 18:00), rozdíl +35 cm. Nahoru táhne horní Berounka (+31 až +34), horní Labe (+21), horní Jizera (+20), horní Ohře (+16 až +18), Zbraslav (+15), dolů Děčín/Ústí (−39 až −43), Beroun (−27 až −31) a Vltava tým (−15 až −19). Průměrná chyba povodně je ale u 30 stanic stejná nebo lepší (13,8–14,1 proti 14,4–14,5).
- Co by pomohlo: menší váha vzdálených stanic, aby jejich protichůdné váhy s týmovými stanicemi byly menší (pokusy B a C). Pak nelineární útlum velkých vln, tedy vstup, který pozná, že vlna je tak velká, že se rozlije do nivy, například rozdíl Kostelec − (Nymburk + Jizera) jako ukazatel. Ten musí projít LOFO; neladil jsem ho.
