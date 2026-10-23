"""Pošle složku se skriptem na Kaggle pod účtem toho, kdo ho spouští.

Použití:  python kaggle/push.py kaggle/gpu-test

V kernel-metadata.json se místo názvu účtu píše KAGGLE_USER, skript ho doplní.
Hotová složka k odeslání vznikne v kaggle/.build/ (není v Gitu).
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Kaggle z virtuálního prostředí, i když není aktivované.
KAGGLE = str(Path(sys.executable).with_name("kaggle")) if Path(sys.executable).with_name("kaggle").exists() else "kaggle"


def kaggle_user():
    if os.environ.get("KAGGLE_USERNAME"):
        return os.environ["KAGGLE_USERNAME"]
    out = subprocess.run([KAGGLE, "config", "view"], capture_output=True, text=True).stdout
    for line in out.splitlines():
        key, _, value = line.strip().lstrip("- ").partition(":")
        if key.strip() == "username" and value.strip() and value.strip() != "None":
            return value.strip()
    sys.exit("Nevím, jaký je tvůj účet na Kaggle. Přihlas se (kaggle auth login) nebo nastav KAGGLE_USERNAME.")


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    src = Path(sys.argv[1])
    user = kaggle_user()
    meta = json.loads((src / "kernel-metadata.json").read_text().replace("KAGGLE_USER", user))

    build = Path(__file__).parent / ".build" / src.name
    shutil.rmtree(build, ignore_errors=True)
    build.mkdir(parents=True)
    shutil.copy(src / meta["code_file"], build / meta["code_file"])
    (build / "kernel-metadata.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))

    cmd = [KAGGLE, "kernels", "push", "-p", str(build)]
    if str(meta.get("enable_gpu")).lower() == "true":
        cmd += ["--accelerator", "NvidiaTeslaT4"]
    subprocess.run(cmd, check=True)
    print(f"\nŽivý výpis: kaggle kernels logs -f {meta['id']}")
    print(f"Stav:       kaggle kernels status {meta['id']}")
    print(f"Výsledky:   kaggle kernels output {meta['id']} -p kaggle/.out/{src.name}")


if __name__ == "__main__":
    main()
