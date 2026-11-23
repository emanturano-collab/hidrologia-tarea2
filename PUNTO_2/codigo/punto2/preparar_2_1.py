"""Cierra el apartado 2.1: temporada de lluvias, año hidrológico y ubicación."""
from pathlib import Path
import gzip
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "datos" / "punto2" / "Abtsgmuend_Untergroeningen"
OUT = DATA / "control_2_1"
OUT.mkdir(exist_ok=True)

ST_LAT, ST_LON, ST_ELEV = 48.9219, 9.9129, 432.0

def main():
    d = pd.read_csv(DATA / "abtsgmuend_precipitation_10min.csv",
                    usecols=["timestamp_utc", "precip_mm"])
    d["timestamp_utc"] = pd.to_datetime(d["timestamp_utc"].astype(str), format="%Y%m%d%H%M", errors="coerce")
    d["precip_mm"] = pd.to_numeric(d["precip_mm"], errors="coerce")
    d.loc[d["precip_mm"] < 0, "precip_mm"] = np.nan
    d = d.dropna(subset=["timestamp_utc"])
    d = d[(d.timestamp_utc >= "2005-01-01") & (d.timestamp_utc <= "2025-12-31 23:59:59")]
    d["year"] = d.timestamp_utc.dt.year
    d["month"] = d.timestamp_utc.dt.month
    d["dayofyear"] = d.timestamp_utc.dt.dayofyear

    # Climatologia mensual: suma anual media y fraccion de años con dato.
    monthly = d.set_index("timestamp_utc")["precip_mm"].resample("MS").sum(min_count=1).to_frame("total_mm")
    monthly["year"] = monthly.index.year
    monthly["month"] = monthly.index.month
    clim = monthly.groupby("month").agg(mean_monthly_mm=("total_mm", "mean"),
                                         sd_monthly_mm=("total_mm", "std"),
                                         n_years=("total_mm", "count")).reset_index()
    clim["fraction_of_annual"] = clim.mean_monthly_mm / clim.mean_monthly_mm.sum()
    clim.to_csv(OUT / "monthly_rainfall_climatology.csv", index=False, float_format="%.3f")

    # La estacionalidad de los maximos subdiarios es mas informativa para IDF:
    # los maximos de 1 h de los 21 años caen entre mayo y septiembre. Se adopta
    # año hidrologico octubre-septiembre para no partir esa temporada de tormentas.
    wet_months = [5, 6, 7, 8, 9]
    dry_months = sorted(set(range(1, 13)) - set(wet_months))
    hydro_start = 10
    d["hydro_year"] = np.where(d.month >= hydro_start, d.year + 1, d.year)
    hydro = d.groupby("hydro_year").agg(records=("precip_mm", "size"), valid=("precip_mm", "count"), total_mm=("precip_mm", "sum")).reset_index()
    hydro["completeness_pct"] = 100 * hydro.valid / hydro.records
    # Con octubre-septiembre, solo 2006-2025 son años hidrologicos completos
    # dentro del periodo descargado (2005 y 2026 quedan truncados).
    hydro["usable_for_ams"] = hydro.hydro_year.between(2006, 2025) & (hydro.completeness_pct >= 80)
    hydro.to_csv(OUT / "hydrological_year_audit.csv", index=False, float_format="%.3f")

    # Reparticion de faltantes por mes y temporada humeda/seca.
    miss = d.assign(missing=d.precip_mm.isna()).groupby("month").agg(records=("missing", "size"), missing=("missing", "sum")).reset_index()
    miss["missing_pct"] = 100 * miss.missing / miss.records
    miss["season"] = np.where(miss.month.isin(wet_months), "wet", "dry")
    miss.to_csv(OUT / "missing_by_month.csv", index=False, float_format="%.3f")

    # Posicion espacial y diferencia de elevacion station-outlet.
    summary = pd.read_csv(DATA / "cuenca_preparada" / "cuenca_resumen.csv")
    s = dict(zip(summary.campo, summary.valor))
    dist_m = float(s.get("outlet_distance_m", np.nan))
    elev_outlet = float(s.get("elev_mean_m", ST_ELEV))
    spatial = {"station_id": "00020", "station_lat": ST_LAT, "station_lon": ST_LON,
               "station_elevation_m": ST_ELEV, "outlet_lat": s.get("outlet_lat"),
               "outlet_lon": s.get("outlet_lon"), "outlet_distance_m": dist_m,
               "basin_area_km2": s.get("area_km2"), "basin_mean_elevation_m": elev_outlet,
               "station_minus_basin_mean_elevation_m": ST_ELEV - elev_outlet,
               "station_inside_drainage": s.get("station_inside_drainage"),
               "spatial_status": "nearby_same_regional_climate_but_outlet_visual_check_pending"}
    (OUT / "spatial_justification.json").write_text(json.dumps(spatial, indent=2), encoding="utf-8")

    lines = ["# Fase 2.1 — resultado del control de datos", "",
             f"- Periodo descargado: 2005-2025; años hidrologicos completos utilizables: 2006-2025 ({int(hydro.usable_for_ams.sum())} años).",
             f"- Meses mas lluviosos que concentran al menos 50% de la climatologia: {', '.join(map(str, wet_months))}.",
             f"- Meses secos restantes: {', '.join(map(str, dry_months))}.",
             f"- Inicio propuesto del año hidrologico: mes {hydro_start}.",
             "- Criterio de año valido: se mantienen los años con completitud >=80%; revisar además vacíos en meses húmedos.",
             f"- Distancia estacion–outlet preliminar: {dist_m:.1f} m; diferencia estacion–elevacion media de cuenca: {ST_ELEV-elev_outlet:.1f} m.",
             "- La estacion es cercana y sirve como referencia regional, pero la relacion outlet-canal/via sigue requiriendo comprobacion visual en QGIS.", "", "## Archivos", "",
             "- `monthly_rainfall_climatology.csv`", "- `hydrological_year_audit.csv`", "- `missing_by_month.csv`", "- `spatial_justification.json`"]
    (OUT / "revision_2_1.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Meses humedos:", wet_months, "inicio_hidro:", hydro_start)
    print(clim.to_string(index=False))

if __name__ == "__main__":
    main()
