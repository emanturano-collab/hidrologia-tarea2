"""Integra productos ya calculados de 1.1.b sin repetir ningún cálculo."""
from __future__ import annotations

from pathlib import Path
import textwrap
import pandas as pd

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
TASK = ROOT
TABLES = TASK / "productos" / "punto1" / "1_1_demanda_atmosferica" / "tablas"
DATA = TASK / "datos" / "punto1" / "procesados" / "1_1_b_pruebas_referencia"
ANNEX = TASK / "anexos" / "punto1" / "1_1_b_pruebas_referencia"

def main() -> None:
    pisco = pd.read_csv(TABLES / "1_1b_metricas_pet_piscoeopm_vs_eto.csv").iloc[0]
    terra = pd.read_csv(TABLES / "1_1b_metricas_terraclimate_y_productos_demanda.csv")
    physical = pd.read_csv(TABLES / "1_1b_comprobacion_fisica_resumen.csv").iloc[0]
    station_daily = pd.read_csv(DATA / "noaa_ghcnh_pei0000sphi_meteorologia_y_eto_diaria.csv", parse_dates=["date"])
    station_monthly = pd.read_csv(DATA / "noaa_ghcnh_pei0000sphi_eto_mensual_completo.csv", parse_dates=["month"])
    request = pd.read_csv(ANNEX / "solicitud_era5land_puntual_estacion_pei0000sphi.csv").iloc[0]
    station_era = pd.read_csv(TABLES / "1_1b_metricas_estacion_noaa_vs_era5land_chiclayo.csv")
    station_era_primary = station_era.query("comparison == 'NOAA kRs=0.19 - ERA5 kRs=0.19' and resolution == 'daily'").iloc[0]
    station_era_direct = station_era.query("comparison == 'NOAA kRs=0.19 - ERA5 ssrd' and resolution == 'daily'").iloc[0]

    valid_station = station_daily.loc[station_daily.valid_fao56]
    checklist = pd.DataFrame([
        {"requirement": "Producto independiente de demanda", "status": "COMPLETADO",
         "evidence": "PISCOeo_pm y TerraClimate v1.1 ponderado; no se cuentan como dos categorías."},
        {"requirement": "Comprobación física P-Q", "status": "COMPLETADO",
         "evidence": f"{physical.n_complete_years} años completos; P-Q no se usó como ETo."},
        {"requirement": "Estación meteorológica: inventario y metadatos", "status": "COMPLETADO",
         "evidence": "NOAA GHCNh PEI0000SPHI, Chiclayo; PSV y SHA-256 auditados."},
        {"requirement": "Estación meteorológica: ETo FAO-56", "status": "COMPLETADO CON SUPUESTOS DECLARADOS",
         "evidence": f"{len(valid_station)} días válidos y {len(station_monthly)} meses completos; Rs ec.50 y altura de viento con sensibilidad."},
        {"requirement": "Comparación puntual estación - ERA5-Land", "status": "COMPLETADO",
         "evidence": f"Celda -6.8, -79.8 validada; {int(station_era_primary.n)} días y {len(station_monthly)} meses comunes."},
        {"requirement": "Segunda categoría de prueba", "status": "COMPLETADO CON LIMITACIÓN ESPACIAL",
         "evidence": "Prueba local costera Chiclayo-ERA5; no valida por sí sola el relieve andino de Racarumi."},
        {"requirement": "ETo representativa final de Racarumi", "status": "PENDIENTE",
         "evidence": "La ETo de cuenca sigue preliminar: 90.1264 % de cobertura espacial ERA5-Land."},
    ])
    checklist.to_csv(TABLES / "1_1b_estado_cumplimiento_preliminar.csv", index=False)
    checklist.to_csv(TABLES / "1_1b_estado_cumplimiento_final_preliminar.csv", index=False)
    existing_metrics = pd.read_csv(TABLES / "1_1b_metricas_consolidadas_preliminares.csv")
    existing_metrics = existing_metrics.loc[existing_metrics["comparison"] != "ETo estación NOAA PEI0000SPHI - ERA5-Land puntual"]
    pd.concat([existing_metrics, station_era], ignore_index=True, sort=False).to_csv(
        TABLES / "1_1b_metricas_consolidadas_finales_preliminares.csv", index=False
    )

    summary = f"""# Resumen integral del apartado 1.1.b - versión preliminar

## Datos y pruebas ejecutadas

La comparación CAMELS-PE/PISCOeo_pm frente a ETo FAO-56 preliminar cubrió
{int(pisco.n_months)} meses (1981-2016): Pearson={pisco.pearson_r:.4f},
Spearman={pisco.spearman_rho:.4f}, sesgo PET-ETo={pisco.bias_pet_minus_eto_mm_month:.3f} mm/mes,
MAE={pisco.mae_mm_month:.3f} y RMSE={pisco.rmse_mm_month:.3f}.

TerraClimate v1.1, ponderado con 219 celdas por área de intersección, se comparó
con ETo ERA5-Land en 511 meses: Pearson={terra.iloc[0].pearson_r:.4f},
Spearman={terra.iloc[0].spearman_rho:.4f}, sesgo={terra.iloc[0].bias_left_minus_right_mm_month:.3f}
mm/mes, MAE={terra.iloc[0].mae_mm_month:.3f} y RMSE={terra.iloc[0].rmse_mm_month:.3f}.
PISCOeo_pm y TerraClimate son contrastes de la misma categoría (productos de
demanda); TerraClimate v1.1 utiliza anomalías ERA5 y no constituye independencia
total respecto a ERA5-Land.

El balance físico usó {int(physical.n_complete_years)} años completos:
P={physical.mean_annual_p_mm:.2f}, Q={physical.mean_annual_q_mm:.2f},
P-Q={physical.mean_annual_p_minus_q_mm:.2f} y ETo preliminar=
{physical.mean_annual_eto_preliminar_mm:.2f} mm/año. P-Q aproxima ET real bajo
supuestos de balance y no se interpretó como ETo.

## Estación NOAA PEI0000SPHI

Se validaron 13 PSV NOAA GHCNh (2010-2022), con {len(valid_station)} días que
cumplen al menos 18 horas de temperatura, punto de rocío y viento, y
{len(station_monthly)} meses completos. La ETo FAO-56 condicional de Chiclayo
usa Rs por ecuación 50 (kRs=0.19, sensibilidad kRs=0.16) y presión de ecuación
7 cuando la presión observada no tiene cobertura diaria suficiente. La altura
instrumental de viento no está en los PSV: se declara un escenario convencional
10 m a 2 m y otro sin ajuste para sensibilidad.

La estación costera (29.6 m) no representa automáticamente Racarumi, cuya ETo
preliminar ponderada corresponde a una elevación media aproximada de 2343 m y
relieve andino. La celda existente P1 queda a {request.nearest_existing_distance_km:.1f} km;
por tanto no se comparó la estación con el promedio de cuenca ni con P1.

## Prueba local estación - ERA5-Land

La celda ERA5-Land retornada fue -6.8, -79.8, a corta distancia de la estación,
y se comparó durante {int(station_era_primary.n)} días y {len(station_monthly)} meses completos.
Con radiación propia ERA5 (`ssrd`): Pearson={station_era_direct.pearson_r:.4f},
Spearman={station_era_direct.spearman_rho:.4f}, sesgo NOAA-ERA5=
{station_era_direct.bias_station_minus_era5_mm:.3f} mm/día, MAE={station_era_direct.mae_mm:.3f}
y RMSE={station_era_direct.rmse_mm:.3f}. Con radiación Eq.50 kRs=0.19 en ambas:
Pearson={station_era_primary.pearson_r:.4f}, Spearman={station_era_primary.spearman_rho:.4f},
sesgo={station_era_primary.bias_station_minus_era5_mm:.3f} mm/día, MAE=
{station_era_primary.mae_mm:.3f} y RMSE={station_era_primary.rmse_mm:.3f}.

## Estado

Se concluye **1.1.b en versión preliminar**: se completaron dos categorías de
prueba exigidas (producto de demanda y estación meteorológica) y la comprobación
física P-Q. La estación costera externa evalúa localmente ERA5-Land; no demuestra
exactitud sobre toda Racarumi. La ETo representativa de cuenca no es definitiva:
sigue pendiente el 9.8736 % de cobertura espacial ERA5-Land.
"""
    (ANNEX / "resumen_integral_1_1b_preliminar.md").write_text(textwrap.dedent(summary), encoding="utf-8")
    (ANNEX / "resumen_integral_final_1_1b_preliminar.md").write_text(textwrap.dedent(summary), encoding="utf-8")
    print(checklist[["requirement", "status"]].to_string(index=False))

if __name__ == "__main__":
    main()
