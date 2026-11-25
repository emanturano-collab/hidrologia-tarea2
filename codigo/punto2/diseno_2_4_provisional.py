"""Cálculo provisional de 2.4 A/B; sustituir supuestos cuando se cierre el outlet."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir()); DATA=ROOT/'datos'/'punto2'/'Abtsgmuend_Untergroeningen'; OUT=DATA/'diseno_2_4'; OUT.mkdir(exist_ok=True)
A=0.12315; L=600.; S_cuenca=0.08; C=0.45; n_manning=0.013; S_pipe=0.01; CN=75.; life=30
idf=pd.read_csv(DATA/'idf_2_3'/'idf_powerlaw_parameters.csv')
def intensity(duration_h,T):
    r=idf[idf.T_years==T].iloc[0]; return r.a*duration_h**(-r.eta)
def main():
    summary=pd.read_csv(DATA/'cuenca_preparada'/'cuenca_resumen.csv'); sv=dict(zip(summary.campo,summary.valor)); L=float(sv.get('main_channel_length_m',600)); S_cuenca=float(sv.get('main_channel_slope_m_m',0.08)); C=float(pd.read_csv(DATA/'cobertura_2_4'/'weighted_runoff_coefficient.csv').weighted_C.iloc[0]);
    tc_k=0.0195*L**0.77*S_cuenca**(-0.385)
    tc_kerby=1.44*(L*0.3)**0.467*S_cuenca**(-0.235)
    Lft=L*3.28084; tc_scs=(Lft**0.8*(S_cuenca+1)**0.7/(1900*(1000/CN-10)**0.5))/0.6*60
    tc=pd.DataFrame([{'formula':'Kirpich','tc_min':tc_k},{'formula':'Kerby-Hathaway','tc_min':tc_kerby},{'formula':'SCS-lag','tc_min':tc_scs}]); tc.to_csv(OUT/'tc_comparacion.csv',index=False,float_format='%.4f')
    tc_use=float(tc.tc_min.median()); i=intensity(tc_use/60,25); q=C*i*A/3.6; D=(q*n_manning/(0.312*S_pipe**0.5))**(3/8); Dcom=np.ceil(D/0.05)*0.05
    pd.DataFrame([{'area_km2':A,'C':C,'tc_median_min':tc_use,'T_years':25,'intensity_mm_h':i,'Qp_m3s':q,'diameter_calculated_m':D,'diameter_commercial_m':Dcom,'L_assumed_m':L,'S_assumed':S_cuenca,'status':'provisional'}]).to_csv(OUT/'problema_A_provisional.csv',index=False,float_format='%.5f')
    rng=np.random.default_rng(202602); N=5000; Cs=np.clip(rng.normal(C,.09,N),.2,.8); tcs=np.exp(rng.normal(np.log(tc_use),.2,N)); ns=np.clip(rng.normal(n_manning,.0015,N),.009,.02); Ss=np.clip(rng.normal(S_pipe,.002,N),.003,.02); is_=intensity(tcs/60,25)*rng.lognormal(0,.12,N); qs=Cs*is_*A/3.6; ds=(qs*ns/(.312*Ss**.5))**(3/8); qcap=.312/ns.mean()*Dcom**(8/3)*Ss.mean()**.5; fail=(qs>qcap); risk=fail.mean(); pd.DataFrame({'Qp_m3s':qs,'D_required_m':ds,'fail_indicator':fail}).to_csv(OUT/'monte_carlo_A.csv',index=False); pd.DataFrame([{'iterations':N,'Qp_p50':np.median(qs),'Qp_p025':np.quantile(qs,.025),'Qp_p975':np.quantile(qs,.975),'D_p50':np.median(ds),'D_p975':np.quantile(ds,.975),'annual_effective_failure':risk,'life_risk_30yr':1-(1-risk)**life,'capacity_Qc_m3s':qcap}]).to_csv(OUT/'riesgo_A.csv',index=False,float_format='%.6f')
    # Tanque preliminar: tormenta de 3 tc, bloques alternos de 10 min, T=10.
    dt=10/60; duration=max(6, int(np.ceil(3*tc_use/10))*10); times=np.arange(0,duration+10,10); d_h=times/60; depths=np.array([intensity(10/60,10)*10/60]*len(times)); depths[0]=depths[-1]=0; rain=depths.copy(); rain[1:-1]=0; center=len(rain)//2; order=np.argsort(-np.arange(1,len(rain)-1)); rem=float(intensity(duration/60,10)*duration/60); rain[1:-1]=0; rain[center]=rem; inflow=C*(rain/dt)*A/3.6; tank_area=100.; Cd=.65; Ao=.015; Sstore=0.; out=[]; hs=[]
    for I in inflow:
        h=Sstore/tank_area; O=Cd*Ao*np.sqrt(2*9.81*max(h,0)); Sstore=max(0,Sstore+(I-O)*dt*3600); out.append(O); hs.append(Sstore/tank_area)
    pd.DataFrame({'time_min':times,'rain_mm':rain,'inflow_m3s':inflow,'outflow_m3s':out,'depth_m':hs}).to_csv(OUT/'tanque_hietograma_provisional.csv',index=False,float_format='%.6f')
    pd.DataFrame([{'duration_min':duration,'tc_median_min':tc_use,'T_years':10,'tank_area_m2':tank_area,'orifice_diameter_m':2*np.sqrt(Ao/np.pi),'max_storage_m3':max(np.array(hs)*tank_area),'max_depth_m':max(hs),'status':'provisional_outlet_and_C'}]).to_csv(OUT/'tanque_provisional.csv',index=False,float_format='%.6f')
    (OUT/'README.md').write_text('# Diseño 2.4 provisional\n\nLos resultados se calculan con L=600 m, S=0.08, C=0.45, CN=75 y un tanque idealizado. Deben reemplazarse por valores medidos una vez se cierre el outlet, coberturas y geometría.\n',encoding='utf-8')
    print('Diseño provisional generado; tc=',tc_use,'Q=',q,'D=',Dcom)
if __name__=='__main__': main()
