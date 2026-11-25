"""Build QA tables, figures and a technical summary from the 90.13 % preliminary run."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
TASK = ROOT
OUT = TASK / "datos" / "punto1" / "procesados" / "1_1_a_fao56_preliminar_90pct"
META = TASK / "datos" / "punto1" / "metadatos"
TABLES = TASK / "productos" / "punto1" / "1_1_demanda_atmosferica" / "tablas"
FIGURES = TASK / "productos" / "punto1" / "1_1_demanda_atmosferica" / "figuras"
GRID = TABLES / "era5land_33_celdas_pesos_y_elevacion.csv"


def main() -> None:
    daily = pd.read_csv(OUT / "fao56_eto_diaria_preliminar_90pct.csv", parse_dates=["date"])
    monthly = pd.read_csv(OUT / "fao56_eto_mensual_preliminar_90pct.csv", parse_dates=["month"])
    coverage = pd.read_csv(META / "fao56_preliminar_90pct_cobertura_y_limitacion.csv").iloc[0]
    grid = pd.read_csv(GRID)
    FIGURES.mkdir(parents=True, exist_ok=True)

    # Independent algebraic reconstruction of FAO-56 equation 6 from saved inputs.
    expected = (
        0.408 * daily["delta_kpa_c"] * (daily["rn_mj_m2_d"] - daily["g_mj_m2_d"])
        + daily["gamma_kpa_c"] * (900.0 / (daily["tmean_c"] + 273.0)) * daily["u2_ms"]
        * (daily["es_kpa"] - daily["ea_kpa"])
    ) / (daily["delta_kpa_c"] + daily["gamma_kpa_c"] * (1 + 0.34 * daily["u2_ms"]))
    comparable = monthly.dropna(subset=["eto_monthly_direct_mm", "difference_direct_minus_daily_mm"]).copy()
    climatology = monthly.assign(calendar_month=monthly["month"].dt.month).groupby("calendar_month", as_index=False).agg(
        eto_sum_daily_mean_mm=("eto_from_daily_mm", "mean"),
        eto_direct_mean_mm=("eto_monthly_direct_mm", "mean"),
        difference_mean_mm=("difference_direct_minus_daily_mm", "mean"),
    )
    climatology.to_csv(TABLES / "fao56_preliminar_90pct_climatologia_mensual.csv", index=False)

    quality = pd.DataFrame([{
        "scope": "PRELIMINAR_NO_FINAL",
        "coverage_weight": float(coverage["weight_covered"]),
        "pending_weight": float(coverage["weight_pending"]),
        "daily_records": len(daily),
        "daily_start": daily["date"].min().date().isoformat(),
        "daily_end": daily["date"].max().date().isoformat(),
        "all_days_have_24_hourly_records": bool((daily["n_hourly_records"] == 24).all()),
        "all_eto_finite": bool(np.isfinite(daily["eto_fao56_mm_d"]).all()),
        "all_eto_nonnegative": bool((daily["eto_fao56_mm_d"] >= 0).all()),
        "max_equation_reconstruction_abs_mm_d": float(np.max(np.abs(expected - daily["eto_fao56_mm_d"]))),
        "months_compared": len(comparable),
        "max_monthly_method_abs_difference_mm": float(comparable["difference_direct_minus_daily_mm"].abs().max()),
        "month_max_difference": comparable.loc[comparable["difference_direct_minus_daily_mm"].abs().idxmax(), "month"].strftime("%Y-%m"),
    }])
    quality.to_csv(TABLES / "fao56_preliminar_90pct_control_calidad.csv", index=False)

    # Time series and aggregation discrepancy.
    fig, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=True, height_ratios=[2, 1])
    axes[0].plot(monthly["month"], monthly["eto_from_daily_mm"], lw=0.8, label="Suma de ETo diaria")
    axes[0].plot(monthly["month"], monthly["eto_monthly_direct_mm"], lw=0.8, label="FAO-56 con medias mensuales")
    axes[0].set_ylabel("ETo (mm/mes)")
    axes[0].set_title("Racarumi: ETo preliminar, cobertura espacial 90.13 %")
    axes[0].legend()
    axes[0].grid(alpha=0.25)
    axes[1].axhline(0, color="black", lw=0.7)
    axes[1].plot(monthly["month"], monthly["difference_direct_minus_daily_mm"], lw=0.8, color="#b44")
    axes[1].set_ylabel("Directa − suma\n(mm/mes)")
    axes[1].set_xlabel("Mes")
    axes[1].grid(alpha=0.25)
    fig.text(0.5, 0.01, "Producto preliminar: falta 9.87 % del peso de cuenca; no usar como ETo final.", ha="center", fontsize=9)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(FIGURES / "fao56_preliminar_90pct_serie_y_agregacion_mensual.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    # Climatology and the non-linearity signal.
    fig, axis = plt.subplots(figsize=(10, 5))
    axis.plot(climatology["calendar_month"], climatology["eto_sum_daily_mean_mm"], marker="o", label="Suma diaria")
    axis.plot(climatology["calendar_month"], climatology["eto_direct_mean_mm"], marker="o", label="Cálculo mensual directo")
    axis.set_xticks(range(1, 13))
    axis.set_xlabel("Mes calendario")
    axis.set_ylabel("ETo media (mm/mes)")
    axis.set_title("Climatología ETo preliminar — Racarumi (90.13 % de cobertura)")
    axis.grid(alpha=0.25)
    axis.legend()
    fig.tight_layout()
    fig.savefig(FIGURES / "fao56_preliminar_90pct_climatologia_mensual.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    # Spatial selection inventory, not a basin polygon map.
    selected = set(daily["point"].dropna().unique())
    grid["used_preliminary"] = grid["cell_id"].isin(selected)
    fig, axis = plt.subplots(figsize=(8, 7))
    for used, group in grid.groupby("used_preliminary"):
        axis.scatter(group["longitude"], group["latitude"], s=group["spatial_weight"] * 9000,
                     c="#1677b8" if used else "#c5c5c5", alpha=0.75,
                     label="Usada (20 celdas)" if used else "Pendiente (13 celdas)")
    axis.set_xlabel("Longitud (°)")
    axis.set_ylabel("Latitud (°)")
    axis.set_title("Cobertura de celdas ERA5-Land para ETo preliminar")
    axis.legend()
    axis.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "fao56_preliminar_90pct_cobertura_espacial.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    max_row = comparable.loc[comparable["difference_direct_minus_daily_mm"].abs().idxmax()]
    text = f"""# Resultados técnicos — ETo FAO-56 preliminar (90.13 %)

**Alcance.** Esta estimación usa 20 de las 33 celdas ERA5-Land y cubre {float(coverage['weight_covered']):.4%} del peso espacial. El {float(coverage['weight_pending']):.4%} restante sigue sin datos horarios, por lo que no es la ETo definitiva de Racarumi.

## Respuestas de 1.1.a

1. **Temperatura.** T2m se convirtió de K a °C y se promedió espacialmente por hora antes de obtener Tmin, Tmax y Tmedia diarios. El cálculo usa el promedio de e°(Tmax) y e°(Tmin) para es.
2. **Humedad.** La presión real de vapor se calculó horario a horario como e°(Td), con Td de ERA5-Land, y luego se promedió a día.
3. **Viento.** La magnitud sqrt(u10²+v10²) se formó por celda y hora antes de la ponderación espacial; la media diaria se transformó a 2 m con FAO-56.
4. **Radiación.** ssrd se verificó como radiación solar, se sumó cada día y se convirtió de J m⁻² a MJ m⁻² d⁻¹. Rn es la del pasto de referencia (albedo 0.23), no la radiación neta de la superficie real.
5. **Calor del suelo y presión.** Se aplicó G≈0 a diario; el cálculo mensual directo usó Gi=0.07(Ti+1−Ti−1). Gamma se obtuvo de la presión espacialmente ponderada.
6. **ETo y agregación.** Se calcularon {len(daily):,} días, desde {daily['date'].min().date()} hasta {daily['date'].max().date()}. La mayor diferencia absoluta entre la suma diaria y el cálculo mensual directo fue {abs(float(max_row['difference_direct_minus_daily_mm'])):.3f} mm en {max_row['month'].strftime('%Y-%m')}; se conserva como señal del error por promediar antes de una ecuación no lineal.

## Control de calidad

- Todos los días retenidos tienen 24 horas; ETo es finita y no negativa.
- La reconstrucción independiente de la ecuación FAO-56 difiere como máximo {float(quality.iloc[0]['max_equation_reconstruction_abs_mm_d']):.3e} mm/día.
- Quedan 13 celdas y {float(coverage['weight_pending']):.4%} del peso para completar la ponderación de Tarea 1.
"""
    (TABLES / "fao56_preliminar_90pct_resumen_tecnico.md").write_text(text, encoding="utf-8")
    print(json.dumps({"daily_rows": len(daily), "monthly_rows": len(monthly), "coverage": float(coverage["weight_covered"]), "max_monthly_difference_mm": float(quality.iloc[0]["max_monthly_method_abs_difference_mm"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
