# Bonificación 2.5 — Peaks Over Threshold (POT)

- Variable: precipitación acumulada en 1 h a partir de datos de 10 minutos.
- Periodo disponible: 2004-08-13 a 2025-12-31 (21.38 años).
- Umbral: percentil 95 = **0.530 mm/h**.
- Regla de declustering: máximos separados por más de 24 h.
- Picos independientes: **1523**.
- Tasa de excedencia: **71.220 eventos/año**.
- Ajuste: distribución Generalizada de Pareto a los excesos, xi=0.23396, beta=1.87417.

Los niveles de retorno están en `pot_return_levels.csv`. POT es una
bonificación complementaria a la AMS/GEV de 2.2; no se mezclan ambas
estimaciones sin una decisión estadística adicional. La sensibilidad al umbral
y a la ventana de 24 h debe reconocerse como incertidumbre.
