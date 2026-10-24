# Ranní zpráva (so 24. 10., větev `dan-nejistota`, vše v `nejistota_dan/`, aplikace v main beze změny)

1. **Pásmo nejistoty hotové** (`ZPRAVA_NEJISTOTA.md`, modul `nejistota_dan.py` + `kvantily.json`): 80 % a 95 % pro Děčín i Ústí
   na 12/24/36 h, pro lineární regresi, Ridge 30 a G3, z chyb mimo trénink na 22 povodních. Zpětně pokrývá 78–80 % / 94–95 %;
   dnešní 90% pásmo v aplikaci jen 72–83 %. Slabina: při rychlém vzestupu ~2 ze 3, na povodni 6/2013 jen 4 z 10.
2. **Grafy na slajd** (`grafy/`): `pokryti.png`, povodně 1/2011, 9/2010, 6/2013 s pásmem, dva snímky aplikace s pásmem;
   text k vysvětlení „proč je pásmo při vzestupu širší“ v `PREZENTACE_PASMO.md`.
3. **Revize aplikace** (`REVIZE_APLIKACE.md`, sloučeno s Codexem): 2 kritické (bez internetu prázdná Mapa a Animace; Dnešek
   na špatné Wi-Fi zamrzne a chybu drží 10 min) a 6 vysokých (u Borise špatně „model do 2018“, tabulka testu, text u mapy,
   pásmo, Dnešek s modelem do 2018, animace běží neviditelně). `app/test_app.py` prochází 9/9 i 10/10 s Dneškem.
4. **Opravy jen jako návrhy**: `patche/01.patch` … `11.patch` (10 jen po 01), všechny jdou po sobě a test s nimi projde.
5. **Rozhodnout ráno (Ondra, Honza):** které patche vzít do main (bezpečné 02, 03, 04, 05, 07, 08; pásmo = 01 + 10 + sloučit
   `nejistota_dan/`; 06 a 09 po vyzkoušení v prohlížeči). Odkud je video Borise (mapa počítá model do 2018, slajd 611 cm
   je z modelu do 2020). Připravit záložní video a hotspot pro případ bez internetu.
6. **Kmitání při nízké vodě** (`KMITANI.md`): model neměnit. Vyhlazení předpovědi kmitání půlí (provoz Děčín +24 h
   6,2 → 3,1 cm, realita 2,2), ale povodně zhorší o 0,4–1,0 cm a v Ondrově validaci propásne o povodeň víc; vyhlazení
   průtoků pod vodními díly nepomůže. Doporučení: vyhladit jen zobrazení v Dnešku pod 1. stupněm (`patche/11.patch`,
   varování se nemění, test aplikace 10/10). Rozhodnout ráno: vzít patch 11, nebo nechat Dnešek kmitat a říct proč.
7. Codex kontroloval pětkrát (metodika, aplikace, opravy, patche, kmitání), nálezy a reakce v `NALEZY_CODEX.md`. Test 2021–2025
   se nespouštěl.
