# Inicio del apartado 2.5 — Bonificación POT

Se seleccionó la bonificación **Peaks Over Threshold (POT)** porque utiliza la
resolución subdiaria disponible y complementa los máximos anuales de 2.2 sin
reemplazarlos.

## Objetivo

Estimar niveles de lluvia horaria a partir de todos los eventos que superan un
umbral, evitando contar varias horas del mismo episodio como eventos
independientes.

## Método aplicado

- Serie de precipitación DWD de 10 minutos.
- Acumulación horaria exigiendo seis registros válidos.
- Umbral: percentil 95 de la lluvia horaria, 0.530 mm/h.
- Declustering: separación mínima de 24 h.
- Picos independientes: 1523.
- Tasa de excedencia: 71.220 eventos/año.
- Distribución de excesos: Generalizada de Pareto, ξ=0.23396 y β=1.87417.

## Resultados de niveles de retorno

| T (años) | Nivel POT 1 h (mm) |
|---:|---:|
| 2 | 18.08 |
| 5 | 24.19 |
| 10 | 29.76 |
| 25 | 38.67 |
| 50 | 46.79 |
| 100 | 56.35 |

Los resultados se encuentran en `PUNTO_2/datos/punto2/Abtsgmuend_Untergroeningen/bonificacion_2_5_pot/`.

## Interpretación y limitaciones

POT produce una estimación complementaria a la AMS/GEV de 2.2. No se deben
combinar ambos resultados sin un modelo estadístico conjunto. La tasa elevada
de excedencias es consecuencia del umbral 95 % y debe someterse a sensibilidad
con umbrales alternativos (90 % y 98 %) y ventanas de declustering distintas.
El resultado no modifica automáticamente la IDF ni el diámetro de 2.4.

**Estado:** 2.5 iniciado, análisis POT reproducible completado; pendiente
realizar sensibilidad del umbral y redactar la comparación final POT–GEV.
