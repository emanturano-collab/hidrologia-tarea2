"""Planifica y valida el lote GLEAM mensual obtenido en una sesion OpenSSH.

No abre conexiones ni conoce contrasenas. ``plan`` crea solo comandos reget
para 2002--2023 que todavia no esten validados. ``validate`` exige que el
tamano coincida con el inventario, valida el NetCDF y solo entonces promueve
un .part al nombre final.
"""
from __future__ import annotations
import argparse, importlib.util, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('gleam_download', HERE / 'descargar_gleam43a_mensual.py')
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)
INV = module.ROOT / 'datos' / 'punto1' / 'gleam4_3a_sftp_inventory.json'
PLAN = module.RAW / 'openssh_reget_2002_2023.sftp'
YEARS = range(2002, 2024)

def expected_sizes():
    data = json.loads(INV.read_text(encoding='utf-8'))
    result = {}
    for item in data['relevant_entries']:
        path = item['path']
        for year in YEARS:
            if path.endswith(f'E_{year}_GLEAM_v4.3a_MO.nc'):
                result[year] = int(item['size_bytes'])
    if set(result) != set(YEARS):
        raise ValueError('El inventario no contiene exactamente los 22 tamanos esperados.')
    return result

def name(year): return f'E_{year}_GLEAM_v4.3a_MO.nc'

def validate_file(path, year, size):
    if path.stat().st_size != size:
        raise ValueError(f'{path.name}: {path.stat().st_size} bytes; inventario espera {size}')
    meta = module.validate(path, year)
    return {'year': year, 'file': path.name, 'bytes': size, 'sha256': module.sha256(path), 'metadata': meta}

def plan(sizes):
    module.RAW.mkdir(parents=True, exist_ok=True)
    commands = []
    for year in YEARS:
        target = module.RAW / name(year)
        part = module.RAW / f'{name(year)}.part'
        if target.exists():
            validate_file(target, year, sizes[year])
            continue
        if part.exists() and part.stat().st_size > sizes[year]:
            raise ValueError(f'{part.name}: .part mayor que el tamano remoto; no se reemplaza')
        remote = f'/data/v4.3a/monthly/E/{name(year)}'
        commands.append(f'reget {remote} {part.name}')
    PLAN.write_text('\n'.join(commands) + ('\n' if commands else ''), encoding='ascii')
    print(f'PLAN={PLAN}')
    print(f'PENDIENTES={len(commands)}')

def validate_all(sizes):
    entries = []
    for year in YEARS:
        target = module.RAW / name(year)
        part = module.RAW / f'{name(year)}.part'
        candidate = target if target.exists() else part
        if not candidate.exists():
            raise FileNotFoundError(f'Falta {name(year)} o su .part; no se completa el lote')
        entry = validate_file(candidate, year, sizes[year])
        if candidate == part:
            part.replace(target)
        entries.append(entry)
        print(f'VALIDO {year} {entry["sha256"]}')
    manifest = module.RAW / 'manifest_gleam43a_E.json'
    old = json.loads(manifest.read_text(encoding='utf-8')) if manifest.exists() else {'files': []}
    merged = {int(x['year']): x for x in old.get('files', [])}
    merged.update({x['year']: x for x in entries})
    manifest.write_text(json.dumps({'host': module.HOST, 'remote_directory': module.REMOTE,
                                    'credentials_stored': False,
                                    'files': [merged[y] for y in sorted(merged)]}, indent=2), encoding='utf-8')
    print(f'LOTE_VALIDADO=22; MANIFEST={manifest}')

ap = argparse.ArgumentParser()
ap.add_argument('action', choices=['plan', 'validate'])
args = ap.parse_args()
sizes = expected_sizes()
plan(sizes) if args.action == 'plan' else validate_all(sizes)
