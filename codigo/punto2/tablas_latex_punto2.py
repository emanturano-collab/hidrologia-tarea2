"""Convierte las tablas finales del punto 2 en fragmentos LaTeX para el informe.

Lee productos/punto2/final/tablas/*.csv (generadas por analisis_final_punto2.py) y
escribe productos/punto2/final/tablas_tex/*.tex.

Ejecucion: python codigo/punto2/tablas_latex_punto2.py
"""
from pathlib import Path
import json

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
TAB = ROOT / "productos" / "punto2" / "final" / "tablas"
OUT = ROOT / "productos" / "punto2" / "final" / "tablas_tex"
OUT.mkdir(parents=True, exist_ok=True)
R = json.loads((ROOT / "productos" / "punto2" / "final" / "resultados_punto2.json").read_text(encoding="utf-8"))
DIS = R["distribucion_diseno"]


def n(v, nd):
    return f"{v:.{nd}f}".replace(".", "{,}")


NOMBRES = {"gev_gmle": "GEV-GMLE", "gev_mle": "GEV-MV", "gev_lmom": "GEV-LM", "gumbel_mle": "Gumbel-MV",
           "gumbel_lmom": "Gumbel-LM", "lp3_mom": "LP3-Mom"}

# Cuantiles de 10 min y 1 h por modelo (2.2.3)
q = pd.read_csv(TAB / "cuantiles_todas_duraciones.csv")
gof = pd.read_csv(TAB / "bondad_ajuste.csv")
rows = []
for d in ("10min", "1h"):
    for m in NOMBRES:
        s = q[(q.duracion == d) & (q.modelo == m)].set_index("T")["profundidad_mm"]
        g = gof[(gof.duracion == d) & (gof.modelo == m)].iloc[0]
        rows.append(f"{d.replace('min', ' min').replace('1h', '1 h')} & {NOMBRES[m]} & "
                    + " & ".join(n(s[T], 1) for T in (2, 5, 10, 25, 50, 100))
                    + f" & {n(g.KS_p, 2)} & {n(g.CvM_p, 2)} & {n(g.PPCC, 3)} \\\\")
(OUT / "cuantiles.tex").write_text("\n".join(rows) + "\n", encoding="utf-8")

# Riesgo por diametro (2.4.A.6)
rd = pd.read_csv(TAB / "riesgo_por_diametro_2_4A.csv")
(OUT / "riesgo_diametro.tex").write_text("\n".join(
    f"{n(r.D_m, 2)} & {n(r.Qc_m3s, 2)} & {n(r.FS, 2)} & {n(100 * r.p_anual_efectiva, 2)} & {n(r.T_efectivo, 0)} & {n(100 * r.riesgo_vida_efectivo, 1)} \\\\"
    for r in rd.itertuples()) + "\n", encoding="utf-8")

FUENTES = {"tc": "$t_c$", "Distribucion": "Distribución", "Evento 2013": "Evento 2013"}


def esc(e):
    for k, v in NOMBRES.items():
        e = e.replace(k, v)
    return (e.replace("Distribucion de diseno sin 2013 (IDF escalada)", "Sin el evento de 2013")
             .replace("tc ", "").replace("IC95", "IC 95 %")
             .replace("%", "\\%").replace("x0.8", "$\\times$0,8").replace("x1.2", "$\\times$1,2")
             .replace("0.", "0,").replace("1.", "1,").replace("2.", "2,").replace("4.", "4,"))


# Sensibilidad del diametro (2.4.A.5)
se = pd.read_csv(TAB / "sensibilidad_2_4A.csv")
(OUT / "sensibilidad.tex").write_text("\n".join(
    f"{FUENTES.get(r.fuente, r.fuente)} & {esc(r.escenario)} & {n(r.Qp_m3s, 3)} & {n(r.D_calculado_m, 2)} & {n(r.D_comercial_m, 2)} \\\\"
    for r in se.itertuples()) + "\n", encoding="utf-8")

# Tanque (2.4.B)
tb = pd.read_csv(TAB / "tanque_escenarios_2_4B.csv")
tb = tb[(tb.metodo != "trapezoidal") | (tb.Q_entrada_max_m3s > R["tanque"]["Qpre_m3s"])]
(OUT / "tanque.tex").write_text("\n".join(
    f"{'Trapezoidal' if r.metodo == 'trapezoidal' else 'Bloques alternos'} & {r.escenario.replace('d=', 'd = ')} & {n(r.Q_entrada_max_m3s, 2)} & {n(r.volumen_entrada_m3, 0)} & {n(r.volumen_requerido_m3, 0)} \\\\"
    for r in tb.itertuples()) + "\n", encoding="utf-8")

# KOSTRA (2.3.3)
k = pd.read_csv(TAB / "comparacion_kostra_uc.csv")
k = k[k["T"].isin([2, 10, 100])]
(OUT / "kostra.tex").write_text("\n".join(
    f"{r.duracion.replace('min', ' min').replace('h', ' h')} & {r.T} & {n(r.kostra_mm, 1)} $\\pm$ {r.kostra_UC_pct:.0f}\\,\\% & {n(r.local_mm, 1)} & {n(r.razon_local_kostra, 2)} & {n(r.local_sin2013_mm, 1)} \\\\"
    for r in k.itertuples()) + "\n", encoding="utf-8")
print(sorted(p.name for p in OUT.glob("*.tex")))
