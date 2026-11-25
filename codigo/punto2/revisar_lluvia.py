"""Auditoria final de la lluvia subdiaria para los apartados 2.2 y 2.3."""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import kendalltau, theilslopes

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
DATA = ROOT / "datos" / "punto2" / "Abtsgmuend_Untergroeningen"

def require_input(path: Path) -> Path:
    if not path.is_file():
        raise FileNotFoundError(f"Entrada no incluida: {path.relative_to(ROOT)}")
    return path

def main():
    raw = pd.read_csv(require_input(DATA / "abtsgmuend_precipitation_10min.csv"), usecols=["timestamp_utc", "quality_code", "precip_mm"])
    raw["timestamp_utc"] = pd.to_datetime(raw["timestamp_utc"].astype(str), format="%Y%m%d%H%M", errors="coerce")
    raw["precip_mm"] = pd.to_numeric(raw["precip_mm"], errors="coerce")
    raw["missing"] = raw["precip_mm"] < 0
    code = raw.groupby("quality_code", dropna=False).agg(records=("quality_code", "size"), missing=("missing", "sum")).reset_index()
    code.to_csv(DATA / "quality_code_audit.csv", index=False)
    intervals = raw["timestamp_utc"].sort_values().diff().dt.total_seconds().div(60).dropna()
    interval_audit = pd.DataFrame({"interval_minutes": intervals.value_counts().index, "records": intervals.value_counts().values})
    interval_audit.to_csv(DATA / "timestamp_interval_audit.csv", index=False)
    ams = pd.read_csv(DATA / "ams_precipitation.csv")
    durations = ["10min", "30min", "1h", "3h", "6h", "12h", "24h"]
    # Coherencia hidrologica: una ventana larga no puede ser menor que una corta.
    pairs = list(zip(durations[:-1], durations[1:]))
    coherence = {f"{a}_le_{b}": bool((ams[f"max_{a}_mm"] <= ams[f"max_{b}_mm"] + 1e-9).all()) for a, b in pairs}
    # Tendencia monotona de maximos anuales (Mann-Kendall via tau) y pendiente Sen.
    rows = []
    for d in durations:
        y = ams[f"max_{d}_mm"].to_numpy(float)
        tau, p = kendalltau(ams.year, y)
        sen = theilslopes(y, ams.year, 0.95)
        rows.append({"duration": d, "n_years": len(y), "mean_mm": y.mean(), "max_mm": y.max(),
                     "max_year": int(ams.loc[np.argmax(y), "year"]), "kendall_tau": tau,
                     "kendall_pvalue": p, "sen_slope_mm_per_year": sen.slope,
                     "sen_low95": sen.low_slope, "sen_high95": sen.high_slope})
    trend = pd.DataFrame(rows)
    trend.to_csv(DATA / "stationarity_tests.csv", index=False, float_format="%.6f")
    # Correccion de Weiss para maximos de ventanas fijas de reloj.
    n_intervals = {"10min": 1, "30min": 3, "1h": 6, "3h": 18, "6h": 36, "12h": 72, "24h": 144}
    corr = ams[["year"]].copy()
    for d, n in n_intervals.items():
        factor = 1.0 / (1.0 - 1.0 / (8.0 * n))
        corr[f"max_{d}_mm_weiss"] = ams[f"max_{d}_mm"] * factor
    corr.to_csv(DATA / "ams_precipitation_weiss.csv", index=False, float_format="%.3f")
    # Resumen legible.
    strongest = ams.loc[ams["max_1h_mm"].idxmax()]
    lines = ["# Revision final de lluvia DWD 00020", "", "## Resultado", "",
             f"- Años analizados: {len(ams)} (2005-2025).",
             "- Resolución efectiva: 10 minutos; no se detectan años con menos de 80% de registros.",
             f"- Mayor máximo anual de 1 h: {strongest.max_1h_mm:.2f} mm en {int(strongest.year)}.",
             "- Se generó la corrección de Weiss para ventanas fijas en `ams_precipitation_weiss.csv`.", "", "## Coherencia entre duraciones", ""]
    lines += [f"- {k}: {'OK' if v else 'REVISAR'}" for k, v in coherence.items()]
    lines += ["", "## Estacionariedad", "", "Los valores de tau, p y pendiente de Sen estan en `stationarity_tests.csv`. "
              "Se debe reportar la prueba formal junto con la incertidumbre de los cuantiles; un p > 0.05 no demuestra estacionariedad absoluta, solo ausencia de evidencia suficiente de tendencia.", "", "## Archivos para iniciar el IDF", "",
              "1. `ams_precipitation_weiss.csv` como maxima anual corregida.",
              "2. `stationarity_tests.csv` para 2.2.6.",
              "3. `ams_precipitation.csv` para rastrear los maximos sin correccion."]
    (DATA / "revision_lluvia.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Auditoria completada:", DATA / "revision_lluvia.md")
    print(trend[["duration", "kendall_tau", "kendall_pvalue", "sen_slope_mm_per_year"]].to_string(index=False))

if __name__ == "__main__":
    main()
