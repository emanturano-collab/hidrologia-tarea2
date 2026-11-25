"""Cierre técnico reproducible del numeral 1.5; no genera interpretación."""
from __future__ import annotations
import hashlib, json
from datetime import date, timedelta
from pathlib import Path
import geopandas as gpd, matplotlib.pyplot as plt, numpy as np, pandas as pd

ROOT=next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir()); DATA=ROOT/'datos/punto1/procesados/1_5_paisaje'; OUT=ROOT/'productos/punto1/1_5_paisaje'
MOD=DATA/'mod16a2gf_bandas_altitudinales_composites_controlado.csv'; INVALID=DATA/'mod16a2gf_bandas_altitudinales_composites_raw.csv'
BASIN_RAW=ROOT/'datos/punto1/mod16a2gf_racarumi_composites_raw.csv'; BASIN_ANNUAL=ROOT/'productos/punto1/punto_1_2_4_mod16_et_anual_hidrologico.csv'
BANDS_CSV=OUT/'1_5_bandas_altitudinales_SRTM.csv'; BANDS_GPKG=DATA/'PE_200907_bandas_altitudinales_SRTM_500m.gpkg'
ETO=OUT/'1_5_eto_fao56_mensual_por_banda.csv'; GLEAM=OUT/'1_5_gleam4_3a_ET_mensual_por_banda.csv'
YEARS=[2002]+list(range(2004,2024)); WINDOWS=[(date(2001,9,1),date(2002,9,1)),(date(2003,9,1),date(2023,9,1))]
def sha(p):
 h=hashlib.sha256();
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def months():
 for a,b in WINDOWS:
  d=a
  while d<b:
   n=(d.replace(day=28)+timedelta(days=4)).replace(day=1);yield d,min(n,b);d=n
def hy(d):return d.year+1 if d.month>=9 else d.year
def aggregate(comp,value='et_mm_composite'):
 rows=[]
 for r in comp.itertuples():
  a,b=date.fromisoformat(r.image_start),date.fromisoformat(r.image_end)
  for s,e in months():
   left,right=max(a,s),min(b,e)
   if left<right:rows.append({'month':s.isoformat(),'hydrological_year':hy(s),'band_id':getattr(r,'band_id',0),'days_covered':(right-left).days,'et_mod16_mm_month':getattr(r,value)*(right-left).days/r.duration_days,'min_coverage_percent':r.valid_coverage_percent})
 p=pd.DataFrame(rows);return p.groupby(['month','hydrological_year','band_id'],as_index=False).agg(days_covered=('days_covered','sum'),et_mod16_mm_month=('et_mod16_mm_month','sum'),min_coverage_percent=('min_coverage_percent','min'))
def main():
 d=pd.read_csv(MOD); base=pd.read_csv(BASIN_RAW); bands=pd.read_csv(BANDS_CSV)
 expected=len(base)*8
 if len(d)!=expected or d.duplicated(['image_start','band_id']).any():raise ValueError(f'MOD16 incompleto/no único: {len(d)} filas; esperadas {expected}')
 if not d.groupby('image_start').band_id.nunique().eq(8).all() or set(d.image_start)!=set(base.image_start):raise ValueError('fechas o bandas MOD16 incompletas')
 if not d.et_scale_factor.eq(.1).all() or not d.source.eq('MODIS/061/MOD16A2GF').all():raise ValueError('factor de escala/fuente inconsistente')
 if d.valid_coverage_percent.min()<95 or d.duration_days.min()<1 or d.duration_days.max()>8:raise ValueError('cobertura o duración inválida')
 m=aggregate(d); m['expected_days']=pd.to_datetime(m.month).dt.days_in_month
 if len(m)!=252*8 or not m.days_covered.eq(m.expected_days).all():raise ValueError('agregación mensual MOD16 incompleta')
 a=m.groupby(['hydrological_year','band_id'],as_index=False).agg(et_mod16_mm_year=('et_mod16_mm_month','sum'),months=('month','count'),min_coverage_percent=('min_coverage_percent','min'))
 if len(a)!=21*8 or not a.months.eq(12).all():raise ValueError('agregación anual MOD16 incompleta')
 # Equivalence check using the same valid-pixel area returned by Earth Engine.
 rb=d.assign(weighted=lambda x:x.et_mm_composite*x.valid_area_m2).groupby('image_start',as_index=False).agg(weighted=('weighted','sum'),valid_area_m2=('valid_area_m2','sum'))
 rb['et_from_bands']=rb.weighted/rb.valid_area_m2; cmp=base.merge(rb,on='image_start');cmp['difference_mm_composite']=cmp.et_from_bands-cmp.et_mm_composite
 basin_comp=cmp[['image_start','image_end','duration_days','et_from_bands','valid_coverage_percent']].rename(columns={'et_from_bands':'et_mm_composite'}); basin_comp['band_id']=0
 basin_month=aggregate(basin_comp); basin_year=basin_month.groupby('hydrological_year',as_index=False).agg(et_from_bands_mm_year=('et_mod16_mm_month','sum'))
 old=pd.read_csv(BASIN_ANNUAL); annual_cmp=old.merge(basin_year,on='hydrological_year');annual_cmp['difference_mm_year']=annual_cmp.et_from_bands_mm_year-annual_cmp.et_mod16_mm_year;annual_cmp['difference_percent']=100*annual_cmp.difference_mm_year/annual_cmp.et_mod16_mm_year
 if annual_cmp.difference_percent.abs().max()>1:raise ValueError('MOD16 por bandas difiere >1% de la serie de cuenca')
 eto=pd.read_csv(ETO); gl=pd.read_csv(GLEAM); combined=eto.merge(gl,on=['month','hydrological_year','band_id']).merge(m[['month','hydrological_year','band_id','et_mod16_mm_month']],on=['month','hydrological_year','band_id'])
 if len(combined)!=252*8:raise ValueError('productos no son temporalmente comparables')
 annual=combined.groupby(['hydrological_year','band_id'],as_index=False).agg(eto_fao56_mm_year=('eto_fao56_mm_month','sum'),et_gleam_mm_year=('et_gleam_mm_month','sum'),et_mod16_mm_year=('et_mod16_mm_month','sum'),months=('month','count'))
 summary=annual.groupby('band_id',as_index=False).agg(eto_fao56_mean_mm_year=('eto_fao56_mm_year','mean'),gleam_mean_mm_year=('et_gleam_mm_year','mean'),mod16_mean_mm_year=('et_mod16_mm_year','mean'),years=('hydrological_year','count')).merge(bands,on='band_id')
 area_ref=2363.302;area_srtm=bands.area_km2_utm17s.sum();area=pd.DataFrame([{'area_srtm_utm17s_km2':area_srtm,'area_reference_km2':area_ref,'difference_km2':area_srtm-area_ref,'difference_percent_reference':100*(area_srtm-area_ref)/area_ref}])
 invalid=pd.read_csv(INVALID); evidence={'file':str(INVALID.relative_to(ROOT)),'sha256':sha(INVALID),'rows':len(invalid),'duplicate_keys':int(invalid.duplicated(['image_start','band_id']).sum()),'unique_keys':int(len(invalid.drop_duplicates(['image_start','band_id']))),'status':'INVALIDADO_NO_USAR','cause':'escritura concurrente de múltiples procesos de extracción'}
 m.to_csv(OUT/'1_5_mod16_ET_mensual_por_banda.csv',index=False);a.to_csv(OUT/'1_5_mod16_ET_anual_hidrologica_por_banda.csv',index=False);combined.to_csv(OUT/'1_5_tabla_mensual_comparativa_por_banda.csv',index=False);annual.to_csv(OUT/'1_5_tabla_anual_comparativa_por_banda.csv',index=False);summary.to_csv(OUT/'1_5_resumen_multianual_gradiente_altitudinal.csv',index=False);cmp.to_csv(OUT/'1_5_control_mod16_compuesto_bandas_vs_cuenca.csv',index=False);annual_cmp.to_csv(OUT/'1_5_control_mod16_anual_bandas_vs_cuenca.csv',index=False);area.to_csv(OUT/'1_5_control_area_srtm_vs_referencia.csv',index=False)
 (OUT/'1_5_evidencia_csv_mod16_invalidado.json').write_text(json.dumps(evidence,indent=2),encoding='utf-8')
 qc={'status':'VALIDADO','mod16_rows':len(d),'mod16_composites':d.image_start.nunique(),'duplicate_keys':0,'bands':8,'scale_factor':.1,'units':'MOD16 ET: mm/composite -> mm/month -> mm/year; ETo/GLEAM: mm/month -> mm/year','minimum_mod16_coverage_percent':float(d.valid_coverage_percent.min()),'months':252,'hydrological_years':YEARS,'mean_mod16_basin_previous_mm_year':float(old.et_mod16_mm_year.mean()),'mean_mod16_from_bands_mm_year':float(annual_cmp.et_from_bands_mm_year.mean()),'maximum_absolute_annual_difference_percent':float(annual_cmp.difference_percent.abs().max()),'area_srtm_km2':area_srtm,'area_reference_km2':area_ref}
 (OUT/'1_5_control_calidad_integral.json').write_text(json.dumps(qc,indent=2),encoding='utf-8')
 g=gpd.read_file(BANDS_GPKG).merge(bands[['band_id','elev_mean_srtm_m']],on='band_id');fig,ax=plt.subplots(figsize=(7,7));g.plot(column='elev_mean_srtm_m',cmap='terrain',legend=True,ax=ax,edgecolor='black',linewidth=.35);ax.set(title='PE_200907: bandas altitudinales SRTM',xlabel='Longitud',ylabel='Latitud');fig.tight_layout();fig.savefig(OUT/'1_5_mapa_bandas_altitudinales.png',dpi=220);plt.close(fig)
 fig,ax=plt.subplots(figsize=(8,5));x=summary.elev_mean_srtm_m;ax.plot(x,summary.eto_fao56_mean_mm_year,'o-',label='ETo FAO-56');ax.plot(x,summary.gleam_mean_mm_year,'o-',label='GLEAM4.3a');ax.plot(x,summary.mod16_mean_mm_year,'o-',label='MOD16A2GF');ax.set(xlabel='Elevación media SRTM de banda (m)',ylabel='Promedio 21 AH (mm/año)',title='Series por banda altitudinal');ax.grid(alpha=.3);ax.legend();fig.tight_layout();fig.savefig(OUT/'1_5_gradiente_multianual_productos.png',dpi=220);plt.close(fig)
 fig,axs=plt.subplots(3,1,figsize=(9,10),sharex=True);names=[('eto_fao56_mm_month','ETo FAO-56'),('et_gleam_mm_month','GLEAM4.3a'),('et_mod16_mm_month','MOD16A2GF')]
 combined['calendar_month']=pd.to_datetime(combined.month).dt.month
 for ax,(col,name) in zip(axs,names):
  c=combined.groupby(['calendar_month','band_id'])[col].mean().unstack();c.plot(ax=ax,legend=False);ax.set(ylabel='mm/mes',title=name);ax.grid(alpha=.25)
 axs[-1].set(xlabel='Mes',xticks=range(1,13));axs[0].legend([f'B{v}' for v in sorted(combined.band_id.unique())],ncol=4,fontsize=7);fig.tight_layout();fig.savefig(OUT/'1_5_climatologia_mensual_por_banda.png',dpi=220);plt.close(fig)
 (OUT/'1_5_metodologia_tecnica.md').write_text('# Numeral 1.5 — registro técnico\n\nBandas SRTM de 500 m; áreas en EPSG:32717. ETo FAO-56 calculada por celda y ponderada por intersección. GLEAM ponderado con su grilla 0,1°. MOD16 extraído por banda en proyección nativa, escala 500 m, factor 0,1; compuestos repartidos por días de solapamiento. Periodo común: AH2002 y AH2004–AH2023. Este archivo registra procedimientos y controles; no contiene interpretación ni conclusiones.\n',encoding='utf-8')
 print(json.dumps(qc,indent=2))
if __name__=='__main__':main()
