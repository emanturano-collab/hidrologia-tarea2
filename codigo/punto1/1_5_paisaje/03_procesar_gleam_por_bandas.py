"""Contraste GLEAM4.3a por bandas; no confunde su grilla 0.1° con relieve fino."""
from __future__ import annotations
import json
from pathlib import Path
import geopandas as gpd, numpy as np, pandas as pd, xarray as xr
from shapely.geometry import box

ROOT=next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
BANDS=ROOT/'datos/punto1/procesados/1_5_paisaje/PE_200907_bandas_altitudinales_SRTM_500m.gpkg'
RAW=ROOT/'datos/punto1/gleam4_3a_raw'; DATA=ROOT/'datos/punto1/procesados/1_5_paisaje'; OUT=ROOT/'productos/punto1/1_5_paisaje'
YEARS=[2002]+list(range(2004,2024))
def hy(d):return d.year+1 if d.month>=9 else d.year
def main():
    bands=gpd.read_file(BANDS).to_crs(4326).sort_values('band_id'); utm=bands.to_crs(32717)
    cells=[]
    # Build just the grid cells which intersect each elevation-band polygon.
    for b in utm.itertuples():
        minx,miny,maxx,maxy=b.geometry.to_crs(4326).bounds if False else bands.loc[bands.band_id==b.band_id].geometry.iloc[0].bounds
        for lat in np.arange(np.floor((miny+.05)*10)/10-.05,np.ceil((maxy-.05)*10)/10+.051,.1):
            for lon in np.arange(np.floor((minx+.05)*10)/10-.05,np.ceil((maxx-.05)*10)/10+.051,.1):
                cell=gpd.GeoSeries([box(lon-.05,lat-.05,lon+.05,lat+.05)],crs=4326).to_crs(32717).iloc[0]
                a=cell.intersection(b.geometry).area
                if a>0: cells.append({'band_id':b.band_id,'lat_center':round(float(lat),2),'lon_center':round(float(lon),2),'intersection_area_m2':a})
    w=pd.DataFrame(cells); w['weight_within_band']=w.intersection_area_m2/w.groupby('band_id').intersection_area_m2.transform('sum')
    if not np.allclose(w.groupby('band_id').weight_within_band.sum(),1):raise ValueError('pesos GLEAM no suman 1')
    monthly=[]
    for year in range(2001,2024):
        p=RAW/f'E_{year}_GLEAM_v4.3a_MO.nc'
        if not p.exists():raise FileNotFoundError(p)
        d=xr.open_dataset(p)
        try:
            for t in pd.to_datetime(d.time.values):
                if hy(t) not in YEARS:continue
                for bid,g in w.groupby('band_id'):
                    vals=[]
                    for r in g.itertuples():
                        x=float(d.E.sel(time=t,lat=r.lat_center,lon=r.lon_center,method='nearest').values)
                        vals.append(x)
                    if not np.isfinite(vals).all() or np.any(np.asarray(vals)<=-999):raise ValueError(f'{t} banda {bid}: faltante GLEAM')
                    monthly.append({'month':t.strftime('%Y-%m-01'),'hydrological_year':hy(t),'band_id':bid,'et_gleam_mm_month':float(np.dot(vals,g.weight_within_band)),'n_gleam_cells':len(g)})
        finally:d.close()
    m=pd.DataFrame(monthly).sort_values(['band_id','month'])
    if len(m)!=252*8 or m.duplicated(['month','band_id']).any():raise ValueError(f'filas mensuales={len(m)}')
    a=m.groupby(['hydrological_year','band_id'],as_index=False).agg(et_gleam_mm_year=('et_gleam_mm_month','sum'),months=('month','count'),n_gleam_cells=('n_gleam_cells','first'))
    if not a.months.eq(12).all():raise ValueError('años incompletos')
    DATA.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
    w.to_csv(DATA/'gleam4_3a_pesos_interseccion_por_banda.csv',index=False);m.to_csv(OUT/'1_5_gleam4_3a_ET_mensual_por_banda.csv',index=False);a.to_csv(OUT/'1_5_gleam4_3a_ET_anual_hidrologica_por_banda.csv',index=False)
    (OUT/'1_5_gleam4_3a_por_bandas_limitacion.json').write_text(json.dumps({'units':'mm.month-1 original; sums in mm/year','resolution':'0.1 degree','warning':'Cada celda GLEAM puede abarcar más de una banda: los resultados son un contraste de grilla gruesa, no evidencia de un gradiente fino independiente.'},indent=2),encoding='utf-8')
    print('GLEAM_OK',len(m),len(a), 'cells',len(w))
if __name__=='__main__':main()
