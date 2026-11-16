# Estación y datos del punto 2

## Estación seleccionada

- Nombre: Abtsgmünd-Untergröningen
- Código DWD: `00020`
- Latitud actual: `48.9219 N`
- Longitud actual: `9.9129 E`
- Elevación actual: `432 m`
- Variable: `RWS_10`, precipitación acumulada en los 10 minutos anteriores
- Unidad: mm
- Intervalo: 10 minutos
- Zona temporal: UTC en el archivo descargado

El metadato geográfico DWD registra los cambios históricos de coordenadas y elevación. La ubicación actual corresponde al periodo desde 2003-08-11. El archivo de precipitación descargado cubre 2004-08-12 a 2025-12-31.

## Verificación temporal

El año 2004 es parcial y se excluye de la serie de máximos anuales. Los años completos 2005–2025 suman 21 años y todos superan 98.5 % de registros no faltantes; por tanto, la estación supera el requisito mínimo de 20 años válidos antes de realizar el control específico de extremos.

## Archivos

- `abtsgmuend_precipitation_10min.csv`: serie unificada de los tres archivos DWD históricos.
- `data_audit.csv`: auditoría de registros por año.
- `station_metadata.csv`: identificación espacial y variables.
- `raw/`: ZIP y archivos originales DWD extraídos.
- `N48E009.hgt.gz`: DEM SRTM que cubre la estación y su entorno.
- `ESA_WorldCover_10m_2021_v200_N48E009_Map.tif`: cobertura del suelo ESA WorldCover 2021.

La microcuenca de 0.1–5 km² todavía debe delimitarse con el DEM y asociarse a una salida real hacia una vía, canal o zona urbana.
