---
name: dan
description: Kontext pro Dana – výchozí zaměření modely a trénink. Spouští Dan na začátku relace.
disable-model-invocation: true
---

Pracuješ s Danem. Má Lenovo Yoga 7i (Core Ultra 7 155H) bez grafiky NVIDIA a Claude Max. Jeho výchozí zaměření jsou modely a trénink, ale role se v týmu míchají, takže může dělat cokoli, co je zrovna potřeba.

Nejdřív:
1. Když nejsi na větvi `dan`, přepni se (`git switch dan`). Pak `git fetch origin` a `git merge origin/main`.
2. Přečti Stav v CLAUDE.md a poslední commity (`git log --all --oneline --since="3 hours ago"`).
3. Jednou nebo dvěma větami shrň stav a co je podle harmonogramu na řadě. Když ve Stavu není, na čem Dan teď dělá, zeptej se.

Když jde o modely:
- Tabulková data, gradient boosting (LightGBM) a scikit-learn trénuj na procesoru, to je rychlé.
- Neuronové sítě a obrázky trénuj na GPU zdarma na Kaggle: skript pošli přes `kaggle kernels push` se zapnutým `enable_gpu` v `kernel-metadata.json` a výsledek stáhni přes `kaggle kernels output`. Data nahraj jako soukromý dataset, ale jen když pořadatelé povolí cloud. Zálohou je Google Colab nebo Tobiasův Mac s M4 (MPS).
- Velký model od nuly netrénuj, dolaďuj předtrénovaný.
- Začni jednoduchým základem (baseline) a každý pokus vyhodnoť společným vyhodnocením. Výsledek ulož jako nový soubor do `results/`.
- Můžeš pustit 2–3 agenty paralelně, každého na jiný přístup.
- Ke každému pokusu zapiš, proč ho zkoušíš. Porota se zeptá.
- Podezřele dobrý výsledek dej zkontrolovat subagentu `kontrolor`.
- Velké modely do Gitu nepatří, sdílej je přes Google Disk.
- Mezi 0:00 a 1:00 je dobré poslat dlouhý trénink na Kaggle, ať běží přes noc.
