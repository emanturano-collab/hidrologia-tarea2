# GLEAM4.3a: evapotranspiración real de Racarumi

## Fuente y validación

Se utilizaron los archivos anuales `E_2001_GLEAM_v4.3a_MO.nc` a `E_2023_GLEAM_v4.3a_MO.nc`. Los tamaños se comprobaron contra el inventario SFTP. Cada archivo contiene la variable `E`, 12 meses, dimensiones `time × lat × lon = 12 × 1800 × 3600`, unidad `mm.month-1` y `_FillValue = -999`. Se calcularon y conservaron hashes SHA-256 en `datos/punto1/gleam4_3a_raw/manifest_gleam43a_E.json`. Los archivos 2002–2023 solo se trasladaron desde el área temporal de transferencia después de superar conjuntamente las validaciones. El archivo 2001 se mantuvo intacto.

La lectura se realizó con `mask_and_scale=False` para comprobar directamente `-999` y los NaN almacenados. En el cálculo espacial se excluyeron únicamente valores no finitos o iguales a `-999`. La variable mensual ya representa milímetros por mes; no se multiplicó por el número de días.

## Ponderación espacial

La grilla GLEAM4.3a tiene resolución de 0,1° y centros en coordenadas terminadas en 0,05°. Se construyeron polígonos de celda de 0,1° alrededor de cada centro y se intersectaron con la delimitación original `PE_200907` de Racarumi. Las áreas de intersección se calcularon en EPSG:6933, una proyección equivalente de área.

Se obtuvieron 35 celdas con intersección positiva. El área total representada fue 2.363.301.796,30 m² y la suma de los pesos fue 1,0000000000000002 (diferencia numérica de redondeo). Los pesos se guardaron en `datos/punto1/PE_200907_GLEAM_grid_weights.csv`. No se reutilizaron los pesos de ERA5-Land.

Para cada mes se calculó la media espacial ponderada por el área de intersección. La cobertura espacial válida fue 100 % en los 252 meses seleccionados. No hubo meses con valores negativos en las celdas de la cuenca.

## Periodo y agregación

Se conservaron exclusivamente AH 2002 y AH 2004–AH 2023, definidos de septiembre a agosto. Son 21 años hidrológicos y 252 meses. AH 2003 no se interpoló ni se incorporó. Cada total anual es la suma directa de sus 12 valores mensuales en `mm/año`; la diferencia máxima entre la suma mensual independiente y la tabla anual fue 0,0 mm.

## Comparación preliminar para el mismo periodo

| Serie | Media (mm/año) |
|---|---:|
| GLEAM4.3a | 740,48 |
| MOD16A2GF v6.1 | 795,55 |
| ET = PISCOp − Q | 603,17 |
| ET = IMERG − Q | 73,11 |

En promedio, GLEAM fue 55,07 mm/año menor que MOD16, 137,31 mm/año mayor que `PISCOp − Q` y 667,37 mm/año mayor que `IMERG − Q`. Estas son diferencias descriptivas para los mismos 21 años, no conclusiones causales. Las estimaciones `P − Q` son balances de largo plazo y su interpretación como ET supone que el cambio de almacenamiento medio, ΔS, sea aproximadamente cero; además pueden reflejar errores o sesgos en precipitación y caudal.

## Reproducibilidad

El procedimiento se ejecuta con `codigo/punto1/procesar_gleam43a_racarumi.py`. La acción `validate-promote` valida y promueve los NetCDF; la acción `process` recalcula pesos, series, agregaciones, comparaciones y controles de calidad. No modifica los productos de MOD16 ni los balances del numeral 1.2.1.
