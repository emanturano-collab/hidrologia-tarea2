"""Bootstrap de cuantiles GEV-MLE para 2.2 (50 replicas por duracion)."""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
DATA = ROOT / "datos" / "punto2" / "Abtsgmuend_Untergroeningen"
annual = pd.read_csv(DATA / "extremos_2_2" / "ams_hydrological_oct_sep.csv")
DUR = {"10min": 1, "30min": 3, "1h": 6, "3h": 18, "6h": 36, "12h": 72, "24h": 144}
TS = [2, 5, 10, 25, 50, 100]
rng = np.random.default_rng(202602)
rows = []
for duration, win in DUR.items():
    x = annual[f"max_{duration}_mm"].dropna().to_numpy(float)
    for b in range(50):
        xb = rng.choice(x, size=len(x), replace=True)
        pars = stats.genextreme.fit(xb)
        for T in TS:
            q = float(stats.genextreme.ppf(1-1/T, *pars))
            rows.append({"duration": duration, "bootstrap": b, "T_years": T, "quantile_mm": q, "intensity_mm_h": q/(win/6)})
bd = pd.DataFrame(rows)
ci = bd.groupby(["duration", "T_years"]).quantile_mm.agg(q025=lambda z:z.quantile(.025), median="median", q975=lambda z:z.quantile(.975)).reset_index()
ci["relative_width"] = (ci.q975-ci.q025)/ci["median"]
out = DATA / "extremos_2_2" / "bootstrap_ci_gev.csv"
ci.to_csv(out, index=False, float_format="%.5f")
print(f"Guardado {len(ci)} intervalos en {out}")
