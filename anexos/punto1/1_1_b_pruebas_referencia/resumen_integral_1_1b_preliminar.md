# Resumen integral del apartado 1.1.b - versión preliminar

## Datos y pruebas ejecutadas

La comparación CAMELS-PE/PISCOeo_pm frente a ETo FAO-56 preliminar cubrió
432 meses (1981-2016): Pearson=0.6972,
Spearman=0.6946, sesgo PET-ETo=-0.984 mm/mes,
MAE=7.970 y RMSE=9.046.

TerraClimate v1.1, ponderado con 219 celdas por área de intersección, se comparó
con ETo ERA5-Land en 511 meses: Pearson=0.8992,
Spearman=0.8882, sesgo=1.361
mm/mes, MAE=4.017 y RMSE=4.903.
PISCOeo_pm y TerraClimate son contrastes de la misma categoría (productos de
demanda); TerraClimate v1.1 utiliza anomalías ERA5 y no constituye independencia
total respecto a ERA5-Land.

El balance físico usó 26 años completos:
P=1082.65, Q=477.27,
P-Q=605.37 y ETo preliminar=
1181.71 mm/año. P-Q aproxima ET real bajo
supuestos de balance y no se interpretó como ETo.

## Estación NOAA PEI0000SPHI

Se validaron 13 PSV NOAA GHCNh (2010-2022), con 3690 días que
cumplen al menos 18 horas de temperatura, punto de rocío y viento, y
101 meses completos. La ETo FAO-56 condicional de Chiclayo
usa Rs por ecuación 50 (kRs=0.19, sensibilidad kRs=0.16) y presión de ecuación
7 cuando la presión observada no tiene cobertura diaria suficiente. La altura
instrumental de viento no está en los PSV: se declara un escenario convencional
10 m a 2 m y otro sin ajuste para sensibilidad.

La estación costera (29.6 m) no representa automáticamente Racarumi, cuya ETo
preliminar ponderada corresponde a una elevación media aproximada de 2343 m y
relieve andino. La celda existente P1 queda a 61.9 km;
por tanto no se comparó la estación con el promedio de cuenca ni con P1.

## Prueba local estación - ERA5-Land

La celda ERA5-Land retornada fue -6.8, -79.8, a corta distancia de la estación,
y se comparó durante 3690 días y 101 meses completos.
Con radiación propia ERA5 (`ssrd`): Pearson=0.6487,
Spearman=0.6625, sesgo NOAA-ERA5=
0.105 mm/día, MAE=0.518
y RMSE=0.670. Con radiación Eq.50 kRs=0.19 en ambas:
Pearson=0.7244, Spearman=0.7302,
sesgo=0.407 mm/día, MAE=
0.561 y RMSE=0.713.

## Estado

Se concluye **1.1.b en versión preliminar**: se completaron dos categorías de
prueba exigidas (producto de demanda y estación meteorológica) y la comprobación
física P-Q. La estación costera externa evalúa localmente ERA5-Land; no demuestra
exactitud sobre toda Racarumi. La ETo representativa de cuenca no es definitiva:
sigue pendiente el 9.8736 % de cobertura espacial ERA5-Land.
