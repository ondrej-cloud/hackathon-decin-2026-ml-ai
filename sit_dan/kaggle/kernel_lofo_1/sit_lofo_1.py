"""LOFO-CV týmové sítě na Kaggle, díl 1/5 foldů (každý 5. fold). Jen procesor, síť je scikit-learn.
Zkopíruje kód a data z datasetu do /tmp/repo, srovná scikit-learn s Danovým notebookem (1.9.1) a pustí lofo_sit.py.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

DIL = "1/5"
print(sys.version, "jader:", os.cpu_count(), flush=True)
zdroj = next(Path("/kaggle/input").rglob("lofo_sit.py")).parents[1]
shutil.copytree(zdroj, "/tmp/repo")
import sklearn  # noqa: E402

if sklearn.__version__ != "1.9.1":
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "scikit-learn==1.9.1"])
subprocess.run([sys.executable, "-c", "import sklearn, pandas; print('verze:', sklearn.__version__, pandas.__version__)"])
r = subprocess.run([sys.executable, "lofo_sit.py", "--foldy", "lofo_foldy.csv", "--vystup", "/kaggle/working/lofo",
                    "--dil", DIL, "--horizonty", "24,12,36", "--seedy", "42", "--prace", str(os.cpu_count())],
                   cwd="/tmp/repo/sit_dan")
sys.exit(r.returncode)
