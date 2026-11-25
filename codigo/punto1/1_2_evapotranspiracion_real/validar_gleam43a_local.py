"""Valida un NetCDF GLEAM descargado con OpenSSH sin conectarse al servidor."""
from __future__ import annotations
import argparse
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("gleam_download", HERE / "descargar_gleam43a_mensual.py")
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

ap = argparse.ArgumentParser()
ap.add_argument("year", type=int)
args = ap.parse_args()
name = f"E_{args.year}_GLEAM_v4.3a_MO.nc"
target = module.RAW / name
part = module.RAW / f"{name}.part"
if not target.exists() and part.exists():
    part.replace(target)
if not target.exists():
    raise FileNotFoundError(f"No existe {target} ni su archivo .part")
meta = module.validate(target, args.year)
print("VALIDO", target.name)
print("SHA256", module.sha256(target))
print("METADATOS", meta)
