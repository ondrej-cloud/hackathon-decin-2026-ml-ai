"""Rozbor naměřených zpoždění provozních dat ČHMÚ (zaznamy_now.csv ze sleduj_now.py).

Zpoždění = čas zveřejnění souboru (HTTP Last-Modified) − čas poslední hodnoty stavu H (a průtoku Q) v souboru.
Pro hodinový model: když aplikace počítá v HH:MM z hodnot v celou hodinu, stanice má d hodin starý vstup, jestli hodnota
z HH:00 ještě není zveřejněná. d pro spuštění v HH:00 a v HH:30 se bere z 90. percentilu zpoždění (v minutách).
Výstup: zpozdeni_stanice.csv, zpozdeni_HH00.json a zpozdeni_HH30.json ({stanice: hodiny} pro zpozdeni_simulace.py).

python zpozdeni.py
"""
import json
import math
from pathlib import Path

import pandas as pd

ZDE = Path(__file__).resolve().parent

if __name__ == "__main__":
    d = pd.read_csv(ZDE / "zaznamy_now.csv")
    d["zverejneno"] = pd.to_datetime(d.last_modified_http, format="%a, %d %b %Y %H:%M:%S GMT", utc=True)
    for v in ("H", "Q"):
        d[f"zpozdeni_{v}_min"] = (d.zverejneno - pd.to_datetime(d[f"posledni_{v}"], utc=True)).dt.total_seconds() / 60
    d = d.sort_values(["stanice", "zverejneno"])
    d["interval_min"] = d.groupby("stanice").zverejneno.diff().dt.total_seconds() / 60
    g = d.groupby("stanice")
    S = pd.DataFrame({
        "vzorku": g.size(),
        "H_median_min": g.zpozdeni_H_min.median().round(0), "H_p90_min": g.zpozdeni_H_min.quantile(0.9).round(0),
        "H_max_min": g.zpozdeni_H_min.max().round(0),
        "Q_median_min": g.zpozdeni_Q_min.median().round(0), "Q_p90_min": g.zpozdeni_Q_min.quantile(0.9).round(0),
        "Q_chybi_podil": g.posledni_Q.apply(lambda s: s.isna().mean()).round(2),
        "interval_median_min": g.interval_min.median().round(0),
    })
    # stáří potřebné hodnoty v celou hodinu: rozhoduje horší z H a Q (Q tam, kde existuje)
    S["p90_min"] = S[["H_p90_min", "Q_p90_min"]].max(axis=1)
    S["d_HH00_h"] = S.p90_min.apply(lambda m: math.ceil(m / 60) if m > 0 else 0)
    S["d_HH30_h"] = S.p90_min.apply(lambda m: math.ceil(max(m - 30, 0) / 60))
    S.to_csv(ZDE / "zpozdeni_stanice.csv", encoding="utf-8")
    for sl, f in (("d_HH00_h", "zpozdeni_HH00.json"), ("d_HH30_h", "zpozdeni_HH30.json")):
        (ZDE / f).write_text(json.dumps({k: int(v) for k, v in S[sl].items()}, ensure_ascii=False), encoding="utf-8")
    print(S.to_string())
    print("od", d.zverejneno.min(), "do", d.zverejneno.max(), "| zveřejnění v dávkách:",
          d.zverejneno.dt.floor("min").value_counts().head(5).to_dict())
