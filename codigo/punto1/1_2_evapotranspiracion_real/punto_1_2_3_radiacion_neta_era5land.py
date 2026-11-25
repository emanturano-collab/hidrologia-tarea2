"""Descarga y procesa la radiacion neta real ERA5-Land para Racarumi.

No lee ni registra credenciales: cdsapi las obtiene desde la configuracion local
del usuario. El producto mensual ordinario no se usa entre 2022-09 y 2023-08,
porque ECMWF documento valores incorrectos para los campos acumulados en ese
periodo. Esos meses se recuperan con el producto mensual por hora a las 00 UTC.
"""

from __future__ import annotations

import calendar
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import cdsapi
import numpy as np
import xarray as xr


ROOT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
DATA_DIR = ROOT / "datos" / "punto1"
PRODUCT_DIR = ROOT / "productos" / "punto1"
RAW_DIR = DATA_DIR / "era5land_radiacion_raw"
CATCHMENT = DATA_DIR / "PE_200907_catchment_T1_original.gpkg"
WEIGHTS_FILE = DATA_DIR / "PE_200907_ERA5Land_grid_weights_T1_original.csv"
DATASET = "reanalysis-era5-land-monthly-means"
LAMBDA_J_KG = 2.45e6
AREA = [-6.2, -79.472, -7.068, -78.477]  # norte, oeste, sur, este; igual a Tarea 1


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_weights(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as stream:
        weights = [{key: float(value) for key, value in row.items()} for row in csv.DictReader(stream)]
    if len(weights) != 33:
        raise ValueError(f"Se esperaban 33 celdas de la Tarea 1; se obtuvieron {len(weights)}.")
    total = sum(row["spatial_weight"] for row in weights)
    if not np.isclose(total, 1.0, atol=1e-12):
        raise ValueError(f"Los pesos espaciales deben sumar 1; suman {total}.")
    return weights


def retrieve(client: cdsapi.Client, filename: str, product_type: str, years: list[str], months: list[str]) -> Path:
    target = RAW_DIR / filename
    if target.exists() and target.stat().st_size > 0:
        print(f"Se reutiliza descarga existente: {target.name}")
        return target
    request = {
        "product_type": [product_type],
        "variable": ["surface_net_solar_radiation", "surface_net_thermal_radiation"],
        "year": years,
        "month": months,
        "time": ["00:00"],
        "area": AREA,
        "data_format": "netcdf",
        "download_format": "unarchived",
    }
    print(f"Solicitando {target.name} a CDS")
    client.retrieve(DATASET, request, str(target))
    return target


def coordinate_name(dataset: xr.Dataset, candidates: tuple[str, ...]) -> str:
    for candidate in candidates:
        if candidate in dataset.coords or candidate in dataset.variables:
            return candidate
    raise KeyError(f"No se encontro ninguna coordenada entre {candidates}.")


def index_for_coordinate(values: np.ndarray, expected: float) -> int:
    index = int(np.argmin(np.abs(values - expected)))
    if not np.isclose(values[index], expected, atol=1e-6):
        raise ValueError(f"No existe la celda esperada {expected}; valor mas cercano {values[index]}.")
    return index


def raw_to_daily_energy(value: float, product_type: str) -> float:
    """Devuelve energia diaria media en J m-2.

    En ``monthly_averaged_reanalysis`` (moda), las acumulaciones se expresan
    como media diaria, con unidad J m-2 day-1. En la recuperacion oficial
    ``monthly_averaged_reanalysis_by_hour_of_day`` a 00 UTC, el valor
    corresponde a la acumulacion diaria de 24 h que termina a las 00 UTC,
    con unidad J m-2. Ambos representan una energia diaria media y se
    multiplican por los dias del mes posteriormente.
    """
    if product_type not in {"monthly_averaged_reanalysis", "monthly_averaged_reanalysis_by_hour_of_day"}:
        raise ValueError(f"Tipo de producto no esperado: {product_type}")
    return value


def process_file(path: Path, product_type: str, weights: list[dict]) -> list[dict]:
    with xr.open_dataset(path) as dataset:
        lat_name = coordinate_name(dataset, ("latitude", "lat"))
        lon_name = coordinate_name(dataset, ("longitude", "lon"))
        time_name = coordinate_name(dataset, ("valid_time", "time"))
        for variable in ("ssr", "str"):
            if variable not in dataset.data_vars:
                raise KeyError(f"No se encontro {variable} en {path.name}: {list(dataset.data_vars)}")
        latitude = np.asarray(dataset[lat_name].values, dtype=float)
        longitude = np.asarray(dataset[lon_name].values, dtype=float)
        ssr = dataset["ssr"].transpose(time_name, lat_name, lon_name)
        str_ = dataset["str"].transpose(time_name, lat_name, lon_name)
        ssr_values = np.asarray(ssr.values, dtype=float)
        str_values = np.asarray(str_.values, dtype=float)
        ssr_units = ssr.attrs.get("units", "")
        str_units = str_.attrs.get("units", "")
        timestamps = np.asarray(dataset[time_name].values)

    cell_indices = [
        (index_for_coordinate(latitude, row["latitude"]), index_for_coordinate(longitude, row["longitude"]))
        for row in weights
    ]
    rows = []
    for time_index, timestamp in enumerate(timestamps):
        month = np.datetime_as_string(timestamp, unit="D")[:7]
        year, month_number = map(int, month.split("-"))
        days = calendar.monthrange(year, month_number)[1]
        solar_cells = np.array([ssr_values[time_index, lat_index, lon_index] for lat_index, lon_index in cell_indices])
        thermal_cells = np.array([str_values[time_index, lat_index, lon_index] for lat_index, lon_index in cell_indices])
        valid = np.isfinite(solar_cells) & np.isfinite(thermal_cells)
        weight_covered = sum(row["spatial_weight"] for row, is_valid in zip(weights, valid) if is_valid)
        if not valid.all():
            solar_daily = thermal_daily = np.nan
        else:
            solar_daily = raw_to_daily_energy(float(sum(value * row["spatial_weight"] for value, row in zip(solar_cells, weights))), product_type)
            thermal_daily = raw_to_daily_energy(float(sum(value * row["spatial_weight"] for value, row in zip(thermal_cells, weights))), product_type)
        net_daily = solar_daily + thermal_daily
        solar_month = solar_daily * days
        thermal_month = thermal_daily * days
        net_month = net_daily * days
        rows.append({
            "month": month,
            "source_product_type": product_type,
            "days_in_month": days,
            "ssr_source_units": ssr_units,
            "str_source_units": str_units,
            "ssr_daily_energy_j_m2": solar_daily,
            "str_daily_energy_j_m2": thermal_daily,
            "rn_daily_energy_j_m2": net_daily,
            "ssr_monthly_energy_j_m2": solar_month,
            "str_monthly_energy_j_m2": thermal_month,
            "rn_monthly_energy_j_m2": net_month,
            "energy_equivalent_mm_month": net_month / LAMBDA_J_KG,
            "valid_grid_cells": int(valid.sum()),
            "intersecting_grid_cells": len(weights),
            "spatial_weight_covered_pct": 100.0 * weight_covered,
            "complete": bool(valid.all()),
        })
    return rows


def main() -> None:
    if not CATCHMENT.exists() or not WEIGHTS_FILE.exists():
        raise FileNotFoundError("Falta la delimitacion o los pesos reutilizados de la Tarea 1.")
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PRODUCT_DIR.mkdir(parents=True, exist_ok=True)
    weights = read_weights(WEIGHTS_FILE)
    # Limite explicito para incidencias transitorias de red: conserva las
    # descargas validas y evita reintentos indefinidos. Cada archivo existente
    # y no vacio se reutiliza en ``retrieve`` sin enviar una nueva solicitud.
    client = cdsapi.Client(wait_until_complete=True, retry_max=5, sleep_max=30)

    # Meses no afectados: septiembre de 2000 a agosto de 2022.
    raw_files = [
        (retrieve(client, "era5land_radiation_moda_2000_09_12.nc", "monthly_averaged_reanalysis", ["2000"], ["09", "10", "11", "12"]), "monthly_averaged_reanalysis"),
        (retrieve(client, "era5land_radiation_moda_2001_2021.nc", "monthly_averaged_reanalysis", [str(year) for year in range(2001, 2022)], [f"{month:02d}" for month in range(1, 13)]), "monthly_averaged_reanalysis"),
        (retrieve(client, "era5land_radiation_moda_2022_01_08.nc", "monthly_averaged_reanalysis", ["2022"], [f"{month:02d}" for month in range(1, 9)]), "monthly_averaged_reanalysis"),
        # Solucion oficial de ECMWF para meses acumulados afectados.
        (retrieve(client, "era5land_radiation_mnth00_2022_09_12.nc", "monthly_averaged_reanalysis_by_hour_of_day", ["2022"], ["09", "10", "11", "12"]), "monthly_averaged_reanalysis_by_hour_of_day"),
        (retrieve(client, "era5land_radiation_mnth00_2023_01_08.nc", "monthly_averaged_reanalysis_by_hour_of_day", ["2023"], [f"{month:02d}" for month in range(1, 9)]), "monthly_averaged_reanalysis_by_hour_of_day"),
    ]

    monthly = []
    for raw_file, product_type in raw_files:
        monthly.extend(process_file(raw_file, product_type, weights))
    monthly = sorted((row for row in monthly if "2000-09" <= row["month"] <= "2023-08"), key=lambda row: row["month"])
    if len(monthly) != 276 or len({row["month"] for row in monthly}) != 276:
        raise RuntimeError(f"Se esperaban 276 meses unicos entre 2000-09 y 2023-08; se obtuvieron {len(monthly)}.")
    if any(not row["complete"] for row in monthly):
        raise RuntimeError("Hay meses con celdas faltantes; no se escriben resultados parciales.")

    output = PRODUCT_DIR / "punto_1_2_3_radiacion_neta_real_era5land_mensual.csv"
    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(monthly[0]))
        writer.writeheader()
        writer.writerows(monthly)
    check_month = next(row for row in monthly if row["month"] == "2021-09")
    check = {
        "month": check_month["month"],
        "formula_net_energy": "rn_monthly_energy_j_m2 = ssr_monthly_energy_j_m2 + str_monthly_energy_j_m2",
        "formula_water_equivalent": "energy_equivalent_mm_month = rn_monthly_energy_j_m2 / 2450000",
        "ssr_monthly_energy_j_m2": check_month["ssr_monthly_energy_j_m2"],
        "str_monthly_energy_j_m2": check_month["str_monthly_energy_j_m2"],
        "rn_monthly_energy_j_m2": check_month["rn_monthly_energy_j_m2"],
        "energy_equivalent_mm_month": check_month["energy_equivalent_mm_month"],
        "identity_error_j_m2": check_month["rn_monthly_energy_j_m2"] - check_month["ssr_monthly_energy_j_m2"] - check_month["str_monthly_energy_j_m2"],
    }
    (PRODUCT_DIR / "punto_1_2_3_verificacion_manual.json").write_text(json.dumps(check, indent=2), encoding="utf-8")
    metadata = {
        "dataset": DATASET,
        "variables": {"ssr": "surface_net_solar_radiation", "str": "surface_net_thermal_radiation"},
        "period": "2000-09 through 2023-08",
        "spatial_resolution": "0.1 degree CDS regular lat-lon grid; native ERA5-Land about 9 km",
        "spatial_weights": {"file": WEIGHTS_FILE.name, "cells": len(weights), "sum": sum(row["spatial_weight"] for row in weights), "method": "Reused exactly from Tarea 1: 0.005-degree subgrid fractional coverage and cos(latitude) area adjustment."},
        "affected_months_solution": "2022-09 through 2023-08 use monthly_averaged_reanalysis_by_hour_of_day at 00:00, the official ECMWF recovery method for erroneous accumulated monthly fields.",
        "sign_convention": "ECMWF native signs retained: Rn = ssr + str. No FAO-56 reference-grass radiation is used.",
        "energy_to_water_conversion": {"lambda_j_kg": LAMBDA_J_KG, "equivalence": "1 kg m-2 = 1 mm"},
        "catchment_file_sha256": sha256(CATCHMENT),
        "weights_file_sha256": sha256(WEIGHTS_FILE),
        "raw_files": [path.name for path, _ in raw_files],
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    (DATA_DIR / "punto_1_2_3_era5land_radiacion_fuente.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(output), "months": len(monthly), "manual_check": str(PRODUCT_DIR / "punto_1_2_3_verificacion_manual.json")}, indent=2))


if __name__ == "__main__":
    main()
