"""Konvoluční síť po čase (TCN) na surových hodinových řadách posledních 48 h všech 14 řad, cíl je změna hladiny.

Na rozdíl od ostatních modelů nebere vybraná zpoždění z X. Pro každý čas vydání t si z nacti() vezme hodiny
t − 47 … t (hladiny Děčín a Ústí, odmocnina 12 průtoků) a filtry po hodinách se učí sama. Z X bere jen index
(čas vydání) a hladinu teď.
"""
import time

import numpy as np
import torch
from torch import nn

from data import nacti

# s 32 kanály trval trénink Děčín +24 h 6 min (limit 5 min na kombinaci), proto 16
PARAMETRY = dict(okno_h=48, kanaly=16, jadro=3, dilatace=(1, 2, 4, 8, 16), dropout=0.1, lr=1e-3, weight_decay=1e-4,
                 batch=512, max_epoch=30, trpelivost=5, zastaveni="posledních 10 % trénovacích řádků v čase",
                 seed=42, cil="změna hladiny", vstupy="14 surových hodinových řad za 48 h, odmocnina průtoků")


class Blok(nn.Module):
    def __init__(self, kanaly, jadro, dilatace, dropout):
        super().__init__()
        self.doplnit = (jadro - 1) * dilatace
        self.conv = nn.Conv1d(kanaly, kanaly, jadro, dilation=dilatace)
        self.drop = nn.Dropout(dropout)

    def forward(self, x):
        # nuly jen zleva: výstup v hodině i vidí jen hodiny <= i (kauzální konvoluce)
        return x + self.drop(torch.relu(self.conv(nn.functional.pad(x, (self.doplnit, 0)))))


class TCN(nn.Module):
    def __init__(self, rad, p):
        super().__init__()
        self.vstup = nn.Conv1d(rad, p["kanaly"], 1)
        self.bloky = nn.Sequential(*[Blok(p["kanaly"], p["jadro"], d, p["dropout"]) for d in p["dilatace"]])
        self.vystup = nn.Linear(p["kanaly"], 1)

    def forward(self, x):  # x: (řádky, řady, hodiny), poslední hodina je čas vydání
        return self.vystup(self.bloky(self.vstup(x))[:, :, -1]).squeeze(1)


def rady():
    """Hodinové řady: hladiny Děčín a Ústí a odmocnina 12 průtoků. Díra v Děčíně 2/2006 je doplněná
    poslední známou hodnotou, tedy jen z minulosti."""
    D = nacti()
    H, Q = [c for c in D if c.endswith("_H")], [c for c in D if c.endswith("_Q")]
    R = D[H + Q].copy()
    R[Q] = np.sqrt(R[Q].clip(lower=0))
    return R.ffill()


def fit(X, y, cil, horizont, seed=PARAMETRY["seed"], okno=PARAMETRY["okno_h"]):
    p = PARAMETRY
    t0 = time.time()
    torch.manual_seed(seed)
    R = rady()
    poz = R.index.get_indexer(X.index)
    assert (poz >= 0).all() and X.index.is_monotonic_increasing
    stred, rozptyl = R.iloc[poz].mean(), R.iloc[poz].std()
    A = ((R - stred) / rozptyl).fillna(0).to_numpy(np.float32)
    A = torch.from_numpy(np.vstack([np.zeros((okno - 1, A.shape[1]), np.float32), A]))
    posun = torch.arange(1 - okno, 1)

    def okna(i):
        """Hodiny t − okno + 1 … t pro každou pozici t v R, tvar (řádky, řady, hodiny)."""
        return A[(i + okno - 1)[:, None] + posun].transpose(1, 2)

    def vstupy(index):
        i = R.index.get_indexer(index)
        assert (i >= 0).all()
        return okna(torch.from_numpy(i))

    zmena = y.to_numpy() - X[f"{cil}_H_0"].to_numpy()
    z_stred, z_rozptyl = zmena.mean(), zmena.std()
    Z = torch.tensor((zmena - z_stred) / z_rozptyl, dtype=torch.float32)
    P = torch.from_numpy(poz)
    n_stop = len(X) // 10
    uc, st = torch.arange(len(X) - n_stop), torch.arange(len(X) - n_stop, len(X))

    sit = TCN(A.shape[1], p)
    opt = torch.optim.Adam(sit.parameters(), lr=p["lr"], weight_decay=p["weight_decay"])
    g = torch.Generator().manual_seed(seed)
    nejlepsi, stav, kdy = np.inf, None, 0
    for epocha in range(p["max_epoch"]):
        sit.train()
        for b in uc[torch.randperm(len(uc), generator=g)].split(p["batch"]):
            opt.zero_grad()
            ztrata = ((sit(okna(P[b])) - Z[b]) ** 2).mean()
            ztrata.backward()
            opt.step()
        sit.eval()
        with torch.no_grad():
            chyba = float(torch.cat([(sit(okna(P[b])) - Z[b]) ** 2 for b in st.split(4096)]).mean())
        if chyba < nejlepsi:
            nejlepsi, kdy = chyba, epocha
            stav = {k: v.clone() for k, v in sit.state_dict().items()}
        print(f"    epocha {epocha + 1}: MSE na zastavovací části {chyba:.4f}, {time.time() - t0:.0f} s")
        if epocha - kdy >= p["trpelivost"]:
            break
    sit.load_state_dict(stav)
    sit.eval()
    print(f"    TCN {cil} +{horizont} h: nejlepší epocha {kdy + 1}, trénink {time.time() - t0:.0f} s")

    def predict(Xp):
        with torch.no_grad():
            out = torch.cat([sit(vstupy(Xp.index[i:i + 4096])) for i in range(0, len(Xp), 4096)]).numpy()
        return Xp[f"{cil}_H_0"].to_numpy() + out * z_rozptyl + z_stred

    # pro vysvětlení (src/tcn_odezvy.py)
    predict.sit, predict.vstupy, predict.cm = sit, vstupy, z_rozptyl
    predict.rady, predict.stred, predict.rozptyl = list(R.columns), stred, rozptyl
    return predict
