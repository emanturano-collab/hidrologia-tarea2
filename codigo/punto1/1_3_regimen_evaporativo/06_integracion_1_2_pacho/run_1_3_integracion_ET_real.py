"""Integra productos publicados del 1.2 de Pacho con el 1.3 existente.

Genera productos nuevos, sin recalcular ni reemplazar los resultados precedentes.
ET real: GLEAM4.3a y MOD16A2GF. ETo: FAO-56 preliminar (90.1264 % de cobertura).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
WORKSPACE = ROOT
INTEGRACION = ROOT / "datos/punto1/originales/1_2_intercambio_pacho"
OUT = ROOT / "datos/punto1/procesados/1_3_regimen_evaporativo"
TAB = ROOT / "productos/punto1/1_3_regimen_evaporativo/tablas"
FIG = ROOT / "productos/punto1/1_3_regimen_evaporativo/figuras"
ANN = ROOT / "anexos/punto1/1_3_regimen_evaporativo"
META = ROOT / "datos/punto1/metadatos"
T1 = ROOT / "datos/punto1/originales/tarea1_minimos/PE_200907_master_monthly.csv"
T1_SEASONS = ROOT / "datos/punto1/originales/tarea1_minimos/point1_monthly_hydroclimatic_classification.csv"
ETO = ROOT / "datos/punto1/procesados/1_1_a_fao56_preliminar_90pct/fao56_eto_mensual_preliminar_90pct.csv"
SOIL = OUT / "1_3_2_humedad_suelo_mensual_ponderada_198101_202308.csv"


def hydro_year(date: pd.Series) -> pd.Series:
    return date.dt.year + (date.dt.month >= 9).astype(int)


def fu(phi: np.ndarray | float, omega: float) -> np.ndarray | float:
    return 1 + phi - np.power(1 + np.power(phi, omega), 1 / omega)


def budyko_1974(phi: np.ndarray | float) -> np.ndarray | float:
    return phi * np.tanh(1 / phi) * np.power(1 - np.exp(-phi), 0.5)


def fit_fu(phi: float, ei: float) -> tuple[float, float]:
    if not (np.isfinite(phi) and np.isfinite(ei) and phi > 0 and 0 <= ei <= min(1, phi)):
        return np.nan, np.nan
    grid = np.linspace(1.001, 20, 19000)
    residual = fu(phi, grid) - ei
    idx = int(np.abs(residual).argmin())
    return float(grid[idx]), float(residual[idx])


def fu_derivative(phi: float, omega: float) -> float:
    return float(1 - phi ** (omega - 1) * (1 + phi ** omega) ** (1 / omega - 1))


def elasticity_fu(phi: float, omega: float) -> float:
    value = float(fu(phi, omega))
    return float(1 + phi * fu_derivative(phi, omega) / (1 - value))


def required(path: Path) -> Path:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


def save_table(frame: pd.DataFrame, name: str, overwrite: bool) -> Path:
    path = TAB / name
    if path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing product: {path}")
    frame.to_csv(path, index=False, encoding="utf-8")
    return path


def save_figure(figure: plt.Figure, stem: str, overwrite: bool) -> list[Path]:
    paths = [FIG / f"{stem}.png", FIG / f"{stem}.pdf"]
    if any(p.exists() for p in paths) and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing figure: {stem}")
    for path in paths:
        figure.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(figure)
    return paths


def main(overwrite: bool = False) -> None:
    for directory in (OUT, TAB, FIG, ANN, META):
        directory.mkdir(parents=True, exist_ok=True)
    gleam = pd.read_csv(required(ROOT / "productos/punto1/punto_1_2_4_gleam_et_mensual.csv"), parse_dates=["month"])
    mod16 = pd.read_csv(required(ROOT / "productos/punto1/punto_1_2_4_mod16_et_mensual.csv"), parse_dates=["month"])
    rn = pd.read_csv(required(ROOT / "productos/punto1/punto_1_2_3_radiacion_neta_real_era5land_mensual.csv"), parse_dates=["month"])
    eto = pd.read_csv(required(ETO), parse_dates=["month"])[["month", "eto_from_daily_mm"]]
    soil = pd.read_csv(required(SOIL), parse_dates=["date"])[["date", "theta_rz_0_100m3_m3"]].rename(columns={"date": "month"})
    master = pd.read_csv(required(T1), parse_dates=["date"])
    seasons = pd.read_csv(required(T1_SEASONS), encoding="utf-8")[['month', 'moisture_class', 'hydroclimatic_class']]

    # Validate source conventions before merging.
    assertions = {
        "gleam_rows": len(gleam), "mod16_rows": len(mod16), "rn_rows": len(rn),
        "gleam_duplicate_months": int(gleam.month.duplicated().sum()),
        "mod16_duplicate_months": int(mod16.month.duplicated().sum()),
        "rn_duplicate_months": int(rn.month.duplicated().sum()),
        "gleam_units": sorted(gleam.units.dropna().unique().tolist()),
        "rn_units": sorted(rn.ssr_source_units.dropna().unique().tolist()),
        "rn_complete_all": bool(rn.complete.all()),
        "rn_spatial_coverage_min_pct": float(rn.spatial_weight_covered_pct.min()),
        "gleam_coverage_min_pct": float(gleam.valid_spatial_coverage_percent.min()),
        "mod16_coverage_min_pct": float(mod16.min_composite_coverage_percent.min()),
    }
    if assertions["gleam_duplicate_months"] or assertions["mod16_duplicate_months"] or assertions["rn_duplicate_months"]:
        raise ValueError("A source has duplicate months")
    if assertions["gleam_units"] != ["mm/month"] or not assertions["rn_complete_all"]:
        raise ValueError("Unexpected ET units or incomplete Rn source")

    et = gleam[["month", "hydrological_year", "et_gleam_mm_month"]].merge(
        mod16[["month", "et_mm", "min_composite_coverage_percent"]], on="month", validate="one_to_one"
    ).merge(rn[["month", "energy_equivalent_mm_month", "rn_monthly_energy_j_m2"]], on="month", validate="one_to_one").merge(
        eto, on="month", validate="one_to_one"
    ).merge(soil, on="month", validate="one_to_one").merge(
        master[["date", "camels_precip_mm_month", "imerg_precip_mm_month", "runoff_mm_month"]],
        left_on="month", right_on="date", how="left", validate="one_to_one"
    ).drop(columns="date")
    et = et.rename(columns={"et_gleam_mm_month": "ET_GLEAM_mm_month", "et_mm": "ET_MOD16_mm_month", "eto_from_daily_mm": "ETo_FAO56_preliminar_mm_month", "camels_precip_mm_month": "PISCOp_mm_month", "imerg_precip_mm_month": "IMERG_mm_month"})
    et["hydrological_year"] = hydro_year(et.month)
    if len(et) != 252 or et[["ETo_FAO56_preliminar_mm_month", "theta_rz_0_100m3_m3", "PISCOp_mm_month"]].isna().any().any():
        raise ValueError("The common monthly analysis period is incomplete")
    for product in ("GLEAM", "MOD16"):
        et[f"ET_{product}_over_ETo"] = et[f"ET_{product}_mm_month"] / et.ETo_FAO56_preliminar_mm_month
        et[f"ET_{product}_over_PISCOp"] = et[f"ET_{product}_mm_month"] / et.PISCOp_mm_month
        et[f"ET_{product}_over_IMERG"] = et[f"ET_{product}_mm_month"] / et.IMERG_mm_month
        et[f"FE_{product}"] = et[f"ET_{product}_mm_month"] / et.energy_equivalent_mm_month

    # Explicit monthly classification. It is a diagnostic based on two independent ET products.
    clim = et.groupby(et.month.dt.month).agg(
        n=("month", "size"), PISCOp_mm_month=("PISCOp_mm_month", "mean"), IMERG_mm_month=("IMERG_mm_month", "mean"),
        ETo_mm_month=("ETo_FAO56_preliminar_mm_month", "mean"), theta_rz_m3_m3=("theta_rz_0_100m3_m3", "mean"),
        Rn_lambda_mm_month=("energy_equivalent_mm_month", "mean"),
        ET_GLEAM_mm_month=("ET_GLEAM_mm_month", "mean"), ET_MOD16_mm_month=("ET_MOD16_mm_month", "mean"),
        ET_GLEAM_over_ETo=("ET_GLEAM_over_ETo", "mean"), ET_MOD16_over_ETo=("ET_MOD16_over_ETo", "mean"),
        ET_GLEAM_over_PISCOp=("ET_GLEAM_over_PISCOp", "mean"), ET_MOD16_over_PISCOp=("ET_MOD16_over_PISCOp", "mean"),
        FE_GLEAM=("FE_GLEAM", "mean"), FE_MOD16=("FE_MOD16", "mean"),
    ).reset_index(names="calendar_month")
    clim["month_name"] = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    clim = clim.merge(seasons, left_on="calendar_month", right_on="month", how="left", validate="one_to_one").drop(columns="month")
    clim["ET_ETo_mean_two_products"] = (clim.ET_GLEAM_over_ETo + clim.ET_MOD16_over_ETo) / 2
    # Diagnostic thresholds declared here, not physical universal constants.
    clim["classification_rule"] = "energy: mean(ET/ETo)>=0.70; water: <=0.50; transition: otherwise"
    clim["limitation_class_preliminary"] = np.select(
        [clim.ET_ETo_mean_two_products >= .70, clim.ET_ETo_mean_two_products <= .50],
        ["energy-limited / water available", "water-limited"], default="transition"
    )
    clim["ET_GLEAM_minus_PISCOp_mm"] = clim.ET_GLEAM_mm_month - clim.PISCOp_mm_month
    clim["ET_MOD16_minus_PISCOp_mm"] = clim.ET_MOD16_mm_month - clim.PISCOp_mm_month
    save_table(clim, "1_3_integracion_1_3_1_climatologia_ET_ETo_ET_P.csv", overwrite)

    # FE and soil-water exploration. A breakpoint is a data diagnostic, not a critical threshold claim.
    fe_rows = []
    for product in ("GLEAM", "MOD16"):
        x = et.theta_rz_0_100m3_m3.to_numpy(); y = et[f"FE_{product}"].to_numpy()
        candidates = np.quantile(x, np.linspace(.15, .85, 71))
        best = None
        for knot in np.unique(candidates):
            design = np.column_stack([np.ones(len(x)), x, np.maximum(0, x - knot)])
            coef, *_ = np.linalg.lstsq(design, y, rcond=None)
            sse = float(np.square(y - design @ coef).sum())
            if best is None or sse < best[0]: best = (sse, knot, coef)
        corr_p = float(pd.Series(x).corr(pd.Series(y), method="pearson"))
        # Pearson correlation of average ranks is Spearman's rho; avoids an optional scipy dependency.
        corr_s = float(pd.Series(x).rank(method="average").corr(pd.Series(y).rank(method="average"), method="pearson"))
        fe_rows.append({"ET_product": product, "n_months": len(et), "FE_mean": float(y.mean()), "FE_min": float(y.min()), "FE_max": float(y.max()), "pearson_FE_theta": corr_p, "spearman_FE_theta": corr_s, "piecewise_knot_theta_m3_m3_exploratory": float(best[1]), "piecewise_slope_below": float(best[2][1]), "piecewise_slope_above": float(best[2][1] + best[2][2]), "piecewise_SSE": best[0], "interpretation": "Exploratory segmented fit; it is not a physical critical threshold without independent validation."})
    fe_summary = pd.DataFrame(fe_rows)
    save_table(fe_summary, "1_3_integracion_1_3_2_FE_humedad_resumen.csv", overwrite)
    save_table(et, "1_3_integracion_serie_mensual_ET_real_ETo_Rn_humedad.csv", overwrite)

    # Annual ET-product Budyko and elasticity. PISCOp is primary; IMERG is sensitivity.
    annual = et.groupby("hydrological_year").agg(
        months=("month", "size"), PISCOp_mm_year=("PISCOp_mm_month", "sum"), IMERG_mm_year=("IMERG_mm_month", "sum"),
        Q_mm_year=("runoff_mm_month", "sum"), ETo_mm_year=("ETo_FAO56_preliminar_mm_month", "sum"),
        ET_GLEAM_mm_year=("ET_GLEAM_mm_month", "sum"), ET_MOD16_mm_year=("ET_MOD16_mm_month", "sum"),
    ).reset_index()
    complete = annual.months.eq(12)
    results = []
    for et_product in ("GLEAM", "MOD16"):
        for precip in ("PISCOp", "IMERG"):
            subset = annual.loc[complete & annual[[f"{precip}_mm_year", f"ET_{et_product}_mm_year", "ETo_mm_year"]].notna().all(axis=1)].copy()
            pmean = subset[f"{precip}_mm_year"].mean(); etmean = subset[f"ET_{et_product}_mm_year"].mean(); etomean = subset.ETo_mm_year.mean()
            phi, ei = etomean / pmean, etmean / pmean
            omega, residual = fit_fu(phi, ei)
            subset[f"phi_{precip}"] = subset.ETo_mm_year / subset[f"{precip}_mm_year"]
            subset[f"EI_{et_product}_{precip}"] = subset[f"ET_{et_product}_mm_year"] / subset[f"{precip}_mm_year"]
            subset[f"Budyko1974_{precip}"] = budyko_1974(subset[f"phi_{precip}"])
            subset[f"vertical_distance_Budyko1974_{et_product}_{precip}"] = subset[f"EI_{et_product}_{precip}"] - subset[f"Budyko1974_{precip}"]
            additions = [f"EI_{et_product}_{precip}", f"vertical_distance_Budyko1974_{et_product}_{precip}"]
            if f"phi_{precip}" not in annual:
                additions.insert(0, f"phi_{precip}")
            annual = annual.merge(subset[["hydrological_year", *additions]], on="hydrological_year", how="left", validate="one_to_one")
            results.append({"ET_product": et_product, "precipitation": precip, "n_complete_hydrological_years": len(subset), "period": "AH 2002; AH 2004-AH 2023", "ETo_coverage_spatial_pct": 90.1264, "P_mean_mm_year": pmean, "ET_mean_mm_year": etmean, "ETo_mean_mm_year": etomean, "phi_ETo_over_P": phi, "EI_ET_over_P": ei, "omega_Fu": omega, "Fu_fit_residual": residual, "Budyko1974_at_mean_phi": float(budyko_1974(phi)), "vertical_distance_at_multiyear_mean": float(ei-budyko_1974(phi)), "elasticity_Fu_theoretical": elasticity_fu(phi, omega), "status": "preliminary: ETo 90.1264% coverage; product ET; no ΔS/regulation closure"})
    budyko = pd.DataFrame(results)
    save_table(budyko, "1_3_integracion_1_3_3_Budyko_ET_real_productos.csv", overwrite)
    save_table(annual, "1_3_integracion_1_3_3_trayectorias_anuales_ET_real.csv", overwrite)

    # Existing empirical values are retained as comparison, not recomputed.
    empirical = pd.DataFrame([
        {"precipitation": "PISCOp", "elasticity_empirical_existing": 1.488, "bootstrap_95pct": "0.927–1.786", "source": "existing 1.3.4, common-period Q/P diagnostic"},
        {"precipitation": "IMERG", "elasticity_empirical_existing": 1.475, "bootstrap_95pct": "0.473–2.216", "source": "existing 1.3.4, common-period Q/P diagnostic"},
    ])
    elastic = budyko.merge(empirical, on="precipitation", how="left")
    elastic["theoretical_minus_empirical"] = elastic.elasticity_Fu_theoretical - elastic.elasticity_empirical_existing
    save_table(elastic, "1_3_integracion_1_3_4_elasticidad_Fu_ET_real_vs_empirica.csv", overwrite)

    # Complementary relation, evaluated separately per product and source. No causal conclusion.
    relation = []
    for product in ("GLEAM", "MOD16"):
        for precip in ("PISCOp", "IMERG"):
            d = annual.loc[complete].copy(); q1, q2 = d[f"{precip}_mm_year"].quantile([1/3, 2/3])
            d["rain_class"] = pd.cut(d[f"{precip}_mm_year"], [-np.inf, q1, q2, np.inf], labels=["dry", "normal", "wet"], include_lowest=True)
            for klass, group in d.groupby("rain_class", observed=False):
                relation.append({"ET_product": product, "precipitation": precip, "rain_class": str(klass), "n_years": len(group), "P_mean_mm_year": group[f"{precip}_mm_year"].mean(), "ET_mean_mm_year": group[f"ET_{product}_mm_year"].mean(), "ETo_mean_mm_year": group.ETo_mm_year.mean(), "ET_ETo_mean": (group[f"ET_{product}_mm_year"] / group.ETo_mm_year).mean()})
            relation.append({"ET_product": product, "precipitation": precip, "rain_class": "correlation_all_years", "n_years": len(d), "P_mean_mm_year": d[f"{precip}_mm_year"].corr(d[f"ET_{product}_mm_year"], method="pearson"), "ET_mean_mm_year": d.ETo_mm_year.corr(d[f"ET_{product}_mm_year"], method="pearson"), "ETo_mean_mm_year": d[f"{precip}_mm_year"].corr(d.ETo_mm_year, method="pearson"), "ET_ETo_mean": np.nan})
    rel = pd.DataFrame(relation)
    save_table(rel, "1_3_integracion_1_3_5_relacion_ET_demanda_seco_humedo.csv", overwrite)

    receipt_manifest = json.loads((INTEGRACION / "MANIFIESTO_COPIA_INTEGRACION.json").read_text(encoding="utf-8-sig"))
    receipt = pd.DataFrame(receipt_manifest)
    receipt["origin"] = "Pacho: GitHub emanturano-collab/hidrologia-tarea2, branch punto-1.2, commit 588ff16b91d5c3533dc7077e72cd809bf3f20768"
    save_table(receipt, "1_3_integracion_inventario_archivos_recibidos_Pacho.csv", overwrite)
    status = pd.DataFrame([
        {"numeral": "1.3.1", "estado": "completado preliminar", "evidencia": "ET/ETo y ET/P de GLEAM y MOD16 para 12 meses; criterios explícitos; cruce con clase húmedo/seco de Tarea 1.", "pendiente": "Reducir incertidumbre de ETo (cobertura 90.1264%) y validar productos ET."},
        {"numeral": "1.3.2", "estado": "completado preliminar", "evidencia": "FE=λET/Rn mensual para GLEAM/MOD16 frente a θ radicular; correlaciones y ajuste segmentado exploratorio.", "pendiente": "No declarar umbral físico sin validación independiente y análisis de resolución."},
        {"numeral": "1.3.3", "estado": "actualizado preliminar", "evidencia": "Budyko con ET de productos, trayectorias anuales y documentos de regulación/trasvases.", "pendiente": "ΔS, operación/derivaciones, naturalización y ET/ETo con cobertura final."},
        {"numeral": "1.3.4", "estado": "actualizado preliminar", "evidencia": "Elasticidad Fu por producto y comparación con la elasticidad empírica existente.", "pendiente": "Incertidumbre conjunta de P, ET, ETo y Q regulado."},
        {"numeral": "1.3.5", "estado": "completado descriptivo preliminar", "evidencia": "ET y ETo por terciles secos/normales/húmedos; correlaciones descriptivas.", "pendiente": "No interpretar correlación como causalidad; validar demanda y productos."},
    ])
    save_table(status, "1_3_integracion_estado_cumplimiento_1_3_1_a_1_3_5.csv", overwrite)

    # Reusable figures.
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(clim.month_name, clim.ET_GLEAM_over_ETo, "o-", label="GLEAM / ETo")
    ax.plot(clim.month_name, clim.ET_MOD16_over_ETo, "o-", label="MOD16 / ETo")
    ax.axhline(.7, color="tab:green", ls="--", lw=.9); ax.axhline(.5, color="tab:red", ls="--", lw=.9)
    ax.set(ylabel="ET/ETo (-)", title="Racarumi: régimen evaporativo mensual (AH 2002; AH 2004-2023)")
    ax.legend(); save_figure(fig, "1_3_integracion_1_3_1_ET_sobre_ETo_mensual", overwrite)
    fig, ax = plt.subplots(figsize=(7.5, 5.5))
    ax.scatter(et.theta_rz_0_100m3_m3, et.FE_GLEAM, s=20, alpha=.65, label="GLEAM")
    ax.scatter(et.theta_rz_0_100m3_m3, et.FE_MOD16, s=20, alpha=.65, label="MOD16")
    ax.set(xlabel="Humedad radicular θ (m³/m³)", ylabel="FE = λET/Rn (-)", title="Fracción evaporativa y humedad del suelo")
    ax.legend(); save_figure(fig, "1_3_integracion_1_3_2_FE_vs_humedad", overwrite)
    fig, ax = plt.subplots(figsize=(7, 6)); x = np.linspace(.02, 3.5, 500)
    ax.plot(x, budyko_1974(x), "k--", label="Budyko (1974)"); ax.plot(x, np.minimum(x, 1), color="0.5", lw=.8, label="límites")
    colors = {"GLEAM": "#1f77b4", "MOD16": "#ff7f0e"}
    for _, row in budyko.loc[budyko.precipitation.eq("PISCOp")].iterrows():
        product = row.ET_product
        trajectory = annual[["hydrological_year", "phi_PISCOp", f"EI_{product}_PISCOp"]].dropna().sort_values("hydrological_year")
        ax.plot(trajectory.phi_PISCOp, trajectory[f"EI_{product}_PISCOp"], "o-", ms=2.6, lw=.7, alpha=.45, color=colors[product], label=f"{product}: trayectoria anual")
        ax.scatter(row.phi_ETo_over_P, row.EI_ET_over_P, s=65, color=colors[product], label=f"{product}: media")
        ax.plot(x, fu(x, row.omega_Fu), lw=1.2, color=colors[product])
    ax.set(xlim=(0, 2.2), ylim=(0, 1.1), xlabel="φ = ETo/P", ylabel="ET/P", title="Budyko con ET de productos; preliminar")
    ax.legend(fontsize=8); save_figure(fig, "1_3_integracion_1_3_3_Budyko_ET_real", overwrite)
    fig, ax = plt.subplots(figsize=(8, 4.8)); order = elastic.loc[elastic.precipitation.eq("PISCOp")].copy();
    ax.bar(np.arange(len(order))-.18, order.elasticity_Fu_theoretical, .36, label="Fu teórica")
    ax.bar(np.arange(len(order))+.18, order.elasticity_empirical_existing, .36, label="Empírica existente")
    ax.set_xticks(np.arange(len(order)), order.ET_product); ax.set(ylabel="Elasticidad (-)", title="Elasticidad teórica actualizada y empírica existente")
    ax.legend(); save_figure(fig, "1_3_integracion_1_3_4_elasticidad_ET_real", overwrite)
    fig, ax = plt.subplots(figsize=(8, 4.8)); d = rel[(rel.ET_product.eq("GLEAM")) & (rel.precipitation.eq("PISCOp")) & (rel.rain_class.isin(["dry","normal","wet"]))]
    ax.plot(d.rain_class, d.ET_mean_mm_year, "o-", label="ET GLEAM"); ax.plot(d.rain_class, d.ETo_mean_mm_year, "o-", label="ETo")
    ax.set(ylabel="mm/año", title="Años secos, normales y húmedos (PISCOp; terciles)"); ax.legend(); save_figure(fig, "1_3_integracion_1_3_5_ET_demanda_por_terciles", overwrite)

    inventory = {
        "pacho_commit": "588ff16b91d5c3533dc7077e72cd809bf3f20768",
        "source_branch": "punto-1.2", "source_zip_sha256": "F03FBA8DE7074D70D5BD6F93A05A7A0DF02DD4157FCC069FC4222707A6CEBB33",
        "integration_input_folder": str(INTEGRACION.relative_to(ROOT)).replace("\\\\", "/"),
        "source_qc": assertions, "common_months": int(len(et)), "common_hydrological_years": int(complete.sum()),
        "limitation": "ETo FAO-56 remains preliminary with 90.1264% spatial coverage; product ET and Rn are distinct products; no annual storage or operations closure.",
    }
    (META / "1_3_integracion_pacho_inventario_y_control_calidad.json").write_text(json.dumps(inventory, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = """# Integración 1.2 de Pacho con 1.3 — síntesis científica

## Datos integrados y periodo común

Se integraron GLEAM4.3a y MOD16A2GF como ET real mensual, junto con radiación neta
real de superficie de ERA5-Land (`SSR + STR`). El periodo común es AH 2002 y AH
2004–AH 2023: 252 meses y 21 años hidrológicos completos. ETo FAO-56 se conserva
como demanda atmosférica preliminar con cobertura espacial de 90.1264 %.

## Interpretación prudente

ET/ETo y ET/P se presentan por producto y no se promedian como si fueran una
observación. FE es `ET/(Rn/lambda)` en escala mensual; no se reemplazó por ET/ETo.
El ajuste segmentado de FE frente a humedad es exploratorio y no constituye un
umbral físico crítico sin validación independiente y evaluación de resolución.

En Budyko se usan ET de productos para los puntos anuales, conforme a la guía.
Por tanto no se trata P−Q como ET anual. El contraste P−Q queda como diagnóstico
condicionado a ΔS, regulación, extracciones y trasvases; estos factores permanecen
en la interpretación documental del numeral 1.3.3.

La relación ET–demanda se evalúa con terciles de lluvia, ET de cada producto y ETo
FAO-56. Las correlaciones son descriptivas: no demuestran causalidad ni la relación
complementaria por sí solas.

## Resultados clave

- La clasificación explícita de ET/ETo medio de GLEAM y MOD16 identifica enero–mayo
  como meses de agua relativamente disponible/limitados por energía; junio, octubre,
  noviembre y diciembre como transición; julio–septiembre como limitados por agua.
  La clasificación es consistente con la fase húmeda de enero–abril y la fase seca
  de junio–septiembre de Tarea 1, aunque mayo se comporta como transición pluvial.
- Con PISCOp, ET mensual excede P en mayo–septiembre para GLEAM y mayo–agosto para
  MOD16. Esto es compatible con liberación de almacenamiento, aportes/regulación,
  desfases o sesgo de productos; no cuantifica ninguno de esos mecanismos.
- FE media es 0.427 (GLEAM) y 0.460 (MOD16); sus correlaciones Pearson con humedad
  radicular son 0.920 y 0.909, respectivamente. Los quiebres segmentados quedan como
  diagnósticos exploratorios, no como umbrales críticos.
- Con PISCOp, GLEAM da `φ=1.082`, `ET/P=0.671`, `ω=2.284` y distancia a Budyko de
  0.030; MOD16 da `ET/P=0.720`, `ω=2.594` y distancia 0.080. IMERG genera ET/P>1;
  por ello no admite ajuste Fu y se conserva solo como sensibilidad de precipitación.
- En terciles PISCOp, ambos productos muestran ET mayor en años húmedos y ETo menor
  en dichos años; la relación es descriptiva y no establece causalidad.

## Estado de cumplimiento

- 1.3.1: completado preliminarmente con dos productos ET y criterios explícitos.
- 1.3.2: completado preliminarmente para FE y humedad; el supuesto umbral sigue
  siendo exploratorio.
- 1.3.3: actualizado con ET de productos; falta cierre de ΔS y operación.
- 1.3.4: elasticidad teórica recalculada por producto; comparación empírica con
  incertidumbre existente, sin atribución causal.
- 1.3.5: comparación descriptiva completada con ambos productos; no causal.
"""
    path = ANN / "1_3_integracion_pacho_sintesis_cientifica.md"
    if path.exists() and not overwrite: raise FileExistsError(path)
    path.write_text(summary, encoding="utf-8")
    print(json.dumps({"rows_monthly": len(et), "years": int(complete.sum()), "budyko": results, "FE": fe_rows}, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--overwrite", action="store_true")
    main(**vars(parser.parse_args()))
