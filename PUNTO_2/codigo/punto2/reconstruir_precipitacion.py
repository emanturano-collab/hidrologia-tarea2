from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'datos'/'punto2'/'Abtsgmuend_Untergroeningen'
rows=[]
for f in sorted((BASE/'raw').glob('10minutenwerte_nieder_00020_*/*produkt*.txt')):
    d=pd.read_csv(f,sep=';',skipinitialspace=True)
    d.columns=[c.strip() for c in d.columns]
    rows.append(pd.DataFrame({'station_id':d['STATIONS_ID'].astype(str).str.strip(),'timestamp_utc':d['MESS_DATUM'].astype(str).str.strip(),'quality_code':d['QN'],'precip_mm':d['RWS_10'],'precip_indicator':d['RWS_IND_10']}))
out=pd.concat(rows,ignore_index=True).drop_duplicates('timestamp_utc').sort_values('timestamp_utc')
out.to_csv(BASE/'abtsgmuend_precipitation_10min.csv',index=False)
print('registros reconstruidos',len(out))
