# Prezentace na 7 minut

Všechno k prezentaci na jednom místě. Prezentujeme od 14:30, odevzdání ve 14:00.

| Soubor | Co tam je |
|---|---|
| `SLAJDY.md` | každý slajd: čas, řečník, co je na slajdu, graf a text řečníka doslova; záložní slajdy Z1–Z10 s odpovědí |
| `OTAZKY.md` | 22 otázek poroty s odpovědí a kdo odpovídá |
| `grafy/` | grafy a obrázky ze slajdů, pojmenované číslem slajdu (`07_boris_2024.png` patří na slajd 7, `Z…` jsou záložní) |

Grafy v `grafy/` jsou kopie z `docs/grafy/prezentace/` (kreslí je `python src/grafy_prezentace.py`), po přegenerování se musí zkopírovat znovu. Fotky `boris_decin_*.jpg`, `mapbox3_decin.jpg` a `video_decin_poster.jpg` jsou snímky z videa a mapy, které používá HTML deck (`web/prezentace/grafy/`). Video se sem nekopíruje (8 MB): je ve `web/prezentace/video/boris_decin_720.mp4`, verze 1920 × 1080 jsou `docs/grafy/video_povoden_decin.mp4` a `video_povoden_usti.mp4` (nejsou v Gitu, má je Honza).

Kostra a proč je takhle postavená: `docs/PREZENTACE_7MIN.md`. Vzhled a Canva: `docs/PREZENTACE.md`. Čísla jsou z `docs/PREHLED.md`, `docs/CESTA_MODELU.md` a `docs/POKUSY.md`.

## Slajdy

Každý slajd odpovídá na jednu otázku poroty, nadpis je odpověď.

| # | Čas | Řečník | Otázka | Nadpis |
|---|---|---|---|---|
| 1 | 0:00–0:45 | Tobias | Co řešíte a pro koho? | Den předem víme, kam v Děčíně dosáhne voda (video) |
| 2 | 0:45–1:25 | Ondra | Odkud se to dá poznat? | Z Prahy teče voda do Děčína 17 hodin, ze Sázavy 25 |
| 3 | 1:25–2:15 | Dan | Co model bere? | Bereme jen řeku, počasí nepomohlo |
| 4 | 2:15–3:25 | Honza | Jak jste vybrali model? | Čtyři modely, vyhrál nejjednodušší |
| 5 | 3:25–4:05 | Honza | Proč zrovna přímka? | Voda v Děčíně je součet řek |
| 6 | 4:05–4:40 | Ondra | Jak víte, že to funguje? | Ověřeno třikrát na povodních, které model neviděl |
| 7 | 4:40–5:25 | Ondra | Funguje to na skutečné povodni? | Boris: 3. stupeň 27 hodin předem, chyba o 55 % menší |
| 8 | 5:25–5:50 | Honza | Dá se to použít? | Každou hodinu nová předpověď z živých dat (snímek, ne živé demo) |
| 9 | 5:50–6:45 | Dan, závěr Tobias | Kde to selže? | Co umíme, co ne a co dál |
| Z1–Z10 | na otázku | podle otázky | | Proč jen lineární regrese? · Co znamená „bude jako teď“? · Proč ne srážky? · Jak moc se pletete? · Funguje to i na jiné povodni? · Podle čeho model rozhoduje? · Je rozliv hydraulický model? · Jak dopadl test? · Není výsledek náhoda výběru validace? · Proč data mimo balíček? |

Rezerva je 15 s. Když se nestíhá, na slajdu 7 vynechat druhý odstavec a říct jen „na testu i ve vícenásobné validaci je chyba o 55 procent menší“.

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
- [ ] Snímek aplikace na slajdu 8 je z dnešního rána a čísla v textu (84, 94, 90 cm) sedí se snímkem.
- [ ] Wi-Fi funguje, záloha hotspot z mobilu.
- [ ] Na flashce: `docs/prezentace.pdf`, video `boris_decin_720.mp4` (nebo 1920 × 1080 od Honzy) a tahle složka.
- [ ] Nabíječka a redukce na projektor.
- [ ] Ve 14:00 odevzdat (PDF a odkaz na deck).

## Když něco selže

Nic neopravovat před porotou.

- Video se nespustí: říct větu ze slajdu 1 nad náhledem a jet dál.
- Deck online se nenačte: PDF z flashky, video zvlášť. Slajd 8 je stejně jen snímek, nic se tím neztratí.
- Porota chce vidět aplikaci a web nejde: aplikace jde pustit lokálně, `.venv/bin/python -m streamlit run app/app.py`, otevře se rovnou na Dnešku (potřebuje internet na data ČHMÚ). Bez internetu ukázat snímek ze slajdu 8 a povodně z archivu (přepínač Dnešek vypnout).
