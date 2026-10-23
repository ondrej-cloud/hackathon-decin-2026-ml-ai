---
name: kaggle
description: Trénink na GPU na Kaggle – nahrání dat, odeslání skriptu, sledování běhu a stažení výsledků. Použij, když je potřeba trénovat neuronovou síť nebo pustit dlouhý trénink přes noc.
argument-hint: "[co natrénovat]"
---

Postup je v `kaggle/README.md`. Úkol: $ARGUMENTS

1. **Kontrola nastavení:** `kaggle kernels list --mine`. Když to selže, člověk není přihlášený: ať sám spustí `! kaggle auth login` (otevře prohlížeč). Přihlašovací údaje v `~/.kaggle/` nikdy nečti ani nevypisuj.
2. **Data:** cloud jen se souhlasem pořadatelů (Stav v CLAUDE.md). Když dataset `<účet>/hackathon-data` neexistuje nebo jsou data nová, nahraj ho podle README, vždy jako soukromý.
3. **Skript:** vycházej z `kaggle/train/train.py`. Na více variant najednou udělej kopii složky s jiným `id` a `title`.
4. **Odladit lokálně:** `python kaggle/train/train.py --quick`. Na Kaggle posílej jen kód, který lokálně proběhl.
5. **Odeslat:** `python kaggle/push.py <složka>`.
6. **Sledovat:** `kaggle kernels logs -f <id>` na pozadí ukazuje výpis živě. Když běh skončí chybou, přečti log a oprav kód.
7. **Výsledky:** `kaggle kernels output <id> -p kaggle/.out/<složka>`. Metriky ulož jako nový soubor do `results/` (autor, čas, popis, metrika, parametry, `"kde": "kaggle"`). Model do `models/` nebo na Google Disk, ne do Gitu.
8. Jednou větou řekni, co doběhlo, s jakým výsledkem a jak dlouho to trvalo. Zbývající hodiny GPU ukáže `kaggle quota`.
