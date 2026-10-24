# Prezentace na 7 minut

Všechno k prezentaci na jednom místě. Prezentujeme od 14:30, odevzdání ve 14:00.

| Soubor | Co tam je |
|---|---|
| `SLAJDY.md` | každý slajd: čas, řečník, co je na slajdu, graf a text řečníka doslova; záložní slajdy Z1–Z10 s odpovědí |
| `OTAZKY.md` | 22 otázek poroty s odpovědí a kdo odpovídá |
| `grafy/` | grafy a obrázky ze slajdů, pojmenované číslem slajdu (`08_boris_2024.png` patří na slajd 8, `Z…` jsou záložní) |

Grafy v `grafy/` jsou kopie z `docs/grafy/prezentace/` (kreslí je `python src/grafy_prezentace.py`), po přegenerování se musí zkopírovat znovu. Fotky `boris_decin_*.jpg`, `mapbox3_decin.jpg` a `video_decin_poster.jpg` jsou snímky z videa a mapy, které používá HTML deck (`web/prezentace/grafy/`). Video se sem nekopíruje (8 MB): je ve `web/prezentace/video/boris_decin_720.mp4`, verze 1920 × 1080 jsou `docs/grafy/video_povoden_decin.mp4` a `video_povoden_usti.mp4` (nejsou v Gitu, má je Honza).

Kostra a proč je takhle postavená: `docs/PREZENTACE_7MIN.md`. Vzhled a Canva: `docs/PREZENTACE.md`. Čísla jsou z `docs/PREHLED.md`, `docs/CESTA_MODELU.md` a `docs/POKUSY.md`.

## Slajdy

| # | Čas | Řečník | Nadpis |
|---|---|---|---|
| 1 | 0:00–0:25 | Tobias | video: Děčín v září 2024 |
| 2 | 0:25–0:50 | Tobias | Den předem víte, kam až voda dosáhne |
| 3 | 0:50–1:30 | Ondra | Co teče Prahou teď, je zítra v Děčíně |
| 4 | 1:30–2:20 | Dan | Co model bere a co ne |
| 5 | 2:20–3:10 | Honza | Od 44 cm k 17: jak jsme došli k přímce |
| 6 | 3:10–3:45 | Honza | Předpověď je součet: kolik centimetrů přidá každá řeka |
| 7 | 3:45–4:20 | Ondra | Ověřujeme třikrát, na povodních, které model neviděl |
| 8 | 4:20–5:10 | Ondra | Boris: 3. stupeň hlášen 27 h předem, chyba o 55 % menší |
| 9 | 5:10–5:40 | Honza | Aplikace: Děčín dnes a za 24 hodin (snímek, ne živé demo) |
| 10 | 5:40–6:40 | Dan, závěr Tobias | Co umíme, co ne a co dál |
| Z1–Z10 | na otázku | podle otázky | Proč jen lineární regrese? · Co znamená „bude jako teď“? · Proč ne srážky? · Jak moc se pletete? · Funguje to i na jiné povodni? · Podle čeho model rozhoduje? · Je rozliv hydraulický model? · Jak dopadl test? · Není výsledek náhoda výběru validace? · Proč data mimo balíček? |

Rezerva je 20 s. Když se nestíhá, na slajdu 8 vynechat druhý odstavec a říct jen „na testu i ve vícenásobné validaci je chyba o 55 procent menší“.

## Jak deck pustit

HTML deck (`web/prezentace/index.html`) je zatím podle staré kostry s živým demem a musí ho Honza přestavět podle tabulky výš. Do té doby platí:

- **Online:** https://field-zero.netlify.app/prezentace/ . Otvírat vždy s lomítkem na konci, ne `/prezentace/index.html`, jinak se deck nenačte.
- **Lokálně:** z kořene repa `npx serve web` a pak http://localhost:3000/prezentace/ .
- **Klávesy:** šipky nebo mezerník další krok, F celá obrazovka, N poznámky řečníka, B černá obrazovka, Home a End na začátek a konec.
- **Canva:** https://www.canva.com/d/xVAIR8am2CrRslj (poznámky řečníka u každé stránky, co dodělat ručně je v `docs/PREZENTACE.md`).
- **PDF záloha:** `docs/prezentace.pdf` (tisk z HTML decku, všechny kroky odkryté, bez videa). Nový se udělá v prohlížeči v decku přes Cmd+P, Uložit jako PDF.

## Před 14:30

- [ ] Nácvik s časomírou v 11:00 a ve 13:00, na druhém hraje Ondra porotu (`OTAZKY.md`). Kdo přetáhne svůj slajd o víc než 10 s, škrtá text.
- [ ] Na Macu, ze kterého se prezentuje: deck na celou obrazovku (F). V druhé kartě web https://field-zero.netlify.app/ na Dnešku, jen pro otázky poroty, během 7 minut se na něj nepřepíná.
- [ ] Video na slajdu 1 se pustí a je bez zvuku.
- [ ] Snímek aplikace na slajdu 9 je z dnešního rána a čísla v textu (84, 94, 90 cm) sedí se snímkem.
- [ ] Wi-Fi funguje, záloha hotspot z mobilu.
- [ ] Na flashce: `docs/prezentace.pdf`, video `boris_decin_720.mp4` (nebo 1920 × 1080 od Honzy) a tahle složka.
- [ ] Nabíječka a redukce na projektor.
- [ ] Ve 14:00 odevzdat (PDF a odkaz na deck).

## Když něco selže

Nic neopravovat před porotou.

- Video se nespustí: říct větu ze slajdu 1 nad náhledem a jet dál.
- Deck online se nenačte: PDF z flashky, video zvlášť. Slajd 9 je stejně jen snímek, nic se tím neztratí.
- Porota chce vidět aplikaci a web nejde: aplikace jde pustit lokálně, `.venv/bin/python -m streamlit run app/app.py`, otevře se rovnou na Dnešku (potřebuje internet na data ČHMÚ). Bez internetu ukázat snímek ze slajdu 9 a povodně z archivu (přepínač Dnešek vypnout).
