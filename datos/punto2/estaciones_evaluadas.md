# Evaluación preliminar de estaciones para el punto 2

## Cuenca de la Tarea 1

La estación hidrológica Racarumi (`-6.633, -79.317`, 265 m) representa la cuenca Chancay–Lambayeque de 2363.302 km². La lista oficial GHCNh no contiene una estación Racarumi. La precipitación de la Tarea 1 procede de una serie diaria PISCO; por tanto, no puede generar directamente ventanas móviles de minutos/horas para la IDF.

## Estaciones peruanas revisadas

| Estación GHCNh | Coordenadas aproximadas | Distancia a Racarumi | Resultado de la revisión |
|---|---:|---:|---|
| Huambos (`PEA00843470`) | -6.450, -78.967; 2200 m | ~44 km | El archivo descargable contiene una sola observación; no sirve para AMS de 20 años. |
| Motupe (`PEM00084442`) | -6.067, -79.682; 191 m | ~75 km | Serie subdiaria observada desde 2020-02; aproximadamente 6.7 años, insuficiente. |
| Jaén (`PEM00084410`) | -5.583, -78.767; 755 m | ~132 km | Serie desde 2011-02; aproximadamente 15 años, insuficiente para el requisito preferente de 20 años. |
| Chiclayo (`PEI0000SPHI`) | -6.788, -79.828; 30 m | ~59 km | La distancia/elevación y el régimen costero son muy distintos de Racarumi; no debe asumirse representativa sin validación climática. |

Conclusión: con los archivos públicos comprobados no se puede defender una estación subdiaria que sea simultáneamente representativa de Racarumi y tenga al menos 20 años válidos. SENAMHI ofrece datos meteorológicos bajo registro/autenticación; si el grupo consigue una serie subdiaria histórica de SENAMHI, debe auditarse antes de aceptarla.

## Candidatos alternativos para cambiar de sitio

Como cribado inicial, el metadato GSDR-IDF muestra estaciones observacionales con más de 20 años y resolución subdiaria en estas zonas:

- cuenca del Delaware/área de Philadelphia, EE. UU. (aprox. 112 años en la estación `US_004672` del metadato GSDR-IDF);
- cuenca del French Broad, Asheville, EE. UU. (aprox. 109 años; `US_003702`);
- cuenca urbana/costera de Hobart, Tasmania (aprox. 104 años; `AU_001864`);
- cuenca de Sydney, Australia (aprox. 102 años; `AU_001461`).

Estos son candidatos, no una selección definitiva: antes de elegir uno hay que descargar el archivo GHCNh/GSDR de la estación exacta, verificar años válidos, escoger una microcuenca DEM de 0.1–5 km² cercana y justificar que la estación y la microcuenca comparten régimen climático y exposición.

## Fuentes y criterio

- GHCNh es una colección horaria/sinóptica con variables de precipitación y archivos por estación; se usó la lista y los archivos oficiales de NCEI.
- GSDR-IDF se usó solo para el cribado de duración del registro; sus curvas ya procesadas no sustituyen la serie subdiaria cruda que exige el análisis reproducible.
