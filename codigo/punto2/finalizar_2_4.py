"""Avanza 2.4 A/B con geometria DEM, C WorldCover y escenarios explicitos."""
from pathlib import Path
import math
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]; DATA=ROOT/'datos'/'punto2'/'Abtsgmuend_Untergroeningen'; OUT=DATA/'diseno_2_4'; OUT.mkdir(exist_ok=True)
A=float(pd.read_csv(DATA/'cuenca_preparada'/'cuenca_resumen.csv').set_index('campo').loc['area_km2','valor']); geom=pd.read_csv(DATA/'cuenca_preparada'/'cuenca_resumen.csv').set_index('campo'); L=float(geom.loc['main_channel_length_m','valor']); S=float(geom.loc['main_channel_slope_m_m','valor']); C=float(pd.read_csv(DATA/'cobertura_2_4'/'weighted_runoff_coefficient.csv').weighted_C.iloc[0]); n=.013; Sp=.01
idf=pd.read_csv(DATA/'idf_2_3'/'idf_powerlaw_parameters.csv')
def i(dh,T):
 r=idf[idf.T_years==T].iloc[0]; return float(r.a*dh**(-r.eta))
def tc_values(): return {'Kirpich':.0195*L**.77*S**(-.385),'Kerby-Hathaway':1.44*(L*.3)**.467*S**(-.235),'SCS-lag':((L*3.28084)**.8*(S+1)**.7/(1900*(1000/75-10)**.5))/0.6*60}
def design_A():
 rows=[]
 for name,tc in tc_values().items():
  for T in [10,25,50]:
   inten=i(tc/60,T); q=C*inten*A/3.6; d=(q*n/(.312*Sp**.5))**(3/8)
   rows.append({'tc_formula':name,'tc_min':tc,'T_years':T,'C':C,'intensity_mm_h':inten,'Qp_m3s':q,'D_calculated_m':d,'D_commercial_0.05m':np.ceil(d/.05)*.05})
 pd.DataFrame(rows).to_csv(OUT/'problema_A_escenarios.csv',index=False,float_format='%.5f')
 # Sensibilidad del escenario conservador de C y tc de Kirpich.
 tc=tc_values()['Kirpich']; sens=[]
 for cc in [C*.8,C,min(1,C*1.2)]:
  for nn in [.011,.013,.017]:
   for ss in [.0075,.01,.015]:
    q=cc*i(tc/60,25)*A/3.6; d=(q*nn/(.312*ss**.5))**(3/8); sens.append({'C':cc,'n':nn,'S_pipe':ss,'Qp_m3s':q,'D_m':d,'D_commercial_m':np.ceil(d/.05)*.05})
 pd.DataFrame(sens).to_csv(OUT/'sensibilidad_A.csv',index=False,float_format='%.5f')
def hyetograph(total_min,T,peak_pos):
 n=max(3,int(np.ceil(total_min/10))); dur=np.arange(1,n+1)*10/60; depths=np.array([i(x,T)*x for x in dur]); inc=np.diff(np.r_[0,depths]); order=np.argsort(inc)[::-1]; h=np.zeros(n); center=n//2; positions=list(range(center,n))+list(range(center-1,-1,-1));
 for k,idx in enumerate(order): h[positions[k]]=inc[idx]
 if peak_pos=='inicio': h=np.roll(h,-max(1,n//3))
 if peak_pos=='final': h=np.roll(h,max(1,n//3))
 return h
def route(total_min,T,tc,peak_pos):
 dt=10/60; h=hyetograph(total_min,T,peak_pos); rain=np.r_[h,np.zeros(12)]; win=max(1,int(round(tc/10))); inflow=C*A/3.6*pd.Series(rain).rolling(win,min_periods=1).mean()/dt
 tank_area=528.; Cd=.65; Ao=math.pi*(.30/2)**2; Sstore=0.; rec=[]
 for t,I in enumerate(inflow):
  H=Sstore/tank_area; O=Cd*Ao*np.sqrt(2*9.81*max(H,0)); Sstore=max(0,Sstore+(float(I)-O)*dt*3600); rec.append((t*10,rain[t],float(I),O,Sstore,Sstore/tank_area))
 return pd.DataFrame(rec,columns=['time_min','rain_mm','inflow_m3s','outflow_m3s','storage_m3','depth_m'])
def design_B():
 tc=tc_values()['Kirpich']; rows=[]
 for total in [max(30,3*tc),max(60,6*tc),max(90,9*tc)]:
  for pos in ['inicio','centro','final']:
   d=route(total,10,tc,pos); rows.append({'duration_min':total,'peak_position':pos,'max_storage_m3':d.storage_m3.max(),'max_depth_m':d.depth_m.max()}); d.to_csv(OUT/f'tanque_{int(total)}min_{pos}.csv',index=False,float_format='%.5f')
 pd.DataFrame(rows).to_csv(OUT/'tanque_escenarios.csv',index=False,float_format='%.5f')
def main():
 design_A(); design_B(); (OUT/'revision_2_4.md').write_text('# Avance de 2.4 A/B\n\nSe usaron área, longitud, pendiente y C ponderado derivados de DEM/WorldCover. Se evaluaron tres tc, T=10/25/50, sensibilidad de C, Manning y pendiente, y tres posiciones del pico del hietograma. La geometría del tanque (100 m2), Cd=0.65 y Ao=0.015 m2 siguen siendo supuestos de escenario y deben reemplazarse por la obra propuesta.\n',encoding='utf-8'); print('2.4 actualizado')
if __name__=='__main__': main()
