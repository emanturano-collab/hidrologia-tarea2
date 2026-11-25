"""Ejecuta las comprobaciones locales disponibles para el apartado 1.1.b.

No modifica datos fuente ni productos del apartado 1.1.a.  Lee la serie diaria
CAMELS-PE de Racarumi y la ETo FAO-56 preliminar ya calculada, conserva solo
meses completos y produce: (i) comparación PISCOeo_pm--ERA5-Land y
(ii) balance físico P-Q frente a ETo.  La cobertura de la ETo es 90.1264 %, por
lo que todos los productos de este script son explícitamente preliminares.
"""

from __future__ import annotations

from pathlib import Path
import calendar
import textwrap

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
CAMELS_DAILY = (
    ROOT / "datos" / "punto1" / "tarea1" / "PE_200907.csv"
)
STATION_METADATA = ROOT / "datos" / "punto1" / "originales" / "tarea1_minimos" / "station.csv"
ETO_DAILY = (
    ROOT / "datos" / "punto1" / "procesados"
    / "1_1_a_fao56_preliminar_90pct" / "fao56_eto_diaria_preliminar_90pct.csv"
)

CODE_DIR = Path(__file__).resolve().parent
DATA_OUT = ROOT / "datos" / "punto1" / "procesados" / "1_1_b_pruebas_referencia"
TABLE_OUT = ROOT / "productos" / "punto1" / "1_1_demanda_atmosferica" / "tablas"
FIG_OUT = ROOT / "productos" / "punto1" / "1_1_demanda_atmosferica" / "figuras"
ANNEX_OUT = ROOT / "anexos" / "punto1" / "1_1_b_pruebas_referencia"

PRELIMINARY_COVERAGE_PCT = 90.12637836877098


def require_file(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"No se encontró el insumo requerido: {path}")


def monthly_from_complete_days(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Acumula valores diarios por mes solamente si todos los días existen."""
    data = frame[["date", *columns]].copy()
    data["month"] = data["date"].dt.to_period("M")
    rows: list[dict[str, object]] = []
    for month, group in data.groupby("month", sort=True):
        expected = calendar.monthrange(month.year, month.month)[1]
        # Se requiere una fecha por cada día y una observación finita de cada variable.
        valid_dates = group["date"].nunique() == expected
        valid_values = all(group[col].notna().sum() == expected for col in columns)
        if valid_dates and valid_values:
            row: dict[str, object] = {"month": month.to_timestamp(), "days_in_month": expected}
            row.update({f"{col}_mm_month": group[col].sum() for col in columns})
            rows.append(row)
    return pd.DataFrame(rows)


def metrics(observed: pd.Series, reference: pd.Series) -> dict[str, float | int]:
    delta = observed - reference
    # Spearman es la correlación de Pearson aplicada a los rangos. Se implementa
    # así para que el flujo no dependa de scipy en el entorno del curso.
    spearman = observed.rank(method="average").corr(reference.rank(method="average"))
    return {
        "n_months": int(len(delta)),
        "pearson_r": float(observed.corr(reference, method="pearson")),
        "spearman_rho": float(spearman),
        "bias_pet_minus_eto_mm_month": float(delta.mean()),
        "mae_mm_month": float(delta.abs().mean()),
        "rmse_mm_month": float(np.sqrt((delta**2).mean())),
    }


def save_figure(fig: plt.Figure, name: str) -> None:
    for suffix in ("png", "pdf"):
        fig.savefig(FIG_OUT / f"{name}.{suffix}", dpi=220 if suffix == "png" else None,
                    bbox_inches="tight")
    plt.close(fig)


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distancia esférica sólo para priorizar estaciones candidatas."""
    radius_km = 6371.0088
    phi1, phi2 = np.radians([lat1, lat2])
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2) ** 2
    return float(2 * radius_km * np.arcsin(np.sqrt(a)))


def main() -> None:
    for directory in (DATA_OUT, TABLE_OUT, FIG_OUT, ANNEX_OUT):
        directory.mkdir(parents=True, exist_ok=True)
    for source in (CAMELS_DAILY, STATION_METADATA, ETO_DAILY):
        require_file(source)

    camels = pd.read_csv(CAMELS_DAILY, parse_dates=["date"])
    eto = pd.read_csv(ETO_DAILY, parse_dates=["date"])
    required_camels = ["prec", "flow_obs", "pet"]
    missing = set(required_camels) - set(camels.columns)
    if missing:
        raise ValueError(f"Faltan columnas CAMELS-PE requeridas: {sorted(missing)}")
    if "eto_fao56_mm_d" not in eto:
        raise ValueError("No existe eto_fao56_mm_d en el producto preliminar de 1.1.a.")

    # 1) Comparación de demanda: PET CAMELS-PE (PISCOeo_pm) y ETo preliminar.
    pet_monthly = monthly_from_complete_days(camels.rename(columns={"pet": "pet"}), ["pet"])
    eto_monthly = monthly_from_complete_days(
        eto.rename(columns={"eto_fao56_mm_d": "eto"}), ["eto"]
    )
    comparison = pet_monthly.merge(eto_monthly, on="month", how="inner")
    comparison = comparison.rename(columns={
        "pet_mm_month": "pet_piscoeopm_mm_month",
        "eto_mm_month": "eto_era5land_preliminar_mm_month",
        "days_in_month_x": "days_in_month",
    }).drop(columns=["days_in_month_y"])
    comparison["difference_pet_minus_eto_mm_month"] = (
        comparison["pet_piscoeopm_mm_month"] - comparison["eto_era5land_preliminar_mm_month"]
    )
    comparison["ratio_pet_to_eto"] = (
        comparison["pet_piscoeopm_mm_month"] / comparison["eto_era5land_preliminar_mm_month"]
    )
    comparison.to_csv(DATA_OUT / "camels_pet_piscoeopm_vs_eto_preliminar_mensual.csv", index=False)
    comparison.to_csv(TABLE_OUT / "1_1b_pet_piscoeopm_vs_eto_preliminar_mensual.csv", index=False)

    demand_metrics = metrics(
        comparison["pet_piscoeopm_mm_month"], comparison["eto_era5land_preliminar_mm_month"]
    )
    demand_metrics.update({
        "comparison": "PISCOeo_pm (CAMELS-PE pet) menos ETo FAO-56 ERA5-Land",
        "period_start": comparison["month"].min().date().isoformat(),
        "period_end": comparison["month"].max().date().isoformat(),
        "units": "mm/month",
        "eto_spatial_coverage_pct": PRELIMINARY_COVERAGE_PCT,
        "status": "PRELIMINAR: la ETo ERA5-Land conserva 9.8736 % de cobertura espacial pendiente",
    })

    # 2) Chequeo físico: P-Q es una aproximación de ET real sólo a largo plazo.
    hydro_monthly = monthly_from_complete_days(camels, ["prec", "flow_obs"])
    physical = hydro_monthly.merge(eto_monthly, on="month", how="inner")
    physical = physical.rename(columns={
        "prec_mm_month": "precipitation_p_mm_month",
        "flow_obs_mm_month": "runoff_q_mm_month",
        "eto_mm_month": "eto_era5land_preliminar_mm_month",
        "days_in_month_x": "days_in_month",
    }).drop(columns=["days_in_month_y"])
    physical["p_minus_q_mm_month"] = (
        physical["precipitation_p_mm_month"] - physical["runoff_q_mm_month"]
    )
    physical["eto_minus_p_minus_q_mm_month"] = (
        physical["eto_era5land_preliminar_mm_month"] - physical["p_minus_q_mm_month"]
    )
    physical["year"] = physical["month"].dt.year
    physical.to_csv(DATA_OUT / "balance_fisico_p_q_eto_preliminar_mensual.csv", index=False)
    physical.to_csv(TABLE_OUT / "1_1b_balance_fisico_p_q_eto_preliminar_mensual.csv", index=False)

    complete_years = []
    for year, group in physical.groupby("year", sort=True):
        if len(group) == 12 and group["month"].dt.month.nunique() == 12:
            complete_years.append({
                "year": int(year),
                "precipitation_p_mm_year": group["precipitation_p_mm_month"].sum(),
                "runoff_q_mm_year": group["runoff_q_mm_month"].sum(),
                "p_minus_q_mm_year": group["p_minus_q_mm_month"].sum(),
                "eto_era5land_preliminar_mm_year": group["eto_era5land_preliminar_mm_month"].sum(),
            })
    annual = pd.DataFrame(complete_years)
    if annual.empty:
        raise ValueError("No hay años completos P-Q-ETo para la comprobación física.")
    annual["eto_minus_p_minus_q_mm_year"] = (
        annual["eto_era5land_preliminar_mm_year"] - annual["p_minus_q_mm_year"]
    )
    annual.to_csv(DATA_OUT / "balance_fisico_p_q_eto_preliminar_anual_completo.csv", index=False)
    annual.to_csv(TABLE_OUT / "1_1b_balance_fisico_p_q_eto_preliminar_anual_completo.csv", index=False)

    physical_summary = pd.DataFrame([{
        "period_start": f"{int(annual.year.min())}-01-01",
        "period_end": f"{int(annual.year.max())}-12-31",
        "n_complete_years": int(len(annual)),
        "mean_annual_p_mm": annual["precipitation_p_mm_year"].mean(),
        "mean_annual_q_mm": annual["runoff_q_mm_year"].mean(),
        "mean_annual_p_minus_q_mm": annual["p_minus_q_mm_year"].mean(),
        "mean_annual_eto_preliminar_mm": annual["eto_era5land_preliminar_mm_year"].mean(),
        "mean_annual_eto_minus_p_minus_q_mm": annual["eto_minus_p_minus_q_mm_year"].mean(),
        "eto_less_than_p_minus_q": bool(
            annual["eto_era5land_preliminar_mm_year"].mean()
            < annual["p_minus_q_mm_year"].mean()
        ),
        "eto_spatial_coverage_pct": PRELIMINARY_COVERAGE_PCT,
        "interpretation": (
            "P-Q aproxima ET real de largo plazo sólo si cambios de almacenamiento y "
            "transferencias son despreciables; no es una referencia directa de ETo."
        ),
    }])
    physical_summary.to_csv(TABLE_OUT / "1_1b_comprobacion_fisica_resumen.csv", index=False)

    pd.DataFrame([demand_metrics]).to_csv(TABLE_OUT / "1_1b_metricas_pet_piscoeopm_vs_eto.csv", index=False)

    # Inventario de la única estación entregada en CAMELS-PE: es hidrométrica, no meteorológica.
    gauge = pd.read_csv(STATION_METADATA).iloc[0]
    station_rows = [{
        "identifier": gauge["gauge_id"], "name": gauge["gauge_name"],
        "latitude": gauge["gauge_lat"], "longitude": gauge["gauge_lon"],
        "elevation_m": gauge["gauge_elev"], "record_start": gauge["gauge_record_start"],
        "record_end": gauge["gauge_record_end"], "observed_streamflow_pct": gauge["gauge_perc_obs"],
        "source": "CAMELS-PE / SENAMHI", "station_role": "aforo / caudal observado",
        "tmax_tmin": "no disponible como observación de estación", "humidity": "no disponible",
        "wind": "no disponible", "radiation": "no disponible", "pressure": "no disponible",
        "eligible_for_station_fao56": False,
        "decision": "No permite recalcular ETo de estación; se requiere serie meteorológica observada."
    }]
    # Candidatas publicadas para el sistema Chancay-Lambayeque. Se anotan sólo
    # como candidatas: no se descargaron registros ni se presume qué variables o
    # continuidad tienen hasta verificarlas en el portal oficial de SENAMHI.
    candidates = [
        ("SENAMHI_CAND_CHUGUR", "Chugur", -6.669450, -78.738072, 2742.0),
        ("SENAMHI_CAND_LLAMA", "Llama", -6.514431, -79.122764, 2096.0),
        ("SENAMHI_CAND_CHANCAY_BANOS", "Chancay Baños", -6.574892, -78.867211, 1639.0),
        ("SENAMHI_CAND_RACARRUMI", "Racarrumi", -6.633244, -79.309761, 254.0),
    ]
    for identifier, name, lat, lon, elevation in candidates:
        station_rows.append({
            "identifier": identifier, "name": name, "latitude": lat, "longitude": lon,
            "elevation_m": elevation, "record_start": "por verificar", "record_end": "por verificar",
            "observed_streamflow_pct": np.nan,
            "source": "Candidata publicada para Chancay-Lambayeque; verificación requerida en SENAMHI",
            "station_role": "tipo y variables por verificar", "tmax_tmin": "por verificar",
            "humidity": "por verificar", "wind": "por verificar", "radiation": "por verificar",
            "pressure": "por verificar", "eligible_for_station_fao56": False,
            "decision": (
                "No elegible hasta confirmar tipo de estación, periodo, continuidad y variables observadas. "
                f"Distancia aproximada al aforo Racarumi: {haversine_km(float(gauge['gauge_lat']), float(gauge['gauge_lon']), lat, lon):.1f} km."
            ),
        })
    station_inventory = pd.DataFrame(station_rows)
    station_inventory.to_csv(ANNEX_OUT / "inventario_estaciones_disponibles.csv", index=False)

    inventory_rows = []
    for variable, meaning, source, usable in [
        ("prec", "Precipitación de cuenca", "PISCOp v2.1 / CAMELS-PE", "Sí, balance P-Q"),
        ("flow_obs", "Caudal observado como lámina", "SENAMHI / CAMELS-PE", "Sí, balance P-Q"),
        ("pet", "ETo/PET de referencia", "PISCOeo_pm v1.0 / CAMELS-PE", "Sí, contraste de producto"),
        ("tmin", "Temperatura mínima grillada", "PISCOt v1.2 / CAMELS-PE", "No, no es estación"),
        ("tmean", "Temperatura media grillada", "PISCOt v1.2 / CAMELS-PE", "No, no es estación"),
        ("tmax", "Temperatura máxima grillada", "PISCOt v1.2 / CAMELS-PE", "No, no es estación"),
        ("srad", "Radiación solar grillada", "ERA5-Land / CAMELS-PE", "No, no es estación"),
        ("vprp", "Presión de vapor grillada", "ERA5-Land / CAMELS-PE", "No, no es estación"),
    ]:
        series = camels.loc[camels[variable].notna(), ["date", variable]]
        inventory_rows.append({
            "variable": variable, "meaning": meaning, "source": source,
            "unit": "mm/day" if variable in {"prec", "flow_obs", "pet"} else (
                "degC" if variable.startswith("t") else ("MJ/m2/day" if variable == "srad" else "hPa")
            ),
            "first_valid_date": series["date"].min().date().isoformat(),
            "last_valid_date": series["date"].max().date().isoformat(),
            "n_valid_daily_records": int(len(series)), "usable_in_1_1b": usable,
        })
    inventory_rows.extend([
        {"variable": "pan_evaporation", "meaning": "Evaporación de tanque", "source": "No localizada en Tarea 1/2",
         "unit": "no disponible", "first_valid_date": "", "last_valid_date": "", "n_valid_daily_records": 0,
         "usable_in_1_1b": "No; requeriría observación y coeficiente de tanque justificado"},
        {"variable": "meteorological_station_FAO56", "meaning": "Tmax/Tmin, humedad, viento, radiación/presión observadas",
         "source": "No localizada en archivos locales", "unit": "no disponible", "first_valid_date": "", "last_valid_date": "",
         "n_valid_daily_records": 0, "usable_in_1_1b": "No; consultar candidatas SENAMHI/GHCNh"},
    ])
    pd.DataFrame(inventory_rows).to_csv(ANNEX_OUT / "inventario_datos_disponibles_y_faltantes.csv", index=False)

    sources = pd.DataFrame([
        {"source_id": "CAMELS_PE_local", "resource": str(CAMELS_DAILY.relative_to(ROOT)),
         "use": "precipitación P, caudal observado Q y pet", "temporal_resolution": "diaria",
         "notes": "CAMELS-PE entrega PISCOp, caudal observado SENAMHI y pet PISCOeo_pm."},
        {"source_id": "PISCOeo_pm", "resource": "https://doi.org/10.1038/s41597-022-01373-8",
         "use": "producto comparativo de demanda", "temporal_resolution": "diaria",
         "notes": "ETo FAO Penman-Monteith grillada; 1981-2016; metodología distinta pero no independiente del método FAO-56."},
        {"source_id": "FAO56_preliminar", "resource": str(ETO_DAILY.relative_to(ROOT)),
         "use": "ETo de referencia para comparación y P-Q", "temporal_resolution": "diaria",
         "notes": "ERA5-Land ponderada sobre 20 celdas; cobertura espacial 90.1264 %, no final."},
        {"source_id": "FAO56_manual", "resource": "https://www.fao.org/4/X0490E/x0490e06.htm",
         "use": "definición de ETo FAO Penman-Monteith", "temporal_resolution": "no aplica",
         "notes": "Fuente metodológica de la ecuación de referencia."},
        {"source_id": "SENAMHI_portal", "resource": "https://tendhis.sispac.net.pe/investigadores/datos/",
         "use": "verificar y, si procede, obtener estación meteorológica candidata", "temporal_resolution": "según estación",
         "notes": "El portal permite consulta y descarga por estación; no se descargaron series en este flujo."},
        {"source_id": "NOAA_GHCND_inventory", "resource": "https://gis.ncdc.noaa.gov/arcgis/rest/services/cdo/ghcnd/MapServer/0",
         "use": "cribado de estaciones GHCN-D cercanas", "temporal_resolution": "diaria",
         "notes": "Consulta espacial 2026-11-21: cero estaciones GHCN-D en -79.8..-78.5, -7.1..-6.1. No infiere ausencia en GHCN-Hourly."},
    ])
    sources.to_csv(ANNEX_OUT / "registro_fuentes_1_1b.csv", index=False)

    # Figuras de demanda.
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(comparison["month"], comparison["pet_piscoeopm_mm_month"], label="PET CAMELS-PE (PISCOeo_pm)", lw=1.0)
    ax.plot(comparison["month"], comparison["eto_era5land_preliminar_mm_month"], label="ETo FAO-56 ERA5-Land (preliminar)", lw=1.0)
    ax.set(title="Racarumi: comparación mensual de demanda evaporativa", ylabel="mm/mes", xlabel="Mes")
    ax.legend(ncol=2, fontsize=8); ax.grid(alpha=.25)
    save_figure(fig, "1_1b_pet_piscoeopm_vs_eto_serie_mensual")

    fig, ax = plt.subplots(figsize=(5.5, 5.2))
    x = comparison["eto_era5land_preliminar_mm_month"]
    y = comparison["pet_piscoeopm_mm_month"]
    ax.scatter(x, y, s=13, alpha=.6)
    limits = [min(x.min(), y.min()), max(x.max(), y.max())]
    ax.plot(limits, limits, "k--", lw=1, label="1:1")
    ax.set(xlabel="ETo FAO-56 ERA5-Land preliminar (mm/mes)", ylabel="PET PISCOeo_pm (mm/mes)",
           title="Racarumi: dispersión mensual")
    ax.legend(); ax.grid(alpha=.25)
    save_figure(fig, "1_1b_pet_piscoeopm_vs_eto_dispersion")

    climatology = comparison.assign(calendar_month=comparison["month"].dt.month).groupby("calendar_month").agg(
        pet_piscoeopm_mm_month=("pet_piscoeopm_mm_month", "mean"),
        eto_era5land_preliminar_mm_month=("eto_era5land_preliminar_mm_month", "mean"),
        difference_pet_minus_eto_mm_month=("difference_pet_minus_eto_mm_month", "mean"),
    ).reset_index()
    climatology.to_csv(TABLE_OUT / "1_1b_climatologia_pet_piscoeopm_vs_eto.csv", index=False)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(climatology.calendar_month, climatology.pet_piscoeopm_mm_month, marker="o", label="PET PISCOeo_pm")
    ax.plot(climatology.calendar_month, climatology.eto_era5land_preliminar_mm_month, marker="o", label="ETo ERA5-Land preliminar")
    ax.set(xticks=range(1,13), xlabel="Mes", ylabel="mm/mes", title="Racarumi: climatología mensual en periodo común")
    ax.legend(); ax.grid(alpha=.25)
    save_figure(fig, "1_1b_pet_piscoeopm_vs_eto_climatologia")

    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(annual.year, annual.precipitation_p_mm_year, label="P", lw=1.2)
    ax.plot(annual.year, annual.runoff_q_mm_year, label="Q", lw=1.2)
    ax.plot(annual.year, annual.p_minus_q_mm_year, label="P-Q (aprox. ET real)", lw=1.2)
    ax.plot(annual.year, annual.eto_era5land_preliminar_mm_year, label="ETo preliminar", lw=1.2)
    ax.set(title="Racarumi: comprobación física anual (sólo años completos)", xlabel="Año", ylabel="mm/año")
    ax.legend(ncol=2, fontsize=8); ax.grid(alpha=.25)
    save_figure(fig, "1_1b_comprobacion_fisica_p_q_eto_anual")

    summary = f"""# Apartado 1.1.b - resultados reproducibles disponibles

## Estado y alcance

Se ejecutaron dos comprobaciones que no requieren descargas nuevas: comparación
con PET de CAMELS-PE/PISCOeo_pm y comprobación física P-Q. La ETo usada sigue
siendo la versión **preliminar** con {PRELIMINARY_COVERAGE_PCT:.4f} % de cobertura
espacial; faltan celdas ERA5-Land, por lo que no representa un resultado final de
cuenca.

## Producto de demanda comparativo

Periodo común de meses completos: {demand_metrics['period_start']} a {demand_metrics['period_end']}.
N = {demand_metrics['n_months']} meses. Pearson = {demand_metrics['pearson_r']:.4f};
Spearman = {demand_metrics['spearman_rho']:.4f}; sesgo PET-ETo =
{demand_metrics['bias_pet_minus_eto_mm_month']:.3f} mm/mes; MAE =
{demand_metrics['mae_mm_month']:.3f} mm/mes; RMSE = {demand_metrics['rmse_mm_month']:.3f} mm/mes.

PISCOeo_pm es una serie independiente en sus insumos espaciales y resolución,
pero utiliza igualmente FAO Penman-Monteith. Por tanto, funciona como contraste
de producto, no como validación observacional independiente.

## Comprobación física P-Q

Usando {len(annual)} años completos ({int(annual.year.min())}-{int(annual.year.max())}):
P = {physical_summary.iloc[0]['mean_annual_p_mm']:.2f} mm/año; Q =
{physical_summary.iloc[0]['mean_annual_q_mm']:.2f} mm/año; P-Q =
{physical_summary.iloc[0]['mean_annual_p_minus_q_mm']:.2f} mm/año; ETo preliminar =
{physical_summary.iloc[0]['mean_annual_eto_preliminar_mm']:.2f} mm/año.
ETo - (P-Q) = {physical_summary.iloc[0]['mean_annual_eto_minus_p_minus_q_mm']:.2f} mm/año.

P-Q aproxima evapotranspiración real de largo plazo sólo con cambios de
almacenamiento y transferencias despreciables; no es una referencia directa de
ETo. Cualquier incoherencia requiere revisar representatividad de P, regulación,
transferencias, flujo subterráneo y almacenamiento; no se corrige alterando datos.

## Prueba de estación / estado de cumplimiento

El archivo local de estación identifica Racarumi como punto de aforo con caudal
observado y no contiene Tmax/Tmin observadas, humedad, viento, radiación o
presión. Por ello no permite recalcular una ETo de estación. No se ha inventado
ni estimado arbitrariamente una estación. El inventario prioriza Racarrumi
(~0.8 km) y Llama (~25.2 km) como candidatas SENAMHI, pero tipo, periodo y
variables deben confirmarse antes de considerarlas elegibles. La solicitud
manual está en `solicitud_manual_estacion_senamhi.md`. Hasta contar con una
serie meteorológica observada o datos de tanque, sólo se cumple una de las tres
categorías de contraste exigidas por la guía (producto de demanda), y el apartado
1.1.b no está terminado.
"""
    (ANNEX_OUT / "resumen_tecnico_1_1b.md").write_text(textwrap.dedent(summary), encoding="utf-8")
    print(f"Comparación PET/ETo: {len(comparison)} meses completos.")
    print(f"Comprobación P-Q/ETo: {len(annual)} años completos.")
    print(f"Productos: {TABLE_OUT}")


if __name__ == "__main__":
    main()
