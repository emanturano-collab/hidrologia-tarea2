"""Control y maxima anual de la serie DWD de 10 minutos."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
DATA = ROOT / "datos" / "punto2" / "Abtsgmuend_Untergroeningen"

def require_input(path: Path) -> Path:
    if not path.is_file():
        raise FileNotFoundError(f"Entrada no incluida: {path.relative_to(ROOT)}")
    return path

def main():
    src = require_input(DATA / "abtsgmuend_precipitation_10min.csv")
    df = pd.read_csv(src)
    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"].astype(str), format="%Y%m%d%H%M", errors="coerce")
    # -999 y cualquier indicador de valor faltante se convierten a NaN.
    df["precip_mm"] = pd.to_numeric(df["precip_mm"], errors="coerce")
    df.loc[df["precip_mm"] < 0, "precip_mm"] = np.nan
    df = df.dropna(subset=["timestamp_utc"]).sort_values("timestamp_utc")
    df = df.set_index("timestamp_utc")
    usable = df.loc["2005-01-01":"2025-12-31 23:59:59", ["precip_mm"]]
    durations = {"10min": 1, "30min": 3, "1h": 6, "3h": 18, "6h": 36, "12h": 72, "24h": 144}
    out = []
    for year, g in usable.groupby(usable.index.year):
        row = {"year": int(year), "records": int(len(g)), "valid_10min": int(g.precip_mm.notna().sum())}
        for label, win in durations.items():
            sums = g["precip_mm"].rolling(win, min_periods=win).sum()
            if sums.notna().any():
                idx = sums.idxmax()
                row[f"max_{label}_mm"] = float(sums.loc[idx])
                row[f"max_{label}_timestamp_utc"] = idx.isoformat()
            else:
                row[f"max_{label}_mm"] = np.nan
                row[f"max_{label}_timestamp_utc"] = ""
        out.append(row)
    ams = pd.DataFrame(out)
    ams.to_csv(DATA / "ams_precipitation.csv", index=False, float_format="%.3f")
    qc = usable.resample("YE").agg(records=("precip_mm", "size"), valid=("precip_mm", "count"))
    qc["year"] = qc.index.year
    qc["completeness_pct"] = 100 * qc["valid"] / qc["records"]
    qc[["year", "records", "valid", "completeness_pct"]].to_csv(DATA / "rainfall_qc_summary.csv", index=False, float_format="%.3f")
    print(f"Años procesados: {len(ams)}; AMS: {DATA / 'ams_precipitation.csv'}")

if __name__ == "__main__":
    main()
