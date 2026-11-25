# Cierre de la sensibilidad POT — apartado 2.5

Se evaluaron umbrales del percentil 90, 95 y 98, manteniendo una ventana de
declustering de 24 h.

| Umbral | Umbral (mm/h) | Picos independientes | Eventos/año | ξ |
|---:|---:|---:|---:|---:|
| P90 | 0,12 | 1600 | 74,82 | 0,2087 |
| P95 | 0,53 | 1523 | 71,22 | 0,2340 |
| P98 | 1,30 | 1131 | 52,89 | 0,2606 |

## Comparación con GEV-MLE para 1 h

Los niveles POT son cercanos a GEV para T=2 años, pero menores para retornos
altos. Para T=100 años:

- POT-P90: 52,87 mm, 56,6 % de GEV.
- POT-P95: 56,35 mm, 60,4 % de GEV.
- POT-P98: 61,10 mm, 65,4 % de GEV.
- GEV-MLE: 93,36 mm.

La diferencia aumenta con el periodo de retorno. El cambio de umbral entre P90
y P98 modifica el nivel POT de T=100 entre 52,87 y 61,10 mm, una variación
aproximada del 15 %. Esto indica sensibilidad al umbral, pero no cambia la
conclusión cualitativa: la IDF GEV-MLE es más conservadora en la cola.

## Dictamen

La bonificación POT confirma que los resultados de 2.2–2.3 dependen del método
de extrapolación. Se conserva la GEV-MLE como curva principal de diseño porque
la tarea exige una estimación de extremos basada en máximos anuales y porque es
la opción con mejor desempeño combinado en las pruebas estadísticas. POT se
reporta como análisis de sensibilidad y no se mezcla con GEV para generar un
tercer valor sin fundamento estadístico.

Archivos reproducibles:

- `pot_threshold_sensitivity.csv`
- `pot_levels_threshold_sensitivity.csv`
- `pot_vs_gev_1h.csv`
- `sensibilidad_pot_2_5.md`
