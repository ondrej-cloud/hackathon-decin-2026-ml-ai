# Prezentace na 7 minut

Všechno k prezentaci na jednom místě. Prezentujeme od 14:30, odevzdání ve 14:00.

| Soubor | Co tam je |
|---|---|
| `SLAJDY.md` | každý slajd: čas, řečník, co je na slajdu, graf a text řečníka doslova; záložní slajdy Z1–Z11 s odpovědí |
| `OTAZKY.md` | 22 otázek poroty s odpovědí a kdo odpovídá |
| `grafy/` | grafy a obrázky ze slajdů, pojmenované číslem slajdu (`07a_boris_2024.png` patří na slajd 7, `Z…` jsou záložní) |

Grafy v `grafy/` jsou kopie z `docs/grafy/prezentace/` (kreslí je `python src/grafy_prezentace.py`), po přegenerování se musí zkopírovat znovu. Fotky `boris_decin_*.jpg`, `mapbox3_decin.jpg` a `video_decin_poster.jpg` jsou snímky z videa a mapy, které používá HTML deck (`web/prezentace/grafy/`). Video se sem nekopíruje (8 MB): je ve `web/prezentace/video/boris_decin_720.mp4`, verze 1920 × 1080 jsou `docs/grafy/video_povoden_decin.mp4` a `video_povoden_usti.mp4` (nejsou v Gitu, má je Honza).

Kostra a proč je takhle postavená: `docs/PREZENTACE_7MIN.md`. Vzhled a Canva: `docs/PREZENTACE.md`. Čísla jsou z `docs/PREHLED.md`, `docs/CESTA_MODELU.md` a `docs/POKUSY.md`.

## Slajdy

Každý slajd odpovídá na jednu otázku poroty, nadpis je odpověď.

| # | Čas | Řečník | Otázka | Nadpis |
|---|---|---|---|---|
| 1 | 0:00–0:40 | Honza | Co řešíte a pro koho? | Den předem víme, kam v Děčíně dosáhne voda (video) |
| 2 | 0:40–1:20 | Dan | Jaká data jste použili? | Jen z balíčku by to nešlo: bereme 20 let a 12 stanic proti proudu |
| 3 | 1:20–2:10 | Dan | Co model bere? | Bereme jen řeku, počasí nepomohlo |
| 4 | 2:10–3:15 | Ondra | Jak jste vybrali model? | Čtyři modely, vyhrál nejjednodušší |
| 5 | 3:15–3:55 | Ondra | Proč zrovna přímka? | Voda v Děčíně je součet řek |
| 6 | 3:55–4:30 | Honza | Jak ověřujete? | Ověřeno třikrát na povodních, které model neviděl |
| 7 | 4:30–5:25 | Honza | Funguje to doopravdy? | Na všech povodních o polovinu menší chyba, Boris 27 hodin předem |
| 8 | 5:25–5:55 | Tobias | Co z toho má město? | Z předpovědi mapa: kam až voda dosáhne |
| 9 | 5:55–6:45 | Tobias | Kde to selže? | Co neumíme a co dál |
| Z1–Z11 | na otázku | podle otázky | | Proč jen lineární regrese? · Co znamená „bude jako teď“? · Proč ne srážky? · Jak moc se pletete? · Funguje to i na jiné povodni? · Podle čeho model rozhoduje? · Je rozliv hydraulický model? · Jak dopadl test? · Proč jen 36 hodin dopředu? · Jak vypadá aplikace dnes? · Proč je lineární regrese v grafu křivka? |

Rezerva je 15 s. Když se nestíhá, na slajdu 7 z druhého odstavce říct jen „na testu i ve vícenásobné validaci je chyba o 55 procent menší“.

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
- [ ] Mapa rozlivu na slajdu 8 je povodeň 4/2006 (869 proti 829 cm); snímek aplikace v záloze Z10 je z dnešního rána (84, 94, 90 cm).
- [ ] Wi-Fi funguje, záloha hotspot z mobilu.
- [ ] Na flashce: `docs/prezentace.pdf`, video `boris_decin_720.mp4` (nebo 1920 × 1080 od Honzy) a tahle složka.
- [ ] Nabíječka a redukce na projektor.
- [ ] Ve 14:00 odevzdat (PDF a odkaz na deck).

## Když něco selže

Nic neopravovat před porotou.

- Video se nespustí: říct větu ze slajdu 1 nad náhledem a jet dál.
- Deck online se nenačte: PDF z flashky, video zvlášť. Slajd 8 je stejně jen obrázek mapy, nic se tím neztratí.
- Porota chce vidět aplikaci a web nejde: aplikace jde pustit lokálně, `.venv/bin/python -m streamlit run app/app.py`, otevře se rovnou na Dnešku (potřebuje internet na data ČHMÚ). Bez internetu ukázat snímek ze zálohy Z10 a povodně z archivu (přepínač Dnešek vypnout).
