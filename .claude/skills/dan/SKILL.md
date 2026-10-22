---
name: dan
description: Role Dana – model a trénink. Spouští Dan na začátku relace.
disable-model-invocation: true
---

Pracuješ s Danem. Má na starosti model a trénink.

Nejdřív:
1. Když nejsi na větvi `dan`, přepni se (`git switch dan`). Pak `git fetch origin` a `git merge origin/main`.
2. Přečti sekci Stav v CLAUDE.md a poslední commity ostatních (`git log --all --oneline --since="3 hours ago"`).
3. Jednou nebo dvěma větami shrň stav a co je podle harmonogramu teď na řadě.

Výpočetní výkon:
- Dan má Lenovo Yoga 7i (Core Ultra 7 155H) bez grafiky NVIDIA.
- Tabulková data, gradient boosting (LightGBM) a scikit-learn trénuj na procesoru, to je rychlé.
- Neuronové sítě a obrázky trénuj na GPU zdarma na Kaggle: skript pošli přes `kaggle kernels push` s `enable_gpu` zapnutým v `kernel-metadata.json` a výsledek stáhni přes `kaggle kernels output`. Data nahraj jako soukromý dataset, ale jen když pořadatelé povolí cloud. Zálohou je Google Colab nebo Tobiasův Mac s M4 (MPS).
- Velký model od nuly netrénuj, dolaďuj předtrénovaný.

Postup:
1. Do 19:00 jednoduchý model (baseline) přes `load_split()` a `src/evaluate.py`. Dokud Ondrovo rozdělení není hotové, použij dočasné, ale počítají se jen výsledky na oficiálním.
2. Každý přístup patří do vlastního `src/train_<popis>.py` a každý pokus se ukládá přes `save_result`. Můžeš pustit 2–3 agenty paralelně, každého na jiný přístup a do vlastního souboru.
3. Do 21:00 první skutečné `src/predict.py` podle dohody s Honzou, pak `/sync main`.
4. Mezi 0:00 a 1:00 připrav dlouhý trénink a pošli ho na Kaggle, ať běží přes noc.
5. Ráno ho vyhodnoť, s Ondrou vyberte finální model a do 11:00 dodej finální `predict.py` a model.

Vždycky:
- Ke každému pokusu zapiš, proč ho zkoušíš. Porota se zeptá.
- Podezřele dobrý výsledek dej zkontrolovat subagentu `kontrolor`.
- Velké modely do Gitu nepatří (`models/*.pt` se ignoruje), sdílej je přes Google Disk.
