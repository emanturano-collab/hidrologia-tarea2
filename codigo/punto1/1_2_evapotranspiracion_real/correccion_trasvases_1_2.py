"""1.2: correccion del balance de largo plazo por los trasvases Chotano-Conchano.

El sistema Chotano-Conchano lleva agua de la vertiente del Maranon al rio Chancay; la
entrega es en Chiroconga (Chancaybanos), aguas arriba de la estacion Racarumi, que esta
en la parte no regulada de la cuenca (Taner et al., 2019). Por eso el caudal medido en
Racarumi incluye agua que no llovio en la cuenca y el balance debe ser ET = P + T - Q.

Volumen anual del trasvase (datos/punto1/metadatos/trasvases_chotano_conchano.csv):
  central 200 hm3/anio (Taner et al., 2019); superior 230 hm3/anio (Gobierno Regional de
  Lambayeque); inferior 133 hm3/anio (aporte citado en el plan de gestion de la cuenca).
Se trata como constante en el periodo comun, porque no hay series anuales publicadas.

Salida: productos/punto1/punto_1_2_correccion_trasvases.csv
Ejecucion: python codigo/punto1/1_2_evapotranspiracion_real/correccion_trasvases_1_2.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
P = ROOT / "productos" / "punto1"
AREA_KM2 = 2363.302
fuentes = pd.read_csv(ROOT / "datos" / "punto1" / "metadatos" / "trasvases_chotano_conchano.csv")
vol = fuentes.set_index("escenario")["volumen_hm3_anio"]
T = vol / AREA_KM2 * 1000  # hm3/anio -> mm/anio sobre la cuenca

prod = pd.read_csv(P / "punto_1_2_4_comparacion_multianual.csv").set_index("series")["mean_mm_year"]
pe = pd.read_csv(P / "1_2_evapotranspiracion_real" / "tablas" / "1_2_2_resumen_propagacion_error_principal.csv")
pm = pe[(pe.precipitation_source == "PL") & (pe.scenario_Q == "main_15pct_bound")].iloc[0]
fe = pd.read_csv(P / "punto_1_2_3_fraccion_evaporativa_resumen.csv").iloc[0]
rn = fe["mean_rn_lambda_mm_year"]
et0 = prod["ET=PISCOp-Q"]
sigma_T = (T["superior"] - T["inferior"]) / np.sqrt(12)  # rango tratado como distribucion uniforme

filas = []
for esc in ("inferior", "central", "superior"):
    et = et0 + T[esc]
    filas.append({"escenario": esc, "trasvase_hm3_anio": vol[esc], "trasvase_mm_anio": T[esc],
                  "ET_balance_sin_trasvase_mm": et0, "ET_balance_corregido_mm": et,
                  "Q_natural_mm": pm["Q_mean_mm_year"] - T[esc],
                  "coef_escorrentia_natural": (pm["Q_mean_mm_year"] - T[esc]) / pm["P_mean_mm_year"],
                  "GLEAM_sobre_balance_pct": 100 * (prod["GLEAM4.3a"] / et - 1),
                  "MOD16_sobre_balance_pct": 100 * (prod["MOD16A2GF v6.1"] / et - 1),
                  "fraccion_evaporativa": et / rn,
                  "sigma_ET_mm": np.sqrt(pm["sigmaET_mm_year"] ** 2 + sigma_T ** 2)})
out = pd.DataFrame(filas)
out.to_csv(P / "punto_1_2_correccion_trasvases.csv", index=False, float_format="%.6f")
print(out.round(2).T.to_string())

# Budyko con la oferta de agua P + T (trasvase central) frente a P sola
from scipy.optimize import brentq

bud = pd.read_csv(P / "1_3_regimen_evaporativo" / "tablas" / "1_3_integracion_1_3_3_Budyko_ET_real_productos.csv")
bud = bud[bud.precipitation == "PISCOp"]
fu = lambda phi, w: 1 + phi - (1 + phi ** w) ** (1 / w)
budyko = lambda phi: np.sqrt(phi * np.tanh(1 / phi) * (1 - np.exp(-phi)))
b = []
for _, r in bud.iterrows():
    for oferta, agua in (("P", r.P_mean_mm_year), ("P + T", r.P_mean_mm_year + T["central"])):
        phi, ei = r.ETo_mean_mm_year / agua, r.ET_mean_mm_year / agua
        w = brentq(lambda x: fu(phi, x) - ei, 1.0001, 20)
        b.append({"producto": r.ET_product, "oferta": oferta, "agua_mm": agua, "phi": phi, "EI": ei,
                  "omega_Fu": w, "Budyko1974": budyko(phi), "distancia_a_Budyko": ei - budyko(phi)})
b = pd.DataFrame(b)
b.to_csv(P / "punto_1_2_correccion_trasvases_budyko.csv", index=False, float_format="%.4f")
print(b.round(3).to_string(index=False))
