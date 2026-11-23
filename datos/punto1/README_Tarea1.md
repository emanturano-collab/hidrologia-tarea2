# PE_200907 - Racarumi

Proyecto colaborativo para el análisis hidroclimático de la cuenca `PE_200907`, estación Racarumi, cuenca Chancay-Lambayeque, región hidrográfica del Pacífico. La estación se localiza en latitud -6.633 y longitud -79.317 (WGS84); el área de drenaje es 2363.302 km².

El punto 1 de la tarea está terminado. Los puntos 2, 3 y 4 deben partir de la tabla maestra mensual y desarrollarse sin modificar los datos seleccionados ni los productos consolidados de este punto.

## Estructura

```text
data/
  selected/PE_200907/     # subconjunto mínimo de CAMELS-PE usado por los scripts
    timeseries/           # serie diaria de la cuenca
    geospatial/           # polígono y punto de la estación
    metadata/             # estación, variables y resumen de selección
  derived/PE_200907/      # resultados intermedios del punto 1
  processed/PE_200907/    # tabla maestra para el trabajo posterior
outputs/PE_200907/        # tablas, figuras, PDF y HTML finales
scripts/                  # flujo reproducible del punto 1
```

`data/raw/` y `data/extracted/` conservan localmente las descargas originales y la extracción completa de CAMELS-PE, pero están excluidos de Git porque no son necesarios para colaborar sobre esta cuenca.

## Datos y periodos

- **CAMELS-PE v1.0.1:** precipitación PISCOp v2.1 y caudal observado diario. El análisis mensual usa `1981-01` a `2023-08`.
- **PISCOt v1.2:** temperaturas mínima, media y máxima diarias incluidas en CAMELS-PE. El periodo mensual completo usado es `1981-01` a `2020-12`.
- **IMERG Final V07:** precipitación diaria `GPM_3IMERGDF` obtenida del dataset GDEX/NCAR `d734000` y promediada espacialmente sobre la cuenca. La cobertura efectiva es `2000-06` a `2023-08`; no se presenta como disponible desde 1998.

Las unidades de la tabla maestra son mm/mes para precipitación y escorrentía, mm/día para caudal medio y grados Celsius para temperatura.

## Criterio de faltantes

No se imputaron ni interpolaron datos diarios. La precipitación CAMELS-PE mensual se conserva solo cuando el mes está completo. El caudal medio mensual se calcula con las observaciones disponibles cuando la cobertura es al menos 90 %; con cobertura menor queda como `NaN`. Cinco meses de caudal no cumplen el umbral: `1981-09`, `1985-07`, `1988-08`, `2001-08` y `2003-08`.

Las temperaturas mensuales requieren el mes diario completo. IMERG mensual también requiere cobertura diaria completa. Los indicadores de días válidos, días faltantes, porcentaje de completitud y disponibilidad se mantienen en la tabla maestra.

La escorrentía mensual se calcula como:

```text
runoff_mm_month = flow_obs_mean_mm_day * expected_days
```

`flow_obs` ya representa una lámina en mm/día, por lo que no se aplica otra conversión mediante el área de la cuenca.

## Tabla maestra

Los puntos 2 a 5 deben usar como entrada principal:

```text
data/processed/PE_200907/PE_200907_master_monthly.csv
```

La columna `date` identifica el primer día de cada mes. Los `NaN` representan ausencia de cobertura o meses rechazados por los criterios anteriores; no deben sustituirse sin una decisión metodológica explícita del equipo.

## Instalación

Desde la raíz del proyecto:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

En Linux o macOS, la activación equivalente es `source .venv/bin/activate`.

## Flujo reproducible del punto 1

Ejecutar desde la raíz del repositorio:

```powershell
python scripts/audit_pe_200907_daily.py
python scripts/build_pe_200907_monthly.py
python scripts/prepare_pe_200907_temperature.py
python scripts/compare_pe_200907_imerg_camels.py
python scripts/analyze_pe_200907_monthly.py
python scripts/build_pe_200907_master_monthly.py
python scripts/build_pe_200907_final_products.py
```

El script `download_imerg_v07_pe_200907.py` produjo la serie diaria de IMERG y solo debe ejecutarse si es necesario reconstruir esa entrada desde GDEX. No forma parte de la ejecución normal del repositorio compartido porque los datos derivados empleados en el punto 1 ya están disponibles.

El PDF se compila desde `outputs/PE_200907/` con dos pasadas de `pdflatex PE_200907_Racarumi_report.tex`. MiKTeX o TeX Live es un requisito externo y no se instala mediante `requirements.txt`.

## Trabajo colaborativo

Crear una rama por componente desde la rama principal actual:

```bash
git switch -c punto-2
git switch -c punto-3
git switch -c punto-4
```

Cada integrante debe trabajar solo en su rama, leer la tabla maestra sin sobrescribirla y guardar nuevos resultados en carpetas claramente identificadas dentro de `outputs/`. Los cambios se integran mediante pull requests breves; antes de fusionar, se debe comprobar que no cambien los 512 registros ni el esquema base de la tabla maestra.

## Archivos compartidos

Se versionan los scripts, la documentación, `requirements.txt`, el subconjunto `data/selected/PE_200907/`, los datos derivados necesarios, la tabla maestra y los productos finales de `outputs/PE_200907/`. Se mantienen fuera del repositorio la descarga ZIP original, la extracción completa de CAMELS-PE, entornos virtuales, cachés, credenciales, pruebas NetCDF y archivos auxiliares de LaTeX.
