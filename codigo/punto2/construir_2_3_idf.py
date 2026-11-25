"""Construye IDF preliminar a partir de GEV-MLE y bootstrap."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
DATA = ROOT / "datos" / "punto2" / "Abtsgmuend_Untergroeningen"
INP = DATA / "extremos_2_2"
OUT = DATA / "idf_2_3"
OUT.mkdir(exist_ok=True)
DUR_H = {"10min": 1/6, "30min": .5, "1h": 1, "3h": 3, "6h": 6, "12h": 12, "24h": 24}
TS = [2, 5, 10, 25, 50, 100]

def main():
    q = pd.read_csv(INP / "quantiles_3methods.csv")
    q = q[(q.distribution == "gev") & (q.method == "mle")].copy()
    q["duration_h"] = q.duration.map(DUR_H)
    q.to_csv(OUT / "idf_gev_mle.csv", index=False, float_format="%.5f")
    # Ajuste analitico i = a(T) d^-eta(T) en log-log.
    fits = []
    curves = []
    for T in TS:
        g = q[q.T_years == T]
        slope, intercept = np.polyfit(np.log(g.duration_h), np.log(g.intensity_mm_h), 1)
        eta = -slope; a = np.exp(intercept)
        pred = a * g.duration_h ** (-eta)
        rmse = float(np.sqrt(np.mean((g.intensity_mm_h-pred)**2)))
        fits.append({"T_years": T, "a": a, "eta": eta, "rmse_mm_h": rmse})
        for d in np.geomspace(1/6, 24, 100): curves.append({"T_years": T, "duration_h": d, "intensity_mm_h": a*d**(-eta)})
    pd.DataFrame(fits).to_csv(OUT / "idf_powerlaw_parameters.csv", index=False, float_format="%.6f")
    pd.DataFrame(curves).to_csv(OUT / "idf_powerlaw_curves.csv", index=False, float_format="%.5f")
    # Evento reciente documentado: maximo anual 1h de 2021.
    annual = pd.read_csv(INP / "ams_hydrological_oct_sep.csv")
    x = annual.max_1h_mm.dropna().to_numpy(float)
    pars = stats.genextreme.fit(x)
    event = float(annual.loc[annual.hydro_year == 2021, "max_1h_mm"].iloc[0])
    F = float(stats.genextreme.cdf(event, *pars)); T = 1/(1-F)
    row = pd.DataFrame([{"event_hydro_year": 2021, "duration_h": 1, "depth_mm": event,
                         "return_period_years_gev_mle": T, "annual_exceedance_probability": 1/T}])
    row.to_csv(OUT / "recent_event_return_period.csv", index=False, float_format="%.6f")
    # Figura IDF.
    plt.figure(figsize=(8,5))
    for T in TS:
        g=q[q.T_years==T].sort_values("duration_h")
        plt.loglog(g.duration_h, g.intensity_mm_h, 'o-', label=f'T={T} años')
    plt.xlabel('Duración (h)'); plt.ylabel('Intensidad (mm/h)'); plt.grid(True, which='both', alpha=.3); plt.legend(); plt.tight_layout()
    plt.savefig(OUT / "idf_gev_mle.png", dpi=180); plt.close()
    (OUT / "revision_2_3.md").write_text(
        "# Apartado 2.3 — IDF preliminar\n\n"
        "Se seleccionó GEV por máxima verosimilitud como modelo provisional: obtuvo "
        "el mejor promedio de las pruebas KS y Cramer–von Mises entre las combinaciones evaluadas. "
        "La selección definitiva debe considerar también L-momentos, bootstrap y la comparación KOSTRA.\n\n"
        "Archivos: `idf_gev_mle.csv`, `idf_powerlaw_parameters.csv`, `idf_powerlaw_curves.csv`, "
        "`recent_event_return_period.csv` e `idf_gev_mle.png`.\n", encoding="utf-8")
    print(f"IDF creada; evento 2021 T preliminar={T:.2f} años")

if __name__ == "__main__": main()
