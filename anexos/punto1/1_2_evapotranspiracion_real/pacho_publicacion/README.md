# Tarea 2 de Hidrología — Racarumi (PE_200907)

Repositorio de trabajo para la Tarea 2 de Hidrología. Conserva el desarrollo técnico, datos procesados, controles de calidad, scripts reproducibles y productos académicos elaborados para la cuenca Racarumi (`PE_200907`), Chancay–Lambayeque, Perú.

La publicación refleja el estado real al 22 de noviembre de 2026. No se han incluido resultados preliminares del numeral **1.2.2**, que permanece pendiente de revisión.

## Cuenca y convenciones

- Delimitación original: `datos/punto1/PE_200907_catchment_T1_original.gpkg`.
- Área usada en los procesamientos: aproximadamente 2363,30 km².
- Año hidrológico: septiembre–agosto.
- Periodo común validado de los balances y productos de ET: AH 2002 y AH 2004–AH 2023; 21 años hidrológicos y 252 meses.
- Los datos faltantes de caudal se conservan como faltantes; no se sustituyeron por cero.

## Apartados desarrollados

| Numeral | Estado | Desarrollo conservado |
|---|---|---|
| 1.2.1 — Balance hídrico | Validado | Precipitación PISCOp e IMERG, caudal, balances `P−Q`, climatología, series de años calendario e hidrológicos. |
| 1.2.2 — Propagación del error | **Excluido** | Pendiente de revisión metodológica; no se publican resultados preliminares. |
| 1.2.3 — Techo energético | Validado | ERA5-Land `ssr + str`, radiación neta real de superficie, conversión `Rn/λ`, techo anual y fracción evaporativa. |
| 1.2.4 — Productos independientes de ET | Validado | GLEAM4.3a y MOD16A2GF, extracción espacial, controles de calidad, comparaciones, tablas y figuras. |
| 1.2.5 — Torres de flujo | Diagnóstico documental | Disponibilidad, representatividad, fuentes y decisión de no realizar validación local directa. |
| 1.3–1.6 | Pendientes | Ver `INTERCAMBIO_COMPANERO_1_3_Y_1_4/README.md` para los insumos existentes y faltantes. |

## Organización

```text
codigo/punto1/       Scripts Python y PowerShell para 1.2.1, 1.2.3 y 1.2.4.
datos/punto1/        Delimitación, pesos espaciales, series de entrada y metadatos.
productos/punto1/    Tablas, controles, validaciones, metodologías, figuras y diagnóstico 1.2.5.
INTERCAMBIO_COMPANERO_1_3_Y_1_4/
                     Índice de insumos para continuar 1.3 y 1.4 sin duplicar datos.
anexos/              Evidencia adicional cuando aplique.
```

## Datos y metodologías principales

### 1.2.1 — Balance hídrico

- Serie mensual original de la Tarea 1: `datos/punto1/PE_200907_master_monthly_T1_original.csv`.
- PISCOp (`camels_precip_mm_month`), IMERG (`imerg_precip_mm_month`) y caudal de lámina (`runoff_mm_month`) se preservan sin alterar.
- Resultados por año hidrológico: `productos/punto1/punto_1_2_anios_hidrologicos_sep_ago.csv`.
- El script `codigo/punto1/punto_1_2_balance_largo_plazo.ps1` genera las tablas del balance para el periodo común.

### 1.2.3 — Techo energético

- Fuente: ERA5-Land Monthly Means, campos `surface_net_solar_radiation` (`ssr`) y `surface_net_thermal_radiation` (`str`).
- Se aplicó `Rn = SSR + STR` con los signos originales de ECMWF y ponderación espacial de las 33 celdas originales de Racarumi.
- Para septiembre de 2022 a agosto de 2023 se usó la solución documentada de ECMWF basada en el promedio mensual por hora a las 00 UTC. La metodología y procedencia se conservan en `datos/punto1/punto_1_2_3_era5land_radiacion_pendiente.md`.
- Serie final: `productos/punto1/punto_1_2_3_radiacion_neta_real_era5land_mensual.csv`. La columna `rn_monthly_energy_j_m2` es Rn mensual real de superficie en J/m² y `energy_equivalent_mm_month` corresponde a `Rn/λ` en mm/mes, con `λ = 2,45×10^6 J/kg`.

### 1.2.4 — GLEAM4.3a y MOD16A2GF

- GLEAM4.3a: variable mensual `E`, en `mm.month-1`; ponderación propia sobre la grilla de 0,1° con 35 celdas. Series finales en `productos/punto1/punto_1_2_4_gleam_et_mensual.csv` y `productos/punto1/punto_1_2_4_gleam_et_anual_hidrologico.csv`.
- MOD16A2GF v6.1: colección Earth Engine `MODIS/061/MOD16A2GF`; se usó `ET` con factor 0,1 y se conservó `ET_QC` como métrica. Los compuestos de ocho días se repartieron por días de solapamiento. Series finales en `productos/punto1/punto_1_2_4_mod16_et_mensual.csv` y `productos/punto1/punto_1_2_4_mod16_et_anual_hidrologico.csv`.
- Metodología, cobertura y limitaciones: archivos `*_metodo_y_control.md`, `*_control_calidad.json`, comparación anual, climatología y figuras dentro de `productos/punto1/`.

### 1.2.5 — Torres de flujo

No se identificó una torre que reuniera a la vez representatividad de Racarumi, cercanía, periodo suficiente y datos públicos adecuados. Por ello no se hizo una validación cuantitativa con torres no representativas. La decisión, fuentes y tabla verificable están en:

- `productos/punto1/punto_1_2_5_decision_metodologica.md`
- `productos/punto1/punto_1_2_5_disponibilidad_torres.xlsx`

## Reproducción

1. Crear un entorno aislado de Python. El entorno `.venv/` no se versiona.
2. Para radiación ERA5-Land: instalar `codigo/punto1/requirements_punto_1_2_3.txt` y configurar las credenciales de CDS únicamente en el perfil local del usuario. Ejecutar `codigo/punto1/punto_1_2_3_radiacion_neta_era5land.py` si se requiere repetir la adquisición y procesamiento.
3. Para GLEAM y MOD16: instalar `codigo/punto1/requirements_punto_1_2_4.txt`. GLEAM requiere credenciales SFTP propias y Earth Engine requiere autorización local y el proyecto configurado por el usuario. Ninguna credencial se guarda en el repositorio.
4. Ejecutar, según se necesite, `procesar_gleam43a_racarumi.py`, `extraer_mod16a2gf_racarumi.py` y `cierre_punto_1_2_4.py`. Todos usan rutas relativas al repositorio.

Los scripts de descarga de GLEAM validan dimensiones, meses, unidades, valores de relleno y SHA-256. Los scripts de OpenSSH conservados no contienen usuarios ni contraseñas.

## Archivos originales grandes no versionados

Los 23 NetCDF globales anuales de GLEAM4.3a (`E_2001...E_2023_GLEAM_v4.3a_MO.nc`) suman aproximadamente 2 GB y no se publican en Git convencional. No se eliminaron localmente. Para reproducirlos:

- Consulte `datos/punto1/gleam4_3a_raw/manifest_gleam43a_E.json`: nombres, tamaños, unidades, dimensiones, periodos, valores de relleno y SHA-256.
- Consulte `datos/punto1/gleam4_3a_sftp_inventory.json` y `codigo/punto1/descargar_gleam43a_mensual.py`.
- Solicite el acceso académico al proveedor oficial GLEAM y respete sus condiciones de redistribución.

Las series extraídas de Racarumi, pesos de grilla, controles de calidad y resultados anuales sí están versionados, por lo que no es necesario volver a descargar esos NetCDF para desarrollar 1.3 o 1.4.

Los NetCDF pequeños de ERA5-Land usados para 1.2.3 sí se conservan en `datos/punto1/era5land_radiacion_raw/` junto al archivo de procedencia y el script de procesamiento.

## Información para 1.3 y 1.4

La carpeta [INTERCAMBIO_COMPANERO_1_3_Y_1_4](INTERCAMBIO_COMPANERO_1_3_Y_1_4/README.md) constituye el índice operativo: especifica para cada variable si está disponible, parcial o faltante, su ruta, unidades, periodo y advertencias. No asume que los insumos no calculados existan.

## Seguridad y publicación

El repositorio no debe incluir secretos, contraseñas, tokens, `.cdsapirc`, archivos `.env`, claves privadas, entorno virtual, cachés, descargas parciales ni NetCDF globales pesados. La configuración de exclusiones está en `.gitignore`.
