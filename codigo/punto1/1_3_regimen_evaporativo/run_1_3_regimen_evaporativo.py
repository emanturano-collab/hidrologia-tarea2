"""Reproducible diagnostics for section 1.3; intentionally preliminary."""
from pathlib import Path
import hashlib, json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT=next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
T1=ROOT/'datos'/'punto1'/'originales'/'tarea1_minimos'
INP=ROOT/'datos/punto1/originales/1_2_balance_hidrico'; OUT=ROOT/'datos/punto1/procesados/1_3_regimen_evaporativo'
TAB=ROOT/'productos/punto1/1_3_regimen_evaporativo/tablas'; FIG=ROOT/'productos/punto1/1_3_regimen_evaporativo/figuras'; ANN=ROOT/'anexos/punto1/1_3_regimen_evaporativo'
CSV=INP/'Racarumi_balance_anual_2001_2023.csv'; XLSX=T1/'Racarumi_balance_anual_2001_2023.xlsx'
MASTER=T1/'PE_200907_master_monthly.csv'
E1=ROOT/'datos/punto1/procesados/1_1_a_fao56_preliminar_90pct/fao56_eto_mensual_preliminar_90pct.csv'
ALT=ROOT/'datos/punto1/procesados/1_1_c_metodos_alternativos/1_1c_tabla_maestra_mensual_preliminar_90pct.csv'
for d in [OUT,TAB,FIG,ANN]: d.mkdir(parents=True,exist_ok=True)
for d in ['01_regimen_mensual','02_humedad_suelo','03_budyko','04_elasticidad','05_relacion_complementaria']:(ROOT/'codigo/punto1/1_3_regimen_evaporativo'/d).mkdir(parents=True,exist_ok=True)
def h(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def hy(d): return d.dt.year+(d.dt.month>=9).astype(int)
def fu(phi,w): return 1+phi-(1+phi**w)**(1/w)
def fit(phi,ei):
 if not(np.isfinite(phi) and np.isfinite(ei) and phi>0 and 0<=ei<=min(1,phi)): return (np.nan,np.nan)
 x=np.linspace(1.01,20,19000); y=fu(np.full(x.size,phi),x); i=np.abs(y-ei).argmin(); return float(x[i]),float(y[i]-ei)
def elast(d,p):
 pm,qm=d[p].mean(),d.Q_mm_anio.mean(); use=(d[p]-pm).abs()>=.01*pm
 v=(((d.loc[use,'Q_mm_anio']-qm)/(d.loc[use,p]-pm))*pm/qm).to_numpy(); e=float(np.median(v)); rng=np.random.default_rng(20261121)
 b=np.array([np.median(rng.choice(v,len(v),replace=True)) for _ in range(5000)])
 return e,int(use.sum()),float(np.quantile(b,.025)),float(np.quantile(b,.975))
# Inputs: preserve originals, validate CSV versus Excel and balances.
cols=['anio_hidrologico','PL_mm_anio','PI_mm_anio','Q_mm_anio','PL_menos_Q_mm_anio','PI_menos_Q_mm_anio']
p=pd.read_csv(CSV)[cols]; x=pd.read_excel(XLSX,sheet_name='Balance anual')[cols]
for c in cols: p[c]=pd.to_numeric(p[c],errors='coerce'); x[c]=pd.to_numeric(x[c],errors='coerce')
p['PL_Q_residual_mm']=p.PL_mm_anio-p.Q_mm_anio-p.PL_menos_Q_mm_anio; p['PI_Q_residual_mm']=p.PI_mm_anio-p.Q_mm_anio-p.PI_menos_Q_mm_anio
p['q_complete']=p.Q_mm_anio.notna(); p['negative_PI_minus_Q']=p.PI_menos_Q_mm_anio<0
qc={'csv_sha256':h(CSV),'xlsx_sha256':h(XLSX),'rows':len(p),'distinct_hydrological_years':int(p.anio_hidrologico.nunique()),'year_first':int(p.anio_hidrologico.min()),'year_last':int(p.anio_hidrologico.max()),'duplicate_years':int(p.anio_hidrologico.duplicated().sum()),'complete_Q_years':int(p.q_complete.sum()),'missing_Q_years':p.loc[~p.q_complete,'anio_hidrologico'].dropna().astype(int).tolist(),'csv_xlsx_max_abs_difference':float(p.subtract(x).abs().max().max()),'max_balance_residual_PL_minus_Q_mm':float(p.PL_Q_residual_mm.abs().max()),'max_balance_residual_PI_minus_Q_mm':float(p.PI_Q_residual_mm.abs().max()),'negative_PI_minus_Q_years':p.loc[p.negative_PI_minus_Q,'anio_hidrologico'].astype(int).tolist(),'provenance':'Información compartida por Pacho; digitalizada desde capturas, pendiente de contrastar con su archivo fuente.'}
(ANN/'control_calidad_fuentes_pacho_1_3.json').write_text(json.dumps(qc,ensure_ascii=False,indent=2),encoding='utf8'); p.to_csv(OUT/'1_3_balance_anual_pacho_validado_sin_modificar.csv',index=False)
# Monthly P and ETo on common dates.
m=pd.read_csv(MASTER,parse_dates=['date']); e=pd.read_csv(E1,parse_dates=['month'])
m=m.merge(e[['month','eto_from_daily_mm']],left_on='date',right_on='month',how='inner').rename(columns={'camels_precip_mm_month':'PL_mm_mes','imerg_precip_mm_month':'PI_mm_mes','eto_from_daily_mm':'ETo_mm_mes'})
m=m.loc[(m.date>='1981-01-01')&(m.date<='2023-08-01')].copy(); m['hydro_year']=hy(m.date);m['calendar_month']=m.date.dt.month
for a in ['PL','PI']:
 m[f'{a}_P_sobre_ETo']=m[f'{a}_mm_mes']/m.ETo_mm_mes;m[f'ETo_sobre_{a}_P']=m.ETo_mm_mes/m[f'{a}_mm_mes'];m[f'{a}_menos_ETo_mm']=m[f'{a}_mm_mes']-m.ETo_mm_mes
cl=m.groupby('calendar_month',as_index=False).agg(PL_mm_mes=('PL_mm_mes','mean'),PI_mm_mes=('PI_mm_mes','mean'),ETo_mm_mes=('ETo_mm_mes','mean'),n_months=('date','count'))
for a in ['PL','PI']: cl[f'{a}_P_sobre_ETo']=cl[f'{a}_mm_mes']/cl.ETo_mm_mes;cl[f'ETo_sobre_{a}_P']=cl.ETo_mm_mes/cl[f'{a}_mm_mes'];cl[f'{a}_menos_ETo_mm']=cl[f'{a}_mm_mes']-cl.ETo_mm_mes
cl['mes']=['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];m.to_csv(OUT/'1_3_serie_mensual_PL_PI_ETo_preliminar_90_1264pct.csv',index=False);cl.to_csv(TAB/'1_3_climatologia_mensual_PL_PI_ETo_preliminar_90_1264pct.csv',index=False)
# Explicit, non-destructive reconciliation with T1.
t=m.groupby('hydro_year',as_index=False).agg(PL_T1_mm=('PL_mm_mes','sum'),PI_T1_mm=('PI_mm_mes','sum'),Q_T1_mm=('runoff_mm_month','sum'),n_months=('date','count'))
ct=p.merge(t,left_on='anio_hidrologico',right_on='hydro_year',how='left');ct['PL_difference_pacho_minus_T1_mm']=ct.PL_mm_anio-ct.PL_T1_mm;ct['PI_difference_pacho_minus_T1_mm']=ct.PI_mm_anio-ct.PI_T1_mm;ct['Q_difference_pacho_minus_T1_mm']=ct.Q_mm_anio-ct.Q_T1_mm;ct.to_csv(TAB/'1_3_contraste_pacho_con_tarea1_mensual.csv',index=False)
# Hydrological annual series, Budyko diagnostic and elasticities.
a=pd.read_csv(ALT,parse_dates=['date']);a['hydro_year']=hy(a.date); ae=a.groupby('hydro_year',as_index=False).agg(ETo_fao56_mm=('fao56','sum'),Makkink_mm=('makkink_1957','sum'),Hargreaves_Samani_mm=('hargreaves_samani_1985','sum'),n_months=('date','count'))
y=p.merge(ae,left_on='anio_hidrologico',right_on='hydro_year',how='left'); y['all_12_months_eto']=y.n_months.eq(12); v=y.loc[y.q_complete&y.all_12_months_eto].copy()
rows=[]
for n in ['PL','PI']:
 y[f'phi_{n}']=y.ETo_fao56_mm/y[f'{n}_mm_anio'];y[f'ETexpl_{n}_mm']=y[f'{n}_menos_Q_mm_anio'];y[f'EIexpl_{n}']=y[f'ETexpl_{n}_mm']/y[f'{n}_mm_anio'];y[f'budyko_admissible_{n}']=y[f'EIexpl_{n}'].between(0,1)&(y[f'EIexpl_{n}']<=y[f'phi_{n}'])
 pm,qm,em=v[f'{n}_mm_anio'].mean(),v.Q_mm_anio.mean(),v.ETo_fao56_mm.mean(); phi,ei=em/pm,(pm-qm)/pm; om,res=fit(phi,ei); fp=1-phi**(om-1)*(1+phi**om)**(1/om-1) if np.isfinite(om) else np.nan; et=1+phi*fp/(1-fu(phi,om)) if np.isfinite(om) else np.nan; ep,nn,lo,hi=elast(v,f'{n}_mm_anio')
 rows.append({'precipitation':n,'n_complete_years':len(v),'n_admissible_annual_points':int(y.loc[v.index,f'budyko_admissible_{n}'].sum()),'P_mean_mm':pm,'Q_mean_mm':qm,'ETo_mean_mm':em,'phi_ETo_over_P':phi,'EI_exploratory_P_minus_Q_over_P':ei,'omega_Fu_exploratory':om,'Fu_fit_residual':res,'elasticity_Fu_exploratory':et,'elasticity_Sankarasubramanian':ep,'n_elasticity_values':nn,'elasticity_bootstrap95_low':lo,'elasticity_bootstrap95_high':hi})
v=y.loc[v.index].copy();y.to_csv(OUT/'1_3_serie_anual_hidrologica_P_Q_ETo_y_diagnosticos.csv',index=False);bs=pd.DataFrame(rows);bs.to_csv(TAB/'1_3_budyko_y_elasticidad_resumen_preliminar.csv',index=False)
# Complementary-relation preparation: terciles, never proof without actual ET.
c=v[['anio_hidrologico','PL_mm_anio','PI_mm_anio','Q_mm_anio','ETo_fao56_mm','Makkink_mm','Hargreaves_Samani_mm']].copy()
cc=[]
for n in ['PL','PI']:
 q1,q2=c[f'{n}_mm_anio'].quantile([1/3,2/3]);c[f'clase_{n}']=pd.cut(c[f'{n}_mm_anio'],[-np.inf,q1,q2,np.inf],labels=['seco','normal','humedo'],include_lowest=True);c[f'anomalia_{n}_mm']=c[f'{n}_mm_anio']-c[f'{n}_mm_anio'].mean()
 for z,g in c.groupby(f'clase_{n}',observed=False):cc.append({'precipitation':n,'class':str(z),'n_years':len(g),'P_mean_mm':g[f'{n}_mm_anio'].mean(),'ETo_FAO56_mean_mm':g.ETo_fao56_mm.mean(),'Makkink_mean_mm':g.Makkink_mm.mean(),'Hargreaves_Samani_mean_mm':g.Hargreaves_Samani_mm.mean()})
c['anomalia_ETo_mm']=c.ETo_fao56_mm-c.ETo_fao56_mm.mean();c.to_csv(TAB/'1_3_clasificacion_anual_seco_normal_humedo_y_demanda.csv',index=False);pd.DataFrame(cc).to_csv(TAB/'1_3_demanda_por_clase_hidrologica_preliminar.csv',index=False)
# Historical Tarea 1 sensitivity.  It is intentionally separate from Pacho's
# common-period estimate and requires 12 valid monthly records for each year.
hist=m.copy();hist['calendar_year']=hist.date.dt.year
history=[]
for label,key in [('hydrological_Sep_Aug','hydro_year'),('calendar_Jan_Dec','calendar_year')]:
 for n in ['PL','PI']:
  h=hist.groupby(key,as_index=False).agg(P_mm=(f'{n}_mm_mes','sum'),Q_mm=('runoff_mm_month','sum'),n_months=('date','count'),n_flow_complete=('flow_obs_complete','sum'))
  h=h.loc[(h.n_months==12)&(h.n_flow_complete==12)].copy()
  h=h.rename(columns={'P_mm':f'{n}_mm_anio','Q_mm':'Q_mm_anio'})
  ee,nn,ll,uu=elast(h,f'{n}_mm_anio')
  history.append({'aggregation':label,'precipitation':n,'n_complete_years':len(h),'year_first':int(h[key].min()),'year_last':int(h[key].max()),'elasticity_Sankarasubramanian':ee,'n_elasticity_values':nn,'bootstrap95_low':ll,'bootstrap95_high':uu})
pd.DataFrame(history).to_csv(TAB/'1_3_elasticidad_historica_y_sensibilidad_anual.csv',index=False)
# Light graphics for dashboard/LaTex reuse.
plt.style.use('seaborn-v0_8-whitegrid');fig,ax=plt.subplots(figsize=(9,4.8));ax.plot(cl.mes,cl.PL_mm_mes,'o-',label='PL');ax.plot(cl.mes,cl.PI_mm_mes,'o-',label='PI');ax.plot(cl.mes,cl.ETo_mm_mes,'o-',label='ETo FAO-56 preliminar');ax.set(ylabel='mm/mes',title='Racarumi: climatología mensual de oferta y demanda climática');ax.legend(ncol=3,fontsize=8);fig.tight_layout()
for z in ['png','pdf']:fig.savefig(FIG/f'1_3_climatologia_mensual_P_ETo_preliminar.{z}',dpi=180)
plt.close(fig)
fig,ax=plt.subplots(figsize=(7,6)); xx=np.linspace(.001,4,600);ax.plot(xx,np.minimum(1,xx),'k--',lw=1,label='límites agua/energía')
for n,col in [('PL','#1f77b4'),('PI','#ff7f0e')]:
 ax.scatter(v[f'phi_{n}'],v[f'EIexpl_{n}'],color=col,alpha=.7,label=f'{n}: P−Q anual');r=bs.set_index('precipitation').loc[n]
 if np.isfinite(r.omega_Fu_exploratory):ax.plot(xx,fu(xx,r.omega_Fu_exploratory),color=col,label=f'Fu {n}, ω={r.omega_Fu_exploratory:.2f}')
ax.set(xlim=(0,4),ylim=(0,1.15),xlabel='Índice de aridez φ = ETo/P',ylabel='Índice evaporativo exploratorio (P−Q)/P',title='Budyko exploratorio; no es ET observada');ax.legend(fontsize=7);fig.tight_layout()
for z in ['png','pdf']:fig.savefig(FIG/f'1_3_budyko_exploratorio.{z}',dpi=180)
plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(10,4.5),sharey=True)
for ax,n,col in zip(axs,['PL','PI'],['#1f77b4','#ff7f0e']):ax.scatter(c[f'{n}_mm_anio'],c.Q_mm_anio,color=col);ax.set(title=f'{n}: precipitación vs escorrentía',xlabel='P (mm/año hidrológico)')
axs[0].set_ylabel('Q (mm/año hidrológico)');fig.tight_layout()
for z in ['png','pdf']:fig.savefig(FIG/f'1_3_elasticidad_dispersion_PL_PI.{z}',dpi=180)
plt.close(fig)
# Exact request only; no download.
soil={'status':'HISTORICO (etapa inicial, superada): solicitud registrada antes de la descarga. La humedad del suelo se descargo y proceso despues en 02_humedad_suelo/process_1_3_2_humedad_suelo.py; ET real y Rn superficial se integraron en 06_integracion_1_2_pacho.','dataset':'reanalysis-era5-land-monthly-means','variables':['volumetric_soil_water_layer_1','volumetric_soil_water_layer_2','volumetric_soil_water_layer_3','volumetric_soil_water_layer_4'],'period':'1981-01 through 2023-08','format':'netcdf','area_N_W_S_E':[-6.350416666666668,-79.32208333366667,-6.917916666666667,-78.62708333333333],'polygon_crs':'EPSG:4326','aggregation':'área ponderada por polígono; 0–100 cm = 0.07*swvl1 + 0.21*swvl2 + 0.72*swvl3','filename':'ERA5Land_monthly_soilwater_Racarumi_198101_202308.nc','destination':'tarea 02/datos/punto1/originales/1_3_humedad_suelo/','official_url':'https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land-monthly-means?tab=download','warning':'No usar Rn de pasto FAO-56 para FE; faltan ET real y radiación neta superficial real.'}
(ANN/'solicitud_era5land_humedad_suelo_historica.json').write_text(json.dumps(soil,ensure_ascii=False,indent=2),encoding='utf8')
summary=['# Apartado 1.3 — estado técnico de la etapa inicial (superado por 02_humedad_suelo y 06_integracion_1_2_pacho)','','ETo es FAO-56 preliminar (20 celdas ERA5-Land, cobertura espacial 90.1264 %), no ET real ni PET observada.','','## Estado frente a la guía','1. Régimen mensual: COMPLETADO como oferta/demanda climática; ET/ETo, ET/P y clasificación final: PENDIENTES por ET real.','2. Humedad del suelo: PENDIENTE POR DATOS. Se dejó solicitud CDS mensual por área; no se descargó nada.','3. Budyko: PRELIMINAR. P−Q es sólo ET exploratoria multi-anual, condicionado a ΔS pequeño y ausencia de aportes, extracciones y regulación significativos.','4. Elasticidad: PRELIMINAR. Mediana no paramétrica de Sankarasubramanian et al. (2001); la regulación documentada en Tarea 1 limita la interpretación.','5. Relación complementaria: PRELIMINAR. La demanda se compara entre terciles de P; no se demuestra sin ET real.','','## Datos exactos aún requeridos de Pacho','1. Archivo fuente trazable y definición/unidad de Q; 2. ET real mensual/anual del 1.2 con metadatos; 3. ΔS o justificación cuantitativa para ΔS≈0; 4. regulación/transferencias/extracciones y periodos; 5. Rn superficial real si se calculará FE.','','## Referencias','Fu, B. (1981). On the calculation of the evaporation from land surface. Atmospheric Sinica, 5, 23–31.','Sankarasubramanian, A., Vogel, R. M. & Limbrunner, J. F. (2001). Climate elasticity of streamflow in the United States. Water Resources Research, 37, 1771–1781. https://doi.org/10.1029/2000WR900330']
(ANN/'resumen_tecnico_preliminar_1_3.md').write_text('\n'.join(summary)+'\n',encoding='utf8')
inv={'script':str(Path(__file__).relative_to(ROOT)),'tables':[q.name for q in TAB.glob('*.csv')],'figures':[q.name for q in FIG.glob('1_3_*')],'annexes':[q.name for q in ANN.glob('*')],'status':'PRELIMINAR: faltan ET real, Rn superficial real y humedad del suelo.'};(ANN/'inventario_productos_1_3.json').write_text(json.dumps(inv,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'source_qc':qc,'budyko_elasticity':rows,'outputs':inv},ensure_ascii=False,indent=2))
