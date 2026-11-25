"""Procesa la estación GHCNh PEI0000SPHI para la prueba de estación de 1.1.b.

Los PSV originales no se modifican. Las horas NOAA son UTC y se convierten a
UTC-05:00. La ETo se calcula sólo con días que cumplen criterios explícitos de
completitud. La radiación no fue observada: se estima con FAO-56 ec. 50 y se
entregan escenarios kRs=0.19 (costero) y 0.16 (sensibilidad).
"""
from __future__ import annotations

import calendar
import hashlib
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
RAW = ROOT / "datos" / "punto1" / "originales" / "noaa_ghcnh" / "PEI0000SPHI"
DATA = ROOT / "datos" / "punto1" / "procesados" / "1_1_b_pruebas_referencia"
META = ROOT / "datos" / "punto1" / "metadatos"
TABLES = ROOT / "productos" / "punto1" / "1_1_demanda_atmosferica" / "tablas"
FIGURES = ROOT / "productos" / "punto1" / "1_1_demanda_atmosferica" / "figuras"
ANNEX = ROOT / "anexos" / "punto1" / "1_1_b_pruebas_referencia"
PISCO_METRICS = TABLES / "1_1b_metricas_pet_piscoeopm_vs_eto.csv"
TERRA_METRICS = TABLES / "1_1b_metricas_terraclimate_y_productos_demanda.csv"
ERA_AVAILABLE = META / "era5land_disponibilidad_1_1a.csv"

STATION = "PEI0000SPHI"
LATITUDE, LONGITUDE, ELEVATION_M = -6.7875, -79.8281, 29.6
LOCAL_TZ = "Etc/GMT+5"
MIN_HOURS_DAY = 18
KRS_PRIMARY, KRS_SENSITIVITY = 0.19, 0.16
SOLAR_CONSTANT, SIGMA, ALBEDO = 0.0820, 4.903e-9, 0.23


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest().upper()


def qc_ok(value: object) -> bool:
    """Acepta blanco/no flag y códigos GHCNh no sospechosos; excluye 2/3/6/7."""
    if pd.isna(value) or str(value).strip() == "":
        return True
    code = str(value).strip().upper()
    # pandas representa los códigos numéricos con valores faltantes como 1.0, 4.0, etc.
    if code.endswith(".0") and code[:-2].isdigit():
        code = code[:-2]
    return code in {"0", "1", "4", "5", "9", "A", "U", "P", "I", "M", "R"}


def es(temp_c: pd.Series | np.ndarray) -> pd.Series | np.ndarray:
    return 0.6108 * np.exp(17.27 * temp_c / (temp_c + 237.3))


def extraterrestrial_radiation(index: pd.DatetimeIndex, latitude: float) -> np.ndarray:
    day = index.dayofyear.to_numpy()
    phi = np.deg2rad(latitude)
    dr = 1 + 0.033 * np.cos(2 * np.pi * day / 365)
    delta = 0.409 * np.sin(2 * np.pi * day / 365 - 1.39)
    ws = np.arccos(-np.tan(phi) * np.tan(delta))
    return (24 * 60 / np.pi) * SOLAR_CONSTANT * dr * (
        ws * np.sin(phi) * np.sin(delta) + np.cos(phi) * np.cos(delta) * np.sin(ws)
    )


def elevation_pressure_kpa(elevation_m: float) -> float:
    """FAO-56 eq. 7; presión atmosférica media desde elevación."""
    return 101.3 * ((293.0 - 0.0065 * elevation_m) / 293.0) ** 5.26


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1, phi2 = np.radians([lat1, lat2])
    dphi, dlambda = np.radians(lat2-lat1), np.radians(lon2-lon1)
    return float(2 * 6371.0088 * np.arcsin(np.sqrt(np.sin(dphi/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlambda/2)**2)))


def last_valid_hourly(raw: pd.DataFrame, variable: str) -> pd.Series:
    quality = variable + "_Quality_Code"
    selected = raw.loc[raw[variable].notna() & raw[quality].map(qc_ok), ["datetime_local", variable]].copy()
    selected["hour"] = selected["datetime_local"].dt.floor("h")
    # Un valor por hora: se mantiene el último informe disponible, sin alterar el PSV.
    selected = selected.sort_values("datetime_local").groupby("hour", as_index=False).tail(1)
    return selected.set_index("hour")[variable].sort_index()


def daily_fao56(daily: pd.DataFrame, krs: float, wind_is_10m: bool) -> pd.Series:
    rs = krs * np.sqrt((daily["tmax_c"] - daily["tmin_c"]).clip(lower=0)) * daily["ra_mj_m2_d"]
    u2 = daily["wind_ms"].copy()
    if wind_is_10m:
        u2 *= 4.87 / np.log(67.8 * 10.0 - 5.42)
    es_daily = (es(daily["tmax_c"]) + es(daily["tmin_c"])) / 2
    delta = 4098 * es(daily["tmean_c"]) / (daily["tmean_c"] + 237.3) ** 2
    gamma = 0.000665 * daily["p_kpa"]
    rso = (0.75 + 2e-5 * ELEVATION_M) * daily["ra_mj_m2_d"]
    rns = (1 - ALBEDO) * rs
    cloudiness = (rs / rso).clip(upper=1.0)
    rnl = SIGMA * (((daily["tmax_c"] + 273.16) ** 4 + (daily["tmin_c"] + 273.16) ** 4) / 2) * (
        0.34 - 0.14 * np.sqrt(daily["ea_kpa"])
    ) * (1.35 * cloudiness - 0.35)
    rn = rns - rnl
    numerator = 0.408 * delta * rn + gamma * (900 / (daily["tmean_c"] + 273)) * u2 * (es_daily - daily["ea_kpa"])
    denominator = delta + gamma * (1 + 0.34 * u2)
    return numerator / denominator


def independent_primary_check(daily: pd.DataFrame) -> pd.Series:
    """Segunda implementación vectorial de FAO-56 para el control numérico."""
    tmax, tmin, tmean = daily["tmax_c"], daily["tmin_c"], daily["tmean_c"]
    u2 = daily["wind_ms"] * (4.87 / np.log(672.58))
    radiation = KRS_PRIMARY * np.sqrt((tmax - tmin).clip(lower=0)) * daily["ra_mj_m2_d"]
    rso = (0.75 + 0.00002 * ELEVATION_M) * daily["ra_mj_m2_d"]
    longwave = SIGMA * (((tmax + 273.16) ** 4 + (tmin + 273.16) ** 4) / 2) * (
        0.34 - 0.14 * np.sqrt(daily["ea_kpa"])
    ) * (1.35 * (radiation / rso).clip(upper=1) - 0.35)
    net_radiation = 0.77 * radiation - longwave
    saturation = (es(tmax) + es(tmin)) / 2
    slope = 4098 * es(tmean) / (tmean + 237.3) ** 2
    psychrometric = 0.000665 * daily["p_kpa"]
    return (0.408 * slope * net_radiation + psychrometric * (900 / (tmean + 273)) * u2 * (saturation - daily["ea_kpa"])) / (
        slope + psychrometric * (1 + 0.34 * u2)
    )


def savefig(fig: plt.Figure, filename: str) -> None:
    for extension in ("png", "pdf"):
        fig.savefig(FIGURES / f"{filename}.{extension}", dpi=220 if extension == "png" else None, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    for folder in (DATA, META, TABLES, FIGURES, ANNEX):
        folder.mkdir(parents=True, exist_ok=True)
    files = sorted(RAW.glob(f"GHCNh_{STATION}_*.psv"))
    expected_years = list(range(2010, 2023))
    years = [int(file.stem.rsplit("_", 1)[1]) for file in files]
    if years != expected_years:
        raise ValueError(f"Años PSV inválidos: {years}")
    if len(files) != len(set(file.name for file in files)):
        raise ValueError("Se detectaron nombres PSV duplicados.")

    columns = ["STATION", "Station_name", "DATE", "LATITUDE", "LONGITUDE", "ELEVATION",
               "temperature", "temperature_Quality_Code", "dew_point_temperature", "dew_point_temperature_Quality_Code",
               "station_level_pressure", "station_level_pressure_Quality_Code", "wind_speed", "wind_speed_Quality_Code",
               "relative_humidity", "relative_humidity_Quality_Code", "wind_speed_Measurement_Code"]
    raw_parts = []
    integrity = []
    for file in files:
        frame = pd.read_csv(file, sep="|", usecols=columns, low_memory=False)
        frame["source_file"] = file.name
        raw_parts.append(frame)
        integrity.append({"file": file.name, "year": int(file.stem[-4:]), "size_bytes": file.stat().st_size,
                          "sha256": digest(file), "rows": len(frame), "status": "VALIDADO"})
    raw = pd.concat(raw_parts, ignore_index=True)
    if set(raw["STATION"].dropna().unique()) != {STATION}:
        raise ValueError("Identificador de estación inesperado en PSV.")
    raw["datetime_local"] = pd.to_datetime(raw["DATE"], utc=True).dt.tz_convert(LOCAL_TZ).dt.tz_localize(None)
    duplicate_timestamps = int(raw["DATE"].duplicated().sum())
    if duplicate_timestamps:
        raise ValueError(f"Se detectaron {duplicate_timestamps} fechas UTC duplicadas.")
    station_values = raw[["LATITUDE", "LONGITUDE", "ELEVATION"]].drop_duplicates()
    if len(station_values) != 1:
        raise ValueError("Metadatos de ubicación inconsistentes entre PSV.")

    hourly = pd.concat({
        "temperature_c": last_valid_hourly(raw, "temperature"),
        "dewpoint_c": last_valid_hourly(raw, "dew_point_temperature"),
        "pressure_hpa": last_valid_hourly(raw, "station_level_pressure"),
        "wind_ms": last_valid_hourly(raw, "wind_speed"),
        "relative_humidity_pct": last_valid_hourly(raw, "relative_humidity"),
    }, axis=1)
    hourly["pressure_hpa"] = hourly["pressure_hpa"].where(hourly["pressure_hpa"].between(900, 1050))
    grouped = hourly.groupby(hourly.index.normalize())
    daily = pd.DataFrame(index=grouped.size().index)
    daily["n_temperature_hours"] = grouped["temperature_c"].count()
    daily["n_dewpoint_hours"] = grouped["dewpoint_c"].count()
    daily["n_wind_hours"] = grouped["wind_ms"].count()
    daily["n_pressure_hours"] = grouped["pressure_hpa"].count()
    daily["tmin_c"] = grouped["temperature_c"].min()
    daily["tmax_c"] = grouped["temperature_c"].max()
    daily["tmean_c"] = grouped["temperature_c"].mean()
    daily["dewpoint_c"] = grouped["dewpoint_c"].mean()
    daily["ea_kpa"] = grouped["dewpoint_c"].apply(lambda x: es(x.dropna()).mean())
    daily["wind_ms"] = grouped["wind_ms"].mean()
    daily["pressure_observed_kpa"] = grouped["pressure_hpa"].mean() / 10.0
    daily["p_kpa"] = daily["pressure_observed_kpa"].where(daily["n_pressure_hours"] >= MIN_HOURS_DAY, elevation_pressure_kpa(ELEVATION_M))
    daily["pressure_source"] = np.where(daily["n_pressure_hours"] >= MIN_HOURS_DAY, "observed_station_level", "FAO56_eq7_elevation")
    daily["valid_temperature"] = daily["n_temperature_hours"] >= MIN_HOURS_DAY
    daily["valid_dewpoint"] = daily["n_dewpoint_hours"] >= MIN_HOURS_DAY
    daily["valid_wind"] = daily["n_wind_hours"] >= MIN_HOURS_DAY
    daily["valid_fao56"] = daily[["valid_temperature", "valid_dewpoint", "valid_wind"]].all(axis=1)
    daily["ra_mj_m2_d"] = extraterrestrial_radiation(pd.DatetimeIndex(daily.index), LATITUDE)
    valid = daily.loc[daily["valid_fao56"]].copy()
    valid["rs_krs019_mj_m2_d"] = KRS_PRIMARY * np.sqrt((valid["tmax_c"] - valid["tmin_c"]).clip(lower=0)) * valid["ra_mj_m2_d"]
    valid["rs_krs016_mj_m2_d"] = KRS_SENSITIVITY * np.sqrt((valid["tmax_c"] - valid["tmin_c"]).clip(lower=0)) * valid["ra_mj_m2_d"]
    valid["u2_assuming_10m_ms"] = valid["wind_ms"] * 4.87 / np.log(67.8 * 10.0 - 5.42)
    valid["eto_fao56_krs019_u10to2_mm_d"] = daily_fao56(valid, KRS_PRIMARY, True)
    valid["eto_fao56_krs016_u10to2_mm_d"] = daily_fao56(valid, KRS_SENSITIVITY, True)
    valid["eto_fao56_krs019_u2assumed_mm_d"] = daily_fao56(valid, KRS_PRIMARY, False)
    valid["eto_radiation_sensitivity_mm_d"] = valid["eto_fao56_krs019_u10to2_mm_d"] - valid["eto_fao56_krs016_u10to2_mm_d"]
    valid["eto_wind_height_sensitivity_mm_d"] = valid["eto_fao56_krs019_u2assumed_mm_d"] - valid["eto_fao56_krs019_u10to2_mm_d"]
    valid["station"] = STATION
    valid["station_name"] = raw["Station_name"].dropna().iat[0]
    valid["latitude"] = LATITUDE; valid["longitude"] = LONGITUDE; valid["elevation_m"] = ELEVATION_M
    valid = valid.reset_index(names="date")
    if not np.isfinite(valid["eto_fao56_krs019_u10to2_mm_d"]).all() or (valid["eto_fao56_krs019_u10to2_mm_d"] < 0).any():
        raise ValueError("ETo primaria contiene valores no físicos.")
    # Control independiente: segunda implementación vectorial de la ecuación 6.
    manual = independent_primary_check(valid).to_numpy()
    valid["eto_manual_check_mm_d"] = manual
    valid["eto_manual_check_abs_error_mm_d"] = np.abs(valid["eto_fao56_krs019_u10to2_mm_d"] - manual)

    daily_out = daily.reset_index(names="date").merge(valid[["date", "eto_fao56_krs019_u10to2_mm_d", "eto_fao56_krs016_u10to2_mm_d", "eto_fao56_krs019_u2assumed_mm_d", "eto_radiation_sensitivity_mm_d", "eto_wind_height_sensitivity_mm_d", "eto_manual_check_mm_d", "eto_manual_check_abs_error_mm_d"]], on="date", how="left")
    daily_out.to_csv(DATA / "noaa_ghcnh_pei0000sphi_meteorologia_y_eto_diaria.csv", index=False)
    daily_out.to_csv(TABLES / "1_1b_noaa_ghcnh_pei0000sphi_calidad_diaria.csv", index=False)

    monthly_rows = []
    for month, part in valid.groupby(valid["date"].dt.to_period("M"), sort=True):
        days = calendar.monthrange(month.year, month.month)[1]
        if len(part) == days and part["date"].nunique() == days:
            monthly_rows.append({"month": month.to_timestamp(), "days_in_month": days,
                                 "eto_fao56_krs019_u10to2_mm_month": part["eto_fao56_krs019_u10to2_mm_d"].sum(),
                                 "eto_fao56_krs016_u10to2_mm_month": part["eto_fao56_krs016_u10to2_mm_d"].sum(),
                                 "eto_fao56_krs019_u2assumed_mm_month": part["eto_fao56_krs019_u2assumed_mm_d"].sum(),
                                 "n_valid_days": len(part)})
    monthly = pd.DataFrame(monthly_rows)
    monthly.to_csv(DATA / "noaa_ghcnh_pei0000sphi_eto_mensual_completo.csv", index=False)
    monthly.to_csv(TABLES / "1_1b_noaa_ghcnh_pei0000sphi_eto_mensual_completo.csv", index=False)

    integrity_df = pd.DataFrame(integrity)
    integrity_df.to_csv(META / "noaa_ghcnh_pei0000sphi_integridad_sha256.csv", index=False)
    variable_summary = pd.DataFrame([
        {"variable": "temperature", "units": "degC", "role": "Tmax, Tmin y Tmedia diaria", "available_records": int(hourly.temperature_c.notna().sum())},
        {"variable": "dew_point_temperature", "units": "degC", "role": "presión real de vapor", "available_records": int(hourly.dewpoint_c.notna().sum())},
        {"variable": "station_level_pressure", "units": "hPa", "role": "gamma; eq. 7 si faltante/no físico", "available_records": int(hourly.pressure_hpa.notna().sum())},
        {"variable": "wind_speed", "units": "m/s", "role": "viento; altura local no documentada en PSV", "available_records": int(hourly.wind_ms.notna().sum())},
        {"variable": "solar_radiation", "units": "no disponible", "role": "estimada con FAO-56 eq. 50", "available_records": 0},
    ])
    variable_summary.to_csv(META / "noaa_ghcnh_pei0000sphi_variables_disponibles.csv", index=False)
    audit_rows = []
    quality_rows = []
    raw_hours = pd.DatetimeIndex(pd.to_datetime(raw["DATE"], utc=True))
    expected_utc_hours = pd.date_range(raw_hours.min(), raw_hours.max(), freq="h", tz="UTC")
    for source_name, output_name in [("temperature", "temperature_c"), ("dew_point_temperature", "dewpoint_c"),
                                     ("station_level_pressure", "pressure_hpa"), ("wind_speed", "wind_ms"),
                                     ("relative_humidity", "relative_humidity_pct")]:
        qc_name = source_name + "_Quality_Code"
        present = raw[source_name].notna()
        accepted = present & raw[qc_name].map(qc_ok)
        audit_rows.append({"variable": source_name, "raw_nonmissing_records": int(present.sum()),
                           "accepted_qc_records": int(accepted.sum()), "rejected_qc_records": int((present & ~accepted).sum()),
                           "selected_unique_local_hours": int(hourly[output_name].notna().sum()),
                           "notes": "Presión adicionalmente restringida a 900-1050 hPa para uso físico." if source_name == "station_level_pressure" else ""})
        counts = raw.loc[present, qc_name].fillna("<blank>").astype(str).value_counts()
        quality_rows.extend({"variable": source_name, "quality_code": code, "count": int(count)} for code, count in counts.items())
    audit_rows.append({"variable": "temporal_index", "raw_nonmissing_records": len(raw),
                       "accepted_qc_records": raw_hours.nunique(), "rejected_qc_records": duplicate_timestamps,
                       "selected_unique_local_hours": len(expected_utc_hours) - raw_hours.nunique(),
                       "notes": "Última columna = horas UTC ausentes entre primer y último registro; no son valores rellenados."})
    pd.DataFrame(audit_rows).to_csv(META / "noaa_ghcnh_pei0000sphi_auditoria_variables_y_continuidad.csv", index=False)
    pd.DataFrame(quality_rows).to_csv(META / "noaa_ghcnh_pei0000sphi_banderas_calidad.csv", index=False)
    annual_quality = daily_out.assign(year=daily_out.date.dt.year).groupby("year").agg(
        calendar_days=("date", "count"), valid_eto_days=("valid_fao56", "sum"),
        complete_pressure_days=("n_pressure_hours", lambda x: int((x >= MIN_HOURS_DAY).sum())),
        mean_temperature_hours=("n_temperature_hours", "mean"), mean_dewpoint_hours=("n_dewpoint_hours", "mean"),
        mean_wind_hours=("n_wind_hours", "mean"),
    ).reset_index()
    annual_quality.to_csv(TABLES / "1_1b_noaa_ghcnh_pei0000sphi_resumen_calidad_anual.csv", index=False)
    station_metadata = pd.DataFrame([{
        "station": STATION, "station_name": raw["Station_name"].dropna().iat[0], "latitude": LATITUDE, "longitude": LONGITUDE,
        "elevation_m": ELEVATION_M, "raw_period_utc_start": raw["DATE"].min(), "raw_period_utc_end": raw["DATE"].max(),
        "raw_records": len(raw), "duplicate_utc_timestamps": duplicate_timestamps, "time_reference": "UTC in GHCNh; processed UTC-05:00",
        "wind_measurement_height": "No documentada en PSV/GHCNh; producto principal asume convencionalmente 10 m y reporta sensibilidad sin ajuste.",
        "radiation": "No observada; FAO-56 eq. 50 con kRs 0.19 costero y sensibilidad 0.16.",
    }])
    station_metadata.to_csv(META / "noaa_ghcnh_pei0000sphi_metadatos_estacion.csv", index=False)

    # La celda de ERA5-Land más cercana disponible es P1, insuficiente para prueba puntual.
    available = pd.read_csv(ERA_AVAILABLE)
    available["distance_km"] = available.apply(lambda x: haversine_km(LATITUDE, LONGITUDE, x.latitude, x.longitude), axis=1)
    nearest = available.sort_values("distance_km").iloc[0]
    request = pd.DataFrame([{
        "purpose": "Comparación estación NOAA - ERA5-Land puntual", "station": STATION,
        "station_latitude": LATITUDE, "station_longitude": LONGITUDE, "station_elevation_m": ELEVATION_M,
        "nearest_existing_era5_point": nearest["point"], "nearest_existing_latitude": nearest["latitude"],
        "nearest_existing_longitude": nearest["longitude"], "nearest_existing_distance_km": nearest["distance_km"],
        "decision": "No usar la celda existente para validación puntual: solicitar una sola serie en la estación y validar la celda retornada.",
        "dataset": "reanalysis-era5-land-timeseries", "request_latitude": LATITUDE, "request_longitude": LONGITUDE,
        "expected_nearest_grid_latitude_approx": -6.8, "expected_nearest_grid_longitude_approx": -79.8,
        "period_utc_start": "2010-01-01 00:00", "period_utc_end": "2022-12-31 23:00", "frequency": "hourly",
        "variables": "2m_temperature;2m_dewpoint_temperature;surface_pressure;surface_solar_radiation_downwards;10m_u_component_of_wind;10m_v_component_of_wind",
        "radiation_sensitivity": "Aplicar también FAO-56 eq. 50 kRs=0.19 a ERA5 para comparación metodológica con la estación.",
        "status": "PENDIENTE: no descargar automáticamente",
    }])
    request.to_csv(ANNEX / "solicitud_era5land_puntual_estacion_pei0000sphi.csv", index=False)

    # Figuras de estación y sensibilidad; no se crea una falsa gráfica estación-ERA5.
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(valid["date"], valid["eto_fao56_krs019_u10to2_mm_d"], lw=.6, label="kRs=0.19, viento 10 m -> 2 m")
    ax.plot(valid["date"], valid["eto_fao56_krs016_u10to2_mm_d"], lw=.6, label="kRs=0.16 (sensibilidad)")
    ax.set(title="Chiclayo: ETo diaria FAO-56 condicional", xlabel="Fecha local UTC-05", ylabel="mm/día")
    ax.legend(fontsize=8); ax.grid(alpha=.25); savefig(fig, "1_1b_noaa_estacion_eto_diaria_y_sensibilidad")
    climatology = valid.assign(month=valid.date.dt.month).groupby("month").agg(
        eto_krs019=("eto_fao56_krs019_u10to2_mm_d", "mean"), eto_krs016=("eto_fao56_krs016_u10to2_mm_d", "mean"),
        radiation_sensitivity=("eto_radiation_sensitivity_mm_d", "mean"), wind_height_sensitivity=("eto_wind_height_sensitivity_mm_d", "mean")
    ).reset_index()
    climatology.to_csv(TABLES / "1_1b_noaa_ghcnh_pei0000sphi_climatologia_y_sensibilidad.csv", index=False)
    fig, ax = plt.subplots(figsize=(9,4.5))
    ax.plot(climatology.month, climatology.eto_krs019, marker="o", label="kRs=0.19")
    ax.plot(climatology.month, climatology.eto_krs016, marker="o", label="kRs=0.16")
    ax.set(title="Chiclayo: climatología ETo de estación", xlabel="Mes", ylabel="mm/día", xticks=range(1,13))
    ax.legend(); ax.grid(alpha=.25); savefig(fig, "1_1b_noaa_estacion_eto_climatologia")
    fig, ax = plt.subplots(figsize=(11,4.5))
    quality_plot = daily_out.assign(year=daily_out.date.dt.year).groupby("year").agg(
        days=("date","count"), valid_fao56=("valid_fao56","sum"), temp_hours=("n_temperature_hours","mean"),
        dew_hours=("n_dewpoint_hours","mean"), wind_hours=("n_wind_hours","mean")
    )
    quality_plot[["temp_hours","dew_hours","wind_hours"]].plot(ax=ax, marker="o")
    ax.axhline(MIN_HOURS_DAY, color="black", ls="--", lw=1, label="umbral 18 h/día")
    ax.set(title="Chiclayo: cobertura diaria media por variable", xlabel="Año", ylabel="horas válidas/día")
    ax.legend(ncol=2, fontsize=8); ax.grid(alpha=.25); savefig(fig, "1_1b_noaa_estacion_cobertura_diaria")

    # Consolida métricas existentes sin recalcular productos anteriores.
    old = pd.concat([pd.read_csv(PISCO_METRICS), pd.read_csv(TERRA_METRICS)], ignore_index=True)
    station_row = pd.DataFrame([{"comparison": "ETo estación NOAA PEI0000SPHI - ERA5-Land puntual", "n_months": 0,
        "pearson_r": np.nan, "spearman_rho": np.nan, "bias_left_minus_right_mm_month": np.nan, "mae_mm_month": np.nan,
        "rmse_mm_month": np.nan, "status": "PENDIENTE: requiere celda ERA5-Land puntual solicitada"}])
    pd.concat([old, station_row], ignore_index=True, sort=False).to_csv(TABLES / "1_1b_metricas_consolidadas_preliminares.csv", index=False)

    primary_mean = valid["eto_fao56_krs019_u10to2_mm_d"].mean()
    sensitivity_mean = valid["eto_radiation_sensitivity_mm_d"].mean()
    wind_sensitivity_mean = valid["eto_wind_height_sensitivity_mm_d"].mean()
    summary = f"""# Prueba de estación NOAA GHCNh - PEI0000SPHI

Los 13 PSV originales (2010-2022) fueron trasladados sin modificación y todos
conservaron SHA-256. GHCNh indexa los registros en UTC; el cálculo diario usa
UTC-05:00. La estación está en Chiclayo ({LATITUDE}, {LONGITUDE}; {ELEVATION_M} m),
un aeropuerto costero, por lo que no se interpreta como representativa del
relieve andino de toda Racarumi.

Se aceptó un día sólo cuando temperatura, punto de rocío y viento tenían al menos
{MIN_HOURS_DAY} horas válidas. Hay {len(valid)} días válidos y {len(monthly)} meses
completos. La presión observada se usó sólo con cobertura suficiente y valores
900-1050 hPa; en los demás días se aplicó FAO-56 ecuación 7 con la elevación.

No hay radiación solar observada. La ETo primaria usa FAO-56 ecuación 50 con
kRs={KRS_PRIMARY} por condición costera: media {primary_mean:.3f} mm/día. La sensibilidad
kRs={KRS_SENSITIVITY} cambia ETo en promedio {sensitivity_mean:.3f} mm/día. La altura
exacta del anemómetro no aparece en los PSV; el producto primario aplica el ajuste
10 m a 2 m como supuesto convencional y el escenario sin ajuste cambia ETo en
{wind_sensitivity_mean:.3f} mm/día en promedio. Estas sensibilidades son parte del
resultado, no observaciones inventadas.

La celda ERA5-Land existente más cercana es {nearest['point']} a
{nearest['distance_km']:.1f} km, por lo cual no es apropiada para una validación
puntual. La solicitud mínima para una sola celda está en
`solicitud_era5land_puntual_estacion_pei0000sphi.csv`; hasta contar con ella no
se reportan métricas estación-ERA5 ni se declara terminada la segunda categoría
de prueba. La ETo de cuenca sigue siendo preliminar (cobertura 90.1264 %).
"""
    (ANNEX / "resumen_tecnico_estacion_noaa_1_1b.md").write_text(textwrap.dedent(summary), encoding="utf-8")
    print(f"Registros originales: {len(raw)}; días ETo válidos: {len(valid)}; meses completos: {len(monthly)}")
    print(f"ETo media primaria: {primary_mean:.3f} mm/día; control máximo: {valid.eto_manual_check_abs_error_mm_d.max():.3e}")
    print(f"ERA5 más cercano existente: {nearest['point']} a {nearest['distance_km']:.1f} km")

if __name__ == "__main__":
    main()
