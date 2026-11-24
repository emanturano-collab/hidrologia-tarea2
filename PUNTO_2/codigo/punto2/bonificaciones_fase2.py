"""Calcula productos reproducibles para los bonos 2.5.1--2.5.5."""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import genextreme, norm

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'datos' / 'punto2' / 'Abtsgmuend_Untergroeningen'
OUT = BASE / 'bonificaciones_2_5'
OUT.mkdir(parents=True, exist_ok=True)
A, C, tc_min, Qc = 0.123154, 0.33239, 4.22613, 7.076
Tvals = np.array([2, 5, 10, 25, 50, 100], dtype=float)

# 2.5.1: expected-cost design using the IDF, empirical AMS losses and FRC.
idf = pd.read_csv(BASE/'idf_2_3'/'idf_powerlaw_parameters.csv')
d_h = tc_min/60
qdesign = C * idf.a.to_numpy() * d_h**(-idf.eta.to_numpy()) * A/3.6
q2 = float(qdesign[0])
ams = pd.read_csv(BASE/'ams_precipitation.csv')
qsample = C * ams.max_1h_mm.to_numpy() / 3.6 * A
r, nlife = 0.06, 30
frc = r*(1+r)**nlife/((1+r)**nlife-1)
rows=[]
for T, Q in zip(Tvals, qdesign):
    cobra=(Q/q2)**0.6
    damage=np.where(qsample>Q,20*(1-np.exp(-(qsample-Q)/(0.5*Q))),0).mean()
    rows.append([T,Q,cobra,frc*cobra,damage,frc*cobra+damage])
cost=pd.DataFrame(rows,columns=['T_years','Q_design_m3s','construction_C0','annualized_construction_C0','expected_damage_C0','expected_total_C0'])
cost.to_csv(OUT/'bono_2_5_1_costo_esperado.csv',index=False)
best=cost.loc[cost.expected_total_C0.idxmin()]

# 2.5.2: POT versus AMS through Langbein's relation.
pot=pd.read_csv(BASE/'bonificacion_2_5_pot'/'pot_return_levels.csv')
pot['T_equiv_Langbein']=1/(1-np.exp(-1/pot.T_years))
amsq=pd.read_csv(BASE/'extremos_2_2'/'quantiles_mle.csv')
amsq=amsq[(amsq.duration=='1h')&(amsq.model=='gev_mle')].copy()
pot['AMS_GEV_at_T_equiv_mm']=np.interp(pot.T_equiv_Langbein,amsq.T_years,amsq.quantile_mm)
pot['difference_POT_minus_AMS_mm']=pot.return_level_mm_1h-pot.AMS_GEV_at_T_equiv_mm
pot.to_csv(OUT/'bono_2_5_2_pot_langbein.csv',index=False)

# 2.5.3: 7% per degree warming scenario.
fit=pd.read_csv(BASE/'extremos_2_2'/'fit_summary_mle.csv')
par=fit[(fit.duration=='1h')&(fit.model=='gev_mle')].iloc[0].parameters.split(';')
cgev, loc, scale = map(float,par)
base=float(qdesign[list(Tvals).index(25)])
base_i=float(amsq[(amsq.T_years==25)].quantile_mm.iloc[0]) if 'amsq' in globals() else float(pd.read_csv(BASE/'extremos_2_2'/'quantiles_mle.csv').query("duration=='1h' and model=='gev_mle' and T_years==25").quantile_mm.iloc[0])
climate=[]
for delta in [0,1,2,3]:
    factor=1.07**delta; q=base*factor; d=(1.5*factor**(3/8)); warmed_i=base_i/factor; p=1-genextreme.cdf(warmed_i,cgev,loc=loc,scale=scale); climate.append([delta,factor,q,d,1/p])
pd.DataFrame(climate,columns=['warming_degC','rain_factor','Qp_m3s','diameter_equiv_m','effective_T_years']).to_csv(OUT/'bono_2_5_3_cambio_climatico.csv',index=False)

# 2.5.4: reliability/resilience/vulnerability from the complete 10-min series.
raw=pd.read_csv(BASE/'abtsgmuend_precipitation_10min.csv')
raw['timestamp']=pd.to_datetime(raw.timestamp_utc.astype(str),format='%Y%m%d%H%M',errors='coerce')
raw['p']=pd.to_numeric(raw.precip_mm,errors='coerce').where(lambda x:x>=0)
hour=raw.set_index('timestamp')['p'].resample('1h').sum(min_count=6).dropna()
q=hour*C*A/3.6
ex=q>Qc
groups=(ex!=ex.shift()).cumsum()
events=[]
for _,g in q[ex].groupby(groups[ex]):
    events.append([g.index.min(),g.index.max(),len(g),float(g.max()),float(g.max()/Qc)])
events_df=pd.DataFrame(events,columns=['start','end','duration_hours','peak_Q_m3s','vulnerability_ratio'])
if len(events_df):
    events_df['recovery_hours']=(pd.to_datetime(events_df.start).shift(-1)-pd.to_datetime(events_df.end)).dt.total_seconds()/3600
    events_df.to_csv(OUT/'bono_2_5_4_exceedance_events.csv',index=False)
summary=pd.DataFrame([['hours_valid',len(q)],['hours_exceeding',int(ex.sum())],['annual_exceedance_frequency',float(ex.sum()/((hour.index.max()-hour.index.min()).days/365.25))],['events',len(events_df)],['mean_recovery_hours',float(events_df.recovery_hours.dropna().mean()) if len(events_df) else np.nan],['max_vulnerability_ratio',float(events_df.vulnerability_ratio.max()) if len(events_df) else np.nan]],columns=['metric','value'])
summary.to_csv(OUT/'bono_2_5_4_reliability_summary.csv',index=False)

# 2.5.5: exploratory Gaussian copula on annual maximum intensity-duration pairs.
amsw=pd.read_csv(BASE/'ams_precipitation.csv')
durcols=[('max_10min_mm',10),('max_30min_mm',30),('max_1h_mm',60),('max_3h_mm',180),('max_6h_mm',360),('max_12h_mm',720),('max_24h_mm',1440)]
vals=amsw[[c for c,_ in durcols]].to_numpy(float); idx=np.nanargmax(vals,axis=1)
pair=pd.DataFrame({'year':amsw.year,'intensity_1h_mm_h':amsw.max_1h_mm,'duration_of_max_depth_min':[durcols[i][1] for i in idx]})
u=pair[['intensity_1h_mm_h','duration_of_max_depth_min']].rank(pct=True)
z=pd.DataFrame(norm.ppf(np.clip(u,0.001,0.999)),columns=u.columns)
rho=float(z.corr().iloc[0,1])
joint=[]
for threshold in [0.90,0.95,0.98]:
    exceed=((u.iloc[:,0]>threshold)&(u.iloc[:,1]>threshold)).sum(); p=exceed/len(pair); joint.append([threshold,exceed,p,1/p if p else np.inf])
pair.to_csv(OUT/'bono_2_5_5_event_pairs.csv',index=False)
pd.DataFrame(joint,columns=['marginal_quantile','joint_exceedances','joint_probability','joint_return_years']).to_csv(OUT/'bono_2_5_5_copula_return_periods.csv',index=False)
(OUT/'bonificaciones_fase2_resumen.md').write_text(f'''# Bonificaciones Fase 2\n\n- **2.5.1 mínimo costo:** T óptimo empírico = {best.T_years:.0f} años; se comparó construcción anualizada y daño esperado con FRC={frc:.5f}.\n- **2.5.2 POT–AMS:** se aplicó Langbein a POT P90–P98 y se comparó con GEV-AMS.\n- **2.5.3 clima:** se evaluó escalamiento 7 % por °C para 1–3 °C; el diámetro equivalente se obtiene con Manning y el periodo efectivo con GEV 1 h.\n- **2.5.4 desempeño:** se convirtió la serie completa a caudal horario con racional; los eventos, recuperación y vulnerabilidad están en CSV.\n- **2.5.5 cópula:** se ajustó una cópula gaussiana exploratoria a intensidad horaria y duración del máximo anual; los periodos conjuntos están en CSV.\n\nLos bonos 2.5.4 y 2.5.5 son resultados exploratorios: requieren revisión del grupo sobre definición de recuperación, dependencia temporal y selección de eventos antes de declararse plenamente obtenidos.\n''',encoding='utf-8')
print(OUT)
