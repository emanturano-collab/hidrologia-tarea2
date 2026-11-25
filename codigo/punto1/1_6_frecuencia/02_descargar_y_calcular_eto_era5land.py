"""Una serie puntual ERA5-Land y ETo FAO-56 para DWD 00020 (UTC)."""
from __future__ import annotations
import importlib.util, json, zipfile
from pathlib import Path
import cdsapi, pandas as pd

ROOT=next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir()); RAW=ROOT/'datos/punto1/1_6_frecuencia/originales_era5land'; PROC=ROOT/'datos/punto1/procesados/1_6_frecuencia'
ZIP=RAW/'ERA5Land_DWD00020_20050101_20251231.zip'; SRC=ROOT/'codigo/punto1/1_1_demanda_atmosferica/1_1_a_fao56/run_fao56_1_1a.py'
REQUEST={'variable':['2m_temperature','2m_dewpoint_temperature','surface_pressure','surface_solar_radiation_downwards','10m_u_component_of_wind','10m_v_component_of_wind'],'location':{'latitude':48.9219,'longitude':9.9129},'date':'2005-01-01/2025-12-31','data_format':'netcdf'}
def load():
 s=importlib.util.spec_from_file_location('fao',SRC);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.LOCAL_TZ='UTC';return m
def main():
 RAW.mkdir(parents=True,exist_ok=True);PROC.mkdir(parents=True,exist_ok=True)
 if not ZIP.exists() or ZIP.stat().st_size==0:
  c=cdsapi.Client();c.retry_max=3;c.sleep_max=20;c.timeout=180;c.retrieve('reanalysis-era5-land-timeseries',REQUEST,str(ZIP))
 with zipfile.ZipFile(ZIP) as z:
  if z.testzip():raise ValueError('ZIP ERA5-Land corrupto')
 fao=load();hourly,meta,_=fao.read_zip_netcdf(ZIP);required={'t2m','d2m','sp','ssrd','u10','v10'}
 if set(hourly)!=required:raise ValueError(f'variables={set(hourly)}')
 d=fao.fao56_daily('DWD00020_ERA5Land',hourly,432.0,48.9219)
 if d.date.min()!=pd.Timestamp('2005-01-01') or d.date.max()!=pd.Timestamp('2025-12-31') or len(d)!=7670:raise ValueError(f'cobertura diaria inesperada: {d.date.min()}..{d.date.max()}, {len(d)}')
 if d.eto_fao56_mm_d.isna().any() or (d.eto_fao56_mm_d<0).any():raise ValueError('ETo diaria inválida')
 m=d.set_index('date').eto_fao56_mm_d.resample('MS').sum().rename('eto_fao56_mm_month').reset_index().rename(columns={'date':'month'})
 m['days']=m.month.dt.days_in_month;m.to_csv(PROC/'era5land_dwd00020_eto_fao56_mensual_2005_2025.csv',index=False)
 pd.DataFrame(meta).to_csv(PROC/'era5land_dwd00020_variables_metadatos.csv',index=False)
 (PROC/'era5land_dwd00020_eto_fuente.json').write_text(json.dumps({'dataset':'reanalysis-era5-land-timeseries','location':[48.9219,9.9129],'period':'2005-01-01/2025-12-31','timezone_for_aggregation':'UTC','method':'FAO-56 Penman-Monteith; ERA5-Land meteorology, not ERA5 potential evaporation','request':REQUEST},indent=2),encoding='utf8')
 print('ETO_OK',len(d),len(m),float(m.eto_fao56_mm_month.mean()))
if __name__=='__main__':main()
