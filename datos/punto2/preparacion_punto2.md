# Preparacion del punto 2

## Insumos listos

1. Serie DWD 00020 en intervalos de 10 minutos, 2005-2025.
2. Control de calidad y completitud anual.
3. Maximas anuales de 10 min, 30 min, 1 h, 3 h, 6 h, 12 h y 24 h.
4. DEM SRTM N48E009.
5. Cobertura ESA WorldCover 2021.
6. Estacion y puntos de control en GeoJSON.

## Delimitacion preliminar

La delimitacion D8 sobre el DEM produjo una microcuenca de 0.12315 km2. El
salto hidrologico mas cercano a la estacion esta a 103.1 m y el punto de salida
seleccionado esta a 414.4 m. El archivo `cuenca_resumen.csv` contiene elevacion,
pendiente media y coordenadas.

La propiedad `station_inside_drainage=False` no es un error de descarga: indica
que el pixel exacto de la estacion no drena hacia el punto de salida elegido.
Por eso la microcuenca debe revisarse en QGIS y, si el profesor exige que el
pluviometro quede dentro del poligono, se debe mover el outlet aguas abajo o
escoger otro cauce cercano, conservando el area entre 0.1 y 5 km2.

Se verifico con QGIS Processing que el DEM SRTM es valido (EPSG:4326, 3601 x
3601 celdas, elevaciones en metros) y que el GeoJSON de la microcuenca se puede
leer como capa vectorial. La interfaz grafica de QGIS no expuso una ventana
controlable en esta sesion, por lo que la comprobacion visual de la relacion
outlet-canal/via queda pendiente de abrir el GeoJSON en QGIS Desktop.

## Siguiente calculo

Con el poligono validado se deben obtener el area final, longitud y pendiente
del cauce, CN ponderado a partir de WorldCover/suelo, tiempo de concentracion y
la lluvia de diseno. Luego se ajustan las distribuciones de extremos y se
resuelven los problemas A (metodo racional) y B (tanque de detencion).
