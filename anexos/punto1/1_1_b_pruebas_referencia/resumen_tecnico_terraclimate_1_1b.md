# TerraClimate v1.1 - contraste de demanda para 1.1.b

## Validación e integración espacial

El NetCDF validado contiene `pet` en mm mensuales, con 512 meses continuos de
1981-01 a 2023-08 y sin valores faltantes. La ponderación usa áreas de
intersección en EPSG:6933: 219 celdas intersectan Racarumi,
sus pesos suman 1.000000000000 y reproducen
2363.301796 km², frente a
2363.301796 km² de la delimitación.

## Comparación con ETo FAO-56 ERA5-Land

El periodo común de meses completos es 1981-01-01 a
2023-07-01 (n=511). Para PET TerraClimate menos
ETo preliminar: Pearson=0.8992;
Spearman=0.8882; sesgo=1.361
mm/mes; MAE=4.017 mm/mes; RMSE=4.903 mm/mes.
El sesgo positivo indica que TerraClimate fue, en promedio, mayor que la ETo
ERA5-Land preliminar en 1.361 mm/mes.
La alta asociación temporal describe una señal estacional compartida; no prueba
equivalencia física entre productos.

## Periodo común de tres productos

PISCOeo_pm termina en 2016; por ello el periodo de tres productos es
1981-01-01 a 2016-12-01
(n=432). TerraClimate-PISCOeo_pm: Pearson=0.8867,
Spearman=0.8965, sesgo=2.440
mm/mes, MAE=4.989 mm/mes y RMSE=6.226
mm/mes. TerraClimate-ETo ERA5-Land en el mismo periodo: Pearson=0.9051,
Spearman=0.8933, sesgo=1.456
mm/mes, MAE=3.971 mm/mes y RMSE=4.815
mm/mes.
El sesgo positivo TerraClimate-PISCOeo_pm (2.440 mm/mes)
indica mayor demanda de TerraClimate en promedio. Las diferencias pueden provenir
de la formulación (TerraClimate v1.1 emplea Penman-Monteith modificado por CO2),
las mallas, las climatologías y los datos meteorológicos parentales, y no deben
atribuirse automáticamente a error de uno de los productos.

## Independencia y limitaciones

La serie se identifica como TerraClimate v1.1. Su PET es ETo de referencia con
Penman-Monteith modificado por CO2. No es completamente independiente de
ERA5-Land: v1.1 incorpora anomalías mensuales ERA5, climatologías CHELSA y
correcciones de vapor CRU TS4.09. Es una comparación de producto, resolución y
formulación, no una validación independiente basada en estación. La ETo FAO-56
comparada mantiene cobertura espacial preliminar de 90.1264 %;
no se interpreta como estimación final de la cuenca.
