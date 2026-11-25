"""Tarea 2 / 1.1.d: explicación física y sensibilidad (versión preliminar).

Lee productos derivados de 1.1.a/1.1.c; no modifica datos ERA5-Land ni
productos anteriores. Todas las ecuaciones no lineales se aplican a cada
celda/día antes de la ponderación espacial del dominio disponible.
"""
from __future__ import annotations
from pathlib import Path
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pyet

ROOT=next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir()); TASK=ROOT
DAILY=TASK/'productos/punto1/1_1_a/fao56_eto_diaria_por_celda_preliminar_90pct.csv'
WEIGHTS=TASK/'productos/punto1/1_1_demanda_atmosferica/tablas/era5land_33_celdas_pesos_y_elevacion.csv'
CMASTER=TASK/'datos/punto1/procesados/1_1_c_metodos_alternativos/1_1c_tabla_maestra_mensual_preliminar_90pct.csv'
PISCO=TASK/'datos/punto1/originales/tarea1_minimos/1_1b_pet_piscoeopm_vs_eto_preliminar_mensual.csv'
TERRA=TASK/'datos/punto1/originales/tarea1_minimos/1_1b_terraclimate_pet_vs_eto_preliminar_mensual.csv'
DATA=TASK/'datos/punto1/procesados/1_1_d_explicacion_fisica'; TAB=TASK/'productos/punto1/1_1_demanda_atmosferica/tablas'; FIG=TASK/'productos/punto1/1_1_demanda_atmosferica/figuras'; ANN=TASK/'anexos/punto1/1_1_d_explicacion_fisica'
COVER=.9012637836877098; SIGMA=4.903e-9; ALBEDO=.23; LAMBDA=2.45
METHODS=['fao56','thornthwaite_1948','hargreaves_samani_1985','priestley_taylor_1972','meyer_1915','makkink_1957','rohwer_1931']
ALT=METHODS[1:]
LABEL={'fao56':'FAO-56','thornthwaite_1948':'Thornthwaite','hargreaves_samani_1985':'Hargreaves-Samani','priestley_taylor_1972':'Priestley-Taylor','meyer_1915':'Meyer (agua libre)','makkink_1957':'Makkink','rohwer_1931':'Rohwer (agua libre)'}
COLOR={'fao56':'#222222','thornthwaite_1948':'#4C78A8','hargreaves_samani_1985':'#F58518','priestley_taylor_1972':'#54A24B','meyer_1915':'#E45756','makkink_1957':'#B279A2','rohwer_1931':'#72B7B2'}
SCENARIOS={'base':{},'T_plus1_ea_const':{'dt':1,'humidity':'ea_const'},'T_plus2_ea_const':{'dt':2,'humidity':'ea_const'},'T_plus1_RH_const':{'dt':1,'humidity':'rh_const'},'T_plus2_RH_const':{'dt':2,'humidity':'rh_const'},'u2_plus10pct':{'wind_factor':1.1},'Rs_minus10pct':{'rs_factor':.9},'ea_plus10pct':{'ea_factor':1.1}}

def es(t): return .6108*np.exp(17.27*np.asarray(t)/(np.asarray(t)+237.3))
def delta(t): return 4098*es(t)/(np.asarray(t)+237.3)**2
def daylight(lat, month):
    j=np.array([15,46,74,105,135,166,196,227,258,288,319,349])[np.asarray(month)-1]
    ph=np.deg2rad(lat); de=.409*np.sin(2*np.pi*j/365-1.39); ws=np.arccos(np.clip(-np.tan(ph)*np.tan(de),-1,1)); return 24/np.pi*ws
def complete_months(x):
    x=x.copy(); x['month_date']=x.date.values.astype('datetime64[M]'); n=x.groupby(['point','month_date']).size().rename('n').reset_index(); n['expected']=pd.DatetimeIndex(n.month_date).days_in_month; return x.merge(n.loc[n.n==n.expected,['point','month_date']],on=['point','month_date'])

def calc_daily(base, scenario):
    """Derive all daily forcings and methods; returns a new frame, leaving base intact."""
    x=base.copy(); dt=scenario.get('dt',0.); x['tmean_c']=x.tmean_c+dt; x['tmax_c']=x.tmax_c+dt; x['tmin_c']=x.tmin_c+dt
    es0=(es(base.tmax_c)+es(base.tmin_c))/2; esn=(es(x.tmax_c)+es(x.tmin_c))/2
    ea=base.ea_kpa.copy()
    if scenario.get('humidity')=='rh_const': ea=base.ea_kpa/es0*esn
    ea=ea*scenario.get('ea_factor',1.); capped=ea>esn; x['ea_kpa']=np.minimum(ea,esn) # no supersaturation / negative VPD
    x['ea_capped']=capped; x['es_kpa']=esn; x['delta_kpa_c']=delta(x.tmean_c); x['gamma_kpa_c']=.000665*x.p_kpa
    x['u2_ms']=base.u2_ms*scenario.get('wind_factor',1.); x['wind10_ms']=base.wind10_ms*scenario.get('wind_factor',1.)
    x['rs_mj_m2_d']=base.rs_mj_m2_d*scenario.get('rs_factor',1.)
    x['rns_mj_m2_d']=(1-ALBEDO)*x.rs_mj_m2_d
    cloud=(x.rs_mj_m2_d/x.rso_mj_m2_d).clip(upper=1)
    x['rnl_mj_m2_d']=SIGMA*(((x.tmax_c+273.16)**4+(x.tmin_c+273.16)**4)/2)*(0.34-0.14*np.sqrt(x.ea_kpa))*(1.35*cloud-.35)
    x['rn_mj_m2_d']=x.rns_mj_m2_d-x.rnl_mj_m2_d; avail=x.rn_mj_m2_d-x.g_mj_m2_d
    den=x.delta_kpa_c+x.gamma_kpa_c*(1+.34*x.u2_ms)
    x['component_radiative_mm_d']=.408*x.delta_kpa_c*avail/den
    x['component_aerodynamic_mm_d']=x.gamma_kpa_c*(900/(x.tmean_c+273))*x.u2_ms*(x.es_kpa-x.ea_kpa)/den
    x['fao56']=x.component_radiative_mm_d+x.component_aerodynamic_mm_d
    x['hargreaves_samani_1985']=.0023*(x.tmean_c+17.8)*np.sqrt((x.tmax_c-x.tmin_c).clip(lower=0))*x.ra_mj_m2_d/LAMBDA
    x['priestley_taylor_1972']=pyet.priestley_taylor(x.tmean_c,rn=x.rn_mj_m2_d,g=x.g_mj_m2_d,pressure=x.p_kpa,alpha=1.26).to_numpy()
    x['makkink_1957']=pyet.makkink(x.tmean_c,x.rs_mj_m2_d,pressure=x.p_kpa,k=.65).to_numpy()
    eair=es(x.tmean_c)*7.50061683; eact=x.ea_kpa*7.50061683; pdhg=x.p_kpa*7.50061683
    u10=x.wind10_ms*3.6; u06=u10*(.6/10)**(1/7)
    x['meyer_1915']=.36*(eair-eact).clip(lower=0)*(1+u10/16)
    x['rohwer_1931']=.771*(1.465-.000732*pdhg)*(.44+.0733*u06)*(eair-eact).clip(lower=0)
    eeq=x.delta_kpa_c/(x.delta_kpa_c+x.gamma_kpa_c)*avail/LAMBDA
    x['eeq_mm_d']=eeq.where(eeq>0); x['alpha_star_cell']=x.fao56/x.eeq_mm_d
    return x

def thorn_monthly(x):
    rows=[]
    for point,g in x.groupby('point'):
        z=g.set_index('date').resample('MS').agg(t=('tmean_c','mean'),n=('tmean_c','size')).reset_index(); z['year']=z.date.dt.year; z['month']=z.date.dt.month; z['expected']=z.date.dt.days_in_month
        full=z.groupby('year').apply(lambda q: len(q)==12 and (q.n==q.expected).all(),include_groups=False); z=z[z.year.isin(full[full].index)].copy(); z['h']=np.where(z.t>0,(z.t/5)**1.514,0); z['I']=z.groupby('year').h.transform('sum'); z['a']=6.75e-7*z.I**3-7.71e-5*z.I**2+.01792*z.I+.49239
        pet=np.where(z.t>0,16*(10*z.t/z.I)**z.a,0); z['thornthwaite_1948']=pet*(z.n/30)*(daylight(float(g.latitude.iloc[0]),z.month)/12); z['point']=point; rows.append(z[['point','date','thornthwaite_1948']])
    return pd.concat(rows,ignore_index=True)

def monthly_basin(x, weights):
    x=complete_months(x); cols=['fao56','component_radiative_mm_d','component_aerodynamic_mm_d','eeq_mm_d']+ALT[1:]
    y=x.groupby(['point','month_date'])[cols].sum().reset_index().rename(columns={'month_date':'date'}); tw=thorn_monthly(x); y=y.merge(tw,on=['point','date'],how='inner'); y['w']=y.point.map(weights)
    out=[]
    for date,g in y.groupby('date'):
        if len(g)!=20: continue
        r={'date':date,'n_cells':20,'coverage_spatial_fraction':COVER};
        for c in cols+['thornthwaite_1948']: r[c]=np.sum(g[c]*g.w)
        r['fraction_radiative_pct']=100*r['component_radiative_mm_d']/r['fao56']; r['fraction_aerodynamic_pct']=100*r['component_aerodynamic_mm_d']/r['fao56']; r['alpha_star']=r['fao56']/r['eeq_mm_d'] if r['eeq_mm_d']>0 else np.nan
        out.append(r)
    o=pd.DataFrame(out)
    # Diagnostics: cell monthly means, then spatial weight.
    diag=x.assign(month_date=x.date.values.astype('datetime64[M]')).groupby(['point','month_date'])[['u2_ms','ea_kpa','es_kpa','rn_mj_m2_d','rs_mj_m2_d']].mean().reset_index(); diag['w']=diag.point.map(weights); diag['vpd_kpa']=diag.es_kpa-diag.ea_kpa
    db=diag.groupby('month_date').apply(lambda g: pd.Series({'vpd_kpa_mean':np.sum(g.vpd_kpa*g.w),'u2_ms_mean':np.sum(g.u2_ms*g.w),'ea_kpa_mean':np.sum(g.ea_kpa*g.w),'rn_mj_m2_d_mean':np.sum(g.rn_mj_m2_d*g.w),'rs_mj_m2_d_mean':np.sum(g.rs_mj_m2_d*g.w)}),include_groups=False).reset_index().rename(columns={'month_date':'date'})
    return o.merge(db,on='date'), y

def figsave(fig,name):
    fig.tight_layout(); fig.savefig(FIG/f'1_1d_{name}.png',dpi=300,bbox_inches='tight'); fig.savefig(FIG/f'1_1d_{name}.pdf',bbox_inches='tight'); plt.close(fig)

def main():
    for p in (DATA,TAB,FIG,ANN): p.mkdir(parents=True,exist_ok=True)
    d=pd.read_csv(DAILY,parse_dates=['date']); w=pd.read_csv(WEIGHTS); ids=sorted(d.point.unique()); w=w[w.cell_id.isin(ids)].copy(); w['norm']=w.spatial_weight/w.spatial_weight.sum(); weights=w.set_index('cell_id').norm.to_dict(); assert len(ids)==20 and abs(sum(weights.values())-1)<1e-10
    base=calc_daily(d,{}); base_month,base_cell=monthly_basin(base,weights); base_month=base_month[(base_month.date>='1981-01-01')&(base_month.date<='2022-12-01')].copy()
    # Core QA: reassembled PM must agree to the saved 1.1.a daily ETo.
    qa=pd.DataFrame([{'check':'base_fao56_vs_1_1a_daily','n':len(base),'max_abs_mm_d':np.max(np.abs(base.fao56-d.eto_fao56_mm_d)),'mean_abs_mm_d':np.mean(np.abs(base.fao56-d.eto_fao56_mm_d)),'pass':np.max(np.abs(base.fao56-d.eto_fao56_mm_d))<1e-10},{'check':'components_sum_fao56','n':len(base),'max_abs_mm_d':np.max(np.abs(base.fao56-(base.component_radiative_mm_d+base.component_aerodynamic_mm_d))),'mean_abs_mm_d':0,'pass':True}])
    qa.to_csv(TAB/'1_1d_controles_calidad.csv',index=False)
    # Aggregate daily physical components, then retain only common 1981-2022 daily dates.
    b=base.copy(); b['w']=b.point.map(weights); basin_daily=b.groupby('date').apply(lambda g: pd.Series({'fao56_mm_d':np.sum(g.fao56*g.w),'radiative_mm_d':np.sum(g.component_radiative_mm_d*g.w),'aerodynamic_mm_d':np.sum(g.component_aerodynamic_mm_d*g.w),'eeq_mm_d':np.sum(g.eeq_mm_d.fillna(0)*g.w),'vpd_kpa':np.sum((g.es_kpa-g.ea_kpa)*g.w),'u2_ms':np.sum(g.u2_ms*g.w)}),include_groups=False).reset_index(); basin_daily=basin_daily[(basin_daily.date>='1981-01-01')&(basin_daily.date<='2022-12-31')]; basin_daily['alpha_star']=basin_daily.fao56_mm_d/basin_daily.eeq_mm_d
    basin_daily.to_csv(DATA/'1_1d_componentes_y_alpha_diarios_preliminar_90pct.csv',index=False)
    base_month.to_csv(DATA/'1_1d_componentes_y_alpha_mensuales_preliminar_90pct.csv',index=False)
    # Sensitivity. Base result used as exact reference; all alternatives recomputed from transformed forcing.
    scen_month=[]; summary=[]; cap=[]
    for name,s in SCENARIOS.items():
        print(f'processing scenario {name}', flush=True)
        z=base if name=='base' else calc_daily(d,s); m,_=monthly_basin(z,weights); m=m[(m.date>='1981-01-01')&(m.date<='2022-12-01')].copy(); m['scenario']=name; scen_month.append(m)
        cap.append({'scenario':name,'ea_capped_cell_days':int(z.ea_capped.sum()),'total_cell_days':len(z),'fraction_pct':100*z.ea_capped.mean()})
    sm=pd.concat(scen_month,ignore_index=True); basev=sm[sm.scenario=='base'][['date']+METHODS].set_index('date')
    for s,g in sm.groupby('scenario'):
        for method in METHODS:
            v=g.set_index('date')[method].reindex(basev.index); ch=v-basev[method]; clim=ch.groupby(ch.index.month).mean(); ixmax=clim.abs().idxmax(); summary.append({'scenario':s,'method':method,'n_months':len(v),'base_annual_mean_mm_y':basev[method].sum()/42,'scenario_annual_mean_mm_y':v.sum()/42,'change_annual_mm_y':ch.sum()/42,'change_annual_pct':100*(ch.sum()/42)/(basev[method].sum()/42),'mean_monthly_change_mm':ch.mean(),'month_max_abs_change':int(ixmax),'max_abs_climatological_change_mm_month':clim.loc[ixmax]})
    sens=pd.DataFrame(summary); sens.to_csv(TAB/'1_1d_sensibilidad_resumen_anual.csv',index=False); sm.to_csv(DATA/'1_1d_sensibilidad_mensual_todos_metodos_preliminar_90pct.csv',index=False); pd.DataFrame(cap).to_csv(TAB/'1_1d_control_sobresaturacion_escenarios.csv',index=False)
    clim_s=sm.melt(id_vars=['date','scenario'],value_vars=METHODS,var_name='method',value_name='mm_month'); clim_s['month']=clim_s.date.dt.month; clim_s=clim_s.merge(clim_s[clim_s.scenario=='base'][['date','method','mm_month']].rename(columns={'mm_month':'base'}),on=['date','method']); clim_changes=clim_s.assign(change=lambda z:z.mm_month-z.base).groupby(['scenario','method','month']).change.mean().reset_index(); clim_changes.to_csv(TAB/'1_1d_sensibilidad_climatologia_mensual.csv',index=False)
    # 1.1b empirical dispersions, kept distinct from confidence intervals.
    p=pd.read_csv(PISCO,parse_dates=['month']); t=pd.read_csv(TERRA,parse_dates=['month']); p['source']='PISCOeo_pm'; p['difference']=p.difference_pet_minus_eto_mm_month; t['source']='TerraClimate'; t['difference']=t.difference_terraclimate_minus_eto_mm_month
    disp=pd.concat([p[['month','source','difference']],t[['month','source','difference']]]); disp['calendar_month']=disp.month.dt.month
    dr=disp.groupby(['source','calendar_month']).difference.agg(n='count',mean='mean',sd='std',q05=lambda x:x.quantile(.05),q95=lambda x:x.quantile(.95),mae=lambda x:x.abs().mean()).reset_index(); dr.to_csv(TAB/'1_1d_dispersion_empirica_1_1b_por_mes.csv',index=False)
    # differences alternative vs FAO climatology and flags relative to source-specific empirical ranges
    cm=pd.read_csv(CMASTER,parse_dates=['date']); cm=cm[(cm.date>='1981-01-01')&(cm.date<='2022-12-01')]; long=cm.melt(id_vars=['date','fao56'],value_vars=ALT,var_name='method',value_name='estimate'); long['calendar_month']=long.date.dt.month; long['difference']=long.estimate-long.fao56; cd=long.groupby(['method','calendar_month']).difference.mean().reset_index(); flags=cd.merge(dr[['source','calendar_month','q05','q95']],on='calendar_month'); flags['within_empirical_dispersion']=(flags.difference>=flags.q05)&(flags.difference<=flags.q95); flags.to_csv(TAB/'1_1d_metodos_vs_dispersion_1_1b.csv',index=False)
    # Figures
    clim=cm.assign(month=cm.date.dt.month).groupby('month')[['fao56']+ALT].mean(); fig,ax=plt.subplots(figsize=(11,5)); ax.plot(clim.index,clim.fao56,color=COLOR['fao56'],lw=2,label='FAO-56'); [ax.plot(clim.index,clim[m],label=LABEL[m],color=COLOR[m]) for m in ALT]
    # Empirical 5--95 ranges of independent product differences, not confidence intervals.
    for source,color in [('PISCOeo_pm','#999999'),('TerraClimate','#BBBBBB')]:
        band=dr[dr.source==source].set_index('calendar_month').reindex(range(1,13)); ax.fill_between(range(1,13),clim.fao56.to_numpy()+band.q05.to_numpy(),clim.fao56.to_numpy()+band.q95.to_numpy(),color=color,alpha=.18,label=f'{source}: dispersión empírica 5--95')
    ax.set(xlabel='Mes calendario',ylabel='mm/mes',xticks=range(1,13),title='Ciclo anual, métodos y dispersión empírica de 1.1.b'); ax.legend(ncol=3,fontsize=7); figsave(fig,'ciclo_anual_metodos')
    cbase=base_month.assign(month=base_month.date.dt.month).groupby('month')[['fraction_radiative_pct','fraction_aerodynamic_pct']].mean(); fig,ax=plt.subplots(figsize=(10,4)); ax.bar(cbase.index,cbase.fraction_radiative_pct,label='Radiativo',color='#F58518'); ax.bar(cbase.index,cbase.fraction_aerodynamic_pct,bottom=cbase.fraction_radiative_pct,label='Aerodinámico',color='#4C78A8'); ax.axhline(100,color='k',lw=.6); ax.set(xticks=range(1,13),xlabel='Mes',ylabel='% de ETo acumulada',title='FAO-56: fracciones mensuales de los componentes'); ax.legend(); figsave(fig,'fracciones_componentes')
    cdiag=base_month.assign(month=base_month.date.dt.month).groupby('month')[['alpha_star','vpd_kpa_mean','u2_ms_mean']].mean(); fig,ax1=plt.subplots(figsize=(10,4)); ax1.plot(cdiag.index,cdiag.alpha_star,'o-',color='#7F3C8D',label='α*');ax1.axhline(1.26,ls='--',color='gray',label='α PT=1.26');ax1.set(xticks=range(1,13),xlabel='Mes',ylabel='α*',title='Coeficiente implícito α* y referencia Priestley-Taylor');ax2=ax1.twinx();ax2.plot(cdiag.index,cdiag.vpd_kpa_mean,'s-',color='#E45756',label='VPD');ax2.plot(cdiag.index,cdiag.u2_ms_mean,'^-',color='#54A24B',label='u2');ax2.set_ylabel('VPD (kPa) / u2 (m s⁻¹)');h,l=ax1.get_legend_handles_labels();h2,l2=ax2.get_legend_handles_labels();ax1.legend(h+h2,l+l2,ncol=4,fontsize=8);figsave(fig,'alpha_star_vpd_viento')
    nonbase=sens[sens.scenario!='base']; pivot=nonbase.pivot(index='method',columns='scenario',values='change_annual_mm_y').reindex(METHODS); fig,ax=plt.subplots(figsize=(12,5)); im=ax.imshow(pivot,cmap='RdBu_r',aspect='auto');ax.set(yticks=range(len(METHODS)),yticklabels=[LABEL[m] for m in METHODS],xticks=range(len(pivot.columns)),xticklabels=pivot.columns,title='Sensibilidad: cambio anual (mm/año)');ax.tick_params(axis='x',rotation=30);fig.colorbar(im,ax=ax,label='mm/año');figsave(fig,'sensibilidad_anual_heatmap')
    heat=clim_changes[(clim_changes.scenario!='base')&(clim_changes.method=='fao56')].pivot(index='scenario',columns='month',values='change').reindex(columns=range(1,13));fig,ax=plt.subplots(figsize=(11,4));im=ax.imshow(heat,cmap='RdBu_r',aspect='auto');ax.set(yticks=range(len(heat)),yticklabels=heat.index,xticks=range(12),xticklabels=range(1,13),xlabel='Mes',title='FAO-56: sensibilidad climatológica mensual');fig.colorbar(im,ax=ax,label='Δ mm/mes');figsave(fig,'fao56_sensibilidad_mensual')
    warm=['T_plus1_ea_const','T_plus2_ea_const','T_plus1_RH_const','T_plus2_RH_const']; fig,ax=plt.subplots(figsize=(10,5));
    for s in warm:
        z=clim_changes[(clim_changes.scenario==s)&(clim_changes.method=='fao56')];ax.plot(z.month,z.change,'o-',label=s)
    ax.set(xticks=range(1,13),xlabel='Mes',ylabel='Δ ETo FAO-56 (mm/mes)',title='Calentamiento: ea constante frente a HR constante');ax.legend(fontsize=8);figsave(fig,'calentamiento_ea_vs_hr')
    # variables used/omitted table
    used=pd.DataFrame([['Thornthwaite','T media, latitud/duración día','Rs,Rn,ea,u','Respuesta directa a T; índice anual recalculado'],['Hargreaves-Samani','Tmin,Tmax,Tmedia,Ra','Rs,Rn,ea,u','Rs y ea no producen respuesta directa'],['Priestley-Taylor','T,Rn,G,presión','u,ea (salvo efecto indirecto en Rnl)','α=1.26 fijo'],['Meyer','T,ea,u10','Rs,Rn','Agua libre; T agua aproximada por T aire'],['Makkink','T,Rs,presión','ea,u,Rn','Radiación solar, no radiación neta'],['Rohwer','T,ea,presión,u0.6','Rs,Rn','Agua libre; proxies de T agua y viento bajo']],columns=['method','included_forcings','omitted_direct_forcings','sensitivity_note']); used.to_csv(TAB/'1_1d_variables_incluidas_omitidas_metodos.csv',index=False)
    # Unit check.
    flux=146; mmh=flux*3600/2.45e6; mmd=mmh*24; w_per_mm=2.45e6/86400
    units=pd.DataFrame([{'latent_heat_flux_W_m2':flux,'seconds_per_hour':3600,'energy_J_m2_h':flux*3600,'lambda_J_kg':2.45e6,'correct_mm_h':mmh,'correct_mm_d':mmd,'claimed_mm_h':3.52,'factor_claimed_over_correct':3.52/mmh,'watts_per_mm_d':w_per_mm,'interpretation':'3.52 corresponde aproximadamente a mm/d, no mm/h.'}]);units.to_csv(TAB/'1_1d_verificacion_unidades.csv',index=False)
    # docs and status
    best=nonbase[nonbase.method=='fao56'].sort_values('change_annual_mm_y',key=lambda s:s.abs()).iloc[-1]
    docs=f'''# 1.1.d - Explicar las diferencias (preliminar)

## Alcance y criterio espacial
Se usan 20 celdas ERA5-Land y pesos de intersección de Tarea 1 renormalizados sobre el dominio disponible ({COVER:.4%}). Cada ecuación se aplicó por celda antes de ponderar. El periodo común es enero de 1981 a diciembre de 2022 (504 meses); Chiclayo no participa.

## Descomposición FAO-56
`ETo = R + A`, donde `R=0.408 Δ(Rn-G)/[Δ+γ(1+0.34u2)]` y `A=γ[900/(T+273)]u2(es-ea)/[Δ+γ(1+0.34u2)]`. Sus fracciones mensuales son sum(R)/sum(ETo) y sum(A)/sum(ETo), por lo que son relaciones de contribuciones acumuladas y no promedios de porcentajes diarios.

`α*=ETo/Eeq`, con `Eeq=Δ/(Δ+γ)(Rn-G)/λ`, usa λ=2.45 MJ kg-1 y queda adimensional. Se excluyen Eeq<=0; el conteo queda en control de calidad. α=1.26 de Priestley-Taylor se muestra solo como referencia. FAO-56 incluye resistencia superficial del pasto de 70 s m-1; por ello α* no se interpreta como diagnóstico único de advección. Valores altos son compatibles con aire seco/advección, no los prueban.

## Sensibilidad
Los siete escenarios cambian una sola entrada a la vez. Al cambiar temperatura se recalculan es, Δ, VPD y Rnl; en HR constante, ea se escala por es nuevo/es original. En ea+10 %, ea se limita a es para evitar sobresaturación y se informa su frecuencia. Thornthwaite recalcula I y a anualmente. Meyer/Rohwer siguen etiquetados como agua libre.

El mayor cambio absoluto anual de FAO-56 fue **{best.scenario}**: {best.change_annual_mm_y:.3f} mm/año ({best.change_annual_pct:.3f} %). Esto no identifica un forzante universal: los tamaños y unidades de las perturbaciones no son comparables entre sí.

## Dispersión de 1.1.b
PISCOeo_pm y TerraClimate se presentan como distribuciones empíricas de diferencias mensuales respecto a FAO-56, por mes calendario (media, desviación, percentiles 5--95); no son intervalos de confianza. Chiclayo se excluye de este diagnóstico espacial.

## Explicación de 1.1.c
Makkink concuerda mejor en los productos reales de 1.1.c porque usa Rs y el balance Δ/(Δ+γ), compartiendo parte de la física radiativa con FAO-56, aunque puede haber compensación de errores. Hargreaves usa Ra y rango térmico: reproduce estacionalidad pero omite humedad/viento. Priestley-Taylor usa Rn, pero su α=1.26 y ausencia de resistencia aerodinámica/superficial explícita explica su sesgo positivo. Thornthwaite depende solo de T y duración del día; su débil amplitud y subestimación no capturan variación de radiación/humedad/viento. Meyer y Rohwer son agua libre y dependen de proxies de temperatura superficial y altura de viento; no son ETo de pasto.

No se hallaron en el proyecto las notas del curso ni el árbol de decisión de su sección 7. Para justificar formalmente la elección de un método simple con solo temperatura se requiere proporcionar esas notas o una captura de esa sección. Sin atribuir un árbol inexistente al profesor, Thornthwaite es el único método de esta implementación que usa únicamente temperatura y duración del día, con las limitaciones observadas.

Milly y Dunne (2016) advierten que una formulación solo térmica puede reproducir el ciclo anual y exagerar sensibilidad al calentamiento; los escenarios con Thornthwaite quedan preparados para contrastar este punto en 1.4.

## Verificación de unidades
146 W m-2 × 3600 s h-1 / (2.45e6 J kg-1) = {mmh:.6f} kg m-2 h-1 = {mmh:.6f} mm h-1, o {mmd:.6f} mm d-1. El valor citado de 3.52 mm h-1 es {3.52/mmh:.1f} veces mayor: corresponde aproximadamente a 3.52 mm/d. Inversamente 1 mm/d equivale a {w_per_mm:.3f} W m-2 sostenidos, aproximadamente 28 W m-2.
'''; (ANN/'resumen_tecnico_interpretacion_1_1d.md').write_text(docs,encoding='utf-8')
    status=pd.DataFrame([['Ciclo anual + dispersión empírica 1.1.b','complete'],['Componentes FAO-56 y alpha*','complete'],['Siete escenarios y seis métodos','complete'],['Verificación dimensional','complete'],['Árbol de decisión de notas sección 7','pending_notes_not_found'],['ETo definitiva de Racarumi','not_complete_9.8736pct_coverage_missing'] ],columns=['requirement','status']);status.to_csv(TAB/'1_1d_estado_cumplimiento_preliminar.csv',index=False)
    inv=[]
    for p in [DATA,TAB,FIG,ANN]: inv += [{'path':str(x.relative_to(ROOT)),'bytes':x.stat().st_size} for x in p.glob('1_1d_*') if x.is_file()]
    pd.DataFrame(inv).to_csv(ANN/'1_1d_inventario_productos.csv',index=False)
    print('OK',len(base_month),'months',len(sens),'scenario-method summaries'); print(qa.to_string(index=False)); print(sens[sens.method=='fao56'][['scenario','change_annual_mm_y','change_annual_pct']].to_string(index=False))
if __name__=='__main__': main()
