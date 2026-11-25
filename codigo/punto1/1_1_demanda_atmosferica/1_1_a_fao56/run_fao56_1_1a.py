"""Reproducible FAO-56 Penman-Monteith processing for Tarea 2, section 1.1.a.

The script never alters source ZIP files.  It reads NetCDF members directly from
the ZIP archives, validates them, and writes only derived products under
``tarea 02/datos`` and ``tarea 02/productos``.

Important methodological choice
-------------------------------
ERA5-Land timestamps are UTC.  Daily hydrological calculations are made in a
fixed UTC-05:00 clock (Peru standard time), retaining only complete 24-hour local calendar days.
Consequently, the two partial edge dates created by the requested UTC interval
are excluded from daily products.
"""

from __future__ import annotations

from hashlib import sha256
from io import BytesIO
from pathlib import Path
import json
import zipfile

import h5netcdf  # noqa: F401 - registers the HDF5 backend used by xarray.
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr


ROOT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
TASK = ROOT
RAW = TASK / "punto 1"
SUPPLEMENT = RAW / "ERA5_Land_Datos_Complementarios"
ELEVATION = (
    ROOT / "datos" / "punto1" / "originales" / "tarea1_minimos" / "PE_200907_ERA5Land_cells_SRTM_elevation.csv"
)
NATIVE_OROGRAPHY = ELEVATION.with_name("PE_200907_ERA5Land_native_orography.csv")

DATA_OUT = TASK / "datos" / "punto1"
PROCESSED = DATA_OUT / "procesados" / "1_1_a_fao56"
METADATA = DATA_OUT / "metadatos"
PRODUCTS = TASK / "productos" / "punto1" / "1_1_demanda_atmosferica"
TABLES = PRODUCTS / "tablas"
FIGURES = PRODUCTS / "figuras"
CHECKS = PRODUCTS / "comprobaciones"
ANNEXES = TASK / "anexos" / "punto1"

EXPECTED = {
    "P1": (-6.6, -79.3),
    "P2": (-6.5, -79.2),
    "P3": (-6.4, -79.2),
    "P4": (-6.6, -79.1),
    "P5": (-6.6, -78.9),
    "P6": (-6.7, -78.7),
    "P7": (-6.8, -78.8),
    "P8": (-6.9, -78.9),
}
REQUIRED = {"t2m", "d2m", "sp", "ssrd", "u10", "v10"}
START_UTC = pd.Timestamp("1981-01-01 00:00:00")
END_UTC = pd.Timestamp("2023-08-31 23:00:00")
EXPECTED_HOURS = len(pd.date_range(START_UTC, END_UTC, freq="h"))
LOCAL_TZ = "Etc/GMT+5"  # IANA's Etc sign is inverted: this means UTC-05:00.
LOCAL_TIME_LABEL = "UTC-05:00 (hora estándar de Perú)"
ALBEDO_REFERENCE = 0.23
SOLAR_CONSTANT = 0.0820  # MJ m-2 min-1
SIGMA = 4.903e-9  # MJ K-4 m-2 day-1


def ensure_output_directories() -> None:
    for folder in (PROCESSED, METADATA, TABLES, FIGURES, CHECKS, ANNEXES):
        folder.mkdir(parents=True, exist_ok=True)


def digest(path: Path) -> str:
    hasher = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def read_zip_netcdf(zip_path: Path) -> tuple[dict[str, pd.Series], list[dict], list[dict]]:
    """Read all variables from a ZIP in memory and return validation metadata."""
    series: dict[str, pd.Series] = {}
    variable_metadata: list[dict] = []
    file_metadata: list[dict] = []
    with zipfile.ZipFile(zip_path) as archive:
        broken_member = archive.testzip()
        if broken_member is not None:
            raise ValueError(f"ZIP corrupto; primer miembro dañado: {broken_member}")
        netcdfs = [member for member in archive.namelist() if member.lower().endswith(".nc")]
        if not netcdfs:
            raise ValueError("El ZIP no contiene archivos NetCDF (.nc).")
        for member in netcdfs:
            dataset = xr.open_dataset(
                BytesIO(archive.read(member)), engine="h5netcdf", decode_times=True
            )
            try:
                time_name = "valid_time" if "valid_time" in dataset.coords else "time"
                if time_name not in dataset.coords:
                    raise ValueError(f"{member}: no se encontró una coordenada temporal.")
                time = pd.DatetimeIndex(pd.to_datetime(dataset[time_name].values))
                latitude = float(dataset["latitude"].values)
                longitude = float(dataset["longitude"].values)
                if longitude > 180:
                    longitude -= 360
                gaps = int(
                    np.count_nonzero(
                        np.diff(time.values).astype("timedelta64[s]").astype("int64") != 3600
                    )
                )
                file_metadata.append(
                    {
                        "member": member,
                        "records": len(time),
                        "start_utc": str(time.min()),
                        "end_utc": str(time.max()),
                        "unique_timestamps": int(time.nunique()),
                        "nonhourly_intervals": gaps,
                        "latitude": latitude,
                        "longitude": longitude,
                    }
                )
                for variable in dataset.data_vars:
                    if variable in series:
                        raise ValueError(f"Variable repetida en un ZIP: {variable}")
                    values = np.asarray(dataset[variable].values, dtype=float)
                    series[variable] = pd.Series(values, index=time, name=variable)
                    variable_metadata.append(
                        {
                            "member": member,
                            "variable": variable,
                            "units": dataset[variable].attrs.get("units", ""),
                            "long_name": dataset[variable].attrs.get("long_name", ""),
                            "step_type": dataset[variable].attrs.get("GRIB_stepType", ""),
                            "records": int(values.size),
                            "missing_values": int(np.count_nonzero(~np.isfinite(values))),
                        }
                    )
            finally:
                dataset.close()
    return series, variable_metadata, file_metadata


def hourly_to_local(series: pd.Series) -> pd.Series:
    """Interpret ERA5 timestamps as UTC and return fixed UTC-05:00 local clock time."""
    local_index = series.index.tz_localize("UTC").tz_convert(LOCAL_TZ).tz_localize(None)
    result = series.copy()
    result.index = local_index
    return result


def saturation_vapour_pressure(temperature_c: pd.Series | float) -> pd.Series | float:
    return 0.6108 * np.exp((17.27 * temperature_c) / (temperature_c + 237.3))


def extraterrestrial_radiation(date_index: pd.DatetimeIndex, latitude_deg: float) -> np.ndarray:
    """FAO-56 equation 21, daily Ra in MJ m-2 day-1."""
    julian_day = date_index.dayofyear.to_numpy()
    latitude_rad = np.deg2rad(latitude_deg)
    inverse_distance = 1 + 0.033 * np.cos(2 * np.pi * julian_day / 365)
    solar_declination = 0.409 * np.sin(2 * np.pi * julian_day / 365 - 1.39)
    sunset_angle = np.arccos(-np.tan(latitude_rad) * np.tan(solar_declination))
    return (24 * 60 / np.pi) * SOLAR_CONSTANT * inverse_distance * (
        sunset_angle * np.sin(latitude_rad) * np.sin(solar_declination)
        + np.cos(latitude_rad) * np.cos(solar_declination) * np.sin(sunset_angle)
    )


def fao56_daily(point: str, hourly: dict[str, pd.Series], elevation_m: float, latitude: float) -> pd.DataFrame:
    """Calculate daily FAO-56 ETo from validated hourly variables for one point."""
    local = pd.DataFrame({name: hourly_to_local(value) for name, value in hourly.items()})
    local["t2m_c"] = local["t2m"] - 273.15
    local["d2m_c"] = local["d2m"] - 273.15
    local["p_kpa"] = local["sp"] / 1000.0
    # The magnitude is formed hourly before any temporal averaging (guide requirement).
    # ``wind10_ms`` is also accepted for an already spatially averaged hourly
    # magnitude; this avoids wrongly reconstructing wind from averaged vectors.
    if "wind10_ms" in local:
        wind_columns = ["wind10_ms"]
    else:
        local["wind10_ms"] = np.hypot(local["u10"], local["v10"])
        wind_columns = ["u10", "v10"]
    local["ea_kpa_hourly"] = saturation_vapour_pressure(local["d2m_c"])

    counts = local[["t2m", "d2m", "sp", "ssrd", *wind_columns]].resample("D").count().min(axis=1)
    daily = pd.DataFrame(index=counts.index)
    daily["n_hourly_records"] = counts
    daily["tmin_c"] = local["t2m_c"].resample("D").min()
    daily["tmax_c"] = local["t2m_c"].resample("D").max()
    daily["tmean_c"] = local["t2m_c"].resample("D").mean()
    daily["ea_kpa"] = local["ea_kpa_hourly"].resample("D").mean()
    daily["p_kpa"] = local["p_kpa"].resample("D").mean()
    daily["wind10_ms"] = local["wind10_ms"].resample("D").mean()
    daily["rs_mj_m2_d"] = local["ssrd"].resample("D").sum() / 1_000_000.0
    # Do not turn partial UTC-edge days into apparently complete local days.
    daily = daily.loc[daily["n_hourly_records"] == 24].copy()
    daily["u2_ms"] = daily["wind10_ms"] * 4.87 / np.log(67.8 * 10.0 - 5.42)
    daily["es_kpa"] = (
        saturation_vapour_pressure(daily["tmax_c"])
        + saturation_vapour_pressure(daily["tmin_c"])
    ) / 2.0
    daily["delta_kpa_c"] = (
        4098 * saturation_vapour_pressure(daily["tmean_c"])
        / (daily["tmean_c"] + 237.3) ** 2
    )
    daily["gamma_kpa_c"] = 0.000665 * daily["p_kpa"]
    daily["ra_mj_m2_d"] = extraterrestrial_radiation(daily.index, latitude)
    daily["rso_mj_m2_d"] = (0.75 + 2e-5 * elevation_m) * daily["ra_mj_m2_d"]
    daily["rns_mj_m2_d"] = (1 - ALBEDO_REFERENCE) * daily["rs_mj_m2_d"]
    cloudiness = (daily["rs_mj_m2_d"] / daily["rso_mj_m2_d"]).clip(upper=1.0)
    daily["rnl_mj_m2_d"] = SIGMA * (
        ((daily["tmax_c"] + 273.16) ** 4 + (daily["tmin_c"] + 273.16) ** 4) / 2
    ) * (0.34 - 0.14 * np.sqrt(daily["ea_kpa"])) * (1.35 * cloudiness - 0.35)
    daily["rn_mj_m2_d"] = daily["rns_mj_m2_d"] - daily["rnl_mj_m2_d"]
    daily["g_mj_m2_d"] = 0.0  # FAO-56 daily calculation: G approximately zero.
    numerator = (
        0.408 * daily["delta_kpa_c"] * (daily["rn_mj_m2_d"] - daily["g_mj_m2_d"])
        + daily["gamma_kpa_c"]
        * (900.0 / (daily["tmean_c"] + 273.0))
        * daily["u2_ms"]
        * (daily["es_kpa"] - daily["ea_kpa"])
    )
    denominator = daily["delta_kpa_c"] + daily["gamma_kpa_c"] * (1 + 0.34 * daily["u2_ms"])
    daily["eto_fao56_mm_d"] = numerator / denominator
    daily.insert(0, "point", point)
    daily.insert(1, "latitude", latitude)
    daily.insert(2, "elevation_dem_m", elevation_m)
    return daily.reset_index(names="date")


def fao56_monthly_direct(daily: pd.DataFrame) -> pd.DataFrame:
    """Apply FAO-56 to monthly mean meteorological variables.

    This is deliberately different from summing daily ETo.  In accordance with
    the course guide, monthly soil heat flux is G_i=0.07(T_{i+1}-T_{i-1}).
    The first and last months cannot be evaluated by this centred expression and
    remain missing rather than being imputed.
    """
    index = pd.DatetimeIndex(daily["date"])
    point = daily["point"].iat[0]
    latitude = float(daily["latitude"].iat[0])
    elevation = float(daily["elevation_dem_m"].iat[0])
    numeric = daily.set_index(index)
    columns = [
        "tmin_c", "tmax_c", "tmean_c", "ea_kpa", "p_kpa", "u2_ms",
        "rs_mj_m2_d", "ra_mj_m2_d", "eto_fao56_mm_d",
    ]
    monthly = numeric[columns].resample("MS").mean()
    monthly["days_in_month"] = monthly.index.days_in_month
    monthly["eto_from_daily_mm"] = numeric["eto_fao56_mm_d"].resample("MS").sum()
    monthly["g_mj_m2_d"] = 0.07 * (
        monthly["tmean_c"].shift(-1) - monthly["tmean_c"].shift(1)
    )
    monthly["es_kpa"] = (
        saturation_vapour_pressure(monthly["tmax_c"])
        + saturation_vapour_pressure(monthly["tmin_c"])
    ) / 2.0
    monthly["delta_kpa_c"] = (
        4098 * saturation_vapour_pressure(monthly["tmean_c"])
        / (monthly["tmean_c"] + 237.3) ** 2
    )
    monthly["gamma_kpa_c"] = 0.000665 * monthly["p_kpa"]
    monthly["rso_mj_m2_d"] = (0.75 + 2e-5 * elevation) * monthly["ra_mj_m2_d"]
    monthly["rns_mj_m2_d"] = (1 - ALBEDO_REFERENCE) * monthly["rs_mj_m2_d"]
    cloudiness = (monthly["rs_mj_m2_d"] / monthly["rso_mj_m2_d"]).clip(upper=1.0)
    monthly["rnl_mj_m2_d"] = SIGMA * (
        ((monthly["tmax_c"] + 273.16) ** 4 + (monthly["tmin_c"] + 273.16) ** 4) / 2
    ) * (0.34 - 0.14 * np.sqrt(monthly["ea_kpa"])) * (1.35 * cloudiness - 0.35)
    monthly["rn_mj_m2_d"] = monthly["rns_mj_m2_d"] - monthly["rnl_mj_m2_d"]
    numerator = (
        0.408 * monthly["delta_kpa_c"] * (monthly["rn_mj_m2_d"] - monthly["g_mj_m2_d"])
        + monthly["gamma_kpa_c"]
        * (900.0 / (monthly["tmean_c"] + 273.0))
        * monthly["u2_ms"]
        * (monthly["es_kpa"] - monthly["ea_kpa"])
    )
    denominator = monthly["delta_kpa_c"] + monthly["gamma_kpa_c"] * (1 + 0.34 * monthly["u2_ms"])
    monthly["eto_monthly_direct_mm_d"] = numerator / denominator
    monthly["eto_monthly_direct_mm"] = (
        monthly["eto_monthly_direct_mm_d"] * monthly["days_in_month"]
    )
    monthly["difference_direct_minus_daily_mm"] = (
        monthly["eto_monthly_direct_mm"] - monthly["eto_from_daily_mm"]
    )
    monthly["difference_relative_pct"] = (
        100 * monthly["difference_direct_minus_daily_mm"] / monthly["eto_from_daily_mm"]
    )
    monthly.insert(0, "point", point)
    monthly.insert(1, "latitude", latitude)
    monthly.insert(2, "elevation_dem_m", elevation)
    return monthly.reset_index(names="month")


def write_figure(monthly: pd.DataFrame) -> None:
    points = sorted(monthly["point"].unique())
    fig, axes = plt.subplots(len(points), 1, figsize=(12, 2.3 * len(points)), sharex=True)
    if len(points) == 1:
        axes = [axes]
    for axis, point in zip(axes, points):
        subset = monthly.loc[monthly["point"] == point]
        axis.plot(subset["month"], subset["eto_from_daily_mm"], lw=0.8, label="Suma de ETo diaria")
        axis.plot(subset["month"], subset["eto_monthly_direct_mm"], lw=0.8, label="Cálculo con medias mensuales")
        axis.set_ylabel("mm mes$^{-1}$")
        axis.set_title(point)
        axis.grid(alpha=0.25)
    axes[0].legend(ncol=2, fontsize=8)
    axes[-1].set_xlabel(f"Mes local ({LOCAL_TIME_LABEL})")
    fig.suptitle("FAO-56: suma diaria frente a cálculo directo mensual", y=1.002)
    fig.tight_layout()
    fig.savefig(FIGURES / "fao56_comparacion_diaria_vs_mensual_por_punto.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    ensure_output_directories()
    elevation = pd.read_csv(ELEVATION)
    elevation["key"] = list(zip(elevation["latitude"].round(4), elevation["longitude"].round(4)))
    elevation_lookup = elevation.set_index("key")["dem_mean_elevation_m"].to_dict()
    weight_lookup = elevation.set_index("key")["era5land_spatial_weight"].to_dict()
    native_orography = pd.read_csv(NATIVE_OROGRAPHY)
    weighted_dem_m = float(
        (elevation["dem_mean_elevation_m"] * elevation["era5land_spatial_weight"]).sum()
    )
    weighted_era5_m = float(
        (native_orography["era5land_geopotential_height_m"] * native_orography["spatial_weight"]).sum()
    )

    availability_rows: list[dict] = []
    input_rows: list[dict] = []
    variable_rows: list[dict] = []
    valid_hourly: dict[str, dict[str, pd.Series]] = {}

    for point, (latitude, longitude) in EXPECTED.items():
        original = RAW / f"datospunto1originalesERA5_Land_{point}.zip"
        sources = [("original", original)]
        if point == "P2":
            sources.append(("complemento_v10", SUPPLEMENT / "ERA5_Land_P2_v10_FALTANTE.zip"))
        if point == "P5":
            sources.append(("complemento_ssrd_correcto", SUPPLEMENT / "ERA5_Land_P5_ssrd_CORRECTO.zip"))

        combined: dict[str, pd.Series] = {}
        point_issues: list[str] = []
        all_file_meta: list[dict] = []
        for source_role, source in sources:
            if not source.exists():
                point_issues.append(f"No existe {source_role}: {source.name}")
                continue
            try:
                series, variables, files = read_zip_netcdf(source)
                input_rows.append(
                    {
                        "point": point,
                        "role": source_role,
                        "path_relative_to_project": str(source.relative_to(ROOT)),
                        "sha256": digest(source),
                        "zip_integrity_ok": True,
                    }
                )
                for variable in variables:
                    variable_rows.append({"point": point, "role": source_role, **variable})
                all_file_meta.extend(files)
                for name, item in series.items():
                    if name in combined:
                        point_issues.append(f"Variable duplicada entre fuentes: {name}")
                    else:
                        combined[name] = item
            except Exception as exc:  # Continue auditing other points rather than hiding a failed source.
                point_issues.append(f"{source_role}: {type(exc).__name__}: {exc}")

        # Validate every NetCDF against its intended coordinate and requested hourly interval.
        for meta in all_file_meta:
            coordinate_ok = (
                np.isclose(meta["latitude"], latitude, atol=1e-6)
                and np.isclose(meta["longitude"], longitude, atol=1e-6)
            )
            time_ok = (
                meta["records"] == EXPECTED_HOURS
                and meta["start_utc"] == str(START_UTC)
                and meta["end_utc"] == str(END_UTC)
                and meta["unique_timestamps"] == EXPECTED_HOURS
                and meta["nonhourly_intervals"] == 0
            )
            if not coordinate_ok:
                point_issues.append(f"Coordenada no coincide en {meta['member']}")
            if not time_ok:
                point_issues.append(f"Tiempo no continuo/completo en {meta['member']}")

        missing = sorted(REQUIRED - set(combined))
        unexpected = sorted(set(combined) - REQUIRED)
        nulls = {name: int(np.count_nonzero(~np.isfinite(item.to_numpy()))) for name, item in combined.items()}
        for name, count in nulls.items():
            if name in REQUIRED and count:
                point_issues.append(f"{name} tiene {count} valores no finitos")
        if missing:
            point_issues.append("Variables obligatorias ausentes: " + ", ".join(missing))
        if "strd" in combined and "ssrd" not in combined:
            point_issues.append(
                "El complemento P5 contiene strd (radiación térmica descendente), no ssrd."
            )
        elevation_m = elevation_lookup.get((round(latitude, 4), round(longitude, 4)))
        if elevation_m is None:
            point_issues.append("No se encontró elevación SRTM asociada al punto.")
        status = "validado_para_fao56" if not point_issues else "bloqueado"
        availability_rows.append(
            {
                "point": point,
                "latitude": latitude,
                "longitude": longitude,
                "elevation_dem_mean_m": elevation_m,
                "available_variables": ";".join(sorted(combined)),
                "missing_required_variables": ";".join(missing),
                "unexpected_variables": ";".join(unexpected),
                "status": status,
                "issues": " | ".join(point_issues),
            }
        )
        if status == "validado_para_fao56":
            valid_hourly[point] = {name: combined[name] for name in REQUIRED}

    availability = pd.DataFrame(availability_rows)
    availability.to_csv(METADATA / "era5land_disponibilidad_1_1a.csv", index=False)
    pd.DataFrame(input_rows).to_csv(METADATA / "era5land_fuentes_sha256_1_1a.csv", index=False)
    pd.DataFrame(variable_rows).to_csv(METADATA / "era5land_variables_unidades_1_1a.csv", index=False)
    availability["era5land_weight_from_tarea1"] = [
        weight_lookup[(round(latitude, 4), round(longitude, 4))]
        for latitude, longitude in zip(availability["latitude"], availability["longitude"])
    ]
    availability.to_csv(METADATA / "fao56_representacion_espacial_1_1a.csv", index=False)
    selected_weight_sum = float(availability["era5land_weight_from_tarea1"].sum())
    pd.DataFrame(
        [{
            "era5land_cells_intersecting_catchment": len(elevation),
            "total_catchment_weight": elevation["era5land_spatial_weight"].sum(),
            "selected_eight_point_weight": selected_weight_sum,
            "weighted_srtm_elevation_m": weighted_dem_m,
            "weighted_era5land_native_elevation_m": weighted_era5_m,
            "era5land_minus_srtm_m": weighted_era5_m - weighted_dem_m,
            "spatial_average_applied": False,
            "reason": "Los ocho puntos solo cubren una fracción de las ponderaciones de la Tarea 1; no se aplica promedio espacial.",
        }]
    ).to_csv(METADATA / "fao56_elevacion_y_ponderacion_1_1a.csv", index=False)

    daily_frames: list[pd.DataFrame] = []
    monthly_frames: list[pd.DataFrame] = []
    radiation_checks: list[dict] = []
    manual_checks: list[dict] = []
    for point, hourly in valid_hourly.items():
        latitude, longitude = EXPECTED[point]
        elevation_m = float(elevation_lookup[(round(latitude, 4), round(longitude, 4))])
        daily = fao56_daily(point, hourly, elevation_m, latitude)
        monthly = fao56_monthly_direct(daily)
        daily_frames.append(daily)
        monthly_frames.append(monthly)
        radiation_checks.append(
            {
                "point": point,
                "ssrd_step_type": "accum",
                "ssrd_hourly_min_j_m2": float(hourly["ssrd"].min()),
                "ssrd_hourly_max_j_m2": float(hourly["ssrd"].max()),
                "daily_rs_min_mj_m2_d": float(daily["rs_mj_m2_d"].min()),
                "daily_rs_max_mj_m2_d": float(daily["rs_mj_m2_d"].max()),
                "conversion": "sum(ssrd hourly) / 1,000,000",
            }
        )
        check = daily.iloc[0]
        radiative = 0.408 * check.delta_kpa_c * (check.rn_mj_m2_d - check.g_mj_m2_d)
        aerodynamic = (
            check.gamma_kpa_c * (900.0 / (check.tmean_c + 273.0)) * check.u2_ms
            * (check.es_kpa - check.ea_kpa)
        )
        denominator = check.delta_kpa_c + check.gamma_kpa_c * (1 + 0.34 * check.u2_ms)
        eto_recomputed = (radiative + aerodynamic) / denominator
        manual_checks.append(
            {
                "point": point,
                "date": check.date,
                "radiative_numerator_term": radiative,
                "aerodynamic_numerator_term": aerodynamic,
                "denominator": denominator,
                "eto_saved_mm_d": check.eto_fao56_mm_d,
                "eto_recomputed_mm_d": eto_recomputed,
                "absolute_difference": abs(check.eto_fao56_mm_d - eto_recomputed),
            }
        )

    if daily_frames:
        daily_all = pd.concat(daily_frames, ignore_index=True)
        monthly_all = pd.concat(monthly_frames, ignore_index=True)
        daily_all.to_csv(PROCESSED / "fao56_eto_diaria_por_punto_validado.csv", index=False)
        monthly_all.to_csv(PROCESSED / "fao56_eto_mensual_por_punto_validado.csv", index=False)
        pd.DataFrame(radiation_checks).to_csv(CHECKS / "fao56_comprobacion_ssrd_diaria.csv", index=False)
        pd.DataFrame(manual_checks).to_csv(CHECKS / "fao56_comprobacion_ecuacion.csv", index=False)
        comparable = monthly_all.dropna(subset=["difference_relative_pct"])
        summary_rows = []
        for point, group in comparable.groupby("point"):
            maximum_index = group["difference_direct_minus_daily_mm"].abs().idxmax()
            summary_rows.append(
                {
                    "point": point,
                    "months_compared": len(group),
                    "mean_abs_difference_mm": group["difference_direct_minus_daily_mm"].abs().mean(),
                    "max_abs_difference_mm": group["difference_direct_minus_daily_mm"].abs().max(),
                    "month_max_abs_difference": group.loc[maximum_index, "month"].strftime("%Y-%m"),
                }
            )
        monthly_summary = pd.DataFrame(summary_rows)
        monthly_summary.to_csv(TABLES / "fao56_resumen_diferencia_diaria_vs_mensual.csv", index=False)
        write_figure(monthly_all)
    else:
        daily_all = pd.DataFrame()
        monthly_all = pd.DataFrame()

    valid_points = ", ".join(sorted(valid_hourly)) or "ninguno"
    blocked = availability.loc[availability.status != "validado_para_fao56", ["point", "issues"]]
    if blocked.empty:
        pending_text = (
            "- Los ocho puntos de esta selección están completos; aún falta una ETo espacialmente representativa de la cuenca.\n"
            "- Antes de 1.1.b debe definirse una ponderación que represente las 33 celdas ERA5-Land de la Tarea 1."
        )
        next_step = "Definir la ponderación espacial y después desarrollar 1.1.b (pruebas independientes de la referencia FAO-56)."
    else:
        pending_text = (
            "- Hay puntos bloqueados: " + blocked.to_dict(orient="records").__repr__() + "\n"
            "- Antes de 1.1.b deben repararse esos insumos y volver a ejecutar este script."
        )
        next_step = "Reparar los insumos bloqueados y repetir 1.1.a antes de desarrollar 1.1.b."
    decision_text = f"""# Fuentes y decisiones - apartado 1.1.a

## Insumos

- ERA5-Land horario en ocho puntos, leído directamente desde los ZIP originales.
- Periodo solicitado y verificado cuando el punto está completo: 1981-01-01 00:00 a 2023-08-31 23:00 UTC.
- Delimitación y elevación SRTM reutilizadas de la Tarea 1. La elevación por punto es la media SRTM de la porción de celda ERA5-Land dentro de la cuenca.
- La Tarea 1 identificó {len(elevation)} celdas ERA5-Land que intersectan la cuenca. La elevación media ponderada SRTM es {weighted_dem_m:.2f} m, frente a {weighted_era5_m:.2f} m en la orografía nativa ERA5-Land (diferencia {weighted_era5_m - weighted_dem_m:.2f} m).

## Decisiones de cálculo

- La agregación diaria se hace en `UTC-05:00` fijo (hora estándar de Perú) y solo conserva días locales con 24 horas. Se evita una zona horaria histórica con cambios de horario que produciría artificialmente días de 23 o 25 horas.
- `t2m` y `d2m`: K a °C restando 273.15; `sp`: Pa a kPa dividiendo entre 1000.
- La magnitud del viento se calcula cada hora como `sqrt(u10^2 + v10^2)` y luego se promedia. Se transforma de 10 m a 2 m con la ecuación 47 de FAO-56.
- `ssrd` es una acumulación horaria en J m-2; para `Rs` diario se suman las 24 horas y se divide entre 1,000,000 para obtener MJ m-2 d-1.
- `Rn` es la radiación neta del pasto de referencia: Rns usa albedo 0.23 y Rnl usa la ecuación FAO-56. No se usa como Rn la radiación neta de la superficie real de ERA5-Land.
- En escala diaria se usa G = 0. Para el cálculo directo mensual se usa G_i = 0.07(T siguiente - T previa); enero de 1981 y agosto de 2023 quedan sin cálculo directo mensual por no tener meses vecinos a ambos lados.

## Limitación espacial

No se calcula una ETo promedio de cuenca: las ocho ubicaciones seleccionadas equivalen a solo {selected_weight_sum:.3f} de la ponderación de intersección de las {len(elevation)} celdas de la Tarea 1. Los productos contienen únicamente resultados por punto validado; hace falta definir una ponderación representativa antes de estimar la ETo de cuenca.

## Estado de los puntos

- Validados para cálculo: {valid_points}.
- Bloqueados: {blocked.to_dict(orient='records')}.
"""
    (METADATA / "fuentes_y_decisiones_1_1a.md").write_text(decision_text, encoding="utf-8")

    tracking = f"""# Seguimiento - Tarea 2, Punto 1, apartado 1.1.a

## Completado en esta ejecución

- Auditoría de ZIP y NetCDF, incluyendo continuidad temporal, coordenadas, variables, unidades y valores no finitos.
- Procesamiento FAO-56 por punto para los puntos completos: {valid_points}.
- Series diarias y mensuales, comprobación de radiación, comprobación algebraica de la ecuación y figura de comparación diaria/mensual.

## Resultados reproducibles creados

- `datos/punto1/procesados/1_1_a_fao56/fao56_eto_diaria_por_punto_validado.csv`
- `datos/punto1/procesados/1_1_a_fao56/fao56_eto_mensual_por_punto_validado.csv`
- `datos/punto1/metadatos/era5land_disponibilidad_1_1a.csv`
- `datos/punto1/metadatos/era5land_fuentes_sha256_1_1a.csv`
- `datos/punto1/metadatos/era5land_variables_unidades_1_1a.csv`
- `productos/punto1/1_1_demanda_atmosferica/tablas/fao56_resumen_diferencia_diaria_vs_mensual.csv`
- `productos/punto1/1_1_demanda_atmosferica/figuras/fao56_comparacion_diaria_vs_mensual_por_punto.png`
- `productos/punto1/1_1_demanda_atmosferica/comprobaciones/` (dos comprobaciones CSV).

## Limitaciones y decisiones pendientes

- No hay ETo espacialmente promediada para Racarumi: antes debe resolverse una ponderación espacial válida.
{pending_text}
- La comparación de producto/estación independiente pertenece a 1.1.b y no se realizó aquí.

## Próximo apartado

{next_step}
"""
    (ANNEXES / "seguimiento_1_1a.md").write_text(tracking, encoding="utf-8")
    print(json.dumps({
        "valid_points": sorted(valid_hourly),
        "blocked_points": availability.loc[availability.status != "validado_para_fao56", "point"].tolist(),
        "daily_rows": int(len(daily_all)),
        "monthly_rows": int(len(monthly_all)),
        "output_root": str(TASK),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
