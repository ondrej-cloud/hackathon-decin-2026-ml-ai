# Trénink na Kaggle

Kaggle dává zdarma GPU (dvě karty T4, běžný kód využije jednu), kolem 30 hodin týdně na účet. Kolik zbývá, ukáže `kaggle quota`. Hodí se na neuronové sítě a noční tréninky. Tabulková data a LightGBM trénujeme u sebe na procesoru.

## Jednorázové nastavení (každý, kdo bude trénovat)

1. Účet na [kaggle.com](https://www.kaggle.com) a v Settings **ověřit telefon**. Bez toho není GPU ani internet.
2. Přihlásit se: `kaggle auth login`. Otevře prohlížeč, potvrdíš a hotovo, žádný soubor s tokenem se nestahuje.
3. Ověřit: `kaggle kernels list --mine` nesmí skončit chybou.
4. Test GPU: `python kaggle/push.py kaggle/gpu-test`, průběh `kaggle kernels logs -f <účet>/hackathon-gpu-test`, výsledek `kaggle kernels output <účet>/hackathon-gpu-test -p kaggle/.out/gpu-test`.

Když test vypíše `"device": "cpu"`, Kaggle GPU nepřidělil, nejčastěji kvůli neověřenému telefonu.

Stejný test jde pustit i lokálně (`python kaggle/gpu-test/gpu_test.py`) a čísla porovnat. Ondrův M1 naměřil 0,5 TFLOPS (FP32) a 0,62 TFLOPS (FP16).

## Postup při tréninku

1. **Data jen se souhlasem pořadatelů.** Nahrát jako soukromý dataset `hackathon-data`:
   `kaggle datasets init -p <složka s daty>`, v `dataset-metadata.json` nastavit `"id": "<účet>/hackathon-data"`, pak `kaggle datasets create -p <složka> --dir-mode zip`.
   Nová verze dat: `kaggle datasets version -p <složka> -m "co se změnilo" --dir-mode zip`.
2. **Doplnit `train/train.py`** (načtení dat a model) a odladit lokálně: `python kaggle/train/train.py --quick`.
3. **Poslat:** `python kaggle/push.py kaggle/train`.
4. **Sledovat:** `kaggle kernels logs -f <účet>/hackathon-train` ukazuje výpis živě, `kaggle kernels status <účet>/hackathon-train` jen stav.
5. **Stáhnout:** `kaggle kernels output <účet>/hackathon-train -p kaggle/.out/train`. Metriky (`metrics.json`) zkopírovat do `results/`, model (`best.pt`) do `models/` nebo na Google Disk.

`kaggle/.build/` a `kaggle/.out/` nejsou v Gitu. Na více variant najednou: zkopírovat `train/` pod jiným názvem, změnit `id` a `title` v `kernel-metadata.json` a poslat, případně z jiného účtu.

