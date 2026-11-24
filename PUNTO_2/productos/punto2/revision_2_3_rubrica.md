# Verificación de cierre — apartado 2.3

| Requisito | Evidencia | Estado |
|---|---|---|
| Parámetros de la expresión IDF | `idf_powerlaw_parameters.csv` | `a(T)` y `eta(T)` para T = 2, 5, 10, 25, 50 y 100 años. |
| Error del ajuste | `idf_fit_error_metrics.csv` | RMSE, MAE, error máximo, R² log-log y rango 0.1667–24 h. |
| Bandas de incertidumbre del evento reciente | `recent_event_return_period_uncertainty.csv` | Evento 2021: 48.27 mm en 1 h; T puntual 17.36 años; bootstrap P2.5–P97.5 = 6.30–178.51 años. |
| Comparación externa | `idf_kostra_comparison.csv`, `kostra_station_cell.csv` | KOSTRA-DWD-2020, celda 186/142, EPSG:3035, cuatro duraciones y nueve retornos. |
| Referencia verificable | `kostra_referencia_verificable.md` | DOI y portal oficial DWD documentados. |
| Interpretación física | `revision_2_3.md` e informe | Se separan evento extremo, anomalía estadística y tendencia temporal. |

## Dictamen

El apartado 2.3 tiene la evidencia cuantitativa exigida. El evento de 2021 se
reporta como extremo/anomalía de la muestra, no como prueba de cambio climático.
La comparación KOSTRA se presenta como contraste de escala y referencia
estadística, no como una estimación directa de sesgo.
