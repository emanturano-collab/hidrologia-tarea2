"""Descarga y recorta los datos del DWD usados para contrastar el evento del 24/07/2013.

Fuentes (DWD Climate Data Center, acceso abierto):
  - Lluvia de 10 min (historical): estaciones 06262, 01197, 01538, 02485.
  - Lluvia diaria (more_precip/historical): 00006, 00019, 00020, 00774, 01674, 02194, 06262.
  - RADOLAN RW horario (grids_germany/hourly/radolan/historical/asc/2013/RW-201307.tar).

Escribe en datos/punto2/vecinas_2013/:
  - 10min_<id>.csv: serie completa (06262 y 01197, que cumplen los requisitos de 2.1) o los dias
    23-25/07/2013 (resto), con columnas fecha_utc, precip_mm (-999 = faltante) y QN.
  - diaria_20130720_20130728.csv: lluvia diaria de las siete estaciones.
  - radolan_RW_20130724-HHMM.asc: tres horas (11:50-14:50 UTC) recortadas a 81 x 81 km.
  - estaciones.csv: coordenadas, altura y periodo de cada estacion.

Uso: python codigo/punto2/descargar_vecinas_2013.py [--cache CARPETA]
La carpeta cache guarda los ZIP originales y no forma parte de la entrega.
"""
from pathlib import Path
import argparse
import io
import re
import tarfile
import urllib.request
import zipfile

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "datos" / "punto2" / "vecinas_2013"
CDC = "https://opendata.dwd.de/climate_environment/CDC"
U10 = f"{CDC}/observations_germany/climate/10_minutes/precipitation/historical/"
UDAY = f"{CDC}/observations_germany/climate/daily/more_precip/historical/"
URAD = f"{CDC}/grids_germany/hourly/radolan/historical/asc/2013/RW-201307.tar"
COMPLETAS = ["06262", "01197"]
EVENTO = ["01538", "02485"]
DIARIAS = ["00006", "00019", "00020", "00774", "01674", "02194", "06262"]

ap = argparse.ArgumentParser()
ap.add_argument("--cache", default=str(ROOT.parent / "cache_dwd"))
CACHE = Path(ap.parse_args().cache)
CACHE.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)


def bajar(url):
    dest = CACHE / url.rsplit("/", 1)[1]
    if not dest.exists():
        print("descargando", url)
        urllib.request.urlretrieve(url, dest)
    return dest


def listado(url, patron):
    html = urllib.request.urlopen(url, timeout=120).read().decode("latin-1")
    return sorted(set(re.findall(patron, html)))


def producto(zp, prefijo):
    with zipfile.ZipFile(zp) as z:
        nombre = [n for n in z.namelist() if n.startswith(prefijo)][0]
        d = pd.read_csv(io.BytesIO(z.read(nombre)), sep=";", skipinitialspace=True)
    d.columns = [c.strip() for c in d.columns]
    return d


# Estaciones (listas oficiales de descripcion)
est = []
for url, tipo in ((U10 + "zehn_min_rr_Beschreibung_Stationen.txt", "10min"),
                  (UDAY + "RR_Tageswerte_Beschreibung_Stationen.txt", "diaria")):
    txt = urllib.request.urlopen(url, timeout=120).read().decode("latin-1").splitlines()[2:]
    for l in txt:
        p = l.split()
        if p and p[0] in set(COMPLETAS + EVENTO + DIARIAS):
            est.append({"id": p[0], "tipo": tipo, "desde": p[1], "hasta": p[2], "altura_m": float(p[3]),
                        "lat": float(p[4]), "lon": float(p[5]), "nombre": " ".join(p[6:-2])})
pd.DataFrame(est).to_csv(OUT / "estaciones.csv", index=False)

# 10 minutos
zips10 = listado(U10, r"10minutenwerte_nieder_\d{5}_\d{8}_\d{8}_hist\.zip")
for sid in COMPLETAS + EVENTO:
    partes = [producto(bajar(U10 + z), "produkt_zehn_min_rr") for z in zips10 if f"_{sid}_" in z]
    d = pd.concat(partes).drop_duplicates("MESS_DATUM").sort_values("MESS_DATUM")
    if sid in EVENTO:
        d = d[(d["MESS_DATUM"] >= 201307230000) & (d["MESS_DATUM"] < 201307260000)]
    d[["MESS_DATUM", "RWS_10", "QN"]].rename(columns={"MESS_DATUM": "fecha_utc", "RWS_10": "precip_mm"}) \
        .to_csv(OUT / f"10min_{sid}.csv", index=False)

# Diarias
zipsd = listado(UDAY, r"tageswerte_RR_\d{5}_\d{8}_\d{8}_hist\.zip")
filas = []
for sid in DIARIAS:
    z = [x for x in zipsd if f"_RR_{sid}_" in x][0]
    d = producto(bajar(UDAY + z), "produkt_nieder_tag")
    d = d[(d["MESS_DATUM"] >= 20130720) & (d["MESS_DATUM"] <= 20130728)]
    filas.append(d[["STATIONS_ID", "MESS_DATUM", "QN_6", "RS", "RSF"]])
pd.concat(filas).to_csv(OUT / "diaria_20130720_20130728.csv", index=False)

# RADOLAN: tres horas recortadas alrededor de la estacion 00020
tar = bajar(URAD)
with tarfile.open(tar) as t:
    dia = tarfile.open(fileobj=io.BytesIO(t.extractfile("RW-20130724.tar.gz").read()), mode="r:gz")
    for hh in ("1250", "1350", "1450"):
        lines = dia.extractfile(f"RW_20130724-{hh}.asc").read().decode().splitlines()
        hd = {k: float(v) for k, v in (l.split() for l in lines[:6])}
        z = np.array([l.split() for l in lines[6:]], dtype=float)[::-1]  # fila 0 = sur
        i0, j0, n = 205 - 40, 516 - 40, 81  # celda de la estacion 00020 (ver contraste_evento_2013.py)
        w = z[i0:i0 + n, j0:j0 + n][::-1]
        head = (f"ncols {n}\nnrows {n}\nxllcorner {hd['xllcorner'] + j0 * hd['cellsize']:.0f}\n"
                f"yllcorner {hd['yllcorner'] + i0 * hd['cellsize']:.0f}\ncellsize {hd['cellsize']:.0f}\nNODATA_value -1\n")
        np.savetxt(OUT / f"radolan_RW_20130724-{hh}.asc", w, fmt="%d", header=head.strip(), comments="")
print("Listo:", sorted(p.name for p in OUT.iterdir()))
