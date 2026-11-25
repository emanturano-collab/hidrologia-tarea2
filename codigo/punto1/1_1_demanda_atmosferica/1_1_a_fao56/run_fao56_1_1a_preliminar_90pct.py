"""FAO-56 provisional for 20 verified ERA5-Land cells (90.13 % coverage).

This is deliberately separate from the eight-point execution.  It is runnable
only after the twelve listed manual CDS ZIPs exist and pass validation.  It
never changes raw ZIPs or the 100 % final workflow.  The basin series is a
weight-normalised average over the covered 90.1264 % only, so it is explicitly
an interim estimate, never the final ETo of Racarumi.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from run_fao56_1_1a import (
    END_UTC,
    EXPECTED_HOURS,
    REQUIRED,
    START_UTC,
    fao56_daily,
    fao56_monthly_direct,
    read_zip_netcdf,
)


ROOT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
TASK = ROOT
RAW = TASK / "punto 1"
SUPPLEMENT = RAW / "ERA5_Land_Datos_Complementarios"
MANUAL = TASK / "datos" / "punto1" / "originales" / "era5land_cds_25_pendientes"
GRID = TASK / "productos" / "punto1" / "1_1_demanda_atmosferica" / "tablas" / "era5land_33_celdas_pesos_y_elevacion.csv"
OUT = TASK / "datos" / "punto1" / "procesados" / "1_1_a_fao56_preliminar_90pct"
META = TASK / "datos" / "punto1" / "metadatos"
TABLES = TASK / "productos" / "punto1" / "1_1_demanda_atmosferica" / "tablas"

EXISTING = {
    "P1": "ERA5L_10", "P2": "ERA5L_05", "P3": "ERA5L_02", "P4": "ERA5L_12",
    "P5": "ERA5L_14", "P6": "ERA5L_23", "P7": "ERA5L_27", "P8": "ERA5L_31",
}
STRATEGIC = [
    "ERA5L_13", "ERA5L_11", "ERA5L_20", "ERA5L_21", "ERA5L_22", "ERA5L_26",
    "ERA5L_06", "ERA5L_07", "ERA5L_28", "ERA5L_15", "ERA5L_25", "ERA5L_19",
]
EXPECTED_UNITS = {"t2m": "K", "d2m": "K", "sp": "Pa", "ssrd": "J m**-2", "u10": "m s**-1", "v10": "m s**-1"}


def source_paths(label: str) -> list[Path]:
    if label in EXISTING:
        paths = [RAW / f"datospunto1originalesERA5_Land_{label}.zip"]
        if label == "P2":
            paths.append(SUPPLEMENT / "ERA5_Land_P2_v10_FALTANTE.zip")
        if label == "P5":
            paths.append(SUPPLEMENT / "ERA5_Land_P5_ssrd_CORRECTO.zip")
        return paths
    return [MANUAL / f"ERA5_Land_{label}_19810101_20230831.zip"]


def load_validated(label: str, latitude: float, longitude: float) -> tuple[dict[str, pd.Series], list[dict]]:
    """Combine complementary ZIPs and reject any incomplete or incompatible source."""
    combined: dict[str, pd.Series] = {}
    audit: list[dict] = []
    for path in source_paths(label):
        if not path.exists():
            raise FileNotFoundError(f"Falta {path.name}")
        values, metadata, files = read_zip_netcdf(path)
        for entry in files:
            actual_lon = entry["longitude"] - 360 if entry["longitude"] > 180 else entry["longitude"]
            valid_time = (
                entry["records"] == EXPECTED_HOURS and entry["unique_timestamps"] == EXPECTED_HOURS
                and entry["start_utc"] == str(START_UTC) and entry["end_utc"] == str(END_UTC)
                and entry["nonhourly_intervals"] == 0
            )
            if not (np.isclose(entry["latitude"], latitude, atol=1e-6) and np.isclose(actual_lon, longitude, atol=1e-6) and valid_time):
                raise ValueError(f"{path.name}: coordenada, periodo o frecuencia incompatibles")
        for entry in metadata:
            if entry["units"] != EXPECTED_UNITS.get(entry["variable"], entry["units"]) or entry["missing_values"]:
                raise ValueError(f"{path.name}: unidad o faltantes no válidos para {entry['variable']}")
        for variable, series in values.items():
            if variable in combined:
                raise ValueError(f"{label}: variable duplicada {variable}")
            combined[variable] = series
        audit.append({"label": label, "zip": str(path.relative_to(ROOT)), "status": "validado"})
    if set(combined) != REQUIRED:
        raise ValueError(f"{label}: variables={sorted(combined)}; se requieren={sorted(REQUIRED)}")
    return combined, audit


def weighted_hourly(hourly_by_cell: dict[str, dict[str, pd.Series]], weights: pd.Series) -> dict[str, pd.Series]:
    """Average scalars and the hourly wind magnitude with normalised covered weights."""
    selected = list(weights.index)
    normalized = weights / weights.sum()
    output: dict[str, pd.Series] = {}
    for variable in ("t2m", "d2m", "sp", "ssrd"):
        frame = pd.concat({cell: hourly_by_cell[cell][variable] for cell in selected}, axis=1)
        output[variable] = frame.mul(normalized, axis=1).sum(axis=1, min_count=len(selected))
    speed = pd.concat(
        {cell: np.hypot(hourly_by_cell[cell]["u10"], hourly_by_cell[cell]["v10"]) for cell in selected}, axis=1
    )
    output["wind10_ms"] = speed.mul(normalized, axis=1).sum(axis=1, min_count=len(selected))
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--replace", action="store_true", help="Replace only this preliminary output after manual review.")
    args = parser.parse_args()
    grid = pd.read_csv(GRID).set_index("cell_id")
    selected = list(EXISTING.values()) + STRATEGIC
    if set(selected) - set(grid.index) or len(selected) != 20:
        raise ValueError("Selección espacial preliminar incompatible con el inventario de 33 celdas.")
    coverage = float(grid.loc[selected, "spatial_weight"].sum())
    if not np.isclose(coverage, 0.9012637836877098, atol=1e-12):
        raise ValueError(f"Cobertura inesperada: {coverage}")
    missing = [path.name for label in STRATEGIC for path in source_paths(label) if not path.exists()]
    if missing:
        print(json.dumps({"status": "PENDIENTE_DESCARGAS_MANUALES", "coverage": coverage, "missing_zip": missing}, ensure_ascii=False))
        return
    if OUT.exists() and any(OUT.iterdir()) and not args.replace:
        raise FileExistsError("Ya existen resultados preliminares; revise o use --replace explícitamente.")

    hourly_by_cell: dict[str, dict[str, pd.Series]] = {}
    audit_rows: list[dict] = []
    for label, cell in EXISTING.items():
        row = grid.loc[cell]
        hourly_by_cell[cell], audit = load_validated(label, float(row.latitude), float(row.longitude))
        audit_rows.extend(audit)
    for cell in STRATEGIC:
        row = grid.loc[cell]
        hourly_by_cell[cell], audit = load_validated(cell, float(row.latitude), float(row.longitude))
        audit_rows.extend(audit)

    OUT.mkdir(parents=True, exist_ok=True)
    weights = grid.loc[selected, "spatial_weight"]
    basin_elevation = float((grid.loc[selected, "dem_mean_elevation_m"] * weights).sum() / coverage)
    basin_latitude = float((grid.loc[selected, "latitude"] * weights).sum() / coverage)
    basin_hourly = weighted_hourly(hourly_by_cell, weights)
    basin_daily = fao56_daily("Racarumi_preliminar_90pct", basin_hourly, basin_elevation, basin_latitude)
    basin_monthly = fao56_monthly_direct(basin_daily)

    point_daily = []
    for cell in selected:
        row = grid.loc[cell]
        point_daily.append(fao56_daily(cell, hourly_by_cell[cell], float(row.dem_mean_elevation_m), float(row.latitude)))
    pd.concat(point_daily, ignore_index=True).to_csv(OUT / "fao56_eto_diaria_por_celda_preliminar_90pct.csv", index=False)
    basin_daily.to_csv(OUT / "fao56_eto_diaria_preliminar_90pct.csv", index=False)
    basin_monthly.to_csv(OUT / "fao56_eto_mensual_preliminar_90pct.csv", index=False)
    pd.DataFrame(audit_rows).to_csv(META / "fao56_preliminar_90pct_fuentes_validadas.csv", index=False)
    pd.DataFrame([{
        "scope": "PRELIMINAR_NO_FINAL", "cells_used": len(selected), "cells_pending": 13,
        "weight_covered": coverage, "weight_pending": 1 - coverage,
        "spatial_method": "Variables horarias ponderadas y normalizadas sobre cobertura disponible; magnitud de viento formada por celda antes de ponderar.",
        "limitation": "No representa el 100 % de la ponderación de Tarea 1; no reportar como ETo definitiva de Racarumi.",
    }]).to_csv(META / "fao56_preliminar_90pct_cobertura_y_limitacion.csv", index=False)
    basin_monthly[["month", "eto_from_daily_mm", "eto_monthly_direct_mm", "difference_direct_minus_daily_mm", "difference_relative_pct"]].to_csv(TABLES / "fao56_preliminar_90pct_resumen_mensual.csv", index=False)
    print(json.dumps({"status": "CALCULADO_PRELIMINAR", "coverage": coverage, "daily_rows": len(basin_daily), "monthly_rows": len(basin_monthly)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
