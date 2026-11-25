"""1.1.a: valida Open-Meteo contra CDS y completa la ETo FAO-56 con las 33 celdas.

1. Control: aplica el mismo calculo FAO-56 del grupo (fao56_daily de run_fao56_1_1a.py)
   a cuatro celdas descargadas de Open-Meteo (2001-2003) y las compara con las mismas
   celdas procesadas desde los ZIP de CDS. Temperatura, humedad y radiacion coinciden;
   el viento de Open-Meteo (ERA5, 0,25 grados) es mayor que el de ERA5-Land del CDS, por
   lo que se estima un factor de correccion del viento por mes calendario y se valida
   dejando fuera una celda cada vez.
2. Chiclayo: repite el calculo para la celda de la estacion PEI0000SPHI y lo compara con
   la serie procesada desde el ZIP original de CDS (que no esta en el repositorio).
3. Cuenca completa: calcula la ETo diaria de las 13 celdas faltantes y pondera las 33
   celdas con los pesos de interseccion de la Tarea 1. Compara con la version de 20
   celdas (90,13 % del peso) usando el mismo metodo de ponderacion (ETo por celda).

Salidas en productos/punto1/1_1_demanda_atmosferica/tablas/ y
datos/punto1/procesados/1_1_a_fao56_completo/.
Ejecucion: python completar_eto_33_celdas.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

from run_fao56_1_1a import fao56_daily

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
OM = ROOT / "datos" / "punto1" / "originales" / "openmeteo_era5land"
TAB = ROOT / "productos" / "punto1" / "1_1_demanda_atmosferica" / "tablas"
PROC = ROOT / "datos" / "punto1" / "procesados" / "1_1_a_fao56_completo"
PROC.mkdir(parents=True, exist_ok=True)
GRID = TAB / "era5land_33_celdas_pesos_y_elevacion.csv"
CDS_CELDAS = ROOT / "productos" / "punto1" / "1_1_a" / "fao56_eto_diaria_por_celda_preliminar_90pct.csv"
CDS_CHICLAYO = ROOT / "datos" / "punto1" / "procesados" / "1_1_b_pruebas_referencia" / "era5land_chiclayo_fao56_diaria.csv"
VARS = ["tmin_c", "tmax_c", "ea_kpa", "u2_ms", "rs_mj_m2_d", "eto_fao56_mm_d"]
grid = pd.read_csv(GRID).set_index("cell_id")


def diaria_openmeteo(celda, elevacion, latitud, factor_viento=None):
    """factor_viento: serie indexada por mes calendario (1-12) que multiplica el viento horario."""
    h = pd.read_csv(OM / f"{celda}.csv", parse_dates=["time"]).set_index("time")
    viento = h["wind10_ms"]
    if factor_viento is not None:
        mes_local = (h.index - pd.Timedelta(hours=5)).month  # mismo dia local UTC-5 que fao56_daily
        viento = viento * factor_viento.reindex(mes_local).to_numpy()
    hourly = {"t2m": h["t2m_c"] + 273.15, "d2m": h["d2m_c"] + 273.15, "sp": h["sp_hpa"] * 100.0,
              "ssrd": h["ssrd_w_m2"] * 3600.0, "wind10_ms": viento}
    d = fao56_daily(celda, hourly, elevacion, latitud)
    d["date"] = pd.to_datetime(d["date"])
    return d


def comparar(om, cds, etiqueta):
    m = om.merge(cds, on="date", suffixes=("_om", "_cds"))
    filas = []
    for v in VARS:
        a, b = m[f"{v}_om"], m[f"{v}_cds"]
        filas.append({"caso": etiqueta, "variable": v, "n_dias": len(m), "media_cds": b.mean(), "media_openmeteo": a.mean(),
                      "sesgo": (a - b).mean(), "sesgo_pct": 100 * (a - b).mean() / b.mean(), "MAE": (a - b).abs().mean(),
                      "r": np.corrcoef(a, b)[0, 1]})
    mm = m.set_index("date")[["eto_fao56_mm_d_om", "eto_fao56_mm_d_cds"]].resample("MS").sum()
    filas.append({"caso": etiqueta, "variable": "eto_mensual_mm", "n_dias": len(mm), "media_cds": mm.iloc[:, 1].mean(),
                  "media_openmeteo": mm.iloc[:, 0].mean(), "sesgo": (mm.iloc[:, 0] - mm.iloc[:, 1]).mean(),
                  "sesgo_pct": 100 * (mm.iloc[:, 0] - mm.iloc[:, 1]).mean() / mm.iloc[:, 1].mean(),
                  "MAE": (mm.iloc[:, 0] - mm.iloc[:, 1]).abs().mean(), "r": np.corrcoef(mm.iloc[:, 0], mm.iloc[:, 1])[0, 1]})
    return pd.DataFrame(filas)


val = []
cds = pd.read_csv(CDS_CELDAS, parse_dates=["date"])
CONTROLES = ["ERA5L_12", "ERA5L_10", "ERA5L_05", "ERA5L_23"]
ctl = {}
for c in CONTROLES:
    om = diaria_openmeteo(c, grid.loc[c, "dem_mean_elevation_m"], grid.loc[c, "latitude"])
    ref = cds[cds.point == c]
    val.append(comparar(om, ref, f"control {c} sin correccion"))
    m = om.merge(ref, on="date", suffixes=("_om", "_cds"))
    ctl[c] = m.assign(mes=m.date.dt.month)


def factor(celdas):
    """Cociente de medias del viento a 2 m (CDS / Open-Meteo) por mes calendario."""
    d = pd.concat([ctl[c] for c in celdas])
    g = d.groupby("mes")
    return g["u2_ms_cds"].mean() / g["u2_ms_om"].mean()


FACTOR = factor(CONTROLES)
pd.DataFrame({"mes": FACTOR.index, "factor_viento": FACTOR.values}).to_csv(
    TAB / "1_1a_factor_viento_openmeteo.csv", index=False, float_format="%.4f")
# Validacion cruzada: el factor de tres celdas se aplica a la cuarta
for c in CONTROLES:
    f = factor([x for x in CONTROLES if x != c])
    om = diaria_openmeteo(c, grid.loc[c, "dem_mean_elevation_m"], grid.loc[c, "latitude"], f)
    val.append(comparar(om, cds[cds.point == c], f"control {c} corregido (validacion cruzada)"))
if (OM / "Chiclayo_SPHI.csv").exists():
    ch = pd.read_csv(CDS_CHICLAYO, parse_dates=["date"])
    elev = float(ch["elevation_dem_m"].iloc[0]) if "elevation_dem_m" in ch else 30.0
    om = diaria_openmeteo("Chiclayo_SPHI", elev, -6.8)
    val.append(comparar(om, ch.rename(columns={"eto_era5_ssrd_mm_d": "eto_fao56_mm_d"}), "Chiclayo 2010-2022 sin correccion"))
    om.to_csv(PROC / "chiclayo_fao56_diaria_openmeteo.csv", index=False, float_format="%.5f")  # costa: sin correccion
    om = diaria_openmeteo("Chiclayo_SPHI", elev, -6.8, FACTOR)
    val.append(comparar(om, ch.rename(columns={"eto_era5_ssrd_mm_d": "eto_fao56_mm_d"}), "Chiclayo 2010-2022 corregido"))
if val:
    v = pd.concat(val)
    v.to_csv(TAB / "1_1a_validacion_openmeteo_vs_cds.csv", index=False, float_format="%.4f")
    print(v.round(3).to_string(index=False))

# Cuenca completa
faltan = [c for c in grid.index if c not in set(cds.point.unique())]
disponibles = [c for c in faltan if (OM / f"{c}.csv").exists()]
print(f"celdas nuevas disponibles: {len(disponibles)} de {len(faltan)}")
if len(disponibles) == len(faltan):
    nuevas = pd.concat([diaria_openmeteo(c, grid.loc[c, "dem_mean_elevation_m"], grid.loc[c, "latitude"], FACTOR) for c in faltan])
    crudas = pd.concat([diaria_openmeteo(c, grid.loc[c, "dem_mean_elevation_m"], grid.loc[c, "latitude"]) for c in faltan])
    nuevas.to_csv(PROC / "fao56_eto_diaria_13_celdas_openmeteo.csv", index=False, float_format="%.5f")
    todas = pd.concat([cds[["date", "point", "eto_fao56_mm_d"]], nuevas[["date", "point", "eto_fao56_mm_d"]]])
    sin_corr = pd.concat([cds[["date", "point", "eto_fao56_mm_d"]], crudas[["date", "point", "eto_fao56_mm_d"]]])
    sin_corr = sin_corr[(sin_corr.date >= "1981-01-01") & (sin_corr.date <= "2022-12-31")]
    todas = todas[(todas.date >= "1981-01-01") & (todas.date <= "2022-12-31")]
    w = grid["spatial_weight"]
    pivot = todas.pivot(index="date", columns="point", values="eto_fao56_mm_d")
    def cuenca(celdas):
        ww = w[celdas] / w[celdas].sum()
        return (pivot[celdas] * ww).sum(axis=1, min_count=len(celdas))
    s90 = cuenca(list(cds.point.unique()))
    s100 = cuenca(list(grid.index))
    s_falt = cuenca(faltan)
    pivot_sc = sin_corr.pivot(index="date", columns="point", values="eto_fao56_mm_d")
    s100_sc = (pivot_sc[list(grid.index)] * (w / w.sum())).sum(axis=1, min_count=len(grid))
    diaria = pd.DataFrame({"eto_20_celdas_mm_d": s90, "eto_33_celdas_mm_d": s100, "eto_13_celdas_mm_d": s_falt,
                           "eto_33_celdas_sin_corr_viento_mm_d": s100_sc})
    diaria.to_csv(PROC / "fao56_eto_diaria_cuenca_33_celdas.csv", float_format="%.5f")
    mens = diaria.resample("MS").sum()
    clim = mens.groupby(mens.index.month).mean()
    clim["dif_pct"] = 100 * (clim["eto_33_celdas_mm_d"] / clim["eto_20_celdas_mm_d"] - 1)
    clim.to_csv(TAB / "1_1a_eto_33_vs_20_celdas_climatologia.csv", float_format="%.4f")
    anual = mens.resample("YS").sum()
    res = pd.DataFrame([{"eto_anual_20_celdas_mm": anual["eto_20_celdas_mm_d"].mean(),
                         "eto_anual_33_celdas_mm": anual["eto_33_celdas_mm_d"].mean(),
                         "eto_anual_13_celdas_mm": anual["eto_13_celdas_mm_d"].mean(),
                         "eto_anual_33_sin_corr_viento_mm": anual["eto_33_celdas_sin_corr_viento_mm_d"].mean(),
                         "dif_anual_pct": 100 * (anual["eto_33_celdas_mm_d"].mean() / anual["eto_20_celdas_mm_d"].mean() - 1),
                         "dif_mensual_max_abs_pct": clim["dif_pct"].abs().max(),
                         "r_mensual": np.corrcoef(mens.iloc[:, 0], mens.iloc[:, 1])[0, 1],
                         "tendencia_sen_20": None, "peso_nuevas": w[faltan].sum()}])
    from scipy import stats
    for col, key in (("eto_20_celdas_mm_d", "tendencia_sen_20"), ("eto_33_celdas_mm_d", "tendencia_sen_33")):
        res[key] = stats.theilslopes(anual[col].values, np.arange(len(anual)))[0]
    res.to_csv(TAB / "1_1a_eto_33_vs_20_celdas_resumen.csv", index=False, float_format="%.4f")
    print(res.round(3).T.to_string())
    print(clim.round(2).to_string())
