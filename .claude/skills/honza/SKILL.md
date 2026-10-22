---
name: honza
description: Role Honzy – aplikace ve Streamlitu a grafy. Spouští Honza na začátku relace.
disable-model-invocation: true
---

Pracuješ s Honzou. Má na starosti aplikaci ve Streamlitu a grafy.

Nejdřív:
1. Když nejsi na větvi `honza`, přepni se (`git switch honza`). Pak `git fetch origin` a `git merge origin/main`.
2. Přečti sekci Stav v CLAUDE.md a poslední commity ostatních (`git log --all --oneline --since="3 hours ago"`).
3. Jednou nebo dvěma větami shrň stav a co je podle harmonogramu teď na řadě.

Honzův notebook je starší. Těžké knihovny instaluj jen tehdy, když jsou opravdu potřeba. Finální demo poběží na Tobiasově Macu s M4, takže tam aplikace musí jít spustit.

Postup:
1. Do 19:00 kostra `app/app.py` a `app/fake_predict.py`. Falešná verze má stejnou funkci jako budoucí `src/predict.py` a vrací věrohodná data. Aplikace zkusí importovat `src.predict` a když ho nenajde, použije falešnou verzi.
2. Do 21:00 napoj první skutečný model od Dana.
3. Navrhuj pro laika: jedna obrazovka, vstup → výsledek → jednoduché vysvětlení, proč to tak vyšlo. České popisky, srozumitelné grafy, žádný žargon. Na první pohled musí být jasné, komu aplikace pomáhá (sekce Stav).
4. Grafy pro prezentaci ukládej i jako obrázky do `app/obrazky/`, ať je má Tobias.
5. Udržuj `app/requirements.txt` se vším, co aplikace potřebuje.
6. V sobotu 8:00–11:00 napoj finální model a vyzkoušej aplikaci na Tobiasově Macu.
7. Do 13:00 natoč záložní video dema (nahrávku obrazovky) pro případ, že na prezentaci něco selže.

Aplikace se spouští příkazem `streamlit run app/app.py`.
