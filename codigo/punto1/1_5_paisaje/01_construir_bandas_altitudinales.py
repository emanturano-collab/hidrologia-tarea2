"""Construye bandas altitudinales de Racarumi desde el SRTM oficial de Tarea 1.

Uso (la ruta al ZIP no se guarda en los productos)::
    python 01_construir_bandas_altitudinales.py --tarea1-zip ruta/ENTREGA_FINAL_HIDROLOGIA.zip

Las bandas son intervalos fijos de 500 m, 250--750 hasta 3750--4250 m. Este
ancho cubre el rango SRTM documentado (264--4084 m) con ocho estratos
interpretables y sin crear intervalos artificialmente estrechos. Las áreas se
calculan tras proyectar los polígonos a UTM 17S (EPSG:32717).
"""
from __future__ import annotations

import argparse
import gzip
import json
import shutil
import zipfile
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from rasterio.features import geometry_mask, shapes
from rasterio.transform import from_origin
from shapely.geometry import shape


ROOT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
GPKG = ROOT / "datos" / "punto1" / "PE_200907_catchment_T1_original.gpkg"
RAW_DIR = ROOT / "datos" / "punto1" / "originales" / "tarea1_minimos" / "srtm1_raw"
DATA_DIR = ROOT / "datos" / "punto1" / "procesados" / "1_5_paisaje"
OUT_DIR = ROOT / "productos" / "punto1" / "1_5_paisaje"
TILE_NAMES = ("S07W080.hgt.gz", "S07W079.hgt.gz")
ZIP_SUFFIX = "Delimitacion_Cuenca_y_Elevacion/srtm1_raw/"
BANDS = np.arange(250, 4251, 500)


def materialize_tile(source_zip: Path, tile_name: str) -> Path:
    """Copy just one required original compressed tile from the Task 1 ZIP."""
    target = RAW_DIR / tile_name
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.stat().st_size > 1_000_000:
        return target
    with zipfile.ZipFile(source_zip) as zf:
        matches = [i for i in zf.infolist() if i.filename.endswith(ZIP_SUFFIX + tile_name)]
        if len(matches) != 1:
            raise ValueError(f"No se encontró de forma única {tile_name} en {source_zip}")
        with zf.open(matches[0]) as src, target.open("wb") as dst:
            shutil.copyfileobj(src, dst)
    return target


def load_hgt(paths: list[Path]) -> tuple[np.ndarray, object]:
    arrays = []
    for path in paths:
        with gzip.open(path, "rb") as f:
            raw = np.frombuffer(f.read(), dtype=">i2")
        if raw.size != 3601 * 3601:
            raise ValueError(f"{path.name}: tamaño HGT inesperado ({raw.size} muestras)")
        arrays.append(raw.reshape(3601, 3601))
    # W080 cubre -80..-79 and W079 -79..-78. The shared meridian is kept once.
    return np.hstack((arrays[0][:, :-1], arrays[1])), from_origin(-80.0, -6.0, 1 / 3600, 1 / 3600)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--tarea1-zip", required=True, type=Path)
    args = p.parse_args()
    if not args.tarea1_zip.is_file():
        raise FileNotFoundError(args.tarea1_zip)
    basin = gpd.read_file(GPKG)
    if basin.empty or basin.crs is None:
        raise ValueError("La delimitación oficial no es legible o no tiene CRS")
    basin = basin.to_crs(4326)
    geom = basin.geometry.union_all()
    dem, transform = load_hgt([materialize_tile(args.tarea1_zip, tile) for tile in TILE_NAMES])
    inside = geometry_mask([geom], transform=transform, invert=True, out_shape=dem.shape)
    valid = inside & (dem != -32768)
    if valid.sum() == 0:
        raise ValueError("El SRTM no intersecta la delimitación oficial")
    # Índices 1..8; cero es fuera de cuenca/no-data.
    cls = np.zeros(dem.shape, dtype=np.uint8)
    cls[valid] = np.digitize(dem[valid], BANDS, right=False)
    if not np.all((cls[valid] >= 1) & (cls[valid] <= len(BANDS) - 1)):
        raise ValueError("Hay elevaciones fuera de los intervalos definidos")
    geoms, values = [], []
    for geo, value in shapes(cls, mask=valid, transform=transform):
        if value:
            geoms.append(shape(geo)); values.append(int(value))
    bands = gpd.GeoDataFrame({"band_id": values}, geometry=geoms, crs=4326)
    bands = bands.dissolve("band_id", as_index=False).sort_values("band_id")
    bands["elev_min_m"] = [int(BANDS[i - 1]) for i in bands.band_id]
    bands["elev_max_m"] = [int(BANDS[i]) for i in bands.band_id]
    bands["band_label"] = bands.apply(lambda r: f"{r.elev_min_m}-{r.elev_max_m} m", axis=1)
    bands_utm = bands.to_crs(32717)
    bands["area_m2"] = bands_utm.geometry.area.to_numpy()
    rows = []
    for row in bands.itertuples(index=False):
        values_in_band = dem[(cls == row.band_id) & valid].astype(float)
        rows.append({"band_id": row.band_id, "band_label": row.band_label,
                     "elev_min_m": row.elev_min_m, "elev_max_m": row.elev_max_m,
                     "elev_mean_srtm_m": float(values_in_band.mean()),
                     "elev_median_srtm_m": float(np.median(values_in_band)),
                     "elev_min_observed_m": int(values_in_band.min()),
                     "elev_max_observed_m": int(values_in_band.max()),
                     "srtm_pixels_1arcsec": int(values_in_band.size),
                     "area_m2_utm17s": float(row.area_m2)})
    table = pd.DataFrame(rows).sort_values("band_id")
    total = table.area_m2_utm17s.sum()
    table["area_km2_utm17s"] = table.area_m2_utm17s / 1e6
    table["basin_area_percent"] = 100 * table.area_m2_utm17s / total
    if not np.isclose(table.basin_area_percent.sum(), 100.0, atol=1e-8):
        raise ValueError("Las superficies no suman 100 %")
    DATA_DIR.mkdir(parents=True, exist_ok=True); OUT_DIR.mkdir(parents=True, exist_ok=True)
    bands.to_file(DATA_DIR / "PE_200907_bandas_altitudinales_SRTM_500m.gpkg", layer="bandas", driver="GPKG")
    table.to_csv(OUT_DIR / "1_5_bandas_altitudinales_SRTM.csv", index=False)
    summary = {"source": "SRTM 1 arc-second; S07W080 y S07W079 de Tarea 1", "catchment": "PE_200907",
               "input_crs": "EPSG:4326", "area_crs": "EPSG:32717", "band_edges_m": BANDS.tolist(),
               "srtm_min_m": int(dem[valid].min()), "srtm_max_m": int(dem[valid].max()),
               "srtm_mean_m_unweighted_pixels": float(dem[valid].mean()),
               "area_km2_utm17s": float(total / 1e6), "bands": len(table)}
    (OUT_DIR / "1_5_bandas_altitudinales_metadatos.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(table.to_string(index=False)); print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
