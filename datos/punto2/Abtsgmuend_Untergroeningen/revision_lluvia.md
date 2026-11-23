# Revision final de lluvia DWD 00020

## Resultado

- Años analizados: 21 (2005-2025).
- Resolución efectiva: 10 minutos; no se detectan años con menos de 80% de registros.
- Mayor máximo anual de 1 h: 81.26 mm en 2013.
- Se generó la corrección de Weiss para ventanas fijas en `ams_precipitation_weiss.csv`.

## Coherencia entre duraciones

- 10min_le_30min: OK
- 30min_le_1h: OK
- 1h_le_3h: OK
- 3h_le_6h: OK
- 6h_le_12h: OK
- 12h_le_24h: OK

## Estacionariedad

Los valores de tau, p y pendiente de Sen estan en `stationarity_tests.csv`. Se debe reportar la prueba formal junto con la incertidumbre de los cuantiles; un p > 0.05 no demuestra estacionariedad absoluta, solo ausencia de evidencia suficiente de tendencia.

## Archivos para iniciar el IDF

1. `ams_precipitation_weiss.csv` como maxima anual corregida.
2. `stationarity_tests.csv` para 2.2.6.
3. `ams_precipitation.csv` para rastrear los maximos sin correccion.
