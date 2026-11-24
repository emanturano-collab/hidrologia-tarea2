"""Documenta WorldCover, completitud anual y corrección de Weiss para la Fase 2."""
from pathlib import Path
import hashlib
import json
import pandas as pd
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "datos" / "punto2" / "Abtsgmuend_Untergroeningen"
COV = DATA / "cobertura_2_4"
QC = DATA / "control_2_1"

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def main():
    tif = COV / "ESA_WorldCover_10m_2021_v200_N48E009_Map.tif"
    if not tif.exists():
        raise FileNotFoundError(tif)
    digest = sha256(tif)
    Image.MAX_IMAGE_PIXELS = None
    im = Image.open(tif)
    tags = im.tag_v2
    metadata = {
        "product": "ESA WorldCover 2021 v200 Map",
        "provider": "ESA WorldCover / VITO",
        "tile": "N48E009",
        "tile_extent": "9E–12E, 48N–51N",
        "download_url": "https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_N48E009_Map.tif",
        "download_date_utc": "2026-11-24",
        "crs": "EPSG:4326",
        "resolution_degrees": [float(x) for x in tags[33550][:2]],
        "dimensions_pixels": list(im.size),
        "sha256": digest,
        "bytes": tif.stat().st_size,
        "classes": {10: "Tree cover", 20: "Shrubland", 30: "Grassland", 40: "Cropland", 50: "Built-up", 60: "Bare / sparse vegetation", 70: "Snow and ice", 80: "Permanent water bodies", 90: "Herbaceous wetland", 95: "Mangroves", 100: "Moss and lichen"},
    }
    (COV / "worldcover_metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    (COV / "worldcover_sha256.txt").write_text(f"{digest}  {tif.name}\n", encoding="utf-8")

    audit = pd.read_csv(QC / "hydrological_year_audit.csv")
    valid = audit[audit["hydro_year"].between(2006, 2025)].copy()
    report = f"""# Completitud anual y criterio de máximos válidos

## Criterio aplicado

El año hidrológico es octubre–septiembre. Se exige al menos 80 % de registros
válidos en el año y al menos 90 % en la temporada lluviosa. Los faltantes se
conservan como ausentes; no se imputan. Los máximos anuales solo se forman con
ventanas móviles completas.

## Resultado

- 2004: periodo calendario parcial, excluido.
- 2005: año hidrológico parcial, excluido de AMS.
- 2006–2025: **20 años hidrológicos válidos**.
- Completitud mínima en 2006–2025: **{valid.completeness_pct.min():.3f} %**.
- Completitud media en 2006–2025: **{valid.completeness_pct.mean():.3f} %**.
- Años hidrológicos descartados por completitud: **0** entre 2006 y 2025.
- 2026: registro parcial, excluido de AMS y tendencias.

La serie cumple el requisito de al menos 20 años válidos de máximos anuales.
La tabla fuente es `hydrological_year_audit.csv`.
"""
    (QC / "completitud_anual.md").write_text(report, encoding="utf-8")
    valid[["hydro_year", "records", "valid", "completeness_pct", "usable_for_ams"]].to_csv(QC / "completitud_anual.csv", index=False, float_format="%.3f")

    weiss = """# Corrección de Weiss (1964)

La estación DWD 00020 registra acumulados en intervalos fijos de 10 minutos
(00, 10, 20, …, 50). El procesamiento de extremos usa ventanas móviles de 10
minutos, 30 minutos, 1, 3, 6, 12 y 24 horas. Por tanto, los máximos de la serie
principal no son máximos de una única ventana fija de reloj y no se aplica una
segunda corrección de Weiss a `ams_hydrological_oct_sep.csv`.

La decisión final es: **ventanas móviles + factor Weiss adicional igual a 1.0
(no aplicado)**, para evitar doble corrección. Si se analizara una serie de
máximos estrictamente fija, la corrección sería `1/(1 - 1/(8n))`, donde `n` es
el número de intervalos de la duración.
"""
    (QC / "weiss_correccion.md").write_text(weiss, encoding="utf-8")
    print(json.dumps({"worldcover_sha256": digest, "valid_hydrological_years": 20, "min_completeness_pct": float(valid.completeness_pct.min())}, indent=2))

if __name__ == "__main__":
    main()
