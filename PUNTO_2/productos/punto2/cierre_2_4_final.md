# Cierre final del apartado 2.4

> Nota de actualización: los valores de referencia para la entrega son los
> del archivo `cierre_final_punto2.md`, generado después de reconstruir las
> salidas auditables. Este documento conserva el cierre anterior como registro.

## 1. Declaración del outlet

El punto de salida adoptado para los cálculos es:

- Latitud: **48.9181944° N**
- Longitud: **9.9123611° E**
- Área drenante: **0.123154 km²**

El punto se seleccionó sobre el extremo aguas abajo del cauce principal
derivado del MDE SRTM y queda dentro del polígono de la microcuenca. La
comprobación visual está en `control_2_1/mapa_revision_visual_detalle.png`.

La revisión con OpenStreetMap muestra que el cauce DEM no coincide exactamente
con una línea OSM confirmada; el cauce OSM etiquetado más cercano está a unos
238 m. Por ello, el outlet se declara formalmente como **outlet sintético
derivado del MDE**, no como una obra existente ni como un punto de aforo real.
Esta hipótesis debe mantenerse explícita en el informe y limita la
interpretación de la geometría hidráulica.

## 2. Coeficiente de escorrentía

La cobertura se obtuvo del raster ESA WorldCover 2021 recortado a la
microcuenca:

| Cobertura | Área | C adoptado |
|---|---:|---:|
| Árboles | 56.17 % | 0.30 |
| Pastizal | 32.10 % | 0.35 |
| Cultivo | 11.74 % | 0.45 |

El valor base usado es:

`C = 0.5617(0.30) + 0.3210(0.35) + 0.1174(0.45) = 0.334`

Los valores por cobertura se adoptan como valores de diseño para una cuenca
rural pequeña, siguiendo como referencia metodológica Chow, Maidment y Mays,
*Applied Hydrology* (1988), tabla de coeficientes de escorrentía para áreas
rurales. No se presentan como mediciones directas de la cuenca.

La incertidumbre se incorporó mediante sensibilidad de ±20 %:

- C bajo: **0.267**
- C base: **0.334**
- C alto: **0.400**

La selección de C debe interpretarse junto con el tipo de suelo, la pendiente,
la humedad antecedente y la magnitud de la tormenta. Si el docente exige un
manual nacional específico, se deben sustituir los tres valores y recalcular
el promedio ponderado.

## 3. Riesgo acumulado de la obra

Para la alcantarilla circular de 1.50 m se obtuvo:

- Capacidad Manning: **7.08 m³/s**
- Probabilidad anual efectiva estimada por Monte Carlo: **0.9569 %**
- Riesgo acumulado de excedencia durante 30 años: **25.057 %**

El riesgo de 25.057 % no se presenta como riesgo bajo. Significa que, bajo las
distribuciones y supuestos utilizados, existe aproximadamente una probabilidad
de 0.219 de que al menos un evento durante la vida de 30 años supere la
capacidad modelada. La cifra depende del outlet sintético, del C adoptado, del
tiempo de concentración, del número de simulaciones y de la IDF seleccionada.

Por tanto, la recomendación de diseño debe incluir una de estas dos decisiones:

1. aceptar la alcantarilla de 1.50 m como solución preliminar, declarando el
   riesgo residual del 21.9 %; o
2. adoptar una medida adicional de seguridad (mayor diámetro, alivio de
   emergencia, mantenimiento y/o control operativo) y volver a calcular el
   riesgo.

## Estado de 2.4

Con estas declaraciones, el apartado 2.4 queda documentado y reproducible. La
limitación del outlet y el riesgo residual deben aparecer también en la
conclusión general del punto 2; no deben ocultarse ni presentarse como una
validación de campo.
