# Revisión visual del outlet

Se generaron dos mapas estáticos a partir del MDE SRTM, el polígono de la microcuenca, los puntos de control, el cauce principal derivado del MDE y las geometrías de cauces disponibles de OpenStreetMap:

- `mapa_revision_visual.png`: contexto regional.
- `mapa_revision_visual_detalle.png`: ampliación del outlet.

## Resultado

1. El outlet usado (`48.9181944 N, 9.9123611 E`) queda sobre el extremo aguas abajo del cauce principal derivado del MDE (línea negra discontinua) y dentro del límite rojo de la microcuenca.
2. La estación DWD 00020 queda al norte del outlet y fuera del polígono de drenaje calculado, tal como indicaba la auditoría espacial previa.
3. Las líneas azules OSM de los cauces cartografiados no coinciden exactamente con el cauce DEM en el outlet; el cauce OSM más cercano etiquetado queda aproximadamente a 238 m. Por tanto, esta comprobación visual **valida la coherencia interna del delineamiento DEM**, pero no permite afirmar que el outlet sea una obra o punto de control sobre un cauce OSM real.

## Implicación para 2.4

Antes de congelar el diseño hidráulico, el informe debe declarar esta limitación y justificar el outlet como punto sintético derivado del MDE, o sustituirlo por un punto sobre una geometría OSM/ortofoto verificable y recalcular área, longitud, pendiente, caudal y tanque.
