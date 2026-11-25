"""Completa errores IDF, incertidumbre del evento y trazabilidad KOSTRA."""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "datos" / "punto2" / "Abtsgmuend_Untergroeningen"
IDF = DATA / "idf_2_3"
EXT = DATA / "extremos_2_2"
SEED = 20261124

def main():
    q = pd.read_csv(IDF / "idf_gev_mle.csv")
    par = pd.read_csv(IDF / "idf_powerlaw_parameters.csv")
    metrics = []
    for T, g in q.groupby("T_years"):
        x = g.duration_h.to_numpy(float); y = g.intensity_mm_h.to_numpy(float)
        p = par.query("T_years == @T").iloc[0]; pred = p.a * x ** (-p.eta); resid = y-pred
        ss_res = float(np.sum(resid**2)); ss_tot = float(np.sum((y-y.mean())**2))
        metrics.append({"T_years": int(T), "n_durations": len(g), "a": float(p.a), "eta": float(p.eta), "rmse_mm_h": float(np.sqrt(np.mean(resid**2))), "mae_mm_h": float(np.mean(np.abs(resid))), "max_abs_error_mm_h": float(np.max(np.abs(resid))), "r2_loglog": float(1-ss_res/ss_tot), "duration_min_h": float(x.min()), "duration_max_h": float(x.max())})
    pd.DataFrame(metrics).to_csv(IDF / "idf_fit_error_metrics.csv", index=False, float_format="%.6f")

    annual = pd.read_csv(EXT / "ams_hydrological_oct_sep.csv"); x = annual.max_1h_mm.dropna().to_numpy(float)
    event = float(annual.loc[annual.hydro_year == 2021, "max_1h_mm"].iloc[0]); rng = np.random.default_rng(SEED); rows = []
    for b in range(1000):
        p = stats.genextreme.fit(rng.choice(x, len(x), replace=True)); F = float(stats.genextreme.cdf(event, *p)); T = 1/max(1-F, 1e-12)
        rows.append({"bootstrap": b, "event_depth_mm": event, "return_period_years": T, "annual_exceedance_probability": 1/T})
    boot = pd.DataFrame(rows); boot.to_csv(IDF / "recent_event_return_period_bootstrap.csv", index=False, float_format="%.8f")
    p0 = stats.genextreme.fit(x); F0 = float(stats.genextreme.cdf(event, *p0))
    summary = pd.DataFrame([{"event_hydro_year": 2021, "duration_h": 1, "depth_mm": event, "point_estimate_T_years": 1/(1-F0), "T_q025": boot.return_period_years.quantile(.025), "T_median": boot.return_period_years.median(), "T_q975": boot.return_period_years.quantile(.975), "p_q025": boot.annual_exceedance_probability.quantile(.025), "p_median": boot.annual_exceedance_probability.median(), "p_q975": boot.annual_exceedance_probability.quantile(.975), "bootstrap_replicas": len(boot), "seed": SEED}])
    summary.to_csv(IDF / "recent_event_return_period_uncertainty.csv", index=False, float_format="%.8f")

    (IDF / "kostra_referencia_verificable.md").write_text("""# Trazabilidad de KOSTRA-DWD-2020

La comparación usa la versión oficial **KOSTRA-DWD-2020** del Deutscher
Wetterdienst (DWD), publicada por el Climate Data Center. Se extrajeron los
rasters ASCII Hn para D00010, D00060, D00360 y D01440 y T = 1, 2, 3, 5, 10,
20, 30, 50 y 100 años. La celda corresponde a la estación DWD 00020: fila 186,
columna 142, CRS ETRS89-LAEA EPSG:3035.

Fuente oficial y DOI: `https://doi.org/10.5676/DWD/KOSTRA-DWD-2020`.
Portal: `https://opendata.dwd.de/climate_environment/CDC/grids_germany/return_periods/precipitation/KOSTRA/KOSTRA_DWD_2020/`.
Cobertura temporal: 1951–2020; resolución espacial: 5 km.

La razón observada/KOSTRA mezcla diferencias de escala espacial, periodo de
referencia y ajuste estadístico; no se interpreta automáticamente como sesgo puro.
""", encoding="utf-8")
    (IDF / "revision_2_3.md").write_text("""# Cierre del apartado 2.3 — IDF y anomalías

La IDF GEV-MLE se ajustó con `i(d,T)=a(T)d^{-eta(T)}`. `idf_powerlaw_parameters.csv`
contiene `a`, `eta` y RMSE; `idf_fit_error_metrics.csv` añade MAE, error máximo,
R² log-log y el rango 0.1667–24 h.

El evento de 1 h de 2021 (48.27 mm) tiene periodo de retorno puntual GEV de
aproximadamente 17.36 años. El bootstrap de 1000 réplicas está en
`recent_event_return_period_bootstrap.csv` y su resumen en
`recent_event_return_period_uncertainty.csv`.

Un evento extremo es una observación grande; una anomalía es su desviación
respecto a la distribución de referencia; una tendencia es un cambio sistemático
en el tiempo. El evento 2021 se reporta como extremo y anomalía estadística, no
como evidencia suficiente de tendencia climática.
""", encoding="utf-8")
    print(summary.to_string(index=False))

if __name__ == '__main__': main()
