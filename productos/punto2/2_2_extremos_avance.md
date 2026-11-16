# Punto 2 — Apartado 2.2: avance de extremos

## Trabajo realizado

1. Se recalcularon las máximas anuales usando año hidrológico octubre–septiembre.
2. Se utilizaron 20 años completos, 2006–2025.
3. Se calcularon máximas móviles para 10 min, 30 min, 1 h, 3 h, 6 h, 12 h y
   24 h.
4. Se ajustaron por máxima verosimilitud Gumbel, GEV y log-Pearson III.
5. Se calcularon cuantiles preliminares para T = 2, 5, 10, 25, 50 y 100 años.
6. Se aplicó Kolmogorov–Smirnov como revisión inicial de ajuste.
7. Se recalculó Mann–Kendall y pendiente de Sen sobre el año hidrológico.

## Archivos

- `extremos_2_2/ams_hydrological_oct_sep.csv`
- `extremos_2_2/fit_summary_mle.csv`
- `extremos_2_2/quantiles_mle.csv`
- `extremos_2_2/stationarity_hydrological_year.csv`

## Resultado preliminar

No se detecta tendencia significativa en ninguna duración con Mann–Kendall
(todos los p-valores son mayores que 0.05). Esto no demuestra estacionariedad
absoluta; indica ausencia de evidencia suficiente de tendencia en los 20 años.

## Trabajo completado posteriormente

- Los tres modelos se ajustaron por momentos, L-momentos y máxima verosimilitud.
- Se añadieron Kolmogorov–Smirnov y Cramer–von Mises.
- Se generaron cuantiles para los seis periodos de retorno.
- Se generaron intervalos bootstrap GEV-MLE al 95 % y ancho relativo.
- El promedio de p-valores favorece provisionalmente GEV-MLE; KS medio 0.857 y
  Cramer–von Mises medio 0.900.
- Las gráficas de probabilidad y el diagrama de razones de L-momentos están en
  `graficas_probabilidad_2_2.png` y `diagrama_lmomentos_2_2.png`.
- El bootstrap muestra inestabilidad muy grande en algunos cuantiles T=100,
  especialmente para duraciones largas; esto debe reportarse como incertidumbre
  de extrapolación y no ocultarse.

## Pendiente de revisión científica

Falta que el grupo inspeccione visualmente ambas figuras y justifique en el
informe por qué GEV-MLE es preferible a GEV-L-momentos o log-Pearson III. La
selección no debe basarse únicamente en el promedio de p-valores.

El apartado 2.2 queda en avance aproximado de **95 %**.
