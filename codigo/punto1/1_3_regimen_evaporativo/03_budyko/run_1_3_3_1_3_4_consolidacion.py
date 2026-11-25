"""Validation and consolidation of existing Budyko/elasticity outputs."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
ROOT=next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
OUT=ROOT/'datos/punto1/procesados/1_3_regimen_evaporativo'; TAB=ROOT/'productos/punto1/1_3_regimen_evaporativo/tablas'; FIG=ROOT/'productos/punto1/1_3_regimen_evaporativo/figuras'; ANN=ROOT/'anexos/punto1/1_3_regimen_evaporativo'
for x in [OUT,TAB,FIG,ANN]:x.mkdir(parents=True,exist_ok=True)
Y=pd.read_csv(OUT/'1_3_serie_anual_hidrologica_P_Q_ETo_y_diagnosticos.csv'); OLD=pd.read_csv(TAB/'1_3_budyko_y_elasticidad_resumen_preliminar.csv').set_index('precipitation'); HIST=pd.read_csv(TAB/'1_3_elasticidad_historica_y_sensibilidad_anual.csv')
V=Y.loc[Y.q_complete.astype(bool)&Y.all_12_months_eto.astype(bool)].sort_values('anio_hidrologico').copy()
FAO=ROOT/'datos/punto1/procesados/1_1_a_fao56_preliminar_90pct/fao56_eto_mensual_preliminar_90pct.csv'
def F(phi,w):return 1+phi-(1+phi**w)**(1/w)
def Fp(phi,w):return 1-phi**(w-1)*(1+phi**w)**(1/w-1)
def B74(phi):return np.sqrt(phi*np.tanh(1/phi)*(1-np.exp(-phi)))
def fit(phi,ei):
 if not(np.isfinite(phi) and np.isfinite(ei) and phi>0 and 0<=ei<=min(1,phi)):return np.nan,np.nan
 w=np.linspace(1.01,20,190000);r=F(phi,w)-ei;i=np.abs(r).argmin();return float(w[i]),float(r[i])
def calc(d,p,label):
 pm,qm,em=d[f'{p}_mm_anio'].mean(),d.Q_mm_anio.mean(),d.ETo_fao56_mm.mean();phi=em/pm;ei=(pm-qm)/pm;w,res=fit(phi,ei);fp=Fp(phi,w);h=1e-6*max(1,phi);num=(F(phi+h,w)-F(phi-h,w))/(2*h);eps=1+phi*fp/(1-F(phi,w))
 return {'precipitation':p,'selection':label,'n_years':len(d),'first_year':int(d.anio_hidrologico.min()),'last_year':int(d.anio_hidrologico.max()),'P_mean_mm':pm,'Q_mean_mm':qm,'ETo_mean_mm':em,'phi':phi,'EI_exploratory':ei,'omega':w,'Fu_at_phi':F(phi,w),'Fu_residual':res,'Budyko1974_at_phi':B74(phi),'vertical_distance_EI_minus_Budyko1974':ei-B74(phi),'Fprime_analytic':fp,'Fprime_numeric':num,'Fprime_abs_error':abs(fp-num),'elasticity_theoretical':eps}
rows=[]
for p in ['PL','PI']:
 rows += [calc(V,p,'all_common_complete'),calc(V.head(10),p,'early_10_complete_years'),calc(V.tail(10),p,'late_10_complete_years')]
 rows += [calc(V.loc[V.anio_hidrologico!=yr],p,f'leave_out_{int(yr)}') for yr in V.anio_hidrologico]
R=pd.DataFrame(rows);M=R.loc[R.selection.eq('all_common_complete')].copy()
for p in ['PL','PI']:
 ix=M.precipitation.eq(p);o=OLD.loc[p];M.loc[ix,'previous_phi']=o.phi_ETo_over_P;M.loc[ix,'previous_EI']=o.EI_exploratory_P_minus_Q_over_P;M.loc[ix,'previous_omega']=o.omega_Fu_exploratory;M.loc[ix,'difference_phi_vs_previous']=M.loc[ix,'phi']-o.phi_ETo_over_P;M.loc[ix,'difference_EI_vs_previous']=M.loc[ix,'EI_exploratory']-o.EI_exploratory_P_minus_Q_over_P;M.loc[ix,'difference_omega_vs_previous']=M.loc[ix,'omega']-o.omega_Fu_exploratory
R=R.merge(M[['precipitation','difference_phi_vs_previous','difference_EI_vs_previous','difference_omega_vs_previous']],on='precipitation',how='left');R.to_csv(TAB/'1_3_3_budyko_sensibilidad_Fu_y_verificacion_matematica.csv',index=False)
# Period audit: direct FAO-56 reaches Aug-2023, whereas the 1.1.c multi-method
# master ends Dec-2022. This extra check never replaces the 20-year baseline.
f=pd.read_csv(FAO,parse_dates=['month']);f['anio_hidrologico']=f.month.dt.year+(f.month.dt.month>=9).astype(int);fa=f.groupby('anio_hidrologico',as_index=False).agg(ETo_fao56_direct_mm=('eto_from_daily_mm','sum'),n_ETo_months=('month','count'))
direct=Y[['anio_hidrologico','PL_mm_anio','PI_mm_anio','Q_mm_anio','q_complete']].merge(fa,on='anio_hidrologico',how='left');direct=direct.loc[direct.q_complete.astype(bool)&direct.n_ETo_months.eq(12)].rename(columns={'ETo_fao56_direct_mm':'ETo_fao56_mm'}).sort_values('anio_hidrologico')
audit=[]
for p in ['PL','PI']:
 a=calc(V,p,'baseline_1_1c_multimethod_20_years');b=calc(direct,p,'supplemental_direct_FAO56_21_years');audit += [a,b]
pd.DataFrame(audit).to_csv(TAB/'1_3_3_auditoria_periodos_FAO_y_multimetodos.csv',index=False)
D=Y.copy()
for p in ['PL','PI']:
 D[f'Budyko1974_{p}']=np.where(D[f'phi_{p}']>0,B74(D[f'phi_{p}']),np.nan);D[f'distance_EIexpl_minus_Budyko1974_{p}']=D[f'EIexpl_{p}']-D[f'Budyko1974_{p}'];D[f'role_{p}']=np.where(~D.q_complete.astype(bool),'excluded_incomplete_Q',np.where(~D.all_12_months_eto.astype(bool),'excluded_incomplete_ETo',np.where(D[f'budyko_admissible_{p}'].astype(bool),'diagnostic_and_admissible','diagnostic_only_not_admissible')))
D.to_csv(OUT/'1_3_3_registro_anual_Budyko_completo_con_roles.csv',index=False)
C=[]
for _,a in M.iterrows():
 o=OLD.loc[a.precipitation];C.append({'precipitation':a.precipitation,'period':'2002–2022 hydrological years; 20 common complete years (2003 excluded for Q)','n_years':20,'omega_Fu_exploratory':a.omega,'phi':a.phi,'elasticity_theoretical_Fu':a.elasticity_theoretical,'elasticity_empirical_Sankarasubramanian':o.elasticity_Sankarasubramanian,'empirical_CI95_low':o.elasticity_bootstrap95_low,'empirical_CI95_high':o.elasticity_bootstrap95_high,'theory_minus_empirical':a.elasticity_theoretical-o.elasticity_Sankarasubramanian,'Q_change_plus10pct_P_theory_pct':10*a.elasticity_theoretical,'Q_change_minus10pct_P_theory_pct':-10*a.elasticity_theoretical,'Q_change_plus10pct_P_empirical_pct':10*o.elasticity_Sankarasubramanian,'Q_change_minus10pct_P_empirical_pct':-10*o.elasticity_Sankarasubramanian})
for _,a in HIST.iterrows():C.append({'precipitation':a.precipitation,'period':f"historical {a.aggregation}: {int(a.year_first)}–{int(a.year_last)}; not directly comparable to Fu fit",'n_years':a.n_complete_years,'elasticity_empirical_Sankarasubramanian':a.elasticity_Sankarasubramanian,'empirical_CI95_low':a.bootstrap95_low,'empirical_CI95_high':a.bootstrap95_high})
C=pd.DataFrame(C);C.to_csv(TAB/'1_3_4_comparacion_elasticidad_teorica_empirica.csv',index=False)
plt.style.use('seaborn-v0_8-whitegrid');xx=np.linspace(.001,4,600);fig,axs=plt.subplots(1,2,figsize=(11,4.6),sharey=True)
for ax,(_,a) in zip(axs,M.iterrows()):
 p=a.precipitation;ax.plot(xx,B74(xx),'k--',label='Budyko (1974)');ax.plot(xx,F(xx,a.omega),color='#1769aa',label=f'Fu, ω={a.omega:.3f}');ax.scatter(V[f'phi_{p}'],V[f'EIexpl_{p}'],s=28,alpha=.65,label='P−Q anual');ax.scatter(a.phi,a.EI_exploratory,s=70,color='#d1495b',zorder=3,label='multianual');ax.vlines(a.phi,B74(a.phi),a.EI_exploratory,color='#d1495b');ax.set(title=f'Racarumi — {p}',xlabel='φ = ETo/P',xlim=(0,4),ylim=(0,1.1));ax.legend(fontsize=7)
axs[0].set_ylabel('ET/P exploratorio');fig.suptitle('Budyko: P−Q no es ET definitiva',y=1.02);fig.tight_layout()
for ext in ['png','pdf']:fig.savefig(FIG/f'1_3_3_Budyko1974_Fu_distancia_exploratoria.{ext}',dpi=180)
plt.close(fig)
E=C.loc[C.period.str.startswith('2002')].set_index('precipitation').loc[['PL','PI']];fig,ax=plt.subplots(figsize=(7,4.5));q=np.arange(2);ax.bar(q-.18,E.elasticity_theoretical_Fu,.35,label='Fu teórica');ax.bar(q+.18,E.elasticity_empirical_Sankarasubramanian,.35,label='Empírica');ax.errorbar(q+.18,E.elasticity_empirical_Sankarasubramanian,yerr=[E.elasticity_empirical_Sankarasubramanian-E.empirical_CI95_low,E.empirical_CI95_high-E.elasticity_empirical_Sankarasubramanian],fmt='none',ecolor='black',capsize=4);ax.set(xticks=q,xticklabels=['PL','PI'],ylabel='Elasticidad de Q respecto a P',title='Elasticidad: Fu vs estimador empírico');ax.legend();fig.tight_layout()
for ext in ['png','pdf']:fig.savefig(FIG/f'1_3_4_elasticidad_teorica_vs_empirica.{ext}',dpi=180)
plt.close(fig)
notes=['# Consolidación preliminar 1.3.3–1.3.4','','ETo FAO-56 se usa como aproximación operacional a la demanda/potencial de Budyko; no es idéntica a la evapotranspiración potencial y tiene cobertura espacial preliminar de 90.1264 %.','', 'P−Q es sólo una ET exploratoria multianual: faltan la demostración de ΔS anual pequeño y la caracterización consolidada de regulación, transferencias o extracciones. Los cinco PI−Q negativos permanecen como diagnósticos de limitación del balance, no ET negativa.','','F(φ)=1+φ−(1+φ^ω)^(1/ω). F′(φ)=1−φ^(ω−1)(1+φ^ω)^(1/ω−1). La tabla incluye derivada analítica y diferencia central numérica.','','La humedad radicular procesada es máxima climatológica en marzo (0.3936 m³/m³) y mínima en agosto (0.2666 m³/m³), coherente con oferta climática alta/baja respectivamente; no permite atribuir por sí sola vegetación, almacenamiento anual ni regulación.','','Cuando 1.2 entregue ET real, la trayectoria anual deberá sustituir EIexpl=(P−Q)/P por ET/P por producto, manteniendo el año Sep–Ago.','','## Referencias','Budyko, M. I. (1974). Climate and Life. Academic Press.','Fu, B. (1981). On the calculation of the evaporation from land surface. Atmospheric Sinica, 5, 23–31.','Sankarasubramanian, A., Vogel, R. M., & Limbrunner, J. F. (2001). Climate elasticity of streamflow in the United States. Water Resources Research, 37, 1771–1781. https://doi.org/10.1029/2000WR900330']
(ANN/'resumen_consolidado_1_3_3_y_1_3_4_preliminar.md').write_text('\n'.join(notes)+'\n',encoding='utf8')
print(json.dumps({'main':M.to_dict(orient='records'),'comparison':C.to_dict(orient='records'),'max_derivative_error':float(M.Fprime_abs_error.max())},ensure_ascii=False,indent=2))
