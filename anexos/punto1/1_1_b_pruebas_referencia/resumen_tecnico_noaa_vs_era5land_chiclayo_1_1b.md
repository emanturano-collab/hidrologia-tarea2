# Estación NOAA frente a ERA5-Land - Chiclayo

La celda ERA5-Land retornó (-6.8000, -79.8000), a
3.40 km de la estación. El ZIP contiene las seis variables,
113976 horas por variable, sin nulos ni huecos; no se añadió a la
ponderación de Racarumi.

Hay 3690 días comunes válidos y 101 meses completos. Con
radiación propia de ERA5 (`ssrd`) frente a NOAA estimada con ecuación 50:
Pearson=0.6487, Spearman=0.6625, sesgo
NOAA-ERA5=0.105 mm/día, MAE=0.518
y RMSE=0.670 mm/día.

Al estimar radiación en ambas fuentes con ecuación 50 y kRs=0.19: Pearson=
0.7244, Spearman=0.7302, sesgo=
0.407 mm/día, MAE=0.561 y
RMSE=0.713 mm/día. Esta segunda comparación reduce la diferencia
metodológica asociada a que NOAA no tiene radiación observada, pero conserva
diferencias de temperatura, humedad, presión y viento entre estación y reanálisis.

La prueba valida el comportamiento local de ERA5-Land en una estación costera
externa a Racarumi. No demuestra precisión en toda la cuenca andina ni modifica
la ETo de cuenca, que sigue preliminar con cobertura 90.1264 %.
