# Contexto espacial de Abtsgmünd-Untergröningen

La estación DWD 00020 se encuentra en Abtsgmünd-Untergröningen. Fuentes
institucionales del estado de Baden-Württemberg describen el río **Kocher** en
Untergröningen y las obras de la carretera federal **B 19** sobre el Kocher:

- [Regierungspräsidium Stuttgart: puentes de la B 19 en Untergröningen](https://rps.baden-wuerttemberg.de/abt4/ref472/b-19-bruecken-in-untergroeningen/)
- [Regierungspräsidium Stuttgart: trabajos en el Kocher entre Abtsgmünd y Untergröningen](https://rps.baden-wuerttemberg.de/presse/medienmitteilungen-und-aktuelle-meldungen/artikel-meldungen/gehoelzpflegearbeiten-am-kocher-ab-dem-5-november-2026-ostalbkreis/)

Estas fuentes confirman que el entorno regional contiene un cauce principal y
una infraestructura vial apropiada para contextualizar el problema 2.4. No
demuestran por sí solas que el outlet preliminar de 48.91819 N, 9.91236 E esté
exactamente sobre un canal o una vía. Esa relación puntual debe verificarse
visualmente en QGIS antes de fijar la geometría definitiva.

Resultado de 2.1: **la estación y el régimen regional quedan justificados; la
verificación geométrica puntual del outlet requiere todavía decidir si se mueve
el punto final hasta el cauce OSM más cercano. La consulta reproducible encontró
51 elementos de agua y 111 vías en 1200 m; el cauce más cercano está a 412.6 m y
la vía más cercana a 118.1 m. El detalle está en `osm_outlet_summary.json`.
