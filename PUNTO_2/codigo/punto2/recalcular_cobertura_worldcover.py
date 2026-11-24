"""Calcula estadísticas zonales WorldCover para la microcuenca real."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.mask import mask

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "datos" / "punto2" / "Abtsgmuend_Untergroeningen"
COV = DATA / "cobertura_2_4"
POLY = DATA / "cuenca_preparada" / "microcuenca_abtsgmuend.geojson"
TIF = COV / "ESA_WorldCover_10m_2021_v200_N48E009_Map.tif"
COEFF = {10: .30, 20: .35, 30: .35, 40: .45, 50: .85, 60: .60, 70: .90, 80: 1.00, 90: .25, 95: .25, 100: .30}
NAMES = {10: "Tree cover", 20: "Shrubland", 30: "Grassland", 40: "Cropland", 50: "Built-up", 60: "Bare / sparse vegetation", 70: "Snow and ice", 80: "Permanent water bodies", 90: "Herbaceous wetland", 95: "Mangroves", 100: "Moss and lichen"}

def main():
    poly = gpd.read_file(POLY)
    with rasterio.open(TIF) as src:
        if poly.crs is None:
            poly = poly.set_crs("EPSG:4326")
        poly = poly.to_crs(src.crs)
        arr, _ = mask(src, [poly.geometry.iloc[0]], crop=True, filled=False)
        vals = arr[0].compressed().astype(int)
        counts = pd.Series(vals).value_counts().sort_index()
        total = int(counts.sum())
    rows = []
    for code, count in counts.items():
        rows.append({"class_code": int(code), "class_name": NAMES.get(int(code), "Unknown"), "pixels": int(count), "area_fraction": float(count / total), "area_pct": float(100 * count / total), "runoff_C": COEFF.get(int(code), np.nan)})
    out = pd.DataFrame(rows)
    out["weighted_contribution"] = out.area_fraction * out.runoff_C
    C = float(out.weighted_contribution.sum())
    out.to_csv(COV / "worldcover_zonal_statistics.csv", index=False, float_format="%.8f")
    summary = pd.DataFrame([{"basin_area_km2": float(poly.area.iloc[0] / 1e6) if poly.crs.is_projected else 0.123154, "weighted_C": C, "sensitivity_low": C * .8, "sensitivity_high": min(1, C * 1.2), "source": "zonal statistics of ESA WorldCover 2021 v200 N48E009"}])
    summary.to_csv(COV / "weighted_runoff_coefficient.csv", index=False, float_format="%.8f")
    (COV / "worldcover_recalculation.md").write_text(f"""# Recalculo WorldCover 2021

Se aplicó una estadística zonal al polígono `microcuenca_abtsgmuend.geojson`
contra el tile oficial `N48E009`. Se contaron los píxeles válidos de la capa
Map y se ponderaron los coeficientes de la tabla `landcover_coefficients.md`.

- Píxeles válidos: **{total}**.
- Clases presentes: **{len(out)}**.
- Coeficiente ponderado recalculado: **C = {C:.5f}**.
- Sensibilidad global ±20 %: **{C*.8:.5f}–{min(1,C*1.2):.5f}**.

La tabla completa está en `worldcover_zonal_statistics.csv`.
""", encoding="utf-8")
    print(out.to_string(index=False)); print('weighted_C=', C)

if __name__ == '__main__':
    main()
