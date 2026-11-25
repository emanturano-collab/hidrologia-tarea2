"""Valida GLEAM4.3a mensual y calcula ET areal de Racarumi PE_200907."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
from shapely.geometry import box

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
RAW = ROOT / "datos" / "punto1" / "gleam4_3a_raw"
TRANSFER_TMP = RAW / "openssh_transfer_tmp"
INV = ROOT / "datos" / "punto1" / "gleam4_3a_sftp_inventory.json"
GPKG = ROOT / "datos" / "punto1" / "PE_200907_catchment_T1_original.gpkg"
WEIGHTS = ROOT / "datos" / "punto1" / "PE_200907_GLEAM_grid_weights.csv"
OUT = ROOT / "productos" / "punto1"

spec = importlib.util.spec_from_file_location("gleam_download", Path(__file__).with_name("descargar_gleam43a_mensual.py"))
validator = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(validator)


def filename(year: int) -> str:
    return f"E_{year}_GLEAM_v4.3a_MO.nc"


def inventory_sizes() -> dict[int, int]:
    data = json.loads(INV.read_text(encoding="utf-8"))
    result = {}
    for item in data["relevant_entries"]:
        for year in range(2001, 2024):
            if item["path"].endswith(filename(year)):
                result[year] = int(item["size_bytes"])
    if set(result) != set(range(2001, 2024)):
        raise ValueError("El inventario no contiene exactamente los tamanos de 2001--2023")
    return result


def validate_one(path: Path, year: int, expected: int) -> dict:
    actual = path.stat().st_size
    if actual != expected:
        raise ValueError(f"{path}: {actual} bytes; inventario espera {expected}")
    metadata = validator.validate(path, year)
    return {"year": year, "file": filename(year), "bytes": actual,
            "sha256": validator.sha256(path), "metadata": metadata}


def validate_and_promote() -> None:
    sizes = inventory_sizes()
    checkpoint_path = RAW / "validacion_transfer_checkpoint.json"
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8")) if checkpoint_path.exists() else {}
    entries = []
    # 2001 solo se lee y valida; nunca se mueve ni se reemplaza.
    entries.append(validate_one(RAW / filename(2001), 2001, sizes[2001]))
    staged = []
    for year in range(2002, 2024):
        source = TRANSFER_TMP / filename(year)
        target = RAW / filename(year)
        if target.exists():
            entries.append(validate_one(target, year, sizes[year]))
        else:
            if not source.exists():
                raise FileNotFoundError(f"Falta archivo de transferencia: {source}")
            saved = checkpoint.get(str(year))
            stat = source.stat()
            if saved and saved.get("bytes") == stat.st_size and saved.get("mtime_ns") == stat.st_mtime_ns:
                entry = saved["entry"]
                print(f"REUTILIZADA_VALIDACION {year}: {entry['sha256']}")
            else:
                entry = validate_one(source, year, sizes[year])
                checkpoint[str(year)] = {"bytes": stat.st_size, "mtime_ns": stat.st_mtime_ns, "entry": entry}
                checkpoint_path.write_text(json.dumps(checkpoint, indent=2), encoding="utf-8")
            entries.append(entry)
            staged.append((source, target))
        print(f"VALIDADO {year}: {entries[-1]['sha256']}")
    # Ningun archivo se incorpora hasta que los 23 superan todas las pruebas.
    for source, target in staged:
        if target.exists():
            raise FileExistsError(f"Se rehusa sobrescribir {target}")
        source.replace(target)
    manifest = {"source": "GLEAM4.3a monthly E", "units": "mm.month-1",
                "credentials_stored": False, "files": entries}
    (RAW / "manifest_gleam43a_E.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"PROMOVIDOS={len(staged)}; ARCHIVOS_VALIDOS={len(entries)}")


def make_weights() -> pd.DataFrame:
    basin = gpd.read_file(GPKG).to_crs(4326).geometry.union_all()
    if basin.is_empty or not basin.is_valid:
        raise ValueError("La delimitacion original de Racarumi es invalida")
    with xr.open_dataset(RAW / filename(2001), mask_and_scale=False) as ds:
        lat = ds.lat.values
        lon = ds.lon.values
    minx, miny, maxx, maxy = basin.bounds
    lat_idx = np.where((lat + 0.05 >= miny) & (lat - 0.05 <= maxy))[0]
    lon_idx = np.where((lon + 0.05 >= minx) & (lon - 0.05 <= maxx))[0]
    rows = []
    basin_ea = gpd.GeoSeries([basin], crs=4326).to_crs(6933).iloc[0]
    for i in lat_idx:
        for j in lon_idx:
            cell = box(float(lon[j] - 0.05), float(lat[i] - 0.05),
                       float(lon[j] + 0.05), float(lat[i] + 0.05))
            cell_ea = gpd.GeoSeries([cell], crs=4326).to_crs(6933).iloc[0]
            area = basin_ea.intersection(cell_ea).area
            if area > 0:
                rows.append({"lat_index": int(i), "lon_index": int(j),
                             "lat_center": float(lat[i]), "lon_center": float(lon[j]),
                             "intersection_area_m2": float(area)})
    weights = pd.DataFrame(rows)
    weights["weight"] = weights.intersection_area_m2 / weights.intersection_area_m2.sum()
    weights.to_csv(WEIGHTS, index=False)
    if abs(weights.weight.sum() - 1) > 1e-12:
        raise ValueError("Los pesos espaciales GLEAM no suman 1")
    return weights


def wanted_month(d: pd.Timestamp) -> bool:
    return (pd.Timestamp("2001-09-01") <= d < pd.Timestamp("2002-09-01") or
            pd.Timestamp("2003-09-01") <= d < pd.Timestamp("2023-09-01"))


def hydro_year(d: pd.Timestamp) -> int:
    return d.year + 1 if d.month >= 9 else d.year


def process() -> None:
    for year in range(2001, 2024):
        if not (RAW / filename(year)).exists():
            raise FileNotFoundError(f"Falta archivo validado {filename(year)}")
    weights = make_weights()
    ii = weights.lat_index.to_numpy(dtype=int)
    jj = weights.lon_index.to_numpy(dtype=int)
    ww = weights.weight.to_numpy(dtype=float)
    monthly = []
    for year in range(2001, 2024):
        with xr.open_dataset(RAW / filename(year), mask_and_scale=False) as ds:
            if ds.E.attrs.get("units") != "mm.month-1":
                raise ValueError(f"{filename(year)}: unidad cambiada")
            for k, raw_time in enumerate(ds.time.values):
                d = pd.Timestamp(raw_time).to_period("M").to_timestamp()
                if not wanted_month(d):
                    continue
                values = ds.E.isel(time=k).values[ii, jj].astype(float)
                valid = np.isfinite(values) & (values != -999)
                coverage = float(ww[valid].sum() * 100)
                if coverage < 95:
                    raise ValueError(f"{d:%Y-%m}: cobertura GLEAM {coverage:.3f}% < 95%")
                et = float(np.sum(values[valid] * ww[valid]) / ww[valid].sum())
                monthly.append({"month": d.strftime("%Y-%m-01"),
                                "hydrological_year": hydro_year(d),
                                "et_gleam_mm_month": et,
                                "valid_spatial_coverage_percent": coverage,
                                "valid_cells": int(valid.sum()),
                                "intersecting_cells": int(len(weights)),
                                "negative_cells": int(np.count_nonzero(values[valid] < 0)),
                                "units": "mm/month"})
    m = pd.DataFrame(monthly).sort_values("month").reset_index(drop=True)
    if len(m) != 252 or m.month.nunique() != 252:
        raise ValueError(f"Se esperaban 252 meses unicos y se obtuvieron {len(m)}")
    expected_hy = [2002] + list(range(2004, 2024))
    if sorted(m.hydrological_year.unique()) != expected_hy:
        raise ValueError("Los anos hidrologicos GLEAM no coinciden con el balance")
    a = m.groupby("hydrological_year", as_index=False).agg(
        months=("month", "count"), et_gleam_mm_year=("et_gleam_mm_month", "sum"),
        minimum_spatial_coverage_percent=("valid_spatial_coverage_percent", "min"),
        months_with_negative_cells=("negative_cells", lambda x: int(np.count_nonzero(np.asarray(x) > 0))))
    if len(a) != 21 or not (a.months == 12).all():
        raise ValueError("No se formaron exactamente 21 anos hidrologicos completos")
    OUT.mkdir(parents=True, exist_ok=True)
    m.to_csv(OUT / "punto_1_2_4_gleam_et_mensual.csv", index=False)
    a.to_csv(OUT / "punto_1_2_4_gleam_et_anual_hidrologico.csv", index=False)

    mod = pd.read_csv(OUT / "punto_1_2_4_mod16_et_anual_hidrologico.csv")
    bal = pd.read_csv(OUT / "punto_1_2_anios_hidrologicos_sep_ago.csv")
    bal["hydrological_year_num"] = bal.hydrological_year.str.extract(r"(\d{4})").astype(int)
    bal = bal[(bal.status == "Completo") & bal.hydrological_year_num.isin(expected_hy)]
    cmp = a.merge(mod[["hydrological_year", "et_mod16_mm_year"]], on="hydrological_year", validate="one_to_one")
    cmp = cmp.merge(bal[["hydrological_year_num", "et_l_mm_year", "et_i_mm_year"]],
                    left_on="hydrological_year", right_on="hydrological_year_num", validate="one_to_one").drop(columns="hydrological_year_num")
    for col in ["et_mod16_mm_year", "et_l_mm_year", "et_i_mm_year"]:
        cmp[f"gleam_minus_{col}"] = cmp.et_gleam_mm_year - cmp[col]
    cmp.to_csv(OUT / "punto_1_2_4_comparacion_anual_productos_y_balance.csv", index=False)
    summary = pd.DataFrame([
        {"series": "GLEAM4.3a", "mean_mm_year": cmp.et_gleam_mm_year.mean()},
        {"series": "MOD16A2GF v6.1", "mean_mm_year": cmp.et_mod16_mm_year.mean()},
        {"series": "ET=PISCOp-Q", "mean_mm_year": cmp.et_l_mm_year.mean()},
        {"series": "ET=IMERG-Q", "mean_mm_year": cmp.et_i_mm_year.mean()}])
    summary["same_hydrological_years"] = "AH2002; AH2004-AH2023"
    summary.to_csv(OUT / "punto_1_2_4_comparacion_multianual.csv", index=False)
    qa = {"files_validated": 23, "monthly_records": int(len(m)), "hydrological_years": expected_hy,
          "grid_resolution_degrees": 0.1, "intersecting_cells": int(len(weights)),
          "weights_sum": float(weights.weight.sum()),
          "intersection_area_m2": float(weights.intersection_area_m2.sum()),
          "minimum_spatial_coverage_percent": float(m.valid_spatial_coverage_percent.min()),
          "months_with_negative_cells": int(np.count_nonzero(m.negative_cells > 0)),
          "monthly_to_annual_max_abs_difference_mm": float((a.set_index("hydrological_year").et_gleam_mm_year - m.groupby("hydrological_year").et_gleam_mm_month.sum()).abs().max()),
          "gleam_mean_mm_year": float(summary.loc[summary.series == "GLEAM4.3a", "mean_mm_year"].iloc[0]),
          "note_balance": "P-Q es un balance de largo plazo sujeto al supuesto Delta S aproximadamente cero."}
    (OUT / "punto_1_2_4_gleam_control_calidad.json").write_text(json.dumps(qa, indent=2), encoding="utf-8")
    print(json.dumps(qa, indent=2))


ap = argparse.ArgumentParser()
ap.add_argument("action", choices=["validate-promote", "process"])
args = ap.parse_args()
validate_and_promote() if args.action == "validate-promote" else process()
