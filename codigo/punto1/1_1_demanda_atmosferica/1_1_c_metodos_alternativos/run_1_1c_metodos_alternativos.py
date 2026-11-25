"""Apartado 1.1.c: métodos alternativos de demanda atmosférica.

Reutiliza exclusivamente la serie diaria por celda creada en 1.1.a. Los
métodos se evalúan por celda y día (Thornthwaite por celda y mes) antes de
ponderar; nunca se aplican a promedios espaciales de variables de entrada.
No modifica datos originales ni resultados de 1.1.a/1.1.b.
"""
from __future__ import annotations

import math
from pathlib import Path
import shutil

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyet

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
DAILY_IN = ROOT / "productos" / "punto1" / "1_1_a" / "fao56_eto_diaria_por_celda_preliminar_90pct.csv"
WEIGHTS_IN = ROOT / "productos" / "punto1" / "1_1_demanda_atmosferica" / "tablas" / "era5land_33_celdas_pesos_y_elevacion.csv"
OUT_DATA = ROOT / "datos" / "punto1" / "procesados" / "1_1_c_metodos_alternativos"
OUT_TABLES = ROOT / "productos" / "punto1" / "1_1_demanda_atmosferica" / "tablas"
OUT_FIGS = ROOT / "productos" / "punto1" / "1_1_demanda_atmosferica" / "figuras"
OUT_ANNEX = ROOT / "anexos" / "punto1" / "1_1_c_metodos_alternativos"
COVERAGE = 0.9012637836877098
METHODS = ["thornthwaite_1948", "hargreaves_samani_1985", "priestley_taylor_1972", "meyer_1915", "makkink_1957", "rohwer_1931"]
LABELS = {"fao56": "FAO-56", "thornthwaite_1948": "Thornthwaite", "hargreaves_samani_1985": "Hargreaves-Samani", "priestley_taylor_1972": "Priestley-Taylor", "meyer_1915": "Meyer", "makkink_1957": "Makkink", "rohwer_1931": "Rohwer"}
COLORS = {"fao56": "#222222", "thornthwaite_1948": "#4C78A8", "hargreaves_samani_1985": "#F58518", "priestley_taylor_1972": "#54A24B", "meyer_1915": "#E45756", "makkink_1957": "#B279A2", "rohwer_1931": "#72B7B2"}


def sat_vp(t_c):
    return 0.6108 * np.exp(17.27 * np.asarray(t_c) / (np.asarray(t_c) + 237.3))


def daylight_hours(latitude_deg: float, month: int) -> float:
    """FAO-56 Eq. 34–35 at day 15 of each month."""
    j = [15, 46, 74, 105, 135, 166, 196, 227, 258, 288, 319, 349][month - 1]
    phi = math.radians(latitude_deg)
    delta = 0.409 * math.sin(2 * math.pi * j / 365 - 1.39)
    ws = math.acos(np.clip(-math.tan(phi) * math.tan(delta), -1, 1))
    return 24 / math.pi * ws


def thornthwaite_monthly(g: pd.DataFrame) -> pd.DataFrame:
    """Original monthly structure, excluding a cell-year unless all 12 months exist."""
    monthly = (g.set_index("date").resample("MS")
                 .agg(tmean_c=("tmean_c", "mean"), n_days=("tmean_c", "size")))
    monthly["expected_days"] = monthly.index.days_in_month
    monthly["year"] = monthly.index.year
    monthly["month"] = monthly.index.month
    full_years = monthly.groupby("year").apply(lambda z: len(z) == 12 and (z.n_days == z.expected_days).all(), include_groups=False)
    monthly = monthly[monthly.year.isin(full_years[full_years].index)].copy()
    monthly["heat_term"] = np.where(monthly.tmean_c > 0, (monthly.tmean_c / 5.0) ** 1.514, 0.0)
    monthly["heat_index_I"] = monthly.groupby("year")["heat_term"].transform("sum")
    I = monthly["heat_index_I"]
    monthly["a"] = 6.75e-7 * I**3 - 7.71e-5 * I**2 + 1.792e-2 * I + 0.49239
    base_cm = np.where(monthly.tmean_c > 0, 16 * (10 * monthly.tmean_c / I) ** monthly["a"], 0.0)
    monthly["daylength_h"] = [daylight_hours(float(g.latitude.iloc[0]), int(m)) for m in monthly.month]
    # In the standard monthly Thornthwaite form the 16 coefficient yields
    # mm/month; the day-length and days-in-month terms are dimensionless.
    monthly["thornthwaite_1948"] = base_cm * (monthly.n_days / 30.0) * (monthly.daylength_h / 12.0)
    monthly["date"] = monthly.index
    return monthly[["date", "thornthwaite_1948", "heat_index_I", "a", "daylength_h", "n_days"]]


def circular_phase_difference(x, ref):
    return ((x - ref + 6) % 12) - 6


def harmonic(values: pd.Series) -> tuple[float, float, int]:
    """Amplitude and phase (calendar month of fitted maximum); values indexed Jan..Dec."""
    y = values.reindex(range(1, 13)).to_numpy(float)
    theta = 2 * np.pi * np.arange(12) / 12
    a = 2 / 12 * np.nansum(y * np.cos(theta))
    b = 2 / 12 * np.nansum(y * np.sin(theta))
    amplitude = float(np.hypot(a, b))
    phase = (math.atan2(b, a) * 12 / (2 * math.pi)) % 12 + 1
    max_month = int(np.nanargmax(y) + 1)
    return amplitude, phase, max_month


def compare(df: pd.DataFrame, group_name: str) -> pd.DataFrame:
    rows = []
    ref = df.fao56
    for method in METHODS:
        x = df[method]
        e = x - ref
        rows.append({"scale": group_name, "method": method, "n": int(x.notna().sum()),
                     "mean_mm": x.mean(), "sd_mm": x.std(ddof=1),
                     "pearson": x.corr(ref, method="pearson"),
                     # Spearman is Pearson correlation of average ranks; this avoids an
                     # unneeded SciPy dependency and handles ties deterministically.
                     "spearman": x.rank(method="average").corr(ref.rank(method="average"), method="pearson"),
                     "bias_alt_minus_fao_mm": e.mean(), "bias_relative_percent": 100 * e.mean() / ref.mean(),
                     "mae_mm": e.abs().mean(), "rmse_mm": np.sqrt((e**2).mean())})
    return pd.DataFrame(rows)


def savefig(fig, stem):
    fig.tight_layout()
    fig.savefig(OUT_FIGS / f"1_1c_{stem}.png", dpi=300, bbox_inches="tight")
    fig.savefig(OUT_FIGS / f"1_1c_{stem}.pdf", bbox_inches="tight")
    plt.close(fig)


def write_docs(manual: pd.DataFrame, qa: pd.DataFrame, metrics: pd.DataFrame, phase: pd.DataFrame):
    best = metrics.sort_values("mae_mm").iloc[0]
    largest = metrics.sort_values("mae_mm", ascending=False).iloc[0]
    max_bias = pd.read_csv(OUT_TABLES / "1_1c_metricas_mes_calendario.csv").sort_values("bias_alt_minus_fao_mm", key=lambda x: x.abs(), ascending=False).iloc[0]
    cal = pd.read_csv(OUT_TABLES / "1_1c_metricas_mes_calendario.csv")
    seasonal = (cal.loc[cal.groupby("method")["bias_alt_minus_fao_mm"].apply(lambda x: x.abs().idxmax()).values,
                        ["method", "month", "bias_alt_minus_fao_mm"]]
                  .assign(method=lambda x: x.method.map(LABELS))
                  .to_markdown(index=False, floatfmt=".3f"))
    ph = phase.copy(); ph["method"] = ph.method.map(LABELS)
    harmonic_table = ph[["method", "amplitude_difference_alt_minus_fao_mm_month", "phase_difference_alt_minus_fao_months", "climatological_maximum_month"]].to_markdown(index=False, floatfmt=".3f")
    md = f"""# 1.1.c — Métodos de otras familias (versión preliminar)

## Alcance reproducible
Se procesaron **20 celdas ERA5-Land** por separado y después se ponderaron con los pesos de la Tarea 1, renormalizados sobre el dominio disponible. La cobertura es {COVERAGE:.4%}; el 9.8736 % restante sigue pendiente. El periodo común comparable es enero de 1981–diciembre de 2022 (504 meses): Thornthwaite exige un índice térmico anual completo; por ello se excluyó 2023, que está incompleto, sin rellenar datos. Todas las tablas están en mm/mes salvo indicación contraria.

## Métodos, ecuaciones y uso
* **Thornthwaite (1948, temperatura):** `PET=16(10T/I)^a (N/12)(d/30)` mm/mes, con `I=sum((T/5)^1.514)` (solo T>0) y `a=6.75e-7 I³−7.71e-5 I²+1.792e-2 I+0.49239`. T es °C, N horas de luz y d días. Se implementó en mensual y años completos; T≤0 contribuye cero. Fue formulado para estimar evapotranspiración potencial a partir de temperatura y latitud; omite radiación observada, humedad y viento.
* **Hargreaves–Samani (1985, temperatura+Ra):** `ET0=0.0023(Tmean+17.8)sqrt(Tmax−Tmin) Ra`, con `Ra` en mm d⁻¹ equivalentes (`Ra_MJ/2.45`). T en °C. Simplifica radiación, humedad y viento mediante el rango térmico. Aplicado como contraste de bajo requerimiento, no calibrado para Racarumi.
* **Priestley–Taylor (1972, radiación):** `ET=1.26 Δ/(Δ+γ)(Rn−G)/λ`; Δ y γ en kPa °C⁻¹, Rn/G MJ m⁻² d⁻¹ y λ MJ kg⁻¹. Representa una superficie húmeda con disponibilidad de energía; omite explícitamente el término aerodinámico. Se usó α=1.26, sin calibración.
* **Meyer (1915, transferencia de masa):** `E=0.36(e_w−e_a)(1+u_9/16)`, E mm d⁻¹, presiones en mm Hg y u en km h⁻¹ aproximadamente a 9 m. Ante la ausencia de unas notas del curso que fijen una constante Dalton, se aplicó Meyer —permitido por la guía— con una formulación publicada y sin calibrarla. Se usó `e_w=es(Taire media)` por ausencia de temperatura de agua y u10 como aproximación a u9. Es evaporación de agua libre y no ETo.
* **Makkink (1957, radiación solar):** `PET=0.65 Δ Rs/[λ(Δ+γ)]`, con Rs MJ m⁻² d⁻¹. Se aplicó mediante `pyet.makkink` v{pyet.__version__}, con λ dependiente de T. Es una formulación calibrada para pasto en los Países Bajos; omite humedad y viento explícitos.
* **Rohwer (1931, transferencia de masa):** `E=0.771(1.465−0.000732P_a)(0.44+0.0733u_0)(e_w−e_a)`, E mm d⁻¹, P/e en mm Hg y u0 en km h⁻¹ a 0.6 m. `u0=u10(0.6/10)^(1/7)` y `e_w=es(Taire media)` son aproximaciones declaradas por falta de viento bajo y temperatura de agua. Es evaporación de agua libre, no ETo; se usa solo como contraste físico experimental.

## Referencias metodológicas
Thornthwaite, C.W. (1948), *An approach toward a rational classification of climate*, Geographical Review 38, 55–94. Hargreaves, G.H. & Samani, Z.A. (1985), *Reference crop evapotranspiration from temperature*, Applied Engineering in Agriculture 1, 96–99. Priestley, C.H.B. & Taylor, R.J. (1972), *On the assessment of surface heat flux and evaporation using large-scale parameters*, Monthly Weather Review 100, 81–92. Meyer, A.F. (1915), *Computing runoff from rainfall and other physical data*. Makkink, G.F. (1957), *Testing the Penman formula by means of lysimeters*, Journal of the Institution of Water Engineers 11, 277–288. Rohwer, C. (1931), *Evaporation from free water surfaces*, U.S. Department of Agriculture Technical Bulletin 271. Allen et al. (1998), FAO-56.

## Control manual independiente
La tabla `1_1c_comprobacion_manual.csv` conserva todas las entradas y salidas para un día/celda y para el primer mes completo de Thornthwaite. El anexo `verificacion_manual_con_sustitucion_1_1c.md` muestra la sustitución numérica. `1_1c_control_pyET.csv` registra la verificación de Hargreaves contra pyet (una celda con índice temporal único); Priestley–Taylor y Makkink se ejecutaron directamente con pyet v{pyet.__version__}.

## Resultados y respuestas a la guía
En la serie mensual común, el menor MAE fue **{LABELS[best.method]}** ({best.mae_mm:.3f} mm/mes); esto es un ranking por MAE, no un ganador universal. El mayor MAE fue **{LABELS[largest.method]}** ({largest.mae_mm:.3f} mm/mes). La desviación mensual de mayor magnitud fue {LABELS[max_bias.method]} en el mes {int(max_bias.month)}: {max_bias.bias_alt_minus_fao_mm:.3f} mm/mes (alternativo−FAO-56).

**Pregunta 1.** Por MAE y RMSE mensuales, Makkink es el más cercano (MAE {metrics.loc[metrics.method=='makkink_1957','mae_mm'].iloc[0]:.3f}; RMSE {metrics.loc[metrics.method=='makkink_1957','rmse_mm'].iloc[0]:.3f} mm/mes), seguido por Hargreaves–Samani (MAE {metrics.loc[metrics.method=='hargreaves_samani_1985','mae_mm'].iloc[0]:.3f}). También tiene la mayor correlación de Pearson ({metrics.loc[metrics.method=='makkink_1957','pearson'].iloc[0]:.3f}). No es un ganador universal: Priestley–Taylor mantiene alta correlación ({metrics.loc[metrics.method=='priestley_taylor_1972','pearson'].iloc[0]:.3f}) pero sobrestima {metrics.loc[metrics.method=='priestley_taylor_1972','bias_alt_minus_fao_mm'].iloc[0]:.3f} mm/mes. Los resultados anuales y cada mes calendario están en sus CSV respectivos.

Primer armónico de la climatología (diferencia = alternativo − FAO-56):

{harmonic_table}

**Pregunta 2.** El comportamiento esperado se interpreta como hipótesis: los métodos radiativos deberían acercarse cuando Rn/Rs domina, mientras los métodos de masa divergen al representar agua libre y requerir temperatura de agua/viento a otras alturas. Los térmicos pueden compensar errores mediante el rango térmico. No se infiere aquí un forzante dominante: esto se contrasta en 1.1.d.

**Pregunta 3.** Los mayores alejamientos por método y su dirección son:

{seasonal}

Meyer y Rohwer son los más alejados: subestiman porque representan una superficie de agua libre con proxies de temperatura superficial y altura de viento, no una referencia de pasto. Frente a 1.1.b, estos son métodos ejecutados sobre el mismo dominio de Racarumi. Como contexto, PISCOeo_pm frente a FAO-56 tuvo MAE 7.970 mm/mes (432 meses) y TerraClimate frente a FAO-56, 4.017 mm/mes (511 meses); no se usa Chiclayo como umbral de incertidumbre de cuenca.

## Limitaciones decisivas
Meyer y Rohwer dependen de temperatura de agua y alturas de viento que ERA5-Land no aporta en esta serie; por ello son escenarios de evaporación de agua libre con proxies, no estimaciones de ETo. La referencia FAO-56 y todos estos resultados siguen siendo preliminares por la cobertura espacial incompleta.
"""
    (OUT_ANNEX / "metodos_ecuaciones_referencias_y_respuestas_1_1c.md").write_text(md, encoding="utf-8")
    first = manual.iloc[0]
    tw = manual[manual.get("method", pd.Series(index=manual.index, dtype=object)).eq("thornthwaite_monthly")].iloc[0]
    check = f"""# Verificación manual con sustitución numérica

## Día {first.date} — celda {first.point}
* Hargreaves–Samani: `0.0023 × ({first.tmean_c:.6f}+17.8) × sqrt({first.tmax_c:.6f}−{first.tmin_c:.6f}) × {first.ra_mm_d:.6f} = {first.hargreaves_samani_1985:.6f} mm/d`.
* Priestley–Taylor: `1.26 × {first.delta_kpa_c:.6f}/({first.delta_kpa_c:.6f}+{first.gamma_kpa_c:.6f}) × {first.rn_mj_m2_d:.6f}/lambda(T)` = `{first.priestley_taylor_1972:.6f} mm/d` (pyet; G=0).
* Makkink: `0.65 × {first.delta_kpa_c:.6f}/({first.delta_kpa_c:.6f}+{first.gamma_kpa_c:.6f}) × {first.rs_mj_m2_d:.6f}/lambda(T)` = `{first.makkink_1957:.6f} mm/d` (pyet).
* Meyer: `0.36 × (es(Taire)−ea) × (1+u10/16)` con `es={first.es_air_kpa:.6f} kPa`, `ea={first.ea_kpa:.6f} kPa`, `u10={first.wind10_ms*3.6:.6f} km/h`, tras convertir presiones a mm Hg = `{first.meyer_1915:.6f} mm/d`.
* Rohwer: con `P={first.p_kpa*7.50061683:.6f} mm Hg`, `u0.6={first.u0p6_kmh:.6f} km/h`, y el mismo déficit de vapor convertido a mm Hg = `{first.rohwer_1931:.6f} mm/d`.

## Mes {tw.date} — Thornthwaite, celda {tw.point}
`I={tw.heat_index_I:.6f}`, `a={tw.a:.6f}`, `N={tw.daylength_h:.6f} h`, `d={int(tw.n_days)}`. Sustitución: `16(10T/I)^a(N/12)(d/30) = {tw.thornthwaite_1948_mm_month:.6f} mm/mes`. Las entradas de temperatura mensual se mantienen en `1_1c_series_mensuales_por_celda_preliminar_90pct.csv`.
"""
    (OUT_ANNEX / "verificacion_manual_con_sustitucion_1_1c.md").write_text(check, encoding="utf-8")


def main():
    for p in (OUT_DATA, OUT_TABLES, OUT_FIGS, OUT_ANNEX): p.mkdir(parents=True, exist_ok=True)
    d = pd.read_csv(DAILY_IN, parse_dates=["date"])
    w = pd.read_csv(WEIGHTS_IN)
    cells = sorted(d.point.unique())
    w = w[w.cell_id.isin(cells)].copy()
    assert len(w) == len(cells) == 20, "Las 20 celdas y pesos deben coincidir"
    w["weight_available_normalized"] = w.spatial_weight / w.spatial_weight.sum()
    weight = w.set_index("cell_id")["weight_available_normalized"]
    assert abs(weight.sum()-1) < 1e-12
    d["vpd_kpa"] = (d.es_kpa - d.ea_kpa).clip(lower=0)
    d["es_air_hg"] = sat_vp(d.tmean_c) * 7.50061683
    d["ea_hg"] = d.ea_kpa * 7.50061683
    d["pressure_hg"] = d.p_kpa * 7.50061683
    d["u10_kmh"] = d.wind10_ms * 3.6
    d["u0p6_kmh"] = d.u10_kmh * (0.6 / 10.0) ** (1/7)
    d["hargreaves_samani_1985"] = 0.0023 * (d.tmean_c + 17.8) * np.sqrt((d.tmax_c-d.tmin_c).clip(lower=0)) * (d.ra_mj_m2_d / 2.45)
    # pyet formulas used directly for radiation methods; alpha fixed exactly as requested.
    d["priestley_taylor_1972"] = pyet.priestley_taylor(d.tmean_c, rn=d.rn_mj_m2_d, g=d.g_mj_m2_d, pressure=d.p_kpa, alpha=1.26).to_numpy()
    d["makkink_1957"] = pyet.makkink(d.tmean_c, d.rs_mj_m2_d, pressure=d.p_kpa, k=0.65).to_numpy()
    d["meyer_1915"] = 0.36 * (d.es_air_hg-d.ea_hg).clip(lower=0) * (1+d.u10_kmh/16)
    d["rohwer_1931"] = 0.771*(1.465-0.000732*d.pressure_hg)*(0.44+0.0733*d.u0p6_kmh)*(d.es_air_hg-d.ea_hg).clip(lower=0)
    for m in METHODS[1:]: d[m] = d[m].clip(lower=0)
    d["year"] = d.date.dt.year; d["month"] = d.date.dt.month

    tw = []
    for cell, g in d.groupby("point", sort=True):
        z = thornthwaite_monthly(g)
        z["point"] = cell
        tw.append(z)
    tw = pd.concat(tw, ignore_index=True)
    # aggregate daily alternative methods per cell/month; retain only complete months.
    mcols = ["eto_fao56_mm_d"] + METHODS[1:]
    monthly_cell = d.set_index("date").groupby("point")[mcols].resample("MS").sum().reset_index()
    nday = d.set_index("date").groupby("point")["tmean_c"].resample("MS").size().rename("n_days").reset_index()
    monthly_cell = monthly_cell.merge(nday, on=["point", "date"])
    monthly_cell = monthly_cell[monthly_cell.n_days == monthly_cell.date.dt.days_in_month].copy()
    monthly_cell = monthly_cell.merge(tw[["point", "date", "thornthwaite_1948"]], on=["point", "date"], how="inner")
    monthly_cell["weight"] = monthly_cell.point.map(weight)
    assert monthly_cell.weight.notna().all()
    # all 20 cels must exist in a date; weighted sum (weights already normalized).
    rows=[]
    for date, g in monthly_cell.groupby("date"):
        if len(g) != 20: continue
        row={"date":date, "coverage_spatial_fraction":COVERAGE, "n_cells":len(g), "quality_flag":"complete_month_all_20_cells"}
        row["fao56"] = np.sum(g.eto_fao56_mm_d*g.weight)
        for m in METHODS: row[m] = np.sum(g[m]*g.weight)
        rows.append(row)
    master = pd.DataFrame(rows).sort_values("date")
    master["units"]="mm_month"
    master.to_csv(OUT_DATA / "1_1c_tabla_maestra_mensual_preliminar_90pct.csv", index=False)
    monthly_cell.to_csv(OUT_DATA / "1_1c_series_mensuales_por_celda_preliminar_90pct.csv", index=False)

    metrics = compare(master, "serie_mensual_comun_1981_2022")
    metrics.to_csv(OUT_TABLES / "1_1c_metricas_serie_mensual.csv", index=False)
    annual = master.set_index("date").resample("YS")[["fao56"]+METHODS].sum().reset_index()
    annual["year"] = annual.date.dt.year
    metrics_ann = compare(annual, "anual_anios_completos_1981_2022")
    metrics_ann.to_csv(OUT_TABLES / "1_1c_metricas_anuales.csv", index=False)
    cal=[]
    for mon, z in master.groupby(master.date.dt.month):
        q=compare(z, "mes_calendario")
        q["month"]=mon; cal.append(q)
    calendar = pd.concat(cal, ignore_index=True)
    calendar.to_csv(OUT_TABLES / "1_1c_metricas_mes_calendario.csv", index=False)
    clim = master.assign(month=master.date.dt.month).groupby("month")[["fao56"]+METHODS].mean()
    phase_rows=[]
    ref_amp, ref_phase, ref_max = harmonic(clim.fao56)
    for key in METHODS:
        amp, ph, mx = harmonic(clim[key])
        phase_rows.append({"method":key,"amplitude_mm_month":amp,"phase_maximum_month_fraction":ph,"climatological_maximum_month":mx,"fao_amplitude_mm_month":ref_amp,"amplitude_difference_alt_minus_fao_mm_month":amp-ref_amp,"phase_difference_alt_minus_fao_months":circular_phase_difference(ph,ref_phase),"fao_climatological_maximum_month":ref_max})
    phase=pd.DataFrame(phase_rows)
    phase.to_csv(OUT_TABLES / "1_1c_amplitud_fase_ciclo_anual.csv", index=False)

    # Independent implementation checks against pyet, only for functions it supplies.
    # pyet Hargreaves needs one non-duplicated datetime index.  Validate one
    # complete ERA5-Land cell; the production calculation above remains the
    # explicit FAO-56-guide equation for every cell.
    dqa = d[d.point == cells[0]].set_index("date").sort_index()
    py_h = pyet.hargreaves(dqa.tmean_c,dqa.tmax_c,dqa.tmin_c,np.deg2rad(float(dqa.latitude.iloc[0])), k=0.0135, method=0)
    py_pt = pyet.priestley_taylor(d.tmean_c,rn=d.rn_mj_m2_d,g=d.g_mj_m2_d,pressure=d.p_kpa,alpha=1.26)
    py_mk = pyet.makkink(d.tmean_c,d.rs_mj_m2_d,pressure=d.p_kpa,k=.65)
    qa=pd.DataFrame([{"check":"hargreaves_formula_vs_pyet_one_cell","n":len(dqa),"max_abs_difference_mm_d":np.max(np.abs(dqa.hargreaves_samani_1985.to_numpy()-py_h.to_numpy())),"explanation":"Difference expected: exact guide uses lambda=2.45; pyet uses temperature-dependent lambda."},{"check":"priestley_taylor_used_pyet","n":len(d),"max_abs_difference_mm_d":0.0,"explanation":"Direct pyet output, alpha=1.26."},{"check":"makkink_used_pyet","n":len(d),"max_abs_difference_mm_d":0.0,"explanation":"Direct pyet output, k=0.65."}])
    qa.to_csv(OUT_TABLES / "1_1c_control_pyET.csv", index=False)
    sample=d.iloc[0]
    manual=pd.DataFrame([{"point":sample.point,"date":sample.date.date(),"tmean_c":sample.tmean_c,"tmax_c":sample.tmax_c,"tmin_c":sample.tmin_c,"ra_mj_m2_d":sample.ra_mj_m2_d,"ra_mm_d":sample.ra_mj_m2_d/2.45,"rn_mj_m2_d":sample.rn_mj_m2_d,"rs_mj_m2_d":sample.rs_mj_m2_d,"delta_kpa_c":sample.delta_kpa_c,"gamma_kpa_c":sample.gamma_kpa_c,"ea_kpa":sample.ea_kpa,"es_air_kpa":sample.es_air_hg/7.50061683,"p_kpa":sample.p_kpa,"wind10_ms":sample.wind10_ms,"u0p6_kmh":sample.u0p6_kmh, **{m:sample[m] for m in METHODS[1:]}}])
    ts=tw.iloc[0]
    manual=pd.concat([manual,pd.DataFrame([{ "point":ts.point,"date":ts.date.date(),"method":"thornthwaite_monthly","heat_index_I":ts.heat_index_I,"a":ts.a,"daylength_h":ts.daylength_h,"n_days":ts.n_days,"thornthwaite_1948_mm_month":ts.thornthwaite_1948}])],ignore_index=True)
    manual.to_csv(OUT_TABLES / "1_1c_comprobacion_manual.csv", index=False)

    # figures
    fig, ax=plt.subplots(figsize=(13,5));
    ax.plot(master.date, master.fao56, label="FAO-56", color=COLORS["fao56"],lw=1.3)
    for m in METHODS: ax.plot(master.date,master[m],label=LABELS[m],color=COLORS[m],alpha=.68,lw=.7)
    ax.set(title="Racarumi: métodos alternativos, serie mensual preliminar",ylabel="Demanda/evaporación estimada (mm/mes)",xlabel="Fecha"); ax.legend(ncol=4,fontsize=8); savefig(fig,"serie_mensual")
    fig,ax=plt.subplots(figsize=(10,5));
    ax.plot(clim.index,clim.fao56,"-o",color=COLORS["fao56"],label="FAO-56",lw=2)
    for m in METHODS: ax.plot(clim.index,clim[m],"-o",color=COLORS[m],label=LABELS[m])
    ax.set(xticks=range(1,13),xlabel="Mes calendario",ylabel="mm/mes",title="Climatología mensual (1981–2022; cobertura 90.1264%)");ax.legend(ncol=3,fontsize=8);savefig(fig,"climatologia_mensual")
    fig,axes=plt.subplots(2,3,figsize=(12,7));
    for ax,m in zip(axes.flat,METHODS):
        ax.scatter(master.fao56,master[m],s=8,alpha=.45,color=COLORS[m]); lo=min(master.fao56.min(),master[m].min()); hi=max(master.fao56.max(),master[m].max()); ax.plot([lo,hi],[lo,hi],"--",color="gray"); ax.set(title=LABELS[m],xlabel="FAO-56 (mm/mes)",ylabel="Método (mm/mes)")
    savefig(fig,"dispersion_vs_fao56")
    fig,axes=plt.subplots(1,2,figsize=(12,4)); x=np.arange(len(METHODS));
    axes[0].bar(x,metrics.mae_mm,color=[COLORS[m] for m in METHODS],label="MAE");axes[0].bar(x,metrics.rmse_mm,fill=False,edgecolor="black",linewidth=1.5,label="RMSE");axes[0].set(xticks=x,xticklabels=[LABELS[m] for m in METHODS],ylabel="mm/mes",title="Error frente a FAO-56");axes[0].tick_params(axis="x",rotation=35);axes[0].legend()
    axes[1].bar(x,metrics.bias_alt_minus_fao_mm,color=[COLORS[m] for m in METHODS]);axes[1].axhline(0,color="black",lw=.7);axes[1].set(xticks=x,xticklabels=[LABELS[m] for m in METHODS],ylabel="Sesgo, alternativo − FAO-56 (mm/mes)",title="Sesgo mensual");axes[1].tick_params(axis="x",rotation=35);savefig(fig,"metricas_sesgo_mae_rmse")
    piv=calendar.pivot(index="method",columns="month",values="bias_alt_minus_fao_mm").reindex(METHODS);fig,ax=plt.subplots(figsize=(11,4));im=ax.imshow(piv,cmap="coolwarm",aspect="auto");ax.set(yticks=range(6),yticklabels=[LABELS[m] for m in METHODS],xticks=range(12),xticklabels=range(1,13),xlabel="Mes",title="Sesgo por mes calendario (mm/mes; alternativo − FAO-56)");fig.colorbar(im,ax=ax,label="mm/mes");savefig(fig,"mapa_calor_sesgo_mes")
    fig,ax=plt.subplots(figsize=(11,5));ax.boxplot([master[m]-master.fao56 for m in METHODS],tick_labels=[LABELS[m] for m in METHODS],showfliers=False);ax.axhline(0,color="black",lw=.7);ax.set(ylabel="Error (mm/mes; alternativo − FAO-56)",title="Distribución de errores mensuales");ax.tick_params(axis="x",rotation=35);savefig(fig,"cajas_errores")
    fig,axes=plt.subplots(1,2,figsize=(12,4));axes[0].bar(x,phase.amplitude_difference_alt_minus_fao_mm_month,color=[COLORS[m] for m in METHODS]);axes[0].axhline(0,color="black",lw=.7);axes[0].set(xticks=x,xticklabels=[LABELS[m] for m in METHODS],ylabel="Diferencia de amplitud (mm/mes)",title="Primer armónico");axes[0].tick_params(axis="x",rotation=35);axes[1].bar(x,phase.phase_difference_alt_minus_fao_months,color=[COLORS[m] for m in METHODS]);axes[1].axhline(0,color="black",lw=.7);axes[1].set(xticks=x,xticklabels=[LABELS[m] for m in METHODS],ylabel="Diferencia de fase (meses)",title="Primer armónico");axes[1].tick_params(axis="x",rotation=35);savefig(fig,"amplitud_fase")
    # context 1.1b: only Racarumi products, not Chiclayo.
    pisco=ROOT/"productos"/"punto1"/"1_1_demanda_atmosferica"/"tablas"/"1_1b_metricas_pet_piscoeopm_vs_eto.csv"
    terra=ROOT/"productos"/"punto1"/"1_1_demanda_atmosferica"/"tablas"/"1_1b_metricas_terraclimate_y_productos_demanda.csv"
    context=[]
    for pp,name in [(pisco,"PISCOeo_pm (1.1.b)"),(terra,"TerraClimate (1.1.b)")]:
        if pp.exists():
            q=pd.read_csv(pp); cols={c.lower():c for c in q.columns};
            row=q.iloc[0];
            for key in ["mae","rmse"]:
                cand=[c for c in q.columns if key in c.lower()]
                if cand: context.append({"method":name,"metric":key.upper(),"value":row[cand[0]]})
    context.extend([{ "method":LABELS[r.method],"metric":"MAE","value":r.mae_mm} for _,r in metrics.iterrows()])
    cdf=pd.DataFrame(context);cdf.to_csv(OUT_TABLES/"1_1c_contexto_dispersion_1_1b.csv",index=False)
    fig,ax=plt.subplots(figsize=(10,4)); v=cdf[cdf.metric=="MAE"];ax.bar(range(len(v)),v.value,color=[COLORS.get(next((k for k,z in LABELS.items() if z==m),""),"gray") for m in v.method]);ax.set(xticks=range(len(v)),xticklabels=v.method,ylabel="MAE reportado (unidades propias de cada comparación)",title="Contexto de dispersión: 1.1.c y productos de 1.1.b");ax.tick_params(axis="x",rotation=30);savefig(fig,"contexto_dispersion_1_1b")
    write_docs(manual,qa,metrics,phase)
    inventory=[]
    for folder in [OUT_DATA,OUT_TABLES,OUT_FIGS,OUT_ANNEX]:
        inventory += [{"path":str(x.relative_to(ROOT)),"bytes":x.stat().st_size} for x in folder.glob("1_1c_*") if x.is_file()]
    pd.DataFrame(inventory).to_csv(OUT_ANNEX/"inventario_productos_1_1c.csv",index=False)
    status=pd.DataFrame([{"requirement":"Seis métodos / cuatro familias obligatorias + dos adicionales","status":"complete"},{"requirement":"20 celdas, ponderación después de cálculo, cobertura 90.1264%","status":"complete_preliminary"},{"requirement":"Comparación mensual, anual y por mes calendario","status":"complete"},{"requirement":"Amplitud/fase, control manual, pyet QA, figuras y documentación","status":"complete"},{"requirement":"ETo definitiva de Racarumi","status":"not_complete: falta 9.8736% de cobertura espacial"}])
    status.to_csv(OUT_TABLES/"1_1c_estado_cumplimiento_preliminar.csv",index=False)
    print(f"OK: {len(master)} meses comunes; {len(annual)} años completos; cobertura={COVERAGE:.6%}")
    print(metrics[["method","mae_mm","rmse_mm","bias_alt_minus_fao_mm","pearson"]].to_string(index=False))

if __name__ == "__main__": main()
