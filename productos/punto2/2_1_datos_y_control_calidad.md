# Punto 2 — Apartado 2.1: datos subdiarios y control de calidad

## Resultado de la fase

La estación DWD 00020 cumple la resolución y longitud requeridas: la serie tiene
10 minutos de resolución y 21 años calendario disponibles (2005–2025). Al
definir el año hidrológico octubre–septiembre para no partir la temporada de
tormentas, quedan **20 años hidrológicos completos utilizables (2006–2025)**.

## Decisiones metodológicas

1. Se excluye 2004 por ser un año de inicio parcial.
2. Se adopta octubre–septiembre como año hidrológico: los máximos anuales de 1 h
   observados se concentran entre mayo y septiembre.
3. Se mantiene el criterio de completitud mínima de 80 %, pero se revisan además
   los faltantes dentro de mayo–septiembre.
4. Los valores negativos de precipitación se tratan como faltantes (`NaN`), no
   como lluvia cero.
5. Las máximas de 10 min, 30 min, 1 h, 3 h, 6 h, 12 h y 24 h se obtienen con
   ventanas móviles.

## Evidencia generada

- `control_2_1/monthly_rainfall_climatology.csv`: climatología mensual y
  fracción de la lluvia anual.
- `control_2_1/hydrological_year_audit.csv`: años hidrológicos, completitud y
  bandera de uso en máximas anuales.
- `control_2_1/missing_by_month.csv`: faltantes por mes y temporada.
- `control_2_1/spatial_justification.json`: coordenadas, distancias, elevación y
  estado de la justificación espacial.
- `control_2_1/revision_2_1.md`: resumen ejecutivo reproducible.

## Justificación espacial preliminar

La estación está aproximadamente a 414 m del outlet preliminar y la diferencia
entre su elevación y la elevación media de la microcuenca es de unos 15 m. Esto
apoya que compartan un régimen regional, pero no reemplaza la comprobación
visual de que el outlet drena hacia un canal, vía o zona urbana. Esa verificación
queda explícitamente pendiente en QGIS.

## Criterio de cierre

El apartado 2.1 se cerrará cuando se incorporen al informe la tabla de años
válidos, la temporada de tormentas, el tratamiento de faltantes, las coordenadas
y la evidencia cartográfica final del outlet.
