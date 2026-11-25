# Apartado 1.1.b - resultados reproducibles disponibles

## Estado y alcance

Se ejecutaron dos comprobaciones que no requieren descargas nuevas: comparación
con PET de CAMELS-PE/PISCOeo_pm y comprobación física P-Q. La ETo usada sigue
siendo la versión **preliminar** con 90.1264 % de cobertura
espacial; faltan celdas ERA5-Land, por lo que no representa un resultado final de
cuenca.

## Producto de demanda comparativo

Periodo común de meses completos: 1981-01-01 a 2016-12-01.
N = 432 meses. Pearson = 0.6972;
Spearman = 0.6946; sesgo PET-ETo =
-0.984 mm/mes; MAE =
7.970 mm/mes; RMSE = 9.046 mm/mes.

PISCOeo_pm es una serie independiente en sus insumos espaciales y resolución,
pero utiliza igualmente FAO Penman-Monteith. Por tanto, funciona como contraste
de producto, no como validación observacional independiente.

## Comprobación física P-Q

Usando 26 años completos (1982-2021):
P = 1082.65 mm/año; Q =
477.27 mm/año; P-Q =
605.37 mm/año; ETo preliminar =
1181.71 mm/año.
ETo - (P-Q) = 576.34 mm/año.

P-Q aproxima evapotranspiración real de largo plazo sólo con cambios de
almacenamiento y transferencias despreciables; no es una referencia directa de
ETo. Cualquier incoherencia requiere revisar representatividad de P, regulación,
transferencias, flujo subterráneo y almacenamiento; no se corrige alterando datos.

## Prueba de estación / estado de cumplimiento

El archivo local de estación identifica Racarumi como punto de aforo con caudal
observado y no contiene Tmax/Tmin observadas, humedad, viento, radiación o
presión. Por ello no permite recalcular una ETo de estación. No se ha inventado
ni estimado arbitrariamente una estación. El inventario prioriza Racarrumi
(~0.8 km) y Llama (~25.2 km) como candidatas SENAMHI, pero tipo, periodo y
variables deben confirmarse antes de considerarlas elegibles. La solicitud
manual está en `solicitud_manual_estacion_senamhi.md`. Hasta contar con una
serie meteorológica observada o datos de tanque, sólo se cumple una de las tres
categorías de contraste exigidas por la guía (producto de demanda), y el apartado
1.1.b no está terminado.
