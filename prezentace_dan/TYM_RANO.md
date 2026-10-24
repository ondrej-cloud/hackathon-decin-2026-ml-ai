# Ranní brief pro tým (so 24. 10.)

Noc dělal Dan (s Claude a Codexem) na větvích `dan-ridge`, `dan-srazky`, `dan-sit`, `dan-nejistota` a `dan-prezentace`.
Do main nešlo nic. Podklady pro prezentaci jsou v `prezentace_dan/` na větvi `dan-prezentace`.

## Co se v noci zjistilo

1. **Finální model zůstává lineární regrese.** Pro 24 h ji nic z noci ve vícenásobné validaci nepřekonalo aspoň o 1 cm
   (na 36 h jen průzkumné H30, bod 2): směs G3
   (½ regrese + ½ LightGBM, 30 stanic) jen o 0,5 cm (19,6 proti 20,1, lepší 6 z 8). V přísném LOFO přes 22 povodní je G3
   lepší (Děčín +24 h: 13,94 proti 15,29 cm, 20 z 22), na validaci ale horší (D24 18,2 proti 15,5). Síť, srážky ani doba doběhu podle
   průtoku nepomohly.
2. **36 h:** regrese s 30 stanicemi je v LOFO lepší o 2,43 cm (17 z 22), ve vícenásobné validaci jen o 0,71 (Děčín)
   a 1,00 cm (Ústí, na hraně). Průzkumné H30 (+ ukazatel útlumu v nivě) o 2,1 a 2,3 cm, ale nápad vznikl z povodně 2006.
3. **18 nových stanic zlepšují začátek vzestupu** (Děčín +24 h na validaci o 5–8 cm u všech čtyř modelů, fyzika jen s 8 stanicemi), celková chyba je podle modelu smíšená.
4. **Pásmo nejistoty v aplikaci je na povodních moc úzké:** aplikace ukazuje 90% pásmo z chyb na tréninku, ve vnořené
   kontrole na 22 povodních pokrylo jen 72–83 % hodin (80% stejnou metodou 58–72 %). Nové pásmo z chyb mimo trénink pokrývá
   78–80 % a 94–95 %, na rychlém vzestupu 59–72 %. Patch je hotový.
5. **Revize aplikace:** 2 kritické nálezy (bez internetu je mapa a animace prázdná; Dnešek na špatné Wi-Fi na minuty
   zamrzne) a 6 vysokých (texty u Borise a testu, DIBAVOD × výškový model, pásmo). 10 patchů; se všemi prochází test 9 z 9, s 01–09 i Dneškem 10 z 10.
6. **Provoz (Dan):** data ČHMÚ chodí po 20 min, hodnota z celé hodiny je u všech stanic venku do HH:40, proto
   počítat v HH:45 (platí pro okamžité hodnoty v celou hodinu; aplikace ale počítá hodinový průměr t:00–t:50 jako archiv, ten je kompletní až později, sjednotit a ověřit) (při doplnění chybějící hodiny poslední hodnotou je chyba D24 o 1,8 cm horší). Za 29 dní nízké vody byla
   oficiální předpověď ČHMÚ přesnější než naše (D24 5,0 proti 7,5 cm), náš model při nízké vodě kmitá.
7. **Reprodukovatelnost main:** hlavní čísla (17,1 / 20,1 / procenta / aplikace) z čistého klonu sedí
   (`REPRODUKOVATELNOST.md`). Otisk verze výsledků
   se liší mezi Windows a Macem kvůli koncům řádků.

## Na co si dát pozor v prezentaci (porota se na to zeptá)

- **Boris „27 h předem“:** je to čas od vydání varování do skutečného překročení 3. stupně. Model překročení čekal o 3 h
  dřív (předpověděl 577 cm, skutečně 551). Říkat přesně tak (`OTAZKY_POROTY.md`, N11).
- **Slajd 4 „kolik centimetrů přidá každá řeka“:** je to rozklad předpovědi, ne bilance vody (Mělník nese vodu Vltavy
  i Labe). Říkat „každá skupina vstupů“ (N16).
- **Test není dokonale čistý:** ranní průzkum (pá 17:46) zkoušel lineární model i na povodních 12/2023 a 9/2024. Konkrétní
  model byl ale zafixovaný před testem a vícenásobná validace bez testových let dala stejných 55 % (N6).
- **Demo Dneška při nízké vodě:** ČHMÚ je teď přesnější než my (5,0 proti 7,5 cm), říct to dřív, než si toho všimne porota;
  náš model je laděný na povodně.
- **Video Borise ukazuje naměřenou hladinu a z ní odvozený rozliv,** ne předpověď. Čísla 611 cm a 27 h na slajdu jsou
  z předpovědi modelu učeného do 2020 (`docs/DENIK.md` so 2:40, `docs/WEB.md`).

## Co má kdo udělat

- **Ondra:** potvrdit regresi pro 24 h. Rozhodnout 36 h (regrese, Ridge 30, nebo H30 s výhradou; doporučení Dana: nechat
  regresi kvůli jednoduchosti a riziku výpadku 30 stanic živě). Jednořádková oprava `verze()` v `src/porovnej.py`
  (`REPRODUKOVATELNOST.md`). U mentora ověřit otázku 40 (kdo odpovídá za varování). Rozhodnout o patchích aplikace.
- **Honza:** záložní video a hotspot (mapa bez internetu je prázdná), před porotou projít všechny záložky. Patche
  z `nejistota_dan/patche/` podle Danovy ranní zprávy: bezpečné 02, 03, 04, 05, 07, 08 (hláška bez internetu, Dnešek
  kratší čekání a neuloží rozbitý soubor, texty Borise, testu a DIBAVOD…), pásmo 01 + 10, 11 (v Dnešku při nízké vodě průměr předpovědí za 3 h,
  kmitání 6,2 → 3,1 cm, varování beze změny), 06 a 09 až po vyzkoušení
  v prohlížeči. Pro Dnešek předvolit `ridge_vse`; čas výpočtu (HH:45) sladit s hodinovým průměrem. V main je od 4:44 i Honzova webová verze
  (Netlify) a HTML prezentace: domluvit s Tobiasem, která verze prezentace se pouští.
- **Tobias:** Danovy tři slajdy (`DAN_VYSTUP.md`) místo slajdu 5, nebo jako zálohu. Grafy `prezentace_dan/grafy/`:
  G1 (doby doběhu) k slajdu 3 nebo do zálohy, G2 (chyba podle horizontu) do zálohy ke slajdu 10, G3 a G4 k Danovým
  slajdům. Formulace slajdů 4 a 7 podle bodů výš.
- **Dan:** nacvičit 80 s z `DAN_VYSTUP.md`, projít `TAHAK_DAN.md` a nejtěžší otázky N1–N20 (hlavně N6, N8, N11).

## Co se před odevzdáním NEMĚNÍ

- Finální model a čísla v prezentaci: validace 17,1, vícenásobná validace 20,1, test 22,4 cm, Boris. Žádné přeladění.
- Test 2021–2025 se znovu nespouští, rozdělení dat, `evaluate.py` a `features.py` se nemění.
- Model v aplikaci se nemění na G3, Ridge 30 ani H30 bez rozhodnutí Ondry.
- Po 11:00 jen opravy, žádné nové funkce.
