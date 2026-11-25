# Prueba de estación NOAA GHCNh - PEI0000SPHI

Los 13 PSV originales (2010-2022) fueron trasladados sin modificación y todos
conservaron SHA-256. GHCNh indexa los registros en UTC; el cálculo diario usa
UTC-05:00. La estación está en Chiclayo (-6.7875, -79.8281; 29.6 m),
un aeropuerto costero, por lo que no se interpreta como representativa del
relieve andino de toda Racarumi.

Se aceptó un día sólo cuando temperatura, punto de rocío y viento tenían al menos
18 horas válidas. Hay 3690 días válidos y 101 meses
completos. La presión observada se usó sólo con cobertura suficiente y valores
900-1050 hPa; en los demás días se aplicó FAO-56 ecuación 7 con la elevación.

No hay radiación solar observada. La ETo primaria usa FAO-56 ecuación 50 con
kRs=0.19 por condición costera: media 4.505 mm/día. La sensibilidad
kRs=0.16 cambia ETo en promedio 0.311 mm/día. La altura
exacta del anemómetro no aparece en los PSV; el producto primario aplica el ajuste
10 m a 2 m como supuesto convencional y el escenario sin ajuste cambia ETo en
0.267 mm/día en promedio. Estas sensibilidades son parte del
resultado, no observaciones inventadas.

La celda ERA5-Land existente más cercana es P1 a
61.9 km, por lo cual no es apropiada para una validación
puntual. La solicitud mínima para una sola celda está en
`solicitud_era5land_puntual_estacion_pei0000sphi.csv`; hasta contar con ella no
se reportan métricas estación-ERA5 ni se declara terminada la segunda categoría
de prueba. La ETo de cuenca sigue siendo preliminar (cobertura 90.1264 %).
