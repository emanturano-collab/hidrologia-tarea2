"""Analisis final del punto 2: extremos (2.2), IDF (2.3) y diseno (2.4 A y B).

Es la fuente unica de las cifras del punto 2 en el informe. Lee la serie de
maximos anuales por anio hidrologico (oct-sep), la cobertura WorldCover, la
geometria de la microcuenca y la referencia KOSTRA-DWD-2020, y escribe tablas,
figuras, un JSON de resultados y un archivo de macros LaTeX en
productos/punto2/final/.

Las decisiones de ingenieria estan en config_diseno_2_4.json.

Ejecucion (desde cualquier carpeta):
    python codigo/punto2/analisis_final_punto2.py
"""
from pathlib import Path
import json
import warnings

import numpy as np
import pandas as pd
from scipy import stats, optimize
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import lmoments3 as lm
from lmoments3 import distr

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[2]
DAT = ROOT / "datos" / "punto2" / "Abtsgmuend_Untergroeningen"
OUT = ROOT / "productos" / "punto2" / "final"
TAB = OUT / "tablas"
FIG = OUT / "figuras"
for p in (TAB, FIG):
    p.mkdir(parents=True, exist_ok=True)
CFG = json.loads((Path(__file__).with_name("config_diseno_2_4.json")).read_text(encoding="utf-8"))
RNG = np.random.default_rng(CFG["seed"])

DUR = {"10min": 10, "30min": 30, "1h": 60, "3h": 180, "6h": 360, "12h": 720, "24h": 1440}
TS = [2, 5, 10, 25, 50, 100]
G = 9.81
plt.rcParams.update({"figure.dpi": 150, "font.size": 9})


def weiss(dmin):
    """Factor de Weiss (1964) para una duracion formada por n intervalos fijos de 10 min."""
    if not CFG["aplicar_weiss"]:
        return 1.0
    n = dmin / 10.0
    return 1.0 / (1.0 - 1.0 / (8.0 * n))


# ---------------------------------------------------------------- datos 2.1 / 2.2
ams = pd.read_csv(DAT / "extremos_2_2" / "ams_hydrological_oct_sep.csv")
N = len(ams)
X = {d: ams[f"max_{d}_mm"].to_numpy(float) * weiss(m) for d, m in DUR.items()}
years = ams["hydro_year"].to_numpy()

# Coherencia entre duraciones: la profundidad no puede disminuir con la duracion.
raw = ams[[f"max_{d}_mm" for d in DUR]].to_numpy(float)
incoherentes = int((np.diff(raw, axis=1) < -1e-9).sum())

# Contraste con la lluvia diaria de reloj (control 2.1.5).
lluvia = pd.read_csv(DAT / "abtsgmuend_precipitation_10min.csv", usecols=["timestamp_utc", "precip_mm"])
lluvia["t"] = pd.to_datetime(lluvia["timestamp_utc"].astype(str), format="%Y%m%d%H%M")
lluvia.loc[lluvia["precip_mm"] < 0, "precip_mm"] = np.nan
lluvia = lluvia.set_index("t")["precip_mm"]
diaria = lluvia.resample("D").sum(min_count=1)
hy = diaria.index.year + (diaria.index.month >= 10)
max_diaria = diaria.groupby(hy).max()
ctrl = pd.DataFrame({"hydro_year": years, "max_24h_movil_mm": ams["max_24h_mm"].to_numpy()})
ctrl["max_dia_reloj_mm"] = max_diaria.reindex(years).to_numpy()
ctrl["razon_movil_reloj"] = ctrl["max_24h_movil_mm"] / ctrl["max_dia_reloj_mm"]
ctrl.to_csv(TAB / "control_ams_vs_diaria.csv", index=False, float_format="%.3f")
completitud = pd.read_csv(DAT / "control_2_1" / "completitud_anual.csv")


# ---------------------------------------------------------------- ajustes
def fit(model, x):
    if model == "gev_mle":
        c, loc, sc = stats.genextreme.fit(x)
        return ("gev", c, loc, sc)
    if model == "gev_gmle":
        # Maxima verosimilitud generalizada (Martins y Stedinger, 2000): prior Beta(6, 9)
        # sobre c + 0.5 (convencion de scipy, c = -xi), que estabiliza la forma con N ~ 20.
        p0 = distr.gev.lmom_fit(x)
        start = np.array([np.clip(p0["c"], -0.45, 0.45), p0["loc"], np.log(p0["scale"])])

        def nlp(v):
            c, loc, lsc = v
            if not -0.5 < c < 0.5:
                return np.inf
            ll = stats.genextreme.logpdf(x, c, loc, np.exp(lsc)).sum()
            return -(ll + stats.beta.logpdf(c + 0.5, 6, 9)) if np.isfinite(ll) else np.inf
        sol = optimize.minimize(nlp, start, method="Nelder-Mead", options={"xatol": 1e-6, "fatol": 1e-8, "maxiter": 4000})
        return ("gev", sol.x[0], sol.x[1], float(np.exp(sol.x[2])))
    if model == "gev_lmom":
        p = distr.gev.lmom_fit(x)
        return ("gev", p["c"], p["loc"], p["scale"])
    if model == "gumbel_mle":
        loc, sc = stats.gumbel_r.fit(x)
        return ("gum", 0.0, loc, sc)
    if model == "gumbel_lmom":
        p = distr.gum.lmom_fit(x)
        return ("gum", 0.0, p["loc"], p["scale"])
    if model == "lp3_mom":
        y = np.log10(x)
        g = stats.skew(y, bias=False)
        return ("lp3", g, y.mean(), y.std(ddof=1))
    raise ValueError(model)


def ppf(par, prob):
    kind, a, loc, sc = par
    if kind == "gev":
        return stats.genextreme.ppf(prob, a, loc, sc)
    if kind == "gum":
        return stats.gumbel_r.ppf(prob, loc, sc)
    return 10 ** stats.pearson3.ppf(prob, a, loc, sc)


def sf(par, x):
    kind, a, loc, sc = par
    if kind == "gev":
        return stats.genextreme.sf(x, a, loc, sc)
    if kind == "gum":
        return stats.gumbel_r.sf(x, loc, sc)
    return stats.pearson3.sf(np.log10(x), a, loc, sc)


def cdf(par, x):
    return 1.0 - sf(par, x)


def q(par, T):
    return ppf(par, 1.0 - 1.0 / T)


MODELOS = ["gev_gmle", "gev_mle", "gev_lmom", "gumbel_mle", "gumbel_lmom", "lp3_mom"]
PAR = {(m, d): fit(m, X[d]) for m in MODELOS for d in DUR}
DIS = CFG["distribucion_diseno"]

# Cuantiles (mm) y bondad de ajuste
rows, gof = [], []
for (m, d), par in PAR.items():
    for T in TS:
        rows.append({"duracion": d, "modelo": m, "T": T, "profundidad_mm": q(par, T),
                     "intensidad_mm_h": q(par, T) * 60 / DUR[d]})
    x = np.sort(X[d])
    pg = (np.arange(1, N + 1) - 0.44) / (N + 0.12)  # Gringorten, no excedencia
    ppcc = np.corrcoef(x, ppf(par, pg))[0, 1]
    ks = stats.kstest(x, lambda v: cdf(par, v))
    cvm = stats.cramervonmises(x, lambda v: cdf(par, v))
    gof.append({"duracion": d, "modelo": m, "KS_D": ks.statistic, "KS_p": ks.pvalue,
                "CvM_W2": cvm.statistic, "CvM_p": cvm.pvalue, "PPCC": ppcc,
                "q100_mm": q(par, 100)})
cuant = pd.DataFrame(rows)
cuant.to_csv(TAB / "cuantiles_todas_duraciones.csv", index=False, float_format="%.3f")
gof = pd.DataFrame(gof)
gof.to_csv(TAB / "bondad_ajuste.csv", index=False, float_format="%.4f")

# L-momentos muestrales (corrige lmoment_ratios_sample.csv anterior)
lmr = pd.DataFrame([{"duracion": d, "tau3": lm.lmom_ratios(X[d], nmom=4)[2],
                     "tau4": lm.lmom_ratios(X[d], nmom=4)[3]} for d in DUR])
lmr.to_csv(TAB / "lmomentos_muestrales.csv", index=False, float_format="%.4f")

# Sensibilidad al evento de julio de 2013
sin2013 = years != 2013
sens13 = []
for d in ["10min", "30min", "1h", "6h"]:
    p_all = PAR[(DIS, d)]
    p_ex = fit(DIS, X[d][sin2013])
    for T in (25, 100):
        sens13.append({"duracion": d, "T": T, "con_2013_mm": q(p_all, T),
                       "sin_2013_mm": q(p_ex, T), "forma_c_con": p_all[1], "forma_c_sin": p_ex[1]})
sens13 = pd.DataFrame(sens13)
sens13["cambio_pct"] = 100 * (sens13["sin_2013_mm"] / sens13["con_2013_mm"] - 1)
sens13.to_csv(TAB / "sensibilidad_evento_2013.csv", index=False, float_format="%.3f")

# ---------------------------------------------------------------- bootstrap (anios completos)
B = CFG["n_bootstrap"]
BOOT = {d: [] for d in DUR}
for b in range(B):
    idx = RNG.integers(0, N, N)
    for d in DUR:
        try:
            BOOT[d].append(fit(DIS, X[d][idx]))
        except Exception:
            BOOT[d].append(PAR[(DIS, d)])
bci = []
for d in DUR:
    for T in TS:
        v = np.array([q(p, T) for p in BOOT[d]])
        lo, med, hi = np.nanpercentile(v, [2.5, 50, 97.5])
        bci.append({"duracion": d, "T": T, "T_sobre_N": T / N, "estimado_mm": q(PAR[(DIS, d)], T),
                    "p025_mm": lo, "mediana_mm": med, "p975_mm": hi,
                    "ancho_relativo": (hi - lo) / q(PAR[(DIS, d)], T)})
bci = pd.DataFrame(bci)
bci.to_csv(TAB / "bootstrap_ic95_cuantiles.csv", index=False, float_format="%.3f")

# ---------------------------------------------------------------- IDF 2.3
# Forma de Koutsoyiannis et al. (1998): i = w(T) / (d + theta)^eta, d en horas.
dd = np.array([DUR[d] / 60 for d in DUR])


def idf_points(model):
    return np.array([[q(PAR[(model, d)], T) * 60 / DUR[d] for d in DUR] for T in TS])


def fit_idf(I):
    def res(p):
        th, eta = p[0], p[1]
        w = p[2:]
        pred = np.log(w[:, None]) - eta * np.log(dd[None, :] + th)
        return (pred - np.log(I)).ravel()
    p0 = np.r_[0.1, 0.7, I[:, 0] * (dd[0] + 0.1) ** 0.7]
    sol = optimize.least_squares(res, p0, bounds=(np.r_[0, 0.01, np.full(len(TS), 1e-6)],
                                                  np.r_[5, 1.0, np.full(len(TS), 1e6)]))
    return sol.x


IDF = {}
for m in MODELOS:
    I = idf_points(m)
    p = fit_idf(I)
    pred = p[2:, None] / (dd[None, :] + p[0]) ** p[1]
    IDF[m] = {"theta_h": p[0], "eta": p[1], "w": dict(zip(TS, p[2:])),
              "rmse_mm_h": float(np.sqrt(np.mean((pred - I) ** 2))),
              "err_rel_max": float(np.max(np.abs(pred / I - 1))),
              "r2_log": float(1 - np.sum((np.log(pred) - np.log(I)) ** 2) / np.sum((np.log(I) - np.log(I).mean()) ** 2))}
pd.DataFrame([{"modelo": m, "theta_h": v["theta_h"], "eta": v["eta"],
               **{f"w_T{T}": v["w"][T] for T in TS}, "rmse_mm_h": v["rmse_mm_h"],
               "error_relativo_max": v["err_rel_max"], "R2_log": v["r2_log"]} for m, v in IDF.items()]
             ).to_csv(TAB / "idf_parametros_koutsoyiannis.csv", index=False, float_format="%.5f")


def w_of_T(model, T):
    """w(T) interpolado en log(T) entre los periodos ajustados."""
    return float(np.exp(np.interp(np.log(T), np.log(TS), np.log([IDF[model]["w"][t] for t in TS]))))


def intensidad(dmin, T, model=DIS):
    return w_of_T(model, T) / (dmin / 60 + IDF[model]["theta_h"]) ** IDF[model]["eta"]


# Intensidad de una replica bootstrap a duracion arbitraria: interpolacion log-log entre
# las duraciones con datos (por debajo de 10 min se extrapola con la pendiente 10-30 min).
DM = np.array(list(DUR.values()), float)
DK = list(DUR)


def _bracket(dmin):
    j = int(np.clip(np.searchsorted(DM, dmin) - 1, 0, len(DM) - 2))
    return j, (np.log(dmin) - np.log(DM[j])) / (np.log(DM[j + 1]) - np.log(DM[j]))


def intensidad_rep(r, dmin, T):
    j, f = _bracket(dmin)
    i0 = q(BOOT[DK[j]][r], T) * 60 / DM[j]
    i1 = q(BOOT[DK[j + 1]][r], T) * 60 / DM[j + 1]
    return float(np.exp(np.log(i0) + f * (np.log(i1) - np.log(i0))))


def prob_exc_rep(r, dmin, i_star):
    j, f = _bracket(dmin)
    p0 = sf(BOOT[DK[j]][r], i_star * DM[j] / 60)
    p1 = sf(BOOT[DK[j + 1]][r], i_star * DM[j + 1] / 60)
    p0, p1 = max(p0, 1e-12), max(p1, 1e-12)
    return float(min(1.0, np.exp(np.log(p0) + f * (np.log(p1) - np.log(p0)))))


# KOSTRA-DWD-2020 con su incertidumbre (UC) en la celda de la estacion
def leer_asc(path, row, col):
    with open(path) as fh:
        head = [next(fh) for _ in range(6)]
        data = np.loadtxt(fh)
    return float(data[row, col])


cell = pd.read_csv(DAT / "idf_2_3" / "kostra_station_cell.csv")
r0, c0 = int(cell["row"].iloc[0]), int(cell["col"].iloc[0])
kos = []
for dname, code in {"10min": "00010", "1h": "00060", "6h": "00360", "24h": "01440"}.items():
    for T in [2, 5, 10, 20, 30, 50, 100]:
        hn = leer_asc(DAT / "kostra" / f"Hn_KOSTRA-DWD-2020_D{code}_T{T:03d}.asc", r0, c0)
        uc = leer_asc(DAT / "kostra" / f"UC_KOSTRA-DWD-2020_D{code}_T{T:03d}.asc", r0, c0)
        loc = q(PAR[(DIS, dname)], T)
        bt = bci[(bci.duracion == dname) & (bci["T"] == T)]
        kos.append({"duracion": dname, "T": T, "kostra_mm": hn, "kostra_UC_pct": uc,
                    "kostra_inf_mm": hn * (1 - uc / 100), "kostra_sup_mm": hn * (1 + uc / 100),
                    "local_mm": loc, "razon_local_kostra": loc / hn,
                    "local_sin2013_mm": q(fit(DIS, X[dname][sin2013]), T)})
kos = pd.DataFrame(kos)
check = cell[(cell.duration == "10min") & (cell.T_years == 2)]["kostra_depth_mm"].iloc[0]
assert abs(kos.query("duracion=='10min' and T==2")["kostra_mm"].iloc[0] - check) < 1e-6, "indice de celda KOSTRA"
kos.to_csv(TAB / "comparacion_kostra_uc.csv", index=False, float_format="%.3f")

# Periodo de retorno de eventos recientes documentados
eventos = []
for anio in (2013, 2018, 2021):
    for d in ("1h",):
        x = X[d][years == anio][0]
        Tp = 1 / sf(PAR[(DIS, d)], x)
        Tb = np.array([1 / max(sf(p, x), 1e-12) for p in BOOT[d]])
        eventos.append({"anio_hidrologico": anio, "duracion": d, "profundidad_mm": x,
                        "T_estimado": Tp, "T_p025": np.percentile(Tb, 2.5), "T_p975": np.percentile(Tb, 97.5)})
eventos = pd.DataFrame(eventos)
eventos.to_csv(TAB / "eventos_recientes_periodo_retorno.csv", index=False, float_format="%.2f")

# ---------------------------------------------------------------- 2.4 A
res = pd.read_csv(DAT / "cuenca_preparada" / "cuenca_resumen.csv").set_index("campo")["valor"]
A = float(res["area_km2"])
L = float(res["main_channel_length_m"])
S = float(res["main_channel_slope_m_m"])
wc = pd.read_csv(ROOT / CFG["C_pre_fuente"])
C0 = float(wc["weighted_contribution"].sum())


def tc_kirpich(L, S):
    return 0.0195 * L ** 0.77 * S ** -0.385


def tc_kerby(L, S, N):
    return 1.44 * (L * N) ** 0.467 * S ** -0.235


def tc_scs(L, S, CN):
    """Retardo SCS (NRCS, 2010): tL[h] = L^0.8 (Sr+1)^0.7 / (1900 Y^0.5), L en pies,
    Sr = 1000/CN - 10 en pulgadas, Y pendiente en %. tc = tL / 0.6."""
    Sr = 1000 / CN - 10
    tl = (L * 3.28084) ** 0.8 * (Sr + 1) ** 0.7 / (1900 * (100 * S) ** 0.5)
    return tl / 0.6 * 60


TC = {"Kirpich": tc_kirpich(L, S), "Kerby": tc_kerby(L, S, CFG["kerby_N"]), "SCS-lag": tc_scs(L, S, CFG["CN_pre"])}
pd.DataFrame([{"formula": k, "tc_min": v} for k, v in TC.items()]).to_csv(TAB / "tc_formulas.csv", index=False, float_format="%.3f")
tc0 = TC[CFG["tc_formula_diseno"]]
T0 = CFG["T_diseno_anios"]
n0, S0 = CFG["n_manning"], CFG["S_tuberia"]
DC = np.array(CFG["diametros_comerciales_m"])


def qp(C, i):
    return C * i * A / 3.6


def d_calc(Q, n=n0, s=S0):
    return (n * Q / (0.312 * s ** 0.5)) ** 0.375


def d_com(Q):
    return float(DC[DC >= d_calc(Q) - 1e-9][0])


def q_cap(D, n=n0, s=S0):
    return 0.312 / n * D ** (8 / 3) * s ** 0.5


i0 = intensidad(tc0, T0)
Q0 = qp(C0, i0)
D0c = d_calc(Q0)
D0 = d_com(Q0)
Qc0 = q_cap(D0)

# Sensibilidad (2.4.A.5)
sens = [("Base", f"{CFG['tc_formula_diseno']}, {DIS}, C={C0:.3f}", Q0)]
for k, v in TC.items():
    if k != CFG["tc_formula_diseno"]:
        sens.append(("tc", f"tc {k} ({v:.1f} min)", qp(C0, intensidad(v, T0))))
for f in (1 - CFG["C_variacion_relativa"], 1 + CFG["C_variacion_relativa"]):
    sens.append(("C", f"C x{f:.1f} ({C0 * f:.3f})", qp(C0 * f, i0)))
iboot = np.array([intensidad_rep(r, tc0, T0) for r in range(B)])
for lab, pc in (("IC95 inferior IDF", 2.5), ("IC95 superior IDF", 97.5)):
    sens.append(("IDF", lab, qp(C0, np.percentile(iboot, pc))))
for m in MODELOS:
    if m != DIS:
        sens.append(("Distribucion", f"IDF {m}", qp(C0, intensidad(tc0, T0, m))))
sens.append(("Evento 2013", "Distribucion de diseno sin 2013 (IDF escalada)",
             Q0 * float(sens13.query("duracion=='10min' and T==25")["sin_2013_mm"].iloc[0]
                        / sens13.query("duracion=='10min' and T==25")["con_2013_mm"].iloc[0])))
sens = pd.DataFrame(sens, columns=["fuente", "escenario", "Qp_m3s"])
sens["D_calculado_m"] = sens["Qp_m3s"].map(d_calc)
sens["D_comercial_m"] = sens["Qp_m3s"].map(d_com)
sens.to_csv(TAB / "sensibilidad_2_4A.csv", index=False, float_format="%.4f")
rank = (sens[sens.fuente != "Base"].groupby("fuente")["D_calculado_m"]
        .agg(lambda s: s.max() - s.min() if len(s) > 1 else abs(s.iloc[0] - D0c))
        .sort_values(ascending=False))
rank_tbl = pd.DataFrame({"fuente": rank.index, "rango_D_calculado_m": rank.values})
for col, fn in (("D_min_m", "min"), ("D_max_m", "max")):
    rank_tbl[col] = rank_tbl["fuente"].map(sens.groupby("fuente")["D_calculado_m"].agg(fn))
rank_tbl.to_csv(TAB / "ranking_incertidumbre_2_4A.csv", index=False, float_format="%.4f")

# Monte Carlo (2.4.A.6)
M = CFG["n_montecarlo"]
tcs = np.exp(RNG.triangular(np.log(TC["Kirpich"]), np.log(tc0), np.log(TC["Kerby"]), M))  # moda en el tc de diseno
Cs = C0 * RNG.uniform(1 - CFG["C_variacion_relativa"], 1 + CFG["C_variacion_relativa"], M)
ns = RNG.uniform(*CFG["n_manning_rango"], M)
Ss = np.clip(RNG.normal(S0, CFG["S_tuberia_desv"], M), 0.004, None)
rs = RNG.integers(0, B, M)
pf, QL = np.empty(M), np.empty(M)
for k in range(M):
    qc = q_cap(D0, ns[k], Ss[k])
    istar = 3.6 * qc / (Cs[k] * A)
    pf[k] = prob_exc_rep(rs[k], tcs[k], istar)
    QL[k] = qp(Cs[k], intensidad_rep(rs[k], tcs[k], T0))
Qcs = q_cap(D0, ns, Ss)
p_eff = float(pf.mean())
nvida = CFG["vida_util_anios"]
mc = {"iteraciones": M, "p_anual_nominal": 1 / T0, "p_anual_efectiva": p_eff,
      "riesgo_vida_nominal": 1 - (1 - 1 / T0) ** nvida, "riesgo_vida_efectivo": 1 - (1 - p_eff) ** nvida,
      "T_efectivo": 1 / p_eff, "prob_QL_mayor_Qc": float(np.mean(QL > Qcs)),
      "QL_p025": float(np.percentile(QL, 2.5)), "QL_p50": float(np.median(QL)), "QL_p975": float(np.percentile(QL, 97.5)),
      "D_calc_p025": float(d_calc(np.percentile(QL, 2.5))), "D_calc_p975": float(d_calc(np.percentile(QL, 97.5))),
      "FS_diseno": Qc0 / Q0}
pd.DataFrame([mc]).to_csv(TAB / "montecarlo_2_4A.csv", index=False, float_format="%.5f")

# Riesgo efectivo para diametros comerciales alternativos (mismas muestras)
alt = []
for Dk in DC[(DC >= D0 - 1e-9)][:4]:
    pk = np.array([prob_exc_rep(rs[k], tcs[k], 3.6 * q_cap(Dk, ns[k], Ss[k]) / (Cs[k] * A)) for k in range(M)]).mean()
    alt.append({"D_m": Dk, "Qc_m3s": q_cap(Dk), "FS": q_cap(Dk) / Q0, "p_anual_efectiva": pk,
                "T_efectivo": 1 / pk, "riesgo_vida_efectivo": 1 - (1 - pk) ** CFG["vida_util_anios"]})
alt = pd.DataFrame(alt)
alt.to_csv(TAB / "riesgo_por_diametro_2_4A.csv", index=False, float_format="%.4f")
# Criterio: menor diametro comercial cuya probabilidad anual efectiva no supera la nominal 1/T
ok = alt[alt["p_anual_efectiva"] <= 1 / T0]
rec = (ok.iloc[0] if len(ok) else alt.iloc[-1]).to_dict()

# Periodo de retorno y riesgo (2.4.A.3)
riesgo = pd.DataFrame([{"T": T, "riesgo_vida_util": 1 - (1 - 1 / T) ** nvida} for T in [2, 5, 10, 25, 50, 100, 200]])
T_req = 1 / (1 - (1 - CFG["riesgo_aceptable_vida_util"]) ** (1 / nvida))
riesgo.to_csv(TAB / "riesgo_vs_T.csv", index=False, float_format="%.4f")

# Escala (2.4.A.7): FRA de Svensson y Jones (2010), forma NERC (1975) aproximada
escala = pd.read_csv(DAT / "diseno_2_4" / "escala_metodo_racional.csv")

# ---------------------------------------------------------------- 2.4 B
tc_u = tc_scs(L, S, CFG["CN_urb"]) * tc0 / TC["SCS-lag"] if CFG["tc_formula_diseno"] == "SCS-lag" else tc0 * 0.6
Cu = CFG["C_urb"]
Qpre = Q0
dt = 0.25  # min
Cd = CFG["orificio_Cd"]
hmax = CFG["tanque_profundidad_util_m"]
Ao = Qpre / (Cd * np.sqrt(2 * G * hmax))
Dor = float(np.sqrt(4 * Ao / np.pi))


def trapecio(d):
    Qpk = qp(Cu, intensidad(d, T0))
    t = np.arange(0, d + tc_u + dt, dt)
    Qt = np.interp(t, [0, tc_u, d, d + tc_u], [0, Qpk, Qpk, 0])
    return t, Qt, Qpk


def hietograma(pos):
    Dh, h = CFG["hietograma_duracion_min"], CFG["hietograma_dt_min"]
    k = np.arange(1, int(Dh / h) + 1)
    P = np.array([intensidad(j * h, T0) * j * h / 60 for j in k])
    inc = np.diff(np.r_[0, P])
    order = np.argsort(inc)[::-1]
    n = len(inc)
    if pos == "inicio":
        blocks = inc[order]
    elif pos == "final":
        blocks = inc[order][::-1]
    else:
        blocks = np.zeros(n)
        c = n // 2
        idx = [c]
        for j in range(1, n):
            idx.append(c + (j + 1) // 2 if j % 2 else c - j // 2)
        for j, b in zip(idx, inc[order]):
            blocks[int(np.clip(j, 0, n - 1))] = b
    return blocks / h * 60  # mm/h por bloque


def tiempo_area(i_blocks):
    h = CFG["hietograma_dt_min"]
    t = np.arange(0, len(i_blocks) * h + tc_u + dt, dt)
    it = np.where(t < len(i_blocks) * h, i_blocks[np.minimum((t // h).astype(int), len(i_blocks) - 1)], 0.0)
    w = max(1, int(round(tc_u / dt)))
    ibar = np.convolve(it, np.ones(w) / w)[: len(t)]
    return t, qp(Cu, ibar)


def transitar(Qin, At):
    s, hmx, omx = 0.0, 0.0, 0.0
    out = np.empty_like(Qin)
    for j, qi in enumerate(Qin):
        h = s / At
        o = Cd * Ao * np.sqrt(2 * G * max(h, 0))
        s = max(0.0, s + (qi - o) * dt * 60)
        out[j] = o
        hmx = max(hmx, h)
    return hmx, out


def area_requerida(Qin):
    lo, hi = 1.0, 1e5
    for _ in range(60):
        mid = np.sqrt(lo * hi)
        if transitar(Qin, mid)[0] > hmax:
            lo = mid
        else:
            hi = mid
    return hi


filasB, hidros = [], {}
for d in CFG["trapezoidal_duraciones_min"]:
    if d < tc_u:
        continue
    t, Qt, Qpk = trapecio(d)
    At = area_requerida(Qt)
    filasB.append({"metodo": "trapezoidal", "escenario": f"d={d} min", "Q_entrada_max_m3s": Qpk,
                   "volumen_entrada_m3": Qt.sum() * dt * 60, "area_tanque_m2": At, "volumen_requerido_m3": At * hmax})
    hidros[("trap", d)] = (t, Qt)
for pos in ("inicio", "centro", "final"):
    t, Qt = tiempo_area(hietograma(pos))
    At = area_requerida(Qt)
    filasB.append({"metodo": "bloques alternos + tiempo-area", "escenario": f"pico al {pos}",
                   "Q_entrada_max_m3s": Qt.max(), "volumen_entrada_m3": Qt.sum() * dt * 60,
                   "area_tanque_m2": At, "volumen_requerido_m3": At * hmax})
    hidros[("hiet", pos)] = (t, Qt)
tb = pd.DataFrame(filasB)
crit = tb.loc[tb["volumen_requerido_m3"].idxmax()]
lado = float(np.ceil(np.sqrt(crit["area_tanque_m2"]) * 2) / 2)
At_dis = lado ** 2
verif = []
for key, (t, Qt) in hidros.items():
    hm, out = transitar(Qt, At_dis)
    verif.append({"hidrograma": f"{key[0]} {key[1]}", "h_max_m": hm, "Q_salida_max_m3s": out.max(),
                  "Q_entrada_max_m3s": Qt.max(), "cumple_Qsal_le_Qpre": bool(out.max() <= Qpre * 1.0001)})
verif = pd.DataFrame(verif)
tb.to_csv(TAB / "tanque_escenarios_2_4B.csv", index=False, float_format="%.3f")
verif.to_csv(TAB / "tanque_verificacion_2_4B.csv", index=False, float_format="%.4f")
trap_max = tb[tb.metodo == "trapezoidal"]["volumen_requerido_m3"].max()
trap_crit = tb[tb.metodo == "trapezoidal"].loc[tb[tb.metodo == "trapezoidal"]["volumen_requerido_m3"].idxmax(), "escenario"]
hiet = tb[tb.metodo != "trapezoidal"].set_index("escenario")["volumen_requerido_m3"]

# ---------------------------------------------------------------- figuras
# Diagrama de razones de L-momentos
fig, ax = plt.subplots(figsize=(5.2, 4.2))
t3 = np.linspace(-0.2, 0.7, 200)
curvas = {"GEV": (distr.gev, "c", np.linspace(-0.6, 0.6, 200)), "GLO": (distr.glo, "k", np.linspace(-0.7, 0.6, 200)),
          "GPA": (distr.gpa, "c", np.linspace(-0.6, 1.0, 200)), "LN3": (distr.gno, "k", np.linspace(-1.5, 1.5, 200)),
          "PE3": (distr.pe3, "skew", np.linspace(-1, 4, 200))}
for name, (dist, key, grid) in curvas.items():
    pts = np.array([dist.lmom_ratios(**{key: g}, loc=0, scale=1, nmom=4)[2:4] for g in grid], float)
    ax.plot(pts[:, 0], pts[:, 1], lw=1, label=name)
ax.plot(0.1699, 0.1504, "k^", label="Gumbel")
ax.plot(0, 0.1226, "ks", label="Normal")
ax.scatter(lmr.tau3, lmr.tau4, c="crimson", zorder=5, label="Muestra (duraciones)")
for _, r in lmr.iterrows():
    ax.annotate(r.duracion, (r.tau3, r.tau4), fontsize=7, xytext=(3, 2), textcoords="offset points")
ax.set(xlim=(-0.1, 0.7), ylim=(-0.05, 0.6), xlabel=r"L-asimetría $\tau_3$", ylabel=r"L-curtosis $\tau_4$")
ax.legend(fontsize=7, ncol=2)
fig.tight_layout()
fig.savefig(FIG / "lmomentos_diagrama.png")
plt.close(fig)

# Graficas de probabilidad (Gringorten) para 10 min y 1 h
fig, axs = plt.subplots(1, 2, figsize=(8, 3.6))
for ax, d in zip(axs, ["10min", "1h"]):
    x = np.sort(X[d])
    pg = (np.arange(1, N + 1) - 0.44) / (N + 0.12)
    ax.plot(-np.log(-np.log(pg)), x, "ko", ms=4, label="Observado (Gringorten)")
    pp = np.linspace(0.02, 0.995, 200)
    for m, st in (("gev_gmle", "-"), ("gev_mle", "--"), ("gumbel_mle", ":"), ("lp3_mom", "-.")):
        ax.plot(-np.log(-np.log(pp)), ppf(PAR[(m, d)], pp), st, label=m)
    ax.set(title=f"Duración {d}", xlabel="Variable reducida de Gumbel  $-\\ln(-\\ln F)$", ylabel="Profundidad (mm)")
axs[0].legend(fontsize=7)
fig.tight_layout()
fig.savefig(FIG / "graficas_probabilidad.png")
plt.close(fig)

# Ancho relativo del IC95 frente a T/N
fig, ax = plt.subplots(figsize=(5, 3.6))
for d in DUR:
    s = bci[bci.duracion == d]
    ax.plot(s["T_sobre_N"], s["ancho_relativo"], "o-", ms=3, label=d)
ax.axvline(2, color="grey", ls="--", lw=0.8)
ax.text(2.05, ax.get_ylim()[1] * 0.9, "T = 2N", fontsize=7)
ax.set(xscale="log", xlabel="T / N", ylabel="Ancho relativo del IC 95 %")
ax.legend(fontsize=7, ncol=2)
fig.tight_layout()
fig.savefig(FIG / "ancho_relativo_ic.png")
plt.close(fig)

# IDF con bandas para T=10 y T=100 y KOSTRA
fig, ax = plt.subplots(figsize=(6, 4.2))
dg = np.geomspace(10, 1440, 100)
for T, col in ((2, "tab:green"), (10, "tab:blue"), (25, "tab:purple"), (100, "tab:red")):
    ax.plot(dg, [intensidad(v, T) for v in dg], color=col, label=f"T = {T} años")
    if T in (10, 100):
        lo = [np.percentile([intensidad_rep(r, v, T) for r in range(0, B, 5)], 2.5) for v in dg[::5]]
        hi = [np.percentile([intensidad_rep(r, v, T) for r in range(0, B, 5)], 97.5) for v in dg[::5]]
        ax.fill_between(dg[::5], lo, hi, color=col, alpha=0.15)
k10 = kos[kos["T"] == 10]
k100 = kos[kos["T"] == 100]
for kk, col in ((k10, "tab:blue"), (k100, "tab:red")):
    ax.errorbar([DUR[d] for d in kk.duracion], kk.kostra_mm * 60 / np.array([DUR[d] for d in kk.duracion]),
                yerr=kk.kostra_mm * kk.kostra_UC_pct / 100 * 60 / np.array([DUR[d] for d in kk.duracion]),
                fmt="s", color=col, mfc="white", ms=4, capsize=2)
ax.plot([], [], "s", color="k", mfc="white", label="KOSTRA-DWD-2020 ± UC")
ax.set(xscale="log", yscale="log", xlabel="Duración (min)", ylabel="Intensidad (mm/h)")
ax.legend(fontsize=7)
fig.tight_layout()
fig.savefig(FIG / "idf_bandas_kostra.png")
plt.close(fig)

# Tornado 2.4A
fig, ax = plt.subplots(figsize=(5.5, 3))
rt = rank_tbl.iloc[::-1]
ax.barh(rt.fuente, rt.D_max_m - rt.D_min_m, left=rt.D_min_m, color="tab:blue", alpha=0.7)
ax.axvline(D0c, color="k", lw=1, label=f"D calculado base = {D0c:.2f} m")
ax.axvline(D0, color="tab:red", ls="--", lw=1, label=f"D comercial = {D0:.2f} m")
ax.set(xlabel="Diámetro calculado (m)")
ax.legend(fontsize=7, loc="lower right")
fig.tight_layout()
fig.savefig(FIG / "tornado_2_4A.png")
plt.close(fig)

# Hidrogramas 2.4B
fig, axs = plt.subplots(1, 2, figsize=(9, 3.6), sharey=True)
for key, (t, Qt) in hidros.items():
    if key[0] == "trap":
        axs[0].plot(t, Qt, lw=1, label=f"d = {key[1]} min")
    else:
        axs[1].plot(t, Qt, lw=1, label=f"Pico al {key[1]}")
t, Qt = hidros[("hiet", crit["escenario"].replace("pico al ", ""))] if crit["metodo"] != "trapezoidal" else hidros[("trap", int(crit["escenario"].split("=")[1].split()[0]))]
_, out = transitar(Qt, At_dis)
ax_c = axs[1] if crit["metodo"] != "trapezoidal" else axs[0]
ax_c.plot(t, out, "k--", lw=1.2, label="Salida (caso crítico)")
for ax in axs:
    ax.axhline(Qpre, color="tab:red", lw=0.8, ls=":")
    ax.set(xlabel="Tiempo (min)", xlim=(0, 200))
axs[0].set(ylabel="Caudal (m³/s)", title="Racional modificado (trapezoidal)")
axs[1].set(title="Bloques alternos + tiempo-área")
axs[0].legend(fontsize=6, ncol=2)
axs[1].legend(fontsize=7)
fig.tight_layout()
fig.savefig(FIG / "hidrogramas_tanque_2_4B.png")
plt.close(fig)

# ---------------------------------------------------------------- resultados
R = {
    "N_anios": N, "anios": [int(years.min()), int(years.max())], "incoherencias_duracion": incoherentes,
    "razon_movil_reloj_mediana": float(ctrl["razon_movil_reloj"].median()),
    "completitud_min_pct": float(completitud["completeness_pct"].min()),
    "weiss": {d: weiss(m) for d, m in DUR.items()},
    "distribucion_diseno": DIS,
    "tc_min": TC, "tc_diseno_min": tc0, "tc_urb_min": tc_u, "A_km2": A, "L_m": L, "S_m_m": S, "C_pre": C0, "C_urb": Cu,
    "T_diseno": T0, "vida_util": nvida, "riesgo_aceptable": CFG["riesgo_aceptable_vida_util"], "T_requerido_por_riesgo": T_req,
    "i_diseno_mm_h": i0, "Qp_m3s": Q0, "D_calculado_m": D0c, "D_comercial_m": D0, "Qc_m3s": Qc0,
    "montecarlo": mc, "diametro_recomendado": rec, "ranking_incertidumbre": rank_tbl.to_dict("records"),
    "idf": {m: {k: v for k, v in IDF[m].items() if k != "w"} | {"w": {str(k): v for k, v in IDF[m]["w"].items()}} for m in MODELOS},
    "tanque": {"Qpre_m3s": Qpre, "orificio_area_m2": Ao, "orificio_D_m": Dor, "Cd": Cd, "h_util_m": hmax,
               "critico": crit.to_dict(), "lado_m": lado, "area_m2": At_dis, "volumen_util_m3": At_dis * hmax,
               "trapezoidal_max_m3": float(trap_max), "trapezoidal_critico": trap_crit,
               "hietograma_m3": hiet.to_dict(), "cumple_todos": bool(verif["cumple_Qsal_le_Qpre"].all()),
               "Q_salida_max_m3s": float(verif["Q_salida_max_m3s"].max())},
}
(OUT / "resultados_punto2.json").write_text(json.dumps(R, indent=2, ensure_ascii=False, default=float), encoding="utf-8")


# Macros LaTeX: cada cifra del informe sale de aqui
def fmt(v, nd):
    return f"{v:.{nd}f}".replace(".", "{,}")


g = lambda d, T, col="profundidad_mm": float(cuant.query("duracion==@d and modelo==@DIS and T==@T")[col].iloc[0])
kq = lambda d, T, col: float(kos.query("duracion==@d and T==@T")[col].iloc[0])
macros = {
    "NAnios": str(N), "AreaMicro": fmt(A, 3), "LongCauce": fmt(L, 1), "PendCauce": fmt(S, 3),
    "Cpre": fmt(C0, 3), "Cpremenos": fmt(C0 * 0.8, 3), "Cpremas": fmt(C0 * 1.2, 3), "Curb": fmt(Cu, 2),
    "tcKirpich": fmt(TC["Kirpich"], 1), "tcKerby": fmt(TC["Kerby"], 1), "tcSCS": fmt(TC["SCS-lag"], 1), "tcUrb": fmt(tc_u, 1),
    "Tdis": str(T0), "Vida": str(nvida), "RiesgoNom": fmt(100 * mc["riesgo_vida_nominal"], 1),
    "RiesgoAcept": fmt(100 * CFG["riesgo_aceptable_vida_util"], 0), "Treq": fmt(T_req, 1),
    "Idis": fmt(i0, 1), "Qp": fmt(Q0, 3), "Dcalc": fmt(D0c, 2), "Dcom": fmt(D0, 2), "Qcap": fmt(Qc0, 2),
    "FS": fmt(mc["FS_diseno"], 2), "Drec": fmt(rec["D_m"], 2), "QcapRec": fmt(rec["Qc_m3s"], 2), "FSrec": fmt(rec["FS"], 2),
    "PeffRec": fmt(100 * rec["p_anual_efectiva"], 2), "TeffRec": fmt(rec["T_efectivo"], 0),
    "RiesgoEffRec": fmt(100 * rec["riesgo_vida_efectivo"], 1), "Peff": fmt(100 * p_eff, 2), "Teff": fmt(mc["T_efectivo"], 0),
    "RiesgoEff": fmt(100 * mc["riesgo_vida_efectivo"], 1), "ProbQLQc": fmt(100 * mc["prob_QL_mayor_Qc"], 1),
    "QLlo": fmt(mc["QL_p025"], 2), "QLhi": fmt(mc["QL_p975"], 2), "Dlo": fmt(mc["D_calc_p025"], 2), "Dhi": fmt(mc["D_calc_p975"], 2),
    "NMC": str(M), "NBoot": str(B),
    "WeissDiez": fmt(weiss(10), 3), "WeissHora": fmt(weiss(60), 3),
    "QdiezTcien": fmt(g("10min", 100), 1), "QhoraTcien": fmt(g("1h", 100), 1),
    "KosHoraTcien": fmt(kq("1h", 100, "kostra_mm"), 1), "RazonHoraTcien": fmt(kq("1h", 100, "razon_local_kostra"), 2),
    "KosUCHoraTcien": fmt(kq("1h", 100, "kostra_UC_pct"), 0), "SinHoraTcien": fmt(kq("1h", 100, "local_sin2013_mm"), 1),
    "RazonDiezTveinte": fmt(kq("10min", 20, "razon_local_kostra"), 2),
    "IDFtheta": fmt(IDF[DIS]["theta_h"], 3), "IDFeta": fmt(IDF[DIS]["eta"], 3), "IDFrmse": fmt(IDF[DIS]["rmse_mm_h"], 1),
    "IDFerr": fmt(100 * IDF[DIS]["err_rel_max"], 1), "IDFrdos": fmt(IDF[DIS]["r2_log"], 3),
    "Qpre": fmt(Qpre, 3), "DOrif": fmt(Dor, 3), "Cd": fmt(Cd, 2), "Hutil": fmt(hmax, 1),
    "VolCrit": fmt(crit["volumen_requerido_m3"], 0), "EscCrit": str(crit["metodo"]) + ", " + str(crit["escenario"]),
    "LadoTanque": fmt(lado, 1), "VolUtil": fmt(At_dis * hmax, 0), "VolTrap": fmt(trap_max, 0), "TrapCrit": str(trap_crit),
    "VolInicio": fmt(hiet["pico al inicio"], 0), "VolCentro": fmt(hiet["pico al centro"], 0), "VolFinal": fmt(hiet["pico al final"], 0),
    "QsalMax": fmt(R["tanque"]["Q_salida_max_m3s"], 3),
    "TeventoTrece": fmt(eventos.query("anio_hidrologico==2013")["T_estimado"].iloc[0], 0),
    "TeventoVeintiuno": fmt(eventos.query("anio_hidrologico==2021")["T_estimado"].iloc[0], 1),
    "TeventoVeintiunoLo": fmt(eventos.query("anio_hidrologico==2021")["T_p025"].iloc[0], 1),
    "TeventoVeintiunoHi": fmt(eventos.query("anio_hidrologico==2021")["T_p975"].iloc[0], 0),
    "AnchoTcien": fmt(100 * float(bci.query("duracion=='10min' and T==100")["ancho_relativo"].iloc[0]), 0),
    "CompletMin": fmt(R["completitud_min_pct"], 2),
}
(OUT / "cifras_punto2.tex").write_text(
    "% Generado por codigo/punto2/analisis_final_punto2.py. No editar a mano.\n"
    + "\n".join(f"\\newcommand{{\\{k}}}{{{v}}}" for k, v in macros.items()) + "\n", encoding="utf-8")
print(json.dumps({k: R[k] for k in ("tc_min", "Qp_m3s", "D_calculado_m", "D_comercial_m", "montecarlo")}, indent=1, default=float))
print(alt.to_string())
print(tb.to_string())
print(verif.to_string())
print(rank_tbl.to_string())
print(kos.query("T in (10,100)").to_string())
print(sens13.to_string())
print(pd.Series({m: IDF[m]["r2_log"] for m in MODELOS}))
