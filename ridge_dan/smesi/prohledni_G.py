import sys; sys.path.insert(0, r"C:\Users\danie\Documents\hackathon-2026-ridge\ridge_dan\zlepseni"); import lofo as L
from pathlib import Path
import pyarrow.parquet as pq
import pandas as pd
import json

base = Path(__file__).resolve().parent.parent / "stanice_vsem"
for name in ("predpovedi_ridge_12_None.parquet", "predpovedi_ridge_30_None.parquet", "predpovedi_lgbm_30_42.parquet"):
    f = pq.ParquetFile(base / name)
    print(name, f.schema_arrow, "rows", f.metadata.num_rows, flush=True)
    idx = json.loads(f.schema_arrow.metadata[b"pandas"])["index_columns"][0]
    d = pd.read_parquet(base / name, filters=[(idx, "<", L.KONEC)])
    print(d.head(2).to_string(), d.dtypes.to_dict(), flush=True)
    for c in d.columns.difference(["y", "pred"]):
        print(c, d[c].unique().tolist(), flush=True)
