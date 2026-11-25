"""Controlled CDS download and validation for Racarumi's 25 missing ERA5-Land cells.

This program never touches the original P1--P8 ZIP archives.  Its default
mode is a safe preflight that creates/updates a reproducible manifest only.
Network requests require BOTH ``--download`` and a valid user-managed CDS
configuration.  Start with ``--trial ERA5L_01 --download``; do not start the
remaining cells until the resulting ZIP is marked VALIDADA.

CDS dataset/request schema (checked 2026-11-21):
``reanalysis-era5-land-timeseries`` with ``variable``, ``location``, ``date``
and ``data_format``.  The time-series product chooses the nearest 0.1-degree
grid point and returns hourly data.  Radiation is requested specifically as
surface_solar_radiation_downwards, not thermal radiation.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import time
import zipfile

import numpy as np
import pandas as pd
import xarray as xr


ROOT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
TASK = ROOT
PENDING_CSV = TASK / "datos" / "punto1" / "metadatos" / "era5land_25_celdas_pendientes_CDS.csv"
RAW_OUTPUT = TASK / "datos" / "punto1" / "originales" / "era5land_cds_25_pendientes"
MANIFEST = TASK / "datos" / "punto1" / "metadatos" / "era5land_25_celdas_manifest.csv"
REQUEST_LOG = TASK / "datos" / "punto1" / "metadatos" / "era5land_25_celdas_solicitudes.jsonl"

DATASET = "reanalysis-era5-land-timeseries"
START = pd.Timestamp("1981-01-01 00:00:00")
END = pd.Timestamp("2023-08-31 23:00:00")
EXPECTED_HOURS = len(pd.date_range(START, END, freq="h"))
VARIABLES = [
    "2m_temperature",
    "2m_dewpoint_temperature",
    "surface_pressure",
    "surface_solar_radiation_downwards",
    "10m_u_component_of_wind",
    "10m_v_component_of_wind",
]
EXPECTED_SHORT = {"t2m", "d2m", "sp", "ssrd", "u10", "v10"}
EXPECTED_UNITS = {
    "t2m": "K", "d2m": "K", "sp": "Pa", "ssrd": "J m**-2",
    "u10": "m s**-1", "v10": "m s**-1",
}


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def digest(path: Path) -> str:
    hasher = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def cds_configuration_status() -> tuple[bool, str]:
    """Return status only; never read or print the contents of .cdsapirc."""
    config = Path.home() / ".cdsapirc"
    if not config.is_file() or config.stat().st_size == 0:
        return False, "No existe un archivo .cdsapirc no vacío en el perfil de Windows."
    try:
        import cdsapi  # noqa: F401
    except ImportError:
        return False, "El archivo .cdsapirc existe, pero el paquete cdsapi no está instalado."
    return True, "Se detectaron cdsapi y .cdsapirc; la licencia del conjunto aún se confirma al enviar la prueba."


def validate_input(frame: pd.DataFrame) -> None:
    required = {"cell_id", "latitude", "longitude", "spatial_weight", "dataset", "period_start_utc", "period_end_utc"}
    absent = required - set(frame.columns)
    if absent or len(frame) != 25 or not frame["cell_id"].is_unique:
        raise ValueError(f"CSV de celdas pendientes inválido; columnas ausentes={sorted(absent)}, filas={len(frame)}")
    if frame[["latitude", "longitude"]].duplicated().any():
        raise ValueError("CSV inválido: hay coordenadas repetidas.")
    if not (frame["dataset"] == DATASET).all():
        raise ValueError("CSV inválido: dataset diferente a reanalysis-era5-land-timeseries.")
    if not ((frame["period_start_utc"] == "1981-01-01 00:00") & (frame["period_end_utc"] == "2023-08-31 23:00")).all():
        raise ValueError("CSV inválido: periodo distinto al aprobado.")


def filename(row: pd.Series) -> str:
    return f"ERA5_Land_{row.cell_id}_19810101_20230831.zip"


def request_for(row: pd.Series) -> dict:
    return {
        "variable": VARIABLES,
        "location": {"latitude": float(row.latitude), "longitude": float(row.longitude)},
        "date": "1981-01-01/2023-08-31",
        "data_format": "netcdf",
    }


def validate_zip(path: Path, requested_lat: float, requested_lon: float) -> dict:
    """Read ZIP in memory and validate all six variables, time and coordinates."""
    result = {"status": "INCOMPLETA", "error": "", "netcdf_files": 0, "records": 0,
              "returned_latitude": "", "returned_longitude": "", "variables": "", "sha256": ""}
    try:
        with zipfile.ZipFile(path) as archive:
            broken = archive.testzip()
            if broken:
                raise ValueError(f"ZIP corrupto: miembro dañado {broken}")
            members = [member for member in archive.namelist() if member.lower().endswith(".nc")]
            if not members:
                raise ValueError("ZIP sin archivos NetCDF")
            collected, units, times, coordinates, missing = set(), {}, [], [], {}
            for member in members:
                dataset = xr.open_dataset(BytesIO(archive.read(member)), engine="h5netcdf", decode_times=True)
                try:
                    time_name = "valid_time" if "valid_time" in dataset.coords else "time"
                    if time_name not in dataset.coords:
                        raise ValueError(f"{member}: no tiene coordenada temporal")
                    index = pd.DatetimeIndex(pd.to_datetime(dataset[time_name].values))
                    times.append(index)
                    coordinates.append((float(dataset.latitude.values), float(dataset.longitude.values)))
                    for variable in dataset.data_vars:
                        values = np.asarray(dataset[variable].values, dtype=float)
                        collected.add(variable)
                        units[variable] = str(dataset[variable].attrs.get("units", ""))
                        missing[variable] = int(np.count_nonzero(~np.isfinite(values)))
                finally:
                    dataset.close()
        if collected != EXPECTED_SHORT:
            raise ValueError(f"variables halladas={sorted(collected)}; requeridas={sorted(EXPECTED_SHORT)}")
        if any(missing[var] for var in EXPECTED_SHORT):
            raise ValueError(f"valores no finitos={missing}")
        # A time-series ZIP groups variables into several NetCDF members.  Each
        # member legitimately has the same hourly time coordinate; validate it
        # member by member rather than treating those equal axes as duplicates.
        reference_time = times[0]
        for index in times:
            if len(index) != EXPECTED_HOURS or index[0] != START or index[-1] != END:
                raise ValueError(f"periodo/registros inválidos: {len(index)}, {index[0]} a {index[-1]}")
            if index.nunique() != EXPECTED_HOURS or not (np.diff(index.values).astype("timedelta64[h]") == np.timedelta64(1, "h")).all():
                raise ValueError("serie temporal no es horaria, continua y sin duplicados")
            if not index.equals(reference_time):
                raise ValueError("los ejes temporales difieren entre miembros NetCDF")
        if len(set(coordinates)) != 1:
            raise ValueError(f"coordenadas distintas entre NetCDF: {coordinates}")
        actual_lat, actual_lon = coordinates[0]
        if actual_lon > 180:
            actual_lon -= 360
        # CDS may round to nearest 0.1-degree grid cell; exact equality is not required.
        if abs(actual_lat - requested_lat) > 0.051 or abs(actual_lon - requested_lon) > 0.051:
            raise ValueError(f"celda retornada ({actual_lat}, {actual_lon}) no corresponde a la ubicación solicitada")
        bad_units = {key: units[key] for key in EXPECTED_SHORT if units[key] != EXPECTED_UNITS[key]}
        if bad_units:
            raise ValueError(f"unidades inesperadas: {bad_units}")
        result.update(status="VALIDADA", netcdf_files=len(members), records=len(reference_time),
                      returned_latitude=actual_lat, returned_longitude=actual_lon,
                      variables=";".join(sorted(collected)), sha256=digest(path))
    except Exception as exc:  # Recorded in manifest; source data are never altered.
        result["error"] = str(exc)
    return result


def write_manifest(frame: pd.DataFrame, previous: dict[str, dict]) -> pd.DataFrame:
    rows = []
    for _, row in frame.iterrows():
        cell = row.cell_id
        target = RAW_OUTPUT / filename(row)
        record = dict(previous.get(cell, {}))
        base = {"cell_id": cell, "requested_latitude": float(row.latitude), "requested_longitude": float(row.longitude),
                "spatial_weight": float(row.spatial_weight), "filename": target.name,
                "dataset": DATASET, "period_start_utc": str(START), "period_end_utc": str(END)}
        if target.exists():
            base.update(validate_zip(target, float(row.latitude), float(row.longitude)))
            base["checked_utc"] = now()
        else:
            base.update({"status": record.get("status", "PENDIENTE"), "error": record.get("error", ""),
                         "netcdf_files": record.get("netcdf_files", 0), "records": record.get("records", 0),
                         "returned_latitude": record.get("returned_latitude", ""), "returned_longitude": record.get("returned_longitude", ""),
                         "variables": record.get("variables", ""), "sha256": record.get("sha256", ""), "checked_utc": now()})
        base["size_bytes"] = target.stat().st_size if target.exists() else 0
        rows.append(base)
    manifest = pd.DataFrame(rows)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    manifest.to_csv(MANIFEST, index=False, quoting=csv.QUOTE_MINIMAL)
    return manifest


def log(event: dict) -> None:
    with REQUEST_LOG.open("a", encoding="utf-8") as output:
        output.write(json.dumps({"utc": now(), **event}, ensure_ascii=False) + "\n")


def download_one(row: pd.Series, retries: int) -> None:
    import cdsapi
    RAW_OUTPUT.mkdir(parents=True, exist_ok=True)
    target = RAW_OUTPUT / filename(row)
    temporary = target.with_suffix(".part")
    if target.exists():
        return
    # Official current CDS initialization: credentials are read privately from
    # .cdsapirc, where ``key`` is the personal access token.  Limits are set
    # afterwards only to keep this controlled workflow from retrying for hours.
    client = cdsapi.Client()
    client.retry_max = 3
    client.sleep_max = 20
    client.timeout = 120
    request = request_for(row)
    for attempt in range(1, retries + 1):
        try:
            log({"event": "request_started", "cell_id": row.cell_id, "attempt": attempt, "request": request})
            client.retrieve(DATASET, request, str(temporary))
            check = validate_zip(temporary, float(row.latitude), float(row.longitude))
            if check["status"] != "VALIDADA":
                raise ValueError(check["error"])
            temporary.replace(target)  # Atomic within its folder, only after validation.
            log({"event": "request_validated", "cell_id": row.cell_id, "attempt": attempt, "sha256": check["sha256"]})
            return
        except Exception as exc:
            log({"event": "request_failed", "cell_id": row.cell_id, "attempt": attempt, "error": str(exc)})
            temporary.unlink(missing_ok=True)
            if attempt == retries:
                raise
            time.sleep(20 * attempt)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true", help="Allow CDS network requests after preflight.")
    parser.add_argument("--trial", metavar="CELL_ID", help="Download only one pending cell first.")
    parser.add_argument("--all-validated-after-trial", action="store_true", help="Sequentially download pending cells; requires a previously VALIDADA trial.")
    parser.add_argument("--retries", type=int, default=3)
    args = parser.parse_args()
    if args.all_validated_after_trial and not args.download:
        parser.error("--all-validated-after-trial requiere --download")
    frame = pd.read_csv(PENDING_CSV)
    validate_input(frame)
    previous = {}
    if MANIFEST.exists():
        previous = {row["cell_id"]: row for row in pd.read_csv(MANIFEST).fillna("").to_dict("records")}
    manifest = write_manifest(frame, previous)
    ready, message = cds_configuration_status()
    print(f"CSV validado: {len(frame)} celdas; peso pendiente={frame.spatial_weight.sum():.15f}")
    print(f"Configuración CDS: {message}")
    print(f"Manifiesto: {MANIFEST}")
    if not args.download:
        print("Modo seguro: no se envió ninguna solicitud. Use --trial ERA5L_01 --download solo tras configurar CDS.")
        return
    if not ready:
        raise SystemExit("No se puede descargar: configure CDS y acepte la licencia antes de volver a ejecutar.")
    validated = set(manifest.loc[manifest.status == "VALIDADA", "cell_id"])
    if args.trial:
        selection = frame.loc[frame.cell_id == args.trial]
        if len(selection) != 1:
            raise SystemExit("--trial debe indicar uno de los 25 cell_id del CSV.")
        download_one(selection.iloc[0], args.retries)
    elif args.all_validated_after_trial:
        if not validated:
            raise SystemExit("Primero descargue y valide una prueba con --trial CELL_ID --download.")
        for _, row in frame.iterrows():
            if row.cell_id not in validated:
                download_one(row, args.retries)
    else:
        raise SystemExit("Por seguridad indique --trial CELL_ID o --all-validated-after-trial.")
    write_manifest(frame, {row["cell_id"]: row for row in pd.read_csv(MANIFEST).fillna("").to_dict("records")})


if __name__ == "__main__":
    main()
