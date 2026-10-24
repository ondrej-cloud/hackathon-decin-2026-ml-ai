# Prezentace na 7 minut

Všechno k prezentaci na jednom místě. Prezentujeme od 14:30, odevzdání ve 14:00.

| Soubor | Co tam je |
|---|---|
| `SLAJDY.md` | každý slajd: čas, řečník, co je na slajdu, graf a text řečníka doslova; demo klik po kliku; záložní slajdy Z1–Z7 |
| `OTAZKY.md` | 20 otázek poroty s odpovědí a kdo odpovídá |
| `grafy/` | grafy a obrázky ze slajdů, pojmenované číslem slajdu (`07_boris_2024.png` patří na slajd 7, `Z…` jsou záložní) |

Grafy v `grafy/` jsou kopie z `docs/grafy/prezentace/` (kreslí je `python src/grafy_prezentace.py`), po přegenerování se musí zkopírovat znovu. Fotky `boris_decin_*.jpg`, `mapbox3_decin.jpg` a `video_decin_poster.jpg` jsou snímky z videa a mapy, které používá HTML deck (`web/prezentace/grafy/`). Video se sem nekopíruje (8 MB): je ve `web/prezentace/video/boris_decin_720.mp4`, verze 1920 × 1080 jsou `docs/grafy/video_povoden_decin.mp4` a `video_povoden_usti.mp4` (nejsou v Gitu, má je Honza).

Odkud je obsah: pořadí a texty slajdů podle HTML decku (`web/prezentace/index.html`, Honza), časy a řečníci podle kostry (`docs/PREZENTACE_7MIN.md`, Ondra), vzhled a Canva v `docs/PREZENTACE.md`. Čísla jsou z `docs/PREHLED.md` a `docs/CESTA_MODELU.md`.

## Slajdy

| # | Čas | Řečník | Nadpis |
|---|---|---|---|
| 1 | 0:00–0:25 | Tobias | video: Děčín v září 2024 |
| 2 | 0:25–0:55 | Tobias | Den předem víte, kam až voda dosáhne |
| 3 | 0:55–1:40 | Ondra | Co teče Prahou teď, je zítra v Děčíně |
| 4 | 1:40–2:15 | Honza | Předpověď je součet: kolik centimetrů přidá každá řeka |
| 5 | 2:15–2:55 | Dan | Žádná z 11 dalších cest nebyla lepší |
| 6 | 2:55–3:30 | Ondra | Ověřujeme třikrát, pokaždé na povodních, které model neviděl |
| 7 | 3:30–4:10 | Ondra | Boris: 3. stupeň hlášen 27 hodin předem |
| 8 | 4:10–4:40 | Ondra | O 55 % menší chyba na testu i na všech 8 povodních |
| 9 | 4:40–5:50 | Honza | Živé demo |
| 10 | 5:50–7:00 | Dan, závěr Tobias | Co umíme, co ne a co dál |
| Z1–Z7 | na otázku | podle otázky | Proč jen lineární regrese? · Co znamená „bude jako teď“? · Proč ne srážky? · Jak moc se pletete? · Funguje to i na jiné povodni? · Podle čeho model rozhoduje? · Je rozliv hydraulický model? |

Když se nestíhá: slajd 8 jen jednou větou na konci slajdu 7 a demo zkrátit na mapu.

## Jak deck pustit

- **Online (na prezentaci):** https://field-zero.netlify.app/prezentace/ . Otvírat vždy s lomítkem na konci, ne `/prezentace/index.html`, jinak se deck nenačte. Odkazy z dema vedou do aplikace na stejném webu.
- **Lokálně:** z kořene repa `npx serve web` a pak http://localhost:3000/prezentace/ . Pozor, lokální server zahazuje parametry v odkazech na `index.html`, takže odkaz „Boris v aplikaci“ lokálně neotevře Borise; mapy (`web/mapa/*.html`) lokálně existují jen po `python src/export_web.py --vse` s tokenem Mapboxu. Demo proto jet z webu.
- **Klávesy:** šipky nebo mezerník další krok, F celá obrazovka, N poznámky řečníka, B černá obrazovka, Home a End na začátek a konec.
- **Canva:** https://www.canva.com/d/xVAIR8am2CrRslj (stejný obsah, poznámky řečníka u každé stránky, co dodělat ručně je v `docs/PREZENTACE.md`).
- **PDF záloha:** `docs/prezentace.pdf` (17 stran, tisk z HTML decku, všechny kroky odkryté, bez videa). Nový se udělá v prohlížeči v decku přes Cmd+P, Uložit jako PDF.

## Před 14:30

- [ ] Nácvik s časomírou v 11:00 a ve 13:00, na druhém hraje Ondra porotu (`OTAZKY.md`). Kdo přetáhne svůj slajd o víc než 10 s, škrtá text.
- [ ] Na Macu, ze kterého se prezentuje: deck online otevřený na celou obrazovku (F), v druhé kartě aplikace https://field-zero.netlify.app/ na Dnešku.
- [ ] Video na slajdu 1 se pustí a je bez zvuku.
- [ ] Dnešek ukazuje dnešní hodinu, ne včerejší (stáří dat do 2 až 3 h). Když je starší, říct to Ondrovi, Dnešek se dá obnovit skriptem `src/dnesek_export.py` (`docs/WEB.md`).
- [ ] Odkaz Boris v aplikaci otevře 14. 9. 2024 11:00 (teď 389 cm, za 24 h 577 cm) a mapa Borise se načte a přehraje.
- [ ] Wi-Fi funguje, záloha hotspot z mobilu.
- [ ] Na flashce: `docs/prezentace.pdf`, video `boris_decin_720.mp4` (nebo 1920 × 1080 od Honzy) a tahle složka.
- [ ] Nabíječka a redukce na projektor.
- [ ] Ve 14:00 odevzdat (PDF a odkaz na deck).

## Když demo selže

Nic neopravovat před porotou. Podrobně je to u slajdu 9 v `SLAJDY.md`:

- Dnešek se nenačte nebo jsou data stará: „Živá data ČHMÚ teď nedorazila, ukážu povodeň, u které víme, jak dopadla“, a rovnou Boris.
- Mapa se nenačte: Zavřít mapu, Home na slajd 1, pustit video a říct „takhle vypadá rozliv po hodinách“, pak na slajd 10.
- Nejde internet: deck z flashky jako PDF, video zvlášť, demo vynechat jednou větou a jet na slajd 10. Kratší prezentace nevadí, přetažená ano.
- Kdyby nešel ani web, aplikace jde pustit lokálně: `.venv/bin/python -m streamlit run app/app.py`, přepínač „Dnešek: živá data ČHMÚ“ vlevo, když už není zapnutý (potřebuje internet na data ČHMÚ).
