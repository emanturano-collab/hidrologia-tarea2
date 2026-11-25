"""Audita si la precipitación horaria DWD puede recuperar meses 10-min incompletos."""
from __future__ import annotations
import zipfile
from pathlib import Path
import certifi, pandas as pd, requests
ROOT=next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir());RAW=ROOT/'datos/punto1/1_6_frecuencia/originales_dwd_00020';P=ROOT/'datos/punto1/procesados/1_6_frecuencia/dwd_00020_precipitacion_mensual_2005_2025.csv';OUT=ROOT/'datos/punto1/procesados/1_6_frecuencia'
URL='https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/hourly/precipitation/historical/stundenwerte_RR_00020_20040814_20251231_hist.zip'
def main():
 zpath=RAW/'stundenwerte_RR_00020_20040814_20251231_hist.zip'
 if not zpath.exists():
  r=requests.get(URL,timeout=120,verify=certifi.where());r.raise_for_status();zpath.write_bytes(r.content)
 with zipfile.ZipFile(zpath) as z:
  if z.testzip():raise ValueError('ZIP horario corrupto')
  n=next(x for x in z.namelist() if x.startswith('produkt_') and x.endswith('.txt'));d=pd.read_csv(z.open(n),sep=';',skipinitialspace=True);d.columns=[x.strip() for x in d.columns]
 d['time']=pd.to_datetime(d.MESS_DATUM.astype(str),format='%Y%m%d%H',errors='coerce');d['p']=pd.to_numeric(d.R1,errors='coerce');d.loc[d.p<0,'p']=float('nan');d=d[(d.time>='2005-01-01')&(d.time<'2026-01-01')];d['month']=d.time.dt.to_period('M').dt.to_timestamp()
 h=d.groupby('month').agg(hour_records=('p','size'),hour_valid=('p','count'),P_hourly_mm_month=('p','sum')).reset_index();h['hour_expected']=h.month.dt.days_in_month*24;h['hour_completeness_pct']=100*h.hour_valid/h.hour_expected
 ten=pd.read_csv(P,parse_dates=['month']);cmp=ten.merge(h,on='month');both=cmp.dropna(subset=['precip_mm_month','P_hourly_mm_month']).copy();both['difference_hourly_minus_10min_mm']=both.P_hourly_mm_month-both.precip_mm_month
 recovery=cmp[cmp.precip_mm_month.isna()][['month','P_hourly_mm_month','hour_completeness_pct']].copy()
 h.to_csv(OUT/'dwd_00020_precipitacion_horaria_mensual_verificacion.csv',index=False);both.to_csv(OUT/'dwd_00020_comparacion_horaria_vs_10min.csv',index=False);recovery.to_csv(OUT/'dwd_00020_meses_candidatos_recuperacion_horaria.csv',index=False)
 print('HOURLY_OK',len(h),'overlap',len(both),'mae',both.difference_hourly_minus_10min_mm.abs().mean());print(recovery.to_string(index=False))
if __name__=='__main__':main()
