Kontrola pouze čtením; nic jsem nezměnil ani nevytvořil. Zkontroloval jsem fyzické řádky 37–39 i ranní položky **#37–39**, které jsou nyní na řádcích 46–48.

| Soubor:řádek | Tvrzení | Co říká zdroj s citací | Zdroj | Oprava |
|---|---|---|---|---|
| `TYM_RANO.md:8` | Nic z noci nepřekonalo regresi ve vícenásobné validaci aspoň o 1 cm. | H30 na 36 h: „Děčín −2,1 cm, Ústí −2,3 cm (6 z 8)“, ovšem průzkumně. | `origin/dan-ridge:ridge_dan/ROZHODNUTI_G3.md`, oddíl H30 | Omezit závěr na 24 h; uvést průzkumnou výjimku H30 pro 36 h. |
| `PREHLED_POKUSU.md:47`; `TYM_RANO.md:19` | Deset patchů, „s nimi test 10 z 10“. | „Se všemi … 9 z 9“; „s 01–09 i `--dnesek` 10 z 10“. | `origin/dan-nejistota:nejistota_dan/REVIZE_APLIKACE.md:5–6` | Se všemi deseti 9/9; s 01–09 a Dneškem 10/10. |
| `TYM_RANO.md:37` | Video Borise je z modelu učeného do 2018. | Hotové video zachycuje „mapa Celá povodeň se skutečnou hladinou, boční panely skryté“. Starší revize popisuje model mapy, nikoli obsah hotového klipu. | `1434c23:docs/DENIK.md`, so 2:40; `b1f89a6:docs/WEB.md`, tabulka dat | Video ukazuje naměřenou hladinu a odvozený rozliv. Čísla 611 cm / 27 h patří předpovědi modelu do 2020. |
| `PREHLED_POKUSU.md:48`; `OTAZKY_POROTY.md:236, 340–342`; `TYM_RANO.md:20–21, 47` | Výpočet v HH:45 řeší dostupnost hodinového vstupu aplikace. | Provozní test používá „hodnota v celou hodinu“. Aplikace však „počítá stejný průměr“ t:00–t:50. Ten v t:45 ještě není kompletní. | `origin/dan-ridge:ridge_dan/PROVOZ.md`, Živá ukázka; `docs/DATA.md:108` | Rozlišit okamžitý odečet HH:00 a archivní hodinový průměr. Doporučení HH:45 podmínit změnou agregace a jejím ověřením. |
| `PREHLED_POKUSU.md:48` | Zhoršení „15,29 → +1,79“. | Tabulka uvádí výchozí chybu 15,29 a **přírůstek** +1,79 cm. | `origin/dan-ridge:ridge_dan/PROVOZ.md`, Dopad zpoždění | „15,29 → 17,08 cm (+1,79 cm)“. |

**Neověřitelná tvrzení v zadaném souboru zdrojů:**

- `PREHLED_POKUSU.md:38`: CV 14,2/15,6; test 16,1/17,5; začátek vzestupu 27,0/32,0. Odkazovaný `ridge_dan/ZPRAVA.md` není mezi zadanými zdroji. Validace 17,8/15,5 doložená je.
- `PREHLED_POKUSU.md:39`; `TYM_RANO.md:14`: přesná zlepšení všech čtyř modelů a rozsah 5–8 cm. Zadané rozhodnutí dokládá například G3 35,4 → 27,8, nikoli všechny čtyři modely; „spolehlivě“ je silnější závěr.
- `TYM_RANO.md:23–24`: reprodukce z čistého klonu. Zadané zdroje potvrzují hlavní čísla a problém CRLF, nikoli tento konkrétní reprodukční běh.
- `TYM_RANO.md:29–30`: skutečnost 551 cm a předpovězené překročení o 3 h dříve. Předpověď 577 cm a předstih 27 h doložené jsou.

**Počty:** 5 typů nesouladů, 4 skupiny neověřitelných tvrzení. Hlavní hodnoty pokrytí pásem, výsledky G3/Ridge 30 a srovnání ČHMÚ 5,0 proti 7,5 cm souhlasí; poslední srovnání platí pro 29 dní nízkého stavu.