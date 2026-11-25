# Tarea 2 de Hidrología (202602): evapotranspiración y diseño hidrológico

## Integrantes

- Andrés Francisco Idrobo Hidrobo
- Enmaly Aleli Manturano Grajeda
- Jeyson Cristian Javier Irpanoca

Grupo: **GXX** (pendiente: número asignado en la Tarea 1).

## Contenido de la entrega

| Ruta | Contenido |
|---|---|
| `T2_202602_GNN_informe.pdf` | Informe (se genera desde `anexos/informe_fuente/informe.tex`). |
| `T2_202602_GNN_presentacion.pdf` | Presentación oral (desde `anexos/informe_fuente/presentacion.tex`). |
| `codigo/punto1/` | Scripts del punto 1, ordenados por apartado (1.1 a 1.6). |
| `codigo/punto2/` | Scripts del punto 2. `analisis_final_punto2.py` produce todas las cifras del punto 2 del informe. |
| `datos/punto1/` | Series de la Tarea 1 (CAMELS-PE, PISCO, IMERG), recortes de ERA5-Land, GLEAM y MOD16 a la cuenca, y metadatos. |
| `datos/punto2/` | Serie DWD de 10 minutos, DEM SRTM recortado, ESA WorldCover recortado, KOSTRA-DWD-2020 y metadatos. |
| `productos/punto1/` | Tablas, series mensuales y anuales y figuras del punto 1. `cifras_punto1.tex` reúne las cifras citadas en el informe. |
| `productos/punto2/final/` | Tablas, figuras, `resultados_punto2.json` y `cifras_punto2.tex` del punto 2. |
| `anexos/` | Enunciado, fuente LaTeX del informe, trazabilidad, verificaciones, borradores anteriores y registro de la revisión final. |

Los archivos `T2_202602_GNN_*.pdf` solo existen dentro del ZIP: `codigo/crear_zip_entrega.py` los copia con el nombre definitivo.

## Procedencia de los datos

| Dato | Fuente y versión | Uso |
|---|---|---|
| Precipitación, caudal y temperatura de la cuenca PE_200907 | CAMELS-PE v1.0.1 (PISCOp v2.1, PISCOt v1.2) | Balance, Budyko, tendencias |
| Precipitación satelital | IMERG Final V07 (GPM_3IMERGDF), 2000-06 a 2023-08 | Sensibilidad a la lluvia |
| Variables meteorológicas horarias | ERA5-Land, `reanalysis-era5-land-timeseries`, 20 de 33 celdas (90,13 % del peso) | ETo FAO-56 y métodos alternativos |
| Radiación neta y humedad del suelo | ERA5-Land, medias mensuales | Techo energético, 1.3.2 |
| ET real | GLEAM v4.3a mensual; MOD16A2GF v6.1 | 1.2.4, 1.3, 1.5 |
| Demanda independiente | TerraClimate; PISCOeo_pm; GHCNh PEI0000SPHI (Chiclayo) | 1.1.b |
| Lluvia de 10 minutos | DWD, estación 00020 Abtsgmünd-Untergröningen, 2004-08 a 2025-12 | Punto 2 |
| DEM | SRTM 1'' (N48E009) | Microcuenca |
| Cobertura | ESA WorldCover 10 m 2021 v200 (SHA-256 en `cobertura_2_4/worldcover_sha256.txt`) | Coeficiente C |
| IDF de referencia | KOSTRA-DWD-2020 (DOI 10.5676/DWD/KOSTRA-DWD-2020) | 2.3 |

Las fechas de descarga, unidades y procesamientos de cada archivo están en `datos/punto1/METADATOS.md` y `datos/punto2/METADATOS.md`.

## Requisitos

- Python 3.9 o superior; dependencias en `codigo/requirements.txt`.
- LaTeX (pdfLaTeX) con `newtx`, `tikz`, `booktabs`, `caption` y `babel` en español, para compilar el informe.
- No se incluyen credenciales. Los scripts de descarga leen las claves de variables de entorno (`GLEAM_SFTP_PASSWORD`) o del archivo `.cdsapirc` del usuario, que no forma parte de la entrega.

## Orden de ejecución

Desde la raíz de la carpeta (todas las rutas son relativas):

```bash
pip install -r codigo/requirements.txt

# Punto 1: las tablas y figuras ya están en productos/punto1; para regenerarlas,
# ejecutar los scripts de cada apartado en este orden:
python codigo/punto1/1_1_demanda_atmosferica/1_1_a_fao56/run_fao56_1_1a_preliminar_90pct.py
python codigo/punto1/1_1_demanda_atmosferica/1_1_a_fao56/build_fao56_preliminar_90pct_products.py
python codigo/punto1/1_1_demanda_atmosferica/1_1_b_pruebas_referencia/run_1_1b_terraclimate_pet.py
python codigo/punto1/1_1_demanda_atmosferica/1_1_b_pruebas_referencia/run_1_1b_camels_pet_y_balance.py
python codigo/punto1/1_1_demanda_atmosferica/1_1_b_pruebas_referencia/run_1_1b_station_vs_era5_chiclayo.py
python codigo/punto1/1_1_demanda_atmosferica/1_1_c_metodos_alternativos/run_1_1c_metodos_alternativos.py
python codigo/punto1/1_1_demanda_atmosferica/1_1_d_explicacion_fisica/run_1_1d_explicacion_fisica.py
python codigo/punto1/1_2_evapotranspiracion_real/02_propagacion_error/run_1_2_2_propagacion_error.py
python codigo/punto1/1_2_evapotranspiracion_real/punto_1_2_3_radiacion_neta_era5land.py
python codigo/punto1/1_2_evapotranspiracion_real/punto_1_2_3_techo_energetico.py
python codigo/punto1/1_2_evapotranspiracion_real/punto_1_2_3_fraccion_evaporativa.py
python codigo/punto1/1_2_evapotranspiracion_real/cierre_punto_1_2_4.py
python codigo/punto1/1_3_regimen_evaporativo/run_1_3_regimen_evaporativo.py
python codigo/punto1/1_3_regimen_evaporativo/06_integracion_1_2_pacho/run_1_3_integracion_ET_real.py
python codigo/punto1/1_4_cambios_demanda_evaporativa/run_1_4.py
python codigo/punto1/1_4_cambios_demanda_evaporativa/run_1_4_1_auditoria.py
python codigo/punto1/1_5_paisaje/05_cierre_tecnico_1_5.py
python codigo/punto1/cifras_punto1.py

# Punto 2 (unos 10 minutos por el bootstrap y el Monte Carlo):
python codigo/punto2/analisis_final_punto2.py
python codigo/punto2/tablas_latex_punto2.py

# Informe y presentación:
cd anexos/informe_fuente
pdflatex informe.tex && pdflatex informe.tex
pdflatex presentacion.tex
cd ../..

# ZIP final (valida el nombre con la expresión regular del enunciado):
python codigo/crear_zip_entrega.py --grupo NN --apellidos Apellido1 Apellido2 Apellido3
```

Las decisiones de diseño del punto 2 (periodo de retorno, vida útil, riesgo aceptable, fórmula de tc, distribución, C urbanizado) están en `codigo/punto2/config_diseno_2_4.json`. Si se cambia un valor, al volver a ejecutar `analisis_final_punto2.py` y recompilar, todas las cifras del informe se actualizan.

## Insumos no incluidos

| Archivo | Razón y efecto |
|---|---|
| `datos/punto1/gleam4_3a_raw/E_20XX_GLEAM_v4.3a_MO.nc` | Archivos globales; se entrega el recorte de la cuenca y el periodo. |
| `ERA5_Land_Racarumi_Humedad_Suelo_1981_2023.zip` | El ZIP original de ERA5-Land no está en el repositorio (su SHA-256 está en `datos/punto1/metadatos/1_3_2_metadatos_y_control_calidad_humedad_suelo.json`). La serie procesada sí está; sin el ZIP no se puede regenerar 1.3.2 desde cero. |
| `datos/punto1/originales/era5land_chiclayo/ERA5_Land_Chiclayo_SPHI_20100101_20230101.zip` | El ZIP original no está en el repositorio; la serie procesada y sus metadatos sí (`datos/punto1/procesados/1_1_b_pruebas_referencia/`). Sin el ZIP, `run_1_1b_station_vs_era5_chiclayo.py` falla con un mensaje explícito. |
| 13 celdas de ERA5-Land (9,87 % del peso de la cuenca) | No se pudieron descargar (error 401 del CDS). La ETo se calculó sobre el 90,13 % restante con pesos renormalizados. |

## Notas

- `codigo/punto2/` conserva los scripts de versiones anteriores (`finalizar_2_4.py`, `diseno_2_4_provisional.py` y otros) y sus salidas en `datos/punto2/Abtsgmuend_Untergroeningen/diseno_2_4/`. Esas cifras quedaron **reemplazadas** por las de `productos/punto2/final/`; ver `anexos/registro_revision_final.md`.
- El estado de ejecución de cada script del punto 1 en la verificación prefinal está en `anexos/historial_versiones/README_entrega_prefinal.md`.
