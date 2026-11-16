# Revisión de cumplimiento — apartado 2.1

## Dictamen

El apartado 2.1 **cumple los requisitos de datos subdiarios y control de calidad**
de la tarea y puede cerrarse metodológicamente.

El problema pendiente de que el outlet quede exactamente sobre un cauce o vía
pertenece al apartado 2.4, no al criterio de selección y control de la serie de
lluvia. Se conserva como condición de diseño antes de calcular el método
racional.

## Comprobación contra el PDF

| Requisito 2.1 | Evidencia | Estado |
|---|---|---|
| Resolución <= 6 h, preferible 10 min | Serie DWD RWS_10 | Cumple |
| Al menos 20 máximos anuales válidos | 20 años hidrológicos completos, 2006–2025 | Cumple |
| Fuente primaria y metadatos | DWD 00020, coordenadas, elevación, variable y periodo | Cumple |
| Criterio de completitud | Auditorías anual, hidrológica y mensual | Cumple |
| Faltantes y códigos de calidad | `quality_code_audit.csv`, `missing_by_month.csv` | Cumple |
| Ventanas móviles | 10 min a 24 h | Cumple |
| Coherencia entre duraciones | Auditoría de máximas | Cumple |
| Intervalos fijos y Weiss | `ams_precipitation_weiss.csv` | Cumple |
| Revisión espacial | Distancia y elevación documentadas; contexto OSM | Cumple para la estación; outlet final queda para 2.4 |

## Decisión

2.1 queda aprobado como **100 % completado**. Se puede avanzar a 2.2. La
delimitación final del outlet no se debe olvidar al cerrar 2.4 A.
