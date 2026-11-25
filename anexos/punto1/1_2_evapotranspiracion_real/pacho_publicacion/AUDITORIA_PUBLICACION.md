# Auditoría de publicación — Tarea 2 de Hidrología

Fecha de preparación: 22 de noviembre de 2026.

## Alcance autorizado

Esta publicación conserva el desarrollo validado del numeral 1.2 de la Tarea 2 para la cuenca Racarumi (`PE_200907`): 1.2.1, 1.2.3, 1.2.4 y 1.2.5. El numeral **1.2.2 está expresamente excluido** porque sus resultados siguen pendientes de revisión. Tampoco se incorpora el ZIP de un compañero ni datos que provengan de él.

No se modificaron, rellenaron ni recalcularon series científicas para esta publicación.

## Auditoría A — desarrollo académico conservado

| Componente | Contenido versionado | Evidencia principal |
|---|---|---|
| Delimitación y entradas de la Tarea 1 | Polígono original, serie maestra mensual y pesos ERA5-Land | `datos/punto1/PE_200907_catchment_T1_original.gpkg`, `datos/punto1/PE_200907_master_monthly_T1_original.csv`, `datos/punto1/PE_200907_ERA5Land_grid_weights_T1_original.csv` |
| 1.2.1: balance hídrico | Script, tablas por años calendario/hidrológicos, climatología y resumen de balance | `codigo/punto1/punto_1_2_balance_largo_plazo.ps1`, `productos/punto1/punto_1_2_*.csv` |
| 1.2.3: techo energético | Descargas ERA5-Land pequeñas, procedencia, script, Rn mensual, conversiones, verificaciones, techo y fracción evaporativa | `datos/punto1/era5land_radiacion_raw/`, `codigo/punto1/punto_1_2_3_*.py`, `productos/punto1/punto_1_2_3_*.csv` y `*.json` |
| 1.2.4: GLEAM y MOD16 | Scripts de adquisición/procesamiento, pesos GLEAM, compuestos MOD16, series mensuales/anuales, controles, comparaciones y figuras | `codigo/punto1/*gleam*`, `codigo/punto1/*mod16*`, `datos/punto1/PE_200907_GLEAM_grid_weights.csv`, `datos/punto1/mod16a2gf_racarumi_composites_raw.csv`, `productos/punto1/punto_1_2_4_*` |
| 1.2.5: torres de flujo | Decisión metodológica y tabla de disponibilidad de estaciones | `productos/punto1/punto_1_2_5_decision_metodologica.md`, `productos/punto1/punto_1_2_5_disponibilidad_torres.xlsx` |
| Documentación y reproducibilidad | Guía, README de GLEAM, requisitos de Python, manifiestos, inventarios y README general | `README.md`, `tarea2_guia.pdf`, `README_GLEAM4.3.pdf`, `Log_file_GLEAM4.3.pdf`, `codigo/punto1/requirements_*.txt`, `datos/punto1/*inventory*.json` |

### Verificaciones realizadas

- Los CSV de Rn contienen 276 meses (septiembre de 2000 a agosto de 2023).
- Las series GLEAM y MOD16 contienen 252 meses y sus archivos anuales 21 años hidrológicos: AH 2002 y AH 2004–AH 2023.
- La serie maestra conserva el periodo histórico disponible (enero de 1981 a agosto de 2023); no se recortó para futuros análisis de tendencia.
- Se conservaron los controles de calidad, archivos de procedencia, verificaciones manuales, figuras y scripts, además de las tablas finales.
- Las rutas declaradas en `INTERCAMBIO_COMPANERO_1_3_Y_1_4/README.md` apuntan a los archivos originales dentro del repositorio, sin duplicar tablas grandes.

## Archivos no versionados, sin eliminación local

| Exclusión | Motivo | Mecanismo de acceso/reproducción |
|---|---|---|
| `datos/punto1/gleam4_3a_raw/E_*_GLEAM_v4.3a_MO.nc` | 23 NetCDF globales, aproximadamente 2 GB; no apropiados para Git convencional y sujetos a condiciones de acceso de GLEAM | Manifiesto con tamaños y SHA-256: `datos/punto1/gleam4_3a_raw/manifest_gleam43a_E.json`; inventario y scripts SFTP/OpenSSH en `datos/punto1/` y `codigo/punto1/` |
| `.venv/`, `__pycache__/`, `tmp/` | Entorno local, cachés, temporales y previsualizaciones reproducibles/no académicas | Regenerables a partir de requisitos y scripts |
| Archivos `.part` y `openssh_transfer_tmp/` de GLEAM | Descargas parciales o área de tránsito; no son fuentes incorporadas | Validación y adquisición documentadas en scripts de GLEAM |
| Credenciales, tokens, claves y configuraciones locales | Seguridad | El repositorio no almacena secretos; cada usuario configura sus propios accesos a CDS, GLEAM y Earth Engine |
| 1.2.2 y ZIP del compañero | Fuera del alcance autorizado y pendiente de aprobación | No se añaden ni se eliminan localmente |

## Auditoría B — continuidad para 1.3 y 1.4

El inventario detallado, con archivo, ruta relativa, variables, unidades, periodo, fuente, estado y advertencias, está en [`INTERCAMBIO_COMPANERO_1_3_Y_1_4/README.md`](INTERCAMBIO_COMPANERO_1_3_Y_1_4/README.md).

Resumen de disponibilidad:

| Numeral futuro | Disponible | Parcial | Faltante |
|---|---|---|---|
| 1.3 | Rn y Rn/λ, ET GLEAM, ET MOD16, PISCOp, IMERG, caudal, balances P−Q y temperaturas base | Clasificación de meses/periodos secos y húmedos aún no calculada | ETo FAO-56, humedad de zona de raíces, ΔS, Budyko/índice de aridez/elasticidad |
| 1.4 | Tmin, Tmean y Tmax mensuales con periodo histórico disponible | Insumos meteorológicos actuales permiten una parte exploratoria, pero no una atribución completa | ETo FAO-56, Thornthwaite, ea, u2, Rs, tendencias, sensibilidad y atribución de forzantes |

La disponibilidad **parcial** no debe declararse como cálculo terminado. En especial, la radiación neta real de superficie no es la radiación neta de referencia FAO-56 ni sustituye a `Rs`.
