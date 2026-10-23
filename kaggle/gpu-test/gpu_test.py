"""Zjistí, jakou grafiku PyTorch vidí, a změří její rychlost na násobení matic.

Běží stejně na Kaggle i u nás, takže čísla jdou přímo porovnat:
    python kaggle/gpu-test/gpu_test.py
"""
import json
import platform
import time
from pathlib import Path

import torch


def pick_device():
    if torch.cuda.is_available():
        return torch.device("cuda"), torch.cuda.get_device_name(0)
    if torch.backends.mps.is_available():
        return torch.device("mps"), "Apple GPU (MPS)"
    return torch.device("cpu"), platform.processor() or "CPU"


def sync(device):
    if device.type == "cuda":
        torch.cuda.synchronize()
    elif device.type == "mps":
        torch.mps.synchronize()


def tflops(device, dtype, n=4096, repeats=20):
    a = torch.randn(n, n, device=device, dtype=dtype)
    b = torch.randn(n, n, device=device, dtype=dtype)
    for _ in range(3):
        a @ b
    sync(device)
    start = time.perf_counter()
    for _ in range(repeats):
        a @ b
    sync(device)
    seconds = time.perf_counter() - start
    return round(2 * n**3 * repeats / seconds / 1e12, 2)


def main():
    device, name = pick_device()
    result = {
        "device": device.type,
        "name": name,
        "torch": torch.__version__,
        "tflops_fp32": tflops(device, torch.float32),
    }
    if device.type in ("cuda", "mps"):
        result["tflops_fp16"] = tflops(device, torch.float16)

    out_dir = Path("/kaggle/working") if Path("/kaggle/working").exists() else Path("kaggle/.out/gpu-test-local")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "gpu_test.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
