"""Descomposición exploratoria de ΔQ con Budyko-Fu para Racarumi (PE_200907).

No descarga ni recalcula ETo. Usa la serie anual hidrológica ya validada en 1.3,
PISCOp (PL), caudal CAMELS-PE y ETo FAO-56. Las contribuciones se obtienen con
Shapley sobre los estados promedio de dos bloques completos; por construcción,
suman exactamente el cambio Fu reconstruido.
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROJECT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
P14 = PROJECT / "productos" / "punto1" / "1_4_cambios_demanda_evaporativa" / "bonificacion_budyko"
OUT_DATA = P14 / "Datos procesados"
OUT_TAB = P14 / "Tablas"
OUT_FIG = P14 / "Figuras"
OUT_ANN = P14 / "Anexos y referencias"
for folder in (OUT_DATA, OUT_TAB, OUT_FIG, OUT_ANN):
    folder.mkdir(parents=True, exist_ok=True)

ANNUAL = PROJECT / "datos" / "punto1" / "procesados" / "1_3_regimen_evaporativo" / "1_3_serie_anual_hidrologica_P_Q_ETo_y_diagnosticos.csv"
FU = PROJECT / "productos" / "punto1" / "1_3_regimen_evaporativo" / "tablas" / "1_3_3_budyko_sensibilidad_Fu_y_verificacion_matematica.csv"
T1_TRENDS = PROJECT / "datos" / "punto1" / "originales" / "tarea1_minimos" / "resultados_comparativos.csv"


def fu(phi: float, omega: float) -> float:
    """ET/P de Fu: F(phi, omega)."""
    return 1.0 + phi - (1.0 + phi**omega) ** (1.0 / omega)


def q_fu(p_mm: float, eto_mm: float, omega: float) -> float:
    """Q anual modelado (mm/año) a partir de Q=P[1-F(ETo/P,omega)]."""
    if p_mm <= 0 or eto_mm < 0 or omega <= 1:
        raise ValueError("Estado Fu fuera del dominio físico usado en este análisis.")
    return p_mm * (1.0 - fu(eto_mm / p_mm, omega))


def shapley_change(early: dict[str, float], late: dict[str, float]) -> dict[str, float]:
    """Atribuye ΔQ-Fu entre P, ETo y omega promediando las 6 permutaciones."""
    variables = ("P_mm_anio", "ETo_fao56_mm", "omega")
    totals = {name: 0.0 for name in variables}
    for order in itertools.permutations(variables):
        state = early.copy()
        q_before = q_fu(state["P_mm_anio"], state["ETo_fao56_mm"], state["omega"])
        for name in order:
            state[name] = late[name]
            q_after = q_fu(state["P_mm_anio"], state["ETo_fao56_mm"], state["omega"])
            totals[name] += q_after - q_before
            q_before = q_after
    return {name: value / 6.0 for name, value in totals.items()}


def main() -> None:
    annual = pd.read_csv(ANNUAL)
    valid = annual.loc[annual["q_complete"].astype(bool) & annual["all_12_months_eto"].astype(bool)].copy()
    valid = valid.sort_values("anio_hidrologico")
    if len(valid) != 20 or valid["anio_hidrologico"].min() != 2002 or valid["anio_hidrologico"].max() != 2022:
        raise ValueError("La base común esperada de 20 observaciones completas (2002–2022) no coincide.")

    fu_table = pd.read_csv(FU)
    row = fu_table.loc[(fu_table["precipitation"] == "PL") & (fu_table["selection"] == "all_common_complete")]
    if len(row) != 1:
        raise ValueError("No se encontró un único omega Fu conjunto para PL.")
    omega = float(row.iloc[0]["omega"])

    # Subperiodos definidos por las diez primeras y últimas observaciones completas.
    early_data, late_data = valid.head(10).copy(), valid.tail(10).copy()
    summaries = []
    states: dict[str, dict[str, float]] = {}
    for label, data in (("Temprano", early_data), ("Tardío", late_data)):
        p = float(data["PL_mm_anio"].mean())
        eto = float(data["ETo_fao56_mm"].mean())
        qobs = float(data["Q_mm_anio"].mean())
        state = {"P_mm_anio": p, "ETo_fao56_mm": eto, "omega": omega}
        states[label] = state
        summaries.append({
            "subperiodo": label,
            "definicion": "10 primeras observaciones completas" if label == "Temprano" else "10 últimas observaciones completas",
            "anios_incluidos": ", ".join(map(str, data["anio_hidrologico"].astype(int).tolist())),
            "n_anios": len(data),
            "PISCOp_PL_mm_anio": p,
            "ETo_FAO56_mm_anio": eto,
            "Q_observado_mm_anio": qobs,
            "omega_Fu_constante": omega,
            "phi_ETo_sobre_P": eto / p,
            "Q_Fu_mm_anio": q_fu(p, eto, omega),
        })
    periods = pd.DataFrame(summaries)
    periods.to_csv(OUT_TAB / "tabla_subperiodos_budyko_fu.csv", index=False, encoding="utf-8")

    contributions = shapley_change(states["Temprano"], states["Tardío"])
    q_early = q_fu(**{"p_mm": states["Temprano"]["P_mm_anio"], "eto_mm": states["Temprano"]["ETo_fao56_mm"], "omega": omega})
    q_late = q_fu(**{"p_mm": states["Tardío"]["P_mm_anio"], "eto_mm": states["Tardío"]["ETo_fao56_mm"], "omega": omega})
    delta_fu = q_late - q_early
    qobs_early = float(periods.loc[periods.subperiodo == "Temprano", "Q_observado_mm_anio"].iloc[0])
    qobs_late = float(periods.loc[periods.subperiodo == "Tardío", "Q_observado_mm_anio"].iloc[0])
    delta_obs = qobs_late - qobs_early
    residue = delta_obs - delta_fu

    labels = {"P_mm_anio": "Precipitación P (PISCOp)", "ETo_fao56_mm": "Demanda ETo FAO-56", "omega": "Parámetro omega"}
    changes = {"P_mm_anio": states["Tardío"]["P_mm_anio"] - states["Temprano"]["P_mm_anio"], "ETo_fao56_mm": states["Tardío"]["ETo_fao56_mm"] - states["Temprano"]["ETo_fao56_mm"], "omega": 0.0}
    table_contrib = pd.DataFrame([
        {"factor": labels[key], "cambio_factor": changes[key], "unidad_factor": "mm/año" if key != "omega" else "adimensional", "contribucion_DeltaQ_mm_anio": contributions[key], "metodo": "Shapley contrafactual Fu (6 permutaciones)"}
        for key in ("P_mm_anio", "ETo_fao56_mm", "omega")
    ])
    table_contrib.loc[len(table_contrib)] = {"factor": "Total reconstruido por Fu", "cambio_factor": np.nan, "unidad_factor": "mm/año", "contribucion_DeltaQ_mm_anio": delta_fu, "metodo": "Suma exacta de contribuciones"}
    table_contrib.to_csv(OUT_TAB / "tabla_contribuciones_budyko_fu.csv", index=False, encoding="utf-8")

    comparison = pd.DataFrame([{
        "Q_observado_temprano_mm_anio": qobs_early,
        "Q_observado_tardio_mm_anio": qobs_late,
        "DeltaQ_observado_mm_anio": delta_obs,
        "Q_Fu_temprano_mm_anio": q_early,
        "Q_Fu_tardio_mm_anio": q_late,
        "DeltaQ_reconstruido_Fu_mm_anio": delta_fu,
        "residuo_observado_menos_Fu_mm_anio": residue,
        "omega_constante": omega,
        "interpretacion_residuo": "No atribuido: puede reflejar estructura de cuenca, almacenamiento, regulación, trasvases, incertidumbre o límites del modelo.",
    }])
    comparison.to_csv(OUT_TAB / "tabla_comparacion_Q_observado_budyko_fu.csv", index=False, encoding="utf-8")

    series = valid[["anio_hidrologico", "PL_mm_anio", "Q_mm_anio", "ETo_fao56_mm"]].copy()
    series["subperiodo"] = np.where(series.index.isin(early_data.index), "Temprano", "Tardío")
    series["omega_constante"] = omega
    series["Q_Fu_mm_anio"] = [q_fu(p, e, omega) for p, e in zip(series.PL_mm_anio, series.ETo_fao56_mm)]
    series.to_csv(OUT_DATA / "serie_anual_entrada_budyko_fu.csv", index=False, encoding="utf-8")

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    x = np.arange(3)
    vals = table_contrib.iloc[:3]["contribucion_DeltaQ_mm_anio"].to_numpy()
    colors = ["#3979ab" if v >= 0 else "#bf4e4e" for v in vals]
    axes[0].bar(x, vals, color=colors)
    axes[0].axhline(0, color="black", linewidth=.8)
    axes[0].set(xticks=x, xticklabels=["P", "ETo", "omega"], ylabel="Contribución a ΔQ (mm/año)", title="Descomposición Shapley - Budyko-Fu")
    axes[0].bar_label(axes[0].containers[0], fmt="%.2f", padding=3, fontsize=9)
    names = ["ΔQ observado", "ΔQ Fu", "Residuo"]
    vals2 = [delta_obs, delta_fu, residue]
    axes[1].bar(names, vals2, color=["#555555", "#3979ab", "#c7832b"])
    axes[1].axhline(0, color="black", linewidth=.8)
    axes[1].set(ylabel="mm/año", title="Cierre de la descomposición")
    axes[1].tick_params(axis="x", rotation=15)
    for bar in axes[1].containers[0]:
        axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height(), f"{bar.get_height():.2f}", ha="center", va="bottom" if bar.get_height() >= 0 else "top", fontsize=9)
    fig.suptitle("Racarumi (PE_200907): bloques hidrológicos completos", y=1.02)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(OUT_FIG / f"bonificacion_budyko_fu_descomposicion.{ext}", dpi=220, bbox_inches="tight")
    plt.close(fig)

    t1 = pd.read_csv(T1_TRENDS, decimal=",")
    t1q = t1.loc[(t1["group"] == "Caudal") & (t1["period_type"] == "Período común")].copy()
    t1q.to_csv(OUT_ANN / "referencia_tarea1_tendencias_caudal_periodo_comun.csv", index=False, encoding="utf-8")
    narrative = f"""# Bonificación 1.4 - descomposición Budyko-Fu

## Resultado reproducible

Se usaron las 20 observaciones completas comunes de año hidrológico (septiembre-agosto), divididas en las diez primeras ({', '.join(map(str, early_data.anio_hidrologico.astype(int)))}) y las diez últimas ({', '.join(map(str, late_data.anio_hidrologico.astype(int)))}). La ausencia de Q en 2003 se conserva: no se imputó.

La precipitación principal es PL/PISCOp, el caudal es CAMELS-PE y la demanda es ETo FAO-56. Se fijó omega={omega:.6f}, tomado del ajuste Fu conjunto PL de 1.3; por ello su contribución temporal es exactamente 0. La formulación es Q=P[1-F(ETo/P,omega)] y la partición Shapley promedia las seis permutaciones, por lo que incorpora las interacciones P-ETo sin dejar término de interacción separado.

El cambio observado es {delta_obs:.3f} mm/año y el cambio reconstruido por Fu es {delta_fu:.3f} mm/año. Las contribuciones son P={contributions['P_mm_anio']:.3f}, ETo={contributions['ETo_fao56_mm']:.3f} y omega={contributions['omega']:.3f} mm/año; el residuo observado menos Fu es {residue:.3f} mm/año.

## Alcance y límites

El resultado es exploratorio, no una atribución causal cerrada. El ajuste usa P-Q como diagnóstico previo de 1.3; no demuestra ΔS anual despreciable ni cuantifica regulación, trasvases o cambios de cobertura. El caudal no está documentado como naturalizado. ETo FAO-56 tiene la cobertura espacial documentada de 90.1264 %. El residuo no se asigna a una causa única.

La referencia de Tarea 1 para el período común reporta tendencia mensual de caudal no significativa; por tanto, su lectura debe separarse del contraste de medias entre bloques y no valida causalmente la descomposición.
"""
    (OUT_ANN / "interpretacion_bonificacion_budyko_fu.md").write_text(narrative, encoding="utf-8")
    audit = {"n_complete_common_years": int(len(valid)), "omega_source": str(FU.relative_to(PROJECT)), "omega_constant": omega, "periods": periods.to_dict(orient="records"), "delta_q_observed_mm_year": delta_obs, "delta_q_fu_mm_year": delta_fu, "residual_mm_year": residue, "contribution_sum_minus_delta_fu": float(table_contrib.iloc[:3]["contribucion_DeltaQ_mm_anio"].sum() - delta_fu)}
    (OUT_ANN / "auditoria_reproducibilidad_budyko_fu.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
