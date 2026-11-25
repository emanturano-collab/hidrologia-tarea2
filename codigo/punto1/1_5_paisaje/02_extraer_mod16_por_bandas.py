"""Extrae MOD16A2GF v6.1 por bandas SRTM, sin descargar rásteres globales."""
from __future__ import annotations
import json, os, time
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
import ee, geopandas as gpd, pandas as pd
from shapely.geometry import mapping

ROOT=next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
BANDS=ROOT/'datos/punto1/procesados/1_5_paisaje/PE_200907_bandas_altitudinales_SRTM_500m.gpkg'
RAW=ROOT/'datos/punto1/procesados/1_5_paisaje/mod16a2gf_bandas_altitudinales_composites_controlado.csv'
LOCK=RAW.with_suffix('.lock')
OUT=ROOT/'productos/punto1/1_5_paisaje'
COLLECTION='MODIS/061/MOD16A2GF'; PROJECT='hidrologia-racarumi'
WINDOWS=[(date(2001,9,1),date(2002,9,1)),(date(2003,9,1),date(2023,9,1))]

def retry(fun, attempts=4):
    err=None
    for i in range(attempts):
        try:return fun()
        except Exception as e:
            err=e
            if i+1<attempts: time.sleep(4*(i+1))
    raise err

def make_fc():
    g=gpd.read_file(BANDS).to_crs(4326).sort_values('band_id')
    return ee.FeatureCollection([ee.Feature(mapping(r.geometry), {'band_id':int(r.band_id),'band_label':r.band_label}) for r in g.itertuples()])

def dates(coll):
    starts=sorted(datetime.fromtimestamp(x/1000,UTC).date() for x in retry(lambda:coll.aggregate_array('system:time_start').getInfo()))
    out=[]
    for i,s in enumerate(starts):
        e=starts[i+1] if i+1<len(starts) else s+timedelta(days=8)
        if any(s<b and e>a for a,b in WINDOWS):out.append((s,e))
    return out

def run():
    ee.Initialize(project=PROJECT)
    start=min(a for a,_ in WINDOWS)-timedelta(days=9); end=max(b for _,b in WINDOWS)+timedelta(days=9)
    coll=ee.ImageCollection(COLLECTION).filterDate(start.isoformat(),end.isoformat())
    wanted=dates(coll); metadata={s.isoformat():(s,e) for s,e in wanted}
    prior=pd.read_csv(RAW) if RAW.exists() else pd.DataFrame()
    done=set(prior.image_start) if not prior.empty else set()
    todo=[s for s,_ in wanted if s.isoformat() not in done]
    fc=make_fc(); RAW.parent.mkdir(parents=True,exist_ok=True)
    for pos in range(0,len(todo),12):
        batch=todo[pos:pos+12]
        ms=[int(datetime(d.year,d.month,d.day,tzinfo=UTC).timestamp()*1000) for d in batch]
        def reduce_one(t):
            im=ee.Image(coll.filter(ee.Filter.eq('system:time_start',t)).first()); raw=im.select('ET'); valid=raw.lt(32761); area=ee.Image.pixelArea()
            good=valid.And(im.select('ET_QC').bitwiseAnd(1).eq(0))
            stack=raw.updateMask(valid).multiply(.1).multiply(area).rename('et_mm_m2').addBands(area.updateMask(valid).rename('valid_area_m2')).addBands(area.rename('total_area_m2')).addBands(area.updateMask(good).rename('qc_good_area_m2'))
            r=stack.reduceRegions(collection=fc,reducer=ee.Reducer.sum(),scale=500,crs=raw.projection(),tileScale=2)
            return r.map(lambda f:f.set('time_start',t))
        features=retry(lambda:ee.FeatureCollection(ee.List(ms).map(reduce_one)).flatten().getInfo())['features']
        rows=[]
        for f in features:
            q=f['properties']; s=datetime.fromtimestamp(q['time_start']/1000,UTC).date(); a,b=metadata[s.isoformat()]
            va,ta,w,qa=(q.get(x) for x in ('valid_area_m2','total_area_m2','et_mm_m2','qc_good_area_m2'))
            if None in (va,ta,w,qa) or va<=0 or ta<=0: raise ValueError(f'{s} banda {q["band_id"]}: sin píxeles válidos')
            cov=100*va/ta
            if cov<95: raise ValueError(f'{s} banda {q["band_id"]}: cobertura {cov:.3f}% <95%')
            rows.append({'image_start':s.isoformat(),'image_end':b.isoformat(),'duration_days':(b-a).days,'band_id':q['band_id'],'band_label':q['band_label'],'et_mm_composite':w/va,'valid_area_m2':va,'total_area_m2':ta,'valid_coverage_percent':cov,'qc_modland_good_percent':100*qa/va,'et_scale_factor':.1,'source':COLLECTION})
        pd.DataFrame(rows).to_csv(RAW,mode='a',header=not RAW.exists(),index=False)
        print(f'{min(pos+len(batch),len(todo))}/{len(todo)} compuestos')
    out=pd.read_csv(RAW); expected=len(wanted)*8
    if len(out)!=expected or out.duplicated(['image_start','band_id']).any():raise ValueError(f'filas={len(out)}; esperadas={expected}')
    (OUT/'1_5_mod16_bandas_control_calidad.json').write_text(json.dumps({'source':COLLECTION,'composites':len(wanted),'bands':8,'rows':len(out),'periods':'AH2002 y AH2004-AH2023','ET_units':'mm per MOD16 composite; scale factor 0.1'},indent=2),encoding='utf-8')
    print('EXTRACCION_OK',len(out))
def main():
    """Prevent concurrent writers; the prior raw CSV remains evidence only."""
    RAW.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd=os.open(LOCK, os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    except FileExistsError:
        raise SystemExit(f'BLOQUEO_ACTIVO: {LOCK}; no se permite otra extracción concurrente.')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f: f.write(str(os.getpid()))
        run()
    finally:
        LOCK.unlink(missing_ok=True)

if __name__=='__main__':main()
