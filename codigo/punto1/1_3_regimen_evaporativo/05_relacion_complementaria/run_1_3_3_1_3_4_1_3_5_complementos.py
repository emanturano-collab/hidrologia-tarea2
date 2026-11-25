"""New complements only: Budyko uncertainty and 1.3.5 demand diagnostics.
Reads prior outputs; does not replace existing Budyko, elasticity or soil products.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
ROOT=next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
OUT=ROOT/'datos/punto1/procesados/1_3_regimen_evaporativo';TAB=ROOT/'productos/punto1/1_3_regimen_evaporativo/tablas';FIG=ROOT/'productos/punto1/1_3_regimen_evaporativo/figuras';ANN=ROOT/'anexos/punto1/1_3_regimen_evaporativo';META=ROOT/'datos/punto1/metadatos'
Y=pd.read_csv(OUT/'1_3_serie_anual_hidrologica_P_Q_ETo_y_diagnosticos.csv');ALT=pd.read_csv(ROOT/'datos/punto1/procesados/1_1_c_metodos_alternativos/1_1c_tabla_maestra_mensual_preliminar_90pct.csv',parse_dates=['date']);SOIL=pd.read_csv(OUT/'1_3_2_humedad_suelo_mensual_ponderada_198101_202308.csv',parse_dates=['date']);D=pd.read_csv(ROOT/'datos/punto1/procesados/1_1_d_explicacion_fisica/1_1d_componentes_y_alpha_mensuales_preliminar_90pct.csv',parse_dates=['date']);U=pd.read_csv(ROOT/'productos/punto1/1_2_evapotranspiracion_real/tablas/1_2_2_resumen_propagacion_error_principal.csv')
FM=pd.read_csv(ROOT/'datos/punto1/procesados/1_1_a_fao56_preliminar_90pct/fao56_eto_mensual_preliminar_90pct.csv',parse_dates=['month'])
for x in [OUT,TAB,FIG,ANN,META]:x.mkdir(parents=True,exist_ok=True)
def hy(s):return s.dt.year+(s.dt.month>=9).astype(int)
def F(phi,w):return 1+phi-(1+phi**w)**(1/w)
def Fp(phi,w):return 1-phi**(w-1)*(1+phi**w)**(1/w-1)
def omega(phi,ei):
 if not(np.isfinite(phi) and np.isfinite(ei) and phi>0 and 0<=ei<=min(1,phi)):return np.nan
 w=np.linspace(1.01,20,190000);return float(w[np.abs(F(phi,w)-ei).argmin()])
def elast(phi,w):return 1+phi*Fp(phi,w)/(1-F(phi,w)) if np.isfinite(w) else np.nan
def save(fig,name):
 for ext in ['png','pdf']:fig.savefig(FIG/f'{name}.{ext}',dpi=180)
 plt.close(fig)
# 1.3.3/1.3.4: use exactly the base 20-year sample already used for multi-method Budyko.
V=Y.loc[Y.q_complete.astype(bool)&Y.all_12_months_eto.astype(bool)].sort_values('anio_hidrologico').copy()
qsc=U[['scenario_Q','Q_bound_assumed_pct','sigmaQ_as_percent_of_Q','sigmaP_interproduct_dispersion_mm_year']].drop_duplicates().copy()
bud=[]
for src in ['PL','PI']:
 p,q,e=V[f'{src}_mm_anio'].mean(),V.Q_mm_anio.mean(),V.ETo_fao56_mm.mean()
 for _,s in qsc.iterrows():
  sp=float(s.sigmaP_interproduct_dispersion_mm_year);sq=float(s.sigmaQ_as_percent_of_Q)/100*q
  # Corners preserve ET=P-Q; no independent ET perturbation is used.
  for ps in [-1,0,1]:
   for qs in [-1,0,1]:
    pp=p+ps*sp;qq=q+qs*sq;phi=e/pp;ei=1-qq/pp;w=omega(phi,ei);admiss=bool(pp>0 and qq>=0 and 0<=ei<=min(1,phi))
    bud.append({'precipitation_source':src,'scenario_Q':s.scenario_Q,'Q_bound_assumed_pct':s.Q_bound_assumed_pct,'P_corner_sign':ps,'Q_corner_sign':qs,'P_mm_year':pp,'Q_mm_year':qq,'ETo_mm_year':e,'phi_ETo_over_P':phi,'EI_P_minus_Q_over_P':ei,'omega_Fu':w,'elasticity_theoretical':elast(phi,w),'physical_admissible':admiss,'dependence_note':'ET recomputed as P-Q in every corner'})
B=pd.DataFrame(bud);B.to_csv(TAB/'1_3_3_4_sensibilidad_Budyko_elasticidad_a_incertidumbre_1_2_2.csv',index=False)
# Main uncertainty table gives delta-method and admissible-corner ranges.
base=[]
for src in ['PL','PI']:
 p,q,e=V[f'{src}_mm_anio'].mean(),V.Q_mm_anio.mean(),V.ETo_fao56_mm.mean();phi=e/p;ei=1-q/p;w=omega(phi,ei)
 for _,s in qsc.iterrows():
  sp=float(s.sigmaP_interproduct_dispersion_mm_year);sq=float(s.sigmaQ_as_percent_of_Q)/100*q;sigphi=abs(e/p**2)*sp;sigei=np.sqrt((q/p**2*sp)**2+(sq/p)**2);z=B.loc[(B.precipitation_source==src)&(B.scenario_Q==s.scenario_Q)&B.physical_admissible]
  base.append({'precipitation_source':src,'scenario_Q':s.scenario_Q,'phi':phi,'EI_exploratory':ei,'omega':w,'elasticity_theoretical':elast(phi,w),'sigma_phi_delta':sigphi,'sigma_EI_delta_preserving_P_minus_Q':sigei,'n_admissible_corners':len(z),'phi_corner_min':z.phi_ETo_over_P.min(),'phi_corner_max':z.phi_ETo_over_P.max(),'EI_corner_min':z.EI_P_minus_Q_over_P.min(),'EI_corner_max':z.EI_P_minus_Q_over_P.max(),'omega_corner_min':z.omega_Fu.min(),'omega_corner_max':z.omega_Fu.max(),'elasticity_corner_min':z.elasticity_theoretical.min(),'elasticity_corner_max':z.elasticity_theoretical.max()})
BS=pd.DataFrame(base);BS.to_csv(TAB/'1_3_3_4_resumen_sensibilidad_incertidumbre_1_2_2.csv',index=False)
# 1.3.5 common 20-year annual table, original ETo coverage 90.1264% retained.
ALT['hydro_year']=hy(ALT.date);A=ALT.groupby('hydro_year',as_index=False).sum(numeric_only=True);A=A.loc[A.hydro_year.isin(V.anio_hidrologico)].copy();SOIL['hydro_year']=hy(SOIL.date);S=SOIL.groupby('hydro_year',as_index=False).agg(theta_rz_mean=('theta_rz_0_100m3_m3','mean'),theta_rz_min=('theta_rz_0_100m3_m3','min'),theta_rz_max=('theta_rz_0_100m3_m3','max'))
D['hydro_year']=hy(D.date);G=D.groupby('hydro_year',as_index=False).mean(numeric_only=True)
FM['hydro_year']=hy(FM.month);TM=FM.groupby('hydro_year',as_index=False).agg(Tmean_C=('tmean_c','mean'))
A=A.rename(columns={'hydro_year':'hy_alt'});S=S.rename(columns={'hydro_year':'hy_soil'});G=G.rename(columns={'hydro_year':'hy_phys'});TM=TM.rename(columns={'hydro_year':'hy_temp'})
C=V[['anio_hidrologico','PL_mm_anio','PI_mm_anio','Q_mm_anio']].merge(A,left_on='anio_hidrologico',right_on='hy_alt',how='left').merge(S,left_on='anio_hidrologico',right_on='hy_soil',how='left').merge(G,left_on='anio_hidrologico',right_on='hy_phys',how='left').merge(TM,left_on='anio_hidrologico',right_on='hy_temp',how='left')
methods=['fao56','makkink_1957','hargreaves_samani_1985','priestley_taylor_1972','thornthwaite_1948','meyer_1915','rohwer_1931']
for method in methods:
 if method not in C and f'{method}_x' in C:C=C.rename(columns={f'{method}_x':method})
for p in ['PL','PI']:
 q1,q2=C[f'{p}_mm_anio'].quantile([1/3,2/3]);C[f'class_{p}_tercile']=pd.cut(C[f'{p}_mm_anio'],[-np.inf,q1,q2,np.inf],labels=['dry','normal','wet'],include_lowest=True);qq=C[f'{p}_mm_anio'].quantile([.25,.75]);C[f'class_{p}_quartile']=pd.cut(C[f'{p}_mm_anio'],[-np.inf,qq.iloc[0],qq.iloc[1],np.inf],labels=['dry','middle','wet'],include_lowest=True)
C.to_csv(OUT/'1_3_5_anual_demanda_humedad_forzantes_y_clases.csv',index=False)
stats=[];rng=np.random.default_rng(20261122)
for p in ['PL','PI']:
 for method in methods:
  groups={str(k):v[method].dropna().to_numpy() for k,v in C.groupby(f'class_{p}_tercile',observed=False)};dry,wet=groups['dry'],groups['wet'];bd=np.array([rng.choice(dry,len(dry),True).mean()-rng.choice(wet,len(wet),True).mean() for _ in range(5000)])
  for cat,val in groups.items():stats.append({'precipitation_source':p,'method':method,'class':cat,'n_years':len(val),'mean_mm_year':val.mean(),'sd_mm_year':val.std(ddof=1),'dry_minus_wet_mm_year':dry.mean()-wet.mean(),'dry_minus_wet_pct_of_wet':100*(dry.mean()-wet.mean())/wet.mean(),'bootstrap95_dry_minus_wet_low':np.quantile(bd,.025),'bootstrap95_dry_minus_wet_high':np.quantile(bd,.975),'units':'mm/year','coverage_ETo_fraction':.9012637836877098})
ST=pd.DataFrame(stats);ST.to_csv(TAB/'1_3_5_demanda_por_clase_seca_normal_humeda_todos_metodos.csv',index=False)
env=[]
for p in ['PL','PI']:
 for cat,g in C.groupby(f'class_{p}_tercile',observed=False):
  env.append({'precipitation_source':p,'class':str(cat),'n_years':len(g),'P_mean_mm_year':g[f'{p}_mm_anio'].mean(),'theta_rz_mean_m3_m3':g.theta_rz_mean.mean(),'Rs_mean_MJ_m2_d':g.rs_mj_m2_d_mean.mean(),'VPD_mean_kPa':g.vpd_kpa_mean.mean(),'u2_mean_m_s':g.u2_ms_mean.mean(),'Tmean_C':g.Tmean_C.mean(),'radiative_fraction_pct':g.fraction_radiative_pct.mean()})
ENV=pd.DataFrame(env);ENV.to_csv(TAB/'1_3_5_humedad_y_forzantes_por_clase.csv',index=False)
# Dashboard-ready category and anomaly figures.
plt.style.use('seaborn-v0_8-whitegrid');main=ST.loc[(ST.precipitation_source=='PL')&(ST.method.isin(['fao56','makkink_1957','hargreaves_samani_1985','priestley_taylor_1972','thornthwaite_1948']))]
fig,ax=plt.subplots(figsize=(10,5));pivot=main.pivot(index='method',columns='class',values='mean_mm_year').reindex(columns=['dry','normal','wet']);pivot.plot(kind='bar',ax=ax);ax.set(ylabel='mm/año',xlabel='Método',title='Demanda anual por clase PL (terciles)');fig.tight_layout();save(fig,'1_3_5_demanda_por_clase_PL')
fig,ax=plt.subplots(figsize=(9,4));colors={'dry':'#d1495b','normal':'#777777','wet':'#2a9d8f'}
for cat,g in C.groupby('class_PL_tercile',observed=False):ax.scatter(g.anio_hidrologico,g.fao56-g.fao56.mean(),label=str(cat),color=colors[str(cat)],s=40)
ax.axhline(0,color='k',lw=.8);ax.set(xlabel='Año hidrológico',ylabel='Anomalía FAO-56 (mm/año)',title='Anomalías de demanda FAO-56 y clase PL');ax.legend();fig.tight_layout();save(fig,'1_3_5_anomalias_demanda_FAO56_PL')
fig,ax=plt.subplots(figsize=(7,4.5));piv=ENV.loc[ENV.precipitation_source=='PL'].set_index('class').reindex(['dry','normal','wet']);ax.plot(piv.index,piv.theta_rz_mean_m3_m3,'o-',label='θrz anual');ax.set(ylabel='m³/m³',title='Humedad radicular por clase PL');ax.legend();fig.tight_layout();save(fig,'1_3_5_humedad_por_clase_PL')
fig,ax=plt.subplots(figsize=(8,4.5));x=np.arange(2);m=BS.loc[BS.scenario_Q.eq('main_15pct_bound')].set_index('precipitation_source').loc[['PL','PI']];ax.errorbar(x,m.elasticity_theoretical,yerr=[m.elasticity_theoretical-m.elasticity_corner_min,m.elasticity_corner_max-m.elasticity_theoretical],fmt='o',capsize=4,label='Fu: rango de esquinas admisibles');ax.set(xticks=x,xticklabels=['PL','PI'],ylabel='Elasticidad teórica',title='Sensibilidad de elasticidad a escenarios 1.2.2');ax.legend();fig.tight_layout();save(fig,'1_3_4_sensibilidad_elasticidad_incertidumbre')
# Explicit ET-real input contract, not a fabricated ET series.
spec=pd.DataFrame({'column':['date','hydro_year','product','ET_mm_month','Rn_surface_MJ_m2_day','quality_flag'],'required':[True,True,True,True,False,False],'purpose':['month start','Sep–Aug closing year','product identity','actual ET only','needed for FE','source/coverage notes']});spec.to_csv(ANN/'1_3_5_especificacion_entrada_ETreal.csv',index=False)
notes=['# Complementos de 1.3.3, 1.3.4 y 1.3.5','','## Alcance','Budyko y elasticidad: sensibilidad nueva propaga escenarios de 1.2.2 manteniendo ET=P−Q; P y ET no se perturbaban independientemente. Los rangos no son intervalos de confianza del promedio multianual.','','## Relación complementaria','Bouchet plantea un acoplamiento negativo entre ET real regional y demanda aparente bajo superficies extensas, retroalimentación atmosférica y advección mínima. Brutsaert y Parlange (1998) discuten este principio en el ciclo hidrológico. No puede evaluarse aquí: faltan ET real y Rn superficial real. Un aumento de ETo en años secos no demuestra complementariedad.','','## Evidencia física disponible','Marzo presenta máxima humedad radicular climatológica y agosto mínima; el rezago máximo humedad–PL es un mes. FAO-56 tiene fracción radiativa dominante, pero esto no demuestra que ET real sea limitada por energía. La regulación y las discrepancias PL–PI limitan inferencia causal.','','## Referencias','Bouchet, R. J. (1963). Evapotranspiration réelle et évapotranspiration potentielle, signification climatique. IAHS General Assembly of Berkeley, pp. 134–142.','Brutsaert, W. & Parlange, M. B. (1998). Hydrologic cycle explains the evaporation paradox. Nature, 396, 30. https://doi.org/10.1038/23845','Fu, B. (1981). On the calculation of evaporation from land surface. Atmospheric Sinica, 5, 23–31.','Sankarasubramanian, A., Vogel, R. M. & Limbrunner, J. F. (2001). Climate elasticity of streamflow in the United States. Water Resources Research, 37, 1771–1781. https://doi.org/10.1029/2000WR900330']
(ANN/'1_3_3_1_3_4_1_3_5_complementos_tecnicos.md').write_text('\n'.join(notes)+'\n',encoding='utf8')
status=['# Estado actualizado — 1.3','','| Numeral | Estado | Límite principal |','|---|---|---|','| 1.3.1 Régimen mensual | PRELIMINAR | ET real mensual pendiente |','| 1.3.2 Humedad del suelo | COMPLETADO como disponibilidad | FE/umbral requieren ET real y Rn superficial |','| 1.3.3 Budyko | PRELIMINAR | P−Q exploratorio; falta ΔS y ET por producto |','| 1.3.4 Elasticidad | PRELIMINAR | regulación, almacenamiento y P/Q inciertos |','| 1.3.5 Relación complementaria | PENDIENTE POR DATOS | sin ET real no se prueba relación inversa |']
(ANN/'1_3_estado_cumplimiento_actualizado.md').write_text('\n'.join(status)+'\n',encoding='utf8')
(META/'1_3_3_1_3_4_1_3_5_control_calidad.json').write_text(json.dumps({'common_hydrological_years':V.anio_hidrologico.astype(int).tolist(),'n_years':len(V),'year_definition':'September–August, labelled by closing year','ETO_coverage_fraction':.9012637836877098,'soil_months_used':'1981-01 to 2023-08; annual grouping restricted to common 20 years','ET_real_available':False,'warning':'P-Q annual retained only as exploratory diagnostic; no ET/P definitive trajectory or complementary-relation conclusion.'},ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'years':C[['anio_hidrologico','class_PL_tercile','class_PI_tercile']].to_dict(orient='records'),'uncertainty':BS.to_dict(orient='records'),'method_stats':ST.loc[ST.method.eq('fao56')].to_dict(orient='records')},ensure_ascii=False,indent=2))
