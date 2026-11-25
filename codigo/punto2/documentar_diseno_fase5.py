"""Completa escala, sensibilidad, tránsito y esquemas de 2.4."""
from pathlib import Path
import math
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "datos" / "punto2" / "Abtsgmuend_Untergroeningen"
OUT = DATA / "diseno_2_4"

def main():
    summ = pd.read_csv(DATA/'cuenca_preparada'/'cuenca_resumen.csv').set_index('campo')
    A0=float(summ.loc['area_km2','valor']); L0=float(summ.loc['main_channel_length_m','valor']); S=float(summ.loc['main_channel_slope_m_m','valor']); C=float(pd.read_csv(DATA/'cobertura_2_4'/'weighted_runoff_coefficient.csv').weighted_C.iloc[0])
    idf=pd.read_csv(DATA/'idf_2_3'/'idf_powerlaw_parameters.csv'); p=idf.query('T_years==25').iloc[0]
    rows=[]
    # Illustration of scale: preserve terrain similarity with L~sqrt(A), and show why FRA matters.
    for label,A,FRA in [('microcuenca',A0,1.00),('10 km2',10.0,.85),('100 km2',100.0,.60),('cuenca_punto1',2363.302,.20)]:
        L=L0*math.sqrt(A/A0); tc=.0195*L**.77*S**(-.385); inten=p.a*(tc/60)**(-p.eta); qp=C*inten*A*FRA/3.6
        rows.append({'scale':label,'area_km2':A,'FRA_illustrative':FRA,'length_proxy_m':L,'tc_kirchich_min':tc,'intensity_T25_mm_h':inten,'rational_Q_with_FRA_m3s':qp,'rational_assumption_warning': 'valid_small_area' if A<=5 else 'not_accepted_as_design'})
    pd.DataFrame(rows).to_csv(OUT/'escala_metodo_racional.csv',index=False,float_format='%.5f')
    (OUT/'escala_metodo_racional.md').write_text('''# Escala y validez del método racional\n\nEl método racional se acepta aquí para la microcuenca de 0.123154 km². La tabla `escala_metodo_racional.csv` muestra una comparación numérica al aumentar el área, usando una longitud proxy proporcional a la raíz del área y FRA ilustrativos decrecientes.\n\nPara 10 y 100 km² la hipótesis de lluvia uniforme y un único tiempo de concentración ya es débil. Para la cuenca del punto 1 (2363.302 km²) el método racional **no se usa como diseño**: un único pluviómetro no representa la variabilidad espacial, la duración crítica deja de ser local y el FRA domina el resultado. Los valores de esas filas son demostrativos, no recomendaciones hidráulicas.\n''',encoding='utf-8')

    sens=pd.read_csv(OUT/'sensibilidad_A.csv'); rows=[]
    for col in ['C','n','S_pipe']:
        g=sens.groupby(col).D_commercial_m.agg(['min','max','mean']).reset_index(); g['parameter']=col; g.rename(columns={col:'value'},inplace=True); rows.append(g[['parameter','value','min','max','mean']])
    out=pd.concat(rows,ignore_index=True); out.to_csv(OUT/'sensibilidad_resumen.csv',index=False,float_format='%.5f')
    (OUT/'sensibilidad_2_4.md').write_text('''# Sensibilidad consolidada de 2.4A\n\nSe variaron C ±20 %, Manning n = 0.011/0.013/0.017 y pendiente de tubería S = 0.0075/0.010/0.015. `sensibilidad_A.csv` conserva las 27 combinaciones; `sensibilidad_resumen.csv` resume el diámetro comercial mínimo, máximo y medio por parámetro. También se compararon los tres tiempos de concentración en `problema_A_escenarios.csv`.\n\nEl diámetro aumenta con C y n, y disminuye con la pendiente construida. La fuente dominante se identifica por el rango de diámetro, no por el número de figuras.\n''',encoding='utf-8')

    (OUT/'ley_salida_y_transito_2_4b.md').write_text('''# Ley de salida y tránsito del tanque (2.4B)\n\nEl tanque rectangular tiene planta 24 × 22 m (área 528 m²), profundidad útil 2.0 m y borde libre 0.5 m. Se usa piscina nivelada con\n\n`dS/dt = I(t) - O(h)`\n\n`S(h) = 528 h` y salida por orificio `O(h) = Cd Ao sqrt(2 g h)`, con `Cd=0.65`, diámetro del orificio 0.30 m y `Ao=πd²/4=0.07069 m²`. La integración usa pasos de 10 minutos, condición inicial S=0 y `h=S/528`.\n\nSe evaluaron duraciones de 30, 60 y 90 minutos y el pico al inicio, centro y final. El caso crítico es 60 min con pico final: 1014.75 m³, 1.92 m, margen 41.25 m³. La salida a h=2 m es 0.288 m³/s.\n''',encoding='utf-8')

    fig, ax = plt.subplots(figsize=(8,4)); ax.add_patch(Rectangle((1,1),6,2,fill=False,lw=2)); ax.add_patch(Rectangle((2.7,1.0),1.0,1.2,color='#9ecae1',alpha=.8)); ax.add_patch(FancyArrowPatch((3.2,3.6),(3.2,3.0),arrowstyle='-|>',mutation_scale=15,lw=2)); ax.add_patch(FancyArrowPatch((3.2,1.0),(3.2,.2),arrowstyle='-|>',mutation_scale=15,lw=2)); ax.text(3.35,3.45,'I(t)'); ax.text(3.35,.35,'O(h)'); ax.text(4.2,2.1,'S(h)=528h'); ax.text(1.1,3.2,'24 m × 22 m'); ax.set_xlim(0,8); ax.set_ylim(0,4); ax.axis('off'); fig.tight_layout(); fig.savefig(OUT/'esquema_tanque_2_4b.png',dpi=180); plt.close(fig)
    fig, ax = plt.subplots(figsize=(8,3)); ax.plot([0,1,2,3],[0,1,1,0],lw=8,color='#8c96a0'); ax.arrow(0.2,1.5,1.2,0,head_width=.12,head_length=.2,color='#2166ac'); ax.text(.1,2.0,'Qp = C i A / 3.6'); ax.text(1.35,.35,'D = 1.50 m'); ax.text(2.0,1.45,'S₀ = 0.010'); ax.set_xlim(0,3.4); ax.set_ylim(0,2.4); ax.axis('off'); fig.tight_layout(); fig.savefig(OUT/'esquema_alcantarilla_2_4a.png',dpi=180); plt.close(fig)
    print(out.to_string(index=False)); print(rows)

if __name__ == '__main__': main()
