# Cierre del apartado 2.3 — IDF y anomalías

La IDF GEV-MLE se ajustó con `i(d,T)=a(T)d^{-eta(T)}`. `idf_powerlaw_parameters.csv`
contiene `a`, `eta` y RMSE; `idf_fit_error_metrics.csv` añade MAE, error máximo,
R² log-log y el rango 0.1667–24 h.

El evento de 1 h de 2021 (48.27 mm) tiene periodo de retorno puntual GEV de
aproximadamente 17.36 años. El bootstrap de 1000 réplicas está en
`recent_event_return_period_bootstrap.csv` y su resumen en
`recent_event_return_period_uncertainty.csv`.

Un evento extremo es una observación grande; una anomalía es su desviación
respecto a la distribución de referencia; una tendencia es un cambio sistemático
en el tiempo. El evento 2021 se reporta como extremo y anomalía estadística, no
como evidencia suficiente de tendencia climática.
