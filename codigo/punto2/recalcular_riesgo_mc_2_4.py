"""Recalcula el riesgo efectivo de 2.4A con un Monte Carlo reproducible.

Cada iteración muestrea una réplica bootstrap de la GEV de 10 minutos,
C, tc, Manning n y pendiente construida. La probabilidad anual efectiva no
se estima contando únicamente excedencias en 5000 sorteos: se obtiene de la
CDF GEV de la réplica para la intensidad que iguala la capacidad.
"""
from pathlib import Path
import math
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "datos" / "punto2" / "Abtsgmuend_Untergroeningen"
OUT = DATA / "diseno_2_4"
SEED = 20261123
N_BOOT = 200
N_MC = 5000
LIFE_YEARS = 30
T_DESIGN = 25


def main():
    rng = np.random.default_rng(SEED)
    summary = pd.read_csv(DATA / "cuenca_preparada" / "cuenca_resumen.csv").set_index("campo")
    A = float(summary.loc["area_km2", "valor"])
    L = float(summary.loc["main_channel_length_m", "valor"])
    S_catch = float(summary.loc["main_channel_slope_m_m", "valor"])
    C0 = float(pd.read_csv(DATA / "cobertura_2_4" / "weighted_runoff_coefficient.csv").weighted_C.iloc[0])
    n0, S0, D = 0.013, 0.010, 1.50
    Qc0 = 0.312 / n0 * D ** (8 / 3) * math.sqrt(S0)
    tc0 = 0.0195 * L ** 0.77 * S_catch ** (-0.385)

    ams = pd.read_csv(DATA / "extremos_2_2" / "ams_hydrological_oct_sep.csv")
    x = ams["max_10min_mm"].dropna().to_numpy(float)
    if len(x) < 10:
        raise ValueError("No hay suficientes máximos anuales de 10 minutos")

    # Réplicas bootstrap de los parámetros GEV-MLE (orden scipy: c, loc, scale).
    boot = []
    for _ in range(N_BOOT):
        xb = rng.choice(x, size=len(x), replace=True)
        pars = stats.genextreme.fit(xb)
        if np.isfinite(pars).all() and pars[2] > 0:
            boot.append(pars)
    pars = np.asarray(boot)
    if len(pars) < 100:
        raise RuntimeError("El bootstrap GEV produjo menos de 100 réplicas válidas")

    idx = rng.integers(0, len(pars), N_MC)
    p = pars[idx]
    C = np.clip(rng.normal(C0, 0.20 * C0, N_MC), 0.10, 0.90)
    tc = np.exp(rng.normal(np.log(tc0), 0.20, N_MC))
    n = np.clip(rng.normal(n0, 0.0015, N_MC), 0.009, 0.020)
    slope = np.clip(rng.normal(S0, 0.002, N_MC), 0.003, 0.020)

    # La duración disponible más próxima es 10 min. Se escala el umbral a tc.
    q25_10 = stats.genextreme.ppf(1 - 1 / T_DESIGN, p[:, 0], p[:, 1], p[:, 2])
    depth_at_tc = q25_10 * (tc / 10.0) ** (-0.20)
    intensity = depth_at_tc / (tc / 60.0)
    q_load = C * intensity * A / 3.6
    q_capacity = 0.312 / n * D ** (8 / 3) * np.sqrt(slope)
    i_star = 3.6 * q_capacity / (C * A)
    depth_star_10 = i_star * (tc / 60.0)
    # Probabilidad anual de superar i* para la réplica GEV seleccionada.
    p_fail = np.clip(1 - stats.genextreme.cdf(depth_star_10, p[:, 0], p[:, 1], p[:, 2]), 0, 1)
    indicator = q_load > q_capacity
    annual_effective = float(np.mean(p_fail))
    life_risk = float(1 - (1 - annual_effective) ** LIFE_YEARS)
    nominal = 1 / T_DESIGN
    fs = Qc0 / (C0 * np.median(q25_10) / (tc0 / 60.0) * A / 3.6)

    draws = pd.DataFrame({
        "bootstrap_replica": idx,
        "C": C, "tc_min": tc, "manning_n": n, "slope_pipe": slope,
        "Q_load_m3s": q_load, "Q_capacity_m3s": q_capacity,
        "i_star_mm_h": i_star, "annual_exceedance_probability": p_fail,
        "load_exceeds_capacity": indicator,
    })
    draws.to_csv(OUT / "monte_carlo_A.csv", index=False, float_format="%.8f")
    summary_out = pd.DataFrame([{
        "seed": SEED, "iterations": N_MC, "bootstrap_replicas": len(pars),
        "duration_reference_min": 10, "T_design_years": T_DESIGN,
        "nominal_annual_probability": nominal,
        "annual_effective_failure_probability": annual_effective,
        "life_years": LIFE_YEARS, "life_risk": life_risk,
        "empirical_indicator_fraction": float(indicator.mean()),
        "Q_capacity_design_m3s": Qc0,
        "Q_load_p50_m3s": float(np.median(q_load)),
        "Q_load_p025_m3s": float(np.quantile(q_load, .025)),
        "Q_load_p975_m3s": float(np.quantile(q_load, .975)),
        "safety_factor_design": fs,
        "method_note": "p_fail is averaged from each bootstrap GEV CDF; indicator fraction is diagnostic, not the risk estimator",
    }])
    summary_out.to_csv(OUT / "riesgo_A.csv", index=False, float_format="%.8f")
    report = f"""# Riesgo Monte Carlo corregido (2.4A)

- Semilla: `{SEED}`; iteraciones: **{N_MC}**; réplicas bootstrap GEV válidas: **{len(pars)}**.
- Periodo de retorno nominal: **T = {T_DESIGN} años**, por lo que 1/T = **{nominal:.4f}**.
- Probabilidad anual efectiva (promedio de CDF GEV por réplica): **{annual_effective:.6f}**.
- Riesgo acumulado en {LIFE_YEARS} años: **{life_risk:.6f} ({life_risk*100:.3f} %)**.
- Fracción diagnóstica de cargas que superan la capacidad en los sorteos: **{indicator.mean():.4f}**.

La fracción de indicadores no sustituye la probabilidad anual efectiva: el diseño
usa la probabilidad de excedencia de cada réplica GEV y luego la promedia. Por eso
una muestra finita puede tener cero excedencias directas sin implicar riesgo físico
nulo. Los parámetros muestreados y las probabilidades por iteración quedan en
`monte_carlo_A.csv`; la síntesis queda en `riesgo_A.csv`.
"""
    (OUT / "revision_riesgo_mc_2_4.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
