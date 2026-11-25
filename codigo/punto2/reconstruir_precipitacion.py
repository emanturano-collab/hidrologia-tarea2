from pathlib import Path
import pandas as pd

ROOT=next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
BASE=ROOT/'datos'/'punto2'/'Abtsgmuend_Untergroeningen'
rows=[]
for f in sorted((BASE/'raw').glob('10minutenwerte_nieder_00020_*/*produkt*.txt')):
    d=pd.read_csv(f,sep=';',skipinitialspace=True)
    d.columns=[c.strip() for c in d.columns]
    rows.append(pd.DataFrame({'station_id':d['STATIONS_ID'].astype(str).str.strip(),'timestamp_utc':d['MESS_DATUM'].astype(str).str.strip(),'quality_code':d['QN'],'precip_mm':d['RWS_10'],'precip_indicator':d['RWS_IND_10']}))
if not rows:
    raise FileNotFoundError(f"Entrada no incluida: no hay archivos DWD extraídos en {BASE/'raw'}")
out=pd.concat(rows,ignore_index=True).drop_duplicates('timestamp_utc').sort_values('timestamp_utc')
# El análisis usa los años calendario completos 2005-2025; 2004 es parcial.
stamp=pd.to_numeric(out['timestamp_utc'],errors='coerce')
out=out.loc[stamp.between(200501010000,202512312350)].copy()
out.to_csv(BASE/'abtsgmuend_precipitation_10min.csv',index=False)
print('registros reconstruidos',len(out))
