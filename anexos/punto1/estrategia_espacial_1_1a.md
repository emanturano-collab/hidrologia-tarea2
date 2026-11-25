# Estrategia espacial para completar FAO-56 - apartado 1.1.a

## Hallazgo verificable

La delimitación `PE_200907_catchment.gpkg` está en `EPSG:4326` y su área proyectada UTM 17S es 2364.37 km². La Tarea 1 tiene 33 celdas ERA5-Land con pesos de intersección que suman 1.000000000000.

Los puntos P1-P8 son ocho celdas reales de esa tabla y acumulan un peso de 0.325836 (32.58 %). Quedan 25 celdas, con 67.42 % del peso, sin series horarias completas. Por ello no es defendible calcular todavía ETo de cuenca con P1-P8, ni rellenar las faltantes por interpolación.

## Alternativas evaluadas

| Alternativa | Cobertura y variables | Ventaja | Limitación | Decisión |
|---|---|---|---|---|
| A. Reusar insumos existentes | Ocho celdas horarias; 32.58 % del peso. Existe temperatura mensual ponderada de Tarea 1. | No requiere descarga. | No aporta las seis variables horarias para las 25 celdas restantes. | Insuficiente. |
| B. CDS `reanalysis-era5-land-timeseries` | 25 coordenadas pendientes, mismas seis variables y periodo que P1-P8. | Mantiene exactamente fuente, resolución horaria y método actual; permite magnitud horaria del viento. | Requiere solicitudes nuevas y credenciales CDS. | Recomendada. |
| C. Earth Engine `ECMWF/ERA5_LAND/DAILY_AGGR` | Celdas diarias de ~11.1 km, con T, Td, presión, radiación y componentes de viento. | Una extracción espacial sería eficiente. | Los no-flujos diarios son promedios de componentes; no preserva la magnitud horaria de viento que exige la guía. También exige acceso Earth Engine y una validación de calendario/proyección. | Útil como contraste, no como fuente principal. |
| D. Interpolar P1-P8 | No aporta observaciones. | Rápida. | Introduce datos no observados/modelados sin base; prohibido por este flujo. | Descartada. |

## Solicitud pendiente recomendada

Usar las 25 filas de `era5land_25_celdas_pendientes_CDS.csv` como coordenadas para `reanalysis-era5-land-timeseries`, desde 1981-01-01 00:00 hasta 2023-08-31 23:00 UTC. Solicitar: temperatura a 2 m, punto de rocío a 2 m, presión superficial, radiación solar superficial descendente, U10 y V10. Mantener los ZIP originales P1-P8 y guardar cada descarga nueva sin alterar los existentes.

## Elevación y resolución

La elevación media SRTM ponderada es 2348.98 m y la orografía nativa ERA5-Land ponderada es 2367.17 m: diferencia 18.19 m. Aun con diferencia media pequeña, la elevación SRTM por celda abarca 264-4084 m, por lo que se debe discutir el suavizado subcelda de T y Td en el informe.

## Regla para el cálculo final

El cálculo principal seguirá la guía: primero se combinarán las **variables meteorológicas diarias con los 33 pesos** y luego se aplicará FAO-56 con Tmax/Tmin espaciales, ea derivada de Td y la magnitud horaria de viento. Como sensibilidad, se podrá comparar contra el promedio ponderado de ETo calculada por celda; ambos procedimientos no son matemáticamente equivalentes.
