"""Build the spatial inventory and the non-download plan for FAO-56 section 1.1.a.

This script is read-only with respect to Tarea 1 and all ERA5-Land ZIP inputs.
It creates reproducible tables and a figure under Tarea 2 only.
"""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd


ROOT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
TASK = ROOT
T1 = ROOT / "datos" / "punto1" / "originales" / "tarea1_minimos"
BASE = T1
CATCHMENT = (
    T1 / "PE_200907_catchment.gpkg"
)
WEIGHTS = (
    T1 / "PE_200907_ERA5Land_Copernicus_grid_weights.csv"
)
SRTM = BASE / "PE_200907_ERA5Land_cells_SRTM_elevation.csv"
OROGRAPHY = BASE / "PE_200907_ERA5Land_native_orography.csv"

METADATA = TASK / "datos" / "punto1" / "metadatos"
TABLES = TASK / "productos" / "punto1" / "1_1_demanda_atmosferica" / "tablas"
FIGURES = TASK / "productos" / "punto1" / "1_1_demanda_atmosferica" / "figuras"
ANNEXES = TASK / "anexos" / "punto1"

SELECTED = {
    (-6.6, -79.3): "P1", (-6.5, -79.2): "P2", (-6.4, -79.2): "P3",
    (-6.6, -79.1): "P4", (-6.6, -78.9): "P5", (-6.7, -78.7): "P6",
    (-6.8, -78.8): "P7", (-6.9, -78.9): "P8",
}
CDS_VARIABLES = (
    "2m_temperature;t2m_dewpoint_temperature;surface_pressure;"
    "surface_solar_radiation_downwards;10m_u_component_of_wind;"
    "10m_v_component_of_wind"
)


def rounded_key(frame: pd.DataFrame) -> pd.Series:
    return list(zip(frame["latitude"].round(4), frame["longitude"].round(4)))


def main() -> None:
    for folder in (METADATA, TABLES, FIGURES, ANNEXES):
        folder.mkdir(parents=True, exist_ok=True)

    catchment = gpd.read_file(CATCHMENT).to_crs(4326)
    geometry = catchment.geometry.union_all()
    weights = pd.read_csv(WEIGHTS)
    srtm = pd.read_csv(SRTM)
    orography = pd.read_csv(OROGRAPHY).rename(
        columns={"requested_latitude": "latitude", "requested_longitude": "longitude"}
    )
    for frame in (weights, srtm, orography):
        frame["key"] = rounded_key(frame)

    table = weights.merge(
        srtm[["key", "dem_mean_elevation_m", "dem_min_elevation_m", "dem_max_elevation_m"]],
        on="key", validate="one_to_one",
    ).merge(
        orography[["key", "era5land_geopotential_height_m"]],
        on="key", validate="one_to_one",
    )
    table["cell_id"] = [f"ERA5L_{index:02d}" for index in range(1, len(table) + 1)]
    table["selected_point"] = [SELECTED.get(key, "") for key in table["key"]]
    table["selected_for_hourly"] = table["selected_point"].ne("")
    table["grid_center_inside_catchment"] = [geometry.covers(gpd.points_from_xy([lon], [lat])[0]) for lat, lon in zip(table.latitude, table.longitude)]
    table["elevation_difference_era5_minus_srtm_m"] = (
        table["era5land_geopotential_height_m"] - table["dem_mean_elevation_m"]
    )
    table = table.sort_values(["latitude", "longitude"], ascending=[False, True]).reset_index(drop=True)
    output_columns = [
        "cell_id", "latitude", "longitude", "selected_point", "selected_for_hourly",
        "grid_center_inside_catchment", "sample_points_inside", "fractional_cell_coverage",
        "area_factor", "spatial_weight", "dem_mean_elevation_m", "dem_min_elevation_m",
        "dem_max_elevation_m", "era5land_geopotential_height_m",
        "elevation_difference_era5_minus_srtm_m",
    ]
    table[output_columns].to_csv(TABLES / "era5land_33_celdas_pesos_y_elevacion.csv", index=False)

    pending = table.loc[~table["selected_for_hourly"], output_columns].copy()
    pending["dataset"] = "reanalysis-era5-land-timeseries"
    pending["period_start_utc"] = "1981-01-01 00:00"
    pending["period_end_utc"] = "2023-08-31 23:00"
    pending["variables_requested"] = CDS_VARIABLES
    pending["reason"] = "Celda con peso real de cuenca sin serie horaria local de las seis variables FAO-56."
    pending.to_csv(METADATA / "era5land_25_celdas_pendientes_CDS.csv", index=False)

    selected_weight = table.loc[table.selected_for_hourly, "spatial_weight"].sum()
    weighted_srtm = (table.dem_mean_elevation_m * table.spatial_weight).sum()
    weighted_orography = (table.era5land_geopotential_height_m * table.spatial_weight).sum()
    audit = pd.DataFrame([{
        "catchment_crs": str(catchment.crs),
        "geometry_type": ";".join(catchment.geom_type.unique()),
        "catchment_area_km2_utm17s": catchment.to_crs(32717).area.sum() / 1e6,
        "era5land_intersecting_cells": len(table),
        "spatial_weights_sum": table.spatial_weight.sum(),
        "selected_hourly_cells": int(table.selected_for_hourly.sum()),
        "selected_hourly_weight": selected_weight,
        "missing_hourly_cells": int((~table.selected_for_hourly).sum()),
        "missing_hourly_weight": 1 - selected_weight,
        "weighted_srtm_elevation_m": weighted_srtm,
        "weighted_era5land_orography_m": weighted_orography,
        "orography_minus_srtm_m": weighted_orography - weighted_srtm,
    }])
    audit.to_csv(METADATA / "era5land_auditoria_espacial_1_1a.csv", index=False)

    fig, ax = plt.subplots(figsize=(8, 8))
    catchment.boundary.plot(ax=ax, color="black", linewidth=1.1, label="Delimitación Racarumi")
    missing = table.loc[~table.selected_for_hourly]
    plotted = ax.scatter(
        missing.longitude, missing.latitude, s=30 + 1300 * missing.spatial_weight,
        c=missing.dem_mean_elevation_m, cmap="viridis", marker="o", edgecolor="white",
        linewidth=0.35, label="Celdas sin serie horaria",
    )
    existing = table.loc[table.selected_for_hourly]
    ax.scatter(
        existing.longitude, existing.latitude, s=40 + 1300 * existing.spatial_weight,
        c=existing.dem_mean_elevation_m, cmap="viridis", marker="s", edgecolor="black",
        linewidth=0.7, label="P1-P8 disponibles",
    )
    for row in existing.itertuples():
        ax.annotate(row.selected_point, (row.longitude, row.latitude), xytext=(3, 3),
                    textcoords="offset points", fontsize=8, fontweight="bold")
    colour_bar = fig.colorbar(plotted, ax=ax, shrink=0.8)
    colour_bar.set_label("Elevación media SRTM de celda (m)")
    ax.set_xlabel("Longitud (°)")
    ax.set_ylabel("Latitud (°)")
    ax.set_title("Racarumi: celdas ERA5-Land, pesos y cobertura horaria actual")
    ax.grid(alpha=0.25)
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURES / "era5land_celdas_pesos_cobertura_horaria.png", dpi=220)
    plt.close(fig)

    strategy = f"""# Estrategia espacial para completar FAO-56 - apartado 1.1.a

## Hallazgo verificable

La delimitación `PE_200907_catchment.gpkg` está en `{catchment.crs}` y su área proyectada UTM 17S es {audit.catchment_area_km2_utm17s.iat[0]:.2f} km². La Tarea 1 tiene {len(table)} celdas ERA5-Land con pesos de intersección que suman {table.spatial_weight.sum():.12f}.

Los puntos P1-P8 son ocho celdas reales de esa tabla y acumulan un peso de {selected_weight:.6f} ({100*selected_weight:.2f} %). Quedan {len(pending)} celdas, con {100*(1-selected_weight):.2f} % del peso, sin series horarias completas. Por ello no es defendible calcular todavía ETo de cuenca con P1-P8, ni rellenar las faltantes por interpolación.

## Alternativas evaluadas

| Alternativa | Cobertura y variables | Ventaja | Limitación | Decisión |
|---|---|---|---|---|
| A. Reusar insumos existentes | Ocho celdas horarias; 32.58 % del peso. Existe temperatura mensual ponderada de Tarea 1. | No requiere descarga. | No aporta las seis variables horarias para las 25 celdas restantes. | Insuficiente. |
| B. CDS `reanalysis-era5-land-timeseries` | 25 coordenadas pendientes, mismas seis variables y periodo que P1-P8. | Mantiene exactamente fuente, resolución horaria y método actual; permite magnitud horaria del viento. | Requiere solicitudes nuevas y credenciales CDS. | Recomendada. |
| C. Earth Engine `ECMWF/ERA5_LAND/DAILY_AGGR` | Celdas diarias de ~11.1 km, con T, Td, presión, radiación y componentes de viento. | Una extracción espacial sería eficiente. | Los no-flujos diarios son promedios de componentes; no preserva la magnitud horaria de viento que exige la guía. También exige acceso Earth Engine y una validación de calendario/proyección. | Útil como contraste, no como fuente principal. |
| D. Interpolar P1-P8 | No aporta observaciones. | Rápida. | Introduce datos no observados/modelados sin base; prohibido por este flujo. | Descartada. |

## Solicitud pendiente recomendada

Usar las {len(pending)} filas de `era5land_25_celdas_pendientes_CDS.csv` como coordenadas para `reanalysis-era5-land-timeseries`, desde 1981-01-01 00:00 hasta 2023-08-31 23:00 UTC. Solicitar: temperatura a 2 m, punto de rocío a 2 m, presión superficial, radiación solar superficial descendente, U10 y V10. Mantener los ZIP originales P1-P8 y guardar cada descarga nueva sin alterar los existentes.

## Elevación y resolución

La elevación media SRTM ponderada es {weighted_srtm:.2f} m y la orografía nativa ERA5-Land ponderada es {weighted_orography:.2f} m: diferencia {weighted_orography-weighted_srtm:.2f} m. Aun con diferencia media pequeña, la elevación SRTM por celda abarca {table.dem_min_elevation_m.min():.0f}-{table.dem_max_elevation_m.max():.0f} m, por lo que se debe discutir el suavizado subcelda de T y Td en el informe.

## Regla para el cálculo final

El cálculo principal seguirá la guía: primero se combinarán las **variables meteorológicas diarias con los 33 pesos** y luego se aplicará FAO-56 con Tmax/Tmin espaciales, ea derivada de Td y la magnitud horaria de viento. Como sensibilidad, se podrá comparar contra el promedio ponderado de ETo calculada por celda; ambos procedimientos no son matemáticamente equivalentes.
"""
    (ANNEXES / "estrategia_espacial_1_1a.md").write_text(strategy, encoding="utf-8")
    print(audit.to_string(index=False))


if __name__ == "__main__":
    main()
