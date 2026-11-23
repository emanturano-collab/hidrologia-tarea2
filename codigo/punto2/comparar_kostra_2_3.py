"""Extrae la celda KOSTRA-DWD-2020 del pluviómetro y compara IDF."""
from pathlib import Path
import numpy as np
import pandas as pd
from pyproj import Transformer

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'datos'/'punto2'/'Abtsgmuend_Untergroeningen'
K=DATA/'kostra'; OUT=DATA/'idf_2_3'
TRET=[1,2,3,5,10,20,30,50,100]
DURS={'D00010': '10min','D00060':'1h','D00360':'6h','D01440':'24h'}

def main():
    x,y=Transformer.from_crs(4326,3035,always_xy=True).transform(9.9129,48.9219)
    rows=[]
    for code,label in DURS.items():
        f=next(K.glob(f'Hn_KOSTRA-DWD-2020_{code}_T001.asc'))
        lines=f.read_text().splitlines(); h={k.lower():float(v) for k,v in (z.split() for z in lines[:6])}
        c=int((x-h['xllcorner'])/h['cellsize']); r=int((h['yllcorner']+h['nrows']*h['cellsize']-y)/h['cellsize'])
        for T in TRET:
            a=np.loadtxt(K/f'Hn_KOSTRA-DWD-2020_{code}_T{T:03d}.asc',skiprows=6)
            val=float(a[r,c])
            rows.append({'duration':label,'T_years':T,'kostra_depth_mm':val,'kostra_intensity_mm_h':val/({'10min':1/6,'1h':1,'6h':6,'24h':24}[label]),'row':r,'col':c,'crs':'EPSG:3035'})
    out=pd.DataFrame(rows); out.to_csv(OUT/'kostra_station_cell.csv',index=False,float_format='%.4f')
    obs=pd.read_csv(OUT/'idf_gev_mle.csv')
    obs=obs[obs.duration.isin(DURS.values())].merge(out[['duration','T_years','kostra_depth_mm','kostra_intensity_mm_h']],on=['duration','T_years'])
    obs['ratio_obs_to_kostra']=obs.intensity_mm_h/obs.kostra_intensity_mm_h
    obs.to_csv(OUT/'idf_kostra_comparison.csv',index=False,float_format='%.5f')
    print('KOSTRA extraido:',len(out),'filas; celda',r,c)
if __name__=='__main__': main()
