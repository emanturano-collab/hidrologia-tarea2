"""Evalúa temporada seca climatológica, sin análisis de frecuencia."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
ROOT=next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir());P=ROOT/'datos/punto1/procesados/1_6_frecuencia/dwd_00020_precipitacion_mensual_2005_2025.csv';E=ROOT/'datos/punto1/procesados/1_6_frecuencia/era5land_dwd00020_eto_fao56_mensual_2005_2025.csv';O=ROOT/'datos/punto1/procesados/1_6_frecuencia'
def main():
 p=pd.read_csv(P,parse_dates=['month']);e=pd.read_csv(E,parse_dates=['month']);m=p.merge(e[['month','eto_fao56_mm_month']],on='month');m['deficit_mm_month']=m.eto_fao56_mm_month-m.precip_mm_month;m['calendar_month']=m.month.dt.month
 # All three climatological means are conditional on the same valid P-ETo pairs.
 pair=m.dropna(subset=['precip_mm_month','eto_fao56_mm_month']).copy()
 c=pair.groupby('calendar_month').agg(P_mm_mean=('precip_mm_month','mean'),ETo_mm_mean=('eto_fao56_mm_month','mean'),deficit_mm_mean=('deficit_mm_month','mean'),valid_years=('deficit_mm_month','count')).reset_index();c['dry_climatological']= (c.deficit_mm_mean>0)&(c.valid_years>=20)
 selected=c.loc[c.dry_climatological,'calendar_month'].tolist()
 if not selected:raise ValueError('No existe temporada con ETo>P climatológico')
 # Must be a single contiguous dry season in the annual cycle (wrap allowed).
 # Consecutive months can either be contained in one calendar year (Apr-Sep)
 # or wrap December-January; in either case there may be only one circular gap.
 gaps=[b-a for a,b in zip(selected,selected[1:])]+[selected[0]+12-selected[-1]]
 if sum(g>1 for g in gaps)!=1:raise ValueError(f'Meses secos no contiguos: {selected}')
 m.to_csv(O/'dwd00020_P_ETo_mensual_2005_2025.csv',index=False);c.to_csv(O/'dwd00020_climatologia_P_ETo_y_deficit.csv',index=False)
 (O/'dwd00020_temporada_seca_criterio.json').write_text(json.dumps({'criterion':'Meses calendario con promedio climatológico ETo FAO-56 - P DWD > 0 mm y >=20 años mensuales válidos','dry_months':selected,'valid_months_total':int(m.deficit_mm_month.notna().sum()),'status':'TEMPORADA_SECA_CLIMATICAMENTE_DEFINIDA'},indent=2),encoding='utf8')
 print(c.to_string(index=False));print('DRY_MONTHS',selected)
if __name__=='__main__':main()
