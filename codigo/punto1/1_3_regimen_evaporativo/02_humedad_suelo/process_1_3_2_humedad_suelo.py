"""ERA5-Land soil-water processing for section 1.3.2.

Reads the downloaded archive without changing it. Results are basin-area weighted
with intersections made afresh from the Racarumi polygon, not from ETo weights.
"""
from __future__ import annotations
import hashlib, json, tempfile, zipfile
from pathlib import Path
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from shapely.geometry import box

ROOT=next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
ZIP=ROOT/'datos/punto1/originales/era5land_humedad_suelo/ERA5_Land_Racarumi_Humedad_Suelo_1981_2023.zip'
GPKG=ROOT/'datos'/'punto1'/'originales'/'tarea1_minimos'/'PE_200907_catchment.gpkg'
OUT=ROOT/'datos/punto1/procesados/1_3_regimen_evaporativo'; TAB=ROOT/'productos/punto1/1_3_regimen_evaporativo/tablas'; FIG=ROOT/'productos/punto1/1_3_regimen_evaporativo/figuras'; META=ROOT/'datos/punto1/metadatos'; ANN=ROOT/'anexos/punto1/1_3_regimen_evaporativo'
CLIM=TAB/'1_3_climatologia_mensual_PL_PI_ETo_preliminar_90_1264pct.csv'
SERIES=OUT/'1_3_serie_mensual_PL_PI_ETo_preliminar_90_1264pct.csv'
for p in [OUT,TAB,FIG,META,ANN]:p.mkdir(parents=True,exist_ok=True)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(fig,name):
 for ext in ['png','pdf']:fig.savefig(FIG/f'{name}.{ext}',dpi=180)
 plt.close(fig)

# ZIP integrity and temporary read-only NetCDF extraction.
if not ZIP.is_file():
 raise FileNotFoundError(f"Entrada no incluida: {ZIP.relative_to(ROOT)}")
with zipfile.ZipFile(ZIP) as z:
 bad=z.testzip(); nc=[i for i in z.infolist() if i.filename.lower().endswith('.nc')]
 if bad or len(nc)!=1:raise RuntimeError(f'ZIP inválido: bad={bad}, netcdf={len(nc)}')
 with tempfile.NamedTemporaryFile(suffix='.nc',delete=False) as f:f.write(z.read(nc[0])); tmp=Path(f.name)
try:
 ds=xr.open_dataset(tmp)
 required=['swvl1','swvl2','swvl3','swvl4']
 if sorted(ds.data_vars)!=required:raise RuntimeError(f'Variables inesperadas: {list(ds.data_vars)}')
 ds=ds.sel(valid_time=slice('1981-01-01','2023-08-01'))
 if ds.sizes['valid_time']!=512:raise RuntimeError(f'Se esperaban 512 meses y hay {ds.sizes["valid_time"]}')
 time=pd.DatetimeIndex(ds.valid_time.values)
 # Check monthly continuity independently of the unequal calendar month lengths.
 continuous=bool(np.all(np.diff(time.year*12+time.month)==1))
 lat=np.asarray(ds.latitude.values); lon=np.asarray(ds.longitude.values)
 gridstep_lat=float(np.median(np.abs(np.diff(lat))));gridstep_lon=float(np.median(np.abs(np.diff(lon))))
 # Construct full 0.1-degree grid cells around coordinates, then intersect basin in equal-area CRS.
 cells=[]
 for iy,y in enumerate(lat):
  for ix,x in enumerate(lon):cells.append({'iy':iy,'ix':ix,'latitude':float(y),'longitude':float(x),'geometry':box(x-gridstep_lon/2,y-gridstep_lat/2,x+gridstep_lon/2,y+gridstep_lat/2)})
 grid=gpd.GeoDataFrame(cells,crs='EPSG:4326'); basin=gpd.read_file(GPKG).to_crs(4326)
 inter=gpd.overlay(grid,basin[['geometry']],how='intersection').to_crs('EPSG:6933');inter['intersection_m2']=inter.area
 weights=inter.groupby(['iy','ix','latitude','longitude'],as_index=False).intersection_m2.sum();weights['weight']=weights.intersection_m2/weights.intersection_m2.sum()
 basin_area=float(basin.to_crs('EPSG:6933').area.sum()); coverage=float(weights.intersection_m2.sum()/basin_area)
 weights.to_csv(TAB/'1_3_2_pesos_espaciales_humedad_suelo_interseccion.csv',index=False)
 # Flatten only intersecting cells; calculate per-layer and root-zone means each month.
 w=weights.sort_values(['iy','ix']); iy=w.iy.to_numpy(dtype=int);ix=w.ix.to_numpy(dtype=int);ww=w.weight.to_numpy()
 result=pd.DataFrame({'date':time})
 qc={}
 for v in required:
  vals=np.asarray(ds[v].values)[:,iy,ix].astype(float); miss=np.isnan(vals)
  qc[v]={'units':ds[v].attrs.get('units'),'min':float(np.nanmin(vals)),'max':float(np.nanmax(vals)),'missing_values':int(miss.sum()),'total_values':int(vals.size),'physically_admissible_0_1':bool(np.nanmin(vals)>=0 and np.nanmax(vals)<=1)}
  result[v+'_m3_m3']=np.nansum(vals*ww,axis=1)
 result['theta_rz_0_100m3_m3']=.07*result.swvl1_m3_m3+.21*result.swvl2_m3_m3+.72*result.swvl3_m3_m3
 result['theta_0_289m3_m3']=(100/289)*result.theta_rz_0_100m3_m3+(189/289)*result.swvl4_m3_m3
 result['difference_deep_minus_rz_m3_m3']=result.theta_0_289m3_m3-result.theta_rz_0_100m3_m3
 result['calendar_month']=result.date.dt.month; result.to_csv(OUT/'1_3_2_humedad_suelo_mensual_ponderada_198101_202308.csv',index=False)
 climat=result.groupby('calendar_month',as_index=False).agg({c:'mean' for c in result.columns if c.endswith('m3_m3')});climat['mes']=['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];climat.to_csv(TAB/'1_3_2_climatologia_humedad_suelo_ponderada.csv',index=False)
 # Join without rebuilding existing P/ETo calculations.
 hydro=pd.read_csv(SERIES,parse_dates=['date'])[['date','PL_mm_mes','PI_mm_mes','ETo_mm_mes']];join=result.merge(hydro,on='date',how='left')
 corr=join[['theta_rz_0_100m3_m3','PL_mm_mes','PI_mm_mes','ETo_mm_mes']].corr(method='pearson')
 lags=[]
 for lag in range(-6,7):
  # positive lag means soil moisture is correlated to P from prior months
  lags.append({'lag_soil_after_P_months':lag,'correlation_PL':join.theta_rz_0_100m3_m3.corr(join.PL_mm_mes.shift(lag)),'correlation_PI':join.theta_rz_0_100m3_m3.corr(join.PI_mm_mes.shift(lag))})
 pd.DataFrame(lags).to_csv(TAB/'1_3_2_desfase_humedad_con_precipitacion.csv',index=False); corr.to_csv(TAB/'1_3_2_correlaciones_humedad_P_ETo.csv')
 # No calculation of FE is possible: only a machine-readable hand-off requirement.
 fe={'status':'PENDIENTE POR DATOS','formula':'FE = lambda_ET / Rn_superficial','available':'theta_rz monthly area-weighted','missing':['ET real mensual coincidente','radiación neta superficial real coincidente'],'prohibition':'No sustituir FE por ET/ETo ni usar Rn de pasto FAO-56. No se define umbral crítico de humedad.'}
 (ANN/'1_3_2_preparacion_FE_pendiente.json').write_text(json.dumps(fe,ensure_ascii=False,indent=2),encoding='utf8')
 qc.update({'source_zip_sha256':digest(ZIP),'netcdf_member':nc[0].filename,'zip_test':'passed','analysis_period':'1981-01 to 2023-08','n_months':512,'temporal_continuity':continuous,'grid_shape':[int(len(lat)),int(len(lon))],'resolution_degrees':[gridstep_lat,gridstep_lon],'bounds_W_S_E_N':[float(lon.min()),float(lat.min()),float(lon.max()),float(lat.max())],'intersecting_cells':int(len(weights)),'basin_coverage_fraction':coverage,'polygon_crs':'EPSG:4326','method':'intersection of 0.1° cells with basin polygon; areas calculated EPSG:6933','root_zone':'0–100 cm: 0.07 swvl1 + 0.21 swvl2 + 0.72 swvl3; not an observed rooting depth','deep_sensitivity':'0–289 cm: (100/289)*theta_0_100 + (189/289)*swvl4'})
 (META/'1_3_2_metadatos_y_control_calidad_humedad_suelo.json').write_text(json.dumps(qc,ensure_ascii=False,indent=2),encoding='utf8')
 # Dashboard-ready figures.
 plt.style.use('seaborn-v0_8-whitegrid')
 fig,ax=plt.subplots(figsize=(10,4));ax.plot(result.date,result.theta_rz_0_100m3_m3,color='#1b6ca8');ax.set(title='Racarumi: humedad volumétrica radicular (0–100 cm)',ylabel='m³/m³',xlabel='Fecha');save(fig,'1_3_2_serie_historica_humedad_radicular')
 fig,ax=plt.subplots(figsize=(9,4));ax.plot(climat.mes,climat.theta_rz_0_100m3_m3,'o-',label='0–100 cm');ax.plot(climat.mes,climat.theta_0_289m3_m3,'o-',label='0–289 cm (sensibilidad)');ax.set(title='Ciclo anual de humedad ponderada por cuenca',ylabel='m³/m³');ax.legend();save(fig,'1_3_2_ciclo_anual_humedad_suelo')
 fig,ax=plt.subplots(figsize=(9,4));
 for v,label in [('swvl1_m3_m3','swvl1: 0–7 cm'),('swvl2_m3_m3','swvl2: 7–28 cm'),('swvl3_m3_m3','swvl3: 28–100 cm'),('swvl4_m3_m3','swvl4: 100–289 cm')]:ax.plot(climat.mes,climat[v],'o-',label=label)
 ax.set(title='Ciclo anual por capa de suelo',ylabel='m³/m³');ax.legend(ncol=2,fontsize=8);save(fig,'1_3_2_ciclo_anual_cuatro_capas')
 for col,name,label in [('PL_mm_mes','1_3_2_humedad_vs_PL','PL (mm/mes)'),('ETo_mm_mes','1_3_2_humedad_vs_ETo','ETo FAO-56 preliminar (mm/mes)')]:
  fig,ax=plt.subplots(figsize=(6,4.5));ax.scatter(join[col],join.theta_rz_0_100m3_m3,s=12,alpha=.55);ax.set(xlabel=label,ylabel='θrz 0–100 cm (m³/m³)',title='Humedad del suelo vs '+label);save(fig,name)
 print(json.dumps({'coverage_fraction':coverage,'qc':qc,'theta_rz_mean':float(result.theta_rz_0_100m3_m3.mean()),'theta_rz_min_month':str(result.loc[result.theta_rz_0_100m3_m3.idxmin(),'date'].date()),'theta_rz_max_month':str(result.loc[result.theta_rz_0_100m3_m3.idxmax(),'date'].date()),'climatology_min_month':str(climat.loc[climat.theta_rz_0_100m3_m3.idxmin(),'mes']),'climatology_max_month':str(climat.loc[climat.theta_rz_0_100m3_m3.idxmax(),'mes']),'correlation':corr.to_dict(),'lag_peak_PL':max(lags,key=lambda q:abs(q['correlation_PL']) if pd.notna(q['correlation_PL']) else -1)},ensure_ascii=False,indent=2))
finally:
 ds.close();tmp.unlink(missing_ok=True)
