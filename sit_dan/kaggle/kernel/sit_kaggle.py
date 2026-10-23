"""Spouštěč na Kaggle: zkopíruje kód a data z datasetu do /tmp/repo, srovná scikit-learn s verzí na Danově notebooku
a pustí sit_dan/beh_sit.py (tolik tréninků souběžně, kolik je jader). Výstup do /kaggle/working/vystup.

Síť je scikit-learn (MLPRegressor), počítá na procesoru, GPU nevyužije.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

print(sys.version, flush=True)
subprocess.run(["nvidia-smi", "-L"])
print("jader:", os.cpu_count(), flush=True)
subprocess.run(["free", "-g"])

zdroj = next(Path("/kaggle/input").rglob("beh_sit.py")).parents[1]
shutil.copytree(zdroj, "/tmp/repo")
print("kód a data z", zdroj, flush=True)

import sklearn  # noqa: E402

if sklearn.__version__ != "1.9.1":
    print("předinstalovaný scikit-learn", sklearn.__version__, "-> instaluji 1.9.1", flush=True)
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "scikit-learn==1.9.1"])
subprocess.run([sys.executable, "-c", "import sys, sklearn, pandas, numpy; "
                "print('verze:', sys.version.split()[0], sklearn.__version__, pandas.__version__, numpy.__version__)"])

prikaz = [sys.executable, "beh_sit.py", "--prace", str(os.cpu_count()), "--vystup", "/kaggle/working/vystup"]
srazky = Path("/tmp/repo/sit_dan/tabulka/srazky_6h.parquet")
if srazky.exists():  # v datasetu je i tabulka srážek: varianty a, b, c na společných hodinách se srážkami
    prikaz += ["--srazky", str(srazky)]
print(" ".join(prikaz), flush=True)
r = subprocess.run(prikaz, cwd="/tmp/repo/sit_dan")
sys.exit(r.returncode)
