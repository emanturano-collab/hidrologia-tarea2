from pathlib import Path
import numpy as np, pandas as pd
from statistics import NormalDist
import matplotlib.pyplot as plt

ROOT=next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
DAILY=ROOT/'datos/punto1/procesados/1_1_a_fao56_preliminar_90pct/fao56_eto_diaria_preliminar_90pct.csv'
MASTER=ROOT/'datos/punto1/procesados/1_1_c_metodos_alternativos/1_1c_tabla_maestra_mensual_preliminar_90pct.csv'
OUT=ROOT/'datos/punto1/procesados/1_4_cambios_demanda_evaporativa'; TAB=ROOT/'productos/punto1/1_4_cambios_demanda_evaporativa/tablas'; FIG=ROOT/'productos/punto1/1_4_cambios_demanda_evaporativa/figuras'; ANN=ROOT/'anexos/punto1/1_4_cambios_demanda_evaporativa'
def trend(y):
 x=np.arange(len(y)); slopes=np.array([(y[j]-y[i])/(j-i) for i in range(len(y)) for j in range(i+1,len(y))]); s=float(np.median(slopes)); lo,hi=np.quantile(slopes,[.025,.975]); S=float(np.sign(slopes).sum()); n=len(y); var=n*(n-1)*(2*n+5)/18; z=(S-np.sign(S))/np.sqrt(var) if S else 0.; p=2*(1-NormalDist().cdf(abs(z))); return dict(sen_per_year=s,sen_ci_low=float(lo),sen_ci_high=float(hi),mk_tau=S/(n*(n-1)/2),mk_p=p,ols_slope=float(np.polyfit(x,y,1)[0]),lag1=pd.Series(y).autocorr(1))
def main():
 for p in (OUT,TAB,FIG,ANN):p.mkdir(parents=True,exist_ok=True)
 d=pd.read_csv(DAILY,parse_dates=['date']); d=d[(d.date.dt.year>=1981)&(d.date.dt.year<=2022)]
 counts=d.groupby(d.date.dt.year).size(); assert d.date.dt.year.nunique()==42 and counts.isin([365,366]).all()
 a=d.set_index('date').resample('YS').agg(eto=('eto_fao56_mm_d','sum'),T=('tmean_c','mean'),ea=('ea_kpa','mean'),u2=('u2_ms','mean'),Rs=('rs_mj_m2_d','mean')).reset_index();a['year']=a.date.dt.year
 m=pd.read_csv(MASTER,parse_dates=['date']); m=m[(m.date.dt.year>=1981)&(m.date.dt.year<=2022)]; th=[c for c in m if 'thorn' in c.lower()][0]; tm=m.set_index('date').resample('YS')[th].sum().reset_index(name='thornthwaite');a=a.merge(tm,on='date')
 rows=[]
 for c in ['eto','thornthwaite','T','ea','u2','Rs']: rows.append({'variable':c}|trend(a[c].to_numpy()))
 tr=pd.DataFrame(rows);tr.to_csv(TAB/'1_4_1_tendencias_anuales.csv',index=False)
 base=a[['T','ea','u2','Rs']].mean(); eps={'T':.01,'ea':.001,'u2':.01,'Rs':.01}; contrib=[]
 def f(z):
  q=d.copy();
  for k in z:q[k.lower()+'_x']=z[k]
  # first-order sensitivity on observed daily FAO-56 formula unavailable without recomputing components; use annual perturbation of documented ETo response
  return None
 # Contributions intentionally left as diagnostic pending full daily component model.
 pd.DataFrame({'status':['No calculado: se requiere modelo diario FAO-56 con forzantes independientes para atribucion sin doble conteo.']}).to_csv(TAB/'1_4_2_estado_atribucion.csv',index=False)
 fig,ax=plt.subplots(figsize=(9,4));ax.plot(a.year,a.eto,label='FAO-56');ax.plot(a.year,a.thornthwaite,label='Thornthwaite');ax.set(xlabel='Año',ylabel='mm/año',title='Racarumi: demanda evaporativa anual (1981-2022)');ax.legend();fig.tight_layout();fig.savefig(FIG/'1_4_1_tendencias_eto_thornthwaite.png',dpi=180);fig.savefig(FIG/'1_4_1_tendencias_eto_thornthwaite.pdf');plt.close(fig)
 a.to_csv(OUT/'1_4_series_anuales_1981_2022.csv',index=False)
 (ANN/'estado_1_4.md').write_text('# Estado 1.4\n\nTendencias calculadas con años completos 1981-2022. La atribución requiere conservar o reconstruir el modelo diario completo de FAO-56; no se infirieron contribuciones.\n',encoding='utf8')
if __name__=='__main__':main()
