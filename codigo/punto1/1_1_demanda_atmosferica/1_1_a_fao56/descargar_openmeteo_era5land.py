"""Descarga horaria de ERA5-Land (via Open-Meteo) para completar 1.1.a y reponer insumos.

Motivo: el servicio CDS de Copernicus rechazo la autenticacion de la cuenta del grupo
(error 401), de modo que 13 de las 33 celdas de la cuenca (9,87 % del peso) y los ZIP
de Chiclayo no estaban disponibles. Open-Meteo redistribuye ERA5-Land sin credenciales
(licencia CC BY 4.0; Zippenfenig, 2023). Con el modelo ``era5_seamless`` entrega la
temperatura y el punto de rocio de ERA5-Land (0,1 grados) y el viento, la radiacion y la
presion de ERA5 (0,25 grados), que son las variables con que se fuerza ERA5-Land.

Grupos de celdas:
  faltantes : las 13 celdas sin datos en la version de 90,13 %.
  control   : ERA5L_12, celda que ya tenia el grupo, para validar Open-Meteo contra CDS.
  control2  : ERA5L_10, ERA5L_05 y ERA5L_23 (565, 1326 y 3423 m) para la correccion del viento.
  chiclayo  : celda ERA5-Land de la estacion PEI0000SPHI (prueba 1.1.b).

Salida: datos/punto1/originales/openmeteo_era5land/<celda>.csv (UTC, horario):
  time, t2m_c, d2m_c, sp_hpa, wind10_ms, ssrd_w_m2 (media de la hora anterior).

Uso: python descargar_openmeteo_era5land.py faltantes control chiclayo
Retoma la descarga si se interrumpe (por anio y por celda).
"""
from pathlib import Path
import json
import sys
import time
import urllib.error
import urllib.request

import pandas as pd

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
OUT = ROOT / "datos" / "punto1" / "originales" / "openmeteo_era5land"
OUT.mkdir(parents=True, exist_ok=True)
GRID = ROOT / "productos" / "punto1" / "1_1_demanda_atmosferica" / "tablas" / "era5land_33_celdas_pesos_y_elevacion.csv"
API = "https://archive-api.open-meteo.com/v1/archive"
VARS = "temperature_2m,dew_point_2m,surface_pressure,wind_speed_10m,shortwave_radiation"
PAUSA_S = 20  # unas 180 solicitudes por hora, por debajo de los limites de la API gratuita

grid = pd.read_csv(GRID).set_index("cell_id")
FALTANTES = ["ERA5L_01", "ERA5L_03", "ERA5L_04", "ERA5L_08", "ERA5L_09", "ERA5L_16", "ERA5L_17",
             "ERA5L_18", "ERA5L_24", "ERA5L_29", "ERA5L_30", "ERA5L_32", "ERA5L_33"]
GRUPOS = {
    "faltantes": [(c, grid.loc[c, "latitude"], grid.loc[c, "longitude"], "1981-01-01", "2023-08-31") for c in FALTANTES],
    "control": [("ERA5L_12", grid.loc["ERA5L_12", "latitude"], grid.loc["ERA5L_12", "longitude"], "2001-01-01", "2003-12-31")],
    "chiclayo": [("Chiclayo_SPHI", -6.8, -79.8, "2010-01-01", "2023-01-01")],
    # Celdas adicionales con datos CDS para estimar la correccion del viento (ERA5 frente a ERA5-Land)
    "control2": [(c, grid.loc[c, "latitude"], grid.loc[c, "longitude"], "2001-01-01", "2003-12-31")
                 for c in ("ERA5L_10", "ERA5L_05", "ERA5L_23")],
}


def pedir(lat, lon, ini, fin):
    q = (f"{API}?latitude={lat:.4f}&longitude={lon:.4f}&start_date={ini}&end_date={fin}&hourly={VARS}"
         "&wind_speed_unit=ms&timezone=GMT&models=era5_seamless&cell_selection=nearest&elevation=nan")
    for intento in range(6):
        try:
            with urllib.request.urlopen(q, timeout=180) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="ignore")[:200]
            if e.code == 429:
                print("  limite de la API:", msg, "- espera 15 min", flush=True)
                time.sleep(900)
                continue
            raise RuntimeError(f"HTTP {e.code}: {msg}")
        except (urllib.error.URLError, TimeoutError) as e:
            print("  error de red:", e, "- reintento", flush=True)
            time.sleep(60)
    raise RuntimeError("sin respuesta tras 6 intentos")


for grupo in sys.argv[1:]:
    for celda, lat, lon, ini, fin in GRUPOS[grupo]:
        destino = OUT / f"{celda}.csv"
        partes_dir = OUT / f"_partes_{celda}"
        partes_dir.mkdir(exist_ok=True)
        for anio in range(int(ini[:4]), int(fin[:4]) + 1):
            parte = partes_dir / f"{anio}.csv"
            if parte.exists():
                continue
            a = max(ini, f"{anio}-01-01")
            b = min(fin, f"{anio}-12-31")
            j = pedir(lat, lon, a, b)
            h = pd.DataFrame(j["hourly"]).rename(columns={
                "temperature_2m": "t2m_c", "dew_point_2m": "d2m_c", "surface_pressure": "sp_hpa",
                "wind_speed_10m": "wind10_ms", "shortwave_radiation": "ssrd_w_m2"})
            h.attrs["celda"] = (j["latitude"], j["longitude"])
            h.to_csv(parte, index=False)
            print(f"{celda} {anio}: {len(h)} h, celda devuelta ({j['latitude']:.3f}, {j['longitude']:.3f}), "
                  f"faltantes {int(h.drop(columns='time').isna().sum().sum())}", flush=True)
            time.sleep(PAUSA_S)
        partes = sorted(partes_dir.glob("*.csv"))
        pd.concat([pd.read_csv(p) for p in partes]).to_csv(destino, index=False)
        for p in partes:
            p.unlink()
        partes_dir.rmdir()
        print(f"LISTO {celda}: {destino.name}", flush=True)
