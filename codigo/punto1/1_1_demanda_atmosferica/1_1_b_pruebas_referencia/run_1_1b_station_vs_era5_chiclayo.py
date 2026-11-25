"""Compara la ETo condicional NOAA Chiclayo con ERA5-Land puntual.

La celda se usa únicamente para una prueba local del reanálisis. No interviene
en la ponderación ni en la ETo de Racarumi.
"""
from __future__ import annotations

from io import BytesIO
import hashlib
from pathlib import Path
import sys
import zipfile

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_1_1b_noaa_ghcnh_station as station  # noqa: E402
import importlib.util  # noqa: E402

CORE_PATH = ROOT / "codigo" / "punto1" / "1_1_demanda_atmosferica" / "1_1_a_fao56" / "run_fao56_1_1a.py"
CORE_SPEC = importlib.util.spec_from_file_location("fao56_core", CORE_PATH)
if CORE_SPEC is None or CORE_SPEC.loader is None:
    raise ImportError("No se pudo cargar el núcleo FAO-56 de 1.1.a")
core = importlib.util.module_from_spec(CORE_SPEC)
CORE_SPEC.loader.exec_module(core)

ZIP = ROOT / "datos" / "punto1" / "originales" / "era5land_chiclayo" / "ERA5_Land_Chiclayo_SPHI_20100101_20230101.zip"
STATION_DAILY = ROOT / "datos" / "punto1" / "procesados" / "1_1_b_pruebas_referencia" / "noaa_ghcnh_pei0000sphi_meteorologia_y_eto_diaria.csv"
STATION_MONTHLY = ROOT / "datos" / "punto1" / "procesados" / "1_1_b_pruebas_referencia" / "noaa_ghcnh_pei0000sphi_eto_mensual_completo.csv"
DATA = ROOT / "datos" / "punto1" / "procesados" / "1_1_b_pruebas_referencia"
META = ROOT / "datos" / "punto1" / "metadatos"
TABLES = ROOT / "productos" / "punto1" / "1_1_demanda_atmosferica" / "tablas"
FIGURES = ROOT / "productos" / "punto1" / "1_1_demanda_atmosferica" / "figuras"
ANNEX = ROOT / "anexos" / "punto1" / "1_1_b_pruebas_referencia"

LAT, LON, ELEVATION = -6.8, -79.8, 29.6
KRS_PRIMARY, KRS_SENS = 0.19, 0.16
REQUIRED = {"t2m", "d2m", "sp", "ssrd", "u10", "v10"}


def sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest().upper()


def metrics(left: pd.Series, right: pd.Series, label: str, resolution: str) -> dict[str, object]:
    d = left - right
    return {"comparison": label, "resolution": resolution, "n": int(len(d)),
            "pearson_r": float(left.corr(right)),
            "spearman_rho": float(left.rank().corr(right.rank())),
            "bias_station_minus_era5_mm": float(d.mean()), "mae_mm": float(d.abs().mean()),
            "rmse_mm": float(np.sqrt((d**2).mean()))}


def full_months(daily: pd.DataFrame, value: str) -> pd.DataFrame:
    copied = daily[["date", value]].copy(); copied["month"] = copied["date"].dt.to_period("M")
    rows = []
    for month, part in copied.groupby("month", sort=True):
        days = month.days_in_month
        if len(part) == days and part.date.nunique() == days and part[value].notna().sum() == days:
            rows.append({"month": month.to_timestamp(), "days_in_month": days, value.replace("_mm_d", "_mm_month"): part[value].sum()})
    return pd.DataFrame(rows)


def savefig(fig: plt.Figure, name: str) -> None:
    for ext in ("png", "pdf"):
        fig.savefig(FIGURES / f"{name}.{ext}", dpi=220 if ext == "png" else None, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    for folder in (DATA, META, TABLES, FIGURES, ANNEX): folder.mkdir(parents=True, exist_ok=True)
    if not ZIP.is_file(): raise FileNotFoundError(ZIP)
    if not STATION_DAILY.is_file() or not STATION_MONTHLY.is_file(): raise FileNotFoundError("Faltan productos NOAA previos")
    series, variable_meta, file_meta = core.read_zip_netcdf(ZIP)
    if set(series) != REQUIRED: raise ValueError(f"Variables ERA5 inválidas: {sorted(series)}")
    coordinates = {(row["latitude"], row["longitude"]) for row in file_meta}
    if len(coordinates) != 1: raise ValueError("Coordenadas inconsistentes en los NetCDF")
    returned_lat, returned_lon = next(iter(coordinates))
    if not (np.isclose(returned_lat, LAT) and np.isclose(returned_lon, LON)):
        raise ValueError(f"Coordenada ERA5 retornada inesperada: {returned_lat}, {returned_lon}")
    if any(row["records"] != 113976 or row["nonhourly_intervals"] != 0 for row in file_meta):
        raise ValueError("Cobertura horaria ERA5 no válida")
    if any(row["missing_values"] != 0 for row in variable_meta):
        raise ValueError("ERA5 contiene valores faltantes")

    # Función validada de 1.1.a: conversiones, viento horario, ssrd y PM-FAO56.
    era_direct = core.fao56_daily("ERA5Land_Chiclayo", series, ELEVATION, LAT)
    era_direct = era_direct.rename(columns={"eto_fao56_mm_d": "eto_era5_ssrd_mm_d"})
    # Misma ecuación 50 usada en la estación: igualdad metodológica de radiación.
    era_indexed = era_direct.set_index("date").copy()
    era_indexed["wind_ms"] = era_indexed["wind10_ms"]
    era_indexed["eto_era5_krs019_mm_d"] = station.daily_fao56(era_indexed, KRS_PRIMARY, True)
    era_indexed["eto_era5_krs016_mm_d"] = station.daily_fao56(era_indexed, KRS_SENS, True)
    era_indexed["rs_era5_krs019_mj_m2_d"] = KRS_PRIMARY * np.sqrt((era_indexed["tmax_c"] - era_indexed["tmin_c"]).clip(lower=0)) * era_indexed["ra_mj_m2_d"]
    era_indexed["rs_era5_krs016_mj_m2_d"] = KRS_SENS * np.sqrt((era_indexed["tmax_c"] - era_indexed["tmin_c"]).clip(lower=0)) * era_indexed["ra_mj_m2_d"]
    era_indexed["ssrd_minus_krs019_mj_m2_d"] = era_indexed["rs_mj_m2_d"] - era_indexed["rs_era5_krs019_mj_m2_d"]
    if not np.isfinite(era_indexed[["eto_era5_ssrd_mm_d", "eto_era5_krs019_mm_d", "eto_era5_krs016_mm_d"]].to_numpy()).all():
        raise ValueError("ETo ERA5 no finita")
    era = era_indexed.reset_index()
    era.to_csv(DATA / "era5land_chiclayo_fao56_diaria.csv", index=False)

    station_daily = pd.read_csv(STATION_DAILY, parse_dates=["date"])
    station_daily = station_daily.loc[station_daily["valid_fao56"]].copy()
    merged = station_daily.merge(era[["date", "eto_era5_ssrd_mm_d", "eto_era5_krs019_mm_d", "eto_era5_krs016_mm_d", "rs_mj_m2_d", "rs_era5_krs019_mj_m2_d", "ssrd_minus_krs019_mj_m2_d"]], on="date", how="inner")
    required_days = len(station_daily)
    if len(merged) != required_days:
        raise ValueError(f"Fechas comunes incompletas: estación={required_days}, común={len(merged)}")
    merged["difference_station_minus_era5_ssrd_mm_d"] = merged["eto_fao56_krs019_u10to2_mm_d"] - merged["eto_era5_ssrd_mm_d"]
    merged["difference_station_minus_era5_krs019_mm_d"] = merged["eto_fao56_krs019_u10to2_mm_d"] - merged["eto_era5_krs019_mm_d"]
    merged["difference_station_minus_era5_krs016_mm_d"] = merged["eto_fao56_krs016_u10to2_mm_d"] - merged["eto_era5_krs016_mm_d"]
    merged.to_csv(DATA / "comparacion_noaa_era5land_chiclayo_diaria.csv", index=False)
    merged.to_csv(TABLES / "1_1b_comparacion_noaa_era5land_chiclayo_diaria.csv", index=False)

    station_monthly = pd.read_csv(STATION_MONTHLY, parse_dates=["month"])
    era_monthly_ssrd = full_months(era, "eto_era5_ssrd_mm_d")
    era_monthly_k19 = full_months(era, "eto_era5_krs019_mm_d")
    era_monthly_k16 = full_months(era, "eto_era5_krs016_mm_d")
    monthly = station_monthly.merge(era_monthly_ssrd, on="month", how="inner").merge(era_monthly_k19, on="month", how="inner").merge(era_monthly_k16, on="month", how="inner", suffixes=("", "_k16"))
    # Las tres series usan todas las fechas válidas de estación agrupadas como meses completos.
    if len(monthly) != len(station_monthly): raise ValueError("No coinciden los meses completos estación-ERA5")
    monthly["difference_station_minus_era5_ssrd_mm_month"] = monthly["eto_fao56_krs019_u10to2_mm_month"] - monthly["eto_era5_ssrd_mm_month"]
    monthly["difference_station_minus_era5_krs019_mm_month"] = monthly["eto_fao56_krs019_u10to2_mm_month"] - monthly["eto_era5_krs019_mm_month"]
    monthly["difference_station_minus_era5_krs016_mm_month"] = monthly["eto_fao56_krs016_u10to2_mm_month"] - monthly["eto_era5_krs016_mm_month"]
    monthly.to_csv(DATA / "comparacion_noaa_era5land_chiclayo_mensual.csv", index=False)
    monthly.to_csv(TABLES / "1_1b_comparacion_noaa_era5land_chiclayo_mensual.csv", index=False)

    metric_rows = [
        metrics(merged["eto_fao56_krs019_u10to2_mm_d"], merged["eto_era5_ssrd_mm_d"], "NOAA kRs=0.19 - ERA5 ssrd", "daily"),
        metrics(merged["eto_fao56_krs019_u10to2_mm_d"], merged["eto_era5_krs019_mm_d"], "NOAA kRs=0.19 - ERA5 kRs=0.19", "daily"),
        metrics(merged["eto_fao56_krs016_u10to2_mm_d"], merged["eto_era5_krs016_mm_d"], "NOAA kRs=0.16 - ERA5 kRs=0.16", "daily"),
        metrics(monthly["eto_fao56_krs019_u10to2_mm_month"], monthly["eto_era5_ssrd_mm_month"], "NOAA kRs=0.19 - ERA5 ssrd", "monthly"),
        metrics(monthly["eto_fao56_krs019_u10to2_mm_month"], monthly["eto_era5_krs019_mm_month"], "NOAA kRs=0.19 - ERA5 kRs=0.19", "monthly"),
    ]
    metric_df = pd.DataFrame(metric_rows)
    metric_df["station"] = station.STATION; metric_df["era5_latitude"] = returned_lat; metric_df["era5_longitude"] = returned_lon
    metric_df["station_radiation"] = "FAO-56 eq.50"
    metric_df.to_csv(TABLES / "1_1b_metricas_estacion_noaa_vs_era5land_chiclayo.csv", index=False)

    seasonal_rows=[]
    for month_no, part in merged.assign(calendar_month=merged.date.dt.month).groupby("calendar_month"):
        row = metrics(part["eto_fao56_krs019_u10to2_mm_d"], part["eto_era5_krs019_mm_d"], "NOAA kRs=.19 - ERA5 kRs=.19", "daily_seasonal")
        row["calendar_month"] = int(month_no); seasonal_rows.append(row)
    seasonal = pd.DataFrame(seasonal_rows).sort_values("calendar_month")
    seasonal.to_csv(TABLES / "1_1b_diferencias_estacionales_noaa_vs_era5land_chiclayo.csv", index=False)

    # Validación y metadatos de la fuente local.
    source_meta = pd.DataFrame([{"file": ZIP.name, "sha256": sha256(ZIP), "returned_latitude": returned_lat, "returned_longitude": returned_lon,
        "period_start_utc": "2010-01-01 00:00", "period_end_utc": "2023-01-01 23:00", "hourly_records_per_variable": 113976,
        "variables": ";".join(sorted(series)), "all_variables_complete": True, "role": "Validación local de estación; excluida de ponderación Racarumi",
        "station_distance_to_era5_cell_km": station.haversine_km(station.LATITUDE, station.LONGITUDE, LAT, LON)}])
    source_meta.to_csv(META / "era5land_chiclayo_sphi_validacion_y_metadatos.csv", index=False)
    pd.DataFrame(variable_meta).to_csv(META / "era5land_chiclayo_sphi_variables_unidades.csv", index=False)

    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    axes[0].plot(monthly.month, monthly.eto_fao56_krs019_u10to2_mm_month, label="NOAA + Eq.50 kRs=.19", lw=1)
    axes[0].plot(monthly.month, monthly.eto_era5_ssrd_mm_month, label="ERA5 ssrd", lw=1)
    axes[0].set(title="Chiclayo: ETo mensual, radiación propia", ylabel="mm/mes"); axes[0].legend(); axes[0].grid(alpha=.25)
    axes[1].plot(monthly.month, monthly.eto_fao56_krs019_u10to2_mm_month, label="NOAA + Eq.50 kRs=.19", lw=1)
    axes[1].plot(monthly.month, monthly.eto_era5_krs019_mm_month, label="ERA5 + Eq.50 kRs=.19", lw=1)
    axes[1].set(title="Chiclayo: ETo mensual, radiación metodológicamente homogénea", xlabel="Mes", ylabel="mm/mes"); axes[1].legend(); axes[1].grid(alpha=.25)
    savefig(fig, "1_1b_noaa_vs_era5land_chiclayo_series_mensuales")
    for suffix, x, y, title in [("ssrd", merged.eto_era5_ssrd_mm_d, merged.eto_fao56_krs019_u10to2_mm_d, "ERA5 ssrd"), ("krs019", merged.eto_era5_krs019_mm_d, merged.eto_fao56_krs019_u10to2_mm_d, "Ambas Eq.50 kRs=.19")]:
        fig, ax = plt.subplots(figsize=(5.5,5.2)); ax.scatter(x,y,s=8,alpha=.35)
        limits=[min(x.min(),y.min()),max(x.max(),y.max())]; ax.plot(limits,limits,"k--",lw=1,label="1:1")
        ax.set(title=f"Chiclayo: dispersión diaria ({title})", xlabel="ETo ERA5-Land (mm/día)", ylabel="ETo NOAA FAO-56 (mm/día)")
        ax.legend(); ax.grid(alpha=.25); savefig(fig, f"1_1b_noaa_vs_era5land_chiclayo_dispersion_{suffix}")
    climate = merged.assign(calendar_month=merged.date.dt.month).groupby("calendar_month").agg(
        noaa_krs019=("eto_fao56_krs019_u10to2_mm_d","mean"), era5_ssrd=("eto_era5_ssrd_mm_d","mean"),
        era5_krs019=("eto_era5_krs019_mm_d","mean"), diff_krs019=("difference_station_minus_era5_krs019_mm_d","mean")
    ).reset_index()
    climate.to_csv(TABLES / "1_1b_climatologia_noaa_vs_era5land_chiclayo.csv", index=False)
    fig, ax = plt.subplots(figsize=(9,4.5)); ax.plot(climate.calendar_month,climate.noaa_krs019,marker="o",label="NOAA Eq.50")
    ax.plot(climate.calendar_month,climate.era5_ssrd,marker="o",label="ERA5 ssrd"); ax.plot(climate.calendar_month,climate.era5_krs019,marker="o",label="ERA5 Eq.50")
    ax.set(title="Chiclayo: climatología diaria de ETo", xlabel="Mes",ylabel="mm/día",xticks=range(1,13));ax.legend(ncol=3,fontsize=8);ax.grid(alpha=.25)
    savefig(fig,"1_1b_noaa_vs_era5land_chiclayo_climatologia")
    fig,ax=plt.subplots(figsize=(9,4.5)); ax.bar(seasonal.calendar_month, seasonal.bias_station_minus_era5_mm)
    ax.axhline(0,color="k",lw=1); ax.set(title="Chiclayo: sesgo estacional NOAA - ERA5, Eq.50 común",xlabel="Mes",ylabel="mm/día",xticks=range(1,13));ax.grid(axis="y",alpha=.25)
    savefig(fig,"1_1b_noaa_vs_era5land_chiclayo_sesgo_estacional")

    primary = metric_df.query("comparison == 'NOAA kRs=0.19 - ERA5 kRs=0.19' and resolution == 'daily'").iloc[0]
    direct = metric_df.query("comparison == 'NOAA kRs=0.19 - ERA5 ssrd' and resolution == 'daily'").iloc[0]
    summary = f"""# Estación NOAA frente a ERA5-Land - Chiclayo

La celda ERA5-Land retornó ({returned_lat:.4f}, {returned_lon:.4f}), a
{source_meta.iloc[0].station_distance_to_era5_cell_km:.2f} km de la estación. El ZIP contiene las seis variables,
{len(series['t2m'])} horas por variable, sin nulos ni huecos; no se añadió a la
ponderación de Racarumi.

Hay {len(merged)} días comunes válidos y {len(monthly)} meses completos. Con
radiación propia de ERA5 (`ssrd`) frente a NOAA estimada con ecuación 50:
Pearson={direct.pearson_r:.4f}, Spearman={direct.spearman_rho:.4f}, sesgo
NOAA-ERA5={direct.bias_station_minus_era5_mm:.3f} mm/día, MAE={direct.mae_mm:.3f}
y RMSE={direct.rmse_mm:.3f} mm/día.

Al estimar radiación en ambas fuentes con ecuación 50 y kRs=0.19: Pearson=
{primary.pearson_r:.4f}, Spearman={primary.spearman_rho:.4f}, sesgo=
{primary.bias_station_minus_era5_mm:.3f} mm/día, MAE={primary.mae_mm:.3f} y
RMSE={primary.rmse_mm:.3f} mm/día. Esta segunda comparación reduce la diferencia
metodológica asociada a que NOAA no tiene radiación observada, pero conserva
diferencias de temperatura, humedad, presión y viento entre estación y reanálisis.

La prueba valida el comportamiento local de ERA5-Land en una estación costera
externa a Racarumi. No demuestra precisión en toda la cuenca andina ni modifica
la ETo de cuenca, que sigue preliminar con cobertura 90.1264 %.
"""
    (ANNEX / "resumen_tecnico_noaa_vs_era5land_chiclayo_1_1b.md").write_text(summary,encoding="utf-8")
    print(f"Días comunes: {len(merged)}; meses completos: {len(monthly)}")
    print(metric_df[["comparison","resolution","n","pearson_r","bias_station_minus_era5_mm","mae_mm","rmse_mm"]].to_string(index=False))

if __name__ == "__main__": main()
