"""Kostra tréninku, která běží stejně u nás i na Kaggle.

Lokálně:  python kaggle/train/train.py --quick     (malý vzorek, 1 epocha, na odladění)
Kaggle:   python kaggle/push.py kaggle/train

Doplnit podle úlohy: load_data(), build_model() a případně metriku v evaluate().
"""
import argparse
import json
import random
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn

SEED = 42
ON_KAGGLE = Path("/kaggle/input").exists()
INPUT_DIR = Path("/kaggle/input") if ON_KAGGLE else Path("data/raw")
OUT_DIR = Path("/kaggle/working") if ON_KAGGLE else Path("kaggle/.out/train-local")


def set_seed(seed=SEED):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def pick_device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def find_file(pattern):
    # Na Kaggle se cesta k datasetu může lišit, proto se hledá kdekoli pod vstupní složkou.
    matches = sorted(INPUT_DIR.rglob(pattern))
    if not matches:
        raise FileNotFoundError(f"{pattern} není v {INPUT_DIR}")
    return matches[0]


def load_data(quick):
    """Vrátí (train_loader, val_loader). Doplnit podle úlohy, testovací část sem nepatří."""
    raise NotImplementedError("Doplnit načtení dat podle zadání.")


def build_model():
    """Vrátí model. Doplnit podle úlohy, nejlépe předtrénovaný a jen doladit."""
    raise NotImplementedError("Doplnit model podle zadání.")


def evaluate(model, loader, device):
    model.eval()
    correct = total = 0
    with torch.no_grad():
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            pred = model(x).argmax(dim=1)
            correct += (pred == y).sum().item()
            total += y.numel()
    return {"metrika": correct / max(total, 1)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="malý vzorek a 1 epocha na odladění")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--lr", type=float, default=1e-3)
    args = parser.parse_args()

    set_seed()
    device = pick_device()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    epochs = 1 if args.quick else args.epochs

    train_loader, val_loader = load_data(args.quick)
    model = build_model().to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr)
    loss_fn = nn.CrossEntropyLoss()

    history, best = [], None
    for epoch in range(1, epochs + 1):
        start = time.perf_counter()
        model.train()
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            loss = loss_fn(model(x), y)
            loss.backward()
            optimizer.step()

        metrics = evaluate(model, val_loader, device)
        metrics.update(epoch=epoch, loss=round(loss.item(), 4), seconds=round(time.perf_counter() - start, 1))
        history.append(metrics)
        print(json.dumps(metrics), flush=True)

        # Ukládat průběžně, ať se při pádu o nic nepřijde.
        torch.save(model.state_dict(), OUT_DIR / "last.pt")
        if best is None or metrics["metrika"] > best["metrika"]:
            best = metrics
            torch.save(model.state_dict(), OUT_DIR / "best.pt")
        (OUT_DIR / "metrics.json").write_text(json.dumps(
            {"device": device.type, "args": vars(args), "best": best, "history": history}, indent=2))


if __name__ == "__main__":
    main()
