"""Extrae de las tablas del punto 1 las cifras citadas en el informe.

No recalcula nada: lee los productos ya generados por los scripts de 1.1 a 1.5 y
escribe productos/punto1/cifras_punto1.tex (macros LaTeX) para que cada numero
del informe sea trazable a un archivo.

Ejecucion: python codigo/punto1/cifras_punto1.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
P = ROOT / "productos" / "punto1"
T11 = P / "1_1_demanda_atmosferica" / "tablas"
T13 = P / "1_3_regimen_evaporativo" / "tablas"
T14 = P / "1_4_cambios_demanda_evaporativa" / "tablas"
D11 = ROOT / "datos" / "punto1" / "procesados" / "1_1_d_explicacion_fisica"


def fmt(v, nd):
    if abs(v) < 0.5 * 10 ** -nd:
        v = 0.0
    return f"{v:.{nd}f}".replace(".", "{,}").replace("-", "$-$")


m = {}
# 1.1.a
clim = pd.read_csv(T11 / "fao56_preliminar_90pct_climatologia_mensual.csv")
m["EToAnual"] = fmt(clim["eto_sum_daily_mean_mm"].sum(), 0)
m["EToMesMin"] = fmt(clim["eto_sum_daily_mean_mm"].min(), 0)
m["EToMesMax"] = fmt(clim["eto_sum_daily_mean_mm"].max(), 0)
m["DifPromMax"] = fmt(clim["difference_mean_mm"].abs().max(), 2)
dvm = pd.read_csv(T11 / "fao56_resumen_diferencia_diaria_vs_mensual.csv")
m["DifPuntoMax"] = fmt(dvm["max_abs_difference_mm"].max(), 2)
cel = pd.read_csv(T11 / "era5land_33_celdas_pesos_y_elevacion.csv")
dz = cel["era5land_geopotential_height_m"] - cel["dem_mean_elevation_m"]
m["DzMin"], m["DzMax"] = fmt(dz.min(), 0), fmt(dz.max(), 0)
m["DzPond"] = fmt((dz * cel["spatial_weight"]).sum() / cel["spatial_weight"].sum(), 0)
m["CobEra"] = fmt(90.1264, 1)

# 1.1.b
fis = pd.read_csv(T11 / "1_1b_comprobacion_fisica_resumen.csv").iloc[0]
m["PmQfis"], m["EToFis"] = fmt(fis["mean_annual_p_minus_q_mm"], 0), fmt(fis["mean_annual_eto_preliminar_mm"], 0)
cons = pd.read_csv(T11 / "1_1b_metricas_consolidadas_finales_preliminares.csv")
tc = cons[cons["comparison"] == "TerraClimate PET - ETo FAO-56 ERA5-Land preliminar"].iloc[0]
pi = cons[cons["comparison"].str.startswith("PISCOeo_pm")].iloc[0]
no = cons[(cons["comparison"] == "NOAA kRs=0.19 - ERA5 ssrd") & (cons["resolution"] == "monthly")].iloc[0]
m["TCr"], m["TCsesgo"], m["TCmae"] = fmt(tc["pearson_r"], 2), fmt(tc["bias_left_minus_right_mm_month"], 1), fmt(tc["mae_mm_month"], 1)
m["PIr"], m["PIsesgo"], m["PImae"] = fmt(pi["pearson_r"], 2), fmt(pi["bias_pet_minus_eto_mm_month"], 1), fmt(pi["mae_mm_month"], 1)
m["NOr"], m["NOsesgo"], m["NOmae"] = fmt(no["pearson_r"], 2), fmt(no["bias_station_minus_era5_mm"], 1), fmt(no["mae_mm"], 1)

# 1.1.c
mc = pd.read_csv(T11 / "1_1c_metricas_serie_mensual.csv").set_index("method")
for k, key in [("Thorn", "thornthwaite_1948"), ("Harg", "hargreaves_samani_1985"), ("PT", "priestley_taylor_1972"),
               ("Meyer", "meyer_1915"), ("Makk", "makkink_1957"), ("Rohw", "rohwer_1931")]:
    m[f"MAE{k}"] = fmt(mc.loc[key, "mae_mm"], 1)
    m[f"Sesgo{k}"] = fmt(mc.loc[key, "bias_relative_percent"], 0)
    m[f"R{k}"] = fmt(mc.loc[key, "pearson"], 2)

# 1.1.d
comp = pd.read_csv(D11 / "1_1d_componentes_y_alpha_mensuales_preliminar_90pct.csv", parse_dates=["date"])
cc = comp.groupby(comp["date"].dt.month)[["fraction_radiative_pct", "alpha_star", "vpd_kpa_mean", "u2_ms_mean"]].mean()
m["FracRadMin"], m["FracRadMax"] = fmt(cc["fraction_radiative_pct"].min(), 0), fmt(cc["fraction_radiative_pct"].max(), 0)
m["AlfaMin"], m["AlfaMax"] = fmt(cc["alpha_star"].min(), 2), fmt(cc["alpha_star"].max(), 2)
m["VPDMin"], m["VPDMax"] = fmt(cc["vpd_kpa_mean"].min(), 2), fmt(cc["vpd_kpa_mean"].max(), 2)
sen = pd.read_csv(T11 / "1_1d_sensibilidad_resumen_anual.csv")
fs = sen[sen["method"] == "fao56"].set_index("scenario")
for k, sc in [("Rs", "Rs_minus10pct"), ("TunoEa", "T_plus1_ea_const"), ("TunoHR", "T_plus1_RH_const"),
              ("TdosEa", "T_plus2_ea_const"), ("TdosHR", "T_plus2_RH_const"), ("Ea", "ea_plus10pct"), ("Udos", "u2_plus10pct")]:
    m[f"Sens{k}"] = fmt(fs.loc[sc, "change_annual_mm_y"], 0)
    m[f"SensPct{k}"] = fmt(fs.loc[sc, "change_annual_pct"], 1)
th = sen[(sen["method"] == "thornthwaite_1948") & (sen["scenario"] == "T_plus1_ea_const")].iloc[0]
m["SensThornTuno"] = fmt(th["change_annual_pct"], 1)

# 1.1.d: calibracion de Hargreaves y Makkink original (calibrar_hargreaves_1_1d.py)
ch = pd.read_csv(T11 / "1_1d_calibracion_hargreaves.csv").set_index("caso")
fila = lambda prefijo: ch.loc[[c for c in ch.index if c.startswith(prefijo)][0]]
m["HSkCal"] = fmt(fila("Hargreaves calibrado 1981-2001").coeficiente, 6)
m["HSkTot"] = fmt(fila("Hargreaves calibrado 1981-2022").coeficiente, 6)
m["HSmaeValOrig"] = fmt(fila("Hargreaves original, validacion").MAE_mm_mes, 1)
m["HSmaeValCal"] = fmt(fila("Hargreaves calibrado 1981-2001").MAE_mm_mes, 1)
m["HSsesgoValCal"] = fmt(fila("Hargreaves calibrado 1981-2001").sesgo_pct, 1)
m["HSmaeTot"] = fmt(fila("Hargreaves calibrado 1981-2022").MAE_mm_mes, 1)
m["MakkOrigSesgo"] = fmt(fila("Makkink original").sesgo_pct, 0)
m["MakkOrigMAE"] = fmt(fila("Makkink original").MAE_mm_mes, 1)
pmh = pd.read_csv(T11 / "1_1d_calibracion_hargreaves_por_mes.csv")
m["HSsesgoSecoMin"] = fmt(pmh.loc[pmh.mes.between(6, 9), "sesgo_original_mm"].min(), 1)
m["HSsesgoSecoMax"] = fmt(pmh.loc[pmh.mes.between(6, 9), "sesgo_original_mm"].max(), 1)
m["HSsesgoHumMin"] = fmt(pmh.loc[pmh.mes.between(1, 3), "sesgo_original_mm"].min(), 1)
m["HSsesgoHumMax"] = fmt(pmh.loc[pmh.mes.between(1, 3), "sesgo_original_mm"].max(), 1)
m["HScalHum"] = fmt(pmh.loc[pmh.mes.between(1, 3), "sesgo_calibrado_mm"].mean(), 1)
m["HScalSeco"] = fmt(pmh.loc[pmh.mes.between(6, 9), "sesgo_calibrado_mm"].mean(), 1)
cr = pd.read_csv(T11 / "1_1d_calibracion_hargreaves_correlaciones.csv").set_index("variable")
m["HSrhoAero"] = fmt(cr.loc["fraccion_aerodinamica_pct", "spearman_rho"], 2)

# 1.2
bal = pd.read_csv(P / "punto_1_2_4_comparacion_multianual.csv").set_index("series")
m["ETgleam"], m["ETmod"] = fmt(bal.loc["GLEAM4.3a", "mean_mm_year"], 0), fmt(bal.loc["MOD16A2GF v6.1", "mean_mm_year"], 0)
m["ETbalL"], m["ETbalI"] = fmt(bal.loc["ET=PISCOp-Q", "mean_mm_year"], 0), fmt(bal.loc["ET=IMERG-Q", "mean_mm_year"], 0)
m["SobreGleam"] = fmt(100 * (bal.loc["GLEAM4.3a", "mean_mm_year"] / bal.loc["ET=PISCOp-Q", "mean_mm_year"] - 1), 0)
m["SobreMod"] = fmt(100 * (bal.loc["MOD16A2GF v6.1", "mean_mm_year"] / bal.loc["ET=PISCOp-Q", "mean_mm_year"] - 1), 0)
pe = pd.read_csv(P / "1_2_evapotranspiracion_real" / "tablas" / "1_2_2_resumen_propagacion_error_principal.csv")
pm = pe[(pe["precipitation_source"] == "PL") & (pe["scenario_Q"] == "main_15pct_bound")].iloc[0]
m["PL"], m["Qmed"], m["DifPLPI"] = fmt(pm["P_mean_mm_year"], 0), fmt(pm["Q_mean_mm_year"], 0), fmt(-pm["precip_difference_bias_PI_minus_PL_mm_year"], 0)
m["SigmaP"], m["SigmaQ"], m["SigmaET"] = fmt(pm["sigmaP_interproduct_dispersion_mm_year"], 0), fmt(pm["sigmaQ_mm_year"], 0), fmt(pm["sigmaET_mm_year"], 0)
m["SigmaETpct"] = fmt(100 * pm["sigmaET_mm_year"] / pm["ET_balance_mean_mm_year"], 0)
fe = pd.read_csv(P / "punto_1_2_3_fraccion_evaporativa_resumen.csv").iloc[0]
m["RnLambda"], m["FEbal"] = fmt(fe["mean_rn_lambda_mm_year"], 0), fmt(fe["f_et_l_multiyear_dimensionless"], 2)

# 1.2: correccion por trasvases (correccion_trasvases_1_2.py)
tr = pd.read_csv(P / "punto_1_2_correccion_trasvases.csv").set_index("escenario")
for k, e in (("Cen", "central"), ("Inf", "inferior"), ("Sup", "superior")):
    m[f"TrHm{k}"] = fmt(tr.loc[e, "trasvase_hm3_anio"], 0)
    m[f"TrMm{k}"] = fmt(tr.loc[e, "trasvase_mm_anio"], 0)
    m[f"ETcorr{k}"] = fmt(tr.loc[e, "ET_balance_corregido_mm"], 0)
m["TrGleam"], m["TrMod"] = fmt(tr.loc["central", "GLEAM_sobre_balance_pct"], 0), fmt(tr.loc["central", "MOD16_sobre_balance_pct"], 0)
m["TrFE"], m["TrCoefNat"] = fmt(tr.loc["central", "fraccion_evaporativa"], 2), fmt(tr.loc["central", "coef_escorrentia_natural"], 2)
m["TrQnat"] = fmt(tr.loc["central", "Q_natural_mm"], 0)
m["TrPctP"] = fmt(100 * tr.loc["central", "trasvase_mm_anio"] / pm["P_mean_mm_year"], 1)
tb = pd.read_csv(P / "punto_1_2_correccion_trasvases_budyko.csv")
sel = lambda prod, of, col: tb[(tb.producto == prod) & (tb.oferta == of)][col].iloc[0]
m["TrPhi"], m["TrEIg"], m["TrEIm"] = fmt(sel("GLEAM", "P + T", "phi"), 2), fmt(sel("GLEAM", "P + T", "EI"), 2), fmt(sel("MOD16", "P + T", "EI"), 2)
m["TrOmG"], m["TrOmM"] = fmt(sel("GLEAM", "P + T", "omega_Fu"), 2), fmt(sel("MOD16", "P + T", "omega_Fu"), 2)
m["TrBudy"] = fmt(sel("GLEAM", "P + T", "Budyko1974"), 2)

# 1.3
c13 = pd.read_csv(T13 / "1_3_integracion_1_3_1_climatologia_ET_ETo_ET_P.csv")
r = c13[["ET_GLEAM_over_ETo", "ET_MOD16_over_ETo"]].mean(axis=1)
m["EToHumMin"], m["EToHumMax"] = fmt(r[:5].min(), 2), fmt(r[:5].max(), 2)
m["EToSecMin"], m["EToSecMax"] = fmt(r[5:9].min(), 2), fmt(r[5:9].max(), 2)
fh = pd.read_csv(T13 / "1_3_integracion_1_3_2_FE_humedad_resumen.csv").set_index("ET_product")
m["CorrFEg"], m["CorrFEm"] = fmt(fh.loc["GLEAM", "pearson_FE_theta"], 2), fmt(fh.loc["MOD16", "pearson_FE_theta"], 2)
m["KnotG"], m["KnotM"] = fmt(fh.loc["GLEAM", "piecewise_knot_theta_m3_m3_exploratory"], 2), fmt(fh.loc["MOD16", "piecewise_knot_theta_m3_m3_exploratory"], 2)
bu = pd.read_csv(T13 / "1_3_integracion_1_3_3_Budyko_ET_real_productos.csv")
bg = bu[(bu.ET_product == "GLEAM") & (bu.precipitation == "PISCOp")].iloc[0]
bm = bu[(bu.ET_product == "MOD16") & (bu.precipitation == "PISCOp")].iloc[0]
m["PhiAr"], m["EIg"], m["EIm"] = fmt(bg["phi_ETo_over_P"], 2), fmt(bg["EI_ET_over_P"], 2), fmt(bm["EI_ET_over_P"], 2)
m["OmG"], m["OmM"], m["BudyEI"] = fmt(bg["omega_Fu"], 2), fmt(bm["omega_Fu"], 2), fmt(bg["Budyko1974_at_mean_phi"], 2)
m["DistG"], m["DistM"] = fmt(bg["vertical_distance_at_multiyear_mean"], 2), fmt(bm["vertical_distance_at_multiyear_mean"], 2)
m["ElasG"], m["ElasM"] = fmt(bg["elasticity_Fu_theoretical"], 2), fmt(bm["elasticity_Fu_theoretical"], 2)
el = pd.read_csv(T13 / "1_3_integracion_1_3_4_elasticidad_Fu_ET_real_vs_empirica.csv")
m["PhiI"] = fmt(bu[(bu.ET_product == "GLEAM") & (bu.precipitation == "IMERG")].iloc[0]["phi_ETo_over_P"], 2)
cr = pd.read_csv(T13 / "1_3_integracion_1_3_5_relacion_ET_demanda_seco_humedo.csv")
cg = cr[(cr.ET_product == "GLEAM") & (cr.precipitation == "PISCOp")].set_index("rain_class")
m["EToSeco"], m["EToHumedo"] = fmt(cg.loc["dry", "ETo_mean_mm_year"], 0), fmt(cg.loc["wet", "ETo_mean_mm_year"], 0)
m["ETSecoG"], m["ETHumG"] = fmt(cg.loc["dry", "ET_mean_mm_year"], 0), fmt(cg.loc["wet", "ET_mean_mm_year"], 0)
m["CorrPETo"] = fmt(cg.loc["correlation_all_years", "ETo_mean_mm_year"], 2)

# 1.4
ta = pd.read_csv(T14 / "1_4_1_tendencias_anuales.csv").set_index("variable")
m["TendETo"], m["pETo"] = fmt(ta.loc["eto", "sen_per_year"], 2), fmt(ta.loc["eto", "mk_p"], 4)
m["TendTh"], m["pTh"] = fmt(ta.loc["thornthwaite", "sen_per_year"], 2), fmt(ta.loc["thornthwaite", "mk_p"], 4)
m["TendT"] = fmt(10 * ta.loc["T", "sen_per_year"], 2)
at = pd.read_csv(T14 / "1_4_2_atribucion_fao56.csv").set_index("forzante")
for k in ["T", "ea", "u2", "Rs"]:
    m[f"Atr{k.capitalize().replace('2', 'dos')}"] = fmt(at.loc[k, "contribucion_mm_ano_por_ano"], 2)
m["AtrSuma"], m["AtrRes"] = fmt(at.loc["suma", "contribucion_mm_ano_por_ano"], 2), fmt(at.loc["residuo_directo_menos_suma", "contribucion_mm_ano_por_ano"], 2)

# 1.5
g = pd.read_csv(P / "1_5_paisaje" / "1_5_resumen_multianual_gradiente_altitudinal.csv")
m["EToBajo"], m["EToAlto"] = fmt(g["eto_fao56_mean_mm_year"].iloc[0], 0), fmt(g["eto_fao56_mean_mm_year"].iloc[-1], 0)
m["GlBajo"], m["GlAlto"] = fmt(g["gleam_mean_mm_year"].iloc[0], 0), fmt(g["gleam_mean_mm_year"].iloc[-1], 0)
m["ModBajo"], m["ModAlto"] = fmt(g["mod16_mean_mm_year"].iloc[0], 0), fmt(g["mod16_mean_mm_year"].iloc[-1], 0)
imx = g["mod16_mean_mm_year"].idxmax()
m["ModMax"], m["ModMaxBanda"] = fmt(g.loc[imx, "mod16_mean_mm_year"], 0), g.loc[imx, "band_label"]

out = P / "cifras_punto1.tex"
out.write_text("% Generado por codigo/punto1/cifras_punto1.py. No editar a mano.\n"
               + "\n".join(f"\\newcommand{{\\{k}}}{{{v}}}" for k, v in m.items()) + "\n", encoding="utf-8")
print(out.read_text(encoding="utf-8"))
