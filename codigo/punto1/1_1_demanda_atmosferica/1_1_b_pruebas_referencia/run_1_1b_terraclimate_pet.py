"""Integra TerraClimate PET para el contraste de demanda del apartado 1.1.b.

El script no recalcula ni sobrescribe la ETo FAO-56 de 1.1.a. Lee la ETo
preliminar existente, pondera TerraClimate por áreas de intersección con
PE_200907 y genera comparaciones separadas con ETo ERA5-Land y PISCOeo_pm.
"""

from __future__ import annotations

from pathlib import Path
import calendar
import hashlib
import textwrap

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from shapely.geometry import box


ROOT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
TERRACLIMATE = (
    ROOT / "datos" / "punto1" / "originales" / "terraclimate"
    / "TerraClimate_v1_1_PET_Racarumi_198101_202308.nc"
)
CATCHMENT = (
    ROOT / "datos" / "punto1" / "originales" / "tarea1_minimos"
    / "PE_200907_catchment.gpkg"
)
ETO_DAILY = (
    ROOT / "datos" / "punto1" / "procesados"
    / "1_1_a_fao56_preliminar_90pct" / "fao56_eto_diaria_preliminar_90pct.csv"
)
PISCO_VS_ETO = (
    ROOT / "datos" / "punto1" / "procesados" / "1_1_b_pruebas_referencia"
    / "camels_pet_piscoeopm_vs_eto_preliminar_mensual.csv"
)
DATA_OUT = ROOT / "datos" / "punto1" / "procesados" / "1_1_b_pruebas_referencia"
METADATA_OUT = ROOT / "datos" / "punto1" / "metadatos"
TABLE_OUT = ROOT / "productos" / "punto1" / "1_1_demanda_atmosferica" / "tablas"
FIG_OUT = ROOT / "productos" / "punto1" / "1_1_demanda_atmosferica" / "figuras"
ANNEX_OUT = ROOT / "anexos" / "punto1" / "1_1_b_pruebas_referencia"
PRELIMINARY_COVERAGE_PCT = 90.12637836877098
EQUAL_AREA_CRS = 6933


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def monthly_from_complete_days(frame: pd.DataFrame) -> pd.DataFrame:
    """Suma ETo diaria sólo cuando están presentes todos los días del mes."""
    data = frame[["date", "eto_fao56_mm_d"]].copy()
    data["month"] = data["date"].dt.to_period("M")
    rows: list[dict[str, object]] = []
    for month, group in data.groupby("month", sort=True):
        expected = calendar.monthrange(month.year, month.month)[1]
        if group["date"].nunique() == expected and group["eto_fao56_mm_d"].notna().sum() == expected:
            rows.append({
                "month": month.to_timestamp(),
                "days_in_month": expected,
                "eto_era5land_preliminar_mm_month": group["eto_fao56_mm_d"].sum(),
            })
    return pd.DataFrame(rows)


def pair_metrics(left: pd.Series, right: pd.Series, label: str) -> dict[str, object]:
    delta = left - right
    return {
        "comparison": label,
        "n_months": int(len(delta)),
        "pearson_r": float(left.corr(right)),
        "spearman_rho": float(left.rank(method="average").corr(right.rank(method="average"))),
        "bias_left_minus_right_mm_month": float(delta.mean()),
        "mae_mm_month": float(delta.abs().mean()),
        "rmse_mm_month": float(np.sqrt((delta**2).mean())),
    }


def save_figure(fig: plt.Figure, name: str) -> None:
    for suffix in ("png", "pdf"):
        fig.savefig(FIG_OUT / f"{name}.{suffix}", dpi=220 if suffix == "png" else None,
                    bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    for directory in (DATA_OUT, METADATA_OUT, TABLE_OUT, FIG_OUT, ANNEX_OUT):
        directory.mkdir(parents=True, exist_ok=True)
    for path in (TERRACLIMATE, CATCHMENT, ETO_DAILY, PISCO_VS_ETO):
        if not path.is_file():
            raise FileNotFoundError(f"Insumo requerido no encontrado: {path}")

    catchment = gpd.read_file(CATCHMENT).to_crs(4326)
    if len(catchment) != 1:
        raise ValueError("La delimitación debe contener un único polígono de cuenca.")
    basin_geom = catchment.geometry.union_all()
    basin_area_m2 = float(catchment.to_crs(EQUAL_AREA_CRS).area.sum())

    with xr.open_dataset(TERRACLIMATE, engine="netcdf4", decode_times=True) as dataset:
        required = {"pet", "lat", "lon", "time"}
        if missing := required - set(dataset.variables):
            raise ValueError(f"Faltan variables/coordenadas TerraClimate: {sorted(missing)}")
        pet = dataset["pet"]
        if pet.dims != ("time", "lat", "lon"):
            raise ValueError(f"Dimensiones PET no esperadas: {pet.dims}")
        if pet.attrs.get("units") != "mm":
            raise ValueError(f"Unidades PET no esperadas: {pet.attrs.get('units')}")
        times = pd.DatetimeIndex(dataset["time"].values)
        expected = pd.date_range(times.min(), times.max(), freq="MS")
        if not times.equals(expected):
            raise ValueError("La serie mensual TerraClimate tiene meses faltantes o duplicados.")
        lat = dataset["lat"].values.astype(float)
        lon = dataset["lon"].values.astype(float)
        if len(lat) != len(np.unique(lat)) or len(lon) != len(np.unique(lon)):
            raise ValueError("Las coordenadas TerraClimate contienen duplicados.")
        finite_count = int(np.isfinite(pet.values).sum())
        missing_count = int(np.isnan(pet.values).sum())
        if missing_count:
            raise ValueError(f"TerraClimate PET contiene {missing_count} valores ausentes.")
        dx = float(np.median(np.abs(np.diff(lon))))
        dy = float(np.median(np.abs(np.diff(lat))))

        weight_rows: list[dict[str, float | int]] = []
        weighted_series = np.zeros(len(times), dtype=float)
        for lat_index, cell_lat in enumerate(lat):
            for lon_index, cell_lon in enumerate(lon):
                cell = box(cell_lon - dx / 2, cell_lat - dy / 2, cell_lon + dx / 2, cell_lat + dy / 2)
                overlap = cell.intersection(basin_geom)
                if overlap.is_empty:
                    continue
                overlap_m2 = float(gpd.GeoSeries([overlap], crs=4326).to_crs(EQUAL_AREA_CRS).area.iloc[0])
                if overlap_m2 <= 0:
                    continue
                weight_rows.append({
                    "lat_index": lat_index, "lon_index": lon_index, "latitude": cell_lat,
                    "longitude": cell_lon, "intersection_area_m2": overlap_m2,
                })
        weights = pd.DataFrame(weight_rows)
        if weights.empty:
            raise ValueError("No hay celdas TerraClimate que intersecten la cuenca.")
        weights["weight_area"] = weights["intersection_area_m2"] / weights["intersection_area_m2"].sum()
        if not np.isclose(weights["weight_area"].sum(), 1.0):
            raise ValueError("Los pesos TerraClimate no suman 1.")
        for row in weights.itertuples(index=False):
            weighted_series += float(row.weight_area) * pet.isel(lat=int(row.lat_index), lon=int(row.lon_index)).values
        global_attrs = dict(dataset.attrs)
        pet_min, pet_max = float(pet.min()), float(pet.max())

    if not np.isclose(weights["intersection_area_m2"].sum(), basin_area_m2, rtol=1e-9):
        raise ValueError("La suma de áreas de intersección no reproduce el área de la cuenca.")
    terra_monthly = pd.DataFrame({
        "month": times,
        "terraclimate_pet_basin_weighted_mm_month": weighted_series,
        "n_intersecting_cells": len(weights),
        "weight_sum": weights["weight_area"].sum(),
    })
    terra_monthly.to_csv(DATA_OUT / "terraclimate_v1_1_pet_ponderada_cuenca_mensual.csv", index=False)
    weights.to_csv(METADATA_OUT / "terraclimate_v1_1_pet_pesos_interseccion_racarumi.csv", index=False)

    validation = pd.DataFrame([{
        "file": TERRACLIMATE.name, "sha256": sha256(TERRACLIMATE),
        "variable": "pet", "variable_description": pet.attrs.get("description"), "units": pet.attrs.get("units"),
        "time_start": times.min().date().isoformat(), "time_end": times.max().date().isoformat(),
        "n_months": len(times), "temporal_resolution": global_attrs.get("time_coverage_resolution"),
        "crs": pet.attrs.get("coordinate_system"), "grid_lat_resolution_deg": dy,
        "grid_lon_resolution_deg": dx, "n_lat": len(lat), "n_lon": len(lon),
        "n_intersecting_cells": len(weights), "weight_sum": weights["weight_area"].sum(),
        "intersection_area_km2": weights["intersection_area_m2"].sum() / 1e6,
        "catchment_area_km2": basin_area_m2 / 1e6, "n_missing_pet_values": missing_count,
        "n_finite_pet_values": finite_count, "pet_grid_min_mm_month": pet_min, "pet_grid_max_mm_month": pet_max,
        "product_version": global_attrs.get("version"), "product_source": global_attrs.get("source"),
        "pet_method": "Reference evapotranspiration; modified Penman-Monteith corrected for CO2 per TerraClimate v1.1 documentation.",
        "independence_status": "No totalmente independiente de ERA5-Land: TerraClimate v1.1 usa anomalías mensuales ERA5, combinadas con climatologías CHELSA y corrección CRU TS4.09.",
        "validation_status": "VALIDADO",
    }])
    validation.to_csv(METADATA_OUT / "terraclimate_v1_1_pet_validacion.csv", index=False)

    eto = pd.read_csv(ETO_DAILY, parse_dates=["date"])
    eto_monthly = monthly_from_complete_days(eto)
    pisco_eto = pd.read_csv(PISCO_VS_ETO, parse_dates=["month"])

    terra_eto = terra_monthly.merge(eto_monthly, on="month", how="inner")
    terra_eto["difference_terraclimate_minus_eto_mm_month"] = (
        terra_eto["terraclimate_pet_basin_weighted_mm_month"] - terra_eto["eto_era5land_preliminar_mm_month"]
    )
    terra_eto["ratio_terraclimate_to_eto"] = (
        terra_eto["terraclimate_pet_basin_weighted_mm_month"] / terra_eto["eto_era5land_preliminar_mm_month"]
    )
    terra_eto.to_csv(DATA_OUT / "terraclimate_pet_vs_eto_preliminar_mensual.csv", index=False)
    terra_eto.to_csv(TABLE_OUT / "1_1b_terraclimate_pet_vs_eto_preliminar_mensual.csv", index=False)

    three_products = terra_monthly.merge(
        pisco_eto[["month", "pet_piscoeopm_mm_month", "eto_era5land_preliminar_mm_month"]],
        on="month", how="inner"
    )
    three_products["difference_terraclimate_minus_piscoeopm_mm_month"] = (
        three_products["terraclimate_pet_basin_weighted_mm_month"] - three_products["pet_piscoeopm_mm_month"]
    )
    three_products["difference_terraclimate_minus_eto_mm_month"] = (
        three_products["terraclimate_pet_basin_weighted_mm_month"] - three_products["eto_era5land_preliminar_mm_month"]
    )
    three_products.to_csv(DATA_OUT / "tres_productos_demanda_mensual_periodo_comun.csv", index=False)
    three_products.to_csv(TABLE_OUT / "1_1b_tres_productos_demanda_mensual_periodo_comun.csv", index=False)

    metrics = pd.DataFrame([
        pair_metrics(
            terra_eto["terraclimate_pet_basin_weighted_mm_month"],
            terra_eto["eto_era5land_preliminar_mm_month"],
            "TerraClimate PET - ETo FAO-56 ERA5-Land preliminar",
        ),
        pair_metrics(
            three_products["terraclimate_pet_basin_weighted_mm_month"],
            three_products["pet_piscoeopm_mm_month"],
            "TerraClimate PET - PISCOeo_pm",
        ),
        pair_metrics(
            three_products["terraclimate_pet_basin_weighted_mm_month"],
            three_products["eto_era5land_preliminar_mm_month"],
            "TerraClimate PET - ETo FAO-56 ERA5-Land preliminar (triple periodo)",
        ),
    ])
    metrics["eto_spatial_coverage_pct"] = PRELIMINARY_COVERAGE_PCT
    metrics["status"] = "PRELIMINAR: ETo ERA5-Land con 9.8736 % de cobertura espacial pendiente"
    metrics.to_csv(TABLE_OUT / "1_1b_metricas_terraclimate_y_productos_demanda.csv", index=False)

    # Series, dispersión y climatología: reutilizables en informe o tablero.
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(terra_eto["month"], terra_eto["terraclimate_pet_basin_weighted_mm_month"], label="PET TerraClimate v1.1", lw=1)
    ax.plot(terra_eto["month"], terra_eto["eto_era5land_preliminar_mm_month"], label="ETo FAO-56 ERA5-Land (preliminar)", lw=1)
    ax.set(title="Racarumi: TerraClimate frente a ETo ERA5-Land", xlabel="Mes", ylabel="mm/mes")
    ax.legend(ncol=2, fontsize=8); ax.grid(alpha=.25)
    save_figure(fig, "1_1b_terraclimate_vs_eto_serie_mensual")

    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(three_products["month"], three_products["terraclimate_pet_basin_weighted_mm_month"], label="PET TerraClimate v1.1", lw=1)
    ax.plot(three_products["month"], three_products["pet_piscoeopm_mm_month"], label="PET PISCOeo_pm", lw=1)
    ax.plot(three_products["month"], three_products["eto_era5land_preliminar_mm_month"], label="ETo FAO-56 ERA5-Land (preliminar)", lw=1)
    ax.set(title="Racarumi: tres productos de demanda, periodo común", xlabel="Mes", ylabel="mm/mes")
    ax.legend(ncol=3, fontsize=8); ax.grid(alpha=.25)
    save_figure(fig, "1_1b_tres_productos_demanda_serie_mensual")

    fig, ax = plt.subplots(figsize=(5.5, 5.2))
    x = terra_eto["eto_era5land_preliminar_mm_month"]
    y = terra_eto["terraclimate_pet_basin_weighted_mm_month"]
    ax.scatter(x, y, s=13, alpha=.6)
    limits = [min(x.min(), y.min()), max(x.max(), y.max())]
    ax.plot(limits, limits, "k--", lw=1, label="1:1")
    ax.set(title="TerraClimate vs ETo ERA5-Land", xlabel="ETo FAO-56 ERA5-Land preliminar (mm/mes)",
           ylabel="PET TerraClimate (mm/mes)")
    ax.legend(); ax.grid(alpha=.25)
    save_figure(fig, "1_1b_terraclimate_vs_eto_dispersion")

    climatology = three_products.assign(calendar_month=three_products["month"].dt.month).groupby("calendar_month").agg(
        terraclimate_pet_basin_weighted_mm_month=("terraclimate_pet_basin_weighted_mm_month", "mean"),
        pet_piscoeopm_mm_month=("pet_piscoeopm_mm_month", "mean"),
        eto_era5land_preliminar_mm_month=("eto_era5land_preliminar_mm_month", "mean"),
    ).reset_index()
    climatology.to_csv(TABLE_OUT / "1_1b_climatologia_tres_productos_demanda.csv", index=False)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(climatology.calendar_month, climatology.terraclimate_pet_basin_weighted_mm_month, marker="o", label="TerraClimate")
    ax.plot(climatology.calendar_month, climatology.pet_piscoeopm_mm_month, marker="o", label="PISCOeo_pm")
    ax.plot(climatology.calendar_month, climatology.eto_era5land_preliminar_mm_month, marker="o", label="ETo ERA5-Land preliminar")
    ax.set(title="Racarumi: climatología de demanda en periodo común", xlabel="Mes", ylabel="mm/mes", xticks=range(1, 13))
    ax.legend(ncol=3, fontsize=8); ax.grid(alpha=.25)
    save_figure(fig, "1_1b_tres_productos_demanda_climatologia")

    # Mapa de pesos; se muestra sólo el borde de la cuenca y centros con peso.
    plot_weights = gpd.GeoDataFrame(weights.copy(), geometry=gpd.points_from_xy(weights.longitude, weights.latitude), crs=4326)
    fig, ax = plt.subplots(figsize=(7, 6))
    catchment.boundary.plot(ax=ax, color="black", linewidth=1.2)
    plot_weights.plot(ax=ax, column="weight_area", cmap="viridis", markersize=25, legend=True)
    ax.set(title="Racarumi: pesos de intersección TerraClimate v1.1", xlabel="Longitud", ylabel="Latitud")
    ax.grid(alpha=.2)
    save_figure(fig, "1_1b_terraclimate_pesos_espaciales")

    full_metric = metrics.iloc[0]
    triple_tc_pisco = metrics.iloc[1]
    triple_tc_eto = metrics.iloc[2]
    summary = f"""# TerraClimate v1.1 - contraste de demanda para 1.1.b

## Validación e integración espacial

El NetCDF validado contiene `pet` en mm mensuales, con 512 meses continuos de
1981-01 a 2023-08 y sin valores faltantes. La ponderación usa áreas de
intersección en EPSG:{EQUAL_AREA_CRS}: {len(weights)} celdas intersectan Racarumi,
sus pesos suman {weights.weight_area.sum():.12f} y reproducen
{weights.intersection_area_m2.sum()/1e6:.6f} km², frente a
{basin_area_m2/1e6:.6f} km² de la delimitación.

## Comparación con ETo FAO-56 ERA5-Land

El periodo común de meses completos es {terra_eto.month.min().date()} a
{terra_eto.month.max().date()} (n={len(terra_eto)}). Para PET TerraClimate menos
ETo preliminar: Pearson={full_metric.pearson_r:.4f};
Spearman={full_metric.spearman_rho:.4f}; sesgo={full_metric.bias_left_minus_right_mm_month:.3f}
mm/mes; MAE={full_metric.mae_mm_month:.3f} mm/mes; RMSE={full_metric.rmse_mm_month:.3f} mm/mes.
El sesgo positivo indica que TerraClimate fue, en promedio, mayor que la ETo
ERA5-Land preliminar en {full_metric.bias_left_minus_right_mm_month:.3f} mm/mes.
La alta asociación temporal describe una señal estacional compartida; no prueba
equivalencia física entre productos.

## Periodo común de tres productos

PISCOeo_pm termina en 2016; por ello el periodo de tres productos es
{three_products.month.min().date()} a {three_products.month.max().date()}
(n={len(three_products)}). TerraClimate-PISCOeo_pm: Pearson={triple_tc_pisco.pearson_r:.4f},
Spearman={triple_tc_pisco.spearman_rho:.4f}, sesgo={triple_tc_pisco.bias_left_minus_right_mm_month:.3f}
mm/mes, MAE={triple_tc_pisco.mae_mm_month:.3f} mm/mes y RMSE={triple_tc_pisco.rmse_mm_month:.3f}
mm/mes. TerraClimate-ETo ERA5-Land en el mismo periodo: Pearson={triple_tc_eto.pearson_r:.4f},
Spearman={triple_tc_eto.spearman_rho:.4f}, sesgo={triple_tc_eto.bias_left_minus_right_mm_month:.3f}
mm/mes, MAE={triple_tc_eto.mae_mm_month:.3f} mm/mes y RMSE={triple_tc_eto.rmse_mm_month:.3f}
mm/mes.
El sesgo positivo TerraClimate-PISCOeo_pm ({triple_tc_pisco.bias_left_minus_right_mm_month:.3f} mm/mes)
indica mayor demanda de TerraClimate en promedio. Las diferencias pueden provenir
de la formulación (TerraClimate v1.1 emplea Penman-Monteith modificado por CO2),
las mallas, las climatologías y los datos meteorológicos parentales, y no deben
atribuirse automáticamente a error de uno de los productos.

## Independencia y limitaciones

La serie se identifica como TerraClimate v1.1. Su PET es ETo de referencia con
Penman-Monteith modificado por CO2. No es completamente independiente de
ERA5-Land: v1.1 incorpora anomalías mensuales ERA5, climatologías CHELSA y
correcciones de vapor CRU TS4.09. Es una comparación de producto, resolución y
formulación, no una validación independiente basada en estación. La ETo FAO-56
comparada mantiene cobertura espacial preliminar de {PRELIMINARY_COVERAGE_PCT:.4f} %;
no se interpreta como estimación final de la cuenca.
"""
    (ANNEX_OUT / "resumen_tecnico_terraclimate_1_1b.md").write_text(textwrap.dedent(summary), encoding="utf-8")
    print(f"TerraClimate validado: {len(times)} meses, {len(weights)} celdas ponderadas.")
    print(f"TerraClimate vs ETo: {len(terra_eto)} meses completos.")
    print(f"Tres productos: {len(three_products)} meses completos.")


if __name__ == "__main__":
    main()
