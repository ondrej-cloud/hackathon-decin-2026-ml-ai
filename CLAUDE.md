# Hackathon ML/AI 2026

Plán týmu, role a harmonogram jsou v README.md. Podklady o minulých ročnících jsou v docs/brainstorming-podklady.md.

## Zadání
(Tobias doplní hned po výběru tématu: co řešíme, pro koho, jak poznáme úspěch)

## Data
(kde leží: data/raw/, co obsahují, sloupce, velikost)

## Metrika
(jedna metrika, např. F1 nebo MAE; počítá ji jen src/evaluate.py na validační části)

## Kdo vlastní které soubory
- Ondra: data/split/, src/evaluate.py, src/features.py
- Dan: src/train_*.py, src/predict.py, models/
- Honza: app/
- Tobias: CLAUDE.md, docs/

## Pravidla pro Claude
- Měň jen soubory toho, kdo s tebou pracuje. Cizí soubory jen čti.
- Nikdy netrénuj ani nelaď na testovací části z data/split/.
- Každý pokus vyhodnoť přes src/evaluate.py a ulož jako nový soubor v results/.
- Po každém funkčním kroku: git pull --rebase, commit jen svých souborů, git push.
- Do commitu napiš jednou větou, co a proč.
- Nikdy git push --force. Data a .env nikdy do Gitu.
