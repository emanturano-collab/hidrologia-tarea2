"""1.1.d: calibracion de Hargreaves-Samani contra FAO-56 y Makkink original.

Sigue el arbol de decision de la seccion 7 de las notas del curso (Hoyos, 2026): con
solo temperaturas maxima y minima, Hargreaves-Samani "idealmente calibrado con una
estacion completa cercana". Aqui la referencia completa es la ETo FAO-56 de la cuenca.

- Calibra el coeficiente 0,0023 con el cociente de sumas en 1981-2001 y lo valida en
  2002-2022 (muestra dividida); luego lo calibra con todo el periodo.
- Explica el sesgo de Hargreaves por mes con el termino aerodinamico de FAO-56.
- Calcula Makkink en su forma original (0,61 D/(D+g) Rs/l - 0,12 mm/d), ademas de la
  variante de de Bruin (1987, k = 0,65 sin constante) que usa pyet.makkink.

Entrada: datos/punto1/procesados/1_1_d_explicacion_fisica/1_1d_componentes_y_alpha_mensuales_preliminar_90pct.csv
Salidas: productos/punto1/1_1_demanda_atmosferica/tablas/1_1d_calibracion_hargreaves*.csv

Ejecucion: python calibrar_hargreaves_1_1d.py (desde cualquier carpeta)
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[4]
ENT = ROOT / "datos" / "punto1" / "procesados" / "1_1_d_explicacion_fisica" / "1_1d_componentes_y_alpha_mensuales_preliminar_90pct.csv"
TAB = ROOT / "productos" / "punto1" / "1_1_demanda_atmosferica" / "tablas"

d = pd.read_csv(ENT, parse_dates=["date"])
d["mes"] = d["date"].dt.month
d["dias"] = d["date"].dt.days_in_month
fao, hs = d["fao56"], d["hargreaves_samani_1985"]
# Makkink original a partir de la variante de de Bruin: ambas comparten D/(D+g) Rs/l dia a dia,
# por lo que la suma mensual es exactamente 0,61/0,65 * de Bruin - 0,12 * dias.
d["makkink_original_1957"] = 0.61 / 0.65 * d["makkink_1957"] - 0.12 * d["dias"]


def metricas(sim, obs):
    e = sim - obs
    return {"sesgo_mm_mes": e.mean(), "sesgo_pct": 100 * e.mean() / obs.mean(), "MAE_mm_mes": e.abs().mean(),
            "RMSE_mm_mes": np.sqrt((e ** 2).mean()), "r": np.corrcoef(sim, obs)[0, 1]}


cal = d["date"].dt.year <= 2001
val = ~cal
k_cal = 0.0023 * fao[cal].sum() / hs[cal].sum()
k_tot = 0.0023 * fao.sum() / hs.sum()
filas = [
    {"caso": "Hargreaves original (0,0023), 1981-2022", "coeficiente": 0.0023, **metricas(hs, fao)},
    {"caso": "Hargreaves original, validacion 2002-2022", "coeficiente": 0.0023, **metricas(hs[val], fao[val])},
    {"caso": "Hargreaves calibrado 1981-2001, validacion 2002-2022", "coeficiente": k_cal, **metricas(hs[val] * k_cal / 0.0023, fao[val])},
    {"caso": "Hargreaves calibrado 1981-2022", "coeficiente": k_tot, **metricas(hs * k_tot / 0.0023, fao)},
    {"caso": "Makkink de Bruin (k = 0,65), 1981-2022", "coeficiente": 0.65, **metricas(d["makkink_1957"], fao)},
    {"caso": "Makkink original (0,61; -0,12), 1981-2022", "coeficiente": 0.61, **metricas(d["makkink_original_1957"], fao)},
]
res = pd.DataFrame(filas)
res.to_csv(TAB / "1_1d_calibracion_hargreaves.csv", index=False, float_format="%.6g")

# Sesgo por mes calendario antes y despues de calibrar, y su relacion con el termino aerodinamico
d["sesgo_hs"] = hs - fao
d["sesgo_hs_cal"] = hs * k_tot / 0.0023 - fao
pm = d.groupby("mes").agg(sesgo_original_mm=("sesgo_hs", "mean"), sesgo_calibrado_mm=("sesgo_hs_cal", "mean"),
                          fraccion_aerodinamica_pct=("fraction_aerodynamic_pct", "mean"),
                          vpd_kpa=("vpd_kpa_mean", "mean"), u2_ms=("u2_ms_mean", "mean"))
pm.to_csv(TAB / "1_1d_calibracion_hargreaves_por_mes.csv", float_format="%.4f")
rho_aero = stats.spearmanr(d["sesgo_hs"], d["fraction_aerodynamic_pct"])
rho_vpd = stats.spearmanr(d["sesgo_hs"], d["vpd_kpa_mean"])
pd.DataFrame([{"variable": "fraccion_aerodinamica_pct", "spearman_rho": rho_aero.statistic, "p": rho_aero.pvalue},
              {"variable": "vpd_kpa", "spearman_rho": rho_vpd.statistic, "p": rho_vpd.pvalue}]
             ).to_csv(TAB / "1_1d_calibracion_hargreaves_correlaciones.csv", index=False, float_format="%.5g")
print(res.round(3).to_string(index=False))
print(pm.round(2).to_string())
print("Spearman sesgo HS vs fraccion aerodinamica:", rho_aero, "\nvs VPD:", rho_vpd)
