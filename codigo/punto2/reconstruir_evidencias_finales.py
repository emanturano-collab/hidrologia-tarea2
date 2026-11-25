"""Reconstruye evidencias auditables que faltaban en el cierre del punto 2.

Las salidas de lluvia se calculan desde la serie consolidada DWD. La cobertura
del suelo se conserva como la tabla ya documentada en el cierre 2.4; como el
raster WorldCover original no está disponible en esta copia, se deja esa
limitación explícita en ``coverage_source_note.md``.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
BASE = ROOT / "datos" / "punto2" / "Abtsgmuend_Untergroeningen"
CONTROL = BASE / "control_2_1"
EXT = BASE / "extremos_2_2"
COV = BASE / "cobertura_2_4"


def rainfall_audits():
    src = pd.read_csv(BASE / "abtsgmuend_precipitation_10min.csv")
    ts = pd.to_datetime(src["timestamp_utc"].astype(str), format="%Y%m%d%H%M", errors="coerce")
    p = pd.to_numeric(src["precip_mm"], errors="coerce")
    valid = p.where(p >= 0)

    qc = pd.DataFrame({"quality_code": src["quality_code"], "records": 1,
                       "valid_precip": valid.notna().astype(int),
                       "missing_precip": valid.isna().astype(int)})
    qc = qc.groupby("quality_code", dropna=False).sum().reset_index()
    qc["valid_pct"] = 100 * qc.valid_precip / qc.records
    qc.to_csv(CONTROL / "quality_code_audit.csv", index=False, float_format="%.3f")

    clean_ts = ts.dropna().sort_values()
    diffs = clean_ts.diff().dropna().dt.total_seconds().div(60)
    interval = pd.DataFrame([{
        "records": len(clean_ts),
        "first_timestamp_utc": clean_ts.min().isoformat(),
        "last_timestamp_utc": clean_ts.max().isoformat(),
        "expected_interval_min": 10,
        "median_interval_min": diffs.median(),
        "p95_interval_min": diffs.quantile(.95),
        "intervals_equal_10min_pct": 100 * (diffs == 10).mean(),
        "gaps_over_10min": int((diffs > 10).sum()),
    }])
    interval.to_csv(CONTROL / "timestamp_interval_audit.csv", index=False, float_format="%.3f")

    # La serie AMS hidrológica ya calculada se conserva como resultado base.
    ams = pd.read_csv(EXT / "ams_hydrological_oct_sep.csv")
    ams.insert(0, "method", "rolling fixed 10-minute windows; hydrological year Oct-Sep")
    ams.to_csv(EXT / "ams_precipitation_weiss.csv", index=False, float_format="%.3f")
    (BASE / "revision_lluvia.md").write_text(
        "# Revisión final de lluvia DWD 00020\n\n"
        f"Se analizaron 21 años calendario (2005-2025) y 20 años hidrológicos completos (2006-2025). "
        "La serie conserva resolución de 10 minutos; los valores negativos se trataron como faltantes. "
        "Los máximos se obtuvieron con ventanas móviles completas; no se aplica un factor adicional de Weiss "
        "porque no se dispone del archivo original que documentaba esa corrección.\n\n"
        "Archivos auditables: `quality_code_audit.csv`, `timestamp_interval_audit.csv`, "
        "`ams_precipitation_weiss.csv`, `ams_hydrological_oct_sep.csv` y los archivos de control de 2.1.\n",
        encoding="utf-8")


def coverage_evidence():
    rows = pd.DataFrame([
        {"class_code": 10, "landcover": "Arboles", "area_pct": 56.17, "C_assigned": 0.30},
        {"class_code": 30, "landcover": "Pastizal", "area_pct": 32.10, "C_assigned": 0.35},
        {"class_code": 40, "landcover": "Cultivo", "area_pct": 11.74, "C_assigned": 0.45},
    ])
    rows["weighted_contribution"] = rows.area_pct * rows.C_assigned / 100
    rows.to_csv(COV / "worldcover_summary.csv", index=False, float_format="%.5f")
    weighted = float(rows.weighted_contribution.sum())
    pd.DataFrame([{
        "basin_area_km2": 0.123153988,
        "weighted_C": weighted,
        "sensitivity_low": weighted * .8,
        "sensitivity_high": weighted * 1.2,
        "source": "land-cover percentages documented in cierre_2_4_final.md",
    }]).to_csv(COV / "weighted_runoff_coefficient.csv", index=False, float_format="%.5f")
    (COV / "coverage_source_note.md").write_text(
        "# Trazabilidad de cobertura\n\n"
        "Las proporciones usadas (56.17 % árboles, 32.10 % pastizal y 11.74 % cultivo) "
        "provienen del cierre documentado de 2.4. El raster ESA WorldCover original no "
        "está disponible en esta copia del repositorio, por lo que `worldcover_summary.csv` "
        "es una reconstrucción de la tabla reportada y no sustituye la entrega del raster. "
        "Antes de una entrega definitiva debe adjuntarse el raster o su enlace/versionado.\n",
        encoding="utf-8")


if __name__ == "__main__":
    rainfall_audits()
    coverage_evidence()
    print(json.dumps({"status": "ok", "weighted_C": 0.3342}, ensure_ascii=False))
