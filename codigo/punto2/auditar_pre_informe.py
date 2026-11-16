"""Auditoría de consistencia previa al informe de entrega."""
from pathlib import Path
import json
import pandas as pd
import py_compile

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "datos" / "punto2" / "Abtsgmuend_Untergroeningen"
OUT = ROOT / "productos" / "punto2"

def check(name, ok, detail):
    return {"check": name, "status": "OK" if ok else "REVISAR", "detail": detail}

def main():
    rows = []
    cuenca = pd.read_csv(BASE / "cuenca_preparada" / "cuenca_resumen.csv").set_index("campo")
    area = float(cuenca.loc["area_km2", "valor"])
    poly = json.loads((BASE / "cuenca_preparada" / "microcuenca_abtsgmuend.geojson").read_text(encoding="utf-8"))
    prop_area = float(poly["features"][0]["properties"]["area_km2"])
    rows.append(check("Área polígono–resumen", abs(area-prop_area) < 1e-5, f"{area:.9f} vs {prop_area:.9f} km² (resumen redondeado)"))

    pts = json.loads((BASE / "cuenca_preparada" / "puntos_control.geojson").read_text(encoding="utf-8"))["features"]
    outlet = next(x for x in pts if x["properties"]["tipo"] == "salida")["geometry"]["coordinates"]
    line = json.loads((BASE / "cuenca_preparada" / "cauce_principal.geojson").read_text(encoding="utf-8"))["features"][0]["geometry"]["coordinates"]
    end = line[-1]
    rows.append(check("Outlet–extremo cauce DEM", max(abs(outlet[0]-end[0]), abs(outlet[1]-end[1])) < 1e-8, f"outlet={outlet}, extremo={end}"))

    ga = pd.read_csv(BASE / "diseno_2_4" / "geometria_alcantarilla.csv").iloc[0]
    rows.append(check("Diámetro final", abs(float(ga.diameter_m)-1.50) < 1e-9, f"D={ga.diameter_m:.2f} m"))
    rows.append(check("Capacidad > caudal mediano", float(ga.capacity_m3s) > float(ga.design_Qp_m3s), f"Qc={ga.capacity_m3s:.2f}, Qp={ga.design_Qp_m3s:.2f} m³/s"))
    rows.append(check("Riesgo reportado", 0 <= float(ga.mc_life_risk_30yr) <= 1, f"riesgo 30 años={ga.mc_life_risk_30yr:.3f}"))

    gt = pd.read_csv(BASE / "diseno_2_4" / "geometria_tanque.csv").iloc[0]
    rows.append(check("Volumen tanque > requerido", float(gt.available_volume_m3) >= float(gt.required_volume_from_scenario_m3), f"{gt.available_volume_m3:.2f} vs {gt.required_volume_from_scenario_m3:.2f} m³"))
    rows.append(check("Profundidad bajo útil", float(gt.max_routed_depth_m) <= float(gt.effective_depth_m), f"{gt.max_routed_depth_m:.2f} vs {gt.effective_depth_m:.2f} m"))

    pot = BASE / "bonificacion_2_5_pot"
    rows.append(check("POT sensibilidad", (pot/"pot_threshold_sensitivity.csv").exists() and (pot/"pot_vs_gev_1h.csv").exists(), "archivos de sensibilidad presentes"))
    rows.append(check("2.2–2.3 resultados", (BASE/"extremos_2_2"/"bootstrap_ci_gev.csv").exists() and (BASE/"idf_2_3"/"idf_kostra_comparison.csv").exists(), "bootstrap e IDF–KOSTRA presentes"))

    scripts = ["finalizar_2_4.py", "geometria_obra_2_4.py", "bonificacion_pot_2_5.py", "sensibilidad_pot_2_5.py"]
    compile_ok = True
    for s in scripts:
        try: py_compile.compile(str(ROOT/"codigo"/"punto2"/s), doraise=True)
        except Exception: compile_ok = False
    rows.append(check("Compilación scripts principales", compile_ok, ", ".join(scripts)))

    df = pd.DataFrame(rows)
    df.to_csv(OUT/"auditoria_pre_informe.csv", index=False)
    md = ["# Resultado de auditoría previa al informe", "", f"Checks OK: {(df.status=='OK').sum()}/{len(df)}", ""]
    md.append(df.to_string(index=False))
    (OUT/"auditoria_pre_informe_resultado.md").write_text("\n".join(md), encoding="utf-8")
    print(df.to_string(index=False))

if __name__ == "__main__": main()
