"""1.3.2: verifica la serie de humedad del suelo con una nueva descarga de ERA5-Land.

El ZIP original de CDS (reanalysis-era5-land-monthly-means) no esta en el repositorio;
su SHA-256 esta en datos/punto1/metadatos/1_3_2_metadatos_y_control_calidad_humedad_suelo.json.
Este script descarga de Open-Meteo (modelo era5_land, sin credenciales) las capas de
0-7, 7-28 y 28-100 cm en las 34 celdas que intersecan la cuenca, calcula medias
mensuales, aplica los mismos pesos de interseccion y la misma zona de raices
(0,07 swvl1 + 0,21 swvl2 + 0,72 swvl3) y compara con la serie procesada.

Ventana de verificacion: 2001-2005 (60 meses); se amplia cambiando ANIOS.
Salidas: datos/punto1/originales/openmeteo_era5land/humedad/<iy>_<ix>.csv y
productos/punto1/1_3_regimen_evaporativo/tablas/1_3_2_verificacion_openmeteo.csv
Uso: python verificar_humedad_openmeteo.py
"""
from pathlib import Path
import json
import time
import urllib.error
import urllib.request

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
TAB = ROOT / "productos" / "punto1" / "1_3_regimen_evaporativo" / "tablas"
OUT = ROOT / "datos" / "punto1" / "originales" / "openmeteo_era5land" / "humedad"
OUT.mkdir(parents=True, exist_ok=True)
SERIE = ROOT / "datos" / "punto1" / "procesados" / "1_3_regimen_evaporativo" / "1_3_2_humedad_suelo_mensual_ponderada_198101_202308.csv"
ANIOS = range(2001, 2006)
API = "https://archive-api.open-meteo.com/v1/archive"
VARS = "soil_moisture_0_to_7cm,soil_moisture_7_to_28cm,soil_moisture_28_to_100cm"
w = pd.read_csv(TAB / "1_3_2_pesos_espaciales_humedad_suelo_interseccion.csv")


def pedir(lat, lon, ini, fin):
    q = (f"{API}?latitude={lat:.4f}&longitude={lon:.4f}&start_date={ini}&end_date={fin}&hourly={VARS}"
         "&timezone=GMT&models=era5_land&cell_selection=nearest&elevation=nan")
    for _ in range(6):
        try:
            with urllib.request.urlopen(q, timeout=180) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print("  limite de la API; espera 15 min", flush=True)
                time.sleep(900)
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            time.sleep(60)
    raise RuntimeError("sin respuesta")


for r in w.itertuples():
    f = OUT / f"{r.iy:02d}_{r.ix:02d}.csv"
    if f.exists():
        continue
    j = pedir(r.latitude, r.longitude, f"{ANIOS[0]}-01-01", f"{ANIOS[-1]}-12-31")
    h = pd.DataFrame(j["hourly"])
    h.to_csv(f, index=False)
    print(f"celda {r.iy},{r.ix}: devuelta ({j['latitude']:.2f}, {j['longitude']:.2f}), {len(h)} h", flush=True)
    time.sleep(20)

capas = ["soil_moisture_0_to_7cm", "soil_moisture_7_to_28cm", "soil_moisture_28_to_100cm"]
acum = None
for r in w.itertuples():
    h = pd.read_csv(OUT / f"{r.iy:02d}_{r.ix:02d}.csv", parse_dates=["time"]).set_index("time")
    m = h[capas].resample("MS").mean() * r.weight
    acum = m if acum is None else acum.add(m, fill_value=0)
acum = acum / w.weight.sum()
acum["theta_rz"] = 0.07 * acum[capas[0]] + 0.21 * acum[capas[1]] + 0.72 * acum[capas[2]]
ref = pd.read_csv(SERIE, parse_dates=["date"]).set_index("date")
c = acum.join(ref, how="inner")
filas = []
for om, cds in ((capas[0], "swvl1_m3_m3"), (capas[1], "swvl2_m3_m3"), (capas[2], "swvl3_m3_m3"), ("theta_rz", "theta_rz_0_100m3_m3")):
    e = c[om] - c[cds]
    filas.append({"variable": cds, "meses": len(c), "media_cds": c[cds].mean(), "media_openmeteo": c[om].mean(),
                  "sesgo": e.mean(), "MAE": e.abs().mean(), "r": np.corrcoef(c[om], c[cds])[0, 1]})
res = pd.DataFrame(filas)
res.to_csv(TAB / "1_3_2_verificacion_openmeteo.csv", index=False, float_format="%.5f")
print(res.round(4).to_string(index=False))
