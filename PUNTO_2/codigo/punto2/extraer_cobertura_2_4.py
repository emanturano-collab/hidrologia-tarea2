"""Extrae ESA WorldCover dentro de la microcuenca y pondera C."""
from pathlib import Path
from osgeo import gdal
import numpy as np, pandas as pd, json

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'datos'/'punto2'/'Abtsgmuend_Untergroeningen'
OUT=DATA/'cobertura_2_4'; OUT.mkdir(exist_ok=True)
SRC=str(DATA/'ESA_WorldCover_10m_2021_v200_N48E009_Map.tif')
MASK=str(DATA/'cuenca_preparada'/'microcuenca_abtsgmuend.geojson')
CLIP=str(OUT/'worldcover_microcuenca.tif')

# Coeficientes racionales representativos para una cuenca pequena rural.
# Deben contrastarse con la tabla adoptada en el informe y con suelo/humedad.
META={10:('Arboles',0.30),20:('Matorral',0.35),30:('Pastizal',0.35),40:('Cultivo',0.45),50:('Construido',0.85),60:('Suelo desnudo',0.60),70:('Nieve/hielo',0.90),80:('Agua',1.00),90:('Humedal',0.25),95:('Manglar',0.25),100:('Musgo/liquen',0.30)}

def main():
    opts=gdal.WarpOptions(format='GTiff',cutlineDSName=MASK,cropToCutline=True,dstNodata=0,xRes=0.0001,yRes=0.0001,resampleAlg='near')
    ds=gdal.Warp(CLIP,SRC,options=opts); ds=None
    ds=gdal.Open(CLIP); arr=ds.GetRasterBand(1).ReadAsArray(); gt=ds.GetGeoTransform(); pix=abs(gt[1]*111320.0*gt[5]*111320.0*np.cos(np.deg2rad(48.92))); vals,cnt=np.unique(arr[arr>0],return_counts=True)
    total=int(cnt.sum()); rows=[]
    for v,n in zip(vals,cnt):
        code=int(v); name,c=META.get(code,(f'Clase_{code}',0.45)); rows.append({'class_code':code,'landcover':name,'pixels':int(n),'area_m2':float(n*pix),'area_pct':float(100*n/total),'C_assigned':c})
    tab=pd.DataFrame(rows).sort_values('area_pct',ascending=False); tab.to_csv(OUT/'worldcover_summary.csv',index=False,float_format='%.5f')
    Cw=float((tab.area_pct*tab.C_assigned).sum()/100); pd.DataFrame([{'basin_area_m2':total*pix,'weighted_C':Cw,'source':'ESA WorldCover 2021 + coefficients documented in landcover_coefficients.md','sensitivity_low':Cw*.8,'sensitivity_high':min(1,Cw*1.2)}]).to_csv(OUT/'weighted_runoff_coefficient.csv',index=False,float_format='%.5f')
    (OUT/'landcover_coefficients.md').write_text('# Coeficientes de escorrentia\n\nLos C asignados son valores racionales representativos por cobertura para una microcuenca pequena. La tabla debe citar Chow et al. y debe discutirse la incertidumbre por suelo, pendiente y humedad antecedente. Se propaga una sensibilidad global de +/-20% en el problema A.\n\n| Clase | C |\n|---|---:|\n'+ '\n'.join(f'| {k} {v[0]} | {v[1]:.2f} |' for k,v in META.items()),encoding='utf-8')
    print(json.dumps({'pixels':total,'pixel_area_m2':pix,'weighted_C':Cw},ensure_ascii=False))
if __name__=='__main__': main()
