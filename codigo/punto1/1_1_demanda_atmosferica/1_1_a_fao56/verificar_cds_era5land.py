"""Prueba mínima de acceso a ERA5-Land sin exponer ni conservar credenciales."""
from __future__ import annotations
from pathlib import Path
import sys
import cdsapi

DATASET = "reanalysis-era5-land-timeseries"
ROOT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
PROBE = ROOT / "tmp" / "cds_era5land_auth_probe.zip"

def main() -> None:
    config = Path.home() / ".cdsapirc"
    if not config.is_file() or config.stat().st_size == 0:
        raise SystemExit("CONFIGURACION_FALTANTE: no existe .cdsapirc no vacío.")
    PROBE.parent.mkdir(exist_ok=True)
    PROBE.unlink(missing_ok=True)
    request = {"variable": ["2m_temperature"], "location": {"latitude": -6.4, "longitude": -79.3},
               "date": "2001-01-01/2001-01-01", "data_format": "netcdf"}
    try:
        client = cdsapi.Client(quiet=True, debug=False)
        client.retry_max, client.sleep_max, client.timeout = 1, 5, 120
        client.retrieve(DATASET, request, str(PROBE))
        if not PROBE.is_file() or PROBE.stat().st_size == 0:
            raise RuntimeError("CDS respondió sin archivo descargado")
        print(f"PRUEBA_CDS_OK: respuesta mínima recibida ({PROBE.stat().st_size} bytes); temporal eliminado.")
    except Exception as exc:
        print(f"PRUEBA_CDS_FALLO: {type(exc).__name__}: {exc}")
        sys.exit(2)
    finally:
        PROBE.unlink(missing_ok=True)

if __name__ == "__main__":
    main()
