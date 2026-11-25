"""Descarga segura de GLEAM4.3a E mensual; nunca guarda credenciales."""
from __future__ import annotations
import argparse, getpass, hashlib, json, os, time
from pathlib import Path
import numpy as np
import paramiko, pandas as pd, xarray as xr

HOST, PORT = 'aether.ugent.be', 2225
REMOTE = '/data/v4.3a/monthly/E'
ROOT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
RAW = ROOT/'datos'/'punto1'/'gleam4_3a_raw'

def connect_sftp(user, pwd, known):
 """Conexion estricta, con reintentos solo ante fallos temporales SSH."""
 last = None
 for attempt in range(1, 4):
  client = paramiko.SSHClient()
  client.load_host_keys(str(known))
  client.set_missing_host_key_policy(paramiko.RejectPolicy())
  try:
   client.connect(HOST, port=PORT, username=user, password=pwd, look_for_keys=False,
                  allow_agent=False, timeout=30, banner_timeout=90, auth_timeout=90,
                  channel_timeout=90, compress=False)
   transport = client.get_transport()
   if transport is None or not transport.is_active():
    raise ConnectionError('El transporte SSH no quedo activo')
   transport.set_keepalive(30)
   return client, client.open_sftp()
  except Exception as exc:
   client.close(); last = exc
   if attempt < 3:
    print(f'Conexion SSH temporalmente fallida ({type(exc).__name__}); reintento {attempt}/3...')
    time.sleep(5 * attempt)
 raise RuntimeError(f'No se pudo abrir SFTP despues de 3 intentos: {type(last).__name__}: {last}') from last

def sha256(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''): h.update(b)
 return h.hexdigest()
def validate(p, year):
 with xr.open_dataset(p, mask_and_scale=False) as ds:
  if 'E' not in ds: raise ValueError(f'{p.name}: falta E')
  if tuple(ds['E'].dims) != ('time', 'lat', 'lon'):
   raise ValueError(f'{p.name}: dimensiones inesperadas de E: {ds["E"].dims}')
  t=[str(pd.Timestamp(x).date())[:7] for x in ds['time'].values]
  want=[f'{year}-{m:02d}' for m in range(1,13)]
  if t != want: raise ValueError(f'{p.name}: meses inesperados {t}')
  units=ds['E'].attrs.get('units')
  fill=ds['E'].attrs.get('_FillValue', ds['E'].encoding.get('_FillValue'))
  if units != 'mm.month-1': raise ValueError(f'{p.name}: unidades inesperadas {units!r}')
  if fill != -999: raise ValueError(f'{p.name}: _FillValue inesperado {fill!r}')
  values=ds['E'].values
  return {'dimensions':dict(ds.sizes),'units':units,'fill_value':float(fill),'time':t,
          'count_fill_minus999':int(np.count_nonzero(values == -999)),
          'count_nan_raw':int(np.count_nonzero(np.isnan(values)))}
def download(sftp, year):
 name=f'E_{year}_GLEAM_v4.3a_MO.nc'; remote=f'{REMOTE}/{name}'; target=RAW/name; part=RAW/(name+'.part')
 stat=sftp.stat(remote); RAW.mkdir(parents=True,exist_ok=True)
 if target.exists() and target.stat().st_size==stat.st_size:
  meta=validate(target,year); return {'year':year,'file':name,'reused':True,'bytes':stat.st_size,'sha256':sha256(target),'metadata':meta}
 offset=part.stat().st_size if part.exists() else 0
 if offset>stat.st_size: part.unlink(); offset=0
 with sftp.open(remote,'rb') as src, open(part,'ab' if offset else 'wb') as dst:
  src.seek(offset)
  while True:
   b=src.read(1048576)
   if not b: break
   dst.write(b)
 if part.stat().st_size != stat.st_size: raise IOError(f'{name}: descarga incompleta')
 os.replace(part,target); meta=validate(target,year)
 return {'year':year,'file':name,'reused':False,'bytes':stat.st_size,'sha256':sha256(target),'metadata':meta}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--all',action='store_true'); a=ap.parse_args()
 known=Path.home()/'.ssh'/'known_hosts'
 if not known.exists(): raise FileNotFoundError('Falta known_hosts verificado')
 user=input('Usuario SFTP GLEAM: ').strip(); pwd=getpass.getpass('Contrasena SFTP GLEAM (oculta): ')
 c=s=None
 try:
  c, s = connect_sftp(user, pwd, known)
  years=list(range(2001,2024)) if a.all else [2001]
  results=[download(s,y) for y in years]
  (RAW/'manifest_gleam43a_E.json').write_text(json.dumps({'host':HOST,'remote_directory':REMOTE,'credentials_stored':False,'files':results},indent=2),encoding='utf-8')
  print('OK',len(results),'archivo(s); manifest_gleam43a_E.json')
 finally:
  pwd=None
  if s is not None: s.close()
  if c is not None: c.close()
if __name__=='__main__': main()
