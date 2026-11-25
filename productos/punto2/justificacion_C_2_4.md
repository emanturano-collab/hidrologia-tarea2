# Justificación del coeficiente de escorrentía

La cobertura ESA WorldCover 2021 dentro del polígono de la microcuenca es:

| Cobertura | Área (%) | C adoptado |
|---|---:|---:|
| Árboles | 56.17 | 0.30 |
| Pastizal | 32.10 | 0.35 |
| Cultivo | 11.74 | 0.45 |

El coeficiente ponderado es:

`C = (0.5617·0.30) + (0.3210·0.35) + (0.1174·0.45) = 0.334`

Se adopta **C = 0.334** como valor base del método racional. Los valores por
cobertura son rangos representativos para una cuenca rural pequeña y deben
atribuirse en el informe a la tabla de coeficientes de escorrentía adoptada
(Chow et al. o manual de drenaje equivalente). No se debe presentar C como una
propiedad observada: depende del suelo, pendiente, humedad antecedente y
magnitud de la tormenta.

Para la incertidumbre se usa una sensibilidad global de ±20 %:

- C bajo: 0.267
- C base: 0.334
- C alto: 0.400

La clasificación de cobertura sí es observada del raster; la traducción de
cobertura a C es un supuesto de ingeniería y debe quedar explícita.
