from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'datos'/'punto2'/'Abtsgmuend_Untergroeningen'/'bonificacion_2_5_pot'
df=pd.read_csv(BASE/'pot_vs_gev_1h.csv')
fig,ax=plt.subplots(figsize=(7,4.2))
for p,g in df.groupby('threshold_percentile'):
    ax.plot(g.T_years,g.pot_mm_1h,'o-',label=f'POT P{int(p*100)}')
g=df[df.threshold_percentile==.95]
ax.plot(g.T_years,g.gev_mle_mm_1h,'k--',label='GEV-MLE')
ax.set_xscale('log'); ax.set_xlabel('Periodo de retorno T (años)'); ax.set_ylabel('Lluvia 1 h (mm)'); ax.grid(alpha=.25); ax.legend(); ax.set_title('Sensibilidad POT y comparación con GEV-MLE')
fig.tight_layout(); fig.savefig(BASE/'pot_sensibilidad_vs_gev.png',dpi=180); plt.close(fig)
