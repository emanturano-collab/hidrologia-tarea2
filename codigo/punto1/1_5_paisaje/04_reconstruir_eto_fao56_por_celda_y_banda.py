"""Reconstruye ETo FAO-56 espacial: 25 ZIP CDS + 8 series P1--P8 validadas."""
from __future__ import annotations
import importlib.util, json
from pathlib import Path
import geopandas as gpd, numpy as np, pandas as pd
from shapely.geometry import box

ROOT=next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
SRC=ROOT/'codigo/punto1/1_1_demanda_atmosferica/1_1_a_fao56/run_fao56_1_1a.py'
ZIPDIR=ROOT/'datos/punto1/originales/era5land_cds_25_pendientes'
MAN=ROOT/'datos/punto1/metadatos/era5land_25_celdas_manifest.csv'
ELEV=ROOT/'datos/punto1/originales/tarea1_minimos/PE_200907_ERA5Land_cells_SRTM_elevation.csv'
P_MONTH=ROOT/'datos/punto1/procesados/1_1_a_fao56/fao56_eto_mensual_por_punto_validado.csv'
BANDS=ROOT/'datos/punto1/procesados/1_5_paisaje/PE_200907_bandas_altitudinales_SRTM_500m.gpkg'
DATA=ROOT/'datos/punto1/procesados/1_5_paisaje'; OUT=ROOT/'productos/punto1/1_5_paisaje'
VALID_HY={2002,*range(2004,2024)}
def key(lat,lon):return f'{round(float(lat),3):.3f},{round(float(lon),3):.3f}'
def hy(t):return t.year+1 if t.month>=9 else t.year
def load_fao():
    spec=importlib.util.spec_from_file_location('fao_source',SRC); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
def main():
    fao=load_fao(); elev=pd.read_csv(ELEV); manifest=pd.read_csv(MAN)
    if len(elev)!=33 or not manifest.status.eq('VALIDADA').all():raise ValueError('No están disponibles las 33 celdas requeridas')
    elev['cell_key']=[key(a,b) for a,b in zip(elev.latitude,elev.longitude)]
    # Existing P1-P8 output is reused only because its raw ZIP archive is absent;
    # provenance remains in the annex and values are not recomputed or altered.
    p=pd.read_csv(P_MONTH,parse_dates=['month']); p['cell_id']=p.point
    # The validated P1--P8 monthly archive retains latitude but not longitude;
    # the original calculation script records the exact approved coordinates.
    p['cell_key']=[key(*fao.EXPECTED[name]) for name in p.point]
    p=p[['month','cell_id','cell_key','eto_from_daily_mm']].rename(columns={'eto_from_daily_mm':'eto_fao56_mm_month'})
    chunks=[p]
    for r in manifest.itertuples():
        z=ZIPDIR/r.filename
        if not z.exists():raise FileNotFoundError(z)
        e=elev.loc[elev.cell_key==key(r.requested_latitude,r.requested_longitude)]
        if len(e)!=1:raise ValueError(f'{r.cell_id}: elevación no asignable')
        q=e.iloc[0]; hourly,_,_=fao.read_zip_netcdf(z)
        d=fao.fao56_daily(r.cell_id,hourly,float(q.dem_mean_elevation_m),float(q.latitude))
        m=d.set_index('date').eto_fao56_mm_d.resample('MS').sum().rename('eto_fao56_mm_month').reset_index().rename(columns={'date':'month'})
        m['cell_id']=r.cell_id; m['cell_key']=q.cell_key; chunks.append(m[['month','cell_id','cell_key','eto_fao56_mm_month']])
    cell=pd.concat(chunks,ignore_index=True); cell['month']=pd.to_datetime(cell.month); cell=cell.merge(elev[['cell_key','latitude','longitude','dem_mean_elevation_m','era5land_spatial_weight']],on='cell_key',how='left')
    if cell.cell_id.nunique()!=33 or cell.eto_fao56_mm_month.isna().any():raise ValueError('ETo incompleta por celda')
    bands=gpd.read_file(BANDS).to_crs(4326).sort_values('band_id'); bu=bands.to_crs(32717)
    rows=[]
    for c in elev.itertuples():
        cg=gpd.GeoSeries([box(c.longitude-.05,c.latitude-.05,c.longitude+.05,c.latitude+.05)],crs=4326).to_crs(32717).iloc[0]
        for b in bu.itertuples():
            area=cg.intersection(b.geometry).area
            if area>0:rows.append({'cell_key':c.cell_key,'band_id':b.band_id,'intersection_area_m2':area})
    w=pd.DataFrame(rows); w['weight_within_band']=w.intersection_area_m2/w.groupby('band_id').intersection_area_m2.transform('sum')
    w['weight_within_cell']=w.intersection_area_m2/w.groupby('cell_key').intersection_area_m2.transform('sum')
    if not np.allclose(w.groupby('band_id').weight_within_band.sum(),1):raise ValueError('pesos por banda inválidos')
    selected=cell.loc[cell.month.map(hy).isin(VALID_HY)].copy(); selected['hydrological_year']=selected.month.map(hy)
    expanded=selected.merge(w[['cell_key','band_id','weight_within_band']],on='cell_key')
    result=expanded.groupby(['month','hydrological_year','band_id'],as_index=False).agg(eto_fao56_mm_month=('eto_fao56_mm_month',lambda s:np.dot(s,expanded.loc[s.index,'weight_within_band'])),n_cells=('cell_id','nunique'))
    expected_cells=w.groupby('band_id').cell_key.nunique().rename('expected_n_cells').reset_index()
    result=result.merge(expected_cells,on='band_id',how='left')
    if len(result)!=252*8 or not result.n_cells.eq(result.expected_n_cells).all():raise ValueError('cobertura temporal o espacial incompleta')
    annual=result.groupby(['hydrological_year','band_id'],as_index=False).agg(eto_fao56_mm_year=('eto_fao56_mm_month','sum'),months=('month','count'))
    if not annual.months.eq(12).all():raise ValueError('año hidrológico incompleto')
    DATA.mkdir(parents=True,exist_ok=True); OUT.mkdir(parents=True,exist_ok=True)
    cell.to_csv(DATA/'fao56_eto_mensual_33_celdas_reconstruido.csv',index=False);w.to_csv(DATA/'era5land_pesos_interseccion_por_banda.csv',index=False)
    result.to_csv(OUT/'1_5_eto_fao56_mensual_por_banda.csv',index=False);annual.to_csv(OUT/'1_5_eto_fao56_anual_hidrologica_por_banda.csv',index=False)
    (OUT/'1_5_eto_fao56_control_calidad.json').write_text(json.dumps({'cells':33,'zip_files_cds':25,'existing_validated_P_series':8,'period':'AH2002 and AH2004-AH2023','months_per_band':252,'units':'mm/month and mm/year','method':'FAO-56 daily ETo summed to month; meteorological grid cells intersected with SRTM bands'},indent=2),encoding='utf-8')
    print('ETO_OK',len(cell),len(result),len(annual))
if __name__=='__main__':main()
