"""Renombra solo las carpetas de consulta y verifica su integridad."""
from pathlib import Path
import csv
import hashlib

ROOT = Path(__file__).resolve().parent
MAPPING = {
    '1.4.1 - Tendencias': '01 - Tendencias',
    '1.4.2 - Atribucion': '02 - Atribucion',
    '1.4.3 - Paradoja del tanque': '03 - Paradoja del tanque',
    'Bonificacion Budyko': '04 - Bonificacion Budyko',
    'Codigo Python': '05 - Codigo Python',
    'Datos utilizados': '06 - Datos utilizados',
    'Tablas y figuras': '07 - Tablas y figuras',
    'Referencias y documentacion': '08 - Referencias y documentacion',
}
EXCLUDE = {'inventario_antes_reorganizacion.csv', 'inventario_despues_reorganizacion.csv',
           'verificacion_integridad_reorganizacion.md', 'organizar_consulta_punto_1_4.py'}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def inventory(destination: Path):
    rows = []
    for path in sorted(ROOT.rglob('*')):
        if path.is_file() and path.name not in EXCLUDE:
            rows.append({'relative_path': str(path.relative_to(ROOT)), 'bytes': path.stat().st_size,
                         'sha256': sha256(path)})
    with destination.open('w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=['relative_path', 'bytes', 'sha256'])
        writer.writeheader(); writer.writerows(rows)
    return rows


def main():
    absent = [old for old in MAPPING if not (ROOT / old).is_dir()]
    occupied = [new for new in MAPPING.values() if (ROOT / new).exists()]
    if absent or occupied:
        raise RuntimeError(f'No se renombra: faltantes={absent}; destinos_existentes={occupied}')
    before = inventory(ROOT / 'inventario_antes_reorganizacion.csv')
    for old, new in MAPPING.items():
        (ROOT / old).rename(ROOT / new)
    after = inventory(ROOT / 'inventario_despues_reorganizacion.csv')
    before_hashes = sorted((row['bytes'], row['sha256']) for row in before)
    after_hashes = sorted((row['bytes'], row['sha256']) for row in after)
    valid = before_hashes == after_hashes and len(before) == len(after)
    report = ROOT / 'verificacion_integridad_reorganizacion.md'
    report.write_text(
        '# Verificación de integridad tras la reorganización\n\n'
        f'- Archivos científicos inventariados antes: {len(before)}.\n'
        f'- Archivos científicos inventariados después: {len(after)}.\n'
        f'- Coincidencia de pares tamaño/SHA-256: {"SÍ" if valid else "NO"}.\n'
        '- Alcance: se renombraron únicamente ocho carpetas de consulta dentro de `PUNTO 1.4`.\n'
        '- No se modificó ni movió ningún archivo de la estructura científica `tarea 02/`.\n', encoding='utf-8')
    if not valid:
        raise RuntimeError('Fallo de integridad: revisar inventarios antes de continuar.')
    print(f'Renombradas {len(MAPPING)} carpetas; {len(after)} archivos preservados; SHA-256 verificado.')


if __name__ == '__main__':
    main()
