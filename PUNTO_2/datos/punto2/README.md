# Datos del punto 2

Esta carpeta contiene los insumos para el diseno hidrologico del punto 2:

- lluvia subdiaria de 10 minutos;
- metadatos de la estacion y control de calidad;
- modelo digital de elevacion (SRTM);
- cobertura del suelo (ESA WorldCover).

La cuenca Racarumi de la Tarea 1 no se usa como estacion de diseno en este punto.
La estacion seleccionada es DWD 00020, Abtsgmuend-Untergroeningen, Alemania.

Coordenadas actuales: 48.9219 N, 9.9129 E.
Elevacion actual: 432 m s.n.m.
Variable: precipitacion acumulada en los 10 minutos anteriores (RWS_10), en mm.
Periodo util para maxima anual: 2005-2025, 21 anos completos.

El archivo `abtsgmuend_precipitation_10min.csv` es la serie consolidada.
El archivo `data_audit.csv` resume la completitud anual.
El archivo `station_metadata.csv` conserva la identificacion y ubicacion.

La carpeta `Abtsgmuend_Untergroeningen/cuenca_preparada` contiene una
delimitacion preliminar reproducible con el DEM (GeoJSON, mascara y resumen
geomorfologico). Tambien incluye `ams_precipitation.csv`, con las maximas
anuales de 10 min, 30 min, 1, 3, 6, 12 y 24 horas, y `rainfall_qc_summary.csv`.
La auditoria final esta en `revision_lluvia.md`, `stationarity_tests.csv`,
`ams_precipitation_weiss.csv`, `quality_code_audit.csv` y
`timestamp_interval_audit.csv`.
Tambien se descargaron las capas oficiales KOSTRA-DWD-2020 para 10 min, 1 h,
6 h y 24 h en la carpeta `Abtsgmuend_Untergroeningen/kostra`, para comparar la
IDF observada con la referencia regional del DWD.

La microcuenca de 0.1 a 5 km2 y su punto de salida aun deben delimitarse con el
DEM, porque una estacion meteorologica no define por si sola el limite de una
microcuenca. Esa delimitacion sera el siguiente paso antes de calcular el area,
la pendiente y el tiempo de concentracion.
