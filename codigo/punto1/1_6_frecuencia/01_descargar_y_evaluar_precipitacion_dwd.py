"""Descarga mínima DWD y control mensual de P para 1.6, estación 00020."""
from __future__ import annotations
import hashlib, zipfile
from pathlib import Path
import pandas as pd
import certifi, requests

ROOT=next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
RAW=ROOT/'datos/punto1/1_6_frecuencia/originales_dwd_00020'
OUT=ROOT/'datos/punto1/procesados/1_6_frecuencia'
BASE='https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/10_minutes/precipitation/historical/'
FILES=['10minutenwerte_nieder_00020_20040812_20091231_hist.zip','10minutenwerte_nieder_00020_20100101_20191231_hist.zip','10minutenwerte_nieder_00020_20200101_20251231_hist.zip']
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def main():
 RAW.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True); parts=[];inventory=[]
 for n in FILES:
  p=RAW/n
  if not p.exists() or p.stat().st_size==0:
   response=requests.get(BASE+n,timeout=120,verify=certifi.where());response.raise_for_status();p.write_bytes(response.content)
  with zipfile.ZipFile(p) as z:
   bad=z.testzip()
   if bad: raise ValueError(f'{n}: ZIP corrupto {bad}')
   member=next(x for x in z.namelist() if x.startswith('produkt_') and x.endswith('.txt'))
   d=pd.read_csv(z.open(member),sep=';',skipinitialspace=True);d.columns=[x.strip() for x in d.columns]
  parts.append(d[['MESS_DATUM','RWS_10']]);inventory.append({'filename':n,'url':BASE+n,'size_bytes':p.stat().st_size,'sha256':digest(p),'member':member})
 d=pd.concat(parts).drop_duplicates('MESS_DATUM').sort_values('MESS_DATUM');d['time_utc']=pd.to_datetime(d.MESS_DATUM.astype(str),format='%Y%m%d%H%M',errors='coerce');d['precip_mm']=pd.to_numeric(d.RWS_10,errors='coerce');d.loc[d.precip_mm<0,'precip_mm']=float('nan');d=d[(d.time_utc>='2005-01-01')&(d.time_utc<'2026-01-01')].copy();d['month']=d.time_utc.dt.to_period('M').dt.to_timestamp()
 monthly=d.groupby('month').agg(records=('precip_mm','size'),valid_records=('precip_mm','count'),precip_mm_month=('precip_mm','sum')).reset_index();monthly['expected_records']=monthly.month.dt.days_in_month*144;monthly['completeness_percent']=100*monthly.valid_records/monthly.expected_records;monthly.loc[monthly.completeness_percent<98.5,'precip_mm_month']=float('nan')
 if len(monthly)!=252: raise ValueError(f'Meses esperados=252; hallados={len(monthly)}')
 clim=monthly.groupby(monthly.month.dt.month).agg(precip_mm_month_mean=('precip_mm_month','mean'),months_valid=('precip_mm_month','count')).reset_index(names='calendar_month')
 monthly.to_csv(OUT/'dwd_00020_precipitacion_mensual_2005_2025.csv',index=False);clim.to_csv(OUT/'dwd_00020_climatologia_precipitacion_mensual.csv',index=False);pd.DataFrame(inventory).to_csv(OUT/'dwd_00020_fuentes_sha256.csv',index=False)
 print('P_OK',len(d),len(monthly),'months_complete',monthly.precip_mm_month.notna().sum());print(clim.to_string(index=False))
if __name__=='__main__':main()
