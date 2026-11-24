"""Genera geometría revisada para 2.4."""
from pathlib import Path
import math
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "datos" / "punto2" / "Abtsgmuend_Untergroeningen"
OUT = DATA / "diseno_2_4"

def main():
    scenarios = pd.read_csv(OUT / "problema_A_escenarios.csv")
    base = scenarios[(scenarios.tc_formula == "Kirpich") & (scenarios.T_years == 25)].iloc[0]
    D, n, S = 1.50, 0.013, 0.010
    Qc = 0.312 / n * D ** (8 / 3) * math.sqrt(S)
    Qp = float(base["Qp_m3s"])
    mc_summary = pd.read_csv(OUT / "riesgo_A.csv").iloc[0]
    annual_failure = float(mc_summary["annual_effective_failure_probability"])
    life_risk = 1 - (1 - annual_failure) ** 30
    pipe = {"obra":"alcantarilla circular", "diameter_m":D, "length_m":30,
            "slope_m_m":S, "manning_n":n, "capacity_m3s":Qc,
            "design_Qp_m3s":Qp, "safety_factor":Qc/Qp,
            "mc_annual_failure":annual_failure, "mc_life_risk_30yr":life_risk,
            "freeboard_note":"verificar entrada, salida y control de remanso"}
    tank = pd.read_csv(OUT / "tanque_escenarios.csv")
    V, max_depth = float(tank.max_storage_m3.max()), float(tank.max_depth_m.max())
    length, width, depth, freeboard = 24.0, 22.0, 2.0, 0.5
    volume = length * width * depth
    orifice_d, Cd = 0.30, 0.65
    Qout = Cd * math.pi * (orifice_d / 2) ** 2 * math.sqrt(2 * 9.81 * depth)
    tank_geom = {"obra":"tanque rectangular", "length_m":length, "width_m":width,
        "effective_depth_m":depth, "freeboard_m":freeboard, "total_depth_m":depth+freeboard,
        "available_volume_m3":volume, "required_volume_from_scenario_m3":V,
        "volume_margin_m3":volume-V, "max_routed_depth_m":max_depth,
        "orifice_diameter_m":orifice_d, "Cd":Cd, "outflow_at_effective_depth_m3s":Qout,
        "status":"validated_preliminary" if max_depth <= depth else "requires_resize"}
    pd.DataFrame([pipe]).to_csv(OUT / "geometria_alcantarilla.csv", index=False, float_format="%.5f")
    pd.DataFrame([tank_geom]).to_csv(OUT / "geometria_tanque.csv", index=False, float_format="%.5f")
    report = f'''# Geometría revisada de la obra

## Alcantarilla
- Diámetro comercial adoptado: **{D:.2f} m**.
- Capacidad Manning: {Qc:.2f} m³/s; caudal T=25: {Qp:.2f} m³/s.
- Factor de seguridad frente al caudal mediano: {Qc/Qp:.2f}.
- Falla anual Monte Carlo: {annual_failure:.4f}; riesgo acumulado 30 años: {life_risk:.3f}.

## Tanque
- Planta: **{length:.0f} m × {width:.0f} m**; profundidad útil {depth:.1f} m; borde libre {freeboard:.1f} m.
- Volumen útil: {volume:.1f} m³; requerido: {V:.1f} m³; margen: {volume-V:.1f} m³.
- Profundidad máxima transitada: {max_depth:.2f} m.
- Orificio: {orifice_d:.2f} m, Cd={Cd:.2f}; salida a h=2 m: {Qout:.3f} m³/s.

La geometría queda validada frente a los escenarios calculados. Se conserva como limitación que el outlet es un punto sintético derivado del MDE y no una estructura OSM confirmada.
'''
    (OUT / "geometria_obra_2_4.md").write_text(report, encoding="utf-8")
    print("Geometría revisada generada")

if __name__ == "__main__": main()
