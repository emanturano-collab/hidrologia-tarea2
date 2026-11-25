"""Bonificación 2.5: Peaks Over Threshold (POT) para lluvia horaria.

Usa la serie de 10 minutos, exige seis datos por hora y declustra excedencias
separadas por al menos 24 h. El resultado es un análisis complementario, no un
reemplazo de la AMS/GEV usada en 2.2.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import genpareto

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
BASE = ROOT / "datos" / "punto2" / "Abtsgmuend_Untergroeningen"
OUT = BASE / "bonificacion_2_5_pot"
OUT.mkdir(exist_ok=True)

def require_input(path: Path) -> Path:
    if not path.is_file():
        raise FileNotFoundError(f"Entrada no incluida: {path.relative_to(ROOT)}")
    return path

def main():
    src = pd.read_csv(require_input(BASE / "abtsgmuend_precipitation_10min.csv"))
    src["time"] = pd.to_datetime(src["timestamp_utc"].astype(str), format="%Y%m%d%H%M", utc=True)
    src["p"] = pd.to_numeric(src["precip_mm"], errors="coerce")
    src.loc[src.p < 0, "p"] = np.nan
    s = src.set_index("time")["p"].sort_index()
    hourly = s.resample("1h").sum(min_count=6).dropna()
    threshold = float(hourly.quantile(0.95))
    exc = hourly[hourly > threshold]
    groups = (exc.index.to_series().diff().dt.total_seconds().div(3600).fillna(999) > 24).cumsum()
    peaks = exc.groupby(groups).max()
    excess = (peaks - threshold).to_numpy(float)
    if len(excess) < 10:
        raise RuntimeError(f"Solo {len(excess)} picos POT; se requieren al menos 10")
    xi, loc, beta = genpareto.fit(excess, floc=0)
    beta = float(beta); xi = float(xi)
    years = (hourly.index.max() - hourly.index.min()).total_seconds() / (365.2425 * 86400)
    lam = len(peaks) / years
    rows = []
    for T in [2, 5, 10, 25, 50, 100]:
        z = lam * T
        if abs(xi) < 1e-8:
            rl = threshold + beta * np.log(z)
        else:
            rl = threshold + beta / xi * (z ** xi - 1)
        rows.append({"T_years": T, "return_level_mm_1h": float(rl), "intensity_mm_h": float(rl), "threshold_mm": threshold, "lambda_events_year": lam})
    pd.DataFrame(rows).to_csv(OUT / "pot_return_levels.csv", index=False, float_format="%.5f")
    peaks.rename("peak_1h_mm").to_csv(OUT / "pot_declustered_peaks.csv", header=True, date_format="%Y-%m-%dT%H:%M:%SZ")
    summary = f'''# Bonificación 2.5 — Peaks Over Threshold (POT)

- Variable: precipitación acumulada en 1 h a partir de datos de 10 minutos.
- Periodo disponible: {hourly.index.min().date()} a {hourly.index.max().date()} ({years:.2f} años).
- Umbral: percentil 95 = **{threshold:.3f} mm/h**.
- Regla de declustering: máximos separados por más de 24 h.
- Picos independientes: **{len(peaks)}**.
- Tasa de excedencia: **{lam:.3f} eventos/año**.
- Ajuste: distribución Generalizada de Pareto a los excesos, xi={xi:.5f}, beta={beta:.5f}.

Los niveles de retorno están en `pot_return_levels.csv`. POT es una
bonificación complementaria a la AMS/GEV de 2.2; no se mezclan ambas
estimaciones sin una decisión estadística adicional. La sensibilidad al umbral
y a la ventana de 24 h debe reconocerse como incertidumbre.
'''
    (OUT / "revision_pot_2_5.md").write_text(summary, encoding="utf-8")
    print(f"POT terminado: {len(peaks)} picos, umbral={threshold:.3f} mm/h, xi={xi:.5f}")

if __name__ == "__main__": main()
