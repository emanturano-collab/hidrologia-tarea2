"""Sensibilidad POT a umbrales alternativos y comparación con GEV-MLE."""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import genpareto

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
BASE = ROOT / "datos" / "punto2" / "Abtsgmuend_Untergroeningen"
OUT = BASE / "bonificacion_2_5_pot"

def decluster(exc):
    groups = (exc.index.to_series().diff().dt.total_seconds().div(3600).fillna(999) > 24).cumsum()
    return exc.groupby(groups).max()

def require_input(path: Path) -> Path:
    if not path.is_file():
        raise FileNotFoundError(f"Entrada no incluida: {path.relative_to(ROOT)}")
    return path

def main():
    src = pd.read_csv(require_input(BASE / "abtsgmuend_precipitation_10min.csv"))
    src["time"] = pd.to_datetime(src["timestamp_utc"].astype(str), format="%Y%m%d%H%M", utc=True)
    src["p"] = pd.to_numeric(src["precip_mm"], errors="coerce")
    src.loc[src.p < 0, "p"] = np.nan
    hourly = src.set_index("time")["p"].sort_index().resample("1h").sum(min_count=6).dropna()
    years = (hourly.index.max() - hourly.index.min()).total_seconds() / (365.2425 * 86400)
    sensitivity = []
    levels = []
    for pct in [0.90, 0.95, 0.98]:
        u = float(hourly.quantile(pct)); peaks = decluster(hourly[hourly > u]); excess = (peaks-u).to_numpy(float)
        xi, _, beta = genpareto.fit(excess, floc=0); lam = len(peaks)/years
        sensitivity.append({"threshold_percentile": pct, "threshold_mm_h": u, "independent_peaks": len(peaks), "lambda_events_year": lam, "xi": xi, "beta": beta})
        for T in [2,5,10,25,50,100]:
            z=lam*T
            rl=u + beta/xi*(z**xi-1) if abs(xi)>1e-8 else u+beta*np.log(z)
            levels.append({"threshold_percentile":pct,"T_years":T,"pot_mm_1h":rl})
    sens = pd.DataFrame(sensitivity); lev = pd.DataFrame(levels)
    sens.to_csv(OUT/"pot_threshold_sensitivity.csv", index=False, float_format="%.6f")
    lev.to_csv(OUT/"pot_levels_threshold_sensitivity.csv", index=False, float_format="%.6f")
    gev = pd.read_csv(BASE/"idf_2_3"/"idf_gev_mle.csv")
    gev1 = gev[(gev.duration=="1h")][["T_years","quantile_mm"]].rename(columns={"quantile_mm":"gev_mle_mm_1h"})
    cmp = lev.merge(gev1,on="T_years")
    cmp["pot_to_gev_ratio"] = cmp.pot_mm_1h/cmp.gev_mle_mm_1h
    cmp.to_csv(OUT/"pot_vs_gev_1h.csv", index=False, float_format="%.6f")
    lines=["# Sensibilidad POT y comparación con GEV-MLE", "", "Se evaluaron umbrales 90 %, 95 % y 98 %, con declustering de 24 h.", ""]
    lines.append(sens.to_string(index=False, float_format=lambda x:f"{x:.4f}"))
    lines += ["", "## Comparación de niveles 1 h", "", cmp.to_string(index=False, float_format=lambda x:f"{x:.3f}"), "", "Interpretación: si el cociente POT/GEV cambia mucho entre umbrales, la bonificación es sensible al umbral y no debe sustituir la IDF principal."]
    (OUT/"sensibilidad_pot_2_5.md").write_text("\n".join(lines), encoding="utf-8")
    print(sens.to_string(index=False)); print(cmp.to_string(index=False))

if __name__ == "__main__": main()
