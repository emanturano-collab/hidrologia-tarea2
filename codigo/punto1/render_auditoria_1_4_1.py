"""Renderiza la figura de consulta desde la tabla ya auditada, sin recalcular tendencias."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
TABLE = ROOT / 'productos/punto1/1_4_cambios_demanda_evaporativa/tablas/1_4_1_tendencias_estacionales_mensuales.csv'
OUT = ROOT / 'productos/punto1/1_4_cambios_demanda_evaporativa/figuras'

data = pd.read_csv(TABLE)
fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
for ax, label, color in zip(axes, ['ETo FAO-56', 'Thornthwaite'], ['#1f77b4', '#ff7f0e']):
    z = data.loc[data['variable'].eq(label)].sort_values('month_number').reset_index(drop=True)
    x = z['month_number'].to_numpy()
    y = z['sen_slope_mm_month_per_year'].to_numpy()
    sig = z['significant_fdr_0_05'].astype(str).str.lower().eq('true').to_numpy()
    ax.axhline(0, color='black', linewidth=.8)
    ax.plot(x, y, color=color, marker='o', linewidth=2, label='Pendiente de Sen')
    ax.scatter(x[sig], y[sig], marker='*', color='black', s=120, label='FDR y TFPW p ≤ 0.05', zorder=3)
    ax.set_title(label); ax.set_ylabel('Sen (mm/mes por año)'); ax.legend(loc='best', frameon=False)
axes[-1].set_xticks(range(1, 13), ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'])
axes[-1].set_xlabel('Mes calendario')
fig.suptitle('Racarumi: tendencias mensuales, 1981-2022')
fig.tight_layout()
fig.savefig(OUT / '1_4_1_tendencias_estacionales_fdr_tfpw.png', dpi=180)
fig.savefig(OUT / '1_4_1_tendencias_estacionales_fdr_tfpw.pdf')
