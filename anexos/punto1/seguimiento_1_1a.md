# Seguimiento - Tarea 2, Punto 1, apartado 1.1.a

## Completado en esta ejecución

- Auditoría de ZIP y NetCDF, incluyendo continuidad temporal, coordenadas, variables, unidades y valores no finitos.
- Procesamiento FAO-56 por punto para los puntos completos: P1, P2, P3, P4, P5, P6, P7, P8.
- Series diarias y mensuales, comprobación de radiación, comprobación algebraica de la ecuación y figura de comparación diaria/mensual.

## Resultados reproducibles creados

- `datos/punto1/procesados/1_1_a_fao56/fao56_eto_diaria_por_punto_validado.csv`
- `datos/punto1/procesados/1_1_a_fao56/fao56_eto_mensual_por_punto_validado.csv`
- `datos/punto1/metadatos/era5land_disponibilidad_1_1a.csv`
- `datos/punto1/metadatos/era5land_fuentes_sha256_1_1a.csv`
- `datos/punto1/metadatos/era5land_variables_unidades_1_1a.csv`
- `productos/punto1/1_1_demanda_atmosferica/tablas/fao56_resumen_diferencia_diaria_vs_mensual.csv`
- `productos/punto1/1_1_demanda_atmosferica/figuras/fao56_comparacion_diaria_vs_mensual_por_punto.png`
- `productos/punto1/1_1_demanda_atmosferica/comprobaciones/` (dos comprobaciones CSV).

## Limitaciones y decisiones pendientes

- No hay ETo espacialmente promediada para Racarumi: antes debe resolverse una ponderación espacial válida.
- Los ocho puntos de esta selección están completos; aún falta una ETo espacialmente representativa de la cuenca.
- Antes de 1.1.b debe definirse una ponderación que represente las 33 celdas ERA5-Land de la Tarea 1.
- La comparación de producto/estación independiente pertenece a 1.1.b y no se realizó aquí.

## Próximo apartado

Definir la ponderación espacial y después desarrollar 1.1.b (pruebas independientes de la referencia FAO-56).
# Estado de cobertura espacial ERA5-Land (actualización 2026-11-21)

- Las ocho series horarias P1--P8 ya validadas se conservan intactas y cubren el 32.583635173883463 % del peso espacial de la cuenca.
- Se validó el inventario de 25 celdas pendientes: identificadores y coordenadas únicos; peso conjunto 0.674163648261164. No se solicitó ni descargó ningún dato nuevo.
- Se preparó `codigo/punto1/1_1_demanda_atmosferica/1_1_a_fao56/download_era5land_25_celdas.py`. Lee el inventario, usa `reanalysis-era5-land-timeseries`, solicita únicamente las seis variables requeridas en formato NetCDF y valida ZIP, variables, unidades, fechas, frecuencia, continuidad, coordenada de la celda retornada, valores no finitos y SHA-256.
- El manifiesto reproducible es `datos/punto1/metadatos/era5land_25_celdas_manifest.csv`: actualmente 25 `PENDIENTE`, 0 descargadas, 0 validadas.
- El entorno no tiene `.cdsapirc` ni `cdsapi`; por política no se intentó eludir la autenticación ni enviar la prueba. Antes de ejecutar la prueba el usuario debe aceptar la licencia en CDS, crear su configuración privada e instalar la dependencia indicada en `requirements_1_1a.txt`.
- La ETo espacial de Racarumi sigue pendiente: no se calculará hasta validar las 33 celdas y sus pesos.
- Prueba CDS del 2026-11-21: `ERA5L_01` alcanzó el servicio al omitir temporalmente un proxy local no disponible, pero CDS respondió `401 Unauthorized` / `operation not allowed` en dos intentos. Se detuvo el proceso antes del tercer reintento; no se descargó ZIP ni quedó archivo parcial. Revisar licencia aceptada y token de la misma cuenta antes de reanudar.
- Diagnóstico local posterior: no existen `CDSAPI_KEY`, `CDSAPI_URL` ni `CDSAPI_RC`; por tanto no hay sobrescritura por entorno. Python y `cdsapi` resuelven el mismo `%USERPROFILE%\\.cdsapirc`; el archivo tiene URL exacta, UTF-8 válido, dos líneas `url`/`key`, sin líneas extra ni espacios extremos. La configuración moderna de CDS usa un token personal único; el descargador no le impone formato heredado y usa la inicialización oficial `cdsapi.Client()`.
- Prueba final controlada: con `cdsapi 0.7.7` actualizado y su cliente moderno interno `ecmwf.datastores`, una única petición de `ERA5L_01` volvió a responder `401 Authentication failed / operation not allowed`. Se abandona la automatización hasta que CDS resuelva el acceso de la cuenta. Para continuar sin API se preparó `anexos/punto1/tabla_descarga_manual_era5land_25.md`.

