"""Síť ve variantách a, b, c (+ srážky) na společných hodinách se srážkami, díl 1/4 úloh. Jen procesor.
Zkopíruje kód a data z datasetu do /tmp/repo, srovná scikit-learn s Danovým notebookem (1.9.1) a pustí beh_sit.py.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

DIL = "1/4"
print(sys.version, "jader:", os.cpu_count(), flush=True)
zdroj = next(Path("/kaggle/input").rglob("srazky_6h.parquet")).parents[2]
shutil.copytree(zdroj, "/tmp/repo")
import sklearn  # noqa: E402

if sklearn.__version__ != "1.9.1":
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "scikit-learn==1.9.1"])
subprocess.run([sys.executable, "-c", "import sklearn, pandas; print('verze:', sklearn.__version__, pandas.__version__)"])
r = subprocess.run([sys.executable, "beh_sit.py", "--srazky", "/tmp/repo/sit_dan/tabulka/srazky_6h.parquet",
                    "--dil", DIL, "--prace", str(os.cpu_count()), "--vystup", "/kaggle/working/vystup"],
                   cwd="/tmp/repo/sit_dan")
sys.exit(r.returncode)
