# Intercambio para los numerales 1.3 y 1.4

Este directorio es un índice de trabajo para ubicar los insumos existentes sin duplicar las fuentes ni modificar series validadas. Los enlaces son relativos al repositorio. Las variables que no existen se declaran como **faltantes**: no deben inferirse de archivos con otro significado físico.

## Convenciones comunes

- Cuenca: Racarumi `PE_200907`; delimitación original: [`../datos/punto1/PE_200907_catchment_T1_original.gpkg`](../datos/punto1/PE_200907_catchment_T1_original.gpkg).
- Año hidrológico: septiembre–agosto.
- Periodo común de productos/balance: AH 2002 y AH 2004–AH 2023, 21 años hidrológicos y 252 meses, desde septiembre de 2001 hasta agosto de 2023. AH 2003 no se incluye por datos de caudal incompletos.
- La serie meteorológica de entrada de la Tarea 1 cubre enero de 1981 a agosto de 2023 (512 meses). Para tendencias de 1.4, no se debe recortar automáticamente al periodo común.

## Auditoría B — insumos del numeral 1.3

| Dato requerido | Archivo y enlace | Variables / unidades | Periodo | Estado | Advertencia metodológica |
|---|---|---|---|---|---|
| Radiación neta real mensual de superficie | [`punto_1_2_3_radiacion_neta_real_era5land_mensual.csv`](../productos/punto1/punto_1_2_3_radiacion_neta_real_era5land_mensual.csv) | `rn_monthly_energy_j_m2`: J/m² por mes | sep. 2000–ago. 2023; 276 meses | Disponible | Es `SSR + STR` de ERA5-Land sobre superficie real. **No es** radiación neta de pasto de referencia FAO-56. |
| Lámina energética mensual `Rn/λ` | [misma serie de Rn](../productos/punto1/punto_1_2_3_radiacion_neta_real_era5land_mensual.csv) | `energy_equivalent_mm_month`: mm/mes; `λ=2,45×10^6 J/kg` | sep. 2000–ago. 2023 | Disponible | Usar la misma fecha mensual y conservar signos/unidades ya validados. |
| Techo energético anual | [`punto_1_2_3_techo_energetico_anual.csv`](../productos/punto1/punto_1_2_3_techo_energetico_anual.csv) | J/m²/año y mm/año | AH 2001–AH 2023; completos según indicador | Disponible | Para comparar ET usar únicamente los años comunes válidos. |
| ET GLEAM mensual | [`punto_1_2_4_gleam_et_mensual.csv`](../productos/punto1/punto_1_2_4_gleam_et_mensual.csv) | `et_gleam_mm_month`, mm/mes | 252 meses, AH 2002 y AH 2004–2023 | Disponible | Producto GLEAM4.3a, variable E mensual; ponderación específica de 35 celdas. |
| ET GLEAM anual | [`punto_1_2_4_gleam_et_anual_hidrologico.csv`](../productos/punto1/punto_1_2_4_gleam_et_anual_hidrologico.csv) | mm/año hidrológico | 21 AH válidos | Disponible | Sumas de 12 meses. |
| ET MOD16 mensual | [`punto_1_2_4_mod16_et_mensual.csv`](../productos/punto1/punto_1_2_4_mod16_et_mensual.csv) | `et_mm`, mm/mes | 252 meses, AH 2002 y AH 2004–2023 | Disponible | MOD16A2GF v6.1; compuestos repartidos uniformemente por días de solapamiento. |
| ET MOD16 anual | [`punto_1_2_4_mod16_et_anual_hidrologico.csv`](../productos/punto1/punto_1_2_4_mod16_et_anual_hidrologico.csv) | mm/año hidrológico | 21 AH válidos | Disponible | Revisar cobertura y `ET_QC` en el control de calidad. |
| Balance PISCOp−Q e IMERG−Q | [`punto_1_2_anios_hidrologicos_sep_ago.csv`](../productos/punto1/punto_1_2_anios_hidrologicos_sep_ago.csv) | `et_l_mm_year`, `et_i_mm_year`, mm/año | AH 2001–AH 2023; 21 completos para comparación | Disponible | `P−Q` es una estimación de balance, no una observación directa de ET; está condicionada a `ΔS≈0`. |
| Precipitación mensual PISCOp e IMERG | [`PE_200907_master_monthly_T1_original.csv`](../datos/punto1/PE_200907_master_monthly_T1_original.csv) | `camels_precip_mm_month`, `imerg_precip_mm_month`, mm/mes | PISCOp ene. 1981–ago. 2023; IMERG según disponibilidad indicada por sus banderas | Disponible / parcial para IMERG histórico | Respetar columnas de disponibilidad, completitud y meses faltantes. |
| Precipitación anual de ambas fuentes | [`punto_1_2_anios_hidrologicos_sep_ago.csv`](../productos/punto1/punto_1_2_anios_hidrologicos_sep_ago.csv) | `pl_mm_year`, `pi_mm_year`, mm/año | AH 2001–AH 2023, con estado | Disponible | Para años incompletos, no sustituir caudal faltante ni usar ET calculada. |
| Caudal mensual | [serie maestra](../datos/punto1/PE_200907_master_monthly_T1_original.csv) | `flow_obs_mean_mm_day` (mm/día) y `runoff_mm_month` (mm/mes) | ene. 1981–ago. 2023; con banderas | Disponible | Para balances mensuales/anuales de lámina, usar `runoff_mm_month`; no rellenar vacíos con cero. |
| Caudal anual | [años hidrológicos](../productos/punto1/punto_1_2_anios_hidrologicos_sep_ago.csv) | `q_mm_year`, mm/año | AH 2001–AH 2023; solo completos | Disponible | Consultar `status` y `missing_q_months`. |
| ETo FAO-56 mensual y anual | — | — | — | **Faltante** | No existe un cálculo FAO-56 validado en este repositorio. Rn de superficie real no es, por sí sola, la radiación de referencia requerida por FAO-56. |
| Humedad del suelo de zona de raíces | — | — | — | **Faltante** | No se ha descargado ni procesado una serie de humedad de suelo de raíces para Racarumi. |
| Cambio de almacenamiento `ΔS` | — | — | — | **Faltante** | No se ha estimado. No inferirlo directamente de `P−Q−ET` sin definir una metodología y fuentes. |
| Budyko, índice de aridez y elasticidad | — | — | — | **Faltante** | Requieren ETo/PET y/o cálculo posterior; no han sido ejecutados. |
| Meses limitados por energía o agua | Parcialmente [`Rn/λ`](../productos/punto1/punto_1_2_3_radiacion_neta_real_era5land_mensual.csv) y ET de productos | Rn/λ y ET, mm/mes | 252 meses comunes de ET | **Parcial** | Hay Rn/λ y ET, pero no existe clasificación final ni ETo/índice de aridez. |
| Años secos y húmedos | Precipitación, caudal y ET en archivos anteriores | mm/mes y mm/año | según cada serie | **Parcial** | Los insumos existen; la clasificación y comparación final no han sido calculadas. |

### Controles relevantes para 1.3

- [Verificación y fuente de Rn ERA5-Land](../productos/punto1/punto_1_2_3_verificacion_manual.json)
- [Techo energético versus balances](../productos/punto1/punto_1_2_3_techo_energetico_vs_balance_anual.csv)
- [Control de calidad GLEAM](../productos/punto1/punto_1_2_4_gleam_control_calidad.json)
- [Control de calidad MOD16](../productos/punto1/punto_1_2_4_mod16_control_calidad.json)
- [Comparación anual de productos y balances](../productos/punto1/punto_1_2_4_comparacion_anual_productos_y_balance.csv)

## Auditoría B — insumos del numeral 1.4

| Dato requerido | Archivo y enlace | Variables / unidades | Periodo | Estado | Observación |
|---|---|---|---|---|---|
| Temperatura del aire mensual | [`PE_200907_master_monthly_T1_original.csv`](../datos/punto1/PE_200907_master_monthly_T1_original.csv) | `tmin_mean_c`, `tmean_mean_c`, `tmax_mean_c`, °C | ene. 1981–ago. 2023 | Disponible | Conservar todo el periodo para análisis de tendencias y sus columnas de completitud. |
| ETo FAO-56 mensual y anual | — | — | — | **Faltante** | Debe calcularse con una fuente y metodología explícitas. |
| Thornthwaite mensual y anual | — | — | — | **Faltante** | No se ha calculado ni validado en el proyecto. |
| Presión real de vapor `ea` | — | — | — | **Faltante** | No está en la serie maestra actual. |
| Velocidad del viento a 2 m `u2` | — | — | — | **Faltante** | No está en la serie maestra actual. |
| Radiación solar incidente `Rs` | — | — | — | **Faltante** | `Rn` no sustituye a `Rs`; se requiere adquirir/procesar una fuente apropiada. |
| Series meteorológicas completas para tendencias | [serie maestra](../datos/punto1/PE_200907_master_monthly_T1_original.csv) | PISCOp, caudal, Tmin/Tmean/Tmax y banderas | ene. 1981–ago. 2023 | **Parcial** | Las temperaturas y parte del balance están disponibles; faltan `ea`, `u2`, `Rs` y ETo. |
| Resultados de tendencias y sensibilidad | — | — | — | **Faltante** | No se han calculado. |
| Atribución de cambios de ETo a forzantes | Temperatura disponible en [serie maestra](../datos/punto1/PE_200907_master_monthly_T1_original.csv) | °C | ene. 1981–ago. 2023 | **Parcial** | No puede completarse sin `ea`, `u2`, `Rs` y el cálculo de ETo. |
| Comparación FAO-56–Thornthwaite | — | — | — | **Faltante** | Ambos productos deben calcularse primero. |

## Fuentes originales y reproducibilidad

| Insumo | Fuente/origen | Script o metadato reproducible |
|---|---|---|
| Precipitación, caudal y temperatura de Tarea 1 | Serie original de la Tarea 1/CAMELS-PE, preservada localmente | [serie mensual original](../datos/punto1/PE_200907_master_monthly_T1_original.csv) |
| Rn real de superficie | ERA5-Land Monthly Means de Copernicus CDS | [script](../codigo/punto1/punto_1_2_3_radiacion_neta_era5land.py), [fuente y control](../datos/punto1/punto_1_2_3_era5land_radiacion_fuente.json) |
| GLEAM4.3a E | GLEAM, NetCDF mensual global | [procesamiento](../codigo/punto1/procesar_gleam43a_racarumi.py), [manifiesto de originales](../datos/punto1/gleam4_3a_raw/manifest_gleam43a_E.json) |
| MOD16A2GF v6.1 | Google Earth Engine, `MODIS/061/MOD16A2GF` | [extracción](../codigo/punto1/extraer_mod16a2gf_racarumi.py), [compuestos empleados](../datos/punto1/mod16a2gf_racarumi_composites_raw.csv) |

## Qué no hacer

- No reemplazar faltantes de caudal por cero.
- No mezclar años calendario con años hidrológicos septiembre–agosto.
- No usar Rn real de superficie como si fuera radiación neta de pasto FAO-56, ni como sustituto directo de `Rs`.
- No afirmar que existen ETo, Thornthwaite, `ea`, `u2`, humedad de raíz, `ΔS`, Budyko o tendencias: permanecen pendientes.
- No volver a descargar los NetCDF globales de GLEAM para trabajar con las series de ET ya extraídas. Si se necesita repetir la extracción espacial, seguir el manifiesto, los scripts y las condiciones oficiales de acceso.
